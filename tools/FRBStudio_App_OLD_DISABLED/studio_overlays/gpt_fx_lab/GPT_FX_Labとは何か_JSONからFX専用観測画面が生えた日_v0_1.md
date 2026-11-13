# GPT FX Labとは何か  
## JSONからFX専用観測画面が生えた日

作成日: 2026-07-05  
配置推奨: `studio_overlays/gpt_fx_lab/`  
対象バージョン: `gpt_fx_lab.fx_chart_viewer v0.7.7`  
位置づけ: Studioくん Overlay / FX M5チャート観測UI / Dow材料点観測フェーズ

---

## 1. この文章の目的

この文章は、`gpt_fx_lab` が何者なのかを、あとから見ても迷子にならないように残すための入口である。

`gpt_fx_lab` は、単なるFXチャート画面ではない。

Studioくんの大きな思想である、

```text
JSONを人間フレンドリーな存在にする
```

を、FX M5データという題材で実証している Overlay である。

---

## 2. 一言でいうと

```text
GPT FX Lab は、
JSONデータからFX専用の観測画面を生やす実験室である。
```

もう少し正確に言うと、

```text
Studioくん本体は汎用JSON研究基盤のままにして、
gpt_fx_lab Overlay 側に FX専用のViewDef / Plugin / Chart Viewer を持たせることで、
ドメイン専用UIを後付けできることを検証している。
```

---

## 3. なぜ作ったのか

最初の目的はシンプルだった。

```text
USDJPY M5 のJSONデータを、
Studioくん上で人間が見やすく観測したい。
```

しかし、作っていくうちに目的は少しずつ育った。

```text
JSONをグリッドで見る
↓
チャートで見る
↓
T3を重ねる
↓
Dow材料点を観測する
↓
Candidate / Basis / History を分ける
↓
Confirm bars を変えて比較する
↓
H/Lレンジ・BB・URL状態保存で観測条件を固定する
```

結果として、単なるチャート表示ではなく、

```text
判断材料を育てるUI
```

になってきた。

---

## 4. 重要な境界線

この画面は、現時点では売買判断ツールではない。

まだやらないこと:

```text
Dow trend 判定
Entry 判定
Exit 判定
利益シミュレーション
売買サイン表示
自動売買
```

現時点でやること:

```text
M5データを観測する
高値・安値の材料点を抽出する
Candidate / Active basis / Retired basis を分けて表示する
Confirm bars による粒度の違いを見る
H/LレンジやBBで価格構造を観測する
観測条件をURLで再現できるようにする
```

合言葉:

```text
ダウ理論を判定する前に、
ダウ理論の材料点を観測する。
```

---

## 5. Studioくん内での位置づけ

`gpt_fx_lab` は、Studioくん本体にFX専用ロジックを混ぜないための Overlay である。

```text
Studioくん本体
  = 汎用JSON研究基盤

studio_overlays/gpt_fx_lab
  = FX専用Overlay

fx_chart_viewer plugin
  = FX観測用の専用画面
```

この分離が重要である。

FX専用画面に見えても、Studioくん本体がFX専用アプリになったわけではない。

むしろ、

```text
汎用基盤の上に、ドメイン専用UIを後付けできる
```

ことを証明している。

---

## 6. 現在の主な機能

### 6.1 M5チャート表示

対象:

```text
USDJPY M5
最新1000件
```

表示系列:

```text
Close
MA20
T3(20, 0.2)
Bollinger Bands(20, shift 0, deviations 2.0)
High/Low range
```

---

### 6.2 Dow材料点表示

点は3層に分ける。

```text
Candidate
Active basis
Retired basis
```

意味:

```text
Candidate
  = 高値候補・安値候補

Active basis
  = 現在採用中のDow材料点

Retired basis
  = 以前は採用されていたが、後から置き換えられた履歴点
```

---

### 6.3 High / Low の価格ソース

高値系の点は `high` で判定する。  
安値系の点は `low` で判定する。  
白いチャート線は `close` である。

```text
High系 = high
Low系  = low
白線   = close
```

このため、点が白線より上や下にずれて見えるのは正しい。

---

### 6.4 色ルール

ユーザーの認知辞書に合わせる。

```text
High系 = 緑
Low系  = 赤
```

理由:

```text
緑 = アップ方向の材料
赤 = ダウン方向の材料
```

---

### 6.5 Confirm bars

`Confirm bars` は、材料点抽出の粒度である。

```text
小さい値 = 細かく拾う / ノイズも拾いやすい
大きい値 = 大きな構造を見る / 確定は遅くなる
```

現時点のプリセット:

```text
10
15
20
30
```

見立て:

```text
10 = Micro / デバッグ用
15 = Short swing / 実戦寄り候補
20 = Dow basis / 構造確認用
30 = さらに大きな構造確認用
```

---

### 6.6 表示モード

```text
Basisのみ
Basis+履歴
全部表示
```

使い分け:

```text
Basisのみ
  = 見やすい通常確認用

Basis+履歴
  = 判断履歴を確認する研究用

全部表示
  = Candidateまで含めたデバッグ用
```

