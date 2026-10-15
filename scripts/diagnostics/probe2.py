"""probe2.py - sky sun alignment + EEVEE material/glass API."""
import bpy, math
from mathutils import Vector

print("\n" + "#" * 90)
print("# PROBE 2")
print("#" * 90)

# --- Sky texture node introspection ---
nt = bpy.data.worlds.new("ProbeWorld")
nt.use_nodes = True
tree = nt.node_tree
sky = tree.nodes.new('ShaderNodeTexSky')
print("\n--- ShaderNodeTexSky ---")
print("  sky_type:", sky.sky_type)
print("  inputs:")
for i in sky.inputs:
    try:
        v = i.default_value
        v = tuple(round(x, 4) for x in v) if hasattr(v, '__len__') else round(v, 4)
        print(f"    {i.name:22s} = {v}")
    except Exception:
        print(f"    {i.name:22s} = <none>")
print("  outputs:")
for o in sky.outputs:
    print(f"    {o.name}")
print("  python props:")
for a in sorted(dir(sky)):
    if a.startswith('_') or a in ('bl_rna', 'rna_type', 'inputs', 'outputs', 'name', 'label',
                                  'location', 'width', 'height', 'color', 'mute', 'hide',
                                  'select', 'parent', 'type', 'dimensions', 'show_options',
                                  'show_preview', 'show_texture', 'texture_mapping', 'image_user',
                                  'internal_links', 'link', 'warning_propagation'):
        continue
    try:
        v = getattr(sky, a)
        if callable(v):
            continue
        if hasattr(v, '__len__'):
            v = tuple(round(x, 4) for x in v)
        elif isinstance(v, float):
            v = round(v, 4)
        print(f"    {a:26s} = {v}")
    except Exception as e:
        print(f"    {a:26s} ! {e}")

# Test the sun_direction read-out
print("\n--- sun_direction calibration (MULTIPLE_SCATTERING) ---")
sky.sky_type = 'MULTIPLE_SCATTERING'
for elev_deg, rot_deg in ((45, 0), (45, 90), (30, 180), (60, 270)):
    sky.sun_elevation = math.radians(elev_deg)
    sky.sun_rotation = math.radians(rot_deg)
    d = getattr(sky, 'sun_direction', None)
    if d is None:
        print("   sun_direction NOT available")
        break
    d = Vector(d)
    print(f"   elev={elev_deg:3d} rot={rot_deg:3d} -> sun_direction=({d.x:7.4f},{d.y:7.4f},{d.z:7.4f})"
          f"  actual_elev={math.degrees(math.asin(max(-1,min(1,d.z)))):6.2f}"
          f"  azim={math.degrees(math.atan2(d.x, d.y)):7.2f}")

# --- Material props for EEVEE glass ---
print("\n--- Material API (EEVEE-relevant) ---")
probe_mats = [m for m in bpy.data.materials if m.name == 'Mat_Glass_Arch']
m = probe_mats[0] if probe_mats else bpy.data.materials[0]
for a in ('blend_method', 'shadow_method', 'surface_render_method', 'use_transparency_overlap',
          'use_raytrace_refraction', 'use_screen_refraction', 'refraction_depth', 'use_backface_culling',
          'use_thickness', 'thickness_mode', 'show_transparent_back', 'use_raytracing', 'displacement_method'):
    try:
        print(f"   Material.{a:28s} = {getattr(m, a)}")
    except Exception as e:
        print(f"   Material.{a:28s} ! {type(e).__name__}")

print("\n--- Glass material current values ---")
if m.use_nodes:
    for n in m.node_tree.nodes:
        if n.type == 'BSDF_PRINCIPLED':
            for k in ('Base Color', 'Metallic', 'Roughness', 'IOR', 'Alpha', 'Transmission Weight',
                      'Specular IOR Level', 'Coat Weight', 'Thin Wall'):
                try:
                    v = n.inputs[k].default_value
                    v = tuple(round(x, 3) for x in v) if hasattr(v, '__len__') else round(v, 3)
                    print(f"   {k:22s} = {v}")
                except Exception as e:
                    print(f"   {k:22s} ! {e}")

# --- Color management looks: enumerate via OCIO through scene ---
print("\n--- Color management ---")
vs = bpy.context.scene.view_settings
print("   current view_transform:", vs.view_transform, " look:", vs.look)
for cand in ('AgX', 'Filmic', 'Standard', 'Khronos PBR Neutral'):
    try:
        vs.view_transform = cand
        print(f"   view_transform '{cand}' OK")
    except Exception as e:
        print(f"   view_transform '{cand}' FAIL")
vs.view_transform = 'AgX'
for cand in ('None', 'AgX - Punchy', 'AgX - Medium High Contrast', 'AgX - Medium Low Contrast',
             'AgX - Very High Contrast', 'AgX - Very Low Contrast', 'Punchy'):
    try:
        vs.look = cand
        print(f"   look '{cand}' OK")
    except Exception as e:
        print(f"   look '{cand}' FAIL")

# --- Node types availability ---
print("\n--- Node types we plan to use ---")
for ntype in ('ShaderNodeTexNoise', 'ShaderNodeTexBrick', 'ShaderNodeBump', 'ShaderNodeValToRGB',
              'ShaderNodeMixRGB', 'ShaderNodeMix', 'ShaderNodeTexVoronoi', 'ShaderNodeTexWave',
              'ShaderNodeMapRange', 'ShaderNodeTexCoord', 'ShaderNodeMapping', 'ShaderNodeTexMusgrave',
              'ShaderNodeTexImage', 'ShaderNodeAmbientOcclusion', 'ShaderNodeLightPath',
              'ShaderNodeTexGradient', 'ShaderNodeSeparateXYZ', 'ShaderNodeMath'):
    ok = 'YES' if ntype in dir(bpy.types) else 'no'
    print(f"   {ntype:28s} {ok}")

print("\n--- Scene render / film ---")
r = bpy.context.scene.render
for a in ('film_transparent', 'use_compositing', 'use_sequencer', 'filter_size', 'file_format',
          'image_settings', 'engine', 'use_motion_blur', 'dither_intensity'):
    try:
        print(f"   render.{a:22s} = {getattr(r, a)}")
    except Exception:
        pass

print("\n--- Camera DOF / lens API ---")
cd = bpy.data.cameras.new("ProbeCam")
for a in ('dof.use_dof', 'dof.aperture_fstop', 'dof.focus_distance', 'dof.focus_object',
          'lens', 'sensor_width', 'sensor_fit', 'shift_x', 'shift_y', 'clip_start', 'clip_end'):
    obj = cd
    for part in a.split('.'):
        obj = getattr(obj, part)
    print(f"   camera.{a:24s} = {obj}")

print("#" * 90 + "\n")
