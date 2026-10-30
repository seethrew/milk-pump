# Measures the visualiser's CPU over time: runs EngineTest (the 120 BPM pattern, Daxy's real data
# folder and settings, so presets change as they do in Live) and samples every thread's CPU time.
# Prints the average, the 95th percentile and the worst moments, each with the busiest thread, and
# writes every sample to a CSV. CPU is in % of ONE core (100 = one core flat out; 16 threads here).
#   powershell -ExecutionPolicy Bypass -File Tools\cpu-profile.ps1 [-Seconds 90] [-Every 0.25]
# With -Preset: that one preset, locked, in a scratch data folder (as preset-shot.ps1), with -Fps
# and -Mesh overriding the frame cap and mesh size there; Daxy's own settings are not touched.
param([int]$Seconds = 90, [double]$Every = 0.25, [string]$Csv = (Join-Path $env:TEMP 'mdvst-cpu.csv'),
      [string]$Preset, [int]$Fps = 0, [int]$Mesh = 0)
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$exe = Join-Path $root 'build\EngineTest\Release\EngineTest.exe'

if ($Preset) {
    $real = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'Milk Pump'
    $test = Join-Path $env:TEMP 'mdvst-cputest'
    New-Item -ItemType Directory -Force $test | Out-Null
    foreach ($d in 'textures', 'data', 'docs', 'fonts', 'shadercache') {   # shader cache shared: no compile in the numbers
        $link = Join-Path $test $d
        if (Get-Item $link -Force -ErrorAction SilentlyContinue) { cmd /c rmdir "$link" | Out-Null }
        cmd /c mklink /J "$link" "$(Join-Path $real $d)" | Out-Null
    }
    foreach ($f in 'beatdrop_img.ini', 'beatdrop_msg.ini') { Copy-Item -Force (Join-Path $real $f) $test }
    $set = @{ szPresetStartup = (Resolve-Path $Preset).Path; bEnablePresetStartup = '1'; bPresetLockOnAtStartup = '1'
              bShaderPrecachingAtStartup = '0'; bFullscreenOnStartup = '0'; nWindowWidth = '1280'; nWindowHeight = '720' }
    if ($Fps)  { 'max_fps_w', 'max_fps_fs', 'max_fps_dm' | ForEach-Object { $set[$_] = "$Fps" } }
    if ($Mesh) { $set['nMeshSize'] = "$Mesh" }
    $ini = Get-Content (Join-Path $real 'beatdrop.ini') | ForEach-Object {
        $k = ($_ -split '=', 2)[0]; if ($set.ContainsKey($k)) { "$k=$($set[$k])" } else { $_ } }
    Set-Content -Encoding Default (Join-Path $test 'beatdrop.ini') $ini
    $env:MDVST_DATA_DIR = $test
}

$p = Start-Process $exe -WorkingDirectory $env:TEMP -PassThru
if ($Preset) { Remove-Item Env:MDVST_DATA_DIR }
Start-Sleep -Seconds 4 # past start-up (window, shaders of the first preset)
$prev = @{}; $prevTotal = $null; $rows = @()
$clock = [Diagnostics.Stopwatch]::StartNew(); $lastT = 0.0
while ($clock.Elapsed.TotalSeconds -lt $Seconds -and -not $p.HasExited) {
    Start-Sleep -Milliseconds ([int]($Every * 1000))
    $p.Refresh()
    $t = $clock.Elapsed.TotalSeconds; $dt = $t - $lastT; $lastT = $t
    $total = $p.TotalProcessorTime.TotalSeconds
    $busy = $null; $busyCpu = 0.0
    foreach ($th in $p.Threads) {
        try { $c = $th.TotalProcessorTime.TotalSeconds } catch { continue }
        if ($prev.ContainsKey($th.Id)) {
            $d = ($c - $prev[$th.Id]) / $dt * 100
            if ($d -gt $busyCpu) { $busyCpu = $d; $busy = $th.Id }
        }
        $prev[$th.Id] = $c
    }
    if ($null -ne $prevTotal) {
        $rows += [pscustomobject]@{ t = [math]::Round($t, 2); cpu = [math]::Round(($total - $prevTotal) / $dt * 100, 1)
                                    thread = $busy; threadCpu = [math]::Round($busyCpu, 1) }
    }
    $prevTotal = $total
}
if (-not $p.HasExited) { $p.CloseMainWindow() | Out-Null; if (-not $p.WaitForExit(8000)) { $p.Kill() } }

$rows | Export-Csv -NoTypeInformation $Csv
$sorted = $rows.cpu | Sort-Object
"samples {0}, average {1:N1}%, median {2:N1}%, 95th percentile {3:N1}%, worst {4:N1}%  (of one core)" -f `
    $rows.Count, ($rows.cpu | Measure-Object -Average).Average, $sorted[[int]($sorted.Count * 0.5)],
    $sorted[[int]($sorted.Count * 0.95)], $sorted[-1]
'worst moments:'
$rows | Sort-Object cpu -Descending | Select-Object -First 8 | Format-Table -AutoSize | Out-String
"CSV: $Csv"
