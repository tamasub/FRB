# Responsibility Expected First Set Folder Layout Notes v0.18.9

## 目的

`responsibility_expected_tests_first_set_data_v0_1.json` は、責務単位 Expected テストの初回MVPデータとして作成された。

v0.18.9では、Test Evidence Rules v0.2 の `test_area / suite_id / artifact_kind` 方針に合わせ、責務 Expected 初期セットの正本配置を次の標準形へ寄せる。

```text
data/json/03_tests/responsibilities/responsibility_expected_first_set/
├─ test_patterns/
├─ expected/
├─ actual/
├─ diff/
├─ relations/
├─ summary/
└─ notes/
```

## 正本配置

現在の test_patterns 正本は次のファイルとする。

```text
data/json/03_tests/responsibilities/responsibility_expected_first_set/test_patterns/responsibility_expected_tests_first_set_data_v0_1.json
```

## 旧MVP配置の扱い

v0.18.8時点のMVPでは、次の直置きパスが使われていた。

```text
data/json/03_tests/responsibilities/responsibility_expected_tests_first_set_data_v0_1.json
```

v0.18.9以降、この直置きパスは新規追加しない。
Node runner は互換のため、旧パスが指定された場合に新標準パスへfallbackできる。

## まだやらないこと

- `qa` 配下の既存資材は移動しない。
- `screen_state` 配下の既存資材は移動しない。
- 過去Expectedの削除は行わない。
- Actual / Diff の本格保存は次段階以降とする。
- Visual Evidence / Playwright 証跡は対象外とする。

## 確認

```text
node tests/responsibilities/run_responsibility_expected_tests.mjs
```

引数なしで標準配置の test_patterns JSON を読み、既存6件がすべて PASS することを確認する。
