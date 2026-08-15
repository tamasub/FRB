using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Web.Script.Serialization;

namespace FRBStudio.NativeShell
{
    internal sealed class NativeCommandDispatcher
    {
        private readonly NativeShellConfig _config;
        private readonly WorkspacePolicy _workspace;
        private readonly JavaScriptSerializer _serializer = new JavaScriptSerializer { MaxJsonLength = int.MaxValue };
        private readonly Dictionary<string, WorkspacePolicy> _folderGrants = new Dictionary<string, WorkspacePolicy>(StringComparer.OrdinalIgnoreCase);
        private readonly Dictionary<string, string> _documentGrants = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        private readonly Dictionary<string, string> _persistedFolderGrantPaths = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        private readonly string _persistedFolderGrantStorePath;

        public NativeCommandDispatcher(NativeShellConfig config, WorkspacePolicy workspace)
        {
            _config = config;
            _workspace = workspace;
            var localAppData = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
            _persistedFolderGrantStorePath = Path.Combine(localAppData, "FRBStudio", "folder_grants.json");
            LoadPersistedFolderGrants();
        }

        public async Task<string> DispatchAsync(string messageJson)
        {
            string requestId = null;
            string command = null;
            try
            {
                var request = _serializer.DeserializeObject(messageJson) as Dictionary<string, object>;
                if (request == null) return SerializeError(null, null, "INVALID_MESSAGE", "JSON object is required.");

                requestId = GetString(request, "request_id");
                command = GetString(request, "command");
                var protocolVersion = GetString(request, "protocol_version") ?? string.Empty;
                var payload = GetDictionary(request, "payload") ?? new Dictionary<string, object>(StringComparer.OrdinalIgnoreCase);

                if (!string.Equals(protocolVersion, _config.ProtocolVersion, StringComparison.Ordinal))
                    return SerializeError(requestId, command, "UNSUPPORTED_PROTOCOL_VERSION", "protocol_version is not supported.");

                if (string.IsNullOrWhiteSpace(requestId))
                    return SerializeError(null, command, "REQUEST_ID_REQUIRED", "request_id is required.");

                if (string.IsNullOrWhiteSpace(command))
                    return SerializeError(requestId, null, "COMMAND_REQUIRED", "command is required.");

                if (!_config.AllowedCommands.Contains(command))
                    return SerializeError(requestId, command, "COMMAND_NOT_ALLOWED", "The native command is not enabled by native_shell.config.json.");

                var result = await ExecuteAsync(command, payload);
                return _serializer.Serialize(new Dictionary<string, object>
                {
                    ["protocol_version"] = _config.ProtocolVersion,
                    ["request_id"] = requestId,
                    ["command"] = command,
                    ["success"] = true,
                    ["result"] = result,
                    ["error"] = null
                });
            }
            catch (OperationCanceledException)
            {
                return SerializeError(requestId, command, "USER_CANCELLED", "Operation cancelled by user.");
            }
            catch (Exception ex)
            {
                var code = ex.Message != null && ex.Message.StartsWith("WORKSPACE_PATH_DENIED", StringComparison.Ordinal)
                    ? "WORKSPACE_PATH_DENIED"
                    : "NATIVE_OPERATION_FAILED";
                return SerializeError(requestId, command, code, ex.Message);
            }
        }

        private async Task<object> ExecuteAsync(string command, IDictionary<string, object> payload)
        {
            switch (command)
            {
                case "system.ping":
                    return new Dictionary<string, object>
                    {
                        ["pong"] = true,
                        ["protocol_version"] = _config.ProtocolVersion,
                        ["workspace_root"] = _workspace.RootPath
                    };

                case "workspace.getCurrent":
                    return new Dictionary<string, object> { ["root_path"] = _workspace.RootPath };

                case "workspace.select":
                    return SelectWorkspace();

                case "folderGrant.select":
                    return SelectFolderGrant(payload);

                case "folderGrant.restore":
                    return RestoreFolderGrant(payload);

                case "folderGrant.list":
                    return ListFolderGrant(payload);

                case "folderGrant.readText":
                    return ReadFolderGrantText(payload);

                case "folderGrant.writeText":
                    return WriteFolderGrantText(payload);

                case "folderGrant.exists":
                    return FolderGrantExists(payload);

                case "folderGrant.createDirectory":
                    return CreateFolderGrantDirectory(payload);

                case "folderGrant.move":
                    return MoveFolderGrantEntry(payload);

                case "folderGrant.describePath":
                    return DescribeFolderGrantPath(payload);

                case "document.writeText":
                    return WriteGrantedDocument(payload);

                case "file.exists":
                    return FileExists(payload);

                case "file.list":
                    return ListFiles(payload);

                case "file.readText":
                    return ReadText(payload);

                case "file.writeText":
                    return WriteText(payload);

                case "dialog.openText":
                    return OpenTextDialog(payload);

                case "dialog.saveText":
                    return SaveTextDialog(payload);

                case "shell.openFolder":
                    return OpenFolder(payload);

                case "process.runProfile":
                    return await RunProcessProfileAsync(payload);

                default:
                    throw new InvalidOperationException("UNKNOWN_COMMAND: command is not implemented by this Native Shell.");
            }
        }

