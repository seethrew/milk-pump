# Builds everything under Source\ with CMake: the engine library (mdvst_engine.lib, plugin mode),
# the VST3 (Milk Pump.vst3), the app (Milk Pump.exe), EngineTest.exe and HostTest.exe. Run
# setup.ps1 once first.
# Usage:  powershell -ExecutionPolicy Bypass -File build.ps1 [-Config Release|Debug|RelWithDebInfo]
param([ValidateSet('Release', 'Debug', 'RelWithDebInfo')] [string]$Config = 'Release')
$ErrorActionPreference = 'Stop'

$root  = $PSScriptRoot
$tools = Join-Path $root 'Tools'
# CMake: the one on the PATH, else a standalone install, else the one inside Visual Studio 2022.
$cmake = (Get-Command cmake -ErrorAction SilentlyContinue).Source
if (-not $cmake -and (Test-Path 'C:\Program Files\CMake\bin\cmake.exe')) { $cmake = 'C:\Program Files\CMake\bin\cmake.exe' }
if (-not $cmake) {
    $vs = & "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe" -latest -property installationPath
    $cmake = Join-Path $vs 'Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe'
}

# This PC's own settings, if any (local-settings.ps1, not published): $ScratchRoot.
$ScratchRoot = $null
if (Test-Path (Join-Path $root 'local-settings.ps1')) { . (Join-Path $root 'local-settings.ps1') }

# vcpkg's caches in Tools\ (kept), its scratch (build trees, downloads: disposable) in $ScratchRoot.
$env:VCPKG_DEFAULT_BINARY_CACHE = Join-Path $tools 'vcpkg-cache\archives'
$env:X_VCPKG_REGISTRIES_CACHE   = Join-Path $tools 'vcpkg-cache\registries'
$env:VCPKG_DISABLE_METRICS      = '1'
New-Item -ItemType Directory -Force $env:VCPKG_DEFAULT_BINARY_CACHE, $env:X_VCPKG_REGISTRIES_CACHE | Out-Null
$scratch  = if ($ScratchRoot) { Join-Path $ScratchRoot 'vcpkg' } else { Join-Path $tools 'vcpkg-scratch' }
$vcpkgOpts = "--x-buildtrees-root=$scratch\buildtrees;--x-packages-root=$scratch\packages;--downloads-root=$scratch\downloads;--clean-after-build"

& $cmake -S $root -B (Join-Path $root 'build') -G 'Visual Studio 17 2022' -A x64 "-DVCPKG_INSTALL_OPTIONS=$vcpkgOpts"
if ($LASTEXITCODE) { throw "CMake configure failed ($LASTEXITCODE)" }
& $cmake --build (Join-Path $root 'build') --config $Config --parallel
if ($LASTEXITCODE) { throw "Build failed ($LASTEXITCODE)" }

Write-Host "Built ($Config): $root\build\EngineTest\$Config\EngineTest.exe"
Write-Host "Built ($Config): $root\build\Source\Plugin\MDVST_Plugin_artefacts\$Config\VST3\Milk Pump.vst3"
