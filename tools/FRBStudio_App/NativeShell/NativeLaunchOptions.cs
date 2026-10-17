using System;
using System.IO;

namespace FRBStudio.NativeShell
{
    internal sealed class NativeLaunchOptions
    {
        public string InitialPage { get; private set; }
        public string InitialJsonPath { get; private set; }
        public string InitialMarkdownPath { get; private set; }

        public static NativeLaunchOptions Parse(string[] args)
        {
            var options = new NativeLaunchOptions();
            if (args == null) return options;

            foreach (var raw in args)
            {
                var arg = raw ?? string.Empty;
                if (arg.StartsWith("--open-json=", StringComparison.OrdinalIgnoreCase))
                {
                    var path = arg.Substring("--open-json=".Length).Trim();
                    if (!Path.IsPathRooted(path) || !path.EndsWith(".json", StringComparison.OrdinalIgnoreCase))
                        throw new ArgumentException("--open-json requires an absolute .json file path.");
                    options.InitialJsonPath = Path.GetFullPath(path);
                    continue;
                }
                if (arg.StartsWith("--open-md=", StringComparison.OrdinalIgnoreCase))
                {
                    var path = arg.Substring("--open-md=".Length).Trim();
                    if (!Path.IsPathRooted(path) || !path.EndsWith(".md", StringComparison.OrdinalIgnoreCase))
                        throw new ArgumentException("--open-md requires an absolute .md file path.");
                    options.InitialMarkdownPath = Path.GetFullPath(path);
                    continue;
                }
                if (arg.StartsWith("--launch=", StringComparison.OrdinalIgnoreCase))
                {
                    var value = arg.Substring("--launch=".Length).Trim();
                    if (string.Equals(value, "markdown", StringComparison.OrdinalIgnoreCase))
                    {
                        options.InitialPage = "mdViewer.html";
                    }
                    continue;
                }

                if (arg.StartsWith("--launch-shortcut=", StringComparison.OrdinalIgnoreCase))
                {
                    try
                    {
                        var encodedId = arg.Substring("--launch-shortcut=".Length).Trim();
                        var shortcutId = Uri.UnescapeDataString(encodedId);
                        if (NativeLaunchShortcutCatalog.TryBuildInitialPage(shortcutId, out var initialPage))
                        {
                            options.InitialPage = initialPage;
                        }
                    }
                    catch
                    {
                        // A stale/invalid convenience task must never block normal NativeShell startup.
                    }
                }
            }
            if (!string.IsNullOrWhiteSpace(options.InitialMarkdownPath) && !string.IsNullOrWhiteSpace(options.InitialJsonPath))
                throw new ArgumentException("--open-json and --open-md cannot be combined.");
            if (!string.IsNullOrWhiteSpace(options.InitialMarkdownPath))
                options.InitialPage = "mdViewer.html?startupMd=1";
            if (!string.IsNullOrWhiteSpace(options.InitialJsonPath))
                options.InitialPage = "index.html?startupJson=1";
            return options;
        }
    }
}
