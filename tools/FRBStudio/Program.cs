using System.Diagnostics;
using System.Text.Json;
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

        return app;
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
        menu.Items.Add("json フォルダーを開く", null, (_, _) => Program.OpenFolder(jsonDir));
        menu.Items.Add("markdown フォルダーを開く", null, (_, _) => Program.OpenFolder(markdownDir));
        menu.Items.Add("defs フォルダーを開く", null, (_, _) => Program.OpenFolder(defsDir));
        menu.Items.Add("tests_screen_state フォルダーを開く", null, (_, _) => Program.OpenFolder(testsScreenStateDir));
        menu.Items.Add("tests_screen_state/test_results/diff フォルダーを開く", null, (_, _) => Program.OpenFolder(testResultsDiffDir));
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

internal sealed record DataFolder(string RelativePath, string FullPath, bool IsPrimary)
{
    public string ApiPrefix => RelativePath.Replace('\\', '/').Trim('/');
}

public sealed record DropJsonRequest(string Name, JsonElement Json);
public sealed record MarkdownSaveRequest(string Name, string? Content);
