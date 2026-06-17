using System.Diagnostics;
using System.Text.Json;
using System.Windows.Forms;
using System.Drawing;

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
        var builder = WebApplication.CreateBuilder(args);
        builder.WebHost.UseUrls(AppUrl);

        var app = builder.Build();

        var root = AppContext.BaseDirectory;
        var dataRootDir = Path.Combine(root, "data");
        var dataDir = Path.Combine(dataRootDir, "json");
        var markdownDir = Path.Combine(dataRootDir, "markdown");
        var defsDir = Path.Combine(root, "defs");

        Directory.CreateDirectory(dataRootDir);
        Directory.CreateDirectory(dataDir);
        Directory.CreateDirectory(markdownDir);
        Directory.CreateDirectory(defsDir);

        // 旧構成 data/*.json から新構成 data/json/*.json へ、初回だけ安全に移行する。
        foreach (var oldJson in Directory.GetFiles(dataRootDir, "*.json"))
        {
            var dest = Path.Combine(dataDir, Path.GetFileName(oldJson));
            if (!File.Exists(dest)) File.Copy(oldJson, dest);
        }

        app.UseDefaultFiles();
        app.UseStaticFiles();

        app.MapGet("/api/data", () => Results.Json(ListJsonFiles(dataDir)));

        app.MapGet("/api/defs", () => Results.Json(ListJsonFiles(defsDir)));

        app.MapGet("/api/data/{name}", async (string name) =>
        {
            var path = SafeJsonPath(dataDir, name);
            if (path is null || !File.Exists(path)) return Results.NotFound();
            return Results.Text(await File.ReadAllTextAsync(path), "application/json");
        });

        app.MapPost("/api/data/{name}", async (string name, JsonElement json) =>
        {
            var path = SafeJsonPath(dataDir, name);
            if (path is null) return Results.BadRequest("invalid file name");

            await WriteJsonAsync(path, json);
            return Results.Ok(new { saved = name });
        });

        app.MapPost("/api/data/drop", async (DropJsonRequest req) =>
        {
            var path = SafeJsonPath(dataDir, req.Name);
            if (path is null) return Results.BadRequest("invalid file name");

            await WriteJsonAsync(path, req.Json);
            return Results.Ok(new { saved = req.Name });
        });

        app.MapGet("/api/markdown", () => Results.Json(ListMarkdownFiles(markdownDir)));

        app.MapGet("/api/markdown/{name}", async (string name) =>
        {
            var path = SafeMarkdownPath(markdownDir, name);
            if (path is null || !File.Exists(path)) return Results.NotFound();
            return Results.Text(await File.ReadAllTextAsync(path), "text/markdown; charset=utf-8");
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

        app.MapGet("/api/defs/{name}", async (string name) =>
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

    private static string[] ListJsonFiles(string dir)
    {
        Directory.CreateDirectory(dir);
        return Directory.GetFiles(dir, "*.json")
            .Select(Path.GetFileName)
            .Where(x => !string.IsNullOrWhiteSpace(x))
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

    private static string? SafeJsonPath(string baseDir, string name)
    {
        if (string.IsNullOrWhiteSpace(name)) return null;
        if (!name.EndsWith(".json", StringComparison.OrdinalIgnoreCase)) return null;
        if (name.Contains("..") || name.Contains('/') || name.Contains('\\')) return null;

        var full = Path.GetFullPath(Path.Combine(baseDir, name));
        var allowed = Path.GetFullPath(baseDir);

        return full.StartsWith(allowed, StringComparison.OrdinalIgnoreCase) ? full : null;
    }


    private static string? SafeMarkdownPath(string baseDir, string name)
    {
        if (string.IsNullOrWhiteSpace(name)) return null;
        if (!name.EndsWith(".md", StringComparison.OrdinalIgnoreCase) &&
            !name.EndsWith(".markdown", StringComparison.OrdinalIgnoreCase)) return null;
        if (name.Contains("..") || name.Contains('/') || name.Contains('\\')) return null;

        var full = Path.GetFullPath(Path.Combine(baseDir, name));
        var allowed = Path.GetFullPath(baseDir);

        return full.StartsWith(allowed, StringComparison.OrdinalIgnoreCase) ? full : null;
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

        var menu = new ContextMenuStrip();
        menu.Items.Add("FRB Studio を開く", null, (_, _) => Program.OpenBrowser(_url));
        menu.Items.Add("data フォルダーを開く", null, (_, _) => Program.OpenFolder(dataDir));
        menu.Items.Add("json フォルダーを開く", null, (_, _) => Program.OpenFolder(jsonDir));
        menu.Items.Add("markdown フォルダーを開く", null, (_, _) => Program.OpenFolder(markdownDir));
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

public sealed record DropJsonRequest(string Name, JsonElement Json);
public sealed record MarkdownSaveRequest(string Name, string? Content);
