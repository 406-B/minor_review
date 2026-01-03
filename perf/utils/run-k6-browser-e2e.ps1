param(
  [string]$UiBaseUrl = 'http://[::1]',
  [string]$ApiBaseUrl = 'http://[::1]',
  [string]$Script = 'perf/k6-browser/e2e-browser-journey.js',
  [string]$UiStages = '10s:1,20s:1,10s:0',
  [string]$BrowserPath = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
  [switch]$ShowBrowser,
  [string]$OutDir
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# Try to keep output readable on Windows PowerShell (avoid mojibake)
try {
  [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
  $OutputEncoding = [System.Text.UTF8Encoding]::new($false)
} catch {
  # best effort
}

function New-Timestamp() { Get-Date -Format 'yyyyMMdd-HHmmss' }

# Locate k6 exe
$k6Preferred = '.\\tools\\k6\\k6-browser\\k6.exe'
$k6Fallback = '.\\tools\\k6\\k6-v1.4.2-windows-amd64\\k6.exe'

$k6 = $null
if (Test-Path $k6Preferred) {
  $k6 = $k6Preferred
} elseif (Test-Path $k6Fallback) {
  $k6 = $k6Fallback
} else {
  throw "k6 not found. Expected either $k6Preferred (recommended for browser E2E) or $k6Fallback"
}

if (-not $OutDir) {
  $OutDir = Join-Path 'perf\\results' ("e2e-browser-" + (New-Timestamp))
}
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$summaryPath = Join-Path $OutDir 'k6-summary.json'
$consolePath = Join-Path $OutDir 'k6-console.txt'
${k6Version} = ''

# Env wiring
$env:UI_BASE_URL = $UiBaseUrl
$env:BASE_URL = $ApiBaseUrl
$env:UI_STAGES = $UiStages
$env:BROWSER_PATH = $BrowserPath
$env:K6_BROWSER_PATH = $BrowserPath
$env:HEADLESS = if ($ShowBrowser) { '0' } else { '1' }

# Tip: if your nginx forces https, use IPv6 loopback base url: http://[::1]
"UI_BASE_URL=$($env:UI_BASE_URL)" | Out-File -Encoding UTF8 $consolePath
"BASE_URL=$($env:BASE_URL)" | Out-File -Encoding UTF8 -Append $consolePath
"UI_STAGES=$($env:UI_STAGES)" | Out-File -Encoding UTF8 -Append $consolePath
"BROWSER_PATH=$($env:BROWSER_PATH)" | Out-File -Encoding UTF8 -Append $consolePath
"HEADLESS=$($env:HEADLESS)" | Out-File -Encoding UTF8 -Append $consolePath
"K6_BIN=$k6" | Out-File -Encoding UTF8 -Append $consolePath
"BROWSER_PATH exists=$([bool](Test-Path ($BrowserPath -replace '/','\\')))" | Out-File -Encoding UTF8 -Append $consolePath

# Capture k6 version for report/debugging
try {
  ${k6Version} = (& $k6 version 2>&1 | Out-String).Trim()
  if (${k6Version}) {
    ("K6_VERSION={0}" -f ${k6Version}) | Out-File -Encoding UTF8 -Append $consolePath
  }
} catch {
  # ignore
}

# Run
$exit = 0
${k6Output} = ''
try {
  ${k6Output} = (& $k6 run $Script --summary-export $summaryPath 2>&1 | Out-String)
  ${k6Output} | Tee-Object -FilePath $consolePath -Append
  $exit = $LASTEXITCODE
} catch {
  $exit = $LASTEXITCODE
  "k6 threw a terminating error (exit=$exit)." | Out-File -Encoding UTF8 -Append $consolePath
}
"k6 exit=$exit" | Out-File -Encoding UTF8 -Append $consolePath

if (!(Test-Path $summaryPath)) {
  throw "summary missing: $summaryPath"
}

# Minimal report
$reportMd = Join-Path $OutDir 'report.md'
$md = @()
$md += '# Browser E2E performance report'
$md += ''
$md += ('Output dir: `{0}`' -f $OutDir)
$md += ''
$md += '## Inputs'
$md += ''
$md += ('- UI_BASE_URL: `{0}`' -f $env:UI_BASE_URL)
$md += ('- BASE_URL: `{0}`' -f $env:BASE_URL)
$md += ('- UI_STAGES: `{0}`' -f $env:UI_STAGES)
$md += ('- BROWSER_PATH: `{0}`' -f $env:BROWSER_PATH)
$md += ('- HEADLESS: `{0}`' -f $env:HEADLESS)
$md += ('- K6_BIN: `{0}`' -f $k6)
$k6VersionLine = 'unknown'
if ($k6Version) { $k6VersionLine = $k6Version }
$md += ('- K6_VERSION: `{0}`' -f $k6VersionLine)
$md += ''
$md += '## Notes'
$md += ''
$md += '- This run records step timings in `ui_step_duration_ms{step=...}`.'
$md += '- If k6 says it can''t find a browser executable, set `-BrowserPath` to your Edge/Chrome path.'
$md += '- If it still fails on the repo-bundled k6, put a newer k6 at `tools/k6/k6-browser/k6.exe` (runner prefers it).'
$md += ''
$md += '## Last error excerpt (best effort)'
$md += ''
if (${k6Output}) {
  $lines = ${k6Output} -split "`r?`n"
  $tail = $lines | Select-Object -Last 40
  $md += '```'
  $md += ($tail -join "`n")
  $md += '```'
} else {
  $md += '_No captured output (see `k6-console.txt`)._'
}
$md += ''
$md += '## Artifacts'
$md += ''
$md += '- `k6-summary.json`'
$md += '- `k6-console.txt`'
$md -join "`n" | Out-File -Encoding UTF8 $reportMd

"Generated: $reportMd";
"Generated: $summaryPath";
"Console: $consolePath";
