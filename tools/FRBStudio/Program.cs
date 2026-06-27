using System.Diagnostics;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Text.RegularExpressions;
using System.Windows.Forms;
using System.Drawing;
using Microsoft.Extensions.Configuration;

namespace FRBStudio;

internal static class Program
{
    private const string AppUrl = "http://localhost:5055";

    [STAThread]
    private static async Task Main(string[] args)
    {
        Application.EnableVisualStyles();
        Application.SetCompatibleTextRenderingDefault(false);

        WebApplication? app = null;

        try
        {
            app = CreateWebApplication(args);
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

    private static WebApplication CreateWebApplication(string[] args)
    {
        var builder = WebApplication.CreateBuilder(new WebApplicationOptions
        {
            Args = args,
            ContentRootPath = AppContext.BaseDirectory
        });
        builder.WebHost.UseUrls(AppUrl);

        var root = AppContext.BaseDirectory;
        var dataRootDir = Path.Combine(root, "data");
        var dataDir = Path.Combine(dataRootDir, "json");
        var markdownDir = Path.Combine(dataRootDir, "markdown");
        var defsDir = Path.Combine(root, "defs");

        Directory.CreateDirectory(dataRootDir);
        Directory.CreateDirectory(dataDir);
        Directory.CreateDirectory(markdownDir);
        Directory.CreateDirectory(defsDir);

        var dataFolders = ResolveDataFolders(
            builder.Configuration,
            root,
            "FrbStudio:DataFolders",
            new[] { "data/json" });

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
            return Results.Text(await File.ReadAllTextAsync(path), "application/json");
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

        app.MapGet("/api/markdown/{name}", async (string name) =>
        {
            var path = SafeMarkdownPath(markdownDir, name);
            if (path is null || !File.Exists(path)) return Results.NotFound();

            var contentType = IsMarkdownCommentSidecarName(Path.GetFileName(path))
                ? "application/json; charset=utf-8"
                : "text/markdown; charset=utf-8";

            return Results.Text(await File.ReadAllTextAsync(path), contentType);
        });

        app.MapPost("/api/markdown/{name}", async (string name, MarkdownSaveRequest req) =>
        {
            var path = SafeMarkdownPath(markdownDir, name);
            if (path is null) return Results.BadRequest("invalid file name");

            await File.WriteAllTextAsync(path, req.Content ?? string.Empty);
            return Results.Ok(new { saved = name });
        });

        app.MapPost("/api/markdown/drop", async (MarkdownSaveRequest req) =>
        {
            var path = SafeMarkdownPath(markdownDir, req.Name);
            if (path is null) return Results.BadRequest("invalid file name");

            await File.WriteAllTextAsync(path, req.Content ?? string.Empty);
            return Results.Ok(new { saved = req.Name });
        });

        app.MapGet("/api/defs/{**name}", async (string name) =>
        {
            var path = SafeJsonPath(defsDir, name);
            if (path is null || !File.Exists(path)) return Results.NotFound();
            return Results.Text(await File.ReadAllTextAsync(path), "application/json");
        });

        app.MapPost("/api/defs/drop", async (DropJsonRequest req) =>
        {
            var path = SafeJsonPath(defsDir, req.Name);
            if (path is null) return Results.BadRequest("invalid file name");

            await WriteJsonAsync(path, req.Json);
            return Results.Ok(new { saved = req.Name });
        });

        // v0.14.37-git-diff-export-command-profile:
        // Data JSONから任意コマンドを実行させず、Program.cs側で許可したCommandProfileだけを実行する。
        app.MapGet("/api/actions/command/profiles", () => Results.Json(commandProfiles.Values.Select(profile => new
        {
            command_profile_id = profile.Id,
            display_name = profile.DisplayName,
            output_path = profile.OutputPath,
            working_directory = profile.WorkingDirectory,
            timeout_seconds = profile.TimeoutSeconds,
            kind = profile.Kind,
            allowed_modes = profile.AllowedModes,
            allowed_test_runner_ids = profile.AllowedTestRunnerIds
        })));

        app.MapPost("/api/actions/command/run", async (CommandRunRequest req) =>
            await RunCommandProfileAsync(commandProfiles, req));

        return app;
    }

    private static IReadOnlyDictionary<string, CommandProfile> BuildCommandProfiles(IConfiguration config, string root)
    {
        var profiles = new Dictionary<string, CommandProfile>(StringComparer.OrdinalIgnoreCase);

        var gitSection = config.GetSection("FrbStudio:CommandProfiles:GitDiffExport");
        var gitProfile = BuildCommandProfile(
            gitSection,
            root,
            defaultId: "git_diff_export",
            defaultDisplayName: "Export-DiffToJson.ps1 / Git Diff JSON Export",
            defaultScriptPath: "tools/git/Export-DiffToJson.ps1",
            defaultOutputPath: @"F:\FRB_Diff\DiffToJson.json",
            kind: "git_diff_export",
            allowedModes: new[] { "WorkingTree", "Staged", "Head", "Range" },
            allowedTestRunnerIds: Array.Empty<string>(),
            defaultTimeoutSeconds: 30);
        profiles[gitProfile.Id] = gitProfile;

        var testSection = config.GetSection("FrbStudio:CommandProfiles:TestRunner");
        var testProfile = BuildCommandProfile(
            testSection,
            root,
            defaultId: "test_runner",
            defaultDisplayName: "TestRunner.ps1 / Studio Test Runner",
            defaultScriptPath: "tools/test/TestRunner.ps1",
            defaultOutputPath: string.Empty,
            kind: "test_runner",
            allowedModes: Array.Empty<string>(),
            allowedTestRunnerIds: new[] { "playwright_ui", "incident_prompt_copy_action_static" },
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
        var outputPath = string.IsNullOrWhiteSpace(section["OutputPath"])
            ? defaultOutputPath
            : section["OutputPath"]!.Trim();

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
            var value = rawPath.Trim();
            var full = Path.IsPathRooted(value)
                ? Path.GetFullPath(value)
                : Path.GetFullPath(Path.Combine(root, value.Replace('/', Path.DirectorySeparatorChar)));

            if (Directory.Exists(full)) return full;
        }

        return FindNearestGitRoot(root) ?? root;
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

        var outputDisplay = FirstNonBlank(req.OutputPathDisplay, req.OutputPath);
        if (!string.IsNullOrWhiteSpace(outputDisplay) && !IsSameCommandPath(outputDisplay, profile.OutputPath))
        {
            return Results.BadRequest("output_path_display does not match Program.cs CommandProfile output path");
        }

        var mode = (req.Mode ?? string.Empty).Trim();
        var range = (req.Range ?? string.Empty).Trim();
        var fromRef = (req.FromRef ?? string.Empty).Trim();
        var toRef = (req.ToRef ?? string.Empty).Trim();

        if (!ValidateGitDiffMode(mode, profile.AllowedModes))
        {
            return Results.BadRequest($"unsupported mode: {mode}");
        }

        if (mode.Equals("Range", StringComparison.OrdinalIgnoreCase))
        {
            if (!IsSafeGitRef(fromRef) || !IsSafeGitRef(toRef))
            {
                return Results.BadRequest("Range mode requires safe from_ref and to_ref");
            }
            range = $"{fromRef}..{toRef}";
            mode = string.Empty;
        }
        else if (string.IsNullOrWhiteSpace(range) && (!string.IsNullOrWhiteSpace(fromRef) || !string.IsNullOrWhiteSpace(toRef)))
        {
            if (!IsSafeGitRef(fromRef) || !IsSafeGitRef(toRef))
            {
                return Results.BadRequest("from_ref and to_ref must both be safe git refs");
            }
            range = $"{fromRef}..{toRef}";
            mode = string.Empty;
        }

        if (!string.IsNullOrWhiteSpace(range) && !IsSafeGitRange(range))
        {
            return Results.BadRequest("range contains unsupported characters");
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

        var startedAt = DateTimeOffset.Now;
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
        var finishedAt = DateTimeOffset.Now;
        var exitCode = timedOut ? -1 : process.ExitCode;
        var success = !timedOut && exitCode == 0;

        var result = new
        {
            success,
            timed_out = timedOut,
            exit_code = exitCode,
            profile_id = profile.Id,
            display_name = profile.DisplayName,
            mode = string.IsNullOrWhiteSpace(req.Mode) ? "(default)" : req.Mode,
            range,
            output_path = profile.OutputPath,
            working_directory = profile.WorkingDirectory,
            command = new
            {
                file = profile.PowerShellExe,
                args = argsForReport
            },
            stdout = TruncateCommandOutput(stdout, 20000),
            stderr = TruncateCommandOutput(stderr, 20000),
            started_at = startedAt.ToString("yyyy-MM-dd HH:mm:ss zzz"),
            finished_at = finishedAt.ToString("yyyy-MM-dd HH:mm:ss zzz"),
            duration_ms = (long)(finishedAt - startedAt).TotalMilliseconds,
            message = success
                ? $"Git Diff JSONを出力しました: {profile.OutputPath}"
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

        var startedAt = DateTimeOffset.Now;

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
                result_kind = "test_passed",
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
                started_at = startedAt.ToString("yyyy-MM-dd HH:mm:ss zzz"),
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
        var finishedAt = DateTimeOffset.Now;
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
            started_at = startedAt.ToString("yyyy-MM-dd HH:mm:ss zzz"),
            finished_at = finishedAt.ToString("yyyy-MM-dd HH:mm:ss zzz"),
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

    private static bool IsSameCommandPath(string left, string right)
    {
        static string Normalize(string value) => StringValue(value)
            .Trim()
            .Trim('"')
            .Replace('/', '\\')
            .TrimEnd('\\')
            .ToUpperInvariant();

        return Normalize(left) == Normalize(right);
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
        return Directory.GetFiles(dir, "*.md")
            .Concat(Directory.GetFiles(dir, "*.markdown"))
            .Select(Path.GetFileName)
            .Where(x => !string.IsNullOrWhiteSpace(x))
            .Distinct(StringComparer.OrdinalIgnoreCase)
            .OrderBy(x => x, StringComparer.OrdinalIgnoreCase)
            .ToArray()!;
    }

    private static async Task WriteJsonAsync(string path, JsonElement json)
    {
        var formatted = JsonSerializer.Serialize(json, new JsonSerializerOptions
        {
            WriteIndented = true
        });
        await File.WriteAllTextAsync(path, formatted);
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
        if (normalized.Split('/', StringSplitOptions.RemoveEmptyEntries).Any(part => part is "." or "..")) return null;

        // v0.13.3.1:
        // Markdown本文の管理APIで、本文に紐づくSidecarコメントJSONも保存できるようにする。
        // 例: article.md.comments.json / article.markdown.comments.json
        // ただし任意JSON保存口にはしない。Markdown本文に紐づく .comments.json のみ許可する。
        if (normalized.Contains('/')) return null;
        if (!IsManagedMarkdownFileName(normalized) && !IsMarkdownCommentSidecarName(normalized)) return null;

        var full = Path.GetFullPath(Path.Combine(baseDir, normalized));
        var allowed = EnsureTrailingSeparator(Path.GetFullPath(baseDir));

        return EnsureTrailingSeparator(Path.GetDirectoryName(full) ?? string.Empty)
            .StartsWith(allowed, StringComparison.OrdinalIgnoreCase)
            ? full
            : null;
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

public sealed record DropJsonRequest(string Name, JsonElement Json);
public sealed record MarkdownSaveRequest(string Name, string? Content);
