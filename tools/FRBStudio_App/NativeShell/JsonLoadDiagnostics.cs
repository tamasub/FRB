using System;
using System.Collections.Generic;
using System.IO;
using System.Text;

namespace FRBStudio.NativeShell
{
    // Failure-only local diagnostics. Never record JSON/DB contents or SQL parameter values.
    internal static class JsonLoadDiagnostics
    {
        private static readonly object Sync = new object();
        private const int MaxLogBytes = 2 * 1024 * 1024;
        internal static string LogPath => Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
            "FRBStudio", "logs", "json_load_errors.log");

        private static string Field(string value, int limit = 1200)
        {
            var text = (value ?? "").Replace("\r", " ").Replace("\n", " ").Replace("\t", " ");
            return text.Length > limit ? text.Substring(0, limit) + "..." : text;
        }

        internal static string Record(string source, string stage, string dataPath,
            string viewDefPath, string errorCode, string message, string detail = "")
        {
            var entry = new StringBuilder();
            entry.AppendLine("[" + DateTimeOffset.Now.ToString("yyyy-MM-dd HH:mm:ss zzz") + "] JSON_LOAD_FAILURE");
            entry.AppendLine("  source=" + Field(source, 80) + " stage=" + Field(stage, 100));
            entry.AppendLine("  data=" + Field(dataPath));
            entry.AppendLine("  view_def=" + Field(viewDefPath));
            entry.AppendLine("  code=" + Field(errorCode, 100));
            entry.AppendLine("  reason=" + Field(message, 2000));
            if (!String.IsNullOrWhiteSpace(detail)) entry.AppendLine("  detail=" + Field(detail, 2200));
            entry.AppendLine();
            lock (Sync)
            {
                var path = LogPath;
                Directory.CreateDirectory(Path.GetDirectoryName(path));
                if (File.Exists(path) && new FileInfo(path).Length > MaxLogBytes)
                {
                    var previous = path + ".old";
                    if (File.Exists(previous)) File.Delete(previous);
                    File.Move(path, previous);
                }
                File.AppendAllText(path, entry.ToString(), new UTF8Encoding(false));
                return path;
            }
        }

        internal static void TryNativeFailure(string command, IDictionary<string, object> payload,
            string errorCode, Exception error)
        {
            if (command != "sqlite.documentLoad" && command != "startupJson.read"
                && command != "dataSource.readOnlyJson" && command != "file.readText") return;
            var path = "";
            if (command == "file.readText" || command == "dataSource.readOnlyJson") path = Value(payload, "path");
            else if (command == "sqlite.documentLoad") path = Value(payload, "document_path");
            else path = "(startupJson.read)";
            if (command == "file.readText" && !path.EndsWith(".json", StringComparison.OrdinalIgnoreCase)) return;
            try { Record("NativeShell", command, path, "", errorCode,
                error?.Message, error?.ToString()); }
            catch { /* Failure logging must never replace the original error. */ }
        }

        private static string Value(IDictionary<string, object> data, string key) =>
            data != null && data.ContainsKey(key) ? Convert.ToString(data[key]) : "";

        internal static IDictionary<string, object> RecordBrowser(IDictionary<string, object> payload)
        {
            var path = Record("Studio UI", Value(payload, "stage"), Value(payload, "data_path"),
                Value(payload, "view_def_path"), Value(payload, "code"),
                Value(payload, "message"), Value(payload, "detail"));
            return new Dictionary<string, object> { ["path"] = path, ["written"] = true };
        }
    }
}
