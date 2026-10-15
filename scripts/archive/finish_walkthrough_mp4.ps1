# finish_walkthrough_mp4.ps1
param(
    [string]$BlenderExe = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe",
    [string]$InputDir = (Join-Path $PSScriptRoot "..\render\walkthrough"),
    [string]$OutputMp4 = (Join-Path $PSScriptRoot "..\Courtyard_Walkthrough_30s.mp4")
)

Write-Host "=== Encoding Full 30s Walkthrough to MP4 ==="
& $BlenderExe -b --python (Join-Path $PSScriptRoot "..\make_mp4.py") -- $InputDir $OutputMp4 24
Write-Host "=== Walkthrough Video Complete: $OutputMp4 ==="
