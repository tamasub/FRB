# Studio共通Change Core 0269 — Step 8: Move

- 対象基準: `FRBStudio_App20261111_205913.zip`
- incident_file: `data/json/01_main/_studio_work_incident_data_v2.json`
- phase: `studio-external-changeset-core-v0_1`
- 状況: Node CLI / 自動試験実施済み。Windows画面受入未完了。

## 変更／理由

- 汎用ChangeSet操作に `move` を追加する。Launch固有のPage ID・親IDをハードコードせず、既存の `StudioTreeModel.place()` を使って、同階層順序変更・カテゴリーフォルダー移動・Page間移動を扱う。
- API契約：`targets:[{id, group_id}]` （1件）、 `placement:{group_id,parent_id,position:'end'|'before'|'after',anchor_id?}`。`move` 自体に物理ファイルパスは無い。
- `dry_run` のExpectedとActualを照合してからcommit。保存SHA競合と既存の安全保存を継承。

## 制約／保証

- Tree定義を持つSectionでのみ許可。無効な親・別Pageの不整合・循環参照・存在しない基準位置は拒否。
- `sort_order` と `parent_item_id`、Page移動時の子孫 `page_id` を整合させる。
- 変更対象外のデータを保持。Move UIの出自制限（物理ファイル非操作）はLaunch側の責務。
- Update/Delete/Addと組み合わせても1文書1ChangeSetの原子性を維持。

## 確認

- `node --test tests/change_core/{change_core,move_core,update_core,native_bridge_cas}.test.mjs`：37/37 PASS。
- CLI Moveのdry_run／commit／古いSHA拒否、同階層・Page間移動、循環参照・不正親拒否確認。
- Windows NativeShell/WebView2実機受入は未完了。