        private object SelectWorkspace()
        {
            using (var dialog = new FolderBrowserDialog
            {
                Description = "FRB Studio Workspace を選択",
                SelectedPath = _workspace.RootPath,
                ShowNewFolderButton = false
            })
            {
                if (dialog.ShowDialog() != DialogResult.OK)
                    throw new OperationCanceledException();

                _workspace.SetRoot(dialog.SelectedPath);
                return new Dictionary<string, object> { ["root_path"] = _workspace.RootPath };
            }
        }

        private object SelectFolderGrant(IDictionary<string, object> payload)
        {
            using (var dialog = new FolderBrowserDialog
            {
                Description = GetString(payload, "description") ?? "フォルダーを開く",
                SelectedPath = Directory.Exists(GetString(payload, "initial_path") ?? string.Empty)
                    ? GetString(payload, "initial_path")
                    : _workspace.RootPath,
                ShowNewFolderButton = false
            })
            {
                if (dialog.ShowDialog() != DialogResult.OK)
                    throw new OperationCanceledException();

                var policy = new WorkspacePolicy(dialog.SelectedPath);
                var persistKey = NormalizePersistKey(GetString(payload, "persist_key"), allowEmpty: true);
                if (!string.IsNullOrWhiteSpace(persistKey))
                {
                    _persistedFolderGrantPaths[persistKey] = policy.RootPath;
                    SavePersistedFolderGrants();
                }
                return ActivateFolderGrant(policy, persistKey, restored: false);
            }
        }

        private object RestoreFolderGrant(IDictionary<string, object> payload)
        {
            var persistKey = NormalizePersistKey(RequiredString(payload, "persist_key"), allowEmpty: false);
            if (!_persistedFolderGrantPaths.TryGetValue(persistKey, out var rootPath) || !Directory.Exists(rootPath))
            {
                return new Dictionary<string, object>
                {
                    ["restored"] = false,
                    ["persist_key"] = persistKey
                };
            }

            var policy = new WorkspacePolicy(rootPath);
            return ActivateFolderGrant(policy, persistKey, restored: true);
        }

        private object ActivateFolderGrant(WorkspacePolicy policy, string persistKey, bool restored)
        {
            var grantId = "folder-" + Guid.NewGuid().ToString("N");
            _folderGrants[grantId] = policy;
            return new Dictionary<string, object>
            {
                ["restored"] = restored,
                ["grant_id"] = grantId,
                ["root_path"] = policy.RootPath,
                ["root_name"] = new DirectoryInfo(policy.RootPath).Name,
                ["persist_key"] = persistKey ?? string.Empty
            };
        }

        private static string NormalizePersistKey(string raw, bool allowEmpty)
        {
            var value = (raw ?? string.Empty).Trim();
            if (string.IsNullOrEmpty(value) && allowEmpty) return string.Empty;
            if (!Regex.IsMatch(value, "^[A-Za-z0-9_.-]{1,80}$"))
                throw new InvalidOperationException("INVALID_PERSIST_KEY: persist_key is invalid.");
            return value;
        }

        private void LoadPersistedFolderGrants()
        {
            try
            {
                if (!File.Exists(_persistedFolderGrantStorePath)) return;
                var json = File.ReadAllText(_persistedFolderGrantStorePath, Encoding.UTF8);
                var loaded = _serializer.Deserialize<Dictionary<string, string>>(json);
                if (loaded == null) return;
                foreach (var item in loaded)
                {
                    var key = NormalizePersistKey(item.Key, allowEmpty: false);
                    if (!string.IsNullOrWhiteSpace(item.Value)) _persistedFolderGrantPaths[key] = item.Value;
                }
            }
            catch
            {
                _persistedFolderGrantPaths.Clear();
            }
        }

        private void SavePersistedFolderGrants()
        {
            var directory = Path.GetDirectoryName(_persistedFolderGrantStorePath);
            if (!Directory.Exists(directory)) Directory.CreateDirectory(directory);
            File.WriteAllText(_persistedFolderGrantStorePath, _serializer.Serialize(_persistedFolderGrantPaths), new UTF8Encoding(false));
        }

