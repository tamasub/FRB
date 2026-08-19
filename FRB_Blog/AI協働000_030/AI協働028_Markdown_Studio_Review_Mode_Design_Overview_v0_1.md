# Markdown Studio 修正概要設計書 v0.1

作成日: 2026-08-16  
対象: FRB Studio / Markdown Studio  
位置づけ: 本チャットセッションで合意した Markdown Studio 改修方針の整理  
ステータス: Draft / 実装前設計整理

---

## 0. この設計の目的

Markdown Studio を、単なる Markdown Viewer / Editor ではなく、

**AIとのコミュニケーションをスムーズに行うための、Human → AI フィードバック入力UI**

として整理する。

今回の中心は、人間同士のレビュー管理ではない。

AIが生成・修正した Markdown に対して、人間が感じた

- 違和感
- NG
- 修正要求
- 確認事項
- 注目箇所

を構造化し、AIへ返しやすくすることを目的とする。

```text
AI
↓
Markdown
↓
人間が確認
↓
Review JSON
↓
AI
```

Markdown は **AI → 人間** のインターフェース、  
Review JSON は **人間 → AI** のインターフェースとして扱う。

---

# 1. 今回解決したい課題

## 1.1 コメント位置ずれ

現状は Markdown 本文にコメントを付けた後、本文へ行挿入・削除を行うと、コメント対象行がずれる。

```text
Markdown
↓
9行目へコメント
↓
途中へ3行挿入
↓
元の9行目が12行目へ移動
↓
コメント位置と本文が不整合
```

行番号は「位置」であって、レビュー対象そのものの恒久IDではない。

人へ提供するレビュー機能として扱うには、注意書きだけでは弱く、  
**ずれが発生する操作自体を構造的に禁止する必要がある。**

---

## 1.2 Editor と Review の責務混在

現在は本文編集とコメント追加を同じ画面状態で実行できる。

これを今後は、

```text
本文を編集する
```

と

```text
固定された本文をレビューする
```

に明確に分離する。

---

## 1.3 Sidecar という内部用語がUIへ露出している

現在の右クリックメニューには、

- Sidecarコメント
- Sidecar OK
- Sidecar NG
- Sidecar要修正
- Sidecar要確認
- Sidecar JSON保存

など、内部実装を前提とした用語が表示されている。

人間が見るUIでは内部構造を意識させず、**日本語中心の業務語彙へ寄せる。**

---

# 2. 中核原則

## 2.1 本文編集とレビューを同時に許可しない

Markdown Studio は次の3モードを持つ。

```text
Viewer
Editor
Review
```

### Viewer

- 入力: Markdown
- 本文: ReadOnly
- コメント追加: 不可
- ハイライト追加: 不可

### Editor

- 入力: Markdown
- 本文: 編集可能
- コメント追加: 不可
- ハイライト追加: 原則不可

### Review

- 入力: Review JSON
- 本文: Review JSON 内の固定 Markdown Snapshot
- 本文編集: 不可
- コメント追加: 可
- 判定追加: 可
- ハイライト追加: 可

---

## 2.2 Review ModeではMarkdownを凍結する

Review Mode開始時点の Markdown を Snapshot として Review JSON に保存する。

Review Mode 中の本文表示は、元 Markdown ファイルではなく、

```text
Review JSON.snapshot
```

を正とする。

これにより、元 Markdown が後から変更されても、レビュー対象は変化しない。

```text
AIが出力した対象
=
人間がレビューした対象
=
Review JSONが保持する対象
```

を一致させる。

---

# 3. Review Mode開始フロー

画面上部のモード切替を次の構成とする。

```text
[ Viewer ] [ Editor ] [ Review ]
```

初めて Review を押した場合、確認ダイアログを表示する。

表示文案:

> 現在のMarkdownをレビュー用の固定文章として保存します。  
> レビュー開始後、本文は編集できません。  
> コメントはこの固定文章に対して記録されます。  
> 続行しますか？

```text
[キャンセル] [レビュー開始]
```

レビュー開始時の処理:

```text
現在のMarkdown
↓
未保存変更があれば保存
↓
Markdown Snapshot取得
↓
Review JSON新規生成
↓
Markdown Studioの入力をReview JSONへ切替
↓
Review Mode開始
```

---

# 4. Review JSON の位置づけ

Review JSON は単なる「コメント保存ファイル」ではない。

```text
Review JSON
=
Markdown Snapshot
+
レビューコメント
+
判定情報
+
ハイライト
+
レビュー用メタ情報
```

として扱う。

Review JSON は **Markdown Studio の新しい入力形式** とする。

JSON形式であることを理由に、JSON Object Studio の主対象へ移すことを今回の設計目的とはしない。

