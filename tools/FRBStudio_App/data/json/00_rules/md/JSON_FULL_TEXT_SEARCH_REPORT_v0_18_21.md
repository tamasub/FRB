# JSON全階層全文検索 実装レポート v0.18.21

## 目的

Studio標準機能として、どのViewDefでも同じ位置に`🔍 全文検索`を表示し、JSON構造を知らなくても子Grid・詳細・非表示項目を含む文字列を探せるようにする。

## UI契約

- 検索エリア上段へ`🔍 全文検索`とテキストボックスを常時表示する。
- 実行は既存の`検索`ボタンを使う。専用ボタンは増やさない。
- `取消`は全文検索語と既存の列検索条件をまとめてクリアする。
- ViewDef側の設定は不要。

## 検索契約

- 各親Grid行が保持するobject / arrayを再帰走査する。
- 対象は文字列値だけ。
- 子Grid、詳細、Grid非表示Fieldの文字列も対象。
- 子階層で一致した場合は親Grid行を表示する。
- 大文字小文字を無視した部分一致。
- 既存の列検索条件とはAND条件。
- Plugin SearchFilterは従来どおりCore検索の後段でAND適用する。
- objectキー名、number、booleanはMVPの検索対象外。

## 責務境界

- `wwwroot/js/responsibilities/search_filter.js`: 再帰的な文字列収集、全文一致、列条件とのAND評価。
- `wwwroot/js/renderers/grid_detail.js`: UI値を読み、SearchFilterへ渡して再描画する。
- `wwwroot/js/runtime/search_state.js`: 全文検索語をCore検索状態へ保存・復元する。
- `wwwroot/index.html` / `wwwroot/styles.css`: 全ViewDef共通の固定UI。

## 今回見送ったもの

- 数値・boolean・キー名検索の切替。
- 正規表現、OR検索、複数語分割。
- 一致箇所のハイライトや詳細内ジャンプ。
- 行単位の永続検索インデックス。

初回は操作と意味を単純に保ち、大きなJSONで性能問題が観測された場合に検索インデックスを追加する。
