# 初期表示の画面状態JSONを検証する

## 基本情報
- 出力日時: 2026/6/20 7:42:08
- Test ID: screen_state_smoke_001
- 画面定義: screen_state_expected_view_def_v0_1.json
- チェック数: 4

## チェック定義一覧
| Check | Type | Target | Expected |
| --- | --- | --- | --- |
| appTitle | equals | appTitle | No-Code JSON Studio v0.3-draft eeee |
| headerText | equals | headerText | true |
| requiredButtons | includesAll | buttons | ["読み込み","保存","新規","削除"] |
| requiredInputs | includesAll | inputs.id | ["defNameInput","dataNameInput","defFile","dataFile"] |

## チェック詳細

### 1. appTitle
- Type: equals
- Target: appTitle

#### Expected
No-Code JSON Studio v0.3-draft eeee

### 2. headerText
- Type: equals
- Target: headerText

#### Expected
true

### 3. requiredButtons
- Type: includesAll
- Target: buttons

#### Expected
```json
[
  "読み込み",
  "保存",
  "新規",
  "削除"
]
```

### 4. requiredInputs
- Type: includesAll
- Target: inputs.id

#### Expected
```json
[
  "defNameInput",
  "dataNameInput",
  "defFile",
  "dataFile"
]
```