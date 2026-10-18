using System;
using System.Collections.Generic;
using System.IO;
using System.Web.Script.Serialization;

namespace FRBStudio.NativeShell
{
    // User-owned launcher presentation preference; independent from ViewDef and FRB Launch.
    internal static class NativeStudioThemePreference
    {
        private static string StorePath => Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
            "FRBStudio", "studio_theme_preference.json");

        private static string Normalize(string value)
        {
            if (string.Equals(value, "light", StringComparison.OrdinalIgnoreCase)) return "light";
            if (string.Equals(value, "dark", StringComparison.OrdinalIgnoreCase)) return "dark";
            return null;
        }

        internal static string TryLoad()
        {
            try
            {
                if (!File.Exists(StorePath)) return null;
                var values = new JavaScriptSerializer()
                    .Deserialize<Dictionary<string, string>>(File.ReadAllText(StorePath));
                return values != null && values.TryGetValue("theme", out var theme)
                    ? Normalize(theme) : null;
            }
            catch (Exception) { return null; } // Corrupt settings must not block startup.
        }

        internal static void TrySave(string theme)
        {
            theme = Normalize(theme);
            if (theme == null) return;
            try
            {
                var path = StorePath;
                Directory.CreateDirectory(Path.GetDirectoryName(path));
                var json = new JavaScriptSerializer().Serialize(new Dictionary<string, string> {
                    ["theme"] = theme
                });
                File.WriteAllText(path, json);
            }
            catch (Exception) { /* Appearance must never block editing or startup. */ }
        }
    }
}
