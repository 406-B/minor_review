param(
  # Total wall-clock budget for the whole limit test.
  [int]$Hours = 6,

  # VU ladder settings.
  [int]$StartVUs = 20,
  [int]$StepVUs = 10,
  [int]$MaxVUs = 300,

  # Per-step duration (seconds). Total steps ~= Hours*3600 / StepSeconds.
  [int]$StepSeconds = 360,

  # How many consecutive failing steps before we declare the system unstable.
  [int]$FailStreakStop = 2,

  # Where to send traffic.
  [string]$BaseUrl = "http://[::1]",

  # k6 executable path (auto-detected when empty).
  [string]$K6Path = "",

  # Path to main script.
  [string]$ScriptPath = ".\\perf\\k6\\api-core-stages.js",

  # Use pressure thresholds profile (p95 tolerant). Recommended for limit tests.
  [switch]$PressureMode,

  # Disable pressure mode (use stricter thresholds). Useful for dry-runs.
  [switch]$NoPressureMode,

  # Skip auto-register (recommended for repeatability).
  [switch]$SkipRegister,

  # Disable skip-register.
  [switch]$NoSkipRegister,

  # Optional: bias traffic to read-heavy during limit tests.
  [string]$FlowWeights = '{"A":85,"B":10,"C":3,"D":2}',

  # Stop conditions (strict only)
  [double]$MaxStrictFailRate = 0.01,
  [int]$MaxStrictP95Ms = 5000,
  [int]$MaxFlowAP95Ms = 5000,
  [int]$MaxFlowBP95Ms = 5000,

  # Additional availability guards
  [double]$MinChecksRate = 0.98,
  [double]$MinRps = 0.1
)

$ErrorActionPreference = 'Stop'

# Defaults: keep unattended test stable and repeatable.
# - PressureMode: use tolerant thresholds (PERF_PRESSURE=1)
# - SkipRegister: avoid repeated register attempts
if (-not $PSBoundParameters.ContainsKey('PressureMode') -and -not $PSBoundParameters.ContainsKey('NoPressureMode')) {
  $PressureMode = $true
}
if ($NoPressureMode) { $PressureMode = $false }

if (-not $PSBoundParameters.ContainsKey('SkipRegister') -and -not $PSBoundParameters.ContainsKey('NoSkipRegister')) {
  $SkipRegister = $true
}
if ($NoSkipRegister) { $SkipRegister = $false }

function Find-K6([string]$Explicit) {
  if ($Explicit -and (Test-Path $Explicit)) { return (Resolve-Path $Explicit).Path }

  $candidates = @(
    '.\\tools\\k6\\k6-v1.4.2-windows-amd64\\k6.exe',
    '.\\tools\\k6\\windows\\amd64\\k6-v1.4.2-windows-amd64\\k6.exe'
  )
  foreach ($c in $candidates) {
    if (Test-Path $c) { return (Resolve-Path $c).Path }
  }

  $found = Get-ChildItem -Path . -Recurse -Filter k6.exe -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName
  if ($found) { return $found }

  throw "k6.exe not found. Provide -K6Path or ensure tools/k6 contains it."
}

function New-RunDir() {
  $ts = Get-Date -Format 'yyyyMMdd-HHmmss'
  $dir = Join-Path (Resolve-Path '.').Path ("perf\\results\\limit-$ts")
  New-Item -ItemType Directory -Force -Path $dir | Out-Null
  return $dir
}

