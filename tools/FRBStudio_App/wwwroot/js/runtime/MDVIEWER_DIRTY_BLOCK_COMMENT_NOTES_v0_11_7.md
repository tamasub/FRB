# mdViewer v0.11.7 — Markdown汚し方式FRBコメント

## 目的

Markdownプレビュー上の意味ブロックに対して、右クリックからコメントを追加できるようにする。
コメントはsidecar JSONには保存せず、Markdown本文をあえて汚す方式で残す。

## コメント形式

```markdown
<!-- FRB_COMMENT_START id="frbcmt_YYYYMMDD_HHMMSS_xxxx" status="TODO" -->
> 🛠 **FRBコメント：要修正**
>
> コメント本文
<!-- FRB_COMMENT_END -->
```

## 方針

- コメントは対象ブロックの直後に挿入する
- Markdown本文に残るため、そのままレビュー会話へ貼り付けられる
- Previewでは吹き出し風のコメントとして表示する
- HTML保存値は混入させない
- FRB_COMMENT_START / END により後から機械抽出しやすくする

## 右クリックメニュー

- ハイライト
- コメント追加
- OKコメント
- NGコメント
- 要修正コメント
- 要確認コメント
- コメント付きMarkdownをコピー

## 備考

これは保存コメント設計の完成形ではなく、コメントする文化を育てるための体験確認版である。
