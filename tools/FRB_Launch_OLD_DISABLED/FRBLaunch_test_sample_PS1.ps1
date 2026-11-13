# FRB Launch - PowerShell launch test
# Windows PowerShell 5.1 / PowerShell 7 (Windows)
# Run this file from FRB Launch file search.
# No administrator privileges are required.

$ErrorActionPreference = 'Stop'

$now = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
$logPath = Join-Path $env:TEMP 'FRBLaunch_PS1_Test.log'
$scriptPath = $MyInvocation.MyCommand.Path
$psVersion = $PSVersionTable.PSVersion.ToString()

$record = @(
    '----- FRB Launch PS1 Test -----'
    "Time       : $now"
    "Script     : $scriptPath"
    "PowerShell : $psVersion"
    "User       : $env:USERNAME"
    "Process ID : $PID"
    ''
) -join [Environment]::NewLine

try {
    Add-Content -LiteralPath $logPath -Value $record -Encoding UTF8
} catch {
    # Display the confirmation window even if the log cannot be written.
    $logPath = "ログ保存失敗: $($_.Exception.Message)"
}

try {
    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -AssemblyName System.Drawing

    $form = New-Object System.Windows.Forms.Form
    $form.Text = 'FRB Launch - PS1 動作確認'
    $form.StartPosition = [System.Windows.Forms.FormStartPosition]::CenterScreen
    $form.FormBorderStyle = [System.Windows.Forms.FormBorderStyle]::FixedDialog
    $form.MaximizeBox = $false
    $form.MinimizeBox = $false
    $form.ShowInTaskbar = $true
    $form.TopMost = $true
    $form.ClientSize = New-Object System.Drawing.Size(460, 205)
    $form.Font = New-Object System.Drawing.Font('Segoe UI', 10)

    $title = New-Object System.Windows.Forms.Label
    $title.Text = 'PS1 実行成功！'
    $title.Font = New-Object System.Drawing.Font('Segoe UI', 15, [System.Drawing.FontStyle]::Bold)
    $title.TextAlign = [System.Drawing.ContentAlignment]::MiddleCenter
    $title.Location = New-Object System.Drawing.Point(10, 15)
    $title.Size = New-Object System.Drawing.Size(440, 44)
    $form.Controls.Add($title)

    $info = New-Object System.Windows.Forms.Label
    $info.Text = "実行日時: $now`r`nPowerShell: $psVersion`r`nログ: $logPath"
    $info.TextAlign = [System.Drawing.ContentAlignment]::MiddleCenter
    $info.Location = New-Object System.Drawing.Point(12, 64)
    $info.Size = New-Object System.Drawing.Size(436, 85)
    $form.Controls.Add($info)

    $ok = New-Object System.Windows.Forms.Button
    $ok.Text = 'OK（閉じる）'
    $ok.Location = New-Object System.Drawing.Point(165, 160)
    $ok.Size = New-Object System.Drawing.Size(130, 32)
    $ok.Add_Click({ $form.Close() })
    $form.Controls.Add($ok)
    $form.AcceptButton = $ok
    $form.Add_Shown({ $form.Activate() })
    [void]$form.ShowDialog()
    $form.Dispose()
} catch {
    # Fall back to a built-in Windows popup if WinForms cannot be loaded.
    $message = "PS1 実行成功！`r`n日時: $now`r`nログ: $logPath"
    try {
        $shell = New-Object -ComObject WScript.Shell
        [void]$shell.Popup($message, 0, 'FRB Launch - PS1 動作確認', 64)
    } catch {
        Write-Host $message
        Read-Host 'Enter を押して終了' | Out-Null
    }
}