function Parse-Summary([string]$summaryPath) {
  $json = Get-Content -Raw -Path $summaryPath | ConvertFrom-Json

  $metrics = $json.metrics
  $out = [ordered]@{}

  function Get-Rate([string]$name) {
    if (-not $metrics.PSObject.Properties.Name.Contains($name)) { return $null }
    $m = $metrics.$name
    if ($m -and $m.values -and $m.values.rate -ne $null) { return [double]$m.values.rate }
    return $null
  }

  function Get-P95Ms([string]$name) {
    if (-not $metrics.PSObject.Properties.Name.Contains($name)) { return $null }
    $m = $metrics.$name
    if ($m -and $m.values -and $m.values."p(95)" -ne $null) { return [int]([double]$m.values."p(95)") }
    return $null
  }

  $out.strictFailRate = Get-Rate 'http_req_failed{expected_response:true}'
  $out.strictP95Ms = Get-P95Ms 'http_req_duration{expected_response:true}'
  $out.flowAP95Ms = Get-P95Ms 'http_req_duration{expected_response:true,flow:A}'
  $out.flowBP95Ms = Get-P95Ms 'http_req_duration{expected_response:true,flow:B}'

  # Throughput
  if ($metrics.PSObject.Properties.Name.Contains('http_reqs')) {
    $out.rps = [double]$metrics.http_reqs.values.rate
  } else {
    $out.rps = $null
  }

  # Checks
  if ($metrics.PSObject.Properties.Name.Contains('checks')) {
    $out.checksRate = [double]$metrics.checks.values.rate
  } else {
    $out.checksRate = $null
  }

  return $out
}

function Should-Stop($parsed) {
  $reasons = @()

  if ($parsed.checksRate -ne $null -and $parsed.checksRate -lt $MinChecksRate) {
    $reasons += ("checks rate {0:P2} < {1:P2}" -f $parsed.checksRate, $MinChecksRate)
  }

  # If summary exists but throughput is basically zero, it usually indicates hard failure / no traffic.
  if ($parsed.rps -ne $null -and $parsed.rps -lt $MinRps) {
    $reasons += ("rps {0:N2} < {1:N2} (no effective traffic)" -f $parsed.rps, $MinRps)
  }

  if ($parsed.strictFailRate -ne $null -and $parsed.strictFailRate -gt $MaxStrictFailRate) {
    $reasons += ("strict fail rate {0:P2} > {1:P2}" -f $parsed.strictFailRate, $MaxStrictFailRate)
  }

  if ($parsed.strictP95Ms -ne $null -and $parsed.strictP95Ms -gt $MaxStrictP95Ms) {
    $reasons += ("global strict p95 {0}ms > {1}ms" -f $parsed.strictP95Ms, $MaxStrictP95Ms)
  }

  if ($parsed.flowAP95Ms -ne $null -and $parsed.flowAP95Ms -gt $MaxFlowAP95Ms) {
    $reasons += ("flow A strict p95 {0}ms > {1}ms" -f $parsed.flowAP95Ms, $MaxFlowAP95Ms)
  }

  if ($parsed.flowBP95Ms -ne $null -and $parsed.flowBP95Ms -gt $MaxFlowBP95Ms) {
    $reasons += ("flow B strict p95 {0}ms > {1}ms" -f $parsed.flowBP95Ms, $MaxFlowBP95Ms)
  }

  return @{ hasStop = ($reasons.Count -gt 0); reasons = $reasons }
}

function Classify-K6Failure([string]$stderrPath, [int]$exitCode) {
  if ($exitCode -eq 0) { return $null }
  if (-not (Test-Path $stderrPath)) { return "k6 exit code $exitCode (no stderr)" }

  $tail = (Get-Content -LiteralPath $stderrPath -ErrorAction SilentlyContinue | Select-Object -Last 80) -join "`n"

  if ($tail -match 'thresholds on metrics' -or $tail -match 'thresholds have been crossed') {
    return "k6 thresholds crossed (exit=$exitCode)"
  }
  if ($tail -match 'request timeout' -or $tail -match 'timeout') {
    return "k6 request timeout(s) observed (exit=$exitCode)"
  }

  return "k6 exit code $exitCode (unknown)"
}

$repoRoot = (Resolve-Path '.').Path
$k6 = Find-K6 $K6Path
$runDir = New-RunDir
$deadline = (Get-Date).AddHours($Hours)
$forceOneStep = ($Hours -le 0)

$results = @()
$failStreak = 0
$lastStable = $null

