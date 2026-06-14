using System.Diagnostics;
using System.Text.Json;

var builder = WebApplication.CreateBuilder(args);
builder.WebHost.UseUrls("http://localhost:5055");

var app = builder.Build();

var root = AppContext.BaseDirectory;
var dataDir = Path.Combine(root, "data");
var defsDir = Path.Combine(root, "defs");

Directory.CreateDirectory(dataDir);
Directory.CreateDirectory(defsDir);

app.UseDefaultFiles();
app.UseStaticFiles();

app.MapGet("/api/data", () =>
{
    return Results.Json(ListJsonFiles(dataDir));
});

app.MapGet("/api/defs", () =>
{
    return Results.Json(ListJsonFiles(defsDir));
});

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

app.MapGet("/api/defs/{name}", async (string name) =>
{
    var path = SafeJsonPath(defsDir, name);
    if (path is null || !File.Exists(path)) return Results.NotFound();
    return Results.Text(await File.ReadAllTextAsync(path), "application/json");
});

OpenBrowser("http://localhost:5055");
app.Run();

static string[] ListJsonFiles(string dir)
{
    Directory.CreateDirectory(dir);
    return Directory.GetFiles(dir, "*.json")
        .Select(Path.GetFileName)
        .Where(x => !string.IsNullOrWhiteSpace(x))
        .OrderBy(x => x, StringComparer.OrdinalIgnoreCase)
        .ToArray()!;
}

static async Task WriteJsonAsync(string path, JsonElement json)
{
    var formatted = JsonSerializer.Serialize(json, new JsonSerializerOptions
    {
        WriteIndented = true
    });
    await File.WriteAllTextAsync(path, formatted);
}

static string? SafeJsonPath(string baseDir, string name)
{
    if (string.IsNullOrWhiteSpace(name)) return null;
    if (!name.EndsWith(".json", StringComparison.OrdinalIgnoreCase)) return null;
    if (name.Contains("..") || name.Contains('/') || name.Contains('\\')) return null;

    var full = Path.GetFullPath(Path.Combine(baseDir, name));
    var allowed = Path.GetFullPath(baseDir);

    return full.StartsWith(allowed, StringComparison.OrdinalIgnoreCase) ? full : null;
}

static void OpenBrowser(string url)
{
    try
    {
        Process.Start(new ProcessStartInfo(url) { UseShellExecute = true });
    }
    catch { }
}

public sealed record DropJsonRequest(string Name, JsonElement Json);
