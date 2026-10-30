# Builds Milk Pump's two installers into Installer\ (WiX 5, Tools\wix; Daxy, 2026-10-30):
#   Milk Pump <version>.msi      the app, the plugin, and the data folder's essentials
#   Milk Pump Presets.msi        BeatDrop's full preset and texture pack (separate, 1 GB+)
# Uses the Release build as it is (run build.ps1 first; setup.ps1 -WithBeatDrop -WithInstaller
# once). The data is staged fresh (not your own Documents\Milk Pump) in build\installer, or under
# $ScratchRoot from local-settings.ps1.
#   powershell -ExecutionPolicy Bypass -File Installer\build-installer.ps1 [-SkipPresets]
param([switch]$SkipPresets)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$root = Split-Path $PSScriptRoot -Parent
$wix = Join-Path $root 'Tools\wix\wix.exe'
if (-not (Test-Path $wix)) { throw "WiX missing: dotnet tool install wix --version 5.0.2 --tool-path Tools\wix" }

$version = ([regex]'VERSION (\d+\.\d+\.\d+)').Match((Get-Content (Join-Path $root 'Source\Plugin\CMakeLists.txt') -Raw)).Groups[1].Value
$appDir = Join-Path $root 'build\App\Release'
$pluginDir = Join-Path $root 'build\Source\Plugin\MDVST_Plugin_artefacts\Release\VST3\Milk Pump.vst3'
foreach ($p in "$appDir\Milk Pump.exe", $pluginDir) { if (-not (Test-Path $p)) { throw "Not built: $p (run build.ps1)" } }
$ScratchRoot = $null   # local-settings.ps1 (this PC's own, not published) may set it
if (Test-Path (Join-Path $root 'local-settings.ps1')) { . (Join-Path $root 'local-settings.ps1') }
$scratch = if ($ScratchRoot) { Join-Path $ScratchRoot 'installer' } else { Join-Path $root 'build\installer' }
Write-Host "Milk Pump $version; staging in $scratch"

function Fresh($dir) { if (Test-Path $dir) { Remove-Item -Recurse -Force $dir }; New-Item -ItemType Directory -Force $dir | Out-Null; $dir }
function Copy-Tree($from, $to) {
    robocopy $from $to /E /NFL /NDL /NJH /NJS /NP | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "Copy failed: $from (robocopy $LASTEXITCODE)" }
}

# The data: the essentials as install-data.ps1 -Pack Light makes them, and the big pack less
# anything the essentials already hold.
$dataMain = Fresh (Join-Path $scratch 'data-main')
& (Join-Path $root 'install-data.ps1') -Pack Light -Target $dataMain
# No shader precache on the first start: it found nothing to do and said so on screen
# ("Precached 0 shaders"). Shaders compile as presets load, as on Daxy's own setup.
$ini = Join-Path $dataMain 'beatdrop.ini'
$lines = [IO.File]::ReadAllLines($ini, [Text.Encoding]::Default) -replace '^bNeedsShaderReprecacheAtStartup=1$', 'bNeedsShaderReprecacheAtStartup=0'
[IO.File]::WriteAllLines($ini, $lines, [Text.Encoding]::Default)
$dataPresets = Join-Path $scratch 'data-presets'
if (-not $SkipPresets) {
    $dataPresets = Fresh $dataPresets
    $full = Join-Path $root 'Reference\BeatDrop\resources\Milkdrop2'
    Write-Host 'Staging the full pack...'
    Copy-Tree "$full\presets" "$dataPresets\presets"
    Copy-Tree "$full\textures" "$dataPresets\textures"
    $dupes = Get-ChildItem $dataPresets -Recurse -File | Where-Object { Test-Path -LiteralPath (Join-Path $dataMain $_.FullName.Substring($dataPresets.Length + 1)) }
    $dupes | Remove-Item -Force
    Write-Host "  $($dupes.Count) files left to the main installer"
}

# Licences and credits, into Program Files\Milk Pump\Licences.
$lic = Fresh (Join-Path $scratch 'licences')
# Everything in Licences\ (third-party texts and Milk Pump's own), and the overview files.
Copy-Item (Join-Path $root 'Licences\*') $lic
Copy-Item (Join-Path $root 'LICENSE.md'), (Join-Path $root 'THIRD-PARTY-NOTICES.md') $lic
Copy-Item (Join-Path $root 'Fonts\FONT_ATTRIBUTION.txt'), (Join-Path $root 'Fonts\FONT_LICENSE_CC-BY-SA-4.0.txt') $lic
$credits = @(
    "Milk Pump $version (beta), by seethrew. Free software: free to use, change and share, never to be sold.",
    '',
    'The MilkDrop 2 visualiser, as an app and a VST3 plugin. Built on:',
    '- BeatDrop (github.com/OfficialIncubo/BeatDrop-Music-Visualizer), BSD 3-Clause.',
    '- MilkDrop3 3.12 (github.com/milkdrop2077/MilkDrop3), BSD 3-Clause.',
    '- MilkDrop 2 by Ryan Geiss / Nullsoft, BSD 3-Clause.',
    '- projectM-eval (the preset expression compiler), MIT.',
    '- JUCE 8 (the plugin), AGPL v3; the VST3 SDK, MIT; Spout, BSD 2-Clause; D3DX9, Microsoft redistributable.',
    '- Fonts: 04b_30 by 04 (the logo); Ac437 EagleSpCGA Alt2 by VileR, CC BY-SA 4.0 (on-screen text).',
    '- Some bundled presets are CC BY-NC-SA 3.0: not for commercial use.',
    '',
    'Milk Pump itself: the engine and the app are BSD 3-Clause, the plugin is GNU AGPL v3 (it is built',
    'with JUCE). The full licence texts are in Program Files\Milk Pump\Licences.')