Write-Host "Limit test run dir: $runDir"
Write-Host "k6: $k6"
Write-Host "Budget: $Hours hours (until $deadline)"

$vu = $StartVUs
$step = 1

while ( ($forceOneStep -or (Get-Date) -lt $deadline) -and $vu -le $MaxVUs) {
  $dur = "${StepSeconds}s"
  $stages = "${dur}:${vu},${dur}:0"

  $summaryPath = Join-Path $runDir ("step-{0:D3}-vus-{1}.summary.json" -f $step, $vu)
  $consolePath = Join-Path $runDir ("step-{0:D3}-vus-{1}.console.txt" -f $step, $vu)
  $stdoutPath = Join-Path $runDir ("step-{0:D3}-vus-{1}.stdout.txt" -f $step, $vu)
  $stderrPath = Join-Path $runDir ("step-{0:D3}-vus-{1}.stderr.txt" -f $step, $vu)

  # Prepare env for this step
  $env:BASE_URL = $BaseUrl
  if ($SkipRegister) { $env:REGISTER_USER = '0' }
  if ($PressureMode) { $env:PERF_PRESSURE = '1' } else { $env:PERF_PRESSURE = '0' }
  if ($FlowWeights) { $env:FLOW_WEIGHTS = $FlowWeights }
  $env:STAGES = $stages

  Write-Host ("\n[Step {0}] VUs={1} Stages={2}" -f $step, $vu, $stages)

  # Run k6 in a separate process and redirect stdout/stderr to file.
  # This avoids VS Code integrated terminal renderer overhead and prevents NativeCommandError
  # from aborting the whole runner when k6 exits non-zero (e.g. thresholds crossed).
  $exitCode = 0
  $args = @('run', $ScriptPath, '--summary-export', $summaryPath)
  $p = Start-Process -FilePath $k6 -ArgumentList $args -NoNewWindow -Wait -PassThru -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath
  $exitCode = [int]$p.ExitCode

  # Merge stdout/stderr into a single file for easy reading.
  # (Start-Process does not allow RedirectStandardOutput and RedirectStandardError to be the same path.)
  if (Test-Path $consolePath) { Remove-Item -Force $consolePath -ErrorAction SilentlyContinue }
  if (Test-Path $stdoutPath) { Get-Content -LiteralPath $stdoutPath -ErrorAction SilentlyContinue | Out-File -LiteralPath $consolePath -Encoding utf8 }
  if (Test-Path $stderrPath) { Get-Content -LiteralPath $stderrPath -ErrorAction SilentlyContinue | Out-File -LiteralPath $consolePath -Encoding utf8 -Append }

  if ($forceOneStep) { $deadline = Get-Date } # ensure single step when Hours<=0

  $parsed = $null
  $stop = $null
  $k6Failure = Classify-K6Failure $stderrPath $exitCode
  if (Test-Path $summaryPath) {
    $parsed = Parse-Summary $summaryPath
    $stop = Should-Stop $parsed
  } else {
    # If k6 died before writing summary, force a stop reason.
    $parsed = @{ strictFailRate = $null; strictP95Ms = $null; flowAP95Ms = $null; flowBP95Ms = $null; rps = $null; checksRate = $null }
    $stop = @{ hasStop = $true; reasons = @("missing summary export ($k6Failure)") }
  }

  # If k6 exits non-zero (e.g. thresholds crossed), treat it as a stop reason for this step.
  # We still rely on parsed metrics to decide (when summary exists), but exit code is a strong signal.
  if ($exitCode -ne 0 -and $stop -and -not $stop.hasStop) {
    $stop = @{ hasStop = $true; reasons = @($k6Failure) }
  } elseif ($exitCode -ne 0 -and $stop -and $stop.hasStop) {
    $stop.reasons = @($stop.reasons + @($k6Failure))
  }

  $row = [ordered]@{
    step = $step
    vus = $vu
    stages = $stages
    k6ExitCode = $exitCode
    rps = $parsed.rps
    strictFailRate = $parsed.strictFailRate
    strictP95Ms = $parsed.strictP95Ms
    flowAP95Ms = $parsed.flowAP95Ms
    flowBP95Ms = $parsed.flowBP95Ms
    ok = (-not $stop.hasStop)
    reasons = ($stop.reasons -join '; ')
    summary = (Split-Path -Leaf $summaryPath)
    console = (Split-Path -Leaf $consolePath)
  }

  $results += (New-Object PSObject -Property $row)

  if ($stop.hasStop) {
    $failStreak++
    Write-Host ("FAIL (streak {0}/{1}): {2}" -f $failStreak, $FailStreakStop, ($stop.reasons -join '; '))
  } else {
    $failStreak = 0
    $lastStable = $row
    Write-Host "OK"
  }

  if ($failStreak -ge $FailStreakStop) {
    Write-Host "\nStopping: reached fail streak threshold."
    break
  }

  $vu += $StepVUs
  $step++
}

