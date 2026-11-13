using System;
using System.Collections.Generic;
using System.Globalization;
using Microsoft.Data.Sqlite;

namespace FRBStudio.NativeShell
{
    // SQLite adapter error contract: database facts only, no Grid/Editor/Toast wording.
    // NativeShell transports these facts; Presentation owns user-facing messages.
    internal sealed class SqliteDataError : Exception
    {
        internal string ErrorCode { get; }
        internal string Table { get; }
        internal string Operation { get; }
        internal string Key { get; }
        internal int SqliteCode { get; }
        internal int SqliteExtendedCode { get; }

        private SqliteDataError(string code, string table, string operation, object key,
            int sqliteCode, int extendedCode, Exception inner)
            : base(inner?.Message ?? code, inner)
        {
            ErrorCode = code;
            Table = table ?? "";
            Operation = operation ?? "";
            Key = key == null ? "" : Convert.ToString(key, CultureInfo.InvariantCulture);
            SqliteCode = sqliteCode;
            SqliteExtendedCode = extendedCode;
        }

        internal IDictionary<string, object> Details() => new Dictionary<string, object>
        {
            ["table"] = Table,
            ["operation"] = Operation,
            ["key"] = Key,
            ["sqlite_code"] = SqliteCode,
            ["sqlite_extended_code"] = SqliteExtendedCode
        };

        internal static SqliteDataError SaveConflict(string table, object key) =>
            new SqliteDataError("SQLITE_SAVE_CONFLICT", table, "UPDATE_OR_DELETE", key, 0, 0,
                new InvalidOperationException("Row changed in database after Studio loaded it."));

        internal static SqliteDataError FromSqlite(SqliteException ex,
            string table = null, string operation = null, object key = null)
        {
            // SQLite extended result codes are stable numeric database error codes.
            // Do not parse localized provider messages to classify the failure.
            var extended = ex.SqliteExtendedErrorCode;
            string code;
            switch (ex.SqliteErrorCode)
            {
                case 19: // SQLITE_CONSTRAINT
                    switch (extended)
                    {
                        case 787:  code = "SQLITE_FOREIGN_KEY"; break;
                        case 2067: // SQLITE_CONSTRAINT_UNIQUE
                        case 1555: code = "SQLITE_UNIQUE"; break; // SQLITE_CONSTRAINT_PRIMARYKEY
                        case 1299: code = "SQLITE_NOT_NULL"; break;
                        case 275:  code = "SQLITE_CHECK"; break;
                        default:   code = "SQLITE_CONSTRAINT"; break;
                    }
                    break;
                case 5:  // SQLITE_BUSY
                case 6:  code = "SQLITE_BUSY"; break; // SQLITE_LOCKED
                case 8:  code = "SQLITE_READ_ONLY"; break;
                case 14: code = "SQLITE_CANNOT_OPEN"; break;
                case 13: code = "SQLITE_DISK_FULL"; break;
                case 10: code = "SQLITE_IO_ERROR"; break;
                default: code = "SQLITE_DATABASE_ERROR"; break;
            }
            return new SqliteDataError(code, table, operation, key,
                ex.SqliteErrorCode, extended, ex);
        }
    }
}
