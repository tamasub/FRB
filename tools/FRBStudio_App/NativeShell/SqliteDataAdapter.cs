using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using System.Web.Script.Serialization;
using Microsoft.Data.Sqlite;

namespace FRBStudio.NativeShell
{
    // Data source boundary. No WebView, Grid, ViewDef or UI references belong here.
    // A workspace-owned DataJSON is the only authority for database/table mapping.
    internal sealed class SqliteDataAdapter
    {
        private readonly WorkspacePolicy _workspace;
        private readonly HashSet<string> _externalReadOnlyFiles;
        private readonly JavaScriptSerializer _json = new JavaScriptSerializer { MaxJsonLength = int.MaxValue };
        private const string SnapshotKey = "__sqlite_snapshot";
        private const string MetaKey = "__sqlite_meta";
        private static readonly Regex Identifier = new Regex(@"^[A-Za-z_][A-Za-z0-9_]*$", RegexOptions.Compiled);
        private static readonly Regex DataPath = new Regex(@"^\$\.[A-Za-z_][A-Za-z0-9_]*$", RegexOptions.Compiled);

        internal SqliteDataAdapter(WorkspacePolicy workspace, IEnumerable<string> externalReadOnlyFiles = null)
        {
            _workspace = workspace;
            _externalReadOnlyFiles = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            foreach (var configured in externalReadOnlyFiles ?? Enumerable.Empty<string>())
            {
                if (String.IsNullOrWhiteSpace(configured)) continue;
                var expanded = Environment.ExpandEnvironmentVariables(configured.Trim());
                if (!Path.IsPathRooted(expanded))
                    throw new InvalidDataException("sqlite_readonly_external_files must contain absolute paths.");
                _externalReadOnlyFiles.Add(Path.GetFullPath(expanded));
            }
        }

        internal static bool IsSqliteDocument(string content)
        {
            try
            {
                var obj = new JavaScriptSerializer { MaxJsonLength = int.MaxValue }.DeserializeObject(content) as IDictionary<string, object>;
                return obj != null && obj.ContainsKey("data_source") &&
                    String.Equals(GetString(Dict(obj["data_source"]), "type"), "sqlite", StringComparison.OrdinalIgnoreCase);
            }
            catch { return false; }
        }

        private sealed class Mapping
        {
            internal string Table;
            internal string DataPath;
            internal string Property;
            internal int Limit;
            internal bool OnOpen;
            internal bool ReadOnly;
            internal string PrimaryKey;
            internal List<string> Columns;
        }

        private static IDictionary<string, object> Dict(object obj) => obj as IDictionary<string, object>;
        private static object[] Array(object obj) => obj as object[] ?? (obj as ArrayList)?.Cast<object>().ToArray();
        private static string GetString(IDictionary<string, object> d, string name) => d != null && d.ContainsKey(name) ? Convert.ToString(d[name], CultureInfo.InvariantCulture) : "";
        private static bool GetBool(IDictionary<string, object> d, string name, bool fallback) => d != null && d.ContainsKey(name) ? Convert.ToBoolean(d[name], CultureInfo.InvariantCulture) : fallback;
        private static string Quote(string name) { if (!Identifier.IsMatch(name ?? "")) throw new InvalidDataException("SQLite identifier is invalid: " + name); return "\"" + name + "\""; }
        private static string Canonical(object v)
        {
            if (v == null || v == DBNull.Value) return "null";
            if (v is bool b) return b ? "1" : "0";
            if (v is byte[] bytes) return "blob:" + Convert.ToBase64String(bytes);
            if (v is string s) return "string:" + s;
            if (v is IConvertible c && !(v is DateTime))
            {
                try { return "number:" + c.ToDecimal(CultureInfo.InvariantCulture).ToString("G29", CultureInfo.InvariantCulture); }
                catch { /* non-numeric values */ }
            }
            return "value:" + Convert.ToString(v, CultureInfo.InvariantCulture);
        }
        private static bool Equal(object a, object b) => Canonical(a) == Canonical(b);
        private static bool RowsEqual(IDictionary<string, object> a, IDictionary<string, object> b, IEnumerable<string> columns) =>
            columns.All(k => Equal(a != null && a.ContainsKey(k) ? a[k] : null, b != null && b.ContainsKey(k) ? b[k] : null));

