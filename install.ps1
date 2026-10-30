# Copies the built plugin into VST3\ in this folder, the folder Live is pointed at (Preferences ->
# Plug-Ins -> VST3 Plug-In Custom Folder). Live loads it from there, so build\ stays free to
# rebuild. The bundle holds only code (the DLL and the two D3DX DLLs); presets, textures and
# settings are in Documents\Milk Pump (install-data.ps1), so the copy is simply mirrored.
# Usage:  powershell -ExecutionPolicy Bypass -File install.ps1 [-Config Release|Debug|RelWithDebInfo]
# "being used by another process" = Live still has the plugin loaded: close the set or Live first.
param([ValidateSet('Release', 'Debug', 'RelWithDebInfo')] [string]$Config = 'Release')
$ErrorActionPreference = 'Stop'

$bundleName = 'Milk Pump.vst3'
$from = Join-Path $PSScriptRoot "build\Source\Plugin\MDVST_Plugin_artefacts\$Config\VST3\$bundleName"
$to   = Join-Path $PSScriptRoot "VST3\$bundleName"
if (-not (Test-Path $from)) { throw "Not built yet ($Config): run build.ps1 first" }

# Once the installer has put Milk Pump in the standard VST3 folder (Installer\), Live finds it
# there; a second copy here would make two (the same plugin ID: the stale-copy crash of
# 2026-10-29). So this copy goes, and the installed one is updated by rerunning the installer.
$installed = Join-Path ${env:CommonProgramFiles} "VST3\$bundleName"
$skipPlugin = Test-Path $installed
if ($skipPlugin) {
    if (Test-Path $to) { Remove-Item -Recurse -Force $to }
    Write-Host "Milk Pump is installed ($installed): not copied here. Update it with the installer."
}
else {
    robocopy $from $to /MIR /R:2 /W:1 /NFL /NDL /NJH /NJS /NP | Out-Null # /R /W: fail fast if Live holds it
    if ($LASTEXITCODE -ge 8) { throw "Copy failed (robocopy $LASTEXITCODE): is Live still using the plugin?" }
}

# The rename (2026-10-29): the bundle was "MilkDrop VST.vst3". Same plugin codes, so Live sees one
# plugin and old sets find it; the old bundle goes, or Live would list it twice.
$oldBundle = Join-Path $PSScriptRoot 'VST3\MilkDrop VST.vst3'
if (Test-Path $oldBundle) { Remove-Item -Recurse -Force $oldBundle; Write-Host "Removed the old bundle: $oldBundle" }

if (-not $skipPlugin) { Write-Host "Installed ($Config): $to" }

# The Milk Pump app (Milk Pump.exe, reacts to whatever the PC plays) goes to App\ in this folder,
# with a Start menu shortcut. A warning, not a failure, if the app is running. Not once the
# installer has installed it (its own Start menu entry): this shortcut would make a second one.
$appFrom = Join-Path $PSScriptRoot "build\App\$Config"
$appTo = Join-Path $PSScriptRoot 'App'
$devShortcut = Join-Path ([Environment]::GetFolderPath('Programs')) 'Milk Pump.lnk'
if (Test-Path (Join-Path ${env:ProgramFiles} 'Milk Pump\Milk Pump.exe')) {
    if (Test-Path $devShortcut) { Remove-Item -Force $devShortcut }
    Write-Host 'The Milk Pump app is installed (Program Files): App\ not updated. Update it with the installer.'
}
elseif (Test-Path (Join-Path $appFrom 'Milk Pump.exe')) {
    robocopy $appFrom $appTo /MIR /R:2 /W:1 /NFL /NDL /NJH /NJS /NP | Out-Null
    if ($LASTEXITCODE -ge 8) { Write-Warning "App not updated: is Milk Pump.exe running?" }
    else {
        Write-Host "Installed the app: $appTo\Milk Pump.exe"
        $lnk = Join-Path ([Environment]::GetFolderPath('Programs')) 'Milk Pump.lnk'
        $sc = (New-Object -ComObject WScript.Shell).CreateShortcut($lnk)
        $sc.TargetPath = Join-Path $appTo 'Milk Pump.exe'
        $sc.WorkingDirectory = $appTo
        $sc.Description = 'Milk Pump: MilkDrop visuals for whatever the PC is playing'
        $sc.Save()
    }
}

# Live takes one custom VST3 folder and does not follow junctions or shortcuts (tried 2026-10-29),
# so SwarmSynth Revived's latest Release builds are copied in beside Milk Pump. Until both are
# final builds in Daxy's normal VST3 folder. SwarmFX comes from its own build folder: the copy
# beside Revived's build is a stale September one.
$swarm = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'SwarmSynthRevived\build'
foreach ($b in @(@('SwarmSynthRevived_artefacts', 'SwarmSynth Revived.vst3'), @('SwarmFX_artefacts', 'SwarmFX.vst3'))) {
    $src = Join-Path $swarm "$($b[0])\Release\VST3\$($b[1])"
    if (-not (Test-Path $src)) { continue }
    robocopy $src (Join-Path $PSScriptRoot "VST3\$($b[1])") /MIR /R:2 /W:1 /NFL /NDL /NJH /NJS /NP | Out-Null
    if ($LASTEXITCODE -ge 8) { Write-Warning "$($b[1]) not updated: is Live using it?" } else { Write-Host "Copied $($b[1])" }
}
