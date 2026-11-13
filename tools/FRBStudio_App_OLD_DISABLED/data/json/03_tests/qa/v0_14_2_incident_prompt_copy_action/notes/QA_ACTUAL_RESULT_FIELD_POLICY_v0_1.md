# QA Actual Result Field Policy v0.1

## 決定

Actual Result JSON のチェック判定フィールドは `pass` を正とする。

## 理由

Studioくんの既存強調表示は `checks[].pass` を基準にしている。
テスト結果JSON側を既存の差分表示文化に合わせることで、共通JSを増やさず、データ契約を揃える。

## 禁止

`passed` を新しい標準フィールドとして増やさない。
必要な場合も、まず既存の `pass` 契約へ寄せる。

## 役割

- Expected JSON: 期待値の正本
- Test Code: Expectedを読む実行仕掛け
- Actual JSON: 実行証跡。判定は `pass` に保存
- ViewDef: `pass` を表示し、既存強調表示に乗せる
