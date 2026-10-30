# Icon mockups for the Milk Pump app (Daxy, 2026-10-30): a yellow cow on black whose middle is a
# hydraulic piston (the "pump"). Each idea shown big and at the small sizes Windows uses, on a
# sheet per round: Icons\mockups.png (A-C), Icons\mockups2.png (A, then D-F built on it), plus
# each one alone at 256 px.
#   powershell -ExecutionPolicy Bypass -File Tools\make-icon-mockups.ps1
# Tools\make-icon.ps1 dot-sources this with -FunctionsOnly for the drawing code of the real icon (G).
param([switch]$FunctionsOnly)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$root = Split-Path $PSScriptRoot -Parent
$dir = Join-Path $root 'Icons'
New-Item -ItemType Directory -Force $dir | Out-Null

$yellow = New-Object Drawing.SolidBrush ([Drawing.Color]::FromArgb(255, 255, 206, 26))
$black = [Drawing.Brushes]::Black

function RoundRect([float]$x, [float]$y, [float]$w, [float]$h, [float]$r) {
    $p = New-Object Drawing.Drawing2D.GraphicsPath
    $d = 2 * $r
    $p.AddArc($x, $y, $d, $d, 180, 90); $p.AddArc($x + $w - $d, $y, $d, $d, 270, 90)
    $p.AddArc($x + $w - $d, $y + $h - $d, $d, $d, 0, 90); $p.AddArc($x, $y + $h - $d, $d, $d, 90, 90)
    $p.CloseFigure(); $p
}
function Fill($g, $brush, $x, $y, $w, $h, $r) { $g.FillPath($brush, (RoundRect $x $y $w $h $r)) }

function Background($g) {
    $g.Clear([Drawing.Color]::Transparent)
    Fill $g $black 0 0 256 256 40
}

# Shared parts: a head facing left with horns, ear and eye; a tail with a tuft.
function Head($g, $x, $y) {
    $g.FillPolygon($yellow, [Drawing.PointF[]]@((New-Object Drawing.PointF ($x + 14), ($y + 6)), (New-Object Drawing.PointF ($x + 8), ($y - 14)), (New-Object Drawing.PointF ($x + 24), ($y + 4))))
    $g.FillPolygon($yellow, [Drawing.PointF[]]@((New-Object Drawing.PointF ($x + 32), ($y + 4)), (New-Object Drawing.PointF ($x + 40), ($y - 16)), (New-Object Drawing.PointF ($x + 44), ($y + 8))))
    Fill $g $yellow $x $y 50 40 14            # skull
    Fill $g $yellow ($x - 8) ($y + 22) 40 32 14 # muzzle, lower and forward
    Fill $g $yellow ($x + 40) ($y + 6) 18 10 5  # ear
    $g.FillEllipse($black, $x + 16, $y + 12, 9, 9)      # eye
    $g.FillEllipse($black, $x - 2, $y + 36, 7, 6)       # nostril
}
function Tail($g, $x, $y) {
    $pen = New-Object Drawing.Pen $yellow.Color, 7
    $pen.StartCap = 'Round'; $pen.EndCap = 'Round'
    $g.DrawBezier($pen, $x, $y, $x + 18, $y + 4, $x + 14, $y + 40, $x + 12, $y + 58)
    Fill $g $yellow ($x + 4) ($y + 54) 16 22 8
}
function Udder($g, $x, $y) {
    Fill $g $yellow $x $y 26 20 10
    foreach ($t in 0..2) { Fill $g $yellow ($x + 3 + $t * 8) ($y + 14) 5 13 2.5 }
}

# A: the cow in two halves, joined by a piston rod. The rear half is the cylinder (gland collar
# and bands); the front half rides on the rod.
function CowA($g) {
    Head $g 18 62
    Fill $g $yellow 60 92 54 66 18                 # front half: chest and shoulders
    Fill $g $yellow 64 150 15 62 5; Fill $g $yellow 94 150 15 62 5   # front legs
    Fill $g $yellow 108 113 44 18 3                # piston rod
    Fill $g $yellow 104 106 10 32 3                # rod's mounting eye on the front half
    Fill $g $yellow 146 100 12 44 3                # gland collar where the rod enters
    Fill $g $yellow 156 86 76 74 22                # rear half = cylinder barrel
    $g.FillRectangle($black, 174, 86, 5, 74); $g.FillRectangle($black, 212, 86, 5, 74)   # barrel bands
    Fill $g $yellow 162 150 15 62 5; Fill $g $yellow 210 150 15 62 5 # back legs
    Udder $g 181 156
    Tail $g 228 94
}
function MockA($g) { Background $g; CowA $g }

