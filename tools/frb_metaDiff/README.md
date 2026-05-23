# MetaDiff v0.2.2-draft

## 目的

MetaDiff Hypothesis Viewer は、AI仮説Markdownと、その根拠になる `- / +` 差分カードを同じ画面で確認するためのViewerです。

AIにレビューを代行させるものではありません。

- 左: AI仮説Markdown
- 右: カテゴリ付き根拠差分カード
- 左の `{{evidence:E001,E002}}` をクリックすると、右が該当カードに絞り込まれます。



## ファイル

- `MetaDiff_HypothesisViewer.html`
- `MetaDiff_Prompt_v0_2_1.md`
- `sample_ai_hypothesis_v0_2_1.md`

## 根拠ボタンの書き方

AI仮説Markdown内に以下を書きます。

```text
{{evidence:E001}}
{{evidence:E001,E002,E004}}
```

Viewerでは、このマーカーが根拠ボタンになります。

## 埋め込みJSON

Markdown末尾に以下のような `diff_hypothesis.json` を入れます。

```json
{
  "schema_version": "0.2.1-draft",
  "label": "AI仮説であり、レビュー結果ではない",
  "diff_story": "",
  "evidence_files": [
    {
      "file_path": "",
      "file_category": [],
      "items": [
        {
          "evidence_id": "E001",
          "category": [],
          "title": "",
          "scope": "",
          "context": [],
          "deleted": [],
          "added": [],
          "keywords": []
        }
      ]
    }
  ]
}
```

## 設計思想

- Markdown本文 = 人間が読むAI仮説・差異想定理由
- 埋め込みJSON = Viewerが読む根拠差分カード
- 右端 = AI仮説を疑うための証拠棚
- 左の根拠ボタン = 仮説文と証拠棚をつなぐ橋


## v0.2.2 修正点

- ツールバー右側にAI仮説Markdown専用のDropエリアを追加
- ファイル選択ボタンだけでなく、Dropエリアへのドラッグ＆ドロップでもMarkdownを読み込めるようにした
- Drop中は枠線と背景色が変わる



----

# DiffJson Viewer v0.1-draft

`DiffToJson.json` を読むためのローカルViewerです。

MetaDiff Hypothesis Viewer が「AI仮説と根拠差分カードを見る画面」なのに対して、こちらは **差分事実そのものを検索・閲覧する画面** です。

## 目的

- DiffToJson.jsonを読み込む
- 複数ファイルの差分を一覧する
- ファイル一覧から1ファイルを選択する
- 選択ファイルだけの差分hunkを表示する
- 全ファイル横断で差分本文を検索する
- DropエリアへJSONを落として読み込む

## ファイル

- `DiffJsonViewer.html`

## 使い方

1. `DiffJsonViewer.html` をブラウザで開く
2. `DiffToJson.json` を選択、または上部Dropエリアへドラッグ＆ドロップ
3. 左のファイル一覧からファイルを選ぶ
4. 右側で選択ファイルの差分を見る
5. 右上検索欄で差分本文・ファイル名を検索する

## 主な機能

### 左ペイン

- 差分サマリー
- Git警告の表示
- ブランチ / head / mode / command 表示
- ファイル名検索
- ステータスフィルタ
  - M: Modified
  - A: Added
  - D: Deleted
  - R: Renamed
  - U: Untracked

### 右ペイン

- 選択ファイルの差分hunk表示
- 全ファイル一覧表示
- 検索一致だけ表示
- 追加行だけ / 削除行だけ / 追加削除だけ の表示切り替え
- Raw JSON確認

## 補足

未追跡ファイルについては、現在のDiffToJson.jsonに内容差分が含まれていない場合、ファイル名のみ表示します。

## 今後の候補

- hunk単位のコピー
- 検索結果のエクスポート
- パッチがmax_patch_charsで切られた場合の明示表示
- ファイル数が多い場合の仮想スクロール
- hunk単位のAIカテゴリ付与との連携




