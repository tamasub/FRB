using System.Diagnostics;
using System.Text;
using System.Text.Encodings.Web;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Text.Json.Nodes;
using System.Text.RegularExpressions;
using System.Text.Unicode;
using System.Windows.Forms;
using System.Drawing;
using System.Runtime.InteropServices;
using Microsoft.Extensions.Configuration;

namespace FRBStudio;

internal static class Program
{
    private const string AppUrl = "http://localhost:5055";
    private const string DefaultDataJsonFolder = "data/json";
    private const string DefaultGitDiffProfileId = "git_diff_export";
    private const string DefaultGitDiffDisplayName = "Export-DiffToJson.ps1 / Git Diff JSON Export";
    private const string DefaultGitDiffScriptPath = "tools/git/Export-DiffToJson.ps1";
    private const string DefaultGitDiffOutputPath = "wwwroot/diff/DiffToJson.json";
    private const string DefaultTestRunnerProfileId = "test_runner";
    private const string DefaultTestRunnerDisplayName = "TestRunner.ps1 / Studio Test Runner";
    private const string DefaultTestRunnerScriptPath = "tools/test/TestRunner.ps1";

    [STAThread]
    private static async Task Main(string[] args)
    {
        Application.EnableVisualStyles();
        Application.SetCompatibleTextRenderingDefault(false);

        WebApplication? app = null;

        try
        {
            var appRoot = ResolveStudioAppRoot();
            app = CreateWebApplication(args, appRoot);
            await app.StartAsync();
            OpenBrowser(AppUrl);

            using var tray = new FrbStudioTrayContext(app, AppUrl);
            Application.Run(tray);
        }
        catch (Exception ex)
        {
            MessageBox.Show(
                "FRB Studio の起動に失敗しました。\n\n" + ex.Message,
                "FRB Studio",
                MessageBoxButtons.OK,
                MessageBoxIcon.Error);
        }
        finally
        {
            if (app is not null)
            {
                try { await app.StopAsync(TimeSpan.FromSeconds(3)); } catch { }
                await app.DisposeAsync();
            }
        }
    }

    private static WebApplication CreateWebApplication(string[] args, string appRoot)
    {
        var builder = WebApplication.CreateBuilder(new WebApplicationOptions
        {
            Args = args,
            ContentRootPath = appRoot
        });
        builder.WebHost.UseUrls(AppUrl);

        var root = appRoot;
        var dataRootDir = Path.Combine(root, "data");
        var dataDir = Path.Combine(dataRootDir, "json");
        var markdownDir = Path.Combine(dataRootDir, "markdown");
        var defsDir = Path.Combine(root, "defs");
        var fieldDefsDir = Path.Combine(root, "fielddefs");
        var overlaysDir = Path.Combine(root, "studio_overlays");

        Directory.CreateDirectory(dataRootDir);
        Directory.CreateDirectory(dataDir);
        Directory.CreateDirectory(markdownDir);
        Directory.CreateDirectory(defsDir);
        Directory.CreateDirectory(fieldDefsDir);
        Directory.CreateDirectory(overlaysDir);

        var dataFolders = ResolveDataFolders(
            builder.Configuration,
            root,
            "FrbStudio:DataFolders",
            new[] { DefaultDataJsonFolder });

        var commandProfiles = BuildCommandProfiles(builder.Configuration, root);

        // 旧構成 data/*.json から新構成 data/json/*.json へ、初回だけ安全に移行する。
        foreach (var oldJson in Directory.GetFiles(dataRootDir, "*.json"))
        {
            var dest = Path.Combine(dataDir, Path.GetFileName(oldJson));
            if (!File.Exists(dest)) File.Copy(oldJson, dest);
        }

        var app = builder.Build();

        app.UseDefaultFiles();
        app.UseStaticFiles();

        app.MapGet("/api/data", () => Results.Json(ListJsonFiles(dataFolders)));

        app.MapGet("/api/defs", () => Results.Json(ListJsonFiles(defsDir)));

        // v0.18.47-field-definition-runtime-validation:
        // item_definition_ref is relative to the independent fielddefs root.
        // Runtime only needs a read path here; editing/browsing policy remains a separate responsibility.
        app.MapGet("/api/fielddefs/{**name}", async (string name) =>
        {
            var path = SafeJsonPath(fieldDefsDir, name);
            if (path is null || !File.Exists(path)) return Results.NotFound();
            return Results.Text(await File.ReadAllTextAsync(path, Encoding.UTF8), "application/json; charset=utf-8");
        });

        // v0.17.0-studio-overlay-manifest-separation:
        // OverlayはCore(wwwroot/defs/data)を変更せず、studio_overlays/{overlayId} 配下で管理する。
        // CoreとOverlayの共通言語は studio_manifest.json。
        app.MapGet("/api/overlays", () => Results.Json(ListOverlayIds(overlaysDir)));

        app.MapGet("/api/overlays/{overlayId}/manifest", async (string overlayId) =>
        {
            var path = SafeOverlayPath(overlaysDir, overlayId, "studio_manifest.json", new[] { ".json" });
            if (path is null || !File.Exists(path)) return Results.NotFound();

            var manifestText = await File.ReadAllTextAsync(path);
            var expanded = ExpandOverlayManifestWildcards(overlaysDir, overlayId, manifestText);
            return Results.Text(expanded, "application/json; charset=utf-8");
        });

        app.MapGet("/api/overlays/{overlayId}/{**name}", async (string overlayId, string name) =>
        {
            var path = SafeOverlayPath(overlaysDir, overlayId, name, new[] { ".json", ".js", ".md" });
            if (path is null || !File.Exists(path)) return Results.NotFound();

            var ext = Path.GetExtension(path).ToLowerInvariant();
            var contentType = ext switch
            {
                ".js" => "application/javascript; charset=utf-8",
                ".md" => "text/markdown; charset=utf-8",
                _ => "application/json; charset=utf-8"
            };
            return Results.Text(await File.ReadAllTextAsync(path), contentType);
        });

        // v0.8.0-chart-comment-sidecar-observation-memo follow-up:
        // Overlay Plugin のコメントSidecar JSONを studio_overlays/{overlayId}/sidecars 配下へ保存する。
        // /api/data は data/json 管理用なので、OverlayのSidecarをそこへ混ぜない。
        app.MapPost("/api/overlays/{overlayId}/sidecars/{**name}", async (string overlayId, string name, JsonElement json) =>
        {
            var sidecarName = "sidecars/" + name;
            var path = SafeOverlayPath(overlaysDir, overlayId, sidecarName, new[] { ".json" });
            if (path is null) return Results.BadRequest("invalid overlay sidecar file name");

            Directory.CreateDirectory(Path.GetDirectoryName(path)!);
            await WriteJsonAsync(path, json);
            return Results.Ok(new { saved = $"overlay/{overlayId}/{sidecarName.Replace('\\', '/')}" });
        });

        app.MapPost("/api/data/drop", async (DropJsonRequest req) =>
        {
            var path = SafeDataPath(dataFolders, req.Name, preferExisting: false);
            if (path is null) return Results.BadRequest("invalid file name");

            Directory.CreateDirectory(Path.GetDirectoryName(path)!);
            await WriteJsonAsync(path, req.Json);
            return Results.Ok(new { saved = ToApiName(dataFolders, path) ?? req.Name });
        });

        app.MapGet("/api/data/{**name}", async (string name) =>
        {
            var path = SafeDataPath(dataFolders, name, preferExisting: true);
            if (path is null || !File.Exists(path)) return Results.NotFound();
            return Results.Text(await File.ReadAllTextAsync(path, Encoding.UTF8), "application/json; charset=utf-8");
        });

        app.MapPost("/api/data/{**name}", async (string name, JsonElement json) =>
        {
            var path = SafeDataPath(dataFolders, name, preferExisting: false);
            if (path is null) return Results.BadRequest("invalid file name");

            Directory.CreateDirectory(Path.GetDirectoryName(path)!);
            await WriteJsonAsync(path, json);
            return Results.Ok(new { saved = ToApiName(dataFolders, path) ?? name });
        });

        app.MapGet("/api/markdown", () => Results.Json(ListMarkdownFiles(markdownDir)));

        app.MapPost("/api/markdown/drop", async (MarkdownSaveRequest req) =>
        {
            var dropName = SafeMarkdownRootFileName(req.Name);
            var path = dropName is null ? null : SafeMarkdownPath(markdownDir, dropName);
            if (path is null || dropName is null) return Results.BadRequest("invalid file name");

            Directory.CreateDirectory(Path.GetDirectoryName(path)!);
            await File.WriteAllTextAsync(path, req.Content ?? string.Empty);
            return Results.Ok(new { saved = dropName });
        });

        // mdViewer v0.16.14.2: ブラウザでは取得できない「名前を付けて保存」先を、
        // FRBStudio.exe 側の WinForms SaveFileDialog でユーザー選択して保存する。
        // data/markdown の管理対象保存とは別口にし、任意パス文字列をHTTPから受け取らない。
        app.MapPost("/api/markdown/save-as-dialog", (MarkdownSaveRequest req) =>
        {
            var result = ShowMarkdownSaveAsDialog(markdownDir, req);
            if (!string.IsNullOrWhiteSpace(result.Error)) return Results.Problem(result.Error, statusCode: 500);
            if (result.Cancelled) return Results.Ok(new { cancelled = true });
            return Results.Ok(new
            {
                cancelled = false,
                saved = result.FileName,
                path = result.SavedPath,
                sidecar_saved = result.SidecarSaved,
                sidecar_file = result.SidecarFileName,
                sidecar_path = result.SidecarSavedPath,
                sidecar_error = result.SidecarError
            });
        });

        app.MapPost("/api/markdown/open-dialog", () =>
        {
            var result = ShowMarkdownOpenDialog();
            if (!string.IsNullOrWhiteSpace(result.Error)) return Results.Problem(result.Error, statusCode: 500);
            if (result.Cancelled) return Results.Ok(new { cancelled = true });
            return Results.Ok(new
            {
                cancelled = false,
                file_name = result.FileName,
                path = result.Path,
                content = result.Content,
                sidecar_file = result.SidecarFileName,
                sidecar_path = result.SidecarPath,
                sidecar_content = result.SidecarContent,
                sidecar_found = !string.IsNullOrWhiteSpace(result.SidecarContent)
            });
        });

        app.MapGet("/api/markdown/{**name}", async (string name) =>
        {
            var path = SafeMarkdownPath(markdownDir, name);
            if (path is null || !File.Exists(path)) return Results.NotFound();

            var contentType = IsMarkdownCommentSidecarName(Path.GetFileName(path))
                ? "application/json; charset=utf-8"
                : "text/markdown; charset=utf-8";

            return Results.Text(await File.ReadAllTextAsync(path), contentType);
        });

        app.MapPost("/api/markdown/{**name}", async (string name, MarkdownSaveRequest req) =>
        {
            var path = SafeMarkdownPath(markdownDir, name);
            if (path is null) return Results.BadRequest("invalid file name");

            Directory.CreateDirectory(Path.GetDirectoryName(path)!);
            await File.WriteAllTextAsync(path, req.Content ?? string.Empty);
            return Results.Ok(new { saved = ToRelativeApiPath(markdownDir, path) });
        });

        app.MapGet("/api/defs/{**name}", async (string name) =>
        {
            var path = SafeJsonPath(defsDir, name);
            if (path is null || !File.Exists(path)) return Results.NotFound();
            return Results.Text(await File.ReadAllTextAsync(path, Encoding.UTF8), "application/json; charset=utf-8");
        });

        app.MapPost("/api/defs/drop", async (DropJsonRequest req) =>
        {
            var path = SafeJsonPath(defsDir, req.Name);
            if (path is null) return Results.BadRequest("invalid file name");

            await WriteJsonAsync(path, req.Json);
            return Results.Ok(new { saved = req.Name });
        });

        // v0.17.9-json-folder-open:
        // ブラウザからはローカルフォルダーを直接開けないため、FRBStudio.exe側で選択中JSONをExplorer表示する。
        // kind=data は dataFolders 契約、kind=viewdef は defs 契約に限定して解決し、任意パス実行を防ぐ。
        app.MapPost("/api/shell/open-json-folder", (OpenJsonFolderRequest req) =>
        {
            var kind = (req.Kind ?? string.Empty).Trim().ToLowerInvariant();
            if (string.IsNullOrWhiteSpace(req.Path)) return Results.BadRequest(new { error = "path is required" });

            var fullPath = ResolveOpenJsonPath(kind, req.Path, dataFolders, defsDir, overlaysDir);

            if (fullPath is null) return Results.BadRequest(new { error = "invalid kind or path" });
            if (!File.Exists(fullPath) && !Directory.Exists(fullPath)) return Results.NotFound(new { error = "file or folder not found" });

            var isFile = File.Exists(fullPath);
            var folder = isFile ? Path.GetDirectoryName(fullPath) : fullPath;
            if (string.IsNullOrWhiteSpace(folder) || !Directory.Exists(folder)) return Results.NotFound(new { error = "folder not found" });

            var selectFile = req.SelectFile ?? req.select_file ?? true;
            OpenExplorerAndBringToFront(folder, isFile && selectFile ? fullPath : null);

            return Results.Ok(new
            {
                opened = folder,
                selected = isFile && selectFile ? fullPath : null,
                kind,
                path = req.Path
            });
        });

        // v0.14.37-git-diff-export-command-profile:
        // Data JSONから任意コマンドを実行させず、Program.cs側で許可したCommandProfileだけを実行する。
        app.MapGet("/api/actions/command/profiles", () => Results.Json(commandProfiles.Values.Select(profile => new
        {
            command_profile_id = profile.Id,
            display_name = profile.DisplayName,
            app_root = profile.AppRoot,
            script_path = profile.ScriptPath,
            script_path_relative = ToAppRootRelative(profile.AppRoot, profile.ScriptPath),
            output_path = profile.OutputPath,
            output_path_relative = ToAppRootRelative(profile.AppRoot, profile.OutputPath),
            working_directory = profile.WorkingDirectory,
            working_directory_relative = ToAppRootRelative(profile.AppRoot, profile.WorkingDirectory),
            timeout_seconds = profile.TimeoutSeconds,
            kind = profile.Kind,
            allowed_modes = profile.AllowedModes,
            allowed_test_runner_ids = profile.AllowedTestRunnerIds
        })));

        app.MapGet("/api/actions/command/diagnostics", () => Results.Json(new
        {
            app_root = root,
            app_context_base_directory = AppContext.BaseDirectory,
            current_directory = Directory.GetCurrentDirectory(),
            profiles = commandProfiles.Values.Select(BuildCommandProfileDiagnostic)
        }));

        app.MapPost("/api/actions/command/run", async (CommandRunRequest req) =>
            await RunCommandProfileAsync(commandProfiles, req));

        return app;
    }