        private WorkspacePolicy RequiredFolderGrant(IDictionary<string, object> payload)
        {
            var grantId = RequiredString(payload, "grant_id");
            if (!_folderGrants.TryGetValue(grantId, out var policy))
                throw new InvalidOperationException("FOLDER_GRANT_NOT_FOUND: folder grant is not active.");
            return policy;
        }

        private object ListFolderGrant(IDictionary<string, object> payload)
        {
            var policy = RequiredFolderGrant(payload);
            var path = GetString(payload, "path") ?? string.Empty;
            var full = policy.ResolveRelativePath(path);
            if (!Directory.Exists(full)) throw new DirectoryNotFoundException(full);

            var extensions = GetStringList(payload, "extensions")
                .Select(x => x.StartsWith(".", StringComparison.Ordinal) ? x : "." + x)
                .ToArray();
            var includeFiles = GetBool(payload, "include_files", true);
            var includeDirectories = GetBool(payload, "include_directories", true);
            var items = new List<object>();

            if (includeDirectories)
            {
                foreach (var dir in Directory.EnumerateDirectories(full, "*", SearchOption.TopDirectoryOnly)
                    .OrderBy(x => Path.GetFileName(x), StringComparer.OrdinalIgnoreCase))
                {
                    items.Add(new Dictionary<string, object>
                    {
                        ["path"] = policy.ToRelativePath(dir),
                        ["name"] = Path.GetFileName(dir),
                        ["is_directory"] = true,
                        ["size"] = 0L
                    });
                }
            }

            if (includeFiles)
            {
                foreach (var file in Directory.EnumerateFiles(full, "*", SearchOption.TopDirectoryOnly)
                    .Where(file => extensions.Length == 0 || extensions.Contains(Path.GetExtension(file), StringComparer.OrdinalIgnoreCase))
                    .OrderBy(x => Path.GetFileName(x), StringComparer.OrdinalIgnoreCase))
                {
                    items.Add(new Dictionary<string, object>
                    {
                        ["path"] = policy.ToRelativePath(file),
                        ["name"] = Path.GetFileName(file),
                        ["is_directory"] = false,
                        ["size"] = new FileInfo(file).Length
                    });
                }
            }

            return new Dictionary<string, object> { ["items"] = items.ToArray() };
        }

        private object ReadFolderGrantText(IDictionary<string, object> payload)
        {
            var policy = RequiredFolderGrant(payload);
            var path = RequiredString(payload, "path");
            var full = policy.ResolveRelativePath(path);
            if (!File.Exists(full)) throw new FileNotFoundException("File not found.", full);
            return new Dictionary<string, object>
            {
                ["path"] = policy.ToRelativePath(full),
                ["full_path"] = full,
                ["content"] = File.ReadAllText(full, new UTF8Encoding(false, true)),
                ["size"] = new FileInfo(full).Length,
                ["last_write_time_utc"] = File.GetLastWriteTimeUtc(full).ToString("o")
            };
        }

        private object WriteFolderGrantText(IDictionary<string, object> payload)
        {
            var policy = RequiredFolderGrant(payload);
            var path = RequiredString(payload, "path");
            var content = GetString(payload, "content") ?? string.Empty;
            var full = policy.ResolveRelativePath(path, allowMissingLeaf: true);
            var dir = Path.GetDirectoryName(full);
            if (!string.IsNullOrWhiteSpace(dir) && !Directory.Exists(dir))
            {
                if (!GetBool(payload, "create_directories", false))
                    throw new DirectoryNotFoundException(dir);
                Directory.CreateDirectory(dir);
            }
            File.WriteAllText(full, content, new UTF8Encoding(false));
            return new Dictionary<string, object>
            {
                ["saved"] = policy.ToRelativePath(full),
                ["full_path"] = full,
                ["size"] = new FileInfo(full).Length
            };
        }

        private object FolderGrantExists(IDictionary<string, object> payload)
        {
            var policy = RequiredFolderGrant(payload);
            var path = GetString(payload, "path") ?? string.Empty;
            var full = policy.ResolveRelativePath(path, allowMissingLeaf: true);
            return new Dictionary<string, object>
            {
                ["exists"] = File.Exists(full) || Directory.Exists(full),
                ["is_file"] = File.Exists(full),
                ["is_directory"] = Directory.Exists(full),
                ["path"] = path.Replace('\\', '/'),
                ["full_path"] = full
            };
        }

