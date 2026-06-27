# AI仮説（差分ストーリー）

## 1. 変更内容の事実要約

今回の差分は、`WorkingTree` の Git Diff を対象に、7ファイル変更・追加576行・削除13行・未追跡5件を含む差分として生成されている。対象リポジトリは `F:/FRB`、ブランチは `main`、差分取得コマンドは `git diff --find-renames` のように見える。{{evidence:E001}}

主な変更は、Studioくんから `Export-DiffToJson.ps1` を実行するための CommandProfile 経路を追加するものに見える。バックエンド側では `Program.cs` に `/api/actions/command/profiles` と `/api/actions/command/run` が追加され、許可済みProfileだけを実行する構造、Mode/Range/ref/OutputPath照合/timeout/stdout・stderr返却などの実行制御が追加されている。{{evidence:E002}}

`.csproj` には `Export-DiffToJson.ps1` を出力ディレクトリへコピーする設定が追加され、`appsettings.json` 系には `GitDiffExport` CommandProfile設定が追加されている。出力先は `F:\FRB_Diff\DiffToJson.json` としてGit管理外へ寄せる意図があるように見える。{{evidence:E003,E004}}

フロント側では `action_registry.js` に `RunCommandProfile` Actionが追加され、選択行から `command_profile_id`、`mode`、`from_ref`、`to_ref`、`output_path_display` などを組み立てて `/api/actions/command/run` にPOSTする構成になっている。`index.html` はAction系JSのキャッシュバスターを更新している。{{evidence:E005,E006}}

インシデントJSONは `studio_work_0062` を未着手から完了・確認済みに更新し、作業依頼、実装結果、判断ログ、変更履歴、実更新ファイル一覧を追記している。{{evidence:E007}}

未追跡として、完了版インシデントJSON、Git Diff実行設定Data/ViewDefと思われるフォルダ、PS1配置と思われる `tools/`、実装メモMDが検出されている。{{evidence:E008}}

なお、Git出力には多数の `LF will be replaced by CRLF` 警告が含まれており、実変更とは別に改行コード警告が差分確認時のノイズになる可能性がある。{{evidence:E009}}

## 2. AI仮説（差分ストーリー）

この差分は、Studioくんを「JSONを見る・編集するツール」から、「許可済みの外部処理をJSONプリセットで起動し、その成果物をまたJSONとして読む管制塔」へ進めるための、最初の縦切り実装のように見える。{{evidence:E001,E002,E005}}

流れとしては、まずGit DiffをJSON化する `Export-DiffToJson.ps1` をStudioくんから起動したい、という要求があり、そのためにData JSON側には人間が選ぶ実行プリセットを持たせ、Program.cs側には実行してよいコマンドの正本であるCommandProfileを持たせる構成にした可能性がある。{{evidence:E002,E004,E005}}

特に `OutputPath` を `F:\FRB_Diff\DiffToJson.json` に寄せている点は、差分生成物をGit配下に置くと「差分が差分を生む」事故が起きるため、Git管理外に退避させたいという意図に見える。Data JSON側にも表示用の出力パスを持たせながら、実行時はProgram.cs側の正本と照合する形にしたことで、人間の確認しやすさと実行安全性を両立しようとしている可能性がある。{{evidence:E004,E005,E007}}

フロントエンドの `RunCommandProfile` は、Gridで選択した1行を「実行リクエスト」に変換する役割を担っているように見える。ここでは任意のコマンドラインを送るのではなく、`command_profile_id` と安全な引数だけを渡しているため、「便利なコマンド実行」ではなく「許可済みCommandProfileの実行」に寄せた設計意図があるように見える。{{evidence:E005}}

インシデントJSONの更新内容を見ると、この実装は単発機能ではなく、今後の「コマンド引数が面倒な作業をStudioくんのData JSONでプリセット化する」方向へ拡張できる足場として記録されているように見える。Git Diff Runは、その第一号として選ばれた可能性が高い。{{evidence:E007,E008}}

一方で、`.csproj` のコピー対象、`appsettings.json` の二重配置、未追跡の `tools/` 配置先、実更新ファイル一覧の粒度には、後続で人間が確認した方がよいズレ候補が残っているようにも見える。{{evidence:E003,E004,E007,E008}}

