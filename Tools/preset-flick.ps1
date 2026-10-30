# Stress test: flicks through presets as fast as a person hammering the keys (Daxy crashed an
# earlier build once doing that, 2026-10-30). EngineTest runs on a scratch data folder whose
# presets, textures etc. are junctions to the real ones (read only use: only H and Space are
# sent, hard and soft cut to the next preset, never a key that saves, renames or deletes) and
# gets one every -Every ms for -Seconds. A crash's stack lands in EngineTest-cycle.log there.
#   powershell -ExecutionPolicy Bypass -File Tools\preset-flick.ps1 [-Seconds 120] [-Every 80] [-Config RelWithDebInfo]
# Before deleting %TEMP%\mdvst-flicktest: rmdir its junctions first (CLAUDE.md, old builds).
param([int]$Seconds = 120, [int]$Every = 80,
      [ValidateSet('Release', 'RelWithDebInfo', 'Debug')] [string]$Config = 'RelWithDebInfo')
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$exe  = Join-Path $root "build\EngineTest\$Config\EngineTest.exe"
$real = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'Milk Pump'
$test = Join-Path $env:TEMP 'mdvst-flicktest'
New-Item -ItemType Directory -Force $test | Out-Null
foreach ($d in 'presets', 'textures', 'data', 'docs', 'fonts', 'startuppreset') {
    $link = Join-Path $test $d
    if (Get-Item $link -Force -ErrorAction SilentlyContinue) { cmd /c rmdir "$link" | Out-Null }
    cmd /c mklink /J "$link" "$(Join-Path $real $d)" | Out-Null
}
foreach ($f in 'beatdrop_img.ini', 'beatdrop_msg.ini') { Copy-Item -Force (Join-Path $real $f) $test }
$ini = Get-Content (Join-Path $real 'beatdrop.ini')
$set = @{ szPresetDir = "$test\presets\"; bPresetLockOnAtStartup = '0'; bShaderPrecachingAtStartup = '0'
          bShowSongTitle = '0'; bFullscreenOnStartup = '0'; nWindowWidth = '960'; nWindowHeight = '540' }
$ini = $ini | ForEach-Object { $k = ($_ -split '=', 2)[0]; if ($set.ContainsKey($k)) { "$k=$($set[$k])" } else { $_ } }
Set-Content -Encoding Unicode (Join-Path $test 'beatdrop.ini') $ini
Remove-Item (Join-Path $test 'EngineTest-cycle.log') -ErrorAction SilentlyContinue

Add-Type @'
using System; using System.Runtime.InteropServices;
public static class Keys { [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint m, IntPtr w, IntPtr l); }
'@
$env:MDVST_DATA_DIR = $test
$p = Start-Process $exe -WorkingDirectory $test -PassThru
$sent = 0
try {
    Start-Sleep 4
    $p.Refresh(); $h = $p.MainWindowHandle
    $end = (Get-Date).AddSeconds($Seconds)
    while ((Get-Date) -lt $end -and -not $p.HasExited) {
        $key = if ($sent % 5 -eq 4) { [char]' ' } else { [char]'H' }
        [Keys]::PostMessage($h, 0x102, [IntPtr][int]$key, [IntPtr]::Zero) | Out-Null   # WM_CHAR
        $sent++
        Start-Sleep -Milliseconds $Every
        $p.Refresh()
    }
    $alive = -not $p.HasExited
    "{0} key presses over {1} s; EngineTest {2}" -f $sent, $Seconds, $(if ($alive) { 'still running' } else { "CRASHED (exit 0x{0:X8})" -f $p.ExitCode })
} finally {
    if (-not $p.HasExited) { $p.CloseMainWindow() | Out-Null; if (-not $p.WaitForExit(8000)) { $p.Kill() } }
    Remove-Item Env:MDVST_DATA_DIR
}
$log = Join-Path $test 'EngineTest-cycle.log'
if (Test-Path $log) { "--- $log"; Get-Content $log }
