# FRB Windows Icon Pack

## 入っているもの

- `FRB.ico` : 元PNGから作成したWindows用マルチサイズICO
- `FRB_tray.ico` : タスクトレイ向けに少し寄せた簡易版ICO
- `FRB_logo.png` : 元画像
- `FRB_tray_preview.png` : トレイ向け簡易版の確認用PNG

## 置き場所

VS Codeで作業している場合は、まずこれでOKです。

```text
F:\FRB\tools\FRBStudio_App\FRB.ico
F:\FRB\tools\FRBStudio_App\FRB_tray.ico
```

つまり、`FRBStudio.csproj` と `Program.cs` があるフォルダー直下です。

## FRBStudio.csproj への追加例

`<PropertyGroup>` の中にこれを追加します。

```xml
<ApplicationIcon>FRB.ico</ApplicationIcon>
```

さらに、ファイルをビルド後の出力先へコピーするために、`</Project>` の直前あたりへ追加します。

```xml
<ItemGroup>
  <Content Include="FRB.ico" CopyToOutputDirectory="PreserveNewest" />
  <Content Include="FRB_tray.ico" CopyToOutputDirectory="PreserveNewest" />
</ItemGroup>
```

## Program.cs のタスクトレイアイコン変更例

今こうなっているところを探します。

```csharp
Icon = SystemIcons.Application,
```

これに変更します。

```csharp
Icon = LoadTrayIcon(),
```

そして `FrbStudioTrayContext` クラスの中に、このメソッドを追加します。

```csharp
private static Icon LoadTrayIcon()
{
    var iconPath = Path.Combine(AppContext.BaseDirectory, "FRB_tray.ico");
    if (File.Exists(iconPath)) return new Icon(iconPath);

    iconPath = Path.Combine(AppContext.BaseDirectory, "FRB.ico");
    if (File.Exists(iconPath)) return new Icon(iconPath);

    return SystemIcons.Application;
}
```

## ビルド

```powershell
dotnet build
```

または実行なら

```powershell
dotnet run
```