Markdown Studio が Review JSON を入力として扱うことで、既存の

- コメント一覧
- コメントから本文位置へ移動
- 本文上の対象表示
- コメント編集
- コメント解決

などを自然に継続利用できる。

---

# 5. Review JSON 構造案

以下は概念構造であり、正式Schemaは実装時に確定する。

```json
{
  "review_version": "0.1",
  "source": {
    "path": "sample.md",
    "hash": "..."
  },
  "snapshot": {
    "markdown": "レビュー開始時点のMarkdown全文"
  },
  "comments": [
    {
      "id": "mdc_001",
      "target": {
        "line_start": 9,
        "line_end": 9,
        "text": "対象となった本文"
      },
      "type": "NG",
      "comment": "ここは期待と異なる",
      "status": "unresolved"
    }
  ],
  "highlights": [
    {
      "id": "mdh_001",
      "target": {
        "line_start": 12,
        "line_end": 12,
        "text": "注目している本文"
      }
    }
  ]
}
```

## 5.1 target.text を保持する理由

行番号だけではなく、レビュー開始時点の対象文字列も保持する。

```text
line_start / line_end
+
target.text
```

とすることで、

- 人間が何を見て判断したか
- AIがどの文章へのフィードバックか
- 将来の再接続候補

を説明しやすくする。

---

# 6. Review JSON の世代管理

今回の実装では複数世代管理を行わない。

基本は、

```text
1 Markdown
↔
1 規定名 Review JSON
```

とする。

Markdown に対応する規定名 Review JSON が存在する場合:

```text
Reviewボタン
↓
既存Review JSONを開く
```

規定名 Review JSON が存在しない場合:

```text
Reviewボタン
↓
レビューデータなし
↓
新規Review JSON生成
```

既存 Review JSON を人間が別名へ変更した場合は、  
規定名 Review JSON が存在しないため「レビューデータなし」と判定してよい。

複数世代・履歴管理は将来拡張とする。

### Review JSON ファイル名

正式命名は実装時に確定する。

例:

```text
document.md.review.json
```

現時点では、**規定名が一意に解決できること**を優先する。

---

# 7. ハイライト

ハイライトは Review JSON に保存する。

ただし、今回の中核目的であるAIレビューコメントとは役割を分ける。

### コメント・判定

主目的:

```text
人間 → AI
```

への構造化フィードバック。

### ハイライト

主目的:

```text
人間自身の注目箇所を保持する
```

Review JSON を再度開いた際に、以前注目していた箇所を復元できることを重視する。

---

# 8. 右クリックメニュー整理

## 8.1 UI用語方針

人間が見るメニューは日本語へ寄せる。

内部クラス名、JSONキー、実装上の構造名は英語のままでよい。

### 用語変更

```text
Block情報
↓
段落情報
```

`Sidecar` という語は人間向けUIから原則撤去する。

---

## 8.2 Editor Mode の右クリック

基本メニューを簡素化する。

```text
段落情報
────────────
行編集
上に行挿入
下に行挿入
段落削除
```

特殊ブロックに必要な操作がある場合のみ、そのブロック固有メニューを追加する。

本文編集に不要な Review 系メニューは表示しない。

---

## 8.3 Viewer Mode の右クリック

レビューコメント追加系のメニューは表示しない。

Viewer は「読む」責務に限定する。

---

## 8.4 Review Mode の右クリック

Review Mode のみレビュー操作を表示する。

候補:

```text
段落情報
────────────
コメント
OK
NG
要修正
要確認
ハイライト
```

最終的な文言・並び順は実装時に調整する。

---

# 9. 保存UI

## 9.1 右クリックのJSON保存を廃止

現在の

```text
Sidecar JSON保存
```

は削除する。

保存操作は右クリックメニューではなく、画面上部の共通保存UIへ統合する。

---

## 9.2 モードにより保存対象を切り替える

### Viewer / Editor

```text
保存対象: Markdown
```

トップの

```text
上書き
名前保存
```

は Markdown を対象とする。

### Review

```text
保存対象: Review JSON
```

トップの

```text
上書き
名前保存
```

は Review JSON を対象とする。

---

## 9.3 保存対象を視覚表示する

`上書き` の左側に、現在の保存対象を表示する。

例:

```text
[ 保存対象: Markdown ] [ 上書き ] [ 保存検査 ] [ 名前保存 ]
```

```text
[ 保存対象: Review JSON ] [ 上書き ] [ 保存検査 ] [ 名前保存 ]
```

「JSON保存モード」「Markdown保存モード」という表現は、Viewer / Editor / Review の「モード」と語彙が衝突するため避ける。

---

# 10. ファイルツリーとReview JSON

Phase 1では、Review JSONをファイルツリーから直接操作することを必須としない。