        private object CreateFolderGrantDirectory(IDictionary<string, object> payload)
        {
            var policy = RequiredFolderGrant(payload);
            var path = RequiredString(payload, "path");
            var full = policy.ResolveRelativePath(path, allowMissingLeaf: true);
            var existed = Directory.Exists(full);
            Directory.CreateDirectory(full);
            return new Dictionary<string, object>
            {
                ["created"] = !existed,
                ["path"] = policy.ToRelativePath(full),
                ["full_path"] = full
            };
        }

        private object DescribeFolderGrantPath(IDictionary<string, object> payload)
        {
            var policy = RequiredFolderGrant(payload);
            var path = GetString(payload, "path") ?? string.Empty;
            var full = policy.ResolveRelativePath(path, allowMissingLeaf: true);
            return new Dictionary<string, object>
            {
                ["path"] = path.Replace('\\', '/'),
                ["full_path"] = full,
                ["root_path"] = policy.RootPath
            };
        }

        private object MoveFolderGrantEntry(IDictionary<string, object> payload)
        {
            var policy = RequiredFolderGrant(payload);
            var sourcePath = RequiredString(payload, "source_path");
            var destinationPath = RequiredString(payload, "destination_path");
            var source = policy.ResolveRelativePath(sourcePath);
            var destination = policy.ResolveRelativePath(destinationPath, allowMissingLeaf: true);
            if (File.Exists(destination) || Directory.Exists(destination))
                throw new IOException("DESTINATION_EXISTS: destination already exists.");

            var destinationParent = Path.GetDirectoryName(destination);
            if (string.IsNullOrWhiteSpace(destinationParent) || !Directory.Exists(destinationParent))
                throw new DirectoryNotFoundException(destinationParent ?? destination);

            var sourceIsFile = File.Exists(source);
            var sourceIsDirectory = Directory.Exists(source);
            if (!sourceIsFile && !sourceIsDirectory)
                throw new FileNotFoundException("Source not found.", source);

            // Preflight all companion destinations before moving anything.
            // A Markdown + Sidecar move must never leave the document set half-moved
            // merely because a companion destination already existed.
            var companionMoves = new List<Tuple<string, string, string>>();
            if (sourceIsFile)
            {
                foreach (var suffix in GetStringList(payload, "companion_suffixes"))
                {
                    var sourceCompanion = source + suffix;
                    if (!File.Exists(sourceCompanion)) continue;
                    var destinationCompanion = destination + suffix;
                    if (File.Exists(destinationCompanion) || Directory.Exists(destinationCompanion))
                        throw new IOException("DESTINATION_EXISTS: companion destination already exists.");
                    companionMoves.Add(Tuple.Create(suffix, sourceCompanion, destinationCompanion));
                }
            }

            if (sourceIsFile)
                File.Move(source, destination);
            else
                Directory.Move(source, destination);

            var companionsMoved = new List<object>();
            foreach (var companionMove in companionMoves)
            {
                File.Move(companionMove.Item2, companionMove.Item3);
                companionsMoved.Add(new Dictionary<string, object>
                {
                    ["suffix"] = companionMove.Item1,
                    ["path"] = policy.ToRelativePath(companionMove.Item3)
                });
            }

            return new Dictionary<string, object>
            {
                ["moved"] = true,
                ["source_path"] = sourcePath.Replace('\\', '/'),
                ["destination_path"] = policy.ToRelativePath(destination),
                ["companions"] = companionsMoved.ToArray()
            };
        }

        private string RegisterDocumentGrant(string fullPath)
        {
            var full = Path.GetFullPath(fullPath);
            var documentId = "document-" + Guid.NewGuid().ToString("N");
            _documentGrants[documentId] = full;
            return documentId;
        }

        private object WriteGrantedDocument(IDictionary<string, object> payload)
        {
            var documentId = RequiredString(payload, "document_id");
            if (!_documentGrants.TryGetValue(documentId, out var full))
                throw new InvalidOperationException("DOCUMENT_GRANT_NOT_FOUND: document grant is not active.");
            if (!File.Exists(full)) throw new FileNotFoundException("Granted document not found.", full);
            var content = GetString(payload, "content") ?? string.Empty;
            File.WriteAllText(full, content, new UTF8Encoding(false));
            return new Dictionary<string, object>
            {
                ["saved"] = Path.GetFileName(full),
                ["path"] = full,
                ["document_id"] = documentId,
                ["size"] = new FileInfo(full).Length
            };
        }

        private object FileExists(IDictionary<string, object> payload)
        {
            var path = RequiredString(payload, "path");
            var full = _workspace.ResolveRelativePath(path, allowMissingLeaf: true);
            return new Dictionary<string, object>
            {
                ["exists"] = File.Exists(full) || Directory.Exists(full),
                ["is_file"] = File.Exists(full),
                ["is_directory"] = Directory.Exists(full),
                ["path"] = path.Replace('\\', '/')
            };
        }

