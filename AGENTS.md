# AGENTS.md

このファイルは、このリポジトリで作業する Codex (Codex.ai/code) 向けのガイダンスを提供する。

## このリポジトリについて

FRB (Fishing Rod Benchmark) は、釣り竿の振動（「感度」）を共有可能・計測可能なデータに変換する個人研究プロジェクト
である。概念自体については `README.md` と `docs/FRB_*.md` を参照。このリポジトリは、その研究・執筆内容（ブログ下書き、
仕様書、実験ログ — 大部分は日本語）と、それを支える実ソフトウェアが混在するモノレポである。

- `firmware/FRB/FRB.ino` — ESP32センサーファームウェア（Arduino、加速度センサー + FFT）。
- `tools/FRBStudio_App/` — **現在アクティブなコードベース**。JSON汎用研究/ビューアー基盤を提供しつつ、その上にFX市場
  シミュレーションラボを載せたローカルWindowsトレイアプリ（「Studioくん」）。現在の開発のほぼすべてがここで行われる。
- `tools/FRBStudio/` — 同じStudioアプリの以前/並行ビルド（発行済み `bin/` 出力が `tools/FRBStudio/bin/` 配下に
  コミットされている）。ソース変更を行うなら `tools/FRBStudio_App/` を優先すること。
- `tools/frb_metaDiff/`、`tools/frb_No-Code_JSON_Studio/`、`tools/frb_purupuru_designer/`、
  `tools/frb_sensor_check_mobile/`、`tools/Utf8Readable/` — それぞれ独立フォルダに完結する、単発のHTML/JSまたは
  PowerShell製の小さなユーティリティ群。

特に指定がなければ、「アプリ」や「Studio」に関するタスクは `tools/FRBStudio_App/` を指すものとみなす。

## 重要: このリポジトリのソースコードの大半はgit管理外

ルートの `.gitignore` はリポジトリ全体で `*.cs` と `*.js` を除外している（「source code - private for now」）。
つまり：

- `Program.cs`（ASP.NET Core/WinFormsバックエンド）や、すべてのプラグイン `.js` ファイル（例:
  `studio_overlays/gpt_fx_lab/plugins/fx_chart_viewer/plugin.js`）は **gitで追跡されておらず**、編集しても
  `git status`/`git diff` には一切現れない。
- 追跡対象になっているのは: `.json`（マニフェスト、view-def、データ、シミュレーションプロファイル）、`.md`（ドキュメント、
  changelog）、テストファイル（`.test.cjs`、`.spec.ts`、`.mjs`）、`.csproj`、設定ファイル、PowerShellスクリプトなど。
- `.cs`/`.js` ファイルに触れた変更については、`git diff`/`git status` が全体像を反映していると思い込まないこと —
  ファイルを直接確認する。ユーザーから明示的に指示がない限り、gitignore対象ファイルを force-add して「直そう」と
  しないこと。

## tools/FRBStudio_App — アーキテクチャ

`Program.cs/Program.cs` はWinFormsトレイアプリ（`net9.0-windows`、`UseWindowsForms=true`）であり、同時に
`http://localhost:5055` にバインドされたASP.NET Core minimal-API Webホストを起動し、そのURLを既定ブラウザで開く。
トレイアイコンが起動中のWebホストを制御し、アプリを閉じるとホストも停止する。

**CoreとOverlayの分離**が中心的な設計思想である（
`studio_overlays/gpt_fx_lab/GPT_FX_Labとは何か_JSONからFX専用観測画面が生えた日_v0_1.md` の§5を参照）:

- **Core** = 汎用JSON研究基盤: `wwwroot/`（フロントエンド）、`defs/`（view定義）、`data/json/`（汎用JSONデータ）を、
  `/api/data`、`/api/defs`、`/api/markdown` 経由で提供する。
- **Overlay** = `studio_overlays/{overlayId}/` 配下に置かれる、ドメイン専用の後付けアドオンで、Coreとは決して混在
  させない。各Overlayは、CoreとOverlay間の共通契約となる独自の `studio_manifest.json`、plugins、view_defs、data
  を持ち、`/api/overlays/{overlayId}/...` 経由で提供される。
- 現時点で唯一かつ主力のOverlayが `studio_overlays/gpt_fx_lab/` である。FX（USDJPY M5）のチャート観測とダウ理論
  ベースの売買シミュレーションラボで、以下を含む:
  - `plugins/fx_chart_viewer/` — チャートビューアープラグイン（`plugin.js` は未追跡、`plugin.json` は追跡対象の
    マニフェストで、テストがアサートする `version` フィールドを持つ）。
  - `simulation/` — シミュレーション実行プロファイルのJSON（`fx_simulation_run_profile*_v0_1.json`）と、理由/
    ルールカタログ（`fx_simulation_reason_rule_catalog_v0_1.json`）。これらがバックテストエンジンの独立した並列
    「Rule Lane」ポートフォリオ3種 — `NORMAL`、`EXPANSION`、`EXPANSION_LITE` — を駆動する（各レーンのエントリー/
    エグジット条件の変遷 — ダウブレイクアウト確定、HSIアンカー起点、T3/Rレベルターゲット、H1/H4サイクルゲート — は
    `CHANGELOG.md` を参照）。
  - `sidecars/` — データセットごとのシミュレーショントレースとチャートコメント。ファイル名のプレフィックスで
    データファイルと対応付けられる（例: `fx_usdjpy_m5_t3_data_v0_1.*`）。
  - `data/`、`view_defs/`、`doc/`、`search_patterns/`、`value_sets/` — Overlayスコープのデータ、view定義、日本語の
    仕様メモ、補助設定。
  - `CHANGELOG.md` — プラグインの挙動変更に関する正本の履歴。過去のバグ/修正の詳細な経緯が記されているため、
    シミュレーションやチャートビューアーのロジックを変更する前に必ず確認すること。
