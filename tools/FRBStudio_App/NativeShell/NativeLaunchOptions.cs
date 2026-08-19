using System;

namespace FRBStudio.NativeShell
{
    internal sealed class NativeLaunchOptions
    {
        public string InitialPage { get; private set; }

        public static NativeLaunchOptions Parse(string[] args)
        {
            var options = new NativeLaunchOptions();
            if (args == null || args.Length == 0) return options;

            for (var i = 0; i < args.Length; i++)
            {
                var raw = args[i] ?? string.Empty;
                string target = null;

                if (raw.StartsWith("--launch=", StringComparison.OrdinalIgnoreCase))
                {
                    target = raw.Substring("--launch=".Length);
                }
                else if (string.Equals(raw, "--launch", StringComparison.OrdinalIgnoreCase) && i + 1 < args.Length)
                {
                    target = args[++i];
                }

                if (string.Equals(target, "markdown", StringComparison.OrdinalIgnoreCase))
                {
                    options.InitialPage = "mdViewer.html";
                    break;
                }
            }

            return options;
        }
    }
}