        private object ListFiles(IDictionary<string, object> payload)
        {
            var path = GetString(payload, "path") ?? string.Empty;
            var full = _workspace.ResolveRelativePath(path);
            if (!Directory.Exists(full))
                throw new DirectoryNotFoundException(full);

            var recursive = GetBool(payload, "recursive", true);
            var entryKind = (GetString(payload, "entry_kind") ?? "files").Trim().ToLowerInvariant();
            var extensions = GetStringList(payload, "extensions")
                .Select(x => x.StartsWith(".", StringComparison.Ordinal) ? x : "." + x)
                .ToArray();
            var search = recursive ? SearchOption.AllDirectories : SearchOption.TopDirectoryOnly;

            IEnumerable<string> entries;
            if (entryKind == "directories")
            {
                entries = Directory.EnumerateDirectories(full, "*", search);
            }
            else
            {
                entries = Directory.EnumerateFiles(full, "*", search);
                if (extensions.Length > 0)
                    entries = entries.Where(file => extensions.Contains(Path.GetExtension(file), StringComparer.OrdinalIgnoreCase));
            }

            var items = entries
                .Select(item => new Dictionary<string, object>
                {
                    ["path"] = _workspace.ToRelativePath(item),
                    ["name"] = Path.GetFileName(item),
                    ["is_directory"] = Directory.Exists(item),
                    ["size"] = File.Exists(item) ? new FileInfo(item).Length : 0L
                })
                .OrderBy(x => Convert.ToString(x["path"]), StringComparer.OrdinalIgnoreCase)
                .Cast<object>()
                .ToArray();

            return new Dictionary<string, object> { ["items"] = items };
        }

        private object ReadText(IDictionary<string, object> payload)
        {
            var path = RequiredString(payload, "path");
            var full = _workspace.ResolveRelativePath(path);
            if (!File.Exists(full)) throw new FileNotFoundException("File not found.", full);

            return new Dictionary<string, object>
            {
                ["path"] = path.Replace('\\', '/'),
                ["content"] = File.ReadAllText(full, new UTF8Encoding(false, true)),
                ["size"] = new FileInfo(full).Length,
                ["last_write_time_utc"] = File.GetLastWriteTimeUtc(full).ToString("o")
            };
        }

        private object WriteText(IDictionary<string, object> payload)
        {
            var path = RequiredString(payload, "path");
            var content = GetString(payload, "content") ?? string.Empty;
            var createDirectories = GetBool(payload, "create_directories", true);
            var full = _workspace.ResolveWritablePath(path, _config.WritableRoots, allowMissingLeaf: true);
            var dir = Path.GetDirectoryName(full);
            if (createDirectories && !string.IsNullOrWhiteSpace(dir)) Directory.CreateDirectory(dir);

            File.WriteAllText(full, content, new UTF8Encoding(false));
            return new Dictionary<string, object>
            {
                ["saved"] = path.Replace('\\', '/'),
                ["size"] = new FileInfo(full).Length
            };
        }

        private object OpenTextDialog(IDictionary<string, object> payload)
        {
            using (var dialog = new OpenFileDialog
            {
                Title = GetString(payload, "title") ?? "ファイルを開く",
                Filter = GetString(payload, "filter") ?? "Text files|*.json;*.md;*.markdown;*.txt|All files|*.*",
                Multiselect = false,
                CheckFileExists = true
            })
            {
                if (dialog.ShowDialog() != DialogResult.OK) throw new OperationCanceledException();

                var selected = dialog.FileName;
                var companions = new Dictionary<string, object>(StringComparer.OrdinalIgnoreCase);
                foreach (var suffix in GetStringList(payload, "companion_suffixes"))
                {
                    var companionPath = selected + suffix;
                    companions[suffix] = File.Exists(companionPath)
                        ? (object)new Dictionary<string, object>
                        {
                            ["found"] = true,
                            ["path"] = companionPath,
                            ["content"] = File.ReadAllText(companionPath, Encoding.UTF8)
                        }
                        : new Dictionary<string, object> { ["found"] = false };
                }

                var documentId = RegisterDocumentGrant(selected);
                return new Dictionary<string, object>
                {
                    ["cancelled"] = false,
                    ["document_id"] = documentId,
                    ["file_name"] = Path.GetFileName(selected),
                    ["path"] = selected,
                    ["content"] = File.ReadAllText(selected, Encoding.UTF8),
                    ["companions"] = companions
                };
            }
        }

