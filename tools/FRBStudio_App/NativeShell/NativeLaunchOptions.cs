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
                }
            }
            return options;
        }
    }
}