[IO.File]::WriteAllLines("$lic\CREDITS.txt", $credits)

# The licence page the installer shows: the credits, as RTF.
$rtf = Join-Path $scratch 'credits.rtf'
$body = ($credits | ForEach-Object { ($_ -replace '\\', '\\' -replace '\{', '\{' -replace '\}', '\}') + '\par' }) -join "`r`n"
[IO.File]::WriteAllText($rtf, "{\rtf1\ansi\deff0{\fonttbl{\f0 Segoe UI;}}\fs18`r`n$body`r`n}", [Text.Encoding]::ASCII)

# The installer's pictures: the icon on black at the left of the first page, small in the banner.
$icon = Join-Path $root 'Source\App\milkpump.ico'
$big = [Drawing.Image]::FromFile((Join-Path $root 'Icons\milkpump-128.png'))
$small = [Drawing.Image]::FromFile((Join-Path $root 'Icons\milkpump-48.png'))
$dialog = New-Object Drawing.Bitmap 493, 312
$g = [Drawing.Graphics]::FromImage($dialog); $g.Clear([Drawing.Color]::White)
$g.FillRectangle([Drawing.Brushes]::Black, 0, 0, 164, 312); $g.DrawImage($big, 18, 92, 128, 128); $g.Dispose()
$dialogBmp = Join-Path $scratch 'dialog.bmp'; $dialog.Save($dialogBmp, [Drawing.Imaging.ImageFormat]::Bmp); $dialog.Dispose()
$banner = New-Object Drawing.Bitmap 493, 58
$g = [Drawing.Graphics]::FromImage($banner); $g.Clear([Drawing.Color]::White); $g.DrawImage($small, 437, 5, 48, 48); $g.Dispose()
$bannerBmp = Join-Path $scratch 'banner.bmp'; $banner.Save($bannerBmp, [Drawing.Imaging.ImageFormat]::Bmp); $banner.Dispose()
$big.Dispose(); $small.Dispose()

# WiX's dialog extension, kept beside this script (Installer\.wix), not machine-wide.
Push-Location $PSScriptRoot
try {
    if (-not (Test-Path '.wix\extensions\WixToolset.UI.wixext')) { & $wix extension add WixToolset.UI.wixext/5.0.2; if ($LASTEXITCODE) { throw 'wix extension add failed' } }
    $common = @('-arch', 'x64', '-ext', 'WixToolset.UI.wixext', '-d', "IconFile=$icon", '-d', "LicenseRtf=$rtf",
                '-d', "DialogBmp=$dialogBmp", '-d', "BannerBmp=$bannerBmp", '-intermediatefolder', (Join-Path $scratch 'obj'))
    $main = Join-Path $PSScriptRoot "Milk Pump $version.msi"
    & $wix build MilkPump.wxs @common -d "Version=$version" -d "AppDir=$appDir" -d "PluginDir=$pluginDir" -d "LicenceDir=$lic" -d "DataDir=$dataMain" -d "ReadmeFile=$(Join-Path $root 'Docs\Milk Pump README.txt')" -o $main
    if ($LASTEXITCODE) { throw 'wix build failed (Milk Pump)' }
    Write-Host ("{0}  ({1:N0} MB)" -f $main, ((Get-Item $main).Length / 1MB))
    if (-not $SkipPresets) {
        $presets = Join-Path $PSScriptRoot 'Milk Pump Presets.msi'
        Write-Host 'Building the presets installer (a few minutes)...'
        & $wix build MilkPumpPresets.wxs @common -d 'Version=1.0.2' -d "DataDir=$dataPresets" -o $presets
        if ($LASTEXITCODE) { throw 'wix build failed (Presets)' }
        Write-Host ("{0}  ({1:N0} MB)" -f $presets, ((Get-Item $presets).Length / 1MB))
    }
}
finally { Pop-Location }
Get-ChildItem $PSScriptRoot -Filter *.wixpdb | Remove-Item -Force
