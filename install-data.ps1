# Fills the data folder, Documents\Milk Pump\, which the plugin (and EngineTest) read presets,
# textures and settings from (Source\Engine\mdvst_paths.h). Adds what is missing and never
# overwrites or deletes anything already there: your settings, presets you added or edited, and
# the shader cache all survive running it again.
#
#   -Pack Full   BeatDrop's full pack: 11,745 presets in their own folders + 1.2 GB of textures,
#                plus the 574-preset light set (about 1.4 GB). The default.
#   -Pack Light  just the 574 presets and their 2 MB of textures.
#
#   -Target DIR  fill DIR instead of Documents\Milk Pump (the installer's clean copy,
#                Installer\build-installer.ps1); the old-folder move is skipped.
#
# Usage:  powershell -ExecutionPolicy Bypass -File install-data.ps1 [-Pack Full|Light]
param([ValidateSet('Full', 'Light')] [string]$Pack = 'Full', [string]$Target)
$ErrorActionPreference = 'Stop'

$root  = $PSScriptRoot
$docs  = [Environment]::GetFolderPath('MyDocuments')
$data  = if ($Target) { $Target } else { Join-Path $docs 'Milk Pump' }   # MDVST_DATA_FOLDER_NAME in Source\Engine\mdvst_paths.h
$full  = Join-Path $root 'Reference\BeatDrop\resources'                     # read only; setup.ps1 -WithBeatDrop
$light = Join-Path $root 'Reference\BeatDrop\BeatDrop\BeatDrop Resources'   # the 574-preset light set

function Add-Missing([string]$from, [string]$to, [string[]]$files) {
    # /XC /XN /XO: skip every file that already exists at the destination, whatever its date.
    # Whole folders recurse (/E); named files are copied from the top level only.
    [string[]]$what = if ($files) { $files } else { '/E' }
    robocopy $from $to @what /XC /XN /XO /NFL /NDL /NJH /NJS /NP | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "Copy failed: $from (robocopy $LASTEXITCODE)" }
}

# The rename (2026-10-29): the data folder was Documents\MilkDrop VST. Move it rather than copy
# 1.3 GB, so settings, presets and the shader cache come along.
$old = if ($Target) { Join-Path $data '_no_old_folder_' } else { Join-Path $docs 'MilkDrop VST' }
# A new plugin run before this script makes a near-empty folder (a default .ini, an empty shader
# cache, no presets\): that one gives way to the real one.
if ((Test-Path $old) -and (Test-Path $data) -and -not (Test-Path (Join-Path $data 'presets'))) {
    Remove-Item -Recurse -Force $data
}
if ((Test-Path $old) -and -not (Test-Path $data)) {
    Rename-Item $old 'Milk Pump'
    Write-Host "Moved the data folder: $old -> $data"
}
New-Item -ItemType Directory -Force $data | Out-Null

# Settings: carry over the ones from the Phase 2 install if there are any (Always on top etc.),
# else BeatDrop's defaults. Only when the data folder has none yet.
$phase2 = Join-Path $root 'VST3\MilkDrop VST.vst3\Contents\x86_64-win'
$settingsFrom = if (Test-Path (Join-Path $phase2 'beatdrop.ini')) { $phase2 } else { $full }
Add-Missing $settingsFrom $data @('beatdrop.ini', 'beatdrop_img.ini', 'beatdrop_msg.ini')
Add-Missing $full $data @('precache.txt', 'PRESET LICENSE.md')

foreach ($dir in 'data', 'docs', 'startuppreset') {
    Add-Missing (Join-Path $full "Milkdrop2\$dir") (Join-Path $data $dir)
}
Add-Missing (Join-Path $light 'presets') (Join-Path $data 'presets')
Add-Missing (Join-Path $light 'textures') (Join-Path $data 'textures')
if ($Pack -eq 'Full') {
    Write-Host 'Copying the full pack (about 1.4 GB), a minute or two...'
    Add-Missing (Join-Path $full 'Milkdrop2\presets') (Join-Path $data 'presets')
    Add-Missing (Join-Path $full 'Milkdrop2\textures') (Join-Path $data 'textures')
}

