# The Milk Pump app's icon (Daxy's pick, 2026-10-30: mockup G, the milk-carton pump) as a Windows
# .ico holding 16, 20, 24, 32, 40, 48, 64, 128 and 256 px, each drawn at 256 and scaled down. Up
# to 32 px the MILK PUMP lettering is left off (it would only be texture); the bands stay.
# Writes Source\App\milkpump.ico (plugin.rc takes it for the app build) and Icons\milkpump-*.png.
#   powershell -ExecutionPolicy Bypass -File Tools\make-icon.ps1
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'make-icon-mockups.ps1') -FunctionsOnly

$sizes = 16, 20, 24, 32, 40, 48, 64, 128, 256
$images = foreach ($s in $sizes) {
    $big = New-Object Drawing.Bitmap 256, 256
    $g = [Drawing.Graphics]::FromImage($big); $g.SmoothingMode = 'AntiAlias'
    MockG $g ($s -gt 32)
    $g.Dispose()
    $img = New-Object Drawing.Bitmap $s, $s
    $g = [Drawing.Graphics]::FromImage($img)
    $g.InterpolationMode = 'HighQualityBicubic'; $g.PixelOffsetMode = 'HighQuality'
    $g.DrawImage($big, 0, 0, $s, $s)
    $g.Dispose(); $big.Dispose()
    $img.Save((Join-Path $dir "milkpump-$s.png"), [Drawing.Imaging.ImageFormat]::Png)
    $ms = New-Object IO.MemoryStream
    $img.Save($ms, [Drawing.Imaging.ImageFormat]::Png)
    $img.Dispose()
    , $ms.ToArray()
}

# ICO: a 6-byte header, a 16-byte entry per image, then the images (PNG inside, Vista and later).
$out = Join-Path $root 'Source\App\milkpump.ico'
$ms = New-Object IO.MemoryStream
$w = New-Object IO.BinaryWriter $ms
$w.Write([uint16]0); $w.Write([uint16]1); $w.Write([uint16]$sizes.Count)
$offset = 6 + 16 * $sizes.Count
for ($i = 0; $i -lt $sizes.Count; $i++) {
    $s = $sizes[$i]
    $w.Write([byte]($s % 256)); $w.Write([byte]($s % 256))   # 256 is written as 0
    $w.Write([byte]0); $w.Write([byte]0); $w.Write([uint16]1); $w.Write([uint16]32)
    $w.Write([uint32]$images[$i].Length); $w.Write([uint32]$offset)
    $offset += $images[$i].Length
}
foreach ($bytes in $images) { $w.Write([byte[]]$bytes) }
[IO.File]::WriteAllBytes($out, $ms.ToArray())
Write-Host $out
