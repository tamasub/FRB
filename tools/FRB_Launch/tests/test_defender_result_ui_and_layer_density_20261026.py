"""Regressions: never mistake an old scan for the current scan; tighten toolbar."""
from pathlib import Path

import defender_scan

ROOT = Path(__file__).resolve().parents[1]
VIEW = (ROOT / 'src/expanded_view.py').read_text(encoding='utf-8')
PAGE_TABS = (ROOT / 'src/page_tab_theme.py').read_text(encoding='utf-8')
APP = (ROOT / 'src/app.py').read_text(encoding='utf-8')


def test_defender_fallback_reports_this_invocation_not_unrelated_ui_summary():
    path = r"C:\Users\example\日本語 & copy's folder\sample file.xlsx"
    script = defender_scan.defender_fallback_script(path)
    assert script.count('Start-MpScan -ScanType CustomScan -ScanPath ') == 1
    assert "日本語 & copy''s folder" in script
    assert "Start-Process -FilePath 'windowsdefender://customscan'" not in script
    assert 'スキャンコマンドが終了しました' in script
    assert "'対象: ' + $targetPath" in script
    assert "'実行開始: ' + $startedAt.ToString" in script
    assert "'実行終了: ' + $finishedAt.ToString" in script
    assert "'脅威の有無: この画面だけでは断定できません'" in script
    assert "Add-Type -AssemblyName System.Windows.Forms" in script
    assert "$dialog.TopMost = $true" in script
    assert "[void]$dialog.ShowDialog()" in script
    assert "$history.Text = '保護の履歴'" in script
    assert "$history.Add_Click({" in script
    assert "'FRB Launch - 今回のDefenderスキャン結果'" in script
    assert 'ScanType QuickScan' not in script
    assert 'ScanType FullScan' not in script
    assert 'Invoke-Expression' not in script


def test_defender_verifies_matching_event_id_before_reporting_completion():
    script = defender_scan.defender_fallback_script('C:/file.txt')
    assert 'Id = 1000,1001,1002' in script
    assert "'Microsoft-Windows-Windows Defender/Operational'" in script
    assert "[string]$fields['Scan Resources']" in script
    assert "[string]$fields['Scan ID']" in script
    assert '$ends.ContainsKey($_)' in script
    assert '-not $cancelled.ContainsKey($_)' in script
    assert 'スキャン完了（Defenderイベント 1001 確認）' in script
    assert 'イベントログとの照合はできませんでした' in script
    assert 'スキャン完了を確認できませんでした' in script
    assert 'Read-Host' in script  # final fallback when a native dialog is blocked
    assert 'No threats' not in script


def test_second_layer_row_itself_shrinks_without_clipping_scrollbar():
    assert 'padding: 4px 15px;' in PAGE_TABS
    assert 'border-radius:9px;padding:4px 10px;text-align:left;font-size:12px;' in VIEW
    assert 'self.toolbar_scroller.setFixedHeight(34)' in VIEW
    assert 'self.root_layout.setContentsMargins(4, 1, 4, 1)' in VIEW
    assert 'outer.setSpacing(5)' in VIEW
    assert 'self.toolbar_scroller.horizontalScrollBar().rangeChanged.connect(' in VIEW
    assert 'self.update_root_toolbar_height)' in VIEW
    assert 'required = 48 if maximum > minimum else 34' in VIEW
    assert 'self.toolbar_scroller.setFixedHeight(41)' not in VIEW


def test_launcher_keeps_defender_inactive_while_research_module_survives():
    assert 'request_native_defender_scan(path)' not in APP
    assert 'start_defender_custom_scan(path)' not in APP
    assert 'from defender_scan import ' not in APP
    assert (ROOT / 'src/defender_scan.py').is_file()
