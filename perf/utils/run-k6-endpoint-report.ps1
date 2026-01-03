param(
  [string]$BaseUrl = 'http://[::1]',
  [string]$Script = 'perf/k6/api-core-stages.js',
  [string]$Stages = '10s:5,20s:30,20s:30,10s:0',
  [switch]$PressureMode,
  [switch]$SkipRegister,
  [int]$P95GoalMs = 200,
  [int]$TopN = 20,
  [string]$OutDir
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function New-Timestamp() { Get-Date -Format 'yyyyMMdd-HHmmss' }

function Percentile([double[]]$values, [double]$p) {
  if (-not $values -or $values.Count -eq 0) { return $null }
  $sorted = @($values | Sort-Object)
  $n = $sorted.Length
  if ($n -eq 1) { return [double]$sorted[0] }
  # linear interpolation between closest ranks
  $rank = ($p / 100.0) * ($n - 1)
  $lo = [math]::Floor($rank)
  $hi = [math]::Ceiling($rank)
  if ($lo -eq $hi) { return [double]$sorted[$lo] }
  $w = $rank - $lo
  return ([double]$sorted[$lo]) * (1.0 - $w) + ([double]$sorted[$hi]) * $w
}

function Parse-K6JsonLines([string]$path) {
  $results = @()
  Get-Content $path | ForEach-Object {
    if (-not $_) { return }
    try {
      $o = $_ | ConvertFrom-Json
      if ($o.type -ne 'Point') { return }
      if ($o.metric -ne 'http_req_duration') { return }

      $tags = $o.data.tags
      $endpoint = $null
      if ($tags.PSObject.Properties.Name -contains 'endpoint') {
        $endpoint = [string]$tags.endpoint
      }
      if ([string]::IsNullOrWhiteSpace($endpoint)) {
        # fallback: raw url/name (least ideal, but still helps)
        if ($tags.PSObject.Properties.Name -contains 'name') {
          $endpoint = [string]$tags.name
        } elseif ($tags.PSObject.Properties.Name -contains 'url') {
          $endpoint = [string]$tags.url
        } else {
          $endpoint = 'unknown'
        }
      }

      $status = $null
      if ($tags.PSObject.Properties.Name -contains 'status') { $status = [int]$tags.status }
      $method = $null
      if ($tags.PSObject.Properties.Name -contains 'method') { $method = [string]$tags.method }
      $flow = $null
      if ($tags.PSObject.Properties.Name -contains 'flow') { $flow = [string]$tags.flow }

      $results += [pscustomobject]@{
        endpoint = $endpoint
        method = $method
        flow = $flow
        status = $status
        duration_ms = [double]$o.data.value
      }
    } catch {
      # ignore malformed lines
    }
  }
  return $results
}

# Locate k6 exe (as documented in perf/README.md)
$k6 = '.\\tools\\k6\\k6-v1.4.2-windows-amd64\\k6.exe'
if (!(Test-Path $k6)) {
  throw "k6 not found at $k6 (need unzip tools/k6/k6-v1.4.2-windows-amd64.zip)"
}

if (-not $OutDir) {
  $OutDir = Join-Path 'perf\\results' ("endpoint-report-" + (New-Timestamp))
}
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$metricsPath = Join-Path $OutDir 'k6-metrics.json'
$summaryPath = Join-Path $OutDir 'k6-summary.json'
$consolePath = Join-Path $OutDir 'k6-console.txt'
$reportMd = Join-Path $OutDir 'top-endpoints.md'
$reportCsv = Join-Path $OutDir 'top-endpoints.csv'

$env:BASE_URL = $BaseUrl
$env:STAGES = $Stages
if ($PressureMode) { $env:PERF_PRESSURE = '1' } else { $env:PERF_PRESSURE = '0' }
if ($SkipRegister) { $env:REGISTER_USER = '0' }

# Run k6: json output has per-request Point with tags
# Note: k6 may write request timeout warnings to stderr, which PowerShell can surface as a NativeCommandError.
# We still want to continue and generate a report from whatever metrics were collected.
$exit = 0
try {
  & $k6 run $Script -o "json=$metricsPath" --summary-export $summaryPath *>> $consolePath
  $exit = $LASTEXITCODE
} catch {
  $exit = $LASTEXITCODE
  "k6 threw a terminating error (exit=$exit). Continuing to parse metrics if present." | Out-File -Append $consolePath
}
"k6 exit=$exit" | Out-File -Append $consolePath

if (!(Test-Path $metricsPath)) {
  throw "metrics missing: $metricsPath"
}

$points = Parse-K6JsonLines $metricsPath
if (-not $points -or $points.Count -eq 0) {
  throw "no http_req_duration points parsed from $metricsPath"
}

$groups = $points | Group-Object endpoint
$rows = foreach ($g in $groups) {
  $dur = @($g.Group | ForEach-Object { [double]$_.duration_ms })
  $count = $dur.Count
  $failCount = @($g.Group | Where-Object { $_.status -ge 400 }).Count
  [pscustomobject]@{
    endpoint = $g.Name
    count = $count
    fail_rate = if ($count -gt 0) { [math]::Round($failCount / $count, 4) } else { 0 }
    p95_ms = [math]::Round((Percentile $dur 95), 1)
    p50_ms = [math]::Round((Percentile $dur 50), 1)
    avg_ms = [math]::Round((($dur | Measure-Object -Average).Average), 1)
    max_ms = [math]::Round((($dur | Measure-Object -Maximum).Maximum), 1)
  }
}

$top = $rows | Sort-Object p95_ms -Descending | Select-Object -First $TopN

# Goal stats
$totalEndpoints = @($rows).Count
$meeting = @($rows | Where-Object { $_.p95_ms -le $P95GoalMs }).Count
$meetingRate = if ($totalEndpoints -gt 0) { [math]::Round($meeting / $totalEndpoints, 4) } else { 0 }
$notMeeting = $totalEndpoints - $meeting
$notMeetingTop = $rows | Where-Object { $_.p95_ms -gt $P95GoalMs } | Sort-Object p95_ms -Descending | Select-Object -First $TopN

# Write CSV
$top | Export-Csv -NoTypeInformation -Encoding UTF8 $reportCsv

# Write Markdown
$md = @()
$md += ('# Top {0} endpoints by p95' -f $TopN)
$md += ''
$md += ('Output dir: `{0}`' -f $OutDir)
$md += ''
$md += ('P95 goal: {0}ms' -f $P95GoalMs)
$md += ('Meeting goal: {0}/{1} ({2})' -f $meeting, $totalEndpoints, $meetingRate)
$md += ('Not meeting: {0}' -f $notMeeting)
$md += ''
$md += '| endpoint | count | fail_rate | p95_ms | p50_ms | avg_ms | max_ms |'
$md += '|---|---:|---:|---:|---:|---:|---:|'
foreach ($r in $top) {
  $md += ('| {0} | {1} | {2} | {3} | {4} | {5} | {6} |' -f $r.endpoint, $r.count, $r.fail_rate, $r.p95_ms, $r.p50_ms, $r.avg_ms, $r.max_ms)
}

$md += ''
$md += ('## Endpoints not meeting p95<= {0}ms (Top {1})' -f $P95GoalMs, $TopN)
$md += ''
$md += '| endpoint | count | fail_rate | p95_ms | p50_ms | avg_ms | max_ms |'
$md += '|---|---:|---:|---:|---:|---:|---:|'
foreach ($r in $notMeetingTop) {
  $md += ('| {0} | {1} | {2} | {3} | {4} | {5} | {6} |' -f $r.endpoint, $r.count, $r.fail_rate, $r.p95_ms, $r.p50_ms, $r.avg_ms, $r.max_ms)
}
$md -join "`n" | Out-File -Encoding UTF8 $reportMd

# Print a short summary
"Generated: $reportMd";
"Generated: $reportCsv";
$top | Format-Table -AutoSize | Out-String -Width 220