    private static string ResolveStudioAppRoot()
    {
        var candidates = new List<string>();
        AddCandidateWithParents(candidates, AppContext.BaseDirectory);
        AddCandidateWithParents(candidates, Directory.GetCurrentDirectory());

        foreach (var candidate in candidates.Distinct(StringComparer.OrdinalIgnoreCase))
        {
            if (IsStudioAppRoot(candidate)) return Path.GetFullPath(candidate);
        }

        // Last resort: keep historical behavior, but normal deployments should be resolved by markers.
        return Path.GetFullPath(AppContext.BaseDirectory);
    }

    private static void AddCandidateWithParents(List<string> candidates, string? startPath)
    {
        if (string.IsNullOrWhiteSpace(startPath)) return;

        DirectoryInfo? dir;
        try
        {
            var full = Path.GetFullPath(startPath);
            dir = Directory.Exists(full) ? new DirectoryInfo(full) : new FileInfo(full).Directory;
        }
        catch
        {
            return;
        }

        while (dir is not null)
        {
            candidates.Add(dir.FullName);
            dir = dir.Parent;
        }
    }

    private static bool IsStudioAppRoot(string path)
    {
        try
        {
            return File.Exists(Path.Combine(path, "wwwroot", "index.html"))
                && Directory.Exists(Path.Combine(path, "data", "json"))
                && Directory.Exists(Path.Combine(path, "defs"))
                && Directory.Exists(Path.Combine(path, "tools"));
        }
        catch
        {
            return false;
        }
    }

    private static IReadOnlyDictionary<string, CommandProfile> BuildCommandProfiles(IConfiguration config, string root)
    {
        var profiles = new Dictionary<string, CommandProfile>(StringComparer.OrdinalIgnoreCase);

        var gitSection = config.GetSection("FrbStudio:CommandProfiles:GitDiffExport");
        var gitProfile = BuildCommandProfile(
            gitSection,
            root,
            defaultId: DefaultGitDiffProfileId,
            defaultDisplayName: DefaultGitDiffDisplayName,
            defaultScriptPath: DefaultGitDiffScriptPath,
            defaultOutputPath: DefaultGitDiffOutputPath,
            kind: "git_diff_export",
            allowedModes: new[] { "WorkingTree", "Staged", "Head", "Range", "FilePair" },
            allowedTestRunnerIds: Array.Empty<string>(),
            defaultTimeoutSeconds: 30);
        profiles[gitProfile.Id] = gitProfile;

        var testSection = config.GetSection("FrbStudio:CommandProfiles:TestRunner");
        var testProfile = BuildCommandProfile(
            testSection,
            root,
            defaultId: DefaultTestRunnerProfileId,
            defaultDisplayName: DefaultTestRunnerDisplayName,
            defaultScriptPath: DefaultTestRunnerScriptPath,
            defaultOutputPath: string.Empty,
            kind: "test_runner",
            allowedModes: Array.Empty<string>(),
            allowedTestRunnerIds: new[] { "playwright_ui", "incident_prompt_copy_action_static", "responsibility_expected_tests", "responsibility_refactor_first_step_smoke" },
            defaultTimeoutSeconds: 120);
        profiles[testProfile.Id] = testProfile;

        return profiles;
    }

    private static CommandProfile BuildCommandProfile(
        IConfigurationSection section,
        string root,
        string defaultId,
        string defaultDisplayName,
        string defaultScriptPath,
        string defaultOutputPath,
        string kind,
        IReadOnlyList<string> allowedModes,
        IReadOnlyList<string> allowedTestRunnerIds,
        int defaultTimeoutSeconds)
    {
        var id = string.IsNullOrWhiteSpace(section["Id"])
            ? defaultId
            : section["Id"]!.Trim();

        var displayName = string.IsNullOrWhiteSpace(section["DisplayName"])
            ? defaultDisplayName
            : section["DisplayName"]!.Trim();

        var scriptPath = ResolveCommandScriptPath(root, section["ScriptPath"] ?? defaultScriptPath, defaultScriptPath);
        var outputPath = ResolveCommandOutputPath(root, section["OutputPath"], defaultOutputPath);

        var configuredWorkingDirectory = section["WorkingDirectory"];
        var workingDirectory = ResolveCommandWorkingDirectory(root, configuredWorkingDirectory);

        var timeoutSeconds = defaultTimeoutSeconds;
        if (int.TryParse(section["TimeoutSeconds"], out var configuredTimeout))
        {
            timeoutSeconds = Math.Clamp(configuredTimeout, 5, 600);
        }

        var powerShellExe = string.IsNullOrWhiteSpace(section["PowerShellExe"])
            ? DefaultPowerShellExe()
            : section["PowerShellExe"]!.Trim();

        return new CommandProfile(
            id,
            displayName,
            root,
            scriptPath,
            outputPath,
            workingDirectory,
            powerShellExe,
            kind,
            allowedModes,
            allowedTestRunnerIds,
            timeoutSeconds);
    }

    private static string DefaultPowerShellExe()
    {
        return OperatingSystem.IsWindows() ? "powershell.exe" : "pwsh";
    }

    private static string ResolveCommandScriptPath(string root, string rawPath, string fallbackRelativePath)
    {
        var value = string.IsNullOrWhiteSpace(rawPath) ? fallbackRelativePath : rawPath.Trim();
        var full = Path.IsPathRooted(value)
            ? Path.GetFullPath(value)
            : Path.GetFullPath(Path.Combine(root, value.Replace('/', Path.DirectorySeparatorChar)));

        // CommandProfileのscriptPathは、Studio配下の許可済みスクリプトに限定する。
        var allowedRoot = EnsureTrailingSeparator(Path.GetFullPath(root));
        if (!full.StartsWith(allowedRoot, StringComparison.OrdinalIgnoreCase))
        {
            return Path.GetFullPath(Path.Combine(root, fallbackRelativePath.Replace('/', Path.DirectorySeparatorChar)));
        }

        return full;
    }

    private static string ResolveCommandWorkingDirectory(string root, string? rawPath)
    {
        if (!string.IsNullOrWhiteSpace(rawPath))
        {
            var full = ResolvePathUnderAppRoot(root, rawPath.Trim());
            if (!string.IsNullOrWhiteSpace(full) && Directory.Exists(full)) return full;
        }

        // CommandProfileはFRBStudio_App rootを基準に実行する。
        // Gitはサブディレクトリ実行でも親の.gitを探索できるため、repo上位パスへ移動しない。
        return Path.GetFullPath(root);
    }

    private static string ResolveCommandOutputPath(string root, string? rawPath, string defaultRelativePath)
    {
        if (string.IsNullOrWhiteSpace(defaultRelativePath) && string.IsNullOrWhiteSpace(rawPath)) return string.Empty;

        var raw = string.IsNullOrWhiteSpace(rawPath) ? defaultRelativePath : rawPath!.Trim();
        var full = ResolvePathUnderAppRoot(root, raw);
        if (!string.IsNullOrWhiteSpace(full)) return full;

        var fallback = ResolvePathUnderAppRoot(root, defaultRelativePath);
        return fallback ?? string.Empty;
    }

    private static string? ResolvePathUnderAppRoot(string root, string rawPath)
    {
        if (string.IsNullOrWhiteSpace(rawPath)) return null;

        try
        {
            var normalized = rawPath.Trim().Trim('"').Replace('/', Path.DirectorySeparatorChar);
            var full = Path.IsPathRooted(normalized)
                ? Path.GetFullPath(normalized)
                : Path.GetFullPath(Path.Combine(root, normalized));

            var rootFull = EnsureTrailingSeparator(Path.GetFullPath(root));
            return EnsureTrailingSeparatorForCompare(full).StartsWith(rootFull, StringComparison.OrdinalIgnoreCase)
                ? full
                : null;
        }
        catch
        {
            return null;
        }
    }

    private static string EnsureTrailingSeparatorForCompare(string path)
    {
        if (string.IsNullOrWhiteSpace(path)) return string.Empty;
        if (File.Exists(path)) return path;
        return EnsureTrailingSeparator(path);
    }

    private static string? FindNearestGitRoot(string startDir)
    {
        var dir = new DirectoryInfo(Path.GetFullPath(startDir));
        while (dir is not null)
        {
            if (Directory.Exists(Path.Combine(dir.FullName, ".git"))) return dir.FullName;
            dir = dir.Parent;
        }
        return null;
    }

    private static async Task<IResult> RunCommandProfileAsync(
        IReadOnlyDictionary<string, CommandProfile> profiles,
        CommandRunRequest req)
    {
        var profileId = FirstNonBlank(req.CommandProfileId, req.ProfileId);
        if (string.IsNullOrWhiteSpace(profileId)) return Results.BadRequest("command_profile_id is required");
        if (!profiles.TryGetValue(profileId, out var profile)) return Results.BadRequest($"unsupported command_profile_id: {profileId}");

        return profile.Kind.Equals("test_runner", StringComparison.OrdinalIgnoreCase)
            ? await RunTestRunnerCommandProfileAsync(profile, req)
            : await RunGitDiffCommandProfileAsync(profile, req);
    }

