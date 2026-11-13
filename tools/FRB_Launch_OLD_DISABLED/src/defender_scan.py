"""One-click Microsoft Defender scan for a selected file or directory.

Prefer Windows Explorer's own Scan with Microsoft Defender context action,
when exposed to Shell.Application. Windows 11 does not expose every modern
shell command through this interface. If absent, invoke the documented
Start-MpScan CustomScan cmdlet in a visible, independent PowerShell console.
Never build a cmd.exe shell string from a file path or claim the file is clean
merely because the scan was *requested*.
"""

import base64
import os
from pathlib import Path
import subprocess


_NATIVE_LABELS = (
    'Microsoft Defenderでスキャンする',
    'Microsoft Defender でスキャンする',
    'Microsoft Defenderでスキャン',
    'Microsoft Defender でスキャン',
    'Windows Defenderでスキャンする',
    'Scan with Microsoft Defender',
    'Scan with Windows Defender',
)


def _ps_literal(value):
    """PowerShell literal quoting: apostrophes and metacharacters are data."""
    return "'" + str(value).replace("'", "''") + "'"


def native_defender_script(path):
    target = Path(path)
    labels = ', '.join(_ps_literal(label) for label in _NATIVE_LABELS)
    return (
        "$ErrorActionPreference = 'Stop'\n"
        "try {\n"
        "  $shell = New-Object -ComObject Shell.Application\n"
        f"  $folder = $shell.Namespace({_ps_literal(str(target.parent))})\n"
        "  if ($null -eq $folder) { Write-Output 'NO_COMMAND'; exit 0 }\n"
        f"  $item = $folder.ParseName({_ps_literal(target.name)})\n"
        "  if ($null -eq $item) { Write-Output 'NO_COMMAND'; exit 0 }\n"
        f"  $names = @({labels})\n"
        "  foreach ($verb in $item.Verbs()) {\n"
        "    $label = ([string]$verb.Name) -replace '&', ''\n"
        "    $label = ($label -replace '\\(&.\\)', '').Trim()\n"
        "    $label = ($label -replace '(?:\\.\\.\\.|…)$', '').Trim()\n"
        "    if ($names -contains $label) {\n"
        "      $verb.DoIt()\n"
        "      Write-Output 'INVOCATION_REQUESTED'\n"
        "      exit 0\n"
        "    }\n"
        "  }\n"
        "  Write-Output 'NO_COMMAND'\n"
        "} catch { Write-Output 'NO_COMMAND' }\n"
    )