---

### 6.7 H/Lレンジ表示

各足の `high-low` 範囲を縦線で表示する。

目的:

```text
点が high / low に置かれている根拠を見えるようにする
```

これは判定ロジックには影響しない。  
観測補助UIである。

---

### 6.8 Bollinger Bands表示

BBは、いつも見慣れている価格構造を確認するための表示系列である。

設定:

```text
Bands Period = 20
Bands Shift = 0
Bands Deviations = 2.0
Source = close
```

注意:

```text
BBは表示のみ。
Dow材料点抽出には使わない。
Entry判定にもまだ使わない。
```

---

### 6.9 URL起動

現在、URLから対象JSON・ViewDef・チャート状態を指定できる。

基本形:

```text
http://localhost:5055/myindex.html?data=overlay/gpt_fx_lab/data/fx_usdjpy_m5_t3_data_v0_1.json&view=overlay/gpt_fx_lab/view_defs/fx_usdjpy_t3_view_def_v0_1.json&action=fx_chart
```

状態指定例:

```text
&confirmBars=20
&viewMode=basis_history
&hlRange=1
&bb=1
&wide=1
```

---

### 6.10 URLコピー

現在表示している観測状態をURLとしてコピーできる。

コピーされる状態:

```text
action=fx_chart
confirmBars
viewMode
hlRange
bb
wide
```

目的:

```text
観測条件をブックマークできる
あとで同じ状態に戻れる
会話で状態を共有しやすい
```

---

### 6.11 右上固定 □ ボタン

`横幅拡大` は、実質的に画面最大化操作になった。

そのため、チャート右上に固定の `□` ボタンとして配置した。

```text
□  = 画面最大化
▢  = 元のサイズへ戻す
```

これは、機能名ではなく画面操作として認識しやすくするためである。

---

## 7. 現在の構成ファイル

主なファイル:

```text
studio_overlays/gpt_fx_lab/
  studio_manifest.json
  CHANGELOG.md
  doc/
    Dow材料点観測フェーズ仕様メモ_v0_7_2.md
  data/
    fx_usdjpy_m5_t3_data_v0_1.json
  view_defs/
    fx_usdjpy_t3_view_def_v0_1.json
  plugins/
    plugin_index.json
    fx_chart_viewer/
      plugin.json
      plugin.js
```

---

## 8. CHANGELOG運用

変更履歴は以下で管理する。

```text
studio_overlays/gpt_fx_lab/CHANGELOG.md
```

役割:

```text
何を変えたか
なぜ変えたか
どのガードを守ったか
次に戻れる道しるべ
```

---

## 9. 仕様メモとの関係

Dow材料点の詳しい仕様は、以下に分けている。

```text
studio_overlays/gpt_fx_lab/doc/Dow材料点観測フェーズ仕様メモ_v0_7_2.md
```

この文書は、

```text
gpt_fx_lab とは何か
なぜこのOverlayが存在するのか
現在の画面は何者なのか
```

を説明する入口である。

Dow材料点の細かい仕様は、doc側を参照する。

---

## 10. 先生ガード

画面がかなりFX専用画面として育ってきたため、先走りやすい。

ここで守ること:

```text
見た目が完成してきた
↓
売買ロジックも完成した気になる
```

この錯覚に注意する。

現在完成しつつあるのは、

```text
観測UI
```

である。

まだ完成していないもの:

```text
判断UI
売買UI
検証UI
```

この順番を守る。

---

## 11. 次フェーズ候補

### 11.1 README / doc整備

まず、現在の画面の意味を文章として固定する。

### 11.2 Basis Wave Line

Active basisをつないだ観測ライン。

ただし、ZigZagとは呼ばない。

```text
未来を見たZigZagではなく、
Confirm済みBasis点をつないだ観測ライン
```

### 11.3 Dow trend state

Basis点が十分に信頼できるようになってから、

```text
高値切り上げ
安値切り上げ
高値切り下げ
安値切り下げ
```

を見る。

### 11.4 Entry Candidate

さらに後のフェーズで、過去に手動シミュレーションしていた売買条件を自動検証する。

例:

```text
Dow trend = up
trend originから指定point以上進んだ
Close > T3
```

ただし、これはまだ先。

---

## 12. このOverlayの意味

`gpt_fx_lab` は、FXのためだけに存在しているように見える。

しかし、より大きな意味では、

```text
JSON
↓
ViewDef
↓
Plugin
↓
ドメイン専用観測UI
```

という流れを証明している。

これはStudioくんの思想そのものである。

```text
Data と View を分ける
View をデータ化する
必要なところだけ Plugin で専用UI化する
結果として、人間フレンドリーな研究画面が生える
```

---

## 13. 合言葉

```text
JSONを、人間フレンドリーに。
```

```text
正解を出すUIではなく、
違和感を見つけるUIを作る。
```

```text
売買する前に、観測する。
```

```text
ダウ理論を判定する前に、
ダウ理論の材料点を観測する。
```

---

## 14. Revision History

- v0.1: 初版。gpt_fx_lab の入口説明として作成。
