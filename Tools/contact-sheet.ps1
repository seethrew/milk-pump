# Combines PNGs into one labelled grid image (for checking many preset screenshots at once).
#   powershell -ExecutionPolicy Bypass -File Tools\contact-sheet.ps1 -Images a.png,b.png -Out sheet.png [-Cols 4] [-Width 480]
param([Parameter(Mandatory)] [string[]]$Images, [Parameter(Mandatory)] [string]$Out, [int]$Cols = 4, [int]$Width = 480)
Add-Type -AssemblyName System.Drawing
$h = [int]($Width * 9 / 16); $rows = [math]::Ceiling($Images.Count / $Cols)
$sheet = New-Object Drawing.Bitmap ($Cols * $Width), ($rows * ($h + 22))
$g = [Drawing.Graphics]::FromImage($sheet); $g.Clear([Drawing.Color]::FromArgb(40, 40, 40))
$font = New-Object Drawing.Font 'Segoe UI', 10
for ($i = 0; $i -lt $Images.Count; $i++) {
    $x = ($i % $Cols) * $Width; $y = [math]::Floor($i / $Cols) * ($h + 22)
    $img = [Drawing.Image]::FromFile((Resolve-Path $Images[$i]).Path)
    $g.DrawImage($img, $x, $y + 22, $Width, $h); $img.Dispose()
    $g.DrawString([IO.Path]::GetFileNameWithoutExtension($Images[$i]), $font, [Drawing.Brushes]::White, $x + 4, $y + 3)
}
$sheet.Save($Out, [Drawing.Imaging.ImageFormat]::Png); $g.Dispose(); $sheet.Dispose()
Write-Host $Out
