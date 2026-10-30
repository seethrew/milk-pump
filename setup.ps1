# Fetches what Milk Pump needs to build, into this folder only: nothing is installed system-wide.
# Anything already there is skipped, so it is safe to run again.
#
#   Tools\JUCE        JUCE 8 (tag 8.0.16-security), for the VST3 plugin
#   Tools\vcpkg       vcpkg, which builds projectM-eval (vcpkg.json) during the first build
#   Tools\D3DX        Microsoft.DXSDK.D3DX 9.29.952.8 (NuGet), laid out as Tools\DXSDK\{Include,Lib\x64}
#   Tools\redist\x64  d3dx9_43.dll (from that package) and d3dx9_31.dll (Microsoft's DirectX
#                     End-User Runtime, June 2010: extracted, not installed)
#   -WithBeatDrop     Reference\BeatDrop: BeatDrop's repository at the commit Milk Pump is built
#                     on, for its presets and textures (install-data.ps1, the installers); 1.4 GB
#   -WithInstaller    Tools\wix: WiX 5.0.2 (a local .NET tool), for Installer\build-installer.ps1
#
# Needs: Windows 10/11 x64, Visual Studio 2022 with "Desktop development with C++", Git; for
# -WithInstaller the .NET 8 SDK.
#   powershell -ExecutionPolicy Bypass -File setup.ps1 [-WithBeatDrop] [-WithInstaller]
param([switch]$WithBeatDrop, [switch]$WithInstaller)
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$tools = Join-Path $root 'Tools'
$temp = Join-Path $env:TEMP 'milkpump-setup'
New-Item -ItemType Directory -Force $tools, $temp | Out-Null

function Step($what) { Write-Host "== $what" }
function Run($exe) { & $exe @args; if ($LASTEXITCODE) { throw "$exe failed ($LASTEXITCODE)" } }

Step 'JUCE 8'
$juce = Join-Path $tools 'JUCE'
if (Test-Path (Join-Path $juce 'CMakeLists.txt')) { Write-Host '   already there' }
else { Run git clone --depth 1 --branch 8.0.16-security https://github.com/juce-framework/JUCE.git $juce }

Step 'vcpkg'
$vcpkg = Join-Path $tools 'vcpkg'
if (-not (Test-Path (Join-Path $vcpkg '.git'))) { Run git clone https://github.com/microsoft/vcpkg.git $vcpkg }
if (Test-Path (Join-Path $vcpkg 'vcpkg.exe')) { Write-Host '   already there' }
else { Run (Join-Path $vcpkg 'bootstrap-vcpkg.bat') -disableMetrics }

Step 'D3DX9 (Microsoft.DXSDK.D3DX 9.29.952.8)'
$d3dx = Join-Path $tools 'D3DX'
if (Test-Path (Join-Path $d3dx 'build\native\include\d3dx9.h')) { Write-Host '   already there' }
else {
    $zip = Join-Path $temp 'd3dx.zip'
    Invoke-WebRequest 'https://www.nuget.org/api/v2/package/Microsoft.DXSDK.D3DX/9.29.952.8' -OutFile $zip
    Expand-Archive $zip $d3dx -Force
}
# Laid out like the June 2010 DirectX SDK, as Source\Engine\CMakeLists.txt expects.
$dxsdk = Join-Path $tools 'DXSDK'
New-Item -ItemType Directory -Force (Join-Path $dxsdk 'Include'), (Join-Path $dxsdk 'Lib\x64') | Out-Null
Copy-Item (Join-Path $d3dx 'build\native\include\*') (Join-Path $dxsdk 'Include') -Force
Copy-Item (Join-Path $d3dx 'build\native\release\lib\x64\*') (Join-Path $dxsdk 'Lib\x64') -Force
$redist = Join-Path $tools 'redist\x64'
New-Item -ItemType Directory -Force $redist | Out-Null
Copy-Item (Join-Path $d3dx 'build\native\release\bin\x64\d3dx9_43.dll') $redist -Force

Step 'd3dx9_31.dll (DirectX End-User Runtime, June 2010)'
# BeatDrop compiles preset shaders with D3DXSHADER_USE_LEGACY_D3DX9_31_DLL, which needs this one;
# the NuGet package lacks it. The redistributable unpacks itself with /Q /T (nothing installed).
if (Test-Path (Join-Path $redist 'd3dx9_31.dll')) { Write-Host '   already there' }
else {
    $exe = Join-Path $temp 'directx_Jun2010_redist.exe'
    if (-not (Test-Path $exe)) {
        Invoke-WebRequest 'https://download.microsoft.com/download/8/4/A/84A35BF1-DAFE-4AE8-82AF-AD2AE20B6B14/directx_Jun2010_redist.exe' -OutFile $exe
    }
    $unpacked = Join-Path $temp 'directx'
    New-Item -ItemType Directory -Force $unpacked | Out-Null
    Start-Process $exe -ArgumentList '/Q', "/T:$unpacked" -Wait
    $cab = Get-ChildItem $unpacked -Filter '*d3dx9_31_x64.cab' | Select-Object -First 1
    if (-not $cab) { throw "No d3dx9_31_x64 cab in $unpacked" }
    Run expand.exe $cab.FullName "-F:d3dx9_31.dll" $redist
}

if ($WithBeatDrop) {
    Step 'BeatDrop (presets and textures, 1.4 GB)'
    $bd = Join-Path $root 'Reference\BeatDrop'
    if (Test-Path (Join-Path $bd 'resources')) { Write-Host '   already there' }
    else {
        Run git clone https://github.com/OfficialIncubo/BeatDrop-Music-Visualizer.git $bd
        Run git -C $bd checkout 44b7ee0f   # the commit Milk Pump's engine was copied from
    }
}

if ($WithInstaller) {
    Step 'WiX 5.0.2'
    if (Test-Path (Join-Path $tools 'wix\wix.exe')) { Write-Host '   already there' }
    else { Run dotnet tool install wix --version 5.0.2 --tool-path (Join-Path $tools 'wix') }
}

Write-Host ''
Write-Host 'Ready. Next: build.ps1 (the plugin, the app, the tests), then install-data.ps1 (the data folder).'
