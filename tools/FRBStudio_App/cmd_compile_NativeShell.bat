cd F:\FRB\tools\FRBStudio_App\NativeShell


dotnet publish -c Release

cd F:\FRB\tools\FRBStudio_App

xcopy ".\NativeShell\bin\Release\net48\publish\*" ".\NativeShell_publish\" /E /I /Y

pause