# Our own presets (Presets\ here): kept current, so a newer copy replaces an older one; anything you
# saved under a new name is never touched.
function Update-Ours([string]$from, [string]$to, [string]$files = '*.milk') {
    robocopy $from $to $files /XO /NFL /NDL /NJH /NJS /NP | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "Copy failed: $from (robocopy $LASTEXITCODE)" }
}
Update-Ours (Join-Path $root 'Presets\SwarmSynth\Patches') (Join-Path $data 'presets\seethrew\Patches')
Update-Ours (Join-Path $root 'Presets\SwarmSynth\Modes') (Join-Path $data 'presets\seethrew\Modes')
# Our presets live in presets\seethrew (Daxy's name for his visual projects, 2026-10-30; it was
# presets\SwarmSynth). Game of Life (Daxy's pick of the Life patches) and Pixel Life go in Patches,
# mixed in with the patch presets (Daxy: "that way you can mix them together").
Update-Ours (Join-Path $root 'Presets\SwarmSynth\Life') (Join-Path $data 'presets\seethrew\Patches')
Update-Ours (Join-Path $root 'Presets\PixelLife') (Join-Path $data 'presets\seethrew\Patches')
Update-Ours (Join-Path $root 'Presets\Startup') (Join-Path $data 'startuppreset')
Update-Ours (Join-Path $root 'Presets\Textures') (Join-Path $data 'textures') '*.png'   # the logo, the Life patches' pictures
Update-Ours (Join-Path $root 'Docs') $data 'Milk Pump README.txt'   # the readme, beside the presets
Update-Ours (Join-Path $root 'Fonts') (Join-Path $data 'fonts') '*.ttf'   # usable by name, this process only

# The opening screen: our logo screen. Only while the setting still names BeatDrop's logo or our
# earlier stand-in, so a startup preset you chose yourself stays. The ini is plain text (no BOM), as the engine writes it.
$ini = Join-Path $data 'beatdrop.ini'
$ours = 'szPresetStartup=startuppreset\Milk Pump Startup.milk'
$lines = [IO.File]::ReadAllLines($ini, [Text.Encoding]::Default)
if ($lines -match '^szPresetStartup=.*(BeatDrop Music Visualizer Startup Preset|MilkDrop VST Startup)\.milk$') {
    $lines = $lines -replace '^szPresetStartup=.*$', $ours
    [IO.File]::WriteAllLines($ini, $lines, [Text.Encoding]::Default)
    Write-Host 'Opening screen: Milk Pump Startup'
}

# All on-screen text in SwarmSynth's pixel font, Ac437 EagleSpCGA Alt2 (fonts\). An 8 x 8 grid, so
# sizes are multiples of 8 (16 px = 2 screen pixels a font pixel), crisp with smoothing off.
# Fonts: 0 menus and the preset browser, 1 "Press F1", preset name, rating, FPS, 2 the help page,
# 3 playlist, 4 tooltips, 5 song titles. Each only while it is still one of BeatDrop's defaults,
# so a font you choose yourself stays.
$sizes = @{ 0 = 16; 1 = 24; 2 = 16; 3 = 16; 4 = 16; 5 = 24 }
$lines = [string[]][IO.File]::ReadAllLines($ini, [Text.Encoding]::Default)
$changed = 0
foreach ($i in $sizes.Keys) {
    if (-not ($lines -match "^szFontFace$i=(Courier|Times New Roman|Arial)$")) { continue }
    $set = @{ "szFontFace$i" = 'Ac437 EagleSpCGA Alt2'; "nFontSize$i" = "$($sizes[$i])"
              "bFontItalic$i" = '0'; "bFontBold$i" = '0'; "bFontAA$i" = '0' }
    $lines = [string[]]($lines | ForEach-Object { $k = ($_ -split '=', 2)[0]; if ($set.ContainsKey($k)) { "$k=$($set[$k])" } else { $_ } })
    $changed++
}
if ($changed) {
    [IO.File]::WriteAllLines($ini, $lines, [Text.Encoding]::Default)
    Write-Host "On-screen text: Ac437 EagleSpCGA Alt2 (SwarmSynth), $changed fonts"
}

$presets = (Get-ChildItem (Join-Path $data 'presets') -Recurse -File -Include '*.milk', '*.milk2').Count
$mb = [math]::Round(((Get-ChildItem $data -Recurse -File | Measure-Object Length -Sum).Sum) / 1MB)
Write-Host "Data folder ($Pack): $data  ($presets presets, $mb MB)"
