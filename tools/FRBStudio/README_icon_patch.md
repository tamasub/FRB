# FRB Studio アイコン表示パッチ

## 置き場所
以下の4ファイルを `F:\FRB\tools\FRBStudio_App\` に上書き/配置してください。

```text
F:\FRB\tools\FRBStudio_App\Program.cs
F:\FRB\tools\FRBStudio_App\FRBStudio.csproj
F:\FRB\tools\FRBStudio_App\FRB.ico
F:\FRB\tools\FRBStudio_App\FRB_tray.ico
```

## 変更内容

- `FRBStudio.csproj`
  - `ApplicationIcon` に `FRB.ico` を指定
  - `FRB.ico` / `FRB_tray.ico` をビルド出力先へコピー

- `Program.cs`
  - タスクトレイの `NotifyIcon` を `SystemIcons.Application` から `FRB_tray.ico` 読み込みへ変更
  - 見つからない場合は `FRB.ico`、さらに無ければ標準アイコンへフォールバック

## ビルド

VS Code のターミナルでプロジェクトフォルダーに移動して実行します。

```powershell
cd F:\FRB\tools\FRBStudio_App
dotnet build
```

配布用に固める場合は例：

```powershell
dotnet publish -c Release -r win-x64 --self-contained false
```

## 注意

Windowsが古いアイコンをキャッシュしている場合、exeのアイコン表示だけ少し遅れて反映されることがあります。
その場合は `bin` / `obj` を削除して再ビルドすると反映されやすいです。
