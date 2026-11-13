# incident_prompt_copy_action フォルダー構造整理メモ v0.1

## 目的

QA系テスト成果物を `data/json/03_tests/qa/{suite_id}/` 配下に集約し、
Expected / Actual / Diff / TestPattern / Relation の正本置き場を明確にする。

## 正本フォルダー

```text
data/json/03_tests/qa/v0_14_2_incident_prompt_copy_action/
├─ test_patterns/
├─ expected/
├─ actual/
├─ diff/
├─ relations/
├─ summary/
└─ notes/
```

## 方針

- `data/json/03_tests` は Studioくんで見るテスト成果物の置き場。
- `tests/qa/static` は実行するテストコードの置き場。
- Expected JSON は期待値の正本。
- Test Code は Expected JSON を読んで Actual Result JSON を出す仕掛け。

## 移行内容

旧配置:

```text
data/json/03_tests/v0_14_2_incident_prompt_copy_action/
```

新配置:

```text
data/json/03_tests/qa/v0_14_2_incident_prompt_copy_action/
```

`patterns/` は意味を明確にするため `test_patterns/` に統一した。