# Write report
$reportPath = Join-Path $runDir 'report.md'
$csvPath = Join-Path $runDir 'report.csv'

$results | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8

$maxStableVUs = if ($lastStable) { $lastStable.vus } else { $null }
$nextVUs = if ($lastStable) { $lastStable.vus + $StepVUs } else { $StartVUs }

$lines = @()
$lines += "# k6 Limit Test Report"
$lines += ""
$lines += "- Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
$lines += "- BudgetHours: $Hours"
$lines += "- BaseUrl: $BaseUrl"
$lines += "- Script: $ScriptPath"
$lines += "- PressureMode: $PressureMode (PERF_PRESSURE=$(if($PressureMode){'1'}else{'0'}))"
$lines += "- FlowWeights: $($FlowWeights)"
$lines += "- Ladder: StartVUs=$StartVUs, StepVUs=$StepVUs, MaxVUs=$MaxVUs"
$lines += "- StepSeconds: $StepSeconds"
$lines += "- StopWhen: strictFailRate>$MaxStrictFailRate OR global p95>$MaxStrictP95Ms ms (consecutive $FailStreakStop steps)"
$lines += ""

if ($maxStableVUs -ne $null) {
  $lines += "## Conclusion"
  $lines += ""
  $lines += "- Last stable step: **$maxStableVUs VUs**"
  $lines += "- Next step (first unstable interval start): **$nextVUs VUs**"
  $lines += ""
} else {
  $lines += "## Conclusion"
  $lines += ""
  $lines += "- No stable step found (stop condition triggered from the first step). Consider lowering StartVUs or relaxing stop conditions."
  $lines += ""
}

$lines += "## Step Details"
$lines += ""
$lines += "| step | VUs | RPS | strict fail rate | strict p95(ms) | flow A p95(ms) | flow B p95(ms) | ok | reasons | summary |"
$lines += "|---:|---:|---:|---:|---:|---:|---:|:--:|---|---|"

foreach ($r in $results) {
  $rps = if ($r.rps -ne $null) { [math]::Round([double]$r.rps, 2) } else { '' }
  $fr = if ($r.strictFailRate -ne $null) { [math]::Round([double]$r.strictFailRate, 4) } else { '' }
  $okMark = if ($r.ok) { 'OK' } else { 'FAIL' }
  $lines += "| $($r.step) | $($r.vus) | $rps | $fr | $($r.strictP95Ms) | $($r.flowAP95Ms) | $($r.flowBP95Ms) | $okMark | $($r.reasons) | $($r.summary) |"
}

$lines += ""
$lines += "## Artifacts"
$lines += ""
$lines += "- $($csvPath | Split-Path -Leaf) (open in Excel)"
$lines += "- Step console output: step-*-console.txt"
$lines += "- Step summaries: step-*-summary.json"

Set-Content -Path $reportPath -Value ($lines -join "`n") -Encoding UTF8

Write-Host "`nDone. Report: $reportPath"
Write-Host "CSV: $csvPath"