    private static IResult CommandProfileBadRequest(CommandProfile profile, string message)
    {
        return Results.Json(new
        {
            success = false,
            result_kind = "launcher_error",
            profile_id = profile.Id,
            message,
            diagnostics = BuildCommandProfileDiagnostic(profile)
        }, statusCode: 400);
    }

    private static async Task<IResult> RunGitDiffCommandProfileAsync(CommandProfile profile, CommandRunRequest req)
    {
        if (!File.Exists(profile.ScriptPath))
        {
            return Results.Json(new
            {
                success = false,
                profile_id = profile.Id,
                message = "CommandProfileのscriptPathが見つかりません",
                script_path = profile.ScriptPath
            }, statusCode: 500);
        }

        if (!Directory.Exists(profile.WorkingDirectory))
        {
            return Results.Json(new
            {
                success = false,
                profile_id = profile.Id,
                message = "CommandProfileのworkingDirectoryが見つかりません",
                working_directory = profile.WorkingDirectory
            }, statusCode: 500);
        }

        // output_path_display / output_path は表示・参考情報としてのみ扱う。
        // 実行出力先の正本はCommandProfile側のOutputPathであり、Run Config明細値で照合・上書きしない。

        var mode = (req.Mode ?? string.Empty).Trim();
        var range = (req.Range ?? string.Empty).Trim();
        var fromRef = (req.FromRef ?? string.Empty).Trim();
        var toRef = (req.ToRef ?? string.Empty).Trim();
        var fromFile = (req.FromFile ?? string.Empty).Trim();
        var toFile = (req.ToFile ?? string.Empty).Trim();
        var fromFilePath = string.Empty;
        var toFilePath = string.Empty;

        if (!ValidateGitDiffMode(mode, profile.AllowedModes))
        {
            return CommandProfileBadRequest(profile, $"unsupported mode: {mode}");
        }

        if (mode.Equals("FilePair", StringComparison.OrdinalIgnoreCase))
        {
            if (!TryResolveDiffInputFilePath(profile.WorkingDirectory, fromFile, out fromFilePath, out var fromFileError))
            {
                return CommandProfileBadRequest(profile, $"from_file is invalid: {fromFileError}");
            }
            if (!TryResolveDiffInputFilePath(profile.WorkingDirectory, toFile, out toFilePath, out var toFileError))
            {
                return CommandProfileBadRequest(profile, $"to_file is invalid: {toFileError}");
            }
            range = string.Empty;
        }
        else if (mode.Equals("Range", StringComparison.OrdinalIgnoreCase))
        {
            if (!IsSafeGitRef(fromRef) || !IsSafeGitRef(toRef))
            {
                return CommandProfileBadRequest(profile, "Range mode requires safe from_ref and to_ref");
            }
            range = $"{fromRef}..{toRef}";
            mode = string.Empty;
        }
        else if (string.IsNullOrWhiteSpace(range) && (!string.IsNullOrWhiteSpace(fromRef) || !string.IsNullOrWhiteSpace(toRef)))
        {
            if (!IsSafeGitRef(fromRef) || !IsSafeGitRef(toRef))
            {
                return CommandProfileBadRequest(profile, "from_ref and to_ref must both be safe git refs");
            }
            range = $"{fromRef}..{toRef}";
            mode = string.Empty;
        }

        if (!string.IsNullOrWhiteSpace(range) && !IsSafeGitRange(range))
        {
            return CommandProfileBadRequest(profile, "range contains unsupported characters");
        }

        var unified = req.Unified is > 0 and <= 100 ? req.Unified.Value : 3;
        var maxPatchChars = req.MaxPatchChars is > 0 and <= 2_000_000 ? req.MaxPatchChars.Value : 60000;

        var outputDir = Path.GetDirectoryName(profile.OutputPath);
        if (!string.IsNullOrWhiteSpace(outputDir)) Directory.CreateDirectory(outputDir);

        var argsForReport = new List<string>();
        var psi = new ProcessStartInfo
        {
            FileName = profile.PowerShellExe,
            WorkingDirectory = profile.WorkingDirectory,
            UseShellExecute = false,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            CreateNoWindow = true,
            StandardOutputEncoding = Encoding.UTF8,
            StandardErrorEncoding = Encoding.UTF8
        };

        void AddArg(string value)
        {
            psi.ArgumentList.Add(value);
            argsForReport.Add(value);
        }

        AddArg("-NoProfile");
        AddArg("-ExecutionPolicy");
        AddArg("Bypass");
        AddArg("-File");
        AddArg(profile.ScriptPath);

        if (!string.IsNullOrWhiteSpace(mode))
        {
            AddArg("-Mode");
            AddArg(mode);
        }

        if (!string.IsNullOrWhiteSpace(range))
        {
            AddArg("-Range");
            AddArg(range);
        }

        if (mode.Equals("FilePair", StringComparison.OrdinalIgnoreCase))
        {
            AddArg("-FromFile");
            AddArg(fromFilePath);
            AddArg("-ToFile");
            AddArg(toFilePath);
        }

        AddArg("-OutputPath");
        AddArg(profile.OutputPath);
        AddArg("-Unified");
        AddArg(unified.ToString());
        AddArg("-MaxPatchChars");
        AddArg(maxPatchChars.ToString());

        if (req.NoPatch == true)
        {
            AddArg("-NoPatch");
        }

        var startedAt = StudioNow();
        using var process = new Process { StartInfo = psi };

        try
        {
            process.Start();
        }
        catch (Exception ex)
        {
            return Results.Json(new
            {
                success = false,
                profile_id = profile.Id,
                message = "CommandProfileの起動に失敗しました",
                error = ex.Message
            }, statusCode: 500);
        }

        var stdoutTask = process.StandardOutput.ReadToEndAsync();
        var stderrTask = process.StandardError.ReadToEndAsync();
        var waitTask = process.WaitForExitAsync();
        var timeoutTask = Task.Delay(TimeSpan.FromSeconds(profile.TimeoutSeconds));

        var completed = await Task.WhenAny(waitTask, timeoutTask);
        var timedOut = completed == timeoutTask;
        if (timedOut)
        {
            try { process.Kill(entireProcessTree: true); } catch { }
        }
        else
        {
            await waitTask;
        }

        var stdout = await stdoutTask;
        var stderr = await stderrTask;
        var finishedAt = StudioNow();
        var exitCode = timedOut ? -1 : process.ExitCode;
        var success = !timedOut && exitCode == 0;

        var createdOutputPath = success
            ? ResolveGitDiffCreatedOutputPath(profile, stdout, startedAt)
            : string.Empty;
        var createdOutputRelativePath = ToAppRootRelative(profile.AppRoot, createdOutputPath);
        var createdStaticUrl = BuildStaticUrlForAppRootPath(profile.AppRoot, createdOutputPath);
        var viewerUrl = string.IsNullOrWhiteSpace(createdStaticUrl)
            ? string.Empty
            : BuildDiffJsonViewerUrl(createdStaticUrl);
        var outputArtifacts = BuildGitDiffOutputArtifacts(profile, createdOutputPath);

        var result = new
        {
            success,
            result_kind = success ? "git_diff_exported" : "launcher_error",
            timed_out = timedOut,
            exit_code = exitCode,
            profile_id = profile.Id,
            display_name = profile.DisplayName,
            mode = string.IsNullOrWhiteSpace(req.Mode) ? "(default)" : req.Mode,
            range,
            from_file = fromFilePath,
            to_file = toFilePath,
            output_path = string.IsNullOrWhiteSpace(createdOutputPath) ? profile.OutputPath : createdOutputPath,
            output_path_relative = string.IsNullOrWhiteSpace(createdOutputPath) ? ToAppRootRelative(profile.AppRoot, profile.OutputPath) : createdOutputRelativePath,
            output_path_configured = profile.OutputPath,
            output_path_configured_relative = ToAppRootRelative(profile.AppRoot, profile.OutputPath),
            diff_json_path = createdOutputRelativePath,
            diff_json_url = createdStaticUrl,
            viewer_url = viewerUrl,
            output_artifacts = outputArtifacts,
            working_directory = profile.WorkingDirectory,
            command = new
            {
                file = profile.PowerShellExe,
                args = argsForReport
            },
            stdout = TruncateCommandOutput(stdout, 20000),
            stderr = TruncateCommandOutput(stderr, 20000),
            started_at = FormatStudioDateTime(startedAt),
            finished_at = FormatStudioDateTime(finishedAt),
            duration_ms = (long)(finishedAt - startedAt).TotalMilliseconds,
            message = success
                ? $"Git Diff JSONを出力しました: {createdOutputRelativePath}"
                : (timedOut ? $"Git Diff Run がタイムアウトしました: {profile.TimeoutSeconds}s" : $"Git Diff Run が失敗しました: exit_code={exitCode}")
        };

        return success
            ? Results.Json(result)
            : Results.Json(result, statusCode: 500);
    }

