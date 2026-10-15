FRB Studio 外部ライブラリ復旧 (2026-10-15 ZIP 調査)

1) FRBStudio_restore_mermaid_11_17_2.cmd と同名 .ps1 を
   FRBStudio_App フォルダー直下 (wwwroot と同じ階層) に配置。
2) .cmd を実行。公式 npm から Mermaid 11.17.2 を取得する。
3) wwwroot/js/lib/mermaid/mermaid.esm.min.mjs が作成されたことを確認。
4) wwwroot/js/lib/mermaid/chunks/ もあることを確認。
5) wwwroot/mdViewer.html で Mermaid の flowchart を表示して確認。

既存の mermaid フォルダーがある場合は安全のためスクリプトを中止します。
このスクリプトは Mermaid だけを復旧し、mdViewer.html や JSON、ソースを編集しません。

他の外部依存物（テスト時に必要な場合のみ）:
- SeleniumTaste/: package-lock.json を使い npm ci (selenium-webdriver 4.47.0)
- SeleniumTaste/driver/: Edge WebDriver をRuntime対応版で配置。Selenium Managerでも解決可能な場合あり
- tools/chatgpt-share-export-minimum/: setup.cmd（node_modulesとPlaywright Chromium）
- NativeShell/: dotnet restore/build（Microsoft.Web.WebView2 1.0.4022.49）

Marked v15.0.12 / DOMPurify v3.2.5 は ZIP に含まれているので再ダウンロード不要。
