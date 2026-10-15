param(
    [string]$BlendFile = (Join-Path $PSScriptRoot "..\Courtyard Apartments 50x100 v3.blend"),
    [string]$BlenderExe = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe",
    [string]$OutputDir = (Join-Path $PSScriptRoot "..\render\walkthrough"),
    [string]$OutputMp4 = (Join-Path $PSScriptRoot "..\Courtyard_Walkthrough_30s.mp4")
)

Write-Host "Starting Walkthrough Frame Rendering (Frames 1-720)..."

if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

$logFile = (Join-Path $PSScriptRoot "..\render\walkthrough_render.log")

# Render frames 1 to 720
& $BlenderExe -b $BlendFile -s 1 -e 720 -o "$OutputDir\frame####" -a 2>&1 | Tee-Object -FilePath $logFile

$renderedCount = (Get-ChildItem $OutputDir -Filter "*.png").Count
Write-Host "Rendered frames count: $renderedCount"

if ($renderedCount -ge 700) {
    Write-Host "Compiling to MP4 video..."
    & $BlenderExe -b --python (Join-Path $PSScriptRoot "..\make_mp4.py") -- $OutputDir $OutputMp4 24
    Write-Host "Finished MP4 generation."
} else {
    Write-Host "Render ended before completion: $renderedCount frames."
}
