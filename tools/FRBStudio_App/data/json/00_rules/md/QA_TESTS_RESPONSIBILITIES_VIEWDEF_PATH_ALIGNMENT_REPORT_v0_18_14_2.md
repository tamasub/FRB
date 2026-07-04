# QA Tests Responsibilities ViewDef Path Alignment Report v0.18.14.2

## 目的

`data/json/03_tests/responsibilities/...` の責務Expectedテスト証跡に対して、ViewDef側だけ `defs/qa/responsibilities/` に分離していたため、Data JSON側の階層概念と一致しにくくなっていた。

また、一部Data/Runnerが旧パス `qa/responsibility/...` を参照しており、`responsibility_expected_diff_view_def_v0_1.json` 読込時に404が発生していた。

## 判断

`defs`側は数字フォルダーを使わない方針を維持する。
そのうえで、QAテスト証跡系ViewDefは `defs/qa/tests/` 配下へ寄せる。

```text
defs/qa/tests/responsibilities/
defs/qa/tests/responsibility_def/
```

## 変更

- 責務Expected証跡ViewDefを `defs/qa/tests/responsibilities/` へ配置
- 責務定義/ExpectedDefマスターViewDefを `defs/qa/tests/responsibility_def/` へ配置
- active Data JSON の `view_def` 参照を新パスへ更新
- responsibility runner の出力 `view_def` を新パスへ更新
- FieldGroupType Resolver static test の参照パスを新パスへ更新

## 旧パス扱い

次の旧フォルダーは互換コピーとして残す必要はない。
ただしZIP差分返却では削除操作を表現できないため、適用後に手動削除してよい。

```text
defs/qa/responsibilities/
defs/qa/responsibility_def/
```

## 確認観点

- `qa/tests/responsibilities/responsibility_expected_diff_view_def_v0_1.json` が読めること
- `qa/tests/responsibilities/responsibility_expected_actual_view_def_v0_1.json` が読めること
- `qa/tests/responsibilities/responsibility_expected_test_patterns_view_def_v0_1.json` が読めること
- FieldGroupType Resolver static test が新パスで通ること
