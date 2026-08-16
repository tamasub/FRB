using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Web.Script.Serialization;

namespace FRBStudio.NativeShell
{
    internal sealed class NativeShellConfig
    {
        public string ProtocolVersion { get; private set; } = "1.0";
        public string VirtualHostName { get; private set; } = "frb-studio.local";
        public string StartPage { get; private set; } = "index.html";
        public bool DevToolsEnabled { get; private set; } = true;
        public bool OpenExternalLinksInDefaultBrowser { get; private set; } = true;
        public string[] WritableRoots { get; private set; } = Array.Empty<string>();
        public string[] WritableFiles { get; private set; } = Array.Empty<string>();
        public HashSet<string> AllowedCommands { get; private set; } = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        public Dictionary<string, NativeProcessProfile> ProcessProfiles { get; private set; } = new Dictionary<string, NativeProcessProfile>(StringComparer.OrdinalIgnoreCase);

        public static NativeShellConfig Load(string path)
        {
            if (!File.Exists(path))
                throw new FileNotFoundException("Native Shell config が見つかりません。", path);

            var serializer = new JavaScriptSerializer { MaxJsonLength = int.MaxValue };
            var raw = serializer.DeserializeObject(File.ReadAllText(path)) as Dictionary<string, object>;
            if (raw == null)
                throw new InvalidDataException("native_shell.config.json を読み込めません。");

            var config = new NativeShellConfig
            {
                ProtocolVersion = GetString(raw, "protocol_version", "1.0"),
                VirtualHostName = GetString(raw, "virtual_host_name", "frb-studio.local"),
                StartPage = GetString(raw, "start_page", "index.html"),
                DevToolsEnabled = GetBool(raw, "dev_tools_enabled", true),
                OpenExternalLinksInDefaultBrowser = GetBool(raw, "open_external_links_in_default_browser", true),
                WritableRoots = GetStringList(raw, "writable_roots").ToArray(),
                WritableFiles = GetStringList(raw, "writable_files").ToArray()
            };

            foreach (var command in GetStringList(raw, "allowed_commands"))
                config.AllowedCommands.Add(command);

            foreach (var profileRaw in GetDictionaryList(raw, "process_profiles"))
            {
                var profile = NativeProcessProfile.FromDictionary(profileRaw);
                if (!string.IsNullOrWhiteSpace(profile.Id)) config.ProcessProfiles[profile.Id] = profile;
            }

            return config;
        }

        internal static string GetString(IDictionary<string, object> raw, string key, string fallback = null)
        {
            if (raw == null || !raw.TryGetValue(key, out var value) || value == null) return fallback;
            var text = Convert.ToString(value)?.Trim();
            return string.IsNullOrWhiteSpace(text) ? fallback : text;
        }

        internal static bool GetBool(IDictionary<string, object> raw, string key, bool fallback)
        {
            if (raw == null || !raw.TryGetValue(key, out var value) || value == null) return fallback;
            if (value is bool b) return b;
            return bool.TryParse(Convert.ToString(value), out var parsed) ? parsed : fallback;
        }

        internal static int GetInt(IDictionary<string, object> raw, string key, int fallback)
        {
            if (raw == null || !raw.TryGetValue(key, out var value) || value == null) return fallback;
            return int.TryParse(Convert.ToString(value), out var parsed) ? parsed : fallback;
        }

        internal static IEnumerable<string> GetStringList(IDictionary<string, object> raw, string key)
        {
            if (raw == null || !raw.TryGetValue(key, out var value) || value == null) yield break;
            foreach (var item in ToObjectEnumerable(value))
            {
                var text = Convert.ToString(item)?.Trim();
                if (!string.IsNullOrWhiteSpace(text)) yield return text;
            }
        }

        internal static IEnumerable<Dictionary<string, object>> GetDictionaryList(IDictionary<string, object> raw, string key)
        {
            if (raw == null || !raw.TryGetValue(key, out var value) || value == null) yield break;
            foreach (var item in ToObjectEnumerable(value))
                if (item is Dictionary<string, object> dict) yield return dict;
        }

        internal static Dictionary<string, object> GetDictionary(IDictionary<string, object> raw, string key)
        {
            if (raw == null || !raw.TryGetValue(key, out var value) || value == null) return null;
            return value as Dictionary<string, object>;
        }

        private static IEnumerable<object> ToObjectEnumerable(object value)
        {
            if (value is object[] array) return array;
            if (value is ArrayList list) return list.Cast<object>();
            return Enumerable.Empty<object>();
        }
    }

    internal sealed class NativeProcessProfile
    {
        public string Id { get; private set; }
        public string DisplayName { get; private set; }
        public string Executable { get; private set; }
        public string WorkingDirectory { get; private set; }
        public int TimeoutSeconds { get; private set; }
        public string[] FixedArguments { get; private set; } = Array.Empty<string>();
        public NativeProcessParameter[] Parameters { get; private set; } = Array.Empty<NativeProcessParameter>();
        public string[] OutputGlobs { get; private set; } = Array.Empty<string>();
        public string LaunchParameterKey { get; private set; }
        public string LaunchParameterValue { get; private set; }

        public static NativeProcessProfile FromDictionary(IDictionary<string, object> raw)
        {
            var launch = NativeShellConfig.GetDictionary(raw, "launch_when_parameter_equals");
            return new NativeProcessProfile
            {
                Id = NativeShellConfig.GetString(raw, "id", string.Empty),
                DisplayName = NativeShellConfig.GetString(raw, "display_name", string.Empty),
                Executable = NativeShellConfig.GetString(raw, "executable", string.Empty),
                WorkingDirectory = NativeShellConfig.GetString(raw, "working_directory", "."),
                TimeoutSeconds = NativeShellConfig.GetInt(raw, "timeout_seconds", 60),
                FixedArguments = NativeShellConfig.GetStringList(raw, "fixed_arguments").ToArray(),
                Parameters = NativeShellConfig.GetDictionaryList(raw, "parameters").Select(NativeProcessParameter.FromDictionary).ToArray(),
                OutputGlobs = NativeShellConfig.GetStringList(raw, "output_globs").ToArray(),
                LaunchParameterKey = NativeShellConfig.GetString(launch, "key", string.Empty),
                LaunchParameterValue = NativeShellConfig.GetString(launch, "value", string.Empty)
            };
        }
    }

    internal sealed class NativeProcessParameter
    {
        public string Key { get; private set; }
        public string Switch { get; private set; }
        public string Kind { get; private set; }
        public bool OmitIfEmpty { get; private set; }
        public string[] AllowedValues { get; private set; } = Array.Empty<string>();
        public string Pattern { get; private set; }
        public int Min { get; private set; } = int.MinValue;
        public int Max { get; private set; } = int.MaxValue;

        public static NativeProcessParameter FromDictionary(IDictionary<string, object> raw)
        {
            return new NativeProcessParameter
            {
                Key = NativeShellConfig.GetString(raw, "key", string.Empty),
                Switch = NativeShellConfig.GetString(raw, "switch", string.Empty),
                Kind = NativeShellConfig.GetString(raw, "kind", "text"),
                OmitIfEmpty = NativeShellConfig.GetBool(raw, "omit_if_empty", false),
                AllowedValues = NativeShellConfig.GetStringList(raw, "allowed_values").ToArray(),
                Pattern = NativeShellConfig.GetString(raw, "pattern", string.Empty),
                Min = NativeShellConfig.GetInt(raw, "min", int.MinValue),
                Max = NativeShellConfig.GetInt(raw, "max", int.MaxValue)
            };
        }
    }
}