        private object SaveTextDialog(IDictionary<string, object> payload)
        {
            using (var dialog = new SaveFileDialog
            {
                Title = GetString(payload, "title") ?? "名前を付けて保存",
                Filter = GetString(payload, "filter") ?? "Text files|*.json;*.md;*.markdown;*.txt|All files|*.*",
                FileName = GetString(payload, "file_name") ?? string.Empty,
                DefaultExt = GetString(payload, "default_extension") ?? string.Empty,
                AddExtension = true,
                OverwritePrompt = true
            })
            {
                if (dialog.ShowDialog() != DialogResult.OK) throw new OperationCanceledException();

                var content = GetString(payload, "content") ?? string.Empty;
                File.WriteAllText(dialog.FileName, content, new UTF8Encoding(false));

                var companionsSaved = new List<object>();
                foreach (var companion in GetDictionaryList(payload, "companions"))
                {
                    var suffix = GetString(companion, "suffix");
                    if (string.IsNullOrWhiteSpace(suffix)) continue;
                    var companionContent = GetString(companion, "content") ?? string.Empty;
                    var companionPath = dialog.FileName + suffix;
                    File.WriteAllText(companionPath, companionContent, new UTF8Encoding(false));
                    companionsSaved.Add(new Dictionary<string, object>
                    {
                        ["suffix"] = suffix,
                        ["path"] = companionPath,
                        ["file_name"] = Path.GetFileName(companionPath)
                    });
                }

                var documentId = RegisterDocumentGrant(dialog.FileName);
                return new Dictionary<string, object>
                {
                    ["cancelled"] = false,
                    ["document_id"] = documentId,
                    ["file_name"] = Path.GetFileName(dialog.FileName),
                    ["path"] = dialog.FileName,
                    ["companions"] = companionsSaved.ToArray()
                };
            }
        }

        private object OpenFolder(IDictionary<string, object> payload)
        {
            var path = RequiredString(payload, "path");
            var full = _workspace.ResolveRelativePath(path);
            var selectFile = GetBool(payload, "select_file", true);

            if (File.Exists(full) && selectFile)
                Process.Start("explorer.exe", "/select,\"" + full + "\"");
            else
            {
                var folder = Directory.Exists(full) ? full : Path.GetDirectoryName(full);
                if (string.IsNullOrWhiteSpace(folder) || !Directory.Exists(folder))
                    throw new DirectoryNotFoundException(folder ?? full);
                Process.Start("explorer.exe", "\"" + folder + "\"");
            }

            return new Dictionary<string, object> { ["opened"] = true, ["path"] = path.Replace('\\', '/') };
        }


