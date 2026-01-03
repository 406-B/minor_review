param(
  [string]$UiBaseUrl = 'http://[::1]',
  [string]$ApiBaseUrl = 'http://[::1]',
  [string]$Workers = '1',
  [string]$Username,
  [string]$Password,
  [switch]$Har,
  [switch]$ShowBrowser,
  [string]$OutDir
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

try {
  [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
  $OutputEncoding = [System.Text.UTF8Encoding]::new($false)
} catch {
}

function New-Timestamp() { Get-Date -Format 'yyyyMMdd-HHmmss' }

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$frontendDir = Join-Path $repoRoot 'src\frontend'

if (-not $OutDir) {
  $OutDir = Join-Path $repoRoot (Join-Path 'perf\results' ("playwright-e2e-" + (New-Timestamp)))
}
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$consolePath = Join-Path $OutDir 'pw-console.txt'
$metricsPath = Join-Path $OutDir 'pw-metrics.jsonl'
$reportMd = Join-Path $OutDir 'report.md'

# Env wiring
$env:UI_BASE_URL = $UiBaseUrl
$env:BASE_URL = $ApiBaseUrl
$env:PW_WORKERS = $Workers
$env:HEADLESS = if ($ShowBrowser) { '0' } else { '1' }

if ($Har) {
  $env:PW_HAR = '1'
  $env:PW_HAR_PATH = (Join-Path $OutDir 'playwright.har')
}

if ($Username) { $env:E2E_USERNAME = $Username }
if ($Password) { $env:E2E_PASSWORD = $Password }

# Make Playwright outputs deterministic & easy to collect
$pwBlobDir = Join-Path $OutDir 'playwright-blob'
$env:PLAYWRIGHT_BLOB_OUTPUT_DIR = $pwBlobDir

# Run
"UI_BASE_URL=$UiBaseUrl" | Out-File -Encoding UTF8 $consolePath
"BASE_URL=$ApiBaseUrl" | Out-File -Encoding UTF8 -Append $consolePath
"PW_WORKERS=$Workers" | Out-File -Encoding UTF8 -Append $consolePath
"HEADLESS=$($env:HEADLESS)" | Out-File -Encoding UTF8 -Append $consolePath

$exit = 0
$raw = ''
try {
  Push-Location $frontendDir
  $raw = (& npm run -s e2e:perf 2>&1 | Out-String)
  $raw | Tee-Object -FilePath $consolePath -Append
  $exit = $LASTEXITCODE
} catch {
  $exit = $LASTEXITCODE
  "playwright threw a terminating error (exit=$exit)." | Out-File -Encoding UTF8 -Append $consolePath
} finally {
  Pop-Location
}

"exit=$exit" | Out-File -Encoding UTF8 -Append $consolePath

# Extract our JSON step lines printed to console
$notesPath = Join-Path $OutDir 'pw-notes.jsonl'
$noteItems = @()
if ($raw) {
  $raw -split "`r?`n" |
    Where-Object { $_.Trim().StartsWith('{') -and $_.Trim().EndsWith('}') } |
    ForEach-Object {
      try {
        $obj = $_ | ConvertFrom-Json -ErrorAction Stop
        if ($obj.type -eq 'step') {
          $_ | Out-File -Encoding UTF8 -Append $metricsPath
        } elseif ($obj.type -eq 'note') {
          $_ | Out-File -Encoding UTF8 -Append $notesPath
          if ($obj.skipped) {
            $noteItems += $obj
          }
        }
      } catch {
        # ignore non-json
      }
    }
}

# Aggregate p50/p95 by step (best effort)
$rows = @()
if (Test-Path $metricsPath) {
  $items = Get-Content $metricsPath | ForEach-Object { $_ | ConvertFrom-Json }
  $groups = $items | Group-Object -Property name
  foreach ($g in $groups) {
    $durs = @($g.Group | ForEach-Object { [double]$_.durMs } | Sort-Object)
    $durCount = @($durs).Count
    if ($durCount -eq 0) { continue }
    $p50i = [Math]::Floor(0.50 * ($durCount - 1))
    $p95i = [Math]::Floor(0.95 * ($durCount - 1))
    $okCount = @($g.Group | Where-Object { $_.ok }).Count
    $rows += [pscustomobject]@{
      step = $g.Name
      count = $durCount
      ok_rate = [Math]::Round(($okCount / [double]$durCount), 4)
      p50_ms = [Math]::Round($durs[$p50i], 2)
      p95_ms = [Math]::Round($durs[$p95i], 2)
      max_ms = [Math]::Round($durs[-1], 2)
    }
  }
}

$md = @()
$md += '# Playwright Browser E2E performance report'
$md += ''
$md += ('Output dir: `{0}`' -f $OutDir)
$md += ''
$md += '## Inputs'
$md += ''
$md += ('- UI_BASE_URL: `{0}`' -f $UiBaseUrl)
$md += ('- BASE_URL: `{0}`' -f $ApiBaseUrl)
$md += ('- HEADLESS: `{0}`' -f $env:HEADLESS)
$md += ('- PW_WORKERS: `{0}`' -f $Workers)
$doApiLoginLine = '1'
if ($env:DO_API_LOGIN) { $doApiLoginLine = $env:DO_API_LOGIN }
$userLine = 'Perf01'
if ($env:E2E_USERNAME) { $userLine = $env:E2E_USERNAME }
elseif ($env:TEST_USERNAME) { $userLine = $env:TEST_USERNAME }
$md += ('- DO_API_LOGIN: `{0}`' -f $doApiLoginLine)
$md += ('- E2E_USERNAME: `{0}`' -f $userLine)
$commLine = '1'
if ($env:DO_UI_COMMUNITY) { $commLine = $env:DO_UI_COMMUNITY }
$profLine = '1'
if ($env:DO_UI_PROFILE) { $profLine = $env:DO_UI_PROFILE }
$md += ('- DO_UI_COMMUNITY: `{0}`' -f $commLine)
$md += ('- DO_UI_PROFILE: `{0}`' -f $profLine)
$uiLoginLine = '1'
if ($env:DO_UI_LOGIN) { $uiLoginLine = $env:DO_UI_LOGIN }
$dishRateLine = '1'
if ($env:DO_DISH_RATE) { $dishRateLine = $env:DO_DISH_RATE }
$dishCheckInLine = '0'
if ($env:DO_DISH_CHECKIN) { $dishCheckInLine = $env:DO_DISH_CHECKIN }
$commDeepLine = '1'
if ($env:DO_COMMUNITY_DEEP) { $commDeepLine = $env:DO_COMMUNITY_DEEP }
$profileDeepLine = '1'
if ($env:DO_PROFILE_DEEP) { $profileDeepLine = $env:DO_PROFILE_DEEP }
$postLikeLine = '0'
if ($env:DO_POST_LIKE) { $postLikeLine = $env:DO_POST_LIKE }
$md += ('- DO_UI_LOGIN: `{0}`' -f $uiLoginLine)
$md += ('- DO_DISH_RATE: `{0}`' -f $dishRateLine)
$md += ('- DO_DISH_CHECKIN: `{0}`' -f $dishCheckInLine)
$md += ('- DO_COMMUNITY_DEEP: `{0}`' -f $commDeepLine)
$md += ('- DO_PROFILE_DEEP: `{0}`' -f $profileDeepLine)
$md += ('- DO_POST_LIKE: `{0}`' -f $postLikeLine)
$harLine = '0'
if ($Har) { $harLine = '1' }
$md += ('- PW_HAR: `{0}`' -f $harLine)
$md += ''
$md += '## Step timing summary (best effort)'
$md += ''
if (@($rows).Count -gt 0) {
  $md += '| step | count | ok_rate | p50_ms | p95_ms | max_ms |'
  $md += '|---|---:|---:|---:|---:|---:|'
  foreach ($r in ($rows | Sort-Object -Property p95_ms -Descending)) {
    $md += ('| {0} | {1} | {2} | {3} | {4} | {5} |' -f $r.step, $r.count, $r.ok_rate, $r.p50_ms, $r.p95_ms, $r.max_ms)
  }
} else {
  $md += '_No step timings captured. See `pw-console.txt`._'
}
$md += ''
$md += '## Skipped / notes (best effort)'
$md += ''
if (@($noteItems).Count -gt 0) {
  $md += '| name | reason | count |'
  $md += '|---|---|---:|'
  $noteGroups = $noteItems | Group-Object -Property reason, name
  foreach ($g in ($noteGroups | Sort-Object -Property Count -Descending)) {
    $reason = $g.Group[0].reason
    $name = $g.Group[0].name
    $md += ('| {0} | {1} | {2} |' -f $name, $reason, $g.Count)
  }
} else {
  $md += '_No skipped notes captured._'
}
$md += ''
$md += '## Artifacts'
$md += ''
$md += '- `pw-console.txt`'
$md += '- `pw-metrics.jsonl` (if any)'
$md += '- `pw-notes.jsonl` (if any)'
$md += '- `playwright-blob/` (if any)'
$md += '- `playwright.har` (if enabled)'
$md -join "`n" | Out-File -Encoding UTF8 $reportMd

"Generated: $reportMd"
"Console: $consolePath"
if (Test-Path $metricsPath) { "Metrics: $metricsPath" }

exit $exit
