# screen_state_smoke_001 folder structure migration v0.1

## 目的

`screen_state_smoke_001` に関係するテストデータを、Studioくんで管理しやすいように `data/json/03_tests` 配下へ集約する。

## 新しい正本フォルダー

```text
data/json/03_tests/screen_state/screen_state_smoke_001/
├─ test_patterns/
├─ expected/
├─ actual/
├─ diff/
├─ relations/
├─ summary/
└─ notes/
```

## 配置方針

- `test_patterns/` : テストパターン台帳
- `expected/` : 期待値JSON。テストの正本。
- `actual/` : 実行時の画面状態JSONなどのActual。
- `diff/` : Expected と Actual の比較結果。
- `relations/` : 制約・Expected・テストとの対応関係。
- `summary/` : 将来の集計・履歴サマリ用。
- `notes/` : 移行メモ、依頼プロンプト、判断ログ。

## 今回の注意

同名Expectedが `data/json/03_screen_state` と `test_patterns` に存在していたため、Studio管理側の `data/json/03_screen_state/screen_state_smoke_001.expected.json` を値の正本として採用し、`test_patterns` 側にあった `check_id` を補完した。

## 次の候補

- screen_stateのActual/DiffとQA Actual Resultの共通サマリ形式を整理する。
- `data/json/03_screen_state` は旧配置として廃止候補。
- `test_patterns` は旧配置として廃止候補。テストデータは `data/json/03_tests` に寄せる。