- コマンド実行用のサーバールート（`/api/actions/command/*`）は、`Program.cs` で定義されたホワイトリスト済み
  PowerShell「CommandProfile」（git diffエクスポート、テストランナー）だけを実行する — 任意のコマンドは意図的に
  受け付けない。

## アプリの実行

リポジトリ内には `dotnet run` の簡易手順は明記されていない。アプリはVisual Studio / `dotnet publish` でビルド・
発行され、生成された `FRBStudio.exe`（または `tools/FRBStudio_App/Program.cs/` からの `dotnet run`）がトレイアプリ
を起動し、`http://localhost:5055/` でUIを提供する。Screen-state系のPlaywrightテストは、実行前にアプリが既にこの
URLで起動していることを前提にしている。

## テスト (tools/FRBStudio_App)

コマンドはすべて `tools/FRBStudio_App/` から実行する（`cd tools/FRBStudio_App`）。「全部まとめて実行」する単一
コマンドは存在せず、テストは対象ツールごとに個別実行する:

- **Playwright screen-stateテスト**（事前に `localhost:5055` でStudioアプリが起動している必要あり）:
  ```powershell
  npx playwright test tests/screen_state/ncjs-screen-state-compare.checks.spec.ts
  ```
  設定は `playwright.config.ts`（`testDir: tests/screen_state`、出力先は `tests/.runtime/playwright-output`）。
  `playwright-report/`、`test-results/`、リポジトリ直下への出力は絶対に発生させないこと — それらは
  `tests/setup.md` に記載の古い名残の慣習。

- **Node標準テストランナー**（`node --test`）による静的QAチェック:
  ```powershell
  node --test tests/qa/static/incident_prompt_copy_action_viewdef_static.test.mjs
  node --test tests/qa/static/field_group_type_resolver_static.test.mjs
  ```

- **Responsibility契約テスト**（`node --test` ではなく素のNodeスクリプト）:
  ```powershell
  node tests/responsibilities/responsibility_expected_tests.mjs
  node tests/responsibilities/responsibility_refactor_first_step_smoke.mjs
  ```

- **gpt_fx_lab Overlayテスト** — 挙動1件につき1ファイルの、その場限りのNodeアサーションスクリプト
  （`assert/strict` 使用）。`node` で直接実行し、任意でFRBStudio_Appのルートパスを唯一の引数として渡せる
  （省略時は `process.cwd()`）:
  ```powershell
  node studio_overlays/gpt_fx_lab/tests/crosshair_lock_v0_1.test.cjs
  node studio_overlays/gpt_fx_lab/tests/expansion_lite_rule_lane_v0_18.test.cjs
  ```
  これらは `plugin.json` マニフェストのフィールド（例: `version`）と、（未追跡の）`plugin.js` 内のリテラルな
  ソース断片の両方に対してアサートしている — プラグインのバージョンを上げたり関数名を変更したりする際は、これらの
  文字列/正規表現アサーションの更新が必要かどうか必ず確認すること。

- **`tools/test/TestRunner.ps1`** — Studioアプリ自身のUIから呼び出される、薄いホワイトリスト式ラッパー。
  受け付ける `-TestRunnerId` は4種類のみ（`playwright_ui`、`incident_prompt_copy_action_static`、
  `responsibility_expected_tests`、`responsibility_refactor_first_step_smoke`）で、それ以外は拒否する。
  `gpt_fx_lab/tests/*.test.cjs` は実行しない。アプリ内テストランナーの配線自体がタスクの主題である場合を除き、
  新しいIDを追加するより上記の `npx`/`node` コマンドを直接呼び出すことを優先する。

## ファームウェア (firmware/FRB)

ESP32向けArduinoスケッチで、`arduino-cli` でビルド/書き込みを行う（正確な実行内容は `.vscode/tasks.json` の
「FRB: Compile」「FRB: Upload」「FRB: Upload SPIFFS」タスクを参照。fqbnは `esp32:esp32:esp32`）。
`tools/upload-spiffs.ps1` と `tools/watch-data-and-upload.ps1` が、スケッチ本体とは別にSPIFFSデータのアップロード
を扱う。

## 知っておくべき慣習

- バージョン付きファイル名（`_v0_1`、`_v0_18` など）が随所にある — 番号が最も大きいものを最新として扱うこと。
  番号の小さい同系ファイルは通常、置き換え済みで削除されずに履歴/参照用として残されている。
- このリポジトリ全体を通じて、設計ドキュメント・changelog・コミットに紐づくメモの主要言語は日本語である。編集時に
  翻訳しないこと — ファイルごとの既存言語に合わせる。
- `studio_overlays/gpt_fx_lab/` は、**観測**（チャート/材料点表示、実装済み）と**判断/売買**（ダウトレンド状態、
  エントリー/エグジットの自動化 — 段階的に少しずつ実装中）を明確に区別している。このOverlayを拡張する際は、
  明示的にスコープされていない売買判断ロジックを追加する前に、CHANGELOGとOverlay入門ドキュメントの「先生ガード」
  節を必ず確認すること。
