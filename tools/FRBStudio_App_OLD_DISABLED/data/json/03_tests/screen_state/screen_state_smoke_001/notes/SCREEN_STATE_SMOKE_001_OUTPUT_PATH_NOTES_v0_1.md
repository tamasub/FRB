# SCREEN_STATE_SMOKE_001 OUTPUT PATH NOTES v0.1

## 目的

Step 2として、`screen_state_smoke_001` の Actual / Diff 出力先を新階層へ統一する。

## 正本

テスト成果物の正本は以下。

```text
data/json/03_tests/screen_state/screen_state_smoke_001/
├─ expected/
├─ actual/
├─ diff/
├─ test_patterns/
├─ relations/
├─ summary/
└─ notes/
```

## 出力先の決定方法

`tests/screen_state/ncjs-screen-state-compare.checks.spec.ts` は、固定文字列ではなく、以下のテストパターンJSONを読む。

```text
data/json/03_tests/screen_state/screen_state_smoke_001/test_patterns/screen_state_test_patterns_data_v0_2_chat.json
```

そこに定義された以下を正とする。

```text
expectedFile
outputActualFile
outputDiffFile
```

## 意図

テストコードは出力先を勝手に決めない。
テストパターンJSONが、Expected / Actual / Diff の関係を持つ。

```text
TestPattern JSON = テスト成果物の入出力契約
Test Code        = 契約を読んで実行する仕掛け
```

## 旧配置

旧 `tests_screen_state/` は独立Playwrightプロジェクト実験時代の名残。
今後の正本は `tests/screen_state/` とする。
