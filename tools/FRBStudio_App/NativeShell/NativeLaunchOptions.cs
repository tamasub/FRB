using System;
using System.IO;

namespace FRBStudio.NativeShell
{
    internal sealed class NativeLaunchOptions
    {
        public string InitialPage { get; private set; }
        public string InitialJsonPath { get; private set; }
        public string InitialMarkdownPath { get; private set; }
        public string LaunchItemId { get; private set; }
        public string LaunchNewCategoryPage { get; private set; }
        public string LaunchPageId { get; private set; }
        public string StudioTheme { get; private set; }

        public static NativeLaunchOptions Parse(string[] args)
        {
            var options = new NativeLaunchOptions();
            if (args == null) return options;

            foreach (var raw in args)
            {
                var arg = raw ?? string.Empty;
                if (arg.StartsWith("--studio-theme=", StringComparison.OrdinalIgnoreCase))
                {
                    var theme = arg.Substring("--studio-theme=".Length).Trim();
                    if (!string.Equals(theme, "light", StringComparison.OrdinalIgnoreCase) &&
                        !string.Equals(theme, "dark", StringComparison.OrdinalIgnoreCase))
                        throw new ArgumentException("--studio-theme requires light or dark.");
                    options.StudioTheme = theme.ToLowerInvariant();
                    continue;
                }
                if (arg.StartsWith("--launch-item-id=", StringComparison.OrdinalIgnoreCase))
                {
                    options.LaunchItemId = arg.Substring("--launch-item-id=".Length).Trim();
                    if (string.IsNullOrWhiteSpace(options.LaunchItemId))
                        throw new ArgumentException("--launch-item-id requires an item ID.");
                    continue;
                }
                if (arg.StartsWith("--launch-page-id=", StringComparison.OrdinalIgnoreCase))
                {
                    options.LaunchPageId = arg.Substring("--launch-page-id=".Length).Trim();
                    if (string.IsNullOrWhiteSpace(options.LaunchPageId))
                        throw new ArgumentException("--launch-page-id requires a page ID.");
                    continue;
                }
                if (arg.StartsWith("--launch-new-category=", StringComparison.OrdinalIgnoreCase))
                {
                    options.LaunchNewCategoryPage = arg.Substring("--launch-new-category=".Length).Trim();
                    if (string.IsNullOrWhiteSpace(options.LaunchNewCategoryPage))
                        throw new ArgumentException("--launch-new-category requires a page ID.");
                    continue;
                }
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
            int launchTargets = (options.LaunchItemId != null ? 1 : 0)
                + (options.LaunchNewCategoryPage != null ? 1 : 0)
                + (options.LaunchPageId != null ? 1 : 0);
            if (launchTargets > 1)
                throw new ArgumentException("Launch edit targets cannot be combined.");
            if (launchTargets > 0 && options.InitialJsonPath == null)
                throw new ArgumentException("Launch edit requires --open-json.");
            if (!string.IsNullOrWhiteSpace(options.InitialMarkdownPath) && !string.IsNullOrWhiteSpace(options.InitialJsonPath))
                throw new ArgumentException("--open-json and --open-md cannot be combined.");
            if (!string.IsNullOrWhiteSpace(options.InitialMarkdownPath))
                options.InitialPage = "mdViewer.html?startupMd=1";
            if (!string.IsNullOrWhiteSpace(options.InitialJsonPath))
            {
                var page = "index.html?startupJson=1";
                if (options.LaunchItemId != null)
                    page += "&focusField=item_id&focusValue=" + Uri.EscapeDataString(options.LaunchItemId) + "&openDetail=true&launchItemProperties=1";
                if (options.LaunchNewCategoryPage != null)
                    page += "&launchNewCategory=1&newCategoryPage=" + Uri.EscapeDataString(options.LaunchNewCategoryPage);
                if (options.LaunchPageId != null)
                    page += "&launchPageId=" + Uri.EscapeDataString(options.LaunchPageId);
                options.InitialPage = page;
            }
            // Startup appearance is deliberately process-scoped, not saved into ViewDef.
            // Only the JSON Object Studio page consumes this launch hint.
            if (options.StudioTheme != null)
            {
                if (string.IsNullOrWhiteSpace(options.InitialPage))
                    options.InitialPage = "index.html";
                if (options.InitialPage.StartsWith("index.html", StringComparison.OrdinalIgnoreCase))
                    options.InitialPage += (options.InitialPage.Contains("?") ? "&" : "?")
                        + "studioTheme=" + options.StudioTheme;
            }
            return options;
        }
    }
}
