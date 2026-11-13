using System;
using System.IO;
using System.Linq;

namespace FRBStudio.NativeShell
{
    internal sealed class WorkspacePolicy
    {
        public string RootPath { get; private set; }

        public WorkspacePolicy(string rootPath)
        {
            SetRoot(rootPath);
        }

        public void SetRoot(string rootPath)
        {
            if (string.IsNullOrWhiteSpace(rootPath))
                throw new ArgumentException("Workspace root is required.", nameof(rootPath));

            var full = Path.GetFullPath(rootPath);
            if (!Directory.Exists(full))
                throw new DirectoryNotFoundException(full);

            RootPath = TrimEndingSeparator(full);
        }

        public string ResolveRelativePath(string relativePath, bool allowMissingLeaf = false)
        {
            var normalized = (relativePath ?? string.Empty).Trim().Replace('/', Path.DirectorySeparatorChar);
            if (Path.IsPathRooted(normalized))
                throw new InvalidOperationException("WORKSPACE_PATH_DENIED: absolute path is not allowed.");

            var full = Path.GetFullPath(Path.Combine(RootPath, normalized));
            EnsureInsideWorkspace(full);
            EnsureNoReparsePointEscape(full, allowMissingLeaf);
            return full;
        }

        public string ToRelativePath(string fullPath)
        {
            var full = Path.GetFullPath(fullPath);
            EnsureInsideWorkspace(full);
            if (string.Equals(full, RootPath, StringComparison.OrdinalIgnoreCase)) return string.Empty;
            var rootWithSeparator = EnsureEndingSeparator(RootPath);
            return full.Substring(rootWithSeparator.Length).Replace(Path.DirectorySeparatorChar, '/');
        }

        public string ResolveWritablePath(string relativePath, string[] writableRoots, string[] writableFiles = null, bool allowMissingLeaf = true)
        {
            var full = ResolveRelativePath(relativePath, allowMissingLeaf);
            var relative = ToRelativePath(full).Replace('\\', '/').Trim('/');
            var allowedByRoot = (writableRoots ?? Array.Empty<string>())
                .Where(root => !string.IsNullOrWhiteSpace(root))
                .Select(root => root.Trim().Replace('\\', '/').Trim('/'))
                .Any(root => string.Equals(relative, root, StringComparison.OrdinalIgnoreCase)
                    || relative.StartsWith(root + "/", StringComparison.OrdinalIgnoreCase));
            var allowedByFile = (writableFiles ?? Array.Empty<string>())
                .Where(file => !string.IsNullOrWhiteSpace(file))
                .Select(file => file.Trim().Replace('\\', '/').Trim('/'))
                .Any(file => string.Equals(relative, file, StringComparison.OrdinalIgnoreCase));
            if (!allowedByRoot && !allowedByFile)
                throw new InvalidOperationException("WORKSPACE_PATH_DENIED: path is outside writable roots/files.");
            return full;
        }

        private void EnsureInsideWorkspace(string fullPath)
        {
            if (string.Equals(fullPath, RootPath, StringComparison.OrdinalIgnoreCase)) return;
            if (!fullPath.StartsWith(EnsureEndingSeparator(RootPath), StringComparison.OrdinalIgnoreCase))
                throw new InvalidOperationException("WORKSPACE_PATH_DENIED: path escapes workspace.");
        }

        private void EnsureNoReparsePointEscape(string fullPath, bool allowMissingLeaf)
        {
            var root = new DirectoryInfo(RootPath);
            var rootWithSeparator = EnsureEndingSeparator(RootPath);
            var relative = string.Equals(fullPath, RootPath, StringComparison.OrdinalIgnoreCase)
                ? string.Empty
                : fullPath.Substring(rootWithSeparator.Length);

            var current = root.FullName;
            var parts = relative.Split(new[] { Path.DirectorySeparatorChar }, StringSplitOptions.RemoveEmptyEntries);
            for (var i = 0; i < parts.Length; i++)
            {
                current = Path.Combine(current, parts[i]);
                var isLeaf = i == parts.Length - 1;
                if (!File.Exists(current) && !Directory.Exists(current))
                {
                    if (allowMissingLeaf || isLeaf) break;
                    continue;
                }

                var attributes = File.GetAttributes(current);
                if ((attributes & FileAttributes.ReparsePoint) != 0)
                    throw new InvalidOperationException("WORKSPACE_PATH_DENIED: reparse point is not allowed in workspace paths.");
            }
        }

        private static string EnsureEndingSeparator(string path)
            => path.EndsWith(Path.DirectorySeparatorChar.ToString(), StringComparison.Ordinal)
                ? path
                : path + Path.DirectorySeparatorChar;

        private static string TrimEndingSeparator(string path)
            => path.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
    }
}