    private static async Task<IResult> RunTestRunnerCommandProfileAsync(CommandProfile profile, CommandRunRequest req)
    {
        if (!File.Exists(profile.ScriptPath))
        {
            return Results.Json(new
            {
                success = false,
                result_kind = "launcher_error",
                profile_id = profile.Id,
                message = "TestRunnerのscriptPathが見つかりません",
                script_path = profile.ScriptPath,
                output_artifacts = Array.Empty<CommandOutputArtifact>()
            }, statusCode: 500);
        }

        if (!Directory.Exists(profile.WorkingDirectory))
        {
            return Results.Json(new
            {
                success = false,
                result_kind = "launcher_error",
                profile_id = profile.Id,
                message = "TestRunnerのworkingDirectoryが見つかりません",
                working_directory = profile.WorkingDirectory,
                output_artifacts = Array.Empty<CommandOutputArtifact>()
            }, statusCode: 500);
        }

        var testRunnerId = FirstNonBlank(req.TestRunnerId, req.RunConfigId);
        if (string.IsNullOrWhiteSpace(testRunnerId))
        {
            return Results.Json(new
            {
                success = false,
                result_kind = "launcher_error",
                profile_id = profile.Id,
                message = "test_runner_id is required",
                output_artifacts = Array.Empty<CommandOutputArtifact>()
            }, statusCode: 400);
        }
        if (!profile.AllowedTestRunnerIds.Any(x => x.Equals(testRunnerId, StringComparison.OrdinalIgnoreCase)))
        {
            return Results.Json(new
            {
                success = false,
                result_kind = "launcher_error",
                profile_id = profile.Id,
                test_runner_id = testRunnerId,
                message = $"unsupported test_runner_id: {testRunnerId}",
                output_artifacts = Array.Empty<CommandOutputArtifact>()
            }, statusCode: 400);
        }

        var outputArtifacts = BuildTestRunnerOutputArtifacts(testRunnerId, profile.WorkingDirectory);

        var expectedRunMode = DefaultTestRunnerRunMode(testRunnerId);
        var runMode = FirstNonBlank(req.RunMode) ?? expectedRunMode;
        if (!runMode.Equals("launch", StringComparison.OrdinalIgnoreCase) && !runMode.Equals("wait", StringComparison.OrdinalIgnoreCase))
        {
            return Results.Json(new
            {
                success = false,
                result_kind = "launcher_error",
                profile_id = profile.Id,
                test_runner_id = testRunnerId,
                run_mode = runMode,
                message = $"unsupported run_mode: {runMode}",
                output_artifacts = outputArtifacts
            }, statusCode: 400);
        }
        if (!runMode.Equals(expectedRunMode, StringComparison.OrdinalIgnoreCase))
        {
            return Results.Json(new
            {
                success = false,
                result_kind = "launcher_error",
                profile_id = profile.Id,
                test_runner_id = testRunnerId,
                run_mode = runMode,
                message = $"run_mode does not match allowed mode for {testRunnerId}: expected {expectedRunMode}",
                output_artifacts = outputArtifacts
            }, statusCode: 400);
        }

        var argsForReport = new List<string>();
        var redirectOutput = runMode.Equals("wait", StringComparison.OrdinalIgnoreCase);
        var psi = new ProcessStartInfo
        {
            FileName = profile.PowerShellExe,
            WorkingDirectory = profile.WorkingDirectory,
            UseShellExecute = false,
            RedirectStandardOutput = redirectOutput,
            RedirectStandardError = redirectOutput,
            CreateNoWindow = redirectOutput
        };

        // launch mode does not redirect stdout/stderr.  Setting StandardOutputEncoding
        // when RedirectStandardOutput=false causes Process.Start() to fail on .NET.
        if (redirectOutput)
        {
            psi.StandardOutputEncoding = Encoding.UTF8;
            psi.StandardErrorEncoding = Encoding.UTF8;
        }

        void AddArg(string value)
        {
            psi.ArgumentList.Add(value);
            argsForReport.Add(value);
        }

        AddArg("-NoProfile");
        AddArg("-ExecutionPolicy");
        AddArg("Bypass");
        AddArg("-File");
        AddArg(profile.ScriptPath);
        AddArg("-TestRunnerId");
        AddArg(testRunnerId);
        AddArg("-RunMode");
        AddArg(runMode);
        AddArg("-RepositoryRoot");
        AddArg(profile.WorkingDirectory);

        var startedAt = StudioNow();

        if (runMode.Equals("launch", StringComparison.OrdinalIgnoreCase))
        {
            using var launchProcess = new Process { StartInfo = psi };
            try
            {
                launchProcess.Start();
            }
            catch (Exception ex)
            {
                return Results.Json(new
                {
                    success = false,
                    result_kind = "launcher_error",
                    profile_id = profile.Id,
                    test_runner_id = testRunnerId,
                    run_mode = runMode,
                    message = "TestRunnerの起動に失敗しました",
                    error = ex.Message,
                    output_artifacts = outputArtifacts
                }, statusCode: 500);
            }

            var result = new
            {
                success = true,
                result_kind = "command_launched",
                profile_id = profile.Id,
                display_name = profile.DisplayName,
                test_runner_id = testRunnerId,
                run_mode = runMode,
                pid = launchProcess.Id,
                working_directory = profile.WorkingDirectory,
                command_preview = req.CommandPreview ?? string.Empty,
                output_artifacts = outputArtifacts,
                command = new
                {
                    file = profile.PowerShellExe,
                    args = argsForReport
                },
                started_at = FormatStudioDateTime(startedAt),
                message = $"TestRunnerを起動しました: {testRunnerId}"
            };
            return Results.Json(result);
        }

        using var process = new Process { StartInfo = psi };
        try
        {
            process.Start();
        }
        catch (Exception ex)
        {
            return Results.Json(new
            {
                success = false,
                result_kind = "launcher_error",
                profile_id = profile.Id,
                test_runner_id = testRunnerId,
                run_mode = runMode,
                message = "TestRunnerの実行に失敗しました",
                error = ex.Message,
                output_artifacts = outputArtifacts
            }, statusCode: 500);
        }

        var stdoutTask = process.StandardOutput.ReadToEndAsync();
        var stderrTask = process.StandardError.ReadToEndAsync();
        var waitTask = process.WaitForExitAsync();
        var timeoutTask = Task.Delay(TimeSpan.FromSeconds(profile.TimeoutSeconds));

        var completed = await Task.WhenAny(waitTask, timeoutTask);
        var timedOut = completed == timeoutTask;
        if (timedOut)
        {
            try { process.Kill(entireProcessTree: true); } catch { }
        }
        else
        {
            await waitTask;
        }

        var stdout = await stdoutTask;
        var stderr = await stderrTask;
        var finishedAt = StudioNow();
        var exitCode = timedOut ? -1 : process.ExitCode;
        var success = !timedOut && exitCode == 0;
        var resultKind = timedOut ? "launcher_error" : (success ? "test_passed" : "test_failed");

        var resultWait = new
        {
            success,
            result_kind = resultKind,
            timed_out = timedOut,
            exit_code = exitCode,
            profile_id = profile.Id,
            display_name = profile.DisplayName,
            test_runner_id = testRunnerId,
            run_mode = runMode,
            working_directory = profile.WorkingDirectory,
            command_preview = req.CommandPreview ?? string.Empty,
            output_artifacts = outputArtifacts,
            command = new
            {
                file = profile.PowerShellExe,
                args = argsForReport
            },
            stdout = TruncateCommandOutput(stdout, 20000),
            stderr = TruncateCommandOutput(stderr, 20000),
            started_at = FormatStudioDateTime(startedAt),
            finished_at = FormatStudioDateTime(finishedAt),
            duration_ms = (long)(finishedAt - startedAt).TotalMilliseconds,
            message = success
                ? $"TestRunner完了: {testRunnerId}"
                : (timedOut ? $"TestRunner がタイムアウトしました: {profile.TimeoutSeconds}s" : $"テスト失敗: {testRunnerId} exit_code={exitCode}")
        };

        return resultKind.Equals("launcher_error", StringComparison.OrdinalIgnoreCase)
            ? Results.Json(resultWait, statusCode: 500)
            : Results.Json(resultWait);
    }

    private static IReadOnlyList<CommandOutputArtifact> BuildTestRunnerOutputArtifacts(string testRunnerId, string workingDirectory)
    {
        var relativePaths = testRunnerId switch
        {
            "playwright_ui" => new[]
            {
                "data/json/03_tests/screen_state/screen_state_smoke_001/diff/screen_state_smoke_001.diff.json"
            },
            "incident_prompt_copy_action_static" => new[]
            {
                "data/json/03_tests/qa/v0_14_2_incident_prompt_copy_action/diff/TP-IPC-001.diff.json"
            },
            "responsibility_expected_tests" => new[]
            {
                "data/json/03_tests/responsibilities/responsibility_expected_first_set/diff/responsibility_expected_first_set_diff_data_v0_1.json"
            },
            "responsibility_refactor_first_step_smoke" => Array.Empty<string>(),
            _ => Array.Empty<string>()
        };

        return relativePaths.Select(relativePath =>
        {
            var fullPath = Path.GetFullPath(Path.Combine(workingDirectory, relativePath.Replace('/', Path.DirectorySeparatorChar)));
            return new CommandOutputArtifact(
                Path: relativePath,
                FullPath: fullPath,
                Exists: File.Exists(fullPath),
                Kind: "diff_json");
        }).ToArray();
    }

    private static string DefaultTestRunnerRunMode(string testRunnerId)
    {
        return testRunnerId.Equals("playwright_ui", StringComparison.OrdinalIgnoreCase)
            ? "launch"
            : "wait";
    }

    private static string? FirstNonBlank(params string?[] values)
    {
        foreach (var value in values)
        {
            if (!string.IsNullOrWhiteSpace(value)) return value.Trim();
        }
        return null;
    }

    private static bool ValidateGitDiffMode(string mode, IReadOnlyList<string> allowedModes)
    {
        if (string.IsNullOrWhiteSpace(mode)) return true;
        return allowedModes.Any(x => x.Equals(mode, StringComparison.OrdinalIgnoreCase));
    }

    private static bool IsSafeGitRef(string value)
    {
        if (string.IsNullOrWhiteSpace(value)) return false;
        if (value.Length > 160) return false;
        return Regex.IsMatch(value, @"^[A-Za-z0-9._/\-~^]+$");
    }

    private static bool IsSafeGitRange(string value)
    {
        if (string.IsNullOrWhiteSpace(value)) return false;
        if (value.Length > 340) return false;
        if (!value.Contains("..", StringComparison.Ordinal)) return false;
        return Regex.IsMatch(value, @"^[A-Za-z0-9._/\-~^]+\.\.[A-Za-z0-9._/\-~^]+$");
    }

    private static string ResolveGitDiffCreatedOutputPath(CommandProfile profile, string stdout, DateTimeOffset startedAt)
    {
        var fromStdout = TryExtractCreatedPathFromStdout(stdout);
        if (!string.IsNullOrWhiteSpace(fromStdout) && File.Exists(fromStdout)) return fromStdout;

        var outputDir = Path.GetDirectoryName(profile.OutputPath);
        if (string.IsNullOrWhiteSpace(outputDir) || !Directory.Exists(outputDir)) return string.Empty;

        var baseName = Path.GetFileNameWithoutExtension(profile.OutputPath);
        var ext = Path.GetExtension(profile.OutputPath);
        if (string.IsNullOrWhiteSpace(baseName)) baseName = "DiffToJson";
        if (string.IsNullOrWhiteSpace(ext)) ext = ".json";

        var threshold = startedAt.LocalDateTime.AddSeconds(-3);
        return Directory.GetFiles(outputDir, $"{baseName}_*{ext}")
            .Select(path => new FileInfo(path))
            .Where(info => info.Exists && info.LastWriteTime >= threshold)
            .OrderByDescending(info => info.LastWriteTimeUtc)
            .Select(info => info.FullName)
            .FirstOrDefault() ?? string.Empty;
    }

    private static string TryExtractCreatedPathFromStdout(string stdout)
    {
        if (string.IsNullOrWhiteSpace(stdout)) return string.Empty;

        var match = Regex.Match(stdout, @"(?im)^\s*Created:\s*(?<path>.+?)\s*$");
        if (!match.Success) return string.Empty;

        var raw = match.Groups["path"].Value.Trim().Trim('"');
        if (string.IsNullOrWhiteSpace(raw)) return string.Empty;

        try
        {
            return Path.GetFullPath(raw);
        }
        catch
        {
            return string.Empty;
        }
    }

    private static IReadOnlyList<CommandOutputArtifact> BuildGitDiffOutputArtifacts(CommandProfile profile, string createdOutputPath)
    {
        if (string.IsNullOrWhiteSpace(createdOutputPath)) return Array.Empty<CommandOutputArtifact>();

        return new[]
        {
            new CommandOutputArtifact(
                Path: ToAppRootRelative(profile.AppRoot, createdOutputPath),
                FullPath: createdOutputPath,
                Exists: File.Exists(createdOutputPath),
                Kind: "diff_json")
        };
    }

    private static string BuildStaticUrlForAppRootPath(string appRoot, string? path)
    {
        if (string.IsNullOrWhiteSpace(path)) return string.Empty;

        try
        {
            var relative = ToAppRootRelative(appRoot, path);
            if (string.IsNullOrWhiteSpace(relative)) return string.Empty;
            relative = relative.Replace('\\', '/').TrimStart('/');
            const string wwwrootPrefix = "wwwroot/";
            if (!relative.StartsWith(wwwrootPrefix, StringComparison.OrdinalIgnoreCase)) return string.Empty;
            var staticPath = relative[wwwrootPrefix.Length..];
            if (string.IsNullOrWhiteSpace(staticPath)) return string.Empty;
            return AppUrl.TrimEnd('/') + "/" + string.Join("/", staticPath.Split('/', StringSplitOptions.RemoveEmptyEntries).Select(Uri.EscapeDataString));
        }
        catch
        {
            return string.Empty;
        }
    }

    private static string BuildDiffJsonViewerUrl(string diffJsonUrl)
    {
        if (string.IsNullOrWhiteSpace(diffJsonUrl)) return string.Empty;
        return AppUrl.TrimEnd('/') + "/DiffJsonViewer.html?path=" + Uri.EscapeDataString(diffJsonUrl);
    }

    private static bool TryResolveDiffInputFilePath(string workingDirectory, string value, out string resolvedPath, out string error)
    {
        resolvedPath = string.Empty;
        error = string.Empty;

        if (string.IsNullOrWhiteSpace(value))
        {
            error = "file path is required";
            return false;
        }
        if (value.Length > 500)
        {
            error = "file path is too long";
            return false;
        }
        if (value.Any(char.IsControl))
        {
            error = "file path contains control characters";
            return false;
        }
        if (value.IndexOfAny(new[] { '*', '?' }) >= 0)
        {
            error = "wildcards are not supported";
            return false;
        }

        try
        {
            var trimmed = value.Trim().Trim('"');
            resolvedPath = Path.IsPathRooted(trimmed)
                ? Path.GetFullPath(trimmed)
                : Path.GetFullPath(Path.Combine(workingDirectory, trimmed));
        }
        catch (Exception ex)
        {
            error = ex.Message;
            return false;
        }

        // FilePair は git diff --no-index による「任意2ファイル比較」なので、
        // 入力ファイルは FRBStudio_App root 配下に限定しない。
        // ただし、出力先は CommandProfile/Export-DiffToJson.ps1 側で FRBStudio_App root 配下に制限する。
        // ここでは「実在するローカルファイルか」「危険なワイルドカード/制御文字を含まないか」だけを確認する。

        if (!File.Exists(resolvedPath))
        {
            error = $"file not found: {resolvedPath}";
            return false;
        }
        if (Directory.Exists(resolvedPath))
        {
            error = $"directory path is not supported: {resolvedPath}";
            return false;
        }

        return true;
    }