# B: the whole body is one hydraulic cylinder; the neck is the polished rod coming out of it.
function MockB($g) {
    Background $g
    Head $g 14 52
    Fill $g $yellow 58 96 52 14 3                  # rod (neck)
    Fill $g $yellow 98 86 14 34 3                  # gland
    Fill $g $yellow 108 80 122 80 34               # barrel = body
    $g.FillRectangle($black, 132, 80, 6, 80); $g.FillRectangle($black, 200, 80, 6, 80)   # end-cap seams
    Fill $g $yellow 150 70 14 14 3                 # hydraulic port on top
    Fill $g $yellow 116 150 16 62 5; Fill $g $yellow 142 150 16 62 5
    Fill $g $yellow 190 150 16 62 5; Fill $g $yellow 214 150 16 62 5
    Udder $g 161 156
    Tail $g 226 92
}

# C: pixel art on a 16 x 16 grid, like the logo: crisp at the smallest sizes.
$pixelCow = @(
    '................',
    '.#..#...........',
    '.####...........',
    '.#.##...........',
    '.######...######',
    '#######..#####.#',
    '###.##########.#',
    '###.##########.#',
    '....###..#####.#',
    '....###...####.#',
    '....#.#...####.#',
    '....#.#...####..',
    '....#.#...#..#..',
    '....#.#...#..#..',
    '................',
    '................')
function MockC($g) {
    Background $g
    $cell = 13; $ox = 24; $oy = 34
    for ($r = 0; $r -lt 16; $r++) { for ($c = 0; $c -lt 16; $c++) {
        if ($pixelCow[$r][$c] -eq '#') { $g.FillRectangle($yellow, $ox + $c * $cell, $oy + $r * $cell, $cell, $cell) } } }
}

# Round 2 (Daxy: "A is the best, 3 more in 3 styles with A as a guide").

# D: bold and mechanical. A's layout, filling more of the square, chunkier legs, and engineering
# details cut in black: a shine line on the rod, bolts on the collar, bands on the barrel.
function MockD($g) {
    Background $g
    Head $g 16 54
    Fill $g $yellow 54 86 60 76 24                 # front half
    Fill $g $yellow 58 148 20 70 8; Fill $g $yellow 92 148 20 70 8   # front legs
    Fill $g $yellow 108 108 52 24 5                # rod
    $g.FillRectangle($black, 114, 114, 38, 4)      # shine on the rod
    Fill $g $yellow 104 100 14 40 5                # mounting eye
    Fill $g $yellow 150 94 16 52 5                 # collar
    $g.FillEllipse($black, 155, 99, 7, 7); $g.FillEllipse($black, 155, 133, 7, 7)   # bolts
    Fill $g $yellow 162 80 78 84 26                # barrel
    $g.FillRectangle($black, 182, 80, 6, 84); $g.FillRectangle($black, 218, 80, 6, 84)
    Fill $g $yellow 166 150 20 68 8; Fill $g $yellow 214 150 20 68 8 # back legs
    Udder $g 187 160
    Tail $g 234 90
}

