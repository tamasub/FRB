# SeleniumTaste (Node.js)

FRB Studio NativeShell / WebView2 を Selenium から実画面操作する E2E taste test。

## 前提

- Node.js 22 以上
- `NativeShell/_publish/FRBStudio.NativeShell.exe`
- Microsoft Edge WebDriver（WebView2 Runtime と互換のある版）

既存配置を優先して次を自動探索する。

```text
SeleniumTaste/driver/edgedriver_win64/msedgedriver.exe
SeleniumTaste/driver/msedgedriver.exe
```

見つからない場合は Selenium Manager / PATH に委譲する。

必要なら環境変数で明示可能。

```powershell
$env:FRB_NATIVE_SHELL="F:\\FRB\\tools\\FRBStudio_App\\NativeShell\\_publish\\FRBStudio.NativeShell.exe"
$env:FRB_EDGE_DRIVER="F:\\FRB\\tools\\FRBStudio_App\\SeleniumTaste\\driver\\edgedriver_win64\\msedgedriver.exe"
```

## 初回だけ

```powershell
cd F:\FRB\tools\FRBStudio_App\SeleniumTaste
npm install
```

## 実行

```powershell
npm test
```

構文確認だけなら:

```powershell
npm run check
```

成功時の最終行:

```text
保存E2E: ALL PASS
```

## Responsibility Driven E2E

```powershell
npm run test:responsibility
npm run test:responsibility:search
npm run test:responsibility:aggregate
```

`grid_aggregate` の正式な承認Runnerは NativeShell / Selenium で Grid Header の表示値を観測する。
内部ロジック診断だけ行う場合は次を使う。

```powershell
npm run test:responsibility:aggregate:internal
```


## Selenium 操作速度の調整

Responsibility Driven E2E では、値を入力した直後の待機時間を次の設定で変更できる。

```text
SeleniumTaste/config/selenium_runner_settings_v0_1.json
```

```json
{
  "timing": {
    "after_value_input_ms": 400
  }
}
```

`after_value_input_ms` はミリ秒。`0` にすると待機なし、`1000` にすると値入力後に1秒待機する。
検索Criteria入力やData Editorの値変更など、`setControlValue` を通る入力操作に共通適用する。
テスト開始時に現在値を `Selenium Timing: after_value_input_ms=...` と表示する。
