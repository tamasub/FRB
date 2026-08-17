# FRB Studio Native Shell — Phase A

`NativeShell/` is the second C# host for FRB Studio.

- `Program.cs/` — existing browser + localhost host (kept unchanged during migration)
- `NativeShell/` — WinForms + WebView2 host without a localhost listener

## Goal

Keep Studio's HTML/CSS/JavaScript and domain logic on the Web side while moving only OS-dependent operations to a thin native adapter.

The Native Shell is intentionally generic. Do not add commands such as `saveFieldDefinition` or `saveIncident`. Prefer generic operations such as `file.readText`, `file.writeText`, dialogs, and approved process profiles.

## Web UI loading

`wwwroot/` is mapped inside WebView2 to:

```text
https://frb-studio.local/
```

using WebView2 Virtual Host Name Mapping. The Native Shell does not start the existing localhost HTTP server.

## Native bridge contract

Web -> C# request:

```json
{
  "protocol_version": "1.0",
  "request_id": "native-...",
  "command": "file.readText",
  "payload": {
    "path": "data/json/sample.json"
  }
}
```

C# -> Web response:

```json
{
  "protocol_version": "1.0",
  "request_id": "native-...",
  "command": "file.readText",
  "success": true,
  "result": {},
  "error": null
}
```

## Configuration

`native_shell.config.json` controls:

- allowed native commands
- writable workspace roots
- process profiles and their allowed parameters
- virtual host name
- development options

`file.writeText` is restricted to configured writable roots. In Phase A these are `data/json`, `data/markdown`, `defs`, and `studio_overlays`; the Web UI cannot use that command to rewrite `NativeShell/`, `Program.cs/`, or `tools/`.

Adding a new profile that can be expressed with the existing generic `process.runProfile` command should be done in JSON rather than by adding Studio-specific C# logic. A genuinely new OS capability may still require C#.

## Build / runtime verification status

The source targets `.NET Framework 4.8` (`net48`) and x64 and references the Microsoft WebView2 SDK.

For normal Windows builds, run the root-level wrapper:

```text
cmd_compile_NativeShell.bat
```

The wrapper resolves `FRBStudio_App` from its own location and calls `tools/build/Build-NativeShell.ps1`. No `C:\...`, `D:\...`, or `F:\...` application path needs to be edited when the folder is moved to another PC.

Build output is always:

```text
NativeShell/_publish/
```

`dotnet` must be available on `PATH`. If it is not, fix the PC tool environment rather than embedding a machine-specific path into FRB Studio source.

This Phase A source has **not** been compiled in the ChatGPT execution environment because a Windows/.NET Framework build toolchain is not available there. Before treating Native Shell as distributable, verify on a Windows development machine:

1. Restore/build `NativeShell/FRBStudio.NativeShell.csproj`.
2. Start the EXE from an FRBStudio_App folder containing `wwwroot/`, `data/json/`, and `defs/`.
3. Confirm no localhost listener is started by Native Shell.
4. Confirm `https://frb-studio.local/index.html` renders.
5. Confirm Data/ViewDef open/save, Markdown open/save, Git Diff, and TestRunner flows.
6. Copy the built application to a clean company-equivalent PC and verify whether it starts without any user-side installation or administrator action.

The final distribution constraint is intentionally not fixed yet; the result of the real-PC verification is a distillation candidate in `studio_work_0158`.


## Persisted folder grant

`folderGrant.select` は任意の `persist_key` を受け取り、ユーザーが明示選択したフォルダーだけを `%LOCALAPPDATA%\FRBStudio\folder_grants.json` に保存できます。
`folderGrant.promptPath` はNativeShell側の入力ダイアログを表示し、Explorer等からコピーした絶対フォルダーパスをユーザーが貼り付けて「開く」を明示確定した場合だけFolder Grantを発行します。JSから任意の絶対パスを無確認でGrant化するコマンドは提供しません。
次回起動時は `folderGrant.restore` に同じ `persist_key` を渡すことで、任意パスをJSから指定せず、過去に承認済みのフォルダーGrantだけを復元します。
Markdown Studioは `markdown.workspace` を使用します。