def request_native_defender_scan(path, *, runner=None):
    """True iff Windows' explicit Defender scan shell verb was requested."""
    if os.name != 'nt':
        raise RuntimeError('Microsoft DefenderスキャンはWindows専用です')
    if not Path(path).exists():
        raise FileNotFoundError(str(path))
    script = native_defender_script(path)
    encoded = base64.b64encode(script.encode('utf-16-le')).decode('ascii')
    run = runner or subprocess.run
    try:
        result = run(['powershell.exe', '-NoProfile', '-Sta', '-EncodedCommand', encoded],
                     capture_output=True, text=True, encoding='utf-8', errors='replace',
                     timeout=10, check=False,
                     creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    except (OSError, subprocess.TimeoutExpired):
        return False
    return (result.returncode == 0 and
            'INVOCATION_REQUESTED' in (result.stdout or '').splitlines())


def defender_fallback_script(path):
    """Run a selected-path scan and report *this invocation*, not stale UI.

    Windows Security's ``customscan`` page may show an unrelated older Quick
    Scan summary even after Start-MpScan completes. The native Explorer shell
    command still takes priority. For the command-line fallback, show a small
    independent result dialog with the actual target and invocation time.
    Where available, correlate Defender event 1000 and 1001 using Scan ID and
    event 1000's Scan Resources; never claim '0 threats' from command success.
    """
    quoted = _ps_literal(str(path))
    return (
        "$ErrorActionPreference = 'Stop'\n"
        "try { $Host.UI.RawUI.WindowTitle = 'FRB Launch - Microsoft Defender scan' } catch {}\n"
        f"$targetPath = {quoted}\n"
        "$startedAt = Get-Date\n"
        "$scanError = $null\n"
        "try {\n"
        "  Import-Module Defender -ErrorAction Stop\n"
        "  Write-Host 'Scanning the selected file or folder with Microsoft Defender...'\n"
        f"  Start-MpScan -ScanType CustomScan -ScanPath {quoted} -ErrorAction Stop\n"
        "} catch {\n"
        "  $scanError = $_.Exception.Message\n"
        "}\n"
        "$finishedAt = Get-Date\n"
        "$eventSummary = 'イベントログとの照合はできませんでした'\n"
        "if ($null -eq $scanError) {\n"
        "  try {\n"
        "    # Event 1000 supplies a Scan ID AND Scan Resources; 1001 is the\n"
        "    # completion of that same ID. Unrelated quick scans must not match.\n"
        "    $events = @(Get-WinEvent -FilterHashtable @{\n"
        "      LogName = 'Microsoft-Windows-Windows Defender/Operational';\n"
        "      Id = 1000,1001,1002; StartTime = $startedAt.AddSeconds(-2)\n"
        "    } -MaxEvents 200 -ErrorAction Stop)\n"
        "    $starts = @()\n"
        "    $ends = @{}\n"
        "    $cancelled = @{}\n"
        "    foreach ($evt in $events) {\n"
        "      $fields = @{}\n"
        "      foreach ($field in ([xml]$evt.ToXml()).Event.EventData.Data) {\n"
        "        $fields[[string]$field.Name] = [string]$field.'#text'\n"
        "      }\n"
        "      $scanId = [string]$fields['Scan ID']\n"
        "      if ([string]::IsNullOrWhiteSpace($scanId)) { continue }\n"
        "      if ($evt.Id -eq 1000) {\n"
        "        $resource = [string]$fields['Scan Resources']\n"
        "        if ($resource.IndexOf($targetPath, [System.StringComparison]::OrdinalIgnoreCase) -ge 0) {\n"
        "          $starts += $scanId\n"
        "        }\n"
        "      } elseif ($evt.Id -eq 1001) { $ends[$scanId] = $evt }\n"
        "      elseif ($evt.Id -eq 1002) { $cancelled[$scanId] = $evt }\n"
        "    }\n"
        "    $matching = @($starts | Where-Object { $ends.ContainsKey($_) -and -not $cancelled.ContainsKey($_) })\n"
        "    if ($matching.Count -gt 0) {\n"
        "      $eventSummary = 'スキャン完了（Defenderイベント 1001 確認）'\n"
        "    } elseif ($starts.Count -gt 0) {\n"
        "      $eventSummary = '開始記録あり・完了イベントは未確認'\n"
        "    }\n"
        "  } catch {\n"
        "    # Event log permissions, schema and delayed writes vary by PC.\n"
        "    # A successful cmdlet alone does not establish a clean result.\n"
        "  }\n"
        "}\n"
        "if ($null -eq $scanError) {\n"
        "  $resultLine = 'Defenderスキャンコマンドが終了しました'\n"
        "} else {\n"
        "  $resultLine = ('実行エラー: ' + $scanError)\n"
        "  $eventSummary = 'スキャン完了を確認できませんでした'\n"
        "}\n"
        "$details = @('対象: ' + $targetPath,\n"
        "  '実行開始: ' + $startedAt.ToString('yyyy/MM/dd HH:mm:ss'),\n"
        "  '実行終了: ' + $finishedAt.ToString('yyyy/MM/dd HH:mm:ss'),\n"
        "  '実行状態: ' + $resultLine, 'Defender記録: ' + $eventSummary,\n"
        "  '脅威の有無: この画面だけでは断定できません',\n"
        "  '検出が疑われる場合はWindows セキュリティの保護の履歴をご確認ください') -join [Environment]::NewLine\n"
        "try {\n"
        "  Add-Type -AssemblyName System.Windows.Forms -ErrorAction Stop\n"
        "  Add-Type -AssemblyName System.Drawing -ErrorAction Stop\n"
        "  $dialog = New-Object System.Windows.Forms.Form\n"
        "  $dialog.Text = 'FRB Launch - 今回のDefenderスキャン結果'\n"
        "  $dialog.Width = 660\n"
        "  $dialog.Height = 310\n"
        "  $dialog.StartPosition = 'CenterScreen'\n"
        "  $dialog.FormBorderStyle = 'FixedDialog'\n"
        "  $dialog.MaximizeBox = $false\n"
        "  $dialog.MinimizeBox = $false\n"
        "  $dialog.TopMost = $true\n"
        "  $label = New-Object System.Windows.Forms.Label\n"
        "  $label.Left = 20; $label.Top = 18; $label.Width = 610; $label.Height = 200\n"
        "  $label.Text = $details\n"
        "  $dialog.Controls.Add($label)\n"
        "  $history = New-Object System.Windows.Forms.Button\n"
        "  $history.Text = '保護の履歴'\n"
        "  $history.Width = 110; $history.Height = 32; $history.Left = 405; $history.Top = 225\n"
        "  $history.Add_Click({\n"
        "    try { Start-Process -FilePath 'windowsdefender://fullhistory/' -ErrorAction Stop }\n"
        "    catch { [System.Windows.Forms.MessageBox]::Show('Windows セキュリティの保護の履歴を開けませんでした') | Out-Null }\n"
        "  })\n"
        "  $dialog.Controls.Add($history)\n"
        "  $close = New-Object System.Windows.Forms.Button\n"
        "  $close.Text = '閉じる'\n"
        "  $close.Width = 96; $close.Height = 32; $close.Left = 532; $close.Top = 225\n"
        "  $close.Add_Click({ $dialog.Close() })\n"
        "  $dialog.Controls.Add($close)\n"
        "  [void]$dialog.ShowDialog()\n"
        "  $dialog.Dispose()\n"
        "} catch {\n"
        "  # A blocked UI framework must not hide an actual scan error/result.\n"
        "  Write-Host $details\n"
        "  Write-Host ('結果画面を開けませんでした: ' + $_.Exception.Message)\n"
        "  Read-Host 'Press Enter to close this window' | Out-Null\n"
        "}\n"
    )


def start_defender_custom_scan(path, *, opener=None):
    """Launch (do not await) a visible PowerShell window for selected-path scan.

    This fallback runs only if the Windows shell verb was not available. A
    subprocess launch is NOT proof that the antivirus scan completed.
    """
    if os.name != 'nt':
        raise RuntimeError('Microsoft DefenderスキャンはWindows専用です')
    if not Path(path).exists():
        raise FileNotFoundError(str(path))
    encoded = base64.b64encode(defender_fallback_script(path).encode('utf-16-le')).decode('ascii')
    (opener or subprocess.Popen)(
        ['powershell.exe', '-NoProfile', '-EncodedCommand', encoded],
        creationflags=getattr(subprocess, 'CREATE_NEW_CONSOLE', 0),
    )