    private static string ToAppRootRelative(string appRoot, string? path)
    {
        if (string.IsNullOrWhiteSpace(path)) return string.Empty;
        try
        {
            var full = Path.GetFullPath(path);
            var rootFull = EnsureTrailingSeparator(Path.GetFullPath(appRoot));
            if (!EnsureTrailingSeparatorForCompare(full).StartsWith(rootFull, StringComparison.OrdinalIgnoreCase)) return full;
            return Path.GetRelativePath(appRoot, full).Replace('\\', '/');
        }
        catch
        {
            return path ?? string.Empty;
        }
    }

    private static object BuildCommandProfileDiagnostic(CommandProfile profile)
    {
        var outputDir = string.IsNullOrWhiteSpace(profile.OutputPath) ? string.Empty : (Path.GetDirectoryName(profile.OutputPath) ?? string.Empty);
        return new
        {
            app_root = profile.AppRoot,
            app_root_exists = Directory.Exists(profile.AppRoot),
            app_context_base_directory = AppContext.BaseDirectory,
            current_directory = Directory.GetCurrentDirectory(),
            profile_id = profile.Id,
            kind = profile.Kind,
            script_path = profile.ScriptPath,
            script_path_relative = ToAppRootRelative(profile.AppRoot, profile.ScriptPath),
            script_exists = File.Exists(profile.ScriptPath),
            working_directory = profile.WorkingDirectory,
            working_directory_relative = ToAppRootRelative(profile.AppRoot, profile.WorkingDirectory),
            working_directory_exists = Directory.Exists(profile.WorkingDirectory),
            output_path = profile.OutputPath,
            output_path_relative = ToAppRootRelative(profile.AppRoot, profile.OutputPath),
            output_directory = outputDir,
            output_directory_relative = ToAppRootRelative(profile.AppRoot, outputDir),
            output_directory_exists = string.IsNullOrWhiteSpace(outputDir) ? (bool?)null : Directory.Exists(outputDir),
            timeout_seconds = profile.TimeoutSeconds
        };
    }

    private static string StringValue(string? value) => value ?? string.Empty;

    private static string TruncateCommandOutput(string? value, int maxChars)
    {
        var text = value ?? string.Empty;
        return text.Length <= maxChars
            ? text
            : text[..maxChars] + $"\n--- truncated: {text.Length - maxChars} chars omitted ---";
    }

    private static IReadOnlyList<DataFolder> ResolveDataFolders(
        IConfiguration config,
        string root,
        string sectionName,
        string[] defaults)
    {
        var configured = config.GetSection(sectionName).Get<string[]>();
        var values = configured is { Length: > 0 } ? configured : defaults;

        var result = new List<DataFolder>();
        var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        var rootFull = EnsureTrailingSeparator(Path.GetFullPath(root));

        foreach (var raw in values)
        {
            if (string.IsNullOrWhiteSpace(raw)) continue;

            var relative = raw.Replace('\\', '/').Trim('/');
            if (string.IsNullOrWhiteSpace(relative)) continue;
            if (Path.IsPathRooted(relative)) continue;
            if (relative.Split('/', StringSplitOptions.RemoveEmptyEntries).Any(part => part == "..")) continue;

            var fullPath = Path.GetFullPath(Path.Combine(root, relative.Replace('/', Path.DirectorySeparatorChar)));
            if (!EnsureTrailingSeparator(fullPath).StartsWith(rootFull, StringComparison.OrdinalIgnoreCase)) continue;
            if (!seen.Add(fullPath)) continue;

            Directory.CreateDirectory(fullPath);
            result.Add(new DataFolder(relative, fullPath, result.Count == 0));
        }

        if (result.Count == 0)
        {
            var fallback = Path.Combine(root, "data", "json");
            Directory.CreateDirectory(fallback);
            result.Add(new DataFolder("data/json", fallback, true));
        }

        return result;
    }

    private static string ExpandOverlayManifestWildcards(string overlaysDir, string overlayId, string manifestText)
    {
        JsonNode? root;
        try
        {
            root = JsonNode.Parse(manifestText);
        }
        catch
        {
            return manifestText;
        }

        if (root is not JsonObject manifest) return manifestText;
        var id = SafeOverlayId(overlayId);
        if (id is null) return manifestText;

        var overlayRoot = Path.GetFullPath(Path.Combine(overlaysDir, id));
        if (!Directory.Exists(overlayRoot)) return manifestText;

        var manifestKeys = new[]
        {
            "data_files", "dataFiles",
            "view_def_files", "viewDefFiles", "view_defs",
            "value_set_files", "valueSetFiles", "value_sets",
            "search_pattern_files", "searchPatternFiles", "search_patterns",
            "plugin_index_files", "pluginIndexFiles", "plugin_indexes"
        };

        var expansionNotes = new JsonArray();
        foreach (var key in manifestKeys)
        {
            if (manifest[key] is not JsonArray values) continue;

            var expandedValues = new List<string>();
            var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);

            foreach (var node in values)
            {
                var value = node?.GetValue<string>()?.Trim();
                if (string.IsNullOrWhiteSpace(value)) continue;

                if (!ContainsOverlayWildcard(value))
                {
                    var normalized = NormalizeOverlayManifestRelativePath(value);
                    if (normalized is not null && seen.Add(normalized)) expandedValues.Add(normalized);
                    continue;
                }

                var matches = ExpandOverlayWildcardPattern(overlayRoot, value);
                foreach (var match in matches)
                {
                    if (seen.Add(match)) expandedValues.Add(match);
                }

                expansionNotes.Add(new JsonObject
                {
                    ["manifest_key"] = key,
                    ["pattern"] = value,
                    ["match_count"] = matches.Count
                });
            }

            manifest[key] = new JsonArray(expandedValues.Select(value => (JsonNode?)JsonValue.Create(value)).ToArray());
        }

        if (expansionNotes.Count > 0)
        {
            manifest["runtime_wildcard_expansion"] = new JsonObject
            {
                ["supported_tokens"] = new JsonArray(JsonValue.Create("*"), JsonValue.Create("?")),
                ["recursive_glob_supported"] = false,
                ["patterns"] = expansionNotes
            };
        }

