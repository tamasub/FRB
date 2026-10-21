# 外部SQLite DBフォルダーの許可設定（2026-10-21）

## 何が変わる？

FRB Studioの管理外にある `.db` ファイルを、明示的に許可したフォルダー内に限って開けます。
従来の `sqlite_readonly_external_files`（ファイル単位の読取専用許可）も使えます。

## 設定例

`NativeShell/native_shell.config.json` の次の配列へ**実際のフォルダー**を追加します。設定例（パスはご自身の環境に置き換えてください）。

```json
"sqlite_readonly_external_directories": [
  "F:\\Work\\CopilotDB"
],
"sqlite_readwrite_external_directories": []
```

- **読取のみ**: `sqlite_readonly_external_directories` に指定し、DataJSONの `data_source.access_mode` を `"read_only"` にします。
- **編集も必要な場合のみ**: `sqlite_readwrite_external_directories` に指定し、DataJSONの `data_source.access_mode` を `"read_write"` にします。読取許可のみのフォルダーでは書込はできません。
- 絶対パスを指定。JSON内のWindowsパス区切り `\` は `\\` と書いてください。`%LOCALAPPDATA%` などの環境変数も使えます。
- サブフォルダー内のDBも許可されますが、類似名の別フォルダー（例 `F:\\Work\\CopilotDB2`）は許可されません。
- フォルダー経路のシンボリックリンク／ジャンクションは安全のため拒否します。
- DBファイルは既存の `.db` である必要があります。SQLiteのテーブルや列がDataJSONと一致する必要もあります。

### DataJSONの例（Studio管理内の `data/json/` に配置）

```json
{
  "data_source": {
    "type": "sqlite",
    "database_path": "F:\\Work\\CopilotDB\\test.db",
    "access_mode": "read_only",
    "tables": [
      { "table": "items", "data_path": "$.items", "load": { "on_open": true, "limit": 100 } }
    ]
  }
}
```

※上記は接続部分のみの例です。実際は既存DataJSONのViewDef参照や項目定義なども必要です。

## 設定ファイルの優先順位と反映方法

1. **EXEと同じ場所**の `native_shell.config.json` があればそちらを使用（通常 `NativeShell/_publish/native_shell.config.json`）。
2. なければ `NativeShell/native_shell.config.json` を使用。
3. 設定変更後は**Studioを再起動**。今回のC#修正を初めて適用する場合は、`cmd_compile_NativeShell.bat` でNativeShellを再ビルドしてください。
4. 読込失敗時は `%LOCALAPPDATA%\FRBStudio\logs\json_load_errors.log` を確認してください。許可の設定が間違っている場合は `WORKSPACE_PATH_DENIED` と設定キーが出ます。

**注意**: `writable_roots` はワークスペース内のJSON等向けの設定です。外部SQLite DBの許可には使いません。編集不要なら必ず読取専用許可を選択してください。
