import bpy
import sys
import os

# Usage: blender -b --python make_mp4.py -- <input_folder> <output_mp4_path> [fps]

argv = sys.argv
if "--" in argv:
    args = argv[argv.index("--") + 1:]
else:
    args = []

if len(args) < 2:
    print("Usage: blender -b --python make_mp4.py -- <input_folder> <output_mp4_path> [fps]")
    sys.exit(1)

input_folder = os.path.abspath(args[0])
output_mp4 = os.path.abspath(args[1])
fps = int(args[2]) if len(args) > 2 else 24

if not os.path.isdir(input_folder):
    print(f"Error: {input_folder} is not a directory.")
    sys.exit(1)

files = sorted([f for f in os.listdir(input_folder) if f.lower().endswith(".png")])
if not files:
    print(f"Error: No PNG files found in {input_folder}")
    sys.exit(1)

print(f"Encoding {len(files)} frames from {input_folder} -> {output_mp4} at {fps} fps")

# Clear existing sequences
scene = bpy.context.scene
if not scene.sequence_editor:
    scene.sequence_editor_create()
se = scene.sequence_editor

# Remove any old strips
for s in list(se.strips):
    se.strips.remove(s)

# Create image strip
first_file = files[0]
strip = se.strips.new_image(
    name="animation",
    filepath=os.path.join(input_folder, first_file),
    channel=1,
    frame_start=1
)

for f in files[1:]:
    strip.elements.append(f)

scene.frame_start = 1
scene.frame_end = len(files)
scene.render.fps = fps

# Configure MP4 H.264 (Blender 5.2 API: media_type = 'VIDEO')
scene.render.image_settings.media_type = 'VIDEO'
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
scene.render.ffmpeg.ffmpeg_preset = 'GOOD'
scene.render.ffmpeg.audio_codec = 'NONE'
scene.render.filepath = output_mp4

print(f"Starting encode: frames 1 to {len(files)}...")
bpy.ops.render.render(animation=True)
print(f"Successfully generated: {output_mp4}")
