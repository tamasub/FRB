# 初期表示の画面状態JSONを検証する — 🚨 FAIL

## テスト結果サマリ
- 出力日時: 2026/6/20 8:04:03
- 判定: 🚨 FAIL
- Test ID: screen_state_smoke_001
- 取得日時: 2026-06-19T14:24:02.883Z
- URL: http://localhost:5055/
- 失敗件数: 1

### 差分サマリ
🚨 1件の差分を検出しました: appTitle
- 失敗チェッカー一覧:
```json
[
  "appTitle"
]
```

## 初回失敗
- Check: appTitle
- Expected: No-Code JSON Studio v0.3-draft eeee
- Actual: No-Code JSON Studio v0.3-draft

## チェッカー結果一覧
| 判定 | Check | Type | Target | Missing | Expected | Actual |
| --- | --- | --- | --- | --- | --- | --- |
| false | appTitle | equals | appTitle | [] | No-Code JSON Studio v0.3-draft eeee | No-Code JSON Studio v0.3-draft |
| true | headerText | equals | headerText | [] | true | true |
| true | requiredButtons | includesAll | buttons | [] | ["読み込み","保存","新規","削除"] | ["読み込み","保存","Markdown出力→Viewer","検索","取消","新規","削除","×","前へ(F7)","次へ(F8)","反映(F12)","閉じる"] |
| true | requiredInputs | includesAll | inputs.id | [] | ["defNameInput","dataNameInput","defFile","dataFile"] | ["defNameInput","dataNameInput","defFile","dataFile"] |

## 失敗チェック詳細

### 1. appTitle
- Type: equals
- Target: appTitle
- Message: appTitle failed: expected No-Code JSON Studio v0.3-draft eeee, actual No-Code JSON Studio v0.3-draft

#### Expected
No-Code JSON Studio v0.3-draft eeee

#### Actual
No-Code JSON Studio v0.3-draft