## 3. 差異想定理由

`Program.cs` の追加量が408行と大きく、API追加、Profile構築、パス解決、Git ref検証、PowerShell起動、timeout、結果JSON返却、DTO/record追加まで含んでいるため、単なる画面ボタン追加ではなく、バックエンドに「CommandProfile Runner」の骨格を入れた差分のように見える。{{evidence:E002}}

`action_registry.js` は81行追加されており、選択行から実行リクエストを作り、静的ホスティングでは実行不可にし、`/api/actions/command/run` にPOSTする処理が入っている。これは既存の `toolbar.executeButton` / ActionRegistry構造に、Git Diff Runを接続するためのフロント側Adapterとして追加されたように見える。{{evidence:E005,E006}}

`appsettings.json` に `CommandProfiles.GitDiffExport` が追加されているため、CommandProfileの値を完全にProgram.cs直書きにせず、設定ファイル側でも管理できるようにした可能性がある。ただし、同様の追加が `tools/FRBStudio/appsettings.json` と `tools/FRBStudio_App/appsettings.json` の両方に入っているため、どちらが実行時正本なのか、また両方必要なのかは確認余地がある。{{evidence:E004}}

`.csproj` にPS1コピー設定が追加されたのは、実行時に `Export-DiffToJson.ps1` が見つからない事故を防ぐための可能性がある。一方で、未追跡ファイル一覧では `tools/FRBStudio_App/tools/` が出ており、`.csproj` が期待する相対位置と実ファイル配置が一致しているかは確認した方がよさそうに見える。{{evidence:E003,E008}}

インシデントJSONでは、`studio_work_0062` が完了・確認済みに更新され、`actual_updated_files` も追加されている。これはv0.12以降の「AIが何を触ったかをインシデントへ残す」運用が、今回のGit Diff Run実装にも適用された可能性がある。{{evidence:E007}}

## 4. 違和感候補

1. `.csproj` のPS1コピー設定と、未追跡に出ている `tools/FRBStudio_App/tools/` の配置が噛み合っているかは確認した方がよい。`FRBStudio.csproj` から見た `tools\git\Export-DiffToJson.ps1` と、実際に同梱されたPS1の場所がズレている可能性がある。{{evidence:E003,E008}}

2. `appsettings.json` が `tools/FRBStudio` と `tools/FRBStudio_App` の両方で変更されている。実行時にどちらを読むのか、両方更新が必要なのか、片方だけでよいのかを人間が確認した方がよい。{{evidence:E004}}

3. `actual_updated_files` はテキストとして記録されているが、`appsettings.json` がどちらのパスか曖昧に見える可能性がある。今回すでに人間側で「appsettings.jsonもかな？」という確認が発生しているため、今後は `tools/FRBStudio/appsettings.json` と `tools/FRBStudio_App/appsettings.json` のようにフル相対パスで残す方が安全そうに見える。{{evidence:E004,E007}}

4. `Program.cs` の追加量が大きいため、`dotnet build` と実機での `Git Diff Run` 成否確認は必須に見える。この差分JSON上では実装内容は見えるが、ビルド・実行結果までは含まれていない。{{evidence:E002}}

5. `LF will be replaced by CRLF` 警告が非常に多く出ているため、今回の機能差分とは別に、改行コード警告がDiffJson ViewerやAI仮説生成時のノイズになる可能性がある。将来的には警告表示の分離、またはGit設定・`.gitattributes`確認が必要かもしれない。{{evidence:E009}}

6. `RunCommandProfile` は静的ホスティング時に拒否する設計になっているが、ボタン自体のdisabled表示や、ユーザーへの事前説明が十分かは画面確認した方がよい。実行時エラーだけでも成立するが、押す前に分かるUIの方が親切な可能性がある。{{evidence:E005}}

7. 未追跡フォルダとして `data/json/04_tools/`、`defs/tools/`、`tools/` が出ているが、DiffToJsonの `changed_files` には中身のpatchが含まれていない。新規追加ファイルの内容確認は、別途Git add前の一覧・実ファイル確認・ZIP内容確認で補う必要がある。{{evidence:E008}}

## 5. 埋め込みJSON

