# v0.13.1-md-sentence-insert-delete

## 目的

Markdown Block Model Foundationで得た `block_id / start_line / end_line / type` を使い、Preview上のSentenceBlockを起点に、前後への挿入・削除・Markdown再生成を行う。

## 実装概要

- EditorモードのPreview上でBlockへマウスを乗せると、点線枠付近に小さな操作バーを表示する。
- 操作バーから `＋上` / `＋下` / `削除` を実行できる。
- 右クリックメニューにも `上にSentence挿入` / `下にSentence挿入` / `SentenceBlock削除` を追加した。
- 挿入・削除はDOMを書き換えるのではなく、Markdown原文を行単位で更新し、その後 `renderMarkdown()` で再描画する。
- 挿入・削除の直前Markdown原文を `lastMutationBackup` に保持し、`↩ 直前操作を戻す` で復帰できるようにした。
- 保存値はMarkdown原文のままで、HTMLやBlock Model情報は本文へ混入させない。

## MVP制約

- この段階ではSentenceBlock = Markdown Blockとして扱う。
- 表セル編集、表の行挿入、sidecar comment JSONは未実装。
- list_itemの前後挿入では、既存の箇条書きマーカーを引き継ぐ。
- paragraph / heading / table / code_blockでは、前後に空行を補ってMarkdownを読みやすく保つ。

## 確認観点

- EditorモードでBlockにマウスを乗せると `＋上 / ＋下 / 削除` が表示される。
- `＋上` で対象Blockの前へMarkdown文が挿入される。
- `＋下` で対象Blockの後へMarkdown文が挿入される。
- `削除` で対象Blockの行範囲だけが削除される。
- `↩` または右クリックメニューの `直前操作を戻す` で、直前の挿入・削除前のMarkdown原文へ戻せる。
- 挿入・削除後にPreviewへ再描画され、Block Modelの行番号とBlock IDが更新される。
- readonly起動時は本文変更系ボタンが無効化される。

## 判断ログ

SentenceBlock操作は、Markdown本文への直接DOM編集ではなく、Block情報から原文行範囲を特定し、Markdown原文を更新して再描画する方式とした。これにより、次工程のTableCell編集やsidecar comment JSONに進む前でも、Markdown本文の保存安全性を保ちやすくする。

---

## v0.13.1.1 md-block inline action sticky fix

### 背景

v0.13.1 初回確認で、カレントSentenceBlockから `＋上 / ＋下 / 削除 / ↩` のインライン操作バーへマウスを移動すると、途中で別Blockへhover判定が移り、操作バーが逃げることがあった。
また、Block種別/IDバッジが操作バーの下に重なり、何か表示されているが読めない状態になっていた。

### 対応

- インライン操作バー上の `mouseenter / mouseleave` を管理し、バーへ移動中はカレントBlockを維持する。
- カレントBlockと操作バーを結ぶ安全領域（corridor）を設け、その範囲内ではhover対象を切り替えない。
- 操作バー表示中はBlock IDバッジを非表示にし、バー下で半端に隠れる表示を避ける。
- 操作バーの z-index を上げ、右クリックメニューとの重なり順を整理した。

### 確認観点

- カレント行から操作バーへマウスを移動してもバーが逃げないこと。
- `＋下` `削除` `↩` が安定して押せること。
- 操作バーの下にBlock IDバッジが半端に重なって見えないこと。
- Preview内で大きく別Blockへマウス移動した場合は、従来どおり対象Blockが切り替わること。
