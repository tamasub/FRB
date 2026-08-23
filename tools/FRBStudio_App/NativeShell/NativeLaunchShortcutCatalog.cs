using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Web.Script.Serialization;

namespace FRBStudio.NativeShell
{
    internal sealed class NativeLaunchShortcut
    {
        public string Id { get; set; }
        public string Caption { get; set; }
        public string DataPath { get; set; }
        public string ViewDefPath { get; set; }
        public IDictionary<string, object> LaunchParams { get; set; }
    }

    internal static class NativeLaunchShortcutCatalog
    {
        private static readonly string[] SupportedLaunchParamKeys =
        {
            "focusField",
            "focusValue",
            "openDetail",
            "action"
        };

        public static IReadOnlyList<NativeLaunchShortcut> Load()
        {
            try
            {
                var appRoot = ResolveStudioAppRoot();
                var settingsPath = Path.Combine(appRoot, "wwwroot", "config", "app_settings.json");
                if (!File.Exists(settingsPath)) return Array.Empty<NativeLaunchShortcut>();

                var serializer = new JavaScriptSerializer();
                var root = serializer.DeserializeObject(File.ReadAllText(settingsPath)) as IDictionary<string, object>;
                if (root == null || !root.TryGetValue("launch_shortcuts", out var rawShortcuts))
                    return Array.Empty<NativeLaunchShortcut>();

                var shortcuts = new List<NativeLaunchShortcut>();
                foreach (var raw in AsObjectList(rawShortcuts))
                {
                    try
                    {
                        var row = raw as IDictionary<string, object>;
                        if (row == null) continue;

                        var id = GetString(row, "id").Trim();
                        var caption = GetString(row, "caption").Trim();
                        var data = NormalizeJsonPath(GetString(row, "data"), required: true);
                        var viewDef = NormalizeJsonPath(GetString(row, "view_def"), required: false);
                        if (string.IsNullOrWhiteSpace(id) || string.IsNullOrWhiteSpace(caption) || string.IsNullOrWhiteSpace(data))
                            continue;

                        shortcuts.Add(new NativeLaunchShortcut
                        {
                            Id = id,
                            Caption = caption,
                            DataPath = data,
                            ViewDefPath = viewDef,
                            LaunchParams = GetDictionary(row, "launch_params")
                        });
                    }
                    catch
                    {
                        // Match the browser menu contract: one invalid shortcut must not hide the valid tasks.
                    }
                }

                return shortcuts;
            }
            catch
            {
                // Launch shortcuts are convenience-only. Invalid/missing settings must never block startup.
                return Array.Empty<NativeLaunchShortcut>();
            }
        }

        public static bool TryBuildInitialPage(string shortcutId, out string initialPage)
        {
            initialPage = null;
            if (string.IsNullOrWhiteSpace(shortcutId)) return false;

            var shortcut = Load().FirstOrDefault(item =>
                string.Equals(item.Id, shortcutId, StringComparison.OrdinalIgnoreCase));
            if (shortcut == null) return false;

            initialPage = BuildInitialPage(shortcut);
            return !string.IsNullOrWhiteSpace(initialPage);
        }

        public static string BuildInitialPage(NativeLaunchShortcut shortcut)
        {
            if (shortcut == null || string.IsNullOrWhiteSpace(shortcut.DataPath)) return null;

            var query = new List<string>
            {
                "data=" + Uri.EscapeDataString(shortcut.DataPath)
            };

            if (!string.IsNullOrWhiteSpace(shortcut.ViewDefPath))
                query.Add("view=" + Uri.EscapeDataString(shortcut.ViewDefPath));

            if (shortcut.LaunchParams != null)
            {
                foreach (var key in SupportedLaunchParamKeys)
                {
                    if (!shortcut.LaunchParams.TryGetValue(key, out var raw) || raw == null) continue;
                    var value = raw is bool flag
                        ? (flag ? "true" : "false")
                        : Convert.ToString(raw, CultureInfo.InvariantCulture)?.Trim();
                    if (string.IsNullOrWhiteSpace(value)) continue;
                    query.Add(Uri.EscapeDataString(key) + "=" + Uri.EscapeDataString(value));
                }
            }

            return "index.html?" + string.Join("&", query);
        }

        private static string ResolveStudioAppRoot()
        {
            var starts = new[] { AppContext.BaseDirectory, Environment.CurrentDirectory };
            foreach (var start in starts)
            {
                if (string.IsNullOrWhiteSpace(start)) continue;
                var dir = new DirectoryInfo(Path.GetFullPath(start));
                while (dir != null)
                {
                    if (File.Exists(Path.Combine(dir.FullName, "wwwroot", "index.html"))
                        && Directory.Exists(Path.Combine(dir.FullName, "data", "json"))
                        && Directory.Exists(Path.Combine(dir.FullName, "defs")))
                        return dir.FullName;
                    dir = dir.Parent;
                }
            }

            throw new DirectoryNotFoundException("FRBStudio_App root を特定できません。");
        }

        private static string NormalizeJsonPath(string raw, bool required)
        {
            var value = (raw ?? string.Empty).Trim();
            if (value.Length == 0)
            {
                if (required) throw new InvalidOperationException("Data JSON が未設定です。");
                return string.Empty;
            }

            var normalized = value.Replace('\\', '/');
            if (normalized.Contains("://")
                || normalized.StartsWith("/", StringComparison.Ordinal)
                || normalized.StartsWith("//", StringComparison.Ordinal)
                || (normalized.Length >= 2 && char.IsLetter(normalized[0]) && normalized[1] == ':')
                || normalized.Contains("?")
                || normalized.Contains("#"))
                throw new InvalidOperationException("Launch shortcut path must be a relative JSON path.");

            var parts = normalized.Split('/');
            if (parts.Any(part => string.IsNullOrWhiteSpace(part) || part == "." || part == ".."))
                throw new InvalidOperationException("Launch shortcut path is invalid.");
            if (!normalized.EndsWith(".json", StringComparison.OrdinalIgnoreCase))
                throw new InvalidOperationException("Launch shortcut path must point to JSON.");

            return string.Join("/", parts);
        }

        private static IEnumerable<object> AsObjectList(object raw)
        {
            if (raw is object[] array) return array;
            if (raw is ArrayList list) return list.Cast<object>();
            if (raw is IEnumerable enumerable && !(raw is string)) return enumerable.Cast<object>();
            return Array.Empty<object>();
        }

        private static string GetString(IDictionary<string, object> source, string key)
        {
            if (source == null || !source.TryGetValue(key, out var raw) || raw == null) return string.Empty;
            return Convert.ToString(raw, CultureInfo.InvariantCulture) ?? string.Empty;
        }

        private static IDictionary<string, object> GetDictionary(IDictionary<string, object> source, string key)
        {
            if (source == null || !source.TryGetValue(key, out var raw) || raw == null) return null;
            return raw as IDictionary<string, object>;
        }
    }
}
