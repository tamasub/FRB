# Studio Change Core v0.1 (studio_work_0269)

## Implementation state

- External Node.js CLI prototype: implemented for **one JSON file / multiple `add` operations / append to end**.
- `dry_run` and `commit`, precondition `base_sha256`, cooperative `.studio-changeset.lock` and same-directory rename.
- The **existing Studio UI** still uses its legacy save path. UI/CLI unified guarantee is **not implemented**.
- Python integration, bundled `node.exe`, Windows filesystem validation, other add placements, Update/Delete/Move: pending.
- The CLI does not expose a server port.

## Trust boundary

1. Copy `config.example.json` **outside the distributed source if appropriate** and register allowed `documents` with absolute file paths. This is trusted administrator configuration; **do not pass an arbitrary file path through the request**.
2. A request supplies a `document_ref` only. `view_def`, `view_id`, and `section_ids` must match the allowlist config.
3. The request must supply the SHA-256 of the target file's **raw bytes**, read by the caller before building the ChangeSet. It is intentionally not derived from the commit-time file.
4. To use dry-run or commit: `node tools/change_core/cli.mjs --config /path/to/config.json < request.json`. stdout is one JSON result; exit code nonzero if rejected.
5. Do not aim the prototype at important files until Windows and NativeShell interactions have been verified. Back up data for integration testing.

## Example request

```json
{
  "schema_version": "studio_changeset_v0_1",
  "request_id": "external-add-001",
  "mode": "dry_run",
  "document_ref": "approved_launch_config",
  "base_sha256": "<64 lowercase hex chars computed from the document's original bytes>",
  "view_def": "launch/frb_launch_maintenance_view_def_v0_1.json",
  "view_id": "items_view",
  "operations": [{
    "operation": "add",
    "section_id": "items",
    "placement": {"group_id": "work", "parent_id": "folders", "position": "end"},
    "records": [{"title":"example.txt","item_kind":"command","launch_actions":[{"launch_action_type":"Open","launch_target":"C:\\example.txt"}]}]
  }]
}
```

`group_id` / `parent_id` are generic placement parameters; the actual row field names come from `section.tree`. Their literal values above are illustrative, not hard-coded. Parent and group must already exist in the target JSON. On the first implementation, only `position=end` is supported, and pre-existing records are not renumbered. A record may include a unique ID, otherwise the Core generates one UUID **before** expected and actual diff calculation.

## Guarantees and limits

- Validation: reuses existing `StudioTreeModel`; if a ViewDef declares `item_definition_ref`, also reuses Studio's DOM-independent Field Definition services. For ViewDefs without `item_definition_ref` the result explicitly reports `SKIPPED_FIELD_DEFINITION_NOT_DECLARED` (it **does not** mean all business rules were checked).
- The Expected Diff consists of the planned allowed row additions, the Actual Diff is calculated by comparing whole documents. Mismatch prevents committing. All changes are applied in memory before a single serialized document is saved.
- Document atomicity is **single-file** only. A failure before rename leaves the original untouched. Filesystem/OS guarantees, crash durability, ACL preservation, Windows file sharing, and uncooperative external editors require practical testing. There is no multi-file transaction.
- Exclusive lock is cooperative: only callers using `.studio-changeset.lock` are serialized. An external editor that ignores this lock can still race; the SHA-256 pre-rename check reduces but cannot eliminate this window. A stale lock after a hard process crash requires manual investigation/removal **after checking for a running writer**.
- The legacy Studio UI and other saving applications do **not** yet share this lock and CAS contract. Do not describe combined Studio + CLI editing as safely coordinated in v0.1.
- Failures are returned as structured `status` and `errors[]`. `CONFLICT` includes a stale SHA or lock contention; rejection leaves original unchanged.

## Tests

```
node --test tests/change_core/change_core.test.mjs tests/tree/tree_model.test.cjs tests/definition/cross_field_definition_test.test.mjs
```

See `data/markdown/STUDIO_CHANGE_CORE_STEP2_0269.md` for acceptance evidence and remaining work.

## Step 3 / NativeShell integration (2026-11-01)

- The NativeShell main `/api/data/{name}.json` save path now uses `file.writeTextCas` (including `fielddefs/` paths). It shares the **lock filename**, raw-byte SHA-256 precondition, and same-directory replacement approach with the external CLI.
- The Studio UI sends the SHA returned by `file.readText` on the initial GET; a changed file yields HTTP 409 and does not overwrite the other writer. **Reload/reconcile before retrying**.
- A 3.9 MB incident document previously failed in `NativeShellForm.OnWebMessageReceived`: the preliminary `new JavaScriptSerializer()` had the default ~2 MB limit, and the caught exception left no browser response. Large native messages now bypass the preliminary UI-control-message decode and reach the existing large-capacity dispatcher.
- **Important limitation**: UI full-document save and CLI `add` use different validation/Expected-diff implementations. They now coordinate storage via the shared lock/CAS **protocol**, but they do **not yet share all validation/Expected-diff Core code**. Other save routes (`/api/defs`, Markdown, startup document, etc.) remain on their prior implementation.
- Windows `File.Replace` and the Node `fs.rename` path are not yet proven equivalent under all Windows external-editor sharing modes. A real Windows NativeShell integration run is still mandatory.

### Python client (no Port)

```python
from tools.change_core.python_client import run_changeset, file_sha256

# document_path must come from trusted configuration, not an arbitrary request path.
request['base_sha256'] = file_sha256(document_path)  # at initial read, BEFORE edits
result = run_changeset(request, node_executable=r'portable\node.exe',
                       cli_path=r'portable\tools\change_core\cli.mjs',
                       config_path=r'approved_config.json')
if result['status'] != 'COMMITTED':
    print(result['status'], result['errors'])  # do not assume success
```

### Windows portable builder (requires valid Node distribution)

```powershell
powershell -File tools/change_core/prepare_portable.ps1 `
  -NodeExecutable C:\trusted-node\node.exe `
  -NodeLicenseFile C:\trusted-node\LICENSE `
  -Destination C:\build\change-core-portable
```

- The script copies only the CLI's needed application support files plus the user-provided executable and license. It **does not download**, verify, or license Node automatically; verify provenance and license before distribution.
- Output is a standalone **CLI folder**, not a Windows executable built or tested by this task. A separate Node install/PATH entry is not needed for a correctly assembled folder.
- No `node.exe` is included in the returned source patch. Test on Windows 11 with actual NativeShell + deployed binary before claiming the packaging acceptance condition.
