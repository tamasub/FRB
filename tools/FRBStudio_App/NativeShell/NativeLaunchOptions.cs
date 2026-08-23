using System;

namespace FRBStudio.NativeShell
{
    internal sealed class NativeLaunchOptions
    {
        public string InitialPage { get; private set; }

        public static NativeLaunchOptions Parse(string[] args)
        {
            var options = new NativeLaunchOptions();
            if (args == null) return options;

            foreach (var raw in args)
            {
                var arg = raw ?? string.Empty;
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
            return options;
        }
    }
}