```diff_hypothesis.json
{
  "schema_version": "0.2.1-draft",
  "label": "AI仮説であり、レビュー結果ではない",
  "diff_story": "StudioくんにGit Diff Runを追加し、Data JSONのプリセット行からフロントAction、Program.csのCommandProfile API、Export-DiffToJson.ps1実行、Git管理外OutputPathへの出力までをつなぐ縦切り実装のように見える。任意コマンド実行ではなく、許可済みprofileと安全な引数だけを通す方向へ寄せている可能性がある。",
  "evidence_files": [
    {
      "file_path": "DiffToJson_20260627_202743.json",
      "file_category": ["diff_summary"],
      "items": [
        {
          "evidence_id": "E001",
          "category": ["summary", "working_tree"],
          "title": "WorkingTree差分の全体サマリ",
          "scope": "file",
          "context": [
            "repository.root = F:/FRB",
            "branch = main",
            "head = e9b14b1",
            "mode = WorkingTree",
            "command = git diff --find-renames"
          ],
          "deleted": [],
          "added": [
            "files_changed = 7",
            "total_added = 576",
            "total_deleted = 13",
            "untracked_files_count = 5"
          ],
          "keywords": ["WorkingTree", "summary", "git diff", "files_changed"]
        }
      ]
    },
    {
      "file_path": "tools/FRBStudio/Program.cs",
      "file_category": ["backend", "command_profile"],
      "items": [
        {
          "evidence_id": "E002",
          "category": ["backend_api", "command_runner", "security_guard"],
          "title": "CommandProfile APIとPowerShell実行制御の追加",
          "scope": "block",
          "context": [
            "Program.cs に 408行追加",
            "/api/actions/command/profiles と /api/actions/command/run を追加",
            "BuildCommandProfiles / RunCommandProfileAsync / CommandRunRequest / CommandProfile を追加"
          ],
          "deleted": [],
          "added": [
            "許可済みprofileだけを実行する構造",
            "Mode / Range / Git ref / OutputPath表示値照合",
            "ProcessStartInfo.ArgumentList による引数渡し",
            "timeout / stdout / stderr / exit_code / duration_ms を返却"
          ],
          "keywords": ["Program.cs", "CommandProfile", "RunCommandProfileAsync", "OutputPath", "timeout"]
        }
      ]
    },
    {
      "file_path": "tools/FRBStudio/FRBStudio.csproj",
      "file_category": ["backend", "packaging"],
      "items": [
        {
          "evidence_id": "E003",
          "category": ["script_packaging"],
          "title": "Export-DiffToJson.ps1の出力ディレクトリコピー設定",
          "scope": "block",
          "context": [
            "FRB_tray.ico のCopyToOutputDirectory設定付近に追加"
          ],
          "deleted": [],
          "added": [
            "<None Update=\"tools\\git\\Export-DiffToJson.ps1\">",
            "<CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>"
          ],
          "keywords": ["FRBStudio.csproj", "Export-DiffToJson.ps1", "CopyToOutputDirectory"]
        }
      ]
    },
    {
      "file_path": "tools/FRBStudio/appsettings.json / tools/FRBStudio_App/appsettings.json",
      "file_category": ["config", "command_profile"],
      "items": [
        {
          "evidence_id": "E004",
          "category": ["config_update", "output_path"],
          "title": "GitDiffExport CommandProfile設定の追加",
          "scope": "block",
          "context": [
            "FrbStudio.DataFolders の後ろに CommandProfiles を追加",
            "2つの appsettings.json に同様の差分"
          ],
          "deleted": [
            "DataFolders 配列終端のみで FrbStudio 設定が終了"
          ],
          "added": [
            "CommandProfiles.GitDiffExport.Id = git_diff_export",
            "DisplayName = Export-DiffToJson.ps1 / Git Diff JSON Export",
            "ScriptPath = tools/git/Export-DiffToJson.ps1",
            "OutputPath = F:\\\\FRB_Diff\\\\DiffToJson.json",
            "TimeoutSeconds = 30"
          ],
          "keywords": ["appsettings.json", "GitDiffExport", "OutputPath", "F:\\\\FRB_Diff\\\\DiffToJson.json"]
        }
      ]
    },
    {
      "file_path": "tools/FRBStudio_App/wwwroot/js/actions/action_registry.js",
      "file_category": ["frontend", "action_registry"],
      "items": [
        {
          "evidence_id": "E005",
          "category": ["frontend_action", "api_bridge"],
          "title": "RunCommandProfile Actionの追加",
          "scope": "block",
          "context": [
            "Noop Action の後ろに RunCommandProfile 関連関数を追加"
          ],
          "deleted": [],
          "added": [
            "commandProfileRowValue",
            "buildCommandProfileRunRequest",
            "postCommandProfileRun",
            "registerStudioAction('RunCommandProfile', ...)",
            "静的ホスティング時は実行不可",
            "選択行がない場合はエラー"
          ],
          "keywords": ["action_registry.js", "RunCommandProfile", "Git Diff Run", "api/actions/command/run"]
        }
      ]
    },
    {
      "file_path": "tools/FRBStudio_App/wwwroot/index.html",
      "file_category": ["frontend", "cache_buster"],
      "items": [
        {
          "evidence_id": "E006",
          "category": ["cache_buster"],
          "title": "Action系JSのキャッシュバスター更新",
          "scope": "line_change",
          "context": [
            "action_registry.js / action_toolbar.js のscriptタグ"
          ],
          "deleted": [
            "v=incident-prompt-copy-0142"
          ],
          "added": [
            "v=git-diff-command-profile-01437"
          ],
          "keywords": ["index.html", "cache", "action_registry.js", "action_toolbar.js"]
        }
      ]
    },
    {
      "file_path": "tools/FRBStudio_App/data/json/01_main/studio_work_incident_data_v0_62_git_diff_command_profile_added.json",
      "file_category": ["incident_data", "work_log"],
      "items": [
        {
          "evidence_id": "E007",
          "category": ["incident_update", "traceability"],
          "title": "studio_work_0062の完了化と作業履歴追記",
          "scope": "block",
          "context": [
            "studio_work_0062 v0.14.37-git-diff-export-command-profile"
          ],
          "deleted": [
            "status = 未着手",
            "verification_status = 未確認",
            "latest_ai_response = インシデント登録時の説明"
          ],
          "added": [
            "status = 完了",
            "verification_status = 確認済み",
            "latest_ai_response = v0.14.37対応完了報告",
            "discussion_history disc_0062_007 / disc_0062_008",
            "decision_log dec_0062_006 / dec_0062_007",
            "change_history chg_0062_002 / chg_0062_003",
            "actual_updated_files"
          ],
          "keywords": ["studio_work_0062", "incident", "actual_updated_files", "change_history"]
        }
      ]
    },
    {
      "file_path": "untracked files",
      "file_category": ["untracked", "new_files"],
      "items": [
        {
          "evidence_id": "E008",
          "category": ["new_artifacts", "needs_add_check"],
          "title": "未追跡の新規成果物群",
          "scope": "file",
          "context": [
            "diff_facts.untracked_files"
          ],
          "deleted": [],
          "added": [
            "tools/FRBStudio_App/data/json/01_main/studio_work_incident_data_v0_62_git_diff_command_profile_done.json",
            "tools/FRBStudio_App/data/json/04_tools/",
            "tools/FRBStudio_App/defs/tools/",
            "tools/FRBStudio_App/tools/",
            "tools/FRBStudio_App/wwwroot/js/runtime/GIT_DIFF_COMMAND_PROFILE_NOTES_v0_14_37.md"
          ],
          "keywords": ["untracked", "04_tools", "defs/tools", "tools", "GIT_DIFF_COMMAND_PROFILE_NOTES"]
        }
      ]
    },
    {
      "file_path": "git_warnings",
      "file_category": ["git_warning", "line_endings"],
      "items": [
        {
          "evidence_id": "E009",
          "category": ["line_ending_warning", "noise"],
          "title": "LF will be replaced by CRLF 警告",
          "scope": "file",
          "context": [
            "git_warnings に多数の改行コード警告が含まれる"
          ],
          "deleted": [],
          "added": [
            "FRBStudio.csproj / Program.cs / appsettings.json / action_registry.js 等で LF→CRLF 警告"
          ],
          "keywords": ["LF", "CRLF", "git_warnings", "line endings"]
        }
      ]
    }
  ]
}
```