# E: A glowing, with milk dripping from the udder, like the opening screen.
function MockE($g) {
    Background $g
    $g.SetClip((RoundRect 0 0 256 256 40))   # the glow stays inside the square's rounded corners
    $cow = New-Object Drawing.Bitmap 256, 256
    $cg = [Drawing.Graphics]::FromImage($cow); $cg.SmoothingMode = 'AntiAlias'; CowA $cg; $cg.Dispose()
    foreach ($blur in 24, 48) {   # a soft halo: the cow shrunk and stretched back up
        $b = New-Object Drawing.Bitmap $blur, $blur
        $bg = [Drawing.Graphics]::FromImage($b); $bg.InterpolationMode = 'HighQualityBicubic'; $bg.DrawImage($cow, 0, 0, $blur, $blur); $bg.Dispose()
        $g.InterpolationMode = 'HighQualityBicubic'
        $g.DrawImage($b, -6, -6, 268, 268)
        $b.Dispose()
    }
    $g.FillRectangle((New-Object Drawing.SolidBrush ([Drawing.Color]::FromArgb(110, 0, 0, 0))), 0, 0, 256, 256)
    $g.DrawImage($cow, 0, 0, 256, 256)
    $cow.Dispose()
    $milk = New-Object Drawing.SolidBrush ([Drawing.Color]::FromArgb(255, 255, 250, 235))
    foreach ($d in @(@(184, 184, 26), @(192, 184, 14), @(200, 184, 34))) {   # drips: x, top, length
        Fill $g $milk $d[0] $d[1] 5 $d[2] 2.5
        $g.FillEllipse($milk, $d[0] - 2, $d[1] + $d[2] - 4, 9, 11)
    }
    $g.ResetClip()
}

# F: A as 32 x 32 pixel art, the logo's blocky look but with enough pixels for the piston:
# the rod with a gap above and below, the collar, one band, eye, udder and tail, placed by hand.
$pixelCow32 = @(
    '................................',
    '................................',
    '................................',
    '................................',
    '................................',
    '................................',
    '................................',
    '...#...#........................',
    '...######.......................',
    '..########......................',
    '..###.####......................',
    '..############.......#.####.#...',
    '.#############....#.##.#####.#..',
    '.#.###########....#.##.#####.#..',
    '.#####..##############.#####.#..',
    '........##############.#####.#..',
    '........######....#.##.#####.#..',
    '........######....#.##.#####.#..',
    '........######......##.#####.#..',
    '........######......##.#######..',
    '........##..##.......#.####.##..',
    '........##..##......##.##.##....',
    '........##..##......##.##.##....',
    '........##..##......##.##.##....',
    '........##..##......##....##....',
    '........##..##......##....##....',
    '........##..##......##....##....',
    '................................',
    '................................',
    '................................',
    '................................',
    '................................')
function MockF($g) {
    Background $g
    for ($r = 0; $r -lt 32; $r++) { for ($c = 0; $c -lt 32; $c++) {
        if ($pixelCow32[$r][$c] -eq '#') { $g.FillRectangle($yellow, $c * 8, $r * 8, 8, 8) } } }
}

# Round 3 (Daxy: the cow was too abstract; combine a hand pump, a hydraulic cylinder and a milk
# carton into a stylised Milk Pump icon). The carton is the pump's body: gable top, the
# cylinder's bands and eye-ended rod, the hand pump's lever and spout, milk pouring out.
# The words come from the logo texture (Tools\make-logo.ps1), which has the redrawn M: the
# font's own M reads as an H.
$logoBmp = [Drawing.Bitmap]::FromFile((Join-Path $root 'Presets\Textures\milkpump.png'))
function LogoWord($x0, $x1, $ink) {   # one word of the logo, its lit pixels in $ink, the rest clear
    $top = 256; $bottom = 0; $left = 1024; $right = 0
    for ($y = 0; $y -lt 256; $y += 2) { for ($x = $x0; $x -lt $x1; $x += 2) { if ($logoBmp.GetPixel($x, $y).R -gt 128) {
        $top = [Math]::Min($top, $y); $bottom = [Math]::Max($bottom, $y + 2); $left = [Math]::Min($left, $x); $right = [Math]::Max($right, $x + 2) } } }
    $w = New-Object Drawing.Bitmap ($right - $left), ($bottom - $top)
    for ($y = 0; $y -lt $w.Height; $y++) { for ($x = 0; $x -lt $w.Width; $x++) {
        if ($logoBmp.GetPixel($left + $x, $top + $y).R -gt 128) { $w.SetPixel($x, $y, $ink) } } }
    $w
}
$words = @{}
foreach ($ink in 'black', 'yellow') {
    $c = if ($ink -eq 'black') { [Drawing.Color]::Black } else { $yellow.Color }
    $words["MILK-$ink"] = LogoWord 0 480 $c
    $words["PUMP-$ink"] = LogoWord 480 1024 $c
}
$shade = New-Object Drawing.SolidBrush ([Drawing.Color]::FromArgb(255, 170, 128, 0))   # the carton's side: darker, not another hue
$milkWhite = New-Object Drawing.SolidBrush ([Drawing.Color]::FromArgb(255, 255, 250, 235))

