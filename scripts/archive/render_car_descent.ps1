# render_car_descent.ps1
param(
    [string]$BlendFile = (Join-Path $PSScriptRoot "..\Courtyard Apartments 50x100 v3.blend"),
    [string]$BlenderExe = "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe",
    [string]$OutputDir = (Join-Path $PSScriptRoot "..\render\descent"),
    [string]$OutputMp4 = (Join-Path $PSScriptRoot "..\Courtyard_Car_Descent.mp4")
)

Write-Host "=== Rendering Car Descent Animation (240 frames, 10s @ 24fps) ==="
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

# Run Blender CLI with python expression to switch active camera and render
$pyExpr = @"
import bpy
scene = bpy.context.scene
cam = bpy.data.objects.get('Camera_CarDescent_Cam')
if cam:
    scene.camera = cam
    print('Switched active camera to:', cam.name)
scene.frame_start = 1
scene.frame_end = 240
scene.render.fps = 24
scene.render.filepath = r'$OutputDir\frame'
bpy.ops.render.render(animation=True)
"@

& $BlenderExe -b $BlendFile --python-expr $pyExpr

Write-Host "=== Encoding Car Descent to MP4 ==="
& $BlenderExe -b --python (Join-Path $PSScriptRoot "..\make_mp4.py") -- $OutputDir $OutputMp4 24

Write-Host "=== Car Descent Video Complete: $OutputMp4 ==="
