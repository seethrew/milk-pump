# Draws the logo texture for the opening screen: "MILK PUMP" in 04b_30 (Fonts\),
# white on black, 1024 x 256, into Presets\Textures\milkpump.png. install-data.ps1 copies it to the
# data folder's textures\, where the startup preset finds it as sampler_pc_milkpump.
#   powershell -ExecutionPolicy Bypass -File Tools\make-logo.ps1
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$root = Split-Path $PSScriptRoot -Parent
$out  = Join-Path $root 'Presets\Textures\milkpump.png'
New-Item -ItemType Directory -Force (Split-Path $out) | Out-Null

$fonts = New-Object Drawing.Text.PrivateFontCollection
$fonts.AddFontFile((Join-Path $root 'Fonts\04B_30.ttf'))
$font = New-Object Drawing.Font $fonts.Families[0], 112, ([Drawing.GraphicsUnit]::Pixel)

$bmp = New-Object Drawing.Bitmap 1024, 256
$g = [Drawing.Graphics]::FromImage($bmp)
$g.Clear([Drawing.Color]::Black)
$g.TextRenderingHint = 'SingleBitPerPixelGridFit'   # a pixel font: hard edges, no smoothing
$fmt = New-Object Drawing.StringFormat
$fmt.Alignment = 'Center'; $fmt.LineAlignment = 'Center'; $fmt.FormatFlags = 'NoWrap'
$g.DrawString('MILK PUMP', $font, [Drawing.Brushes]::White, (New-Object Drawing.RectangleF 0, 8, 1024, 256), $fmt)

# 04b_30's M has only a small notch, so it reads as an H (Daxy, 2026-10-30). Both Ms (the 1st and
# 7th runs of lit columns: M I L K P U M P) are redrawn on the font's own 4-pixel grid: two
# stems, a V and two diagonals between them ($middle), the font's rounded corners and its shine dot.
$cell = 4
$lit = @(for ($x = 0; $x -lt 1024; $x++) { $on = $false; for ($y = 0; $y -lt 256; $y += 2) { if ($bmp.GetPixel($x, $y).R -gt 128) { $on = $true; break } }; $on })
$runs = @(); $start = -1
for ($x = 0; $x -le 1024; $x++) {
    $on = $x -lt 1024 -and $lit[$x]
    if ($on -and $start -lt 0) { $start = $x }
    if (-not $on -and $start -ge 0) { $runs += , @($start, $x); $start = -1 }
}
$top = 256; $bottom = 0
for ($y = 0; $y -lt 256; $y++) { for ($x = $runs[0][0]; $x -lt $runs[0][1]; $x++) { if ($bmp.GetPixel($x, $y).R -gt 128) { $top = [Math]::Min($top, $y); $bottom = [Math]::Max($bottom, $y + 1) } } }
foreach ($i in @(0, 6)) {   # M I L K P U M P
    $x0 = $runs[$i][0]; $w = [int](($runs[$i][1] - $x0) / $cell); $h = [int](($bottom - $top) / $cell)
    $stem = [int][Math]::Floor(($w - 8) / 2); $gapL = $stem; $gapR = $w - $stem - 1
    # Between the stems (9 cells), row by row: '#' lit. The V narrows to a rounded bottom; the
    # diagonals are chunky and meet in a blunt, rounded point two thirds of the way down; the
    # legs are open below. (Daxy, 2026-10-30: the V chunkier, lower, then slightly rounded.)
    $middle = @('.........', '#.......#', '#.......#', '##.....##', '##.....##', '###...###', '###...###',
                '####.####', '#########', '#########', '#########', '#########', '.#######.', '.#######.',
                '..#####..', '..#####..', '...###...')
    if ($gapR - $gapL + 1 -ne 9) { throw "M: expected 9 cells between the stems, got $($gapR - $gapL + 1)" }
    $g.FillRectangle([Drawing.Brushes]::Black, $x0, $top, $w * $cell, $h * $cell)
    for ($r = 0; $r -lt $h; $r++) {
        for ($c = 0; $c -lt $w; $c++) {
            $on = $true
            if ($c -ge $gapL -and $c -le $gapR) { $on = $r -lt $middle.Count -and $middle[$r][$c - $gapL] -eq '#' }
            if (($r -eq 0 -or $r -eq $h - 1) -and ($c -lt 2 -or $c -ge $w - 2 -or ($c -ge $stem - 2 -and $c -lt $stem) -or ($c -gt $w - $stem - 1 -and $c -le $w - $stem + 1))) { $on = $false }   # rounded corners
            if (($r -eq 2 -or $r -eq 3) -and $c -ge 2 -and $c -le 4) { $on = $false }   # shine
            if ($r -eq 4 -and $c -eq 2) { $on = $false }
            if ($on) { $g.FillRectangle([Drawing.Brushes]::White, $x0 + $c * $cell, $top + $r * $cell, $cell, $cell) }
        }
    }
}
$bmp.Save($out, [Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
Write-Host $out