function Poly([float[]]$xy) {
    $p = New-Object Drawing.Drawing2D.GraphicsPath
    $pts = for ($i = 0; $i -lt $xy.Count; $i += 2) { New-Object Drawing.PointF $xy[$i], $xy[$i + 1] }
    $p.AddPolygon([Drawing.PointF[]]$pts); $p
}
function Circle($x, $y, $r) { $p = New-Object Drawing.Drawing2D.GraphicsPath; $p.AddEllipse($x - $r, $y - $r, 2 * $r, 2 * $r); $p }
function Stroke($pts, $width) {   # a thick curve as a fillable outline
    $p = New-Object Drawing.Drawing2D.GraphicsPath
    $p.AddBeziers([Drawing.PointF[]]@(foreach ($q in $pts) { New-Object Drawing.PointF $q[0], $q[1] }))
    $pen = New-Object Drawing.Pen ([Drawing.Color]::White), $width
    $pen.StartCap = 'Round'; $pen.EndCap = 'Round'
    $p.Widen($pen); $p
}

# The parts, back to front: @(path, brush). $lever adds the hand pump's lever.
function PumpCarton($lever) {
    $parts = @()
    if ($lever) {
        $parts += , @((Stroke @(@(104, 40), @(150, 30), @(196, 26), @(214, 60), @(232, 92), @(236, 126), @(228, 150)) 13), $yellow)   # the lever, out to its grip
        $parts += , @((Circle 168 66 9), $yellow)                                   # its pivot post on the fin
        $parts += , @((RoundRect 164 34 8 34 3), $yellow)
    }
    $parts += , @((RoundRect 100 34 12 44 3), $yellow)     # piston rod, into the top
    $parts += , @((Circle 106 30 13), $yellow)            # the rod's eye
    $parts += , @((Poly @(150, 112, 186, 98, 186, 206, 150, 222)), $shade)        # carton side
    $parts += , @((Poly @(150, 112, 186, 98, 166, 72)), $shade)                   # side gable
    $parts += , @((Poly @(70, 112, 150, 112, 166, 72, 86, 72)), $yellow)          # roof
    $parts += , @((RoundRect 84 62 84 12 3), $yellow)                              # top fin
    $parts += , @((RoundRect 70 112 80 110 4), $yellow)                            # carton front
    $parts += , @((RoundRect 34 136 40 18 4), $yellow)                             # spout
    $parts += , @((RoundRect 28 140 16 24 4), $yellow)                             # spout nozzle, turned down
    $parts
}
function Details($g, $ink, $lettering = $true) {   # the cylinder's bands and MILK PUMP across the front, in $ink
    $g.FillRectangle($ink, 70, 128, 80, 6); $g.FillRectangle($ink, 70, 198, 80, 6)
    if (-not $lettering) { return }
    $name = if ($ink -eq $black) { 'black' } else { 'yellow' }
    $g.InterpolationMode = 'HighQualityBicubic'
    foreach ($row in @(@('MILK', 148), @('PUMP', 172))) {
        $bmp = $words["$($row[0])-$name"]
        $w = 62; $h = $bmp.Height * $w / $bmp.Width
        $g.DrawImage($bmp, [single](110 - $w / 2), [single]$row[1], [single]$w, [single]$h)
    }
}
function Pour($g) {   # milk from the spout: a stream, a drop, a splash
    Fill $g $milkWhite 32 164 8 34 4
    $g.FillEllipse($milkWhite, 30, 202, 12, 14)
    $g.FillEllipse($milkWhite, 14, 222, 44, 10)
}

# G: flat and solid, like the earlier ones: the full combination with the lever.
function MockG($g, $lettering = $true) {
    Background $g
    foreach ($part in (PumpCarton $true)) { $g.FillPath($part[1], $part[0]) }
    Details $g $black $lettering
    Pour $g
}

