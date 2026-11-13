# FRB Launch / studio_work_0269 — Explorer File Drop / Files Exp root order

## 対象と基準
- 実装基準: `launch_app_20261111_214342.zip` に、直前配布の `FRBLaunch_0269_IconDrop_SearchHint_Fix_20261111_diff.zip` を適用した状態。
- Studioくん: 既存の Change Core `Move` を使用。Studio側の変更なし。
- 変更対象: ExplorerからのファイルDrop、Files ExpのPC区切り線、Files Exp内の登録済みルートフォルダーの表示順入れ替え。

## 変更内容
### ExplorerからのファイルDrop
- Qt `mime.urls()` に加えて、Windows/OLEの `FileNameW` / `FileName`（`index=N`を含む）、生の `text/uri-list`、絶対ファイルパス文字列を解釈。
- `file:` URIを安全にローカルパスへ変換。`http(s)` URLの既存動作は維持。
- 値の存在確認、対象カテゴリーの許可、Studio CLIのdry_run→commitは引き続き既存経路で検証する。
- ファイル・フォルダー実体の移動、変更、削除はしない。Files Expルート余白への**ファイル**Dropは従来どおり禁止。

### Files ExpのPC区切り線
- PCルート行の上部に薄い水平区切り線を描画。
- 見た目だけの変更。PCの行・ナビゲーション構造を変えない。

### Files Expのルートフォルダーの並び替え
- 対象: `System / Files` (`page_id=system`, `parent_item_id=folders`、設定に応じて変更可) に直接登録された `item_kind=directory` の**登録済みルートショートカット**だけ。
- 登録済みルート同士の上半分／下半分で `before`/`after` の表示順変更。Expのルート余白へのDropで末尾に配置。
- 確認応答なし。Studio CLIの既存Moveで保存。Pathは変更しない。
- **禁止**: PC、Files配下の展開済み実フォルダー、実ファイル、未登録の物理パス、ルート以外のアイテムへのDrop、仮想Pageや別Pageへのルート移動。
- LIST内のJSONアイテムMoveとは区別。Dropデータに物理パスを含めず、JSON IDで指定。

## 検証
- 新規の純粋関数／MIMEテスト: URL形式、ファイル形式（単数・複数）、Windows FileNameW、URI、危険なテキストの拒否、ルートの許可・拒否、位置の前後/末尾。
- Studio CLI統合テスト: 一時コピーした設定JSONで登録済みルートのMoveとPath不変を確認。
- GUIのWindows/Qt実機受入は未実施（当実行環境はPySide6なし）。特にExplorerのファイルDropでは実際に渡されるMIME形式が環境によって異なるため再確認が必要。
- 幅広い既存テストの古い想定による失敗は、改修前ZIPでも同一失敗が起こることを確認した。今回の新規テストでは新規失敗なし。

## 受入チェック（Windows）
1. Explorerから `.txt` と `.xlsx` をLISTの設定JSONカテゴリーへDropでき、設定JSONに登録される。
2. ファイルをFiles Expのルート余白へDropしたときは拒否される（仕様）。同じ場所への実フォルダーDropは登録できる。
3. ExpのPC直前に区切り線が見える。
4. Expの登録済みルートフォルダーを、別の登録済みルートフォルダーへドラッグして順番変更できる。元のPathは変わらない。
5. Exp内のPC・PC配下のドライブやサブフォルダーにはMove不可。
6. 既存LISTカテゴリーへのファイル登録、JSONメニューMove、ブラウザURL Drop、実フォルダーナビゲーションを回帰確認。
