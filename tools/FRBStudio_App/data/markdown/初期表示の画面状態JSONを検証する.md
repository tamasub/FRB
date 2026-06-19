# 初期表示の画面状態JSONを検証する

- 出力日時: 2026/6/20 0:42:46
- status: fail
- 件数: 4

## 基本情報
- 判定: 🚨 FAIL
- 差分サマリ: 🚨 1件の差分を検出しました: appTitle
- 失敗件数: 1
- 初回失敗 Check: appTitle
- 初回失敗 Expected: No-Code JSON Studio v0.3-draft eeee
- 初回失敗 Actual: No-Code JSON Studio v0.3-draft
- Test ID: screen_state_smoke_001
- テスト名: 初期表示の画面状態JSONを検証する
- 取得日時: 2026-06-19T14:24:02.883Z
- URL: http://localhost:5055/
- Status(raw): fail
- 画面タイトル: No-Code JSON Studio v0.3-draft
- ヘッダー検出: true

---

## チェッカー一覧
| 判定 | Check | Type | Target | Missing | Expected | Actual |
| --- | --- | --- | --- | --- | --- | --- |
| false | appTitle | equals | appTitle | [] | No-Code JSON Studio v0.3-draft eeee | No-Code JSON Studio v0.3-draft |
| true | headerText | equals | headerText | [] | true | true |
| true | requiredButtons | includesAll | buttons | [] | ["読み込み","保存","新規","削除"] | ["読み込み","保存","Markdown出力→Viewer","検索","取消","新規","削除","×","前へ(F7)","次へ(F8)","反映(F12)","閉じる"] |
| true | requiredInputs | includesAll | inputs.id | [] | ["defNameInput","dataNameInput","defFile","dataFile"] | ["defNameInput","dataNameInput","defFile","dataFile"] |