# H: line art (like the cylinder drawing): yellow outlines on black, each part hiding the ones
# behind it.
function MockH($g) {
    Background $g
    $pen = New-Object Drawing.Pen $yellow.Color, 7
    $pen.LineJoin = 'Round'
    foreach ($part in (PumpCarton $true)) { $g.FillPath($black, $part[0]); $g.DrawPath($pen, $part[0]) }
    Details $g $yellow
    $milkPen = New-Object Drawing.Pen $milkWhite.Color, 6
    $milkPen.StartCap = 'Round'; $milkPen.EndCap = 'Round'
    $g.DrawLine($milkPen, 36, 170, 36, 196); $g.DrawEllipse($milkPen, 31, 204, 10, 11); $g.DrawArc($milkPen, 14, 220, 44, 12, 200, 140)
}

# I: simpler, for the small sizes: no lever; the carton is the cylinder, its eye-ended rod
# straight up out of the top, and the spout pouring.
function MockI($g) {
    Background $g
    foreach ($part in (PumpCarton $false)) { $g.FillPath($part[1], $part[0]) }
    Details $g $black
    Pour $g
}

if ($FunctionsOnly) { return }
$sheets = [ordered]@{
    'mockups.png'  = [ordered]@{ 'A  two halves on a rod' = 'MockA'; 'B  body is the cylinder' = 'MockB'; 'C  pixel, like the logo' = 'MockC' }
    'mockups2.png' = [ordered]@{ 'A  the guide' = 'MockA'; 'D  bold, mechanical' = 'MockD'; 'E  glowing, dripping milk' = 'MockE'; 'F  32 px pixel art' = 'MockF' }
    'mockups3.png' = [ordered]@{ 'G  carton pump, solid' = 'MockG'; 'H  carton pump, line art' = 'MockH'; 'I  carton cylinder, simple' = 'MockI' }
}
foreach ($file in $sheets.Keys) {
$mocks = $sheets[$file]
$sheet = New-Object Drawing.Bitmap 1100, (90 + 300 * $mocks.Count)
$sg = [Drawing.Graphics]::FromImage($sheet)
$sg.Clear([Drawing.Color]::FromArgb(255, 60, 60, 64))
$label = New-Object Drawing.Font 'Segoe UI', 20
$sg.DrawString('Milk Pump icon ideas: 256, 64, 48, 32, 16 px (the last four at real size)', $label, [Drawing.Brushes]::White, 20, 20)
$row = 0
foreach ($name in $mocks.Keys) {
    $big = New-Object Drawing.Bitmap 256, 256
    $g = [Drawing.Graphics]::FromImage($big)
    $g.SmoothingMode = 'AntiAlias'
    if ($name -like 'C*' -or $name -like 'F*') { $g.SmoothingMode = 'None' }
    & $mocks[$name] $g
    $g.Dispose()
    $big.Save((Join-Path $dir ("mockup-" + $name.Substring(0, 1) + ".png")), [Drawing.Imaging.ImageFormat]::Png)
    $y = 80 + $row * 300
    $sg.DrawString($name, $label, [Drawing.Brushes]::White, 20, $y)
    $sg.DrawImage($big, 20, $y + 36, 256, 256)
    $x = 320
    foreach ($s in 64, 48, 32, 16) {
        $sg.InterpolationMode = if (($name -like 'C*' -and $s -eq 16) -or ($name -like 'F*' -and $s -eq 32)) { 'NearestNeighbor' } else { 'HighQualityBicubic' }
        $sg.DrawImage($big, $x, $y + 36 + (256 - $s) / 2, $s, $s)
        $x += $s + 40
    }
    # and the 32 px one blown up 4x, to see what the pixels really are
    $small = New-Object Drawing.Bitmap 32, 32
    $g2 = [Drawing.Graphics]::FromImage($small); $g2.InterpolationMode = 'HighQualityBicubic'; $g2.DrawImage($big, 0, 0, 32, 32); $g2.Dispose()
    $sg.InterpolationMode = 'NearestNeighbor'; $sg.PixelOffsetMode = 'Half'
    $sg.DrawImage($small, 780, $y + 36 + 64, 128, 128)
    $sg.PixelOffsetMode = 'Default'
    $sg.DrawString('32 px, zoomed', (New-Object Drawing.Font 'Segoe UI', 11), [Drawing.Brushes]::Silver, 780, $y + 36 + 200)
    $small.Dispose(); $big.Dispose()
    $row++
}
$out = Join-Path $dir $file
$sheet.Save($out, [Drawing.Imaging.ImageFormat]::Png)
$sg.Dispose(); $sheet.Dispose()
Write-Host $out
}
