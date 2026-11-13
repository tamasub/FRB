$old = @{}
$new = @{}

git diff -- wwwroot/countstep/countstep.txt |
  ForEach-Object {
    if ($_ -match '^([+-])\s*([^\s]+\.(?:js|mjs|cs|html|css))\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*$') {
      $sign = $matches[1]
      $file = $matches[2]
      $total = [int]$matches[6]

      if ($sign -eq '-') { $old[$file] = $total }
      if ($sign -eq '+') { $new[$file] = $total }
    }
  }

($old.Keys + $new.Keys | Sort-Object -Unique) |
  ForEach-Object {
    $file = $_
    $before = if ($old.ContainsKey($file)) { $old[$file] } else { 0 }
    $after  = if ($new.ContainsKey($file)) { $new[$file] } else { 0 }

    [pscustomobject]@{
      File = $file
      Before = $before
      After = $after
      Delta = $after - $before
    }
  } |
  Where-Object { $_.Delta -ne 0 } |
  Sort-Object Delta -Descending |
  Format-Table -AutoSize