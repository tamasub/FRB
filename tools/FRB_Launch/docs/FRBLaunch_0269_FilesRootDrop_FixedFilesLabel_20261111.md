# FRB Launch / studio_work_0269 — Files Exp ルート登録先・固定表示名の修正

基準ZIP：`launch_app_20261111_192711.zip`
修正範囲：Files ExpルートのAdd登録先と、画面表示の固定文字列。Update/Delete/Moveには着手しない。

## 変更内容

1. Files Exp列の**ルート余白**へ既存フォルダーをDropした場合、登録先のPage選択を廃止し、設定済みの `expanded_view_options.json` が示す **System / Filesカテゴリー**に登録する。
   - この構成では `page_id=system`, `parent_item_id=folders`。
   - これにより、Files Expが投影するルートフォルダーのデータ集合へ登録される。
   - 実ファイル/フォルダーは移動しない。ファイルとURLのルートDrop禁止も維持。
2. 同じルート余白の右クリックメニュー（カテゴリー作成・既存フォルダー登録）も、上記と**同じ登録先**を使用する。
3. `System / Files` カテゴリーが見つからない、またはカテゴリーでない場合、Page直下へフォールバックせず安全に拒否する。
4. Files画面の**緑フォルダー横のヘッダー文字は常に `Files`**。設定JSONの `folders.title` を編集しても、このヘッダーへ反映されない。データJSONの文字列そのものは変更しない。

## 責務と制約

- 変更はすべてStudio Change Core CLIの `dry_run → commit` を通す。LaunchからJSONを直接書き換えない。
- 設定JSON上の `System / Files` のタイトルはStudio Editorで引き続き変更可能。表示名とDataを分離。
- Files登録ルート自身のコンテキストメニュー、下層の実フォルダーのコンテキストメニューには手を加えない。
- 本修正は**ファイル・フォルダーのルート登録先とヘッダーラベル**に限定。カテゴリーフォルダーのFiles Exp内投影、詳細編集・削除・並べ替えは別途受入対象。

## 検証結果

- 新規ルート契約テスト + 既存Add / Expテスト：**23 passed**。
- Studio CLI結合テストで、一時設定JSONへ既存フォルダーAddを実行し `COMMITTED`。登録後のレコードで `page_id=system`, `parent_item_id=folders` を確認。
- 構文コンパイルOK。
- Windows実画面のQt Drop / 描画表示は、ユーザー環境での受入待ち。上記のテストは実機操作そのものを保証しない。

## Windows受入（最初の2項目）

1. Exp列のルート余白へExplorerから既存フォルダーをDrop。Page選択が**出ず**、Files Exp直下に新しいフォルダーが現れること。
2. Studioの設定JSON `folders.title` を変更してLaunchを再読み込みしても、緑フォルダー右側のヘッダーが `Files` のままであること。

※ 過去のAdd-onlyメモにある「Expルート余白はPageを選択する」は本修正で変更された。