        return manifest.ToJsonString(new JsonSerializerOptions
        {
            WriteIndented = true,
            Encoder = JavaScriptEncoder.UnsafeRelaxedJsonEscaping
        });
    }

    private static bool ContainsOverlayWildcard(string value)
        => value.Contains('*') || value.Contains('?');

    private static string? NormalizeOverlayManifestRelativePath(string value)
    {
        var normalized = value.Replace('\\', '/').Trim('/');
        if (string.IsNullOrWhiteSpace(normalized)) return null;
        if (normalized.Contains("//", StringComparison.Ordinal)) return null;
        if (normalized.Contains("://", StringComparison.OrdinalIgnoreCase)) return null;
        if (Path.IsPathRooted(normalized)) return null;

        var parts = normalized.Split('/', StringSplitOptions.RemoveEmptyEntries);
        if (parts.Length == 0 || parts.Any(part => part is "." or "..")) return null;
        return string.Join('/', parts);
    }

    private static List<string> ExpandOverlayWildcardPattern(string overlayRoot, string pattern)
    {
        var normalized = NormalizeOverlayManifestRelativePath(pattern);
        if (normalized is null || normalized.Contains("**", StringComparison.Ordinal)) return new List<string>();

        var slash = normalized.LastIndexOf('/');
        var directoryPart = slash >= 0 ? normalized[..slash] : string.Empty;
        var filePattern = slash >= 0 ? normalized[(slash + 1)..] : normalized;

        if (ContainsOverlayWildcard(directoryPart)) return new List<string>();
        if (string.IsNullOrWhiteSpace(filePattern)) return new List<string>();

        var directoryPath = Path.GetFullPath(Path.Combine(overlayRoot, directoryPart.Replace('/', Path.DirectorySeparatorChar)));
        var allowedRoot = EnsureTrailingSeparator(overlayRoot);
        if (!directoryPath.StartsWith(allowedRoot, StringComparison.OrdinalIgnoreCase)
            && !directoryPath.Equals(overlayRoot, StringComparison.OrdinalIgnoreCase))
        {
            return new List<string>();
        }
        if (!Directory.Exists(directoryPath)) return new List<string>();

        var regexPattern = "^" + Regex.Escape(filePattern)
            .Replace("\\*", ".*")
            .Replace("\\?", ".") + "$";
        var regex = new Regex(regexPattern, RegexOptions.IgnoreCase | RegexOptions.CultureInvariant);

        return Directory.GetFiles(directoryPath, "*", SearchOption.TopDirectoryOnly)
            .Where(File.Exists)
            .Where(file => regex.IsMatch(Path.GetFileName(file)))
            .Select(file => Path.GetRelativePath(overlayRoot, file).Replace('\\', '/'))
            .OrderBy(file => file, StringComparer.OrdinalIgnoreCase)
            .ToList();
    }

    private static string[] ListOverlayIds(string overlaysDir)
    {
        Directory.CreateDirectory(overlaysDir);
        return Directory.GetDirectories(overlaysDir)
            .Select(Path.GetFileName)
            .Where(id => SafeOverlayId(id) is not null)
            .Select(id => id!)
            .OrderBy(id => id, StringComparer.OrdinalIgnoreCase)
            .ToArray();
    }

    private static string? SafeOverlayId(string? overlayId)
    {
        if (string.IsNullOrWhiteSpace(overlayId)) return null;
        var id = overlayId.Trim();
        return Regex.IsMatch(id, "^[A-Za-z0-9_-]+$") ? id : null;
    }

    private static string? SafeOverlayPath(string overlaysDir, string overlayId, string name, string[] allowedExtensions)
    {
        var id = SafeOverlayId(overlayId);
        if (id is null || string.IsNullOrWhiteSpace(name)) return null;

        var normalized = Uri.UnescapeDataString(name).Replace('\\', '/').Trim('/');
        if (string.IsNullOrWhiteSpace(normalized)) return null;
        if (normalized.Contains("://", StringComparison.OrdinalIgnoreCase)) return null;
        if (Path.IsPathRooted(normalized)) return null;

        var parts = normalized.Split('/', StringSplitOptions.RemoveEmptyEntries);
        if (parts.Length == 0) return null;
        if (parts.Any(part => part is "." or "..")) return null;
        if (parts.Any(part => part.IndexOfAny(Path.GetInvalidFileNameChars()) >= 0)) return null;

        var fileName = parts[^1];
        var ext = Path.GetExtension(fileName);
        if (string.IsNullOrWhiteSpace(ext)) return null;
        if (!allowedExtensions.Any(x => ext.Equals(x, StringComparison.OrdinalIgnoreCase))) return null;

        var overlayRoot = Path.GetFullPath(Path.Combine(overlaysDir, id));
        var full = Path.GetFullPath(Path.Combine(overlayRoot, Path.Combine(parts)));
        var allowed = EnsureTrailingSeparator(overlayRoot);

        return full.StartsWith(allowed, StringComparison.OrdinalIgnoreCase)
            ? full
            : null;
    }

    private static string[] ListJsonFiles(IReadOnlyList<DataFolder> folders)
    {
        var files = new List<string>();

        foreach (var folder in folders)
        {
            Directory.CreateDirectory(folder.FullPath);

            foreach (var file in Directory.GetFiles(folder.FullPath, "*.json", SearchOption.AllDirectories))
            {
                var relative = ToRelativeApiPath(folder.FullPath, file);
                if (string.IsNullOrWhiteSpace(relative)) continue;

                files.Add(folder.IsPrimary
                    ? relative
                    : $"{folder.ApiPrefix}/{relative}");
            }
        }

        return files
            .Distinct(StringComparer.OrdinalIgnoreCase)
            .OrderBy(x => x, StringComparer.OrdinalIgnoreCase)
            .ToArray();
    }


    private static string[] ListJsonFiles(string dir)
    {
        Directory.CreateDirectory(dir);
        return Directory.GetFiles(dir, "*.json", SearchOption.AllDirectories)
            .Select(file => ToRelativeApiPath(dir, file))
            .Where(x => !string.IsNullOrWhiteSpace(x))
            .Distinct(StringComparer.OrdinalIgnoreCase)
            .OrderBy(x => x, StringComparer.OrdinalIgnoreCase)
            .ToArray()!;
    }


    private static string[] ListMarkdownFiles(string dir)
    {
        Directory.CreateDirectory(dir);
        return Directory.EnumerateFiles(dir, "*", SearchOption.AllDirectories)
            .Where(path => IsManagedMarkdownFileName(Path.GetFileName(path)))
            .Select(path => ToRelativeApiPath(dir, path))
            .Where(x => !string.IsNullOrWhiteSpace(x))
            .Distinct(StringComparer.OrdinalIgnoreCase)
            .OrderBy(x => x, StringComparer.OrdinalIgnoreCase)
            .ToArray()!;
    }

    private static async Task WriteJsonAsync(string path, JsonElement json)
    {
        // v0.9-json-utf8-human-readable-save:
        // Data JSON is the human/AI collaboration source of truth, so Japanese text must remain directly readable.
        // UnicodeRanges.All avoids the default non-ASCII \uXXXX escaping while keeping the JSON encoder boundary explicit.
        var formatted = JsonSerializer.Serialize(json, HumanReadableJsonOptions);
        await File.WriteAllTextAsync(path, formatted, new UTF8Encoding(false));
    }

    private static string? ResolveOpenJsonPath(
        string kind,
        string name,
        IReadOnlyList<DataFolder> dataFolders,
        string defsDir,
        string overlaysDir)
    {
        // v0.17.9.1-json-folder-open-overlay:
        // Overlay選択値は datalist 上では overlay/{id}/data/foo.json や overlay/{id}/view_defs/foo.json として流れる。
        // /api/data や /api/defs の管理フォルダーではなく studio_overlays/{id}/... が実体なので、
        // フォルダーOpen時も Overlay API名として安全に解決する。
        var overlayPath = SafeStudioOverlayApiJsonPath(overlaysDir, name);
        if (overlayPath is not null) return overlayPath;

        return kind switch
        {
            "data" => SafeDataPath(dataFolders, name, preferExisting: true),
            "viewdef" or "def" or "defs" => SafeJsonPath(defsDir, name),
            _ => null
        };
    }

    private static string? SafeStudioOverlayApiJsonPath(string overlaysDir, string name)
    {
        if (string.IsNullOrWhiteSpace(name)) return null;

        var normalized = Uri.UnescapeDataString(name).Replace('\\', '/').Trim('/');
        if (string.IsNullOrWhiteSpace(normalized)) return null;
        if (!normalized.StartsWith("overlay/", StringComparison.OrdinalIgnoreCase)) return null;
        if (normalized.Contains("://", StringComparison.OrdinalIgnoreCase)) return null;
        if (Path.IsPathRooted(normalized)) return null;

        var parts = normalized.Split('/', StringSplitOptions.RemoveEmptyEntries);
        if (parts.Length < 4) return null;
        if (!parts[0].Equals("overlay", StringComparison.OrdinalIgnoreCase)) return null;

        var overlayId = parts[1];
        var relative = string.Join('/', parts.Skip(2));
        return SafeOverlayPath(overlaysDir, overlayId, relative, new[] { ".json" });
    }

    private static string? SafeDataPath(IReadOnlyList<DataFolder> folders, string name, bool preferExisting)
    {
        if (string.IsNullOrWhiteSpace(name)) return null;

        var normalized = Uri.UnescapeDataString(name).Replace('\\', '/').Trim('/');
        if (string.IsNullOrWhiteSpace(normalized)) return null;
        if (!normalized.EndsWith(".json", StringComparison.OrdinalIgnoreCase)) return null;
        if (normalized.Contains("://", StringComparison.OrdinalIgnoreCase)) return null;
        if (Path.IsPathRooted(normalized)) return null;
        if (normalized.Split('/', StringSplitOptions.RemoveEmptyEntries).Any(part => part is "." or "..")) return null;

        // 旧互換: ファイル名だけ指定された場合は、既存ファイルを全DataFoldersから探す。
        // 保存時に既存が見つからない場合は、先頭のDataFolder(data/json)へ保存する。
        if (!normalized.Contains('/'))
        {
            if (preferExisting)
            {
                foreach (var folder in folders)
                {
                    var existing = SafeJsonPath(folder.FullPath, normalized);
                    if (existing is not null && File.Exists(existing)) return existing;
                }
            }

            return SafeJsonPath(folders[0].FullPath, normalized);
        }

        // DataFoldersで外部フォルダーが定義されている場合は、接頭辞つき相対パスとして扱う。
        // Primary(data/json)配下のサブフォルダーは、接頭辞なしの相対パスとして扱う。
        foreach (var folder in folders.Where(f => !f.IsPrimary).OrderByDescending(f => f.ApiPrefix.Length))
        {
            var prefix = folder.ApiPrefix + "/";
            if (!normalized.StartsWith(prefix, StringComparison.OrdinalIgnoreCase)) continue;

            var relative = normalized[prefix.Length..];
            return SafeJsonPath(folder.FullPath, relative);
        }

        if (preferExisting)
        {
            var primaryExisting = SafeJsonPath(folders[0].FullPath, normalized);
            if (primaryExisting is not null && File.Exists(primaryExisting)) return primaryExisting;
        }

        return SafeJsonPath(folders[0].FullPath, normalized);
    }


    private static string? ToApiName(IReadOnlyList<DataFolder> folders, string path)
    {
        var fullPath = Path.GetFullPath(path);

        foreach (var folder in folders.OrderByDescending(f => f.FullPath.Length))
        {
            var folderPath = EnsureTrailingSeparator(Path.GetFullPath(folder.FullPath));
            if (!fullPath.StartsWith(folderPath, StringComparison.OrdinalIgnoreCase)) continue;

            var relative = ToRelativeApiPath(folder.FullPath, fullPath);
            if (string.IsNullOrWhiteSpace(relative)) return null;
            return folder.IsPrimary ? relative : $"{folder.ApiPrefix}/{relative}";
        }

        return null;
    }


    private static string? SafeJsonPath(string baseDir, string name)
    {
        if (string.IsNullOrWhiteSpace(name)) return null;

        var normalized = Uri.UnescapeDataString(name).Replace('\\', '/').Trim('/');
        if (string.IsNullOrWhiteSpace(normalized)) return null;
        if (!normalized.EndsWith(".json", StringComparison.OrdinalIgnoreCase)) return null;
        if (normalized.Contains("://", StringComparison.OrdinalIgnoreCase)) return null;
        if (Path.IsPathRooted(normalized)) return null;
        if (normalized.Split('/', StringSplitOptions.RemoveEmptyEntries).Any(part => part is "." or "..")) return null;

        var full = Path.GetFullPath(Path.Combine(baseDir, normalized.Replace('/', Path.DirectorySeparatorChar)));
        var allowed = EnsureTrailingSeparator(Path.GetFullPath(baseDir));

        return full.StartsWith(allowed, StringComparison.OrdinalIgnoreCase)
            ? full
            : null;
    }


    private static string? SafeMarkdownPath(string baseDir, string name)
    {
        if (string.IsNullOrWhiteSpace(name)) return null;

        var normalized = Uri.UnescapeDataString(name).Replace('\\', '/').Trim('/');
        if (string.IsNullOrWhiteSpace(normalized)) return null;
        if (normalized.Contains("://", StringComparison.OrdinalIgnoreCase)) return null;
        if (Path.IsPathRooted(normalized)) return null;

        var parts = normalized.Split('/', StringSplitOptions.RemoveEmptyEntries);
        if (parts.Length == 0) return null;
        if (parts.Any(part => part is "." or "..")) return null;
        if (parts.Any(part => part.IndexOfAny(Path.GetInvalidFileNameChars()) >= 0)) return null;

        // v0.16.10:
        // Markdown本文は data/markdown 配下のサブフォルダ管理を許可する。
        // ただし任意ファイル保存口にはしない。末尾ファイル名が .md/.markdown、
        // または本文に紐づく .comments.json の場合だけ許可する。
        var fileName = parts[^1];
        if (!IsManagedMarkdownFileName(fileName) && !IsMarkdownCommentSidecarName(fileName)) return null;

        var full = Path.GetFullPath(Path.Combine(baseDir, Path.Combine(parts)));
        var allowed = EnsureTrailingSeparator(Path.GetFullPath(baseDir));

        return full.StartsWith(allowed, StringComparison.OrdinalIgnoreCase)
            ? full
            : null;
    }

    private static string? SafeMarkdownRootFileName(string name)
    {
        if (string.IsNullOrWhiteSpace(name)) return null;
        var normalized = Uri.UnescapeDataString(name).Replace('\\', '/').Trim('/');
        var fileName = normalized.Split('/', StringSplitOptions.RemoveEmptyEntries).LastOrDefault();
        if (string.IsNullOrWhiteSpace(fileName)) return null;
        if (fileName is "." or "..") return null;
        if (fileName.IndexOfAny(Path.GetInvalidFileNameChars()) >= 0) return null;
        return IsManagedMarkdownFileName(fileName) ? fileName : null;
    }

    private static MarkdownOpenDialogResult ShowMarkdownOpenDialog()
    {
        MarkdownOpenDialogResult? result = null;
        Exception? error = null;

        var thread = new Thread(() =>
        {
            try
            {
                using var dialog = new OpenFileDialog
                {
                    Title = "Markdown を開く",
                    DefaultExt = "md",
                    CheckFileExists = true,
                    RestoreDirectory = true,
                    Filter = "Markdown files (*.md;*.markdown)|*.md;*.markdown|Text files (*.txt)|*.txt|All files (*.*)|*.*"
                };

                var documents = Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments);
                if (!string.IsNullOrWhiteSpace(documents) && Directory.Exists(documents))
                {
                    dialog.InitialDirectory = documents;
                }

                if (ShowMarkdownOpenFileDialogForeground(dialog) != DialogResult.OK)
                {
                    result = new MarkdownOpenDialogResult(true, null, null, null, null, null, null, null);
                    return;
                }

                var selectedPath = dialog.FileName;
                var content = File.ReadAllText(selectedPath, Encoding.UTF8);
                var sidecarPath = selectedPath + ".comments.json";
                var sidecarContent = File.Exists(sidecarPath)
                    ? NormalizeReadableJsonContent(File.ReadAllText(sidecarPath, Encoding.UTF8))
                    : null;

                result = new MarkdownOpenDialogResult(
                    false,
                    selectedPath,
                    Path.GetFileName(selectedPath),
                    content,
                    File.Exists(sidecarPath) ? sidecarPath : null,
                    File.Exists(sidecarPath) ? Path.GetFileName(sidecarPath) : null,
                    sidecarContent,
                    null);
            }
            catch (Exception ex)
            {
                error = ex;
            }
        });

        thread.SetApartmentState(ApartmentState.STA);
        thread.Start();
        thread.Join();

        if (error is not null)
        {
            return new MarkdownOpenDialogResult(false, null, null, null, null, null, null, error.Message);
        }

        return result ?? new MarkdownOpenDialogResult(true, null, null, null, null, null, null, null);
    }

    private static MarkdownSaveAsDialogResult ShowMarkdownSaveAsDialog(string markdownDir, MarkdownSaveRequest req)
    {
        MarkdownSaveAsDialogResult? result = null;
        Exception? error = null;

        var suggestedName = req.Name;
        var content = req.Content ?? string.Empty;

        var thread = new Thread(() =>
        {
            try
            {
                using var dialog = new SaveFileDialog
                {
                    Title = "Markdown に名前を付けて保存",
                    FileName = SafeMarkdownSaveDialogFileName(suggestedName),
                    DefaultExt = "md",
                    AddExtension = true,
                    OverwritePrompt = true,
                    RestoreDirectory = true,
                    Filter = "Markdown files (*.md;*.markdown)|*.md;*.markdown|Text files (*.txt)|*.txt|All files (*.*)|*.*"
                };

                var documents = Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments);
                if (!string.IsNullOrWhiteSpace(documents) && Directory.Exists(documents))
                {
                    dialog.InitialDirectory = documents;
                }

                // mdViewer v0.16.14.2: APサーバスレッドから出したSaveFileDialogは、親ウィンドウが無いと
                // Chrome/Edgeの背面に回ることがある。現在前面にいるブラウザHWNDを
                // ownerとして渡し、ダイアログをブラウザの前面に固定する。
                if (ShowMarkdownSaveFileDialogForeground(dialog) != DialogResult.OK)
                {
                    result = new MarkdownSaveAsDialogResult(true, null, null, null);
                    return;
                }

                var selectedPath = dialog.FileName;
                Directory.CreateDirectory(Path.GetDirectoryName(selectedPath)!);
                File.WriteAllText(selectedPath, content, new UTF8Encoding(false));

                // mdViewer v0.16.14.3: 「名前を付けて保存」はMarkdown本体だけではなく、
                // コメントSidecar JSONも同じフォルダへ並べて保存する。
                // 保存先: xxx.md -> xxx.md.comments.json
                // Sidecar本文はフロントから渡された最新内容を優先し、無い場合は data/markdown 側の既存Sidecarをコピーする。
                var sidecar = SaveMarkdownCommentSidecarAlongside(markdownDir, req, selectedPath);

                result = new MarkdownSaveAsDialogResult(
                    false,
                    selectedPath,
                    Path.GetFileName(selectedPath),
                    null,
                    sidecar.Saved,
                    sidecar.SavedPath,
                    sidecar.FileName,
                    sidecar.Error);
            }
            catch (Exception ex)
            {
                error = ex;
            }
        });

        thread.SetApartmentState(ApartmentState.STA);
        thread.Start();
        thread.Join();

        if (error is not null)
        {
            return new MarkdownSaveAsDialogResult(false, null, null, error.Message);
        }

        return result ?? new MarkdownSaveAsDialogResult(true, null, null, null);
    }

    private static MarkdownSidecarSaveResult SaveMarkdownCommentSidecarAlongside(string markdownDir, MarkdownSaveRequest req, string selectedMarkdownPath)
    {
        try
        {
            var sidecarContent = FirstNonBlank(req.SidecarContent, ReadManagedMarkdownSidecarContent(markdownDir, req));
            if (string.IsNullOrWhiteSpace(sidecarContent)) return MarkdownSidecarSaveResult.NotFound;

            var sidecarPath = selectedMarkdownPath + ".comments.json";
            var sidecarFileName = Path.GetFileName(sidecarPath);
            var targetFileName = Path.GetFileName(selectedMarkdownPath);
            var exportContent = NormalizeExportedMarkdownCommentSidecarContent(sidecarContent, targetFileName, sidecarFileName);

            Directory.CreateDirectory(Path.GetDirectoryName(sidecarPath)!);
            File.WriteAllText(sidecarPath, exportContent, new UTF8Encoding(false));
            return new MarkdownSidecarSaveResult(true, sidecarPath, sidecarFileName, null);
        }
        catch (Exception ex)
        {
            return new MarkdownSidecarSaveResult(false, null, null, ex.Message);
        }
    }

    private static string? ReadManagedMarkdownSidecarContent(string markdownDir, MarkdownSaveRequest req)
    {
        foreach (var candidateName in EnumerateMarkdownSidecarCandidateNames(req))
        {
            var path = SafeMarkdownPath(markdownDir, candidateName);
            if (path is not null && File.Exists(path)) return File.ReadAllText(path);
        }

        return null;
    }

    private static IEnumerable<string> EnumerateMarkdownSidecarCandidateNames(MarkdownSaveRequest req)
    {
        var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);

        foreach (var value in AddIterator(req.SidecarName)) yield return value;
        foreach (var value in AddIterator(req.SourceName)) yield return value;
        foreach (var value in AddIterator(req.Name)) yield return value;

        IEnumerable<string> AddIterator(string? value)
        {
            if (string.IsNullOrWhiteSpace(value)) yield break;
            var normalized = Uri.UnescapeDataString(value).Replace('\\', '/').Trim('/');
            if (string.IsNullOrWhiteSpace(normalized)) yield break;
            if (normalized.StartsWith("data/markdown/", StringComparison.OrdinalIgnoreCase)) normalized = normalized["data/markdown/".Length..];
            if (normalized.StartsWith("markdown/", StringComparison.OrdinalIgnoreCase)) normalized = normalized["markdown/".Length..];
            if (normalized.Contains("://", StringComparison.OrdinalIgnoreCase) || normalized.StartsWith("//") || Path.IsPathRooted(normalized)) yield break;
            if (!normalized.EndsWith(".comments.json", StringComparison.OrdinalIgnoreCase)) normalized += ".comments.json";
            if (seen.Add(normalized)) yield return normalized;
        }
    }

    private static readonly JsonSerializerOptions HumanReadableJsonOptions = new()
    {
        WriteIndented = true,
        Encoder = JavaScriptEncoder.Create(UnicodeRanges.All)
    };


    private static readonly TimeZoneInfo StudioTimeZone = ResolveStudioTimeZone();

    private static TimeZoneInfo ResolveStudioTimeZone()
    {
        foreach (var id in new[] { "Tokyo Standard Time", "Asia/Tokyo" })
        {
            try { return TimeZoneInfo.FindSystemTimeZoneById(id); } catch { }
        }
        return TimeZoneInfo.Local;
    }

    private static DateTimeOffset StudioNow() => TimeZoneInfo.ConvertTime(DateTimeOffset.UtcNow, StudioTimeZone);

    private static string FormatStudioDateTime(DateTimeOffset? value = null, bool includeMilliseconds = false)
    {
        var dt = TimeZoneInfo.ConvertTime(value ?? DateTimeOffset.UtcNow, StudioTimeZone);
        return includeMilliseconds
            ? dt.ToString("yyyy-MM-dd_HH:mm:ss.fff")
            : dt.ToString("yyyy-MM-dd_HH:mm:ss");
    }

    private static string FormatStudioFileTimestamp(DateTimeOffset? value = null, bool includeMilliseconds = false)
    {
        var dt = TimeZoneInfo.ConvertTime(value ?? DateTimeOffset.UtcNow, StudioTimeZone);
        return includeMilliseconds
            ? dt.ToString("yyyyMMdd_HHmmss_fff")
            : dt.ToString("yyyyMMdd_HHmmss");
    }

    private static string FormatStudioIsoJst(DateTimeOffset? value = null, bool includeMilliseconds = false)
    {
        var dt = TimeZoneInfo.ConvertTime(value ?? DateTimeOffset.UtcNow, StudioTimeZone);
        return includeMilliseconds
            ? dt.ToString("yyyy-MM-dd'T'HH:mm:ss.fffzzz")
            : dt.ToString("yyyy-MM-dd'T'HH:mm:sszzz");
    }

    private static string NormalizeReadableJsonContent(string rawContent)
    {
        try
        {
            var node = JsonNode.Parse(rawContent);
            return node is null ? rawContent : node.ToJsonString(HumanReadableJsonOptions);
        }
        catch
        {
            return rawContent;
        }
    }

    private static string NormalizeExportedMarkdownCommentSidecarContent(string rawContent, string targetFileName, string sidecarFileName)
    {
        try
        {
            var node = JsonNode.Parse(rawContent) as JsonObject;
            if (node is null) return rawContent;

            node["target_file"] = targetFileName;
            node["sidecar_name"] = sidecarFileName;
            node["updated_at"] = FormatStudioDateTime();

            return node.ToJsonString(HumanReadableJsonOptions);
        }
        catch
        {
            return rawContent;
        }
    }


    private static void OpenExplorerAndBringToFront(string folder, string? selectedPath)
    {
        var arguments = !string.IsNullOrWhiteSpace(selectedPath)
            ? $"/n,/select,\"{selectedPath}\""
            : $"/n,\"{folder}\"";

        Process? process = null;
        try
        {
            process = Process.Start(new ProcessStartInfo
            {
                FileName = "explorer.exe",
                Arguments = arguments,
                UseShellExecute = true
            });
        }
        catch
        {
            // Explorer起動失敗時は呼び出し元で例外にしない。
            // フォルダーOpenは補助操作なので、既存処理の安定性を優先する。
        }

        // Windows 11ではExplorerが既存プロセス/既存ウィンドウを再利用し、裏に隠れることがある。
        // まずProcessのMainWindowHandleを試し、だめならShell.Applicationで対象フォルダーのExplorerウィンドウを探して前面化する。
        try
        {
            if (process is not null)
            {
                try { process.WaitForInputIdle(800); } catch { }
                process.Refresh();
                if (process.MainWindowHandle != IntPtr.Zero)
                {
                    ForceWindowToForeground(process.MainWindowHandle);
                    return;
                }
            }
        }
        catch
        {
            // COM探索へフォールバックする。
        }

        for (var i = 0; i < 8; i++)
        {
            Thread.Sleep(150);
            if (TryBringExplorerWindowForFolderToForeground(folder)) return;
        }
    }

    private static bool TryBringExplorerWindowForFolderToForeground(string folder)
    {
        object? shellObject = null;
        try
        {
            var shellType = Type.GetTypeFromProgID("Shell.Application");
            if (shellType is null) return false;

            shellObject = Activator.CreateInstance(shellType);
            if (shellObject is null) return false;

            var targetFolder = NormalizeComparablePath(folder);
            if (string.IsNullOrWhiteSpace(targetFolder)) return false;

            dynamic shell = shellObject;
            foreach (var window in shell.Windows())
            {
                try
                {
                    var fullName = Convert.ToString(window.FullName) ?? string.Empty;
                    if (!fullName.EndsWith("explorer.exe", StringComparison.OrdinalIgnoreCase)) continue;

                    var locationUrl = Convert.ToString(window.LocationURL) ?? string.Empty;
                    var windowFolder = ExplorerLocationUrlToLocalPath(locationUrl);
                    if (string.IsNullOrWhiteSpace(windowFolder)) continue;
                    if (!PathsEqual(windowFolder, targetFolder)) continue;

                    var handle = new IntPtr(Convert.ToInt64(window.HWND));
                    ForceWindowToForeground(handle);
                    return true;
                }
                catch
                {
                    // 対象外のExplorer/特殊フォルダーは無視する。
                }
            }
        }
        catch
        {
            return false;
        }
        finally
        {
            try
            {
                if (shellObject is not null && Marshal.IsComObject(shellObject)) Marshal.FinalReleaseComObject(shellObject);
            }
            catch { }
        }

        return false;
    }

    private static string? ExplorerLocationUrlToLocalPath(string locationUrl)
    {
        if (string.IsNullOrWhiteSpace(locationUrl)) return null;
        if (!Uri.TryCreate(locationUrl, UriKind.Absolute, out var uri) || !uri.IsFile) return null;
        return NormalizeComparablePath(uri.LocalPath);
    }

    private static string? NormalizeComparablePath(string? path)
    {
        if (string.IsNullOrWhiteSpace(path)) return null;
        try
        {
            return Path.GetFullPath(path).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
        }
        catch
        {
            return null;
        }
    }

    private static bool PathsEqual(string? left, string? right)
    {
        var a = NormalizeComparablePath(left);
        var b = NormalizeComparablePath(right);
        return !string.IsNullOrWhiteSpace(a)
            && !string.IsNullOrWhiteSpace(b)
            && string.Equals(a, b, StringComparison.OrdinalIgnoreCase);
    }

    private static DialogResult ShowMarkdownOpenFileDialogForeground(OpenFileDialog dialog)
    {
        var foregroundHandle = GetForegroundWindow();
        if (foregroundHandle != IntPtr.Zero)
        {
            ForceWindowToForeground(foregroundHandle);
            return dialog.ShowDialog(new ExternalWin32Window(foregroundHandle));
        }

        using var owner = new Form
        {
            ShowInTaskbar = false,
            TopMost = true,
            StartPosition = FormStartPosition.Manual,
            Size = new Size(1, 1),
            Location = new Point(-32000, -32000)
        };
        owner.Load += (_, _) =>
        {
            owner.BeginInvoke(new Action(() =>
            {
                owner.Activate();
                owner.BringToFront();
            }));
        };
        owner.Show();
        owner.Activate();
        return dialog.ShowDialog(owner);
    }

    private static DialogResult ShowMarkdownSaveFileDialogForeground(SaveFileDialog dialog)
    {
        var foregroundHandle = GetForegroundWindow();
        if (foregroundHandle != IntPtr.Zero)
        {
            ForceWindowToForeground(foregroundHandle);
            return dialog.ShowDialog(new ExternalWin32Window(foregroundHandle));
        }

        using var owner = new Form
        {
            Text = "FRB Studio - Save As",
            ShowInTaskbar = false,
            TopMost = true,
            StartPosition = FormStartPosition.CenterScreen,
            Size = new Size(1, 1),
            FormBorderStyle = FormBorderStyle.None,
            Opacity = 0.01
        };

        owner.Show();
        ForceWindowToForeground(owner.Handle);
        owner.Activate();

        return dialog.ShowDialog(owner);
    }

    private static void ForceWindowToForeground(IntPtr handle)
    {
        if (handle == IntPtr.Zero) return;
        try
        {
            ShowWindow(handle, SW_SHOWNORMAL);
            SetWindowPos(handle, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW);
            SetForegroundWindow(handle);
            SetWindowPos(handle, HWND_NOTOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW);
        }
        catch
        {
            // 前面化はOSのフォーカス制御に拒否されることがある。
            // その場合もShowDialog自体は継続する。
        }
    }

    private sealed class ExternalWin32Window : IWin32Window
    {
        public ExternalWin32Window(IntPtr handle)
        {
            Handle = handle;
        }

        public IntPtr Handle { get; }
    }

    private static readonly IntPtr HWND_TOPMOST = new(-1);
    private static readonly IntPtr HWND_NOTOPMOST = new(-2);
    private const int SW_SHOWNORMAL = 1;
    private const uint SWP_NOMOVE = 0x0002;
    private const uint SWP_NOSIZE = 0x0001;
    private const uint SWP_SHOWWINDOW = 0x0040;

    [DllImport("user32.dll")]
    private static extern IntPtr GetForegroundWindow();

    [DllImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool SetForegroundWindow(IntPtr hWnd);

    [DllImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

    [DllImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int x, int y, int cx, int cy, uint flags);

    private static string SafeMarkdownSaveDialogFileName(string? suggestedName)
    {
        var name = string.IsNullOrWhiteSpace(suggestedName) ? "frb_thought.md" : suggestedName;
        name = Uri.UnescapeDataString(name).Replace('\\', '/').Split('/', StringSplitOptions.RemoveEmptyEntries).LastOrDefault() ?? "frb_thought.md";
        foreach (var ch in Path.GetInvalidFileNameChars()) name = name.Replace(ch, '_');
        name = name.Trim();
        if (string.IsNullOrWhiteSpace(name)) name = "frb_thought.md";
        if (!IsManagedMarkdownFileName(name) && !name.EndsWith(".txt", StringComparison.OrdinalIgnoreCase)) name += ".md";
        return name;
    }

    private static bool IsManagedMarkdownFileName(string name)
    {
        return name.EndsWith(".md", StringComparison.OrdinalIgnoreCase) ||
               name.EndsWith(".markdown", StringComparison.OrdinalIgnoreCase);
    }

    private static bool IsMarkdownCommentSidecarName(string name)
    {
        return name.EndsWith(".md.comments.json", StringComparison.OrdinalIgnoreCase) ||
               name.EndsWith(".markdown.comments.json", StringComparison.OrdinalIgnoreCase);
    }

    private static string ToRelativeApiPath(string baseDir, string path)
    {
        var baseFull = EnsureTrailingSeparator(Path.GetFullPath(baseDir));
        var fileFull = Path.GetFullPath(path);
        if (!fileFull.StartsWith(baseFull, StringComparison.OrdinalIgnoreCase)) return string.Empty;

        return Path.GetRelativePath(baseFull, fileFull)
            .Replace(Path.DirectorySeparatorChar, '/')
            .Replace(Path.AltDirectorySeparatorChar, '/')
            .Trim('/');
    }

    private static string EnsureTrailingSeparator(string path)
    {
        return path.EndsWith(Path.DirectorySeparatorChar)
            ? path
            : path + Path.DirectorySeparatorChar;
    }

    internal static void OpenBrowser(string url)
    {
        try
        {
            Process.Start(new ProcessStartInfo(url) { UseShellExecute = true });
        }
        catch { }
    }

    internal static void OpenFolder(string path)
    {
        try
        {
            Directory.CreateDirectory(path);
            Process.Start(new ProcessStartInfo(path) { UseShellExecute = true });
        }
        catch { }
    }

    internal static Icon LoadAppIcon()
    {
        var root = AppContext.BaseDirectory;
        var candidates = new[]
        {
            Path.Combine(root, "FRB_tray.ico"),
            Path.Combine(root, "FRB.ico"),
            Path.Combine(AppContext.BaseDirectory, "wwwroot", "FRB_tray.ico"),
            Path.Combine(AppContext.BaseDirectory, "wwwroot", "FRB.ico")
        };

        foreach (var path in candidates)
        {
            try
            {
                if (File.Exists(path)) return new Icon(path);
            }
            catch { }
        }

        return SystemIcons.Application;
    }
}

internal sealed class FrbStudioTrayContext : ApplicationContext
{
    private readonly WebApplication _app;
    private readonly string _url;
    private readonly NotifyIcon _notifyIcon;

    public FrbStudioTrayContext(WebApplication app, string url)
    {
        _app = app;
        _url = url;

        var root = AppContext.BaseDirectory;
        var dataDir = Path.Combine(root, "data");
        var jsonDir = Path.Combine(dataDir, "json");
        var markdownDir = Path.Combine(dataDir, "markdown");
        var defsDir = Path.Combine(root, "defs");
        var testsScreenStateDir = Path.Combine(root, "tests_screen_state");
        var testResultsDiffDir = Path.Combine(root, "tests_screen_state", "test_results", "diff");

        var menu = new ContextMenuStrip();
        menu.Items.Add("FRB Studio を開く", null, (_, _) => Program.OpenBrowser(_url));
        menu.Items.Add("data フォルダーを開く", null, (_, _) => Program.OpenFolder(dataDir));
        menu.Items.Add("－ json フォルダーを開く", null, (_, _) => Program.OpenFolder(jsonDir));
        menu.Items.Add("－ markdown フォルダーを開く", null, (_, _) => Program.OpenFolder(markdownDir));
        menu.Items.Add("defs フォルダーを開く", null, (_, _) => Program.OpenFolder(defsDir));
        menu.Items.Add(new ToolStripSeparator());
        menu.Items.Add("終了", null, async (_, _) => await ExitAsync());

        _notifyIcon = new NotifyIcon
        {
            Icon = Program.LoadAppIcon(),
            Text = "FRB Studio - No-Code JSON Studio",
            ContextMenuStrip = menu,
            Visible = true
        };

        _notifyIcon.DoubleClick += (_, _) => Program.OpenBrowser(_url);
        _notifyIcon.ShowBalloonTip(
            1500,
            "FRB Studio 起動中",
            "右クリックでメニュー、ダブルクリックで開きます。",
            ToolTipIcon.Info);
    }

    private async Task ExitAsync()
    {
        _notifyIcon.Visible = false;
        try { await _app.StopAsync(TimeSpan.FromSeconds(3)); } catch { }
        Application.Exit();
    }

    protected override void Dispose(bool disposing)
    {
        if (disposing)
        {
            _notifyIcon.Visible = false;
            _notifyIcon.Dispose();
        }

        base.Dispose(disposing);
    }
}

internal sealed class CommandRunRequest
{
    [JsonPropertyName("command_profile_id")]
    public string? CommandProfileId { get; set; }

    [JsonPropertyName("profile_id")]
    public string? ProfileId { get; set; }

    [JsonPropertyName("mode")]
    public string? Mode { get; set; }

    [JsonPropertyName("range")]
    public string? Range { get; set; }

    [JsonPropertyName("from_ref")]
    public string? FromRef { get; set; }

    [JsonPropertyName("to_ref")]
    public string? ToRef { get; set; }

    [JsonPropertyName("from_file")]
    public string? FromFile { get; set; }

    [JsonPropertyName("to_file")]
    public string? ToFile { get; set; }

    [JsonPropertyName("output_path_display")]
    public string? OutputPathDisplay { get; set; }

    [JsonPropertyName("output_path")]
    public string? OutputPath { get; set; }

    [JsonPropertyName("unified")]
    public int? Unified { get; set; }

    [JsonPropertyName("max_patch_chars")]
    public int? MaxPatchChars { get; set; }

    [JsonPropertyName("no_patch")]
    public bool? NoPatch { get; set; }

    [JsonPropertyName("test_runner_id")]
    public string? TestRunnerId { get; set; }

    [JsonPropertyName("run_config_id")]
    public string? RunConfigId { get; set; }

    [JsonPropertyName("run_mode")]
    public string? RunMode { get; set; }

    [JsonPropertyName("command_preview")]
    public string? CommandPreview { get; set; }
}

internal sealed record CommandOutputArtifact(
    [property: JsonPropertyName("path")] string Path,
    [property: JsonPropertyName("full_path")] string FullPath,
    [property: JsonPropertyName("exists")] bool Exists,
    [property: JsonPropertyName("kind")] string Kind);

internal sealed record CommandProfile(
    string Id,
    string DisplayName,
    string AppRoot,
    string ScriptPath,
    string OutputPath,
    string WorkingDirectory,
    string PowerShellExe,
    string Kind,
    IReadOnlyList<string> AllowedModes,
    IReadOnlyList<string> AllowedTestRunnerIds,
    int TimeoutSeconds);

internal sealed record DataFolder(string RelativePath, string FullPath, bool IsPrimary)
{
    public string ApiPrefix => RelativePath.Replace('\\', '/').Trim('/');
}

public sealed record OpenJsonFolderRequest(string? Kind, string? Path, bool? SelectFile, bool? select_file);
public sealed record DropJsonRequest(string Name, JsonElement Json);
public sealed record MarkdownSaveRequest(string Name, string? Content, string? SourceName, string? SidecarName, string? SidecarContent);

public sealed record MarkdownOpenDialogResult(
    bool Cancelled,
    string? Path,
    string? FileName,
    string? Content,
    string? SidecarPath,
    string? SidecarFileName,
    string? SidecarContent,
    string? Error);

public sealed record MarkdownSaveAsDialogResult(
    bool Cancelled,
    string? SavedPath,
    string? FileName,
    string? Error,
    bool SidecarSaved = false,
    string? SidecarSavedPath = null,
    string? SidecarFileName = null,
    string? SidecarError = null);

internal sealed record MarkdownSidecarSaveResult(bool Saved, string? SavedPath, string? FileName, string? Error)
{
    public static MarkdownSidecarSaveResult NotFound { get; } = new(false, null, null, null);
}