基本操作:

```text
ファイルツリー
↓
Markdownを選択
↓
Reviewボタン
↓
対応するReview JSONを内部的に解決
```

将来的には、

```text
Review JSONを表示する / 表示しない
```

の切替を追加してもよい。

ただし今回は、

- ファイル分類
- 表示フィルター
- Review JSON直接オープン
- Markdownとの関連付けUI
- Review世代管理

まで広げない。

---

# 11. 巨大Markdownファイル警告

巨大な Markdown を誤クリックした際、読み込みに時間がかかり、UIが固まったように見える問題へ対応する。

ファイル本文を読み込む前にファイルサイズを確認し、閾値以上の場合は確認ダイアログを出す。

```text
Markdownファイル選択
↓
ファイルサイズ確認
↓
閾値未満
  → 通常ロード

閾値以上
  → 確認ダイアログ
     「このファイルは大きいため、
       表示に時間がかかる可能性があります。
       開きますか？」
```

```text
[キャンセル] [開く]
```

## 11.1 設定配置

閾値は Native Shell の権限制約ではないため、

```text
native_shell.config.json
```

には置かない。

Studio の動作設定として、

```text
wwwroot/config/app_settings.json
```

へ置く。

構造案:

```json
{
  "markdown": {
    "large_file_warning_enabled": true,
    "large_file_warning_bytes": 524288
  }
}
```

`524288` bytes（512 KiB）は初期候補値。  
実利用を見て調整可能とする。

---

# 12. Markdown Studio レイアウト微調整

本チャットで出たレイアウト要求も継続する。

## 12.1 コードブロックの選択表示

Editor Modeで黒系コードブロックがカレントになった際、背景が白くフラッシュして文字が読めなくなる状態を廃止する。

要求:

```text
通常コードブロック
= ダーク背景

カレントコードブロック
= ダークグレー寄りの背景
```

カレント表現のために大幅な明色化・フラッシュを行わない。

---

## 12.2 右サイドバーの縦配分

右側を次の順序とする。

```text
INDEX / 目次
↓
コメントレビュー
↓
ドキュメントメタ
```

ドキュメントメタは最下部へ配置し、余白を減らす。

目次とコメントレビューへ、より多くの高さを配分する。

---

## 12.3 ウィンドウ横幅への追従

ウィンドウ全体を横へ広げた場合、Markdown Studio全体も横へ広がる。

ただし本文の可読幅はむやみに拡大しない。

```text
ウィンドウ横幅増加
↓
左ファイルツリー   → 広がる
中央本文           → おおむね既存幅を維持
右レビュー領域     → 広がる
```

主目的は、ファイルツリーの文字切れを減らすこと。

---

# 13. 今回やらないこと

今回のMarkdown Studio改修では、以下を対象外とする。

- 人間同士のレビュー依頼・承認ワークフロー
- 複数レビュアー管理
- メンション
- コメント返信スレッド
- 既読管理
- 担当者割当
- Review JSONの複数世代管理
- Review JSONの高度な自動再接続
- ファイルツリーの高度なReview JSON分類UI
- 設定専用UIの設計・実装

特に設定UIは次フェーズで別途設計する。

---

# 14. 設計の中心メッセージ

今回の改修は、コメントの行ずれを回避するためだけの対症療法ではない。

```text
Editor
= Markdownそのものを変更する場所

Review
= 固定されたMarkdownに対して、
  人間の判断を構造化する場所
```

へ責務を分離する。

そして最終的には、

```text
AI
↓
Markdown
↓
Human Review
↓
Review JSON
↓
AI
```

という循環を成立させる。

> **Markdown Studio の Review Mode は、人間同士のレビュー管理機能ではない。  
> 人間がMarkdownを読んで感じた違和感・判断・修正要求を、AIへ構造化して返すためのHuman → AIインターフェースである。**

---

# 15. 実装フェーズ案

## Phase 1 — Review Mode基礎

- Viewer / Editor / Review の3モード化
- Review開始確認
- Markdown Snapshot生成
- Review JSON新規作成 / 既存読込
- Review Mode本文ReadOnly化
- コメント・判定をReview Mode限定へ変更
- Sidecar表記撤去
- `Block情報` → `段落情報`

## Phase 2 — 保存契約整理

- Review JSONへハイライト保存
- 上部保存ボタンの保存対象切替
- 保存対象ラベル追加
- 右クリックのJSON保存撤去

## Phase 3 — 安全性・UI微調整

- 巨大Markdown警告
- コードブロック白フラッシュ抑止
- 右サイドバー高さ最適化
- 横幅追従改善

---

## Revision History

- 2026-08-16: v0.1 初版。本チャットセッションのMarkdown Studio改修方針を整理。