        private async Task<object> RunProcessProfileAsync(IDictionary<string, object> payload)
        {
            var profileId = RequiredString(payload, "profile_id");
            if (!_config.ProcessProfiles.TryGetValue(profileId, out var profile))
                throw new InvalidOperationException("PROCESS_PROFILE_NOT_ALLOWED: unknown profile_id.");

            if (string.IsNullOrWhiteSpace(profile.Executable))
                throw new InvalidOperationException("PROCESS_PROFILE_INVALID: executable is empty.");

            var workingDirectory = _workspace.ResolveRelativePath(profile.WorkingDirectory ?? string.Empty);
            var argumentTokens = new List<string>();
            argumentTokens.AddRange(profile.FixedArguments ?? Array.Empty<string>());

            foreach (var spec in profile.Parameters ?? Array.Empty<NativeProcessParameter>())
            {
                payload.TryGetValue(spec.Key, out var rawValue);
                var token = ValidateProcessParameter(spec, rawValue);
                if (token == null) continue;

                if (string.Equals(spec.Kind, "boolean_switch", StringComparison.OrdinalIgnoreCase))
                {
                    if ((bool)token && !string.IsNullOrWhiteSpace(spec.Switch)) argumentTokens.Add(spec.Switch);
                    continue;
                }

                if (!string.IsNullOrWhiteSpace(spec.Switch)) argumentTokens.Add(spec.Switch);
                argumentTokens.Add(Convert.ToString(token));
            }

            var arguments = string.Join(" ", argumentTokens.Select(QuoteArgument));
            var launchMode = IsLaunchMode(profile, payload);
            var startInfo = new ProcessStartInfo
            {
                FileName = profile.Executable,
                Arguments = arguments,
                WorkingDirectory = workingDirectory,
                UseShellExecute = false,
                CreateNoWindow = true,
                RedirectStandardOutput = !launchMode,
                RedirectStandardError = !launchMode
            };
            if (!launchMode)
            {
                startInfo.StandardOutputEncoding = Encoding.UTF8;
                startInfo.StandardErrorEncoding = Encoding.UTF8;
            }

            var startedAt = DateTime.UtcNow;
            var stopwatch = Stopwatch.StartNew();
            var process = new Process { StartInfo = startInfo };
            if (!process.Start()) throw new InvalidOperationException("PROCESS_START_FAILED");
            if (launchMode)
            {
                return new Dictionary<string, object>
                {
                    ["profile_id"] = profile.Id,
                    ["display_name"] = profile.DisplayName,
                    ["result_kind"] = "command_launched",
                    ["success"] = true,
                    ["run_mode"] = "launch",
                    ["process_id"] = process.Id,
                    ["command_preview"] = profile.Executable + " " + arguments,
                    ["working_directory"] = workingDirectory,
                    ["duration_ms"] = stopwatch.ElapsedMilliseconds,
                    ["message"] = profile.DisplayName + " を起動しました"
                };
            }

            var stdoutTask = process.StandardOutput.ReadToEndAsync();
            var stderrTask = process.StandardError.ReadToEndAsync();
            var timeoutMs = Math.Max(1, profile.TimeoutSeconds) * 1000;
            var exited = await Task.Run(() => process.WaitForExit(timeoutMs));
            if (!exited)
            {
                try { process.Kill(); } catch { }
                throw new TimeoutException("PROCESS_TIMEOUT: " + profile.Id);
            }

            var stdout = await stdoutTask;
            var stderr = await stderrTask;
            stopwatch.Stop();
            var artifacts = FindOutputArtifacts(profile, startedAt);
            var success = process.ExitCode == 0;
            var resultKind = string.Equals(profile.Id, "test_runner", StringComparison.OrdinalIgnoreCase)
                ? (success ? "test_passed" : "test_failed")
                : (success ? "command_completed" : "command_failed");

            return new Dictionary<string, object>
            {
                ["profile_id"] = profile.Id,
                ["display_name"] = profile.DisplayName,
                ["result_kind"] = resultKind,
                ["success"] = success,
                ["run_mode"] = GetString(payload, "run_mode") ?? "wait",
                ["test_runner_id"] = GetString(payload, "test_runner_id") ?? string.Empty,
                ["exit_code"] = process.ExitCode,
                ["duration_ms"] = stopwatch.ElapsedMilliseconds,
                ["working_directory"] = workingDirectory,
                ["command_preview"] = profile.Executable + " " + arguments,
                ["stdout"] = stdout,
                ["stderr"] = stderr,
                ["output_artifacts"] = artifacts,
                ["message"] = success ? profile.DisplayName + " が完了しました" : profile.DisplayName + " が失敗しました"
            };
        }

        private object ValidateProcessParameter(NativeProcessParameter spec, object rawValue)
        {
            if (string.Equals(spec.Kind, "boolean_switch", StringComparison.OrdinalIgnoreCase))
            {
                if (rawValue == null) return false;
                if (rawValue is bool b) return b;
                return bool.TryParse(Convert.ToString(rawValue), out var parsed) && parsed;
            }

            var text = Convert.ToString(rawValue)?.Trim() ?? string.Empty;
            if (string.IsNullOrWhiteSpace(text))
            {
                if (spec.OmitIfEmpty) return null;
                throw new InvalidOperationException("PROCESS_PARAMETER_REQUIRED: " + spec.Key);
            }

            if (string.Equals(spec.Kind, "enum", StringComparison.OrdinalIgnoreCase))
            {
                if (!spec.AllowedValues.Contains(text, StringComparer.OrdinalIgnoreCase))
                    throw new InvalidOperationException("PROCESS_PARAMETER_DENIED: " + spec.Key);
                return text;
            }

            if (string.Equals(spec.Kind, "integer", StringComparison.OrdinalIgnoreCase))
            {
                if (!int.TryParse(text, out var value) || value < spec.Min || value > spec.Max)
                    throw new InvalidOperationException("PROCESS_PARAMETER_DENIED: " + spec.Key);
                return value.ToString();
            }

            if (string.Equals(spec.Kind, "workspace_path", StringComparison.OrdinalIgnoreCase))
            {
                if (Path.IsPathRooted(text))
                {
                    var relative = _workspace.ToRelativePath(Path.GetFullPath(text));
                    _workspace.ResolveRelativePath(relative, allowMissingLeaf: true);
                    return relative;
                }

                var full = _workspace.ResolveRelativePath(text, allowMissingLeaf: true);
                return _workspace.ToRelativePath(full);
            }

            if (!string.IsNullOrWhiteSpace(spec.Pattern) && !Regex.IsMatch(text, spec.Pattern, RegexOptions.CultureInvariant))
                throw new InvalidOperationException("PROCESS_PARAMETER_DENIED: " + spec.Key);