        private string DatabaseFile(IDictionary<string, object> ds)
        {
            var path = Environment.ExpandEnvironmentVariables(GetString(ds, "database_path").Trim());
            if (String.IsNullOrWhiteSpace(path) || !path.EndsWith(".db", StringComparison.OrdinalIgnoreCase))
                throw new InvalidDataException("data_source.database_path must point to an existing .db file.");
            string full;
            if (Path.IsPathRooted(path))
            {
                // External access is intentionally opt-in, exact-file, and READ ONLY.
                // DataJSON alone cannot grant itself filesystem permissions.
                if (!String.Equals(GetString(ds, "access_mode"), "read_only", StringComparison.OrdinalIgnoreCase))
                    throw new InvalidOperationException("WORKSPACE_PATH_DENIED: external SQLite databases require read_only mode.");
                full = Path.GetFullPath(path);
                if (!_externalReadOnlyFiles.Contains(full))
                    throw new InvalidOperationException("WORKSPACE_PATH_DENIED: SQLite external DB is not in native allowlist.");
            }
            else
            {
                // Existing workspace policy remains authoritative for ordinary SQLite documents.
                full = _workspace.ResolveRelativePath(path);
            }
            if (!File.Exists(full)) throw new FileNotFoundException("SQLite database is missing (not created automatically).", full);
            return full;
        }
        private List<Mapping> GetMappings(IDictionary<string, object> ds)
        {
            var tables = ds != null && ds.ContainsKey("tables") ? Array(ds["tables"]) : null;
            if (tables == null || tables.Length == 0) throw new InvalidDataException("data_source.tables is required.");
            var result = new List<Mapping>();
            var uniquePaths = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            foreach (var raw in tables)
            {
                var d = Dict(raw);
                var name = GetString(d, "table");
                var path = GetString(d, "data_path");
                Quote(name);
                if (!DataPath.IsMatch(path)) throw new InvalidDataException("Only top-level array paths like $.employees are supported: " + path);
                if (!uniquePaths.Add(path)) throw new InvalidDataException("Duplicate data_path: " + path);
                var load = d != null && d.ContainsKey("load") ? Dict(d["load"]) : null;
                var limit = load != null && load.ContainsKey("limit") ? Convert.ToInt32(load["limit"]) : 100;
                if (limit < 1 || limit > 2000) throw new InvalidDataException("load.limit must be 1..2000.");
                result.Add(new Mapping { Table = name, DataPath = path, Property = path.Substring(2), Limit = limit,
                    OnOpen = GetBool(load, "on_open", true), ReadOnly = GetString(ds, "access_mode") != "read_write" });
            }
            return result;
        }
        private static List<string> ResolveTableColumns(SqliteConnection connection, SqliteTransaction tx, Mapping map)
        {
            var cols = new List<string>();
            var pk = new List<Tuple<int, string>>();
            using (var cmd = connection.CreateCommand())
            {
                cmd.Transaction = tx;
                cmd.CommandText = "PRAGMA table_info(" + Quote(map.Table) + ")";
                using (var r = cmd.ExecuteReader())
                {
                    while (r.Read())
                    {
                        var column = r.GetString(1);
                        Quote(column);
                        cols.Add(column);
                        var order = r.GetInt32(5);
                        if (order > 0) pk.Add(Tuple.Create(order, column));
                    }
                }
            }
            if (cols.Count == 0) throw new InvalidDataException("SQLite table not found or has no columns: " + map.Table);
            map.PrimaryKey = pk.Count == 1 ? pk[0].Item2 : null;
            map.Columns = cols;
            if (!map.ReadOnly && map.PrimaryKey == null) throw new InvalidDataException("Writing requires exactly one primary key (v0.1): " + map.Table);
            return cols;
        }
        private static List<IDictionary<string, object>> ReadRows(SqliteConnection connection, SqliteTransaction tx, Mapping map, out bool truncated)
        {
            var rows = new List<IDictionary<string, object>>();
            truncated = false;
            if (!map.OnOpen) return rows;
            using (var cmd = connection.CreateCommand())
            {
                cmd.Transaction = tx;
                cmd.CommandText = "SELECT * FROM " + Quote(map.Table) +
                    (map.PrimaryKey == null ? "" : " ORDER BY " + Quote(map.PrimaryKey)) + " LIMIT @limit";
                cmd.Parameters.AddWithValue("@limit", map.Limit + 1);
                using (var reader = cmd.ExecuteReader())
                {
                    while (reader.Read())
                    {
                        if (rows.Count >= map.Limit) { truncated = true; break; }
                        var d = new Dictionary<string, object>(StringComparer.OrdinalIgnoreCase);
                        for (var i = 0; i < reader.FieldCount; i++)
                        {
                            var value = reader.IsDBNull(i) ? null : reader.GetValue(i);
                            if (value is long int64 && (int64 > 9007199254740991L || int64 < -9007199254740991L))
                                throw new NotSupportedException("SQLite 64-bit integer exceeds JavaScript safe integer range: " + map.Table);
                            if (value is byte[]) throw new NotSupportedException("BLOB columns are not supported by the first SQLite adapter: " + map.Table);
                            d[reader.GetName(i)] = value;
                        }
                        rows.Add(d);
                    }
                }
            }
            return rows;
        }
        private static object DbValue(object value) => value ?? DBNull.Value;
        private static IDictionary<string, object> FindPk(IEnumerable<IDictionary<string, object>> rows, Mapping map, object pk)
        {
            return rows.FirstOrDefault(row => row.ContainsKey(map.PrimaryKey) && Equal(row[map.PrimaryKey], pk));
        }
        private static IDictionary<string, object> ReadCurrent(SqliteConnection con, SqliteTransaction tx, Mapping map, object pk)
        {
            using (var cmd = con.CreateCommand())
            {
                cmd.Transaction = tx;
                cmd.CommandText = "SELECT * FROM " + Quote(map.Table) + " WHERE " + Quote(map.PrimaryKey) + " = @pk";
                cmd.Parameters.AddWithValue("@pk", DbValue(pk));
                using (var reader = cmd.ExecuteReader())
                {
                    if (!reader.Read()) return null;
                    var row = new Dictionary<string, object>(StringComparer.OrdinalIgnoreCase);
                    for (var i = 0; i < reader.FieldCount; i++) row[reader.GetName(i)] = reader.IsDBNull(i) ? null : reader.GetValue(i);
                    return row;
                }
            }
        }
        private static List<IDictionary<string, object>> AsRows(object value, string label)
        {
            var array = Array(value);
            if (array == null) throw new InvalidDataException(label + " must be an array.");
            return array.Select(x => Dict(x) ?? throw new InvalidDataException("Array row must be an object: " + label)).ToList();
        }
        private static void CheckUniqueIds(IEnumerable<IDictionary<string, object>> rows, Mapping map)
        {
            var seen = new HashSet<string>();
            foreach (var row in rows)
            {
                if (!row.ContainsKey(map.PrimaryKey) || row[map.PrimaryKey] == null) continue;
                if (!seen.Add(Canonical(row[map.PrimaryKey]))) throw new InvalidDataException("Duplicate primary key in edited rows: " + map.Table);
            }
        }
        private static int ApplyChanges(SqliteConnection con, SqliteTransaction tx, Mapping map,
            IList<IDictionary<string, object>> originals, IList<IDictionary<string, object>> edited)
        {
            CheckUniqueIds(edited, map);
            var changed = 0;
            foreach (var old in originals)
            {
                var pk = old[map.PrimaryKey];
                var now = FindPk(edited, map, pk);
                if (now != null && RowsEqual(old, now, map.Columns)) continue;
                var dbRow = ReadCurrent(con, tx, map, pk);
                if (!RowsEqual(old, dbRow, map.Columns)) throw SqliteDataError.SaveConflict(map.Table, pk);
                using (var cmd = con.CreateCommand())
                {
                    cmd.Transaction = tx;
                    if (now == null)
                    {
                        cmd.CommandText = "DELETE FROM " + Quote(map.Table) + " WHERE " + Quote(map.PrimaryKey) + "=@pk";
                        cmd.Parameters.AddWithValue("@pk", DbValue(pk));
                    }
                    else
                    {
                        if (!Equal(now[map.PrimaryKey], pk)) throw new InvalidDataException("Primary key cannot be edited: " + map.Table);
                        var columns = map.Columns.Where(k => k != map.PrimaryKey && !Equal(old[k], now.ContainsKey(k) ? now[k] : null)).ToArray();
                        if (columns.Length == 0) continue;
                        cmd.CommandText = "UPDATE " + Quote(map.Table) + " SET " + String.Join(", ", columns.Select((c, i) => Quote(c) + "=@v" + i)) + " WHERE " + Quote(map.PrimaryKey) + "=@pk";
                        for (var i = 0; i < columns.Length; i++) cmd.Parameters.AddWithValue("@v" + i, DbValue(now.ContainsKey(columns[i]) ? now[columns[i]] : null));
                        cmd.Parameters.AddWithValue("@pk", DbValue(pk));
                    }
                    try
                    {
                        if (cmd.ExecuteNonQuery() != 1) throw new InvalidOperationException("SQLite row update failed: " + map.Table);
                    }
                    catch (SqliteException ex)
                    {
                        throw SqliteDataError.FromSqlite(ex, map.Table, now == null ? "DELETE" : "UPDATE", pk);
                    }
                    changed++;
                }
            }
            foreach (var row in edited)
            {
                var pk = row.ContainsKey(map.PrimaryKey) ? row[map.PrimaryKey] : null;
                if (pk != null && FindPk(originals, map, pk) != null) continue;
                // New row: only columns supplied by the editor; SQLite default handles the rest.
                var cols = map.Columns.Where(c => row.ContainsKey(c) && !(c == map.PrimaryKey && row[c] == null)).ToArray();
                using (var cmd = con.CreateCommand())
                {
                    cmd.Transaction = tx;
                    if (cols.Length == 0) cmd.CommandText = "INSERT INTO " + Quote(map.Table) + " DEFAULT VALUES";
                    else
                    {
                        cmd.CommandText = "INSERT INTO " + Quote(map.Table) + " (" + String.Join(",", cols.Select(Quote)) + ") VALUES (" + String.Join(",", cols.Select((c, i) => "@v" + i)) + ")";
                        for (var i = 0; i < cols.Length; i++) cmd.Parameters.AddWithValue("@v" + i, DbValue(row[cols[i]]));
                    }
                    try
                    {
                        if (cmd.ExecuteNonQuery() != 1) throw new InvalidOperationException("SQLite INSERT failed: " + map.Table);
                    }
                    catch (SqliteException ex)
                    {
                        throw SqliteDataError.FromSqlite(ex, map.Table, "INSERT", pk);
                    }
                    changed++;
                }
            }
            return changed;
        }

