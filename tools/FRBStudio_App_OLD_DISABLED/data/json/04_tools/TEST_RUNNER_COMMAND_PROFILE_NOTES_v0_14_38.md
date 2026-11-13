# v0.17.2 Test Runner / AppRoot Path Contract

`TestRunner.ps1` は、FRBStudio_App root を基準に実行する。

- Program.cs の CommandProfile は `tools/test/TestRunner.ps1` を FRBStudio_App root 相対パスとして解決する
- `WorkingDirectory` は `.` を標準とし、FRBStudio_App root を意味する
- `TestRunner.ps1` は自分自身の位置 `tools/test/../..` または渡された `-RepositoryRoot` から FRBStudio_App root を解決する
- `tools/FRBStudio_App` のような上位リポジトリ構造を前提にしない
- 会社PCやZIP展開先で、FRBStudio_Appより上位のフォルダー名が変わっても動作することを目指す
