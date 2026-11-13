# FRB Studio Change Core — Step 6 / Delete Cascade (studio_work_0269)

- 基準ソース：`FRBStudio_App20261111_194044.zip`
- 実装：`delete.targets[]` / `cascade:true` を共通ChangeSetに追加。Addは維持。
- 対象：承認済みViewDefのTree構造、指定IDと子孫のJSONレコードのみ。
- 既存保証：trusted config / SHA-256 / dry_run / commit / Expected→Actual Diff / lock / atomic replaceを維持。
- `group_id` と項目IDの整合性確認、親子整合性、不存在・重複・子持ち非cascadeを保存前に拒否。
- JSON配列の削除で添字が繰り上がるため、Expected/Actual Diffは移動した行の比較も含む。生存レコードの内容は変更しない。
- レスポンスに `summary.deleted` を追加。互換のため `summary.added` を維持。
- Field Definitionの入力値検査はAddレコードのみに実行（Deleteで詰められた既存レコードは新規入力ではない）。
- 動作確認：`node --test tests/change_core/change_core.test.mjs`：25/25 PASS。Launchの一時JSON経由のdry_run/commit/競合検出もテスト済み。
- 未確認：Windows NativeShell/WebView2の実画面受入、電源断耐性。
- 未対応：Update / Move、Pageそのものの削除、複数ファイル間原子性、文書全体の画面・CLI共通保証の完全化。
- 対応内容は差分ZIP。実際のユーザーデータは変更していない。
