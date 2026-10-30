# Renders one preset and saves screenshots of it: EngineTest (its 120 BPM pattern) runs on a scratch
# data folder whose startup preset is the one given, locked, and the visualiser window is grabbed
# a few times. For checking presets we write (Presets\) without touching Daxy's own settings.
#   powershell -ExecutionPolicy Bypass -File Tools\preset-shot.ps1 -Preset <file.milk> [-Out <dir>] [-Shots 3]
param(
    [Parameter(Mandatory)] [string]$Preset,
    [string]$Out = (Join-Path $env:TEMP 'mdvst-presetshots'),
    [int]$Shots = 3,
    [double]$Every = 2.5,
    [double]$Speed = 1.0,  # the plugin's Speed control
    [double]$Wait = 4,     # seconds before the first shot
    [ValidateSet('Release', 'RelWithDebInfo', 'Debug')] [string]$Config = 'Release'  # RelWithDebInfo: crash stacks with names
)
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$exe  = Join-Path $root "build\EngineTest\$Config\EngineTest.exe"   # a crash's stack: EngineTest-cycle.log in %TEMP%\mdvst-presettest
$real = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'Milk Pump'
$test = Join-Path $env:TEMP 'mdvst-presettest'
$Preset = (Resolve-Path $Preset).Path

# Scratch data folder: textures etc. linked to the real ones (read only use), own .ini files.
New-Item -ItemType Directory -Force $test, $Out | Out-Null
# Never presets\: the test window can take keyboard focus, and BeatDrop's load menu can save,
# rename and delete preset files.
# Relinked every run, so they follow the data folder if it moves. rmdir on a junction removes only the
# link, never what it points at.
foreach ($d in 'textures', 'data', 'docs') {
    $link = Join-Path $test $d
    if (Get-Item $link -Force -ErrorAction SilentlyContinue) { cmd /c rmdir "$link" | Out-Null }   # Test-Path misses a broken link
    cmd /c mklink /J "$link" "$(Join-Path $real $d)" | Out-Null
}
foreach ($f in 'beatdrop_img.ini', 'beatdrop_msg.ini') { Copy-Item -Force (Join-Path $real $f) $test }
$ini = Get-Content (Join-Path $real 'beatdrop.ini')
$set = @{ szPresetStartup = $Preset; bEnablePresetStartup = '1'; bPresetLockOnAtStartup = '1'
          bShaderPrecachingAtStartup = '0'; bShowSongTitle = '0'; bFullscreenOnStartup = '0'
          nWindowWidth = '960'; nWindowHeight = '540' }
$ini = $ini | ForEach-Object { $k = ($_ -split '=', 2)[0]; if ($set.ContainsKey($k)) { "$k=$($set[$k])" } else { $_ } }
Set-Content -Encoding Unicode (Join-Path $test 'beatdrop.ini') $ini

Add-Type -ReferencedAssemblies System.Drawing @'
using System; using System.Drawing; using System.Drawing.Imaging; using System.Runtime.InteropServices;
public static class Grab {
    [DllImport("user32.dll")] static extern bool GetClientRect(IntPtr h, out RECT r);
    [DllImport("user32.dll")] static extern bool PrintWindow(IntPtr h, IntPtr dc, uint flags);
    public struct RECT { public int L, T, R, B; }
    public static void Save(IntPtr h, string path) {
        RECT r; GetClientRect(h, out r);
        using (var bmp = new Bitmap(Math.Max(1, r.R - r.L), Math.Max(1, r.B - r.T)))
        using (var g = Graphics.FromImage(bmp)) {
            IntPtr dc = g.GetHdc(); PrintWindow(h, dc, 3); g.ReleaseHdc(dc); // client area, full content
            bmp.Save(path, ImageFormat.Png);
        }
    }
}
'@

$env:MDVST_DATA_DIR = $test
$p = Start-Process $exe -ArgumentList "speed=$Speed" -WorkingDirectory $test -PassThru
try {
    $name = [IO.Path]::GetFileNameWithoutExtension($Preset) -replace '[^\w\- ]', '_'
    if ($Speed -ne 1.0) { $name += "-speed$Speed" }
    Start-Sleep -Seconds $Wait
    for ($i = 1; $i -le $Shots; $i++) {
        $p.Refresh()
        if ($p.HasExited) { throw "EngineTest exited (code $($p.ExitCode))" }
        $file = Join-Path $Out "$name-$i.png"
        [Grab]::Save($p.MainWindowHandle, $file)
        Write-Host $file
        Start-Sleep -Milliseconds ([int]($Every * 1000))
    }
} finally {
    if (-not $p.HasExited) { $p.CloseMainWindow() | Out-Null; if (-not $p.WaitForExit(8000)) { $p.Kill() } }
    Remove-Item Env:MDVST_DATA_DIR
}
