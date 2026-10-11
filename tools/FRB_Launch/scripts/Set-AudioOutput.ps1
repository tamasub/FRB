[CmdletBinding()]
param([string]$DeviceId='', [string]$ConfigPath='', [string]$VariableId='', [switch]$Choose, [switch]$List)
$ErrorActionPreference='Stop'
$logDir=Join-Path $env:LOCALAPPDATA 'FRBLaunch'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
try {
    Add-Type -Path (Join-Path $PSScriptRoot 'AudioEndpoint.cs')
    $devices=@([FrbAudio.Audio]::List())
    if (-not $devices.Count) { throw 'No active audio output devices. Connect the speaker/earphones first.' }
    if ($List) {
        $lines=@('Audio output devices (active only)', '')
        foreach ($d in $devices) { $lines+=@(('Name: '+$d.Name),('Id: '+$d.Id),('Default: '+$d.Default+' / Communications: '+$d.Communications),'') }
        $report=Join-Path $logDir 'audio_devices.txt'
        $lines | Set-Content -LiteralPath $report -Encoding UTF8
        Start-Process notepad.exe -ArgumentList ('"'+$report+'"')
        exit 0
    }
    $data=$null;$original=$null;$variable=$null
    if ($VariableId) {
        if (-not $ConfigPath) { throw 'ConfigPath is required with VariableId.' }
        $original=[IO.File]::ReadAllBytes($ConfigPath)
        $data=Get-Content -LiteralPath $ConfigPath -Raw -Encoding UTF8 | ConvertFrom-Json
        $vars=@($data.launch_variables | Where-Object { $_.variable_id -eq $VariableId })
        if ($vars.Count -ne 1) { throw ('Configuration variable not found or duplicated: '+$VariableId) }
        $variable=$vars[0];$DeviceId=[string]$variable.launch_value
    }
    $save=$false
    if ($Choose -or -not $DeviceId -or $DeviceId.StartsWith('REPLACE_')) {
        Add-Type -AssemblyName System.Windows.Forms
        Add-Type -AssemblyName System.Drawing
        $form=New-Object Windows.Forms.Form
        $form.Text=$(if ($variable) { 'FRB Launch - '+$variable.title+'を登録' } else { 'FRB Launch - 音声出力を切り替え' });$form.Width=620;$form.Height=330
        $form.StartPosition='CenterScreen';$form.TopMost=$true
        $listBox=New-Object Windows.Forms.ListBox
        $listBox.Dock='Fill';$listBox.Font=New-Object Drawing.Font('Yu Gothic UI',11)
        foreach ($d in $devices) { [void]$listBox.Items.Add($d.Name + $(if ($d.Default) {' [Default]'} else {''})) }
        $listBox.SelectedIndex=0
        for ($i=0;$i -lt $devices.Count;$i++) {
            if ($devices[$i].Id -eq $DeviceId) { $listBox.SelectedIndex=$i;break }
        }
        $form.Add_Shown({[void]$listBox.Focus()})
        $buttons=New-Object Windows.Forms.FlowLayoutPanel;$buttons.Dock='Bottom';$buttons.Height=45
        $ok=New-Object Windows.Forms.Button;$ok.Text=$(if ($variable) {'登録'} else {'切替'});$ok.DialogResult=[Windows.Forms.DialogResult]::OK
        $cancel=New-Object Windows.Forms.Button;$cancel.Text='キャンセル';$cancel.DialogResult=[Windows.Forms.DialogResult]::Cancel
        $buttons.Controls.Add($ok);$buttons.Controls.Add($cancel)
        $form.Controls.Add($listBox);$form.Controls.Add($buttons);$form.AcceptButton=$ok;$form.CancelButton=$cancel
        $listBox.Add_DoubleClick({$form.DialogResult=[Windows.Forms.DialogResult]::OK;$form.Close()})
        try {
            if ($form.ShowDialog() -ne [Windows.Forms.DialogResult]::OK) { Write-Host 'Cancelled';exit 0 }
            $DeviceId=$devices[$listBox.SelectedIndex].Id;$save=($null -ne $variable)
        } finally { $form.Dispose() }
    }
    [FrbAudio.Audio]::Set($DeviceId)
    if ($save) {
        $variable.launch_value=$DeviceId
        $json=$data | ConvertTo-Json -Depth 100
        if ([Convert]::ToBase64String([IO.File]::ReadAllBytes($ConfigPath)) -ne [Convert]::ToBase64String($original)) {
            throw 'Output switched, but JSON was edited elsewhere. Registration was not saved. Retry registration.'
        }
        $backup=Join-Path $logDir ('audio_config_'+(Get-Date -Format 'yyyyMMdd_HHmmss')+'_'+[Guid]::NewGuid().ToString('N')+'.json')
        $temp=$ConfigPath+'.'+[Guid]::NewGuid().ToString('N')+'.tmp'
        try {
            [IO.File]::WriteAllText($temp,$json,[Text.UTF8Encoding]::new($false))
            if ([Convert]::ToBase64String([IO.File]::ReadAllBytes($ConfigPath)) -ne [Convert]::ToBase64String($original)) {
                throw 'Output switched, but JSON changed during registration. No settings were saved.'
            }
            [IO.File]::WriteAllBytes($backup,$original)
            [IO.File]::Replace($temp,$ConfigPath,[System.Management.Automation.Language.NullString]::Value)
        } finally { if (Test-Path -LiteralPath $temp) { Remove-Item -LiteralPath $temp } }
        $savedData=Get-Content -LiteralPath $ConfigPath -Raw -Encoding UTF8 | ConvertFrom-Json
        $savedVars=@($savedData.launch_variables | Where-Object { $_.variable_id -eq $VariableId })
        if ($savedVars.Count -ne 1 -or $savedVars[0].launch_value -ne $DeviceId) {
            throw 'JSON save verification failed. Check the audio log and configuration.'
        }
        $savedName=($devices | Where-Object {$_.Id -eq $DeviceId} | Select-Object -First 1).Name
        $registration='Registered: '+$VariableId+' = '+$DeviceId+' JSON: '+$ConfigPath+' Backup: '+$backup
        Write-Host $registration
        Add-Content -LiteralPath (Join-Path $logDir 'audio.log') -Encoding UTF8 -Value ((Get-Date -Format 'yyyy/MM/dd HH:mm:ss')+' '+$registration)
        Add-Type -AssemblyName System.Windows.Forms
        [void][Windows.Forms.MessageBox]::Show(
            ('JSONにIDを保存しました。'+[Environment]::NewLine+[Environment]::NewLine+
             $variable.title+': '+$savedName+[Environment]::NewLine+
             '変数: '+$VariableId+[Environment]::NewLine+
             'ID: '+$DeviceId+[Environment]::NewLine+[Environment]::NewLine+
             '保存先: '+$ConfigPath),
            'FRB Launch - 登録完了', [Windows.Forms.MessageBoxButtons]::OK,
            [Windows.Forms.MessageBoxIcon]::Information,
            [Windows.Forms.MessageBoxDefaultButton]::Button1,
            [Windows.Forms.MessageBoxOptions]::DefaultDesktopOnly)
    }
    $name=($devices | Where-Object {$_.Id -eq $DeviceId} | Select-Object -First 1).Name
    Write-Host ('Output switched: '+$name)
    Add-Content -LiteralPath (Join-Path $logDir 'audio.log') -Encoding UTF8 -Value ((Get-Date -Format 'yyyy/MM/dd HH:mm:ss')+' Output switched: '+$name+' '+$DeviceId)
    exit 0
} catch {
    $failure=$_.Exception.ToString()
    try {
        Add-Type -AssemblyName System.Windows.Forms
        [void][Windows.Forms.MessageBox]::Show(
            ('音声出力の処理に失敗しました。'+[Environment]::NewLine+$failure+[Environment]::NewLine+
             'ログ: '+(Join-Path $logDir 'audio.log')),
            'FRB Launch - 音声出力エラー', [Windows.Forms.MessageBoxButtons]::OK,
            [Windows.Forms.MessageBoxIcon]::Error,
            [Windows.Forms.MessageBoxDefaultButton]::Button1,
            [Windows.Forms.MessageBoxOptions]::DefaultDesktopOnly)
    } catch { }
    Write-Host ('ERROR: '+$failure)
    Add-Content -LiteralPath (Join-Path $logDir 'audio.log') -Encoding UTF8 -Value ((Get-Date -Format 'yyyy/MM/dd HH:mm:ss')+' ERROR: '+$failure)
    exit 1
}