            return text;
        }

        private bool IsLaunchMode(NativeProcessProfile profile, IDictionary<string, object> payload)
        {
            if (string.IsNullOrWhiteSpace(profile.LaunchParameterKey)) return false;
            var value = GetString(payload, profile.LaunchParameterKey) ?? string.Empty;
            return string.Equals(value, profile.LaunchParameterValue, StringComparison.OrdinalIgnoreCase);
        }

        private object[] FindOutputArtifacts(NativeProcessProfile profile, DateTime startedAtUtc)
        {
            var output = new List<object>();
            foreach (var glob in profile.OutputGlobs ?? Array.Empty<string>())
            {
                var normalized = (glob ?? string.Empty).Replace('/', Path.DirectorySeparatorChar);
                var dirPart = Path.GetDirectoryName(normalized) ?? string.Empty;
                var pattern = Path.GetFileName(normalized);
                if (string.IsNullOrWhiteSpace(pattern)) continue;

                string fullDir;
                try { fullDir = _workspace.ResolveRelativePath(dirPart); }
                catch { continue; }
                if (!Directory.Exists(fullDir)) continue;

                foreach (var file in Directory.EnumerateFiles(fullDir, pattern, SearchOption.TopDirectoryOnly))
                {
                    var info = new FileInfo(file);
                    if (info.LastWriteTimeUtc < startedAtUtc.AddSeconds(-2)) continue;
                    output.Add(new Dictionary<string, object>
                    {
                        ["path"] = _workspace.ToRelativePath(file),
                        ["exists"] = true,
                        ["kind"] = "file",
                        ["last_write_time_utc"] = info.LastWriteTimeUtc.ToString("o")
                    });
                }
            }

            return output
                .OrderByDescending(item => Convert.ToString(((Dictionary<string, object>)item)["last_write_time_utc"]))
                .ToArray();
        }

        private static string QuoteArgument(string value)
        {
            var text = value ?? string.Empty;
            if (text.Length > 0 && !text.Any(char.IsWhiteSpace) && !text.Contains("\"") && !text.Contains("\\")) return text;
            return "\"" + text.Replace("\\", "\\\\").Replace("\"", "\\\"") + "\"";
        }

        private string SerializeError(string requestId, string command, string code, string message)
        {
            return _serializer.Serialize(new Dictionary<string, object>
            {
                ["protocol_version"] = _config.ProtocolVersion,
                ["request_id"] = requestId,
                ["command"] = command,
                ["success"] = false,
                ["result"] = null,
                ["error"] = new Dictionary<string, object>
                {
                    ["code"] = code,
                    ["message"] = message ?? string.Empty
                }
            });
        }

        private static string RequiredString(IDictionary<string, object> raw, string key)
        {
            var value = GetString(raw, key);
            if (string.IsNullOrWhiteSpace(value)) throw new InvalidOperationException(key + " is required.");
            return value;
        }

        private static string GetString(IDictionary<string, object> raw, string key)
        {
            if (raw == null || !raw.TryGetValue(key, out var value) || value == null) return null;
            return Convert.ToString(value);
        }

        private static bool GetBool(IDictionary<string, object> raw, string key, bool fallback)
        {
            if (raw == null || !raw.TryGetValue(key, out var value) || value == null) return fallback;
            if (value is bool b) return b;
            return bool.TryParse(Convert.ToString(value), out var parsed) ? parsed : fallback;
        }

        private static Dictionary<string, object> GetDictionary(IDictionary<string, object> raw, string key)
        {
            if (raw == null || !raw.TryGetValue(key, out var value) || value == null) return null;
            return value as Dictionary<string, object>;
        }

        private static IEnumerable<string> GetStringList(IDictionary<string, object> raw, string key)
        {
            if (raw == null || !raw.TryGetValue(key, out var value) || value == null) yield break;
            foreach (var item in ToObjectEnumerable(value))
            {
                var text = Convert.ToString(item)?.Trim();
                if (!string.IsNullOrWhiteSpace(text)) yield return text;
            }
        }

        private static IEnumerable<Dictionary<string, object>> GetDictionaryList(IDictionary<string, object> raw, string key)
        {
            if (raw == null || !raw.TryGetValue(key, out var value) || value == null) yield break;
            foreach (var item in ToObjectEnumerable(value))
                if (item is Dictionary<string, object> dict) yield return dict;
        }

        private static IEnumerable<object> ToObjectEnumerable(object value)
        {
            if (value is object[] array) return array;
            if (value is ArrayList list) return list.Cast<object>();
            return Enumerable.Empty<object>();
        }
    }
}
