# FRB Studio Markdown Patch

## 配置

このZipを展開して、以下へ上書きしてください。

```text
F:\FRB\tools\FRBStudio_App\
```

`mdViewer.html` は `wwwroot\mdViewer.html` に入ります。

## フォルダー構成

```text
FRBStudio_App
├─ Program.cs
├─ FRBStudio.csproj
├─ FRB.ico
├─ FRB_tray.ico
├─ wwwroot
│  └─ mdViewer.html
├─ data
│  ├─ json
│  └─ markdown
└─ defs
```

## 変更内容

- `data/json` をJSONデータ置き場に変更
- `data/markdown` をMarkdown管理置き場に追加
- 起動時、旧 `data/*.json` は `data/json/*.json` へ初回コピー
- Markdown管理API追加
  - `GET /api/markdown`
  - `GET /api/markdown/{name}`
  - `POST /api/markdown/{name}`
- `mdViewer.html` に管理Markdown選択コンボ追加
- 管理Markdownは選択した瞬間に読み込み
- ローカル/DropしたMarkdownは、管理対象にするか確認
- 上書きボタンで `data/markdown` へ保存

## ビルド

```powershell
cd F:\FRB\tools\FRBStudio_App
dotnet build
```
