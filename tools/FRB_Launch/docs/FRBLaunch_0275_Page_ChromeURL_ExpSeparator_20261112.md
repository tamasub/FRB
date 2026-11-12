# FRB Launch 0275 / 2026-11-12 — Page管理・Chrome URL登録・Exp区切り線

## 対象と境界

基準：`launch_app_20261112_144604.zip`。Launchのみ変更。保留中の「←で設定JSONフォルダーへ戻る」の仕様・実装には触れない。

### 1. Exp区切り線の上下余白

Expの仮想Page群とPC行の境目にある既存線を使う。PC行の高さを43pxとし、線をPC行の上端から8pxに描く。全行同一高さ設定を解除し、個別の高さが有効になるようにした。**モデル上にクリック可能な空行は増やしていない。**

### 2. Page追加・簡易編集・登録解除

- Files Expの「～ フォルダー Drop エリア ～」余白右クリック：`Pageを追加...` と従来の `既存フォルダーを登録...`。
- Page行の右クリック：既存のJSONメニューに `簡易編集...`（Page名・Pageアイコン）と `登録解除...` を追加。
- Pageの操作は `pages_view` / `pages` section の **Studio Change Core CLI** へ送る。`dry_run → Expected/Actual Diff → commit`。UUID IDはCoreで採番、登録順は既存sort_orderの最大+10。
- **空のPageのみ登録解除可能**。登録アイテムのあるPageを勝手に消すと孤児データが残るため安全拒否する。System Pageも解除不可。今後、配下アイテムを含めた一括解除を認めるかは別途仕様合意が必要。
- Launch設定JSONの直接書き換え、Windows実フォルダー削除はしない。

### 3. ChromeのアドレスバーからURLをドラッグ

- Files Expの設定JSON Page行・カテゴリーフォルダー、Files Listの設定JSON Page/カテゴリーフォルダーにドロップする。
- `http://` と `https://` のみ。URIリスト・ChromiumのWindows URL形式・テキストURLに加えてHTMLリンクを解釈する。
- 登録データは既存の `records_for_sources()` を通す。URLは `command`、globeアイコン、Openアクションのブックマーク型項目になる。Studio Change Core経由で追加する。
- Files Expの**空白ルートDropエリアへのURL直接登録は不可**。ここは引き続き「実フォルダーのみ」の場所。ブックマークは設定JSON Page/カテゴリーフォルダーにドロップする。

## 検証

- Page Add→Edit→Delete：Studio実CLI＋テスト用JSONでCOMMITTEDを確認。
- Chromeの text/plain / text/uri-list / UniformResourceLocatorW / text/html：型判定とOpenレコードを確認。
- Bookmarkカテゴリ―へのURL追加：Studio CLIでテスト用JSONに登録成功。
- 関連テスト：新規14件PASS。広めの選択範囲は93件PASS・4件FAIL、4件は基準ZIPでも再現。
- GUI/PySide6操作とChrome実ドラッグはこの環境では未実施。Windows実機受入が必要。

## Windows受入項目

1. ExpのPC直前の区切り線の上下に余白があり、PCのクリックやホイールを阻害しない。
2. Expの余白右クリックからPageを追加 → ExpのPage一覧とPageタブに表示される。
3. 作成したPageを右クリック → 簡易編集でアイコン・タイトル変更 → 登録解除。既存Page（配下あり）は保護メッセージ。
4. ChromeアドレスバーのURLをブックマーク用の設定JSONフォルダーへドラッグ → Openする新規URLアイテムが追加され、再起動後も残る。
5. リモコン表示・非表示で、既存のコンテキストメニューとぐりぐり操作が維持されている。
