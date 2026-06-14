うぃーー、まずこれで最小起動いける。

## 1. プロジェクト作成

```bat
mkdir FRBStudio
cd FRBStudio
dotnet new web
mkdir wwwroot defs data
```

## 2. `Program.cs` 全貼り替え

## 3. 起動確認

```bat
dotnet run
```

ブラウザでこれ。

```txt
http://localhost:5055
```

## 4. publish

```bat
dotnet publish -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true
```

出力先はだいたいここ。

```txt
bin\Release\net10.0\win-x64\publish\
```

`dotnet publish` はアプリを発行先フォルダへ出力し、self-contained は実行に必要な .NET ファイルも含める方式。Single File publish も公式に案内あり。([Microsoft Learn][1])

次は `wwwroot/index.html` から `/api/data/fft_log_sample.json` を読んで、保存ボタンでPOSTする形に繋げれば完成やね。

[1]: https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-publish?utm_source=chatgpt.com "dotnet publish command - .NET CLI"