        private IDictionary<string, object> ReadDefinition(string documentPath, out IDictionary<string, object> dataSource)
        {
            if (!File.Exists(documentPath)) throw new FileNotFoundException("DataJSON not found.", documentPath);
            var definition = Dict(_json.DeserializeObject(File.ReadAllText(documentPath)));
            dataSource = definition != null && definition.ContainsKey("data_source") ? Dict(definition["data_source"]) : null;
            if (GetString(dataSource, "type") != "sqlite") throw new InvalidDataException("DataJSON is not a SQLite data source.");
            return definition;
        }
        private static SqliteConnection Connect(string fullPath, bool readOnly)
        {
            var builder = new SqliteConnectionStringBuilder { DataSource = fullPath,
                Mode = readOnly ? SqliteOpenMode.ReadOnly : SqliteOpenMode.ReadWrite, DefaultTimeout = 5 };
            var con = new SqliteConnection(builder.ToString());
            con.Open();
            using (var cmd = con.CreateCommand()) { cmd.CommandText = "PRAGMA foreign_keys=ON"; cmd.ExecuteNonQuery(); }
            return con;
        }
        private IDictionary<string, object> LoadFromConnection(IDictionary<string, object> def, IList<Mapping> maps, SqliteConnection con, SqliteTransaction tx)
        {
            var snap = new Dictionary<string, object>();
            var meta = new Dictionary<string, object>();
            foreach (var map in maps)
            {
                ResolveTableColumns(con, tx, map);
                bool truncated;
                var rows = ReadRows(con, tx, map, out truncated);
                def[map.Property] = rows.ToArray();
                snap[map.Property] = rows.ToArray().Select(row => new Dictionary<string, object>(row)).ToArray();
                meta[map.Property] = new Dictionary<string, object> { ["table"] = map.Table, ["loaded"] = rows.Count,
                    ["limit"] = map.Limit, ["limit_hit"] = truncated, ["on_open"] = map.OnOpen };
            }
            def[SnapshotKey] = snap;
            def[MetaKey] = meta;
            return def;
        }
        internal IDictionary<string, object> Load(string documentPath)
        {
            IDictionary<string, object> ds;
            var doc = ReadDefinition(documentPath, out ds);
            var maps = GetMappings(ds);
            var readOnly = GetString(ds, "access_mode") != "read_write";
            using (var con = Connect(DatabaseFile(ds), readOnly))
            {
                // Read-only providers must not begin a write-intent SQLite transaction.
                // Each SELECT is read-only; the Launch index is concurrently updated using WAL.
                if (readOnly) return LoadFromConnection(doc, maps, con, null);
                using (var tx = con.BeginTransaction())
                {
                    var loaded = LoadFromConnection(doc, maps, con, tx);
                    tx.Commit();
                    return loaded;
                }
            }
        }
        internal IDictionary<string, object> Save(string documentPath, string editedJson)
        {
            IDictionary<string, object> ds;
            var definition = ReadDefinition(documentPath, out ds);
            if (GetString(ds, "access_mode") != "read_write")
                throw new InvalidOperationException("SQLite data source is read-only.");
            var maps = GetMappings(ds);
            var updated = Dict(_json.DeserializeObject(editedJson));
            if (updated == null || !updated.ContainsKey(SnapshotKey)) throw new InvalidDataException("Missing SQLite original row snapshot. Reload the document.");
            var snapshots = Dict(updated[SnapshotKey]);
            if (snapshots == null) throw new InvalidDataException("Invalid SQLite row snapshot.");
            var count = 0;
            using (var con = Connect(DatabaseFile(ds), false))
            using (var tx = con.BeginTransaction())
            {
                foreach (var map in maps)
                {
                    ResolveTableColumns(con, tx, map);
                    if (map.ReadOnly) throw new InvalidOperationException("SQLite data source is read-only.");
                    if (!updated.ContainsKey(map.Property) || !snapshots.ContainsKey(map.Property)) throw new InvalidDataException("SQLite table data missing: " + map.Table);
                    var before = AsRows(snapshots[map.Property], map.Table + " original");
                    var after = AsRows(updated[map.Property], map.Table + " edited");
                    count += ApplyChanges(con, tx, map, before, after);
                }
                tx.Commit();
            }
            // Re-read from DB to refresh original snapshots and generated PK values.
            var reloaded = Load(documentPath);
            return new Dictionary<string, object> { ["changed_rows"] = count, ["document"] = reloaded, ["saved"] = Path.GetFileName(documentPath) };
        }
    }
}
