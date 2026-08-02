Set-Location "F:\FRB"

chcp 65001 | Out-Null

$utf8 = New-Object System.Text.UTF8Encoding $false
[Console]::InputEncoding  = $utf8
[Console]::OutputEncoding = $utf8
$OutputEncoding = $utf8

Get-Content "F:\FRB\FRB_Blog\AI協働001_AI駆動開発.md" -Raw -Encoding utf8 |
    codex exec "入力された文章の内容を日本語で要約してください" |
    Out-File "F:\FRB\ChatGPT_answer.md" -Encoding utf8

Write-Host ""
Write-Host "完了：F:\FRB\ChatGPT_answer.md"
