"""
import os as _os
_PROJ = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", ".."))
render_hero_v3.py -- production architectural visualisation renders for the
Courtyard Apartments, 15.24 x 30.48 m plot, Nairobi.

Run:
  blender.exe -b "Courtyard Apartments 50x100 v3.blend" --python render_hero_v3.py -- \
      resx=1920 resy=1080 samples=128 quality=final

Useful options (all key=value after the "--"):
  only=01,04          render only these shot numbers
  resx / resy         resolution
  samples             EEVEE TAA samples
  out=<dir>           output directory
  quality=draft|final draft lowers raytracing cost for fast contact sheets

Scene coordinate convention (from the design brief -- IMPORTANT for cameras):
  X:  0 = NORTH boundary ... 15.24 = SOUTH boundary
  Y:  0 = WEST street/gate ... 30.48 = EAST rear
  Z:  0 = street level, 0.90 = GF podium, 4.20/7.20/10.20/13.20 = L1-L4, 16.20 = roof
  Courtyard void: X 6.30-13.44, Y 7.30-23.00   Courtyard lawn: X 7.20-12.50, Y 8.50-19.50
  Feature tree: X 7.76-11.94, Y 12.30-16.70, canopy top Z 8.10
  Colonnade (shaded, under north wing): X 3.60-6.58, Y 5.20-23.00, floor Z 0.91
  North-wing courtyard balconies project south into the void: X 6.30-7.50
  Roof pergola: X 0.80-5.60, Y 10.10-15.88, Z 16.20-19.10
"""

import bpy
import bmesh
import math
import os
import random
import sys
import time
from mathutils import Vector, Matrix

# ═══════════════════════════════════════════════════════════════════════════
#  0.  ARGUMENTS
# ═══════════════════════════════════════════════════════════════════════════
PROJ = _PROJ

_argv = sys.argv
_extra = _argv[_argv.index('--') + 1:] if '--' in _argv else []
ARGS = {}
for _tok in _extra:
    if '=' in _tok:
        _k, _v = _tok.split('=', 1)
        ARGS[_k.strip()] = _v.strip()

OUTDIR = ARGS.get('out', os.path.join(PROJ, 'render', 'hero'))
RES_X = int(ARGS.get('resx', 1920))
RES_Y = int(ARGS.get('resy', 1080))
SAMPLES = int(ARGS.get('samples', 96))
QUALITY = ARGS.get('quality', 'final')
ONLY = [s.strip() for s in ARGS.get('only', '').split(',') if s.strip()]
# lighting overrides -- used for fast exposure/ratio sweeps
SKYMUL = float(ARGS.get('skymul', 1.0))
SUNMUL = float(ARGS.get('sunmul', 1.0))
EXPADD = float(ARGS.get('expadd', 0.0))

random.seed(20261014)
os.makedirs(OUTDIR, exist_ok=True)

SCENE = bpy.context.scene

def log(msg):
    print(f"[hero] {msg}", flush=True)

def safe_set(holder, attr, value, label=None):
    """Set an attribute, tolerating API differences between Blender versions."""
    try:
        setattr(holder, attr, value)
        return True
    except Exception as exc:
        log(f"  (skip) {label or attr}: {exc}")
        return False

def safe_input(node, name, value):
    try:
        node.inputs[name].default_value = value
        return True
    except Exception:
        return False

# ═══════════════════════════════════════════════════════════════════════════
#  1.  HIDE ALL ANNOTATION / COMPLIANCE / HELPER OBJECTS FROM RENDER
# ═══════════════════════════════════════════════════════════════════════════
def hide_annotations():
    hidden = 0
    doomed_types = {'FONT', 'CURVE', 'CAMERA', 'EMPTY', 'LIGHT'}
    for coll_name in ('Annotations',):
        coll = bpy.data.collections.get(coll_name)
        if coll:
            safe_set(coll, 'hide_render', True, 'collection.hide_render')
            for obj in coll.objects:
                obj.hide_render = True
                hidden += 1
            for child in coll.children:
                safe_set(child, 'hide_render', True)
                for obj in child.objects:
                    obj.hide_render = True
                    hidden += 1
    # Belt and braces: kill anything that looks like an annotation by name,
    # plus stray text/curves that would otherwise float through a render.
    kill_words = ('CONFLICT', 'Annotation', 'annotation', 'Label_', 'North_Arrow',
                  'Walkthrough_Path', 'Car_Descent_Path', 'Swept_Path',
                  'Camera_Walkthrough', 'Camera_CarDescent', 'Camera_0', 'Prod_')
    for obj in bpy.data.objects:
        if any(w in obj.name for w in kill_words):
            obj.hide_render = True
            hidden += 1
        elif obj.type in doomed_types and obj.type != 'CAMERA':
            # stray text / curves never belong in a photoreal frame
            if obj.type in ('FONT', 'CURVE'):
                obj.hide_render = True
                hidden += 1
    log(f"annotation/helper objects hidden from render: {hidden}")

# ═══════════════════════════════════════════════════════════════════════════
#  2.  RENDER / COLOUR-MANAGEMENT SETTINGS
# ═══════════════════════════════════════════════════════════════════════════
def configure_render():
    r = SCENE.render
    r.engine = 'BLENDER_EEVEE'
    r.resolution_x = RES_X
    r.resolution_y = RES_Y
    r.resolution_percentage = 100
    r.image_settings.file_format = 'PNG'
    r.image_settings.color_mode = 'RGB'
    r.image_settings.color_depth = '8'
    r.film_transparent = False
    r.use_compositing = False
    r.dither_intensity = 1.0
    r.filter_size = 1.5

    ee = SCENE.eevee
    ee.taa_render_samples = SAMPLES
    safe_set(ee, 'use_shadows', True)
    safe_set(ee, 'use_raytracing', True)
    safe_set(ee, 'ray_tracing_method', 'SCREEN')
    safe_set(ee, 'shadow_ray_count', 4)
    safe_set(ee, 'shadow_step_count', 12)
    safe_set(ee, 'shadow_resolution_scale', 2.0)
    safe_set(ee, 'use_fast_gi', True)
    safe_set(ee, 'fast_gi_method', 'GLOBAL_ILLUMINATION')
    safe_set(ee, 'fast_gi_resolution', '1')
    safe_set(ee, 'fast_gi_ray_count', 4)
    safe_set(ee, 'fast_gi_step_count', 16)
    safe_set(ee, 'fast_gi_distance', 4.0)
    safe_set(ee, 'fast_gi_bias', 0.04)
    safe_set(ee, 'direct_light_intensity', 1.0)
    safe_set(ee, 'indirect_light_intensity', 1.0)
    safe_set(ee, 'clamp_surface_indirect', 6.0)
    safe_set(ee, 'use_volumetric_shadows', False)
    safe_set(ee, 'use_bokeh_jittered', True)

    rt = getattr(ee, 'ray_tracing_options', None)
    if rt:
        safe_set(rt, 'resolution_scale', '1' if QUALITY == 'final' else '2')
        safe_set(rt, 'use_denoise', True)
        safe_set(rt, 'denoise_spatial', True)
        safe_set(rt, 'denoise_bilateral', True)
        safe_set(rt, 'screen_trace_quality', 0.5 if QUALITY == 'final' else 0.25)
        safe_set(rt, 'screen_trace_thickness', 0.15)
        safe_set(rt, 'trace_max_roughness', 0.6)

    vs = SCENE.view_settings
    safe_set(vs, 'view_transform', 'Khronos PBR Neutral')
    safe_set(vs, 'look', 'None')
    safe_set(vs, 'exposure', 0.0)
    safe_set(vs, 'gamma', 1.0)

    log(f"engine={r.engine} {RES_X}x{RES_Y} samples={SAMPLES} quality={QUALITY} "
        f"view={vs.view_transform}/{vs.look}")

def configure_compositor():
    """Blender 5.x moved the scene compositor onto a node group. Try the new
    API, then the legacy one; if neither works we simply render without bloom
    and add the glow in post instead."""
    try:
        ng = bpy.data.node_groups.get('Hero_Compositor')
        if ng is None:
            ng = bpy.data.node_groups.new('Hero_Compositor', 'CompositorNodeTree')
        if hasattr(ng, 'interface') and len(ng.interface.items_tree) == 0:
            ng.interface.new_socket(name='Image', in_out='INPUT',
                                    socket_type='NodeSocketColor')
            ng.interface.new_socket(name='Image', in_out='OUTPUT',
                                    socket_type='NodeSocketColor')
        try:
            SCENE.compositing_node_group = ng
        except Exception:
            safe_set(SCENE, 'use_nodes', True, 'scene.use_nodes')
        tree = ng

        tree.nodes.clear()
        gin = tree.nodes.new('NodeGroupInput')
        gout = tree.nodes.new('NodeGroupOutput')
        glare = tree.nodes.new('CompositorNodeGlare')
        try:
            glare.glare_type = 'BLOOM'
        except Exception:
            glare.glare_type = 'FOG_GLOW'
        safe_set(glare, 'quality', 'HIGH')
        safe_set(glare, 'mix', 0.0)
        safe_set(glare, 'threshold', 1.2)
        safe_set(glare, 'size', 7)
        tree.links.new(gin.outputs[0], glare.inputs['Image'])
        tree.links.new(glare.outputs['Image'], gout.inputs[0])
        SCENE.render.use_compositing = True
        log("compositor bloom rig installed (node-group API)")
        return glare
    except Exception as exc:
        log(f"compositor unavailable ({exc}); rendering without bloom")
        return None

BLOOM_NODE = None

def set_bloom(amount):
    if BLOOM_NODE is not None:
        try:
            BLOOM_NODE.mix = amount
        except Exception:
            pass

# ═══════════════════════════════════════════════════════════════════════════
#  3.  MATERIAL LIBRARY  (procedural, no external textures required)
# ═══════════════════════════════════════════════════════════════════════════
def fresh_material(name):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    return mat, nt

def add_principled(nt, base, rough, metallic=0.0, spec=0.5, ior=1.45,
                   transmission=0.0, alpha=1.0, sheen=0.0):
    b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    safe_input(b, 'Base Color', (base[0], base[1], base[2], 1.0))
    safe_input(b, 'Roughness', rough)
    safe_input(b, 'Metallic', metallic)
    safe_input(b, 'Specular IOR Level', spec)
    safe_input(b, 'IOR', ior)
    safe_input(b, 'Transmission Weight', transmission)
    safe_input(b, 'Alpha', alpha)
    safe_input(b, 'Sheen Weight', sheen)
    return b

def add_output(nt, bsdf):
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return out

def add_coords(nt, scale=(1.0, 1.0, 1.0), rotate=(0.0, 0.0, 0.0)):
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping')
    safe_input(mp, 'Scale', scale)
    safe_input(mp, 'Rotation', rotate)
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
    return mp

def add_noise(nt, vec, scale, detail=8.0, roughness=0.55, distortion=0.0):
    n = nt.nodes.new('ShaderNodeTexNoise')
    safe_input(n, 'Scale', scale)
    safe_input(n, 'Detail', detail)
    safe_input(n, 'Roughness', roughness)
    safe_input(n, 'Distortion', distortion)
    nt.links.new(vec, n.inputs['Vector'])
    return n

def mix_rgb(nt, fac, c1, c2):
    m = nt.nodes.new('ShaderNodeMixRGB')
    nt.links.new(fac, m.inputs['Fac'])
    if isinstance(c1, tuple):
        safe_input(m, 'Color1', (c1[0], c1[1], c1[2], 1.0))
    else:
        nt.links.new(c1, m.inputs['Color1'])
    if isinstance(c2, tuple):
        safe_input(m, 'Color2', (c2[0], c2[1], c2[2], 1.0))
    else:
        nt.links.new(c2, m.inputs['Color2'])
    return m

def add_bump(nt, bsdf, height_socket, strength=0.2, distance=0.02):
    bump = nt.nodes.new('ShaderNodeBump')
    safe_input(bump, 'Strength', strength)
    safe_input(bump, 'Distance', distance)
    nt.links.new(height_socket, bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    return bump

def add_ramp(nt, fac, stops):
    """stops = list of (position, value) where value is float or (r,g,b)"""
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    cr = ramp.color_ramp
    while len(cr.elements) > 1:
        cr.elements.remove(cr.elements[-1])
    first = True
    for pos, val in stops:
        if first:
            el = cr.elements[0]
            first = False
        else:
            el = cr.elements.new(pos)
        el.position = pos
        if isinstance(val, tuple):
            el.color = (val[0], val[1], val[2], 1.0)
        else:
            el.color = (val, val, val, 1.0)
    nt.links.new(fac, ramp.inputs['Fac'])
    return ramp

def build_surface(name, base, base2, rough_lo, rough_hi,
                  noise_scale, bump_strength, metallic=0.0, spec=0.5,
                  detail=8.0, distortion=0.0, bump_scale=None, sheen=0.0):
    """Generic weathered surface: two-tone colour mottle + micro relief bump."""
    mat, nt = fresh_material(name)
    coords = add_coords(nt)
    bsdf = add_principled(nt, base, rough_lo, metallic=metallic, spec=spec, sheen=sheen)
    add_output(nt, bsdf)

    # large-scale colour mottling
    n_big = add_noise(nt, coords.outputs['Vector'], noise_scale, detail=6.0,
                      roughness=0.6, distortion=distortion)
    ramp = add_ramp(nt, n_big.outputs['Fac'],
                    [(0.25, (base[0], base[1], base[2])),
                     (0.75, (base2[0], base2[1], base2[2]))])
    nt.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    # fine roughness break-up
    n_fine = add_noise(nt, coords.outputs['Vector'], bump_scale or noise_scale * 14.0,
                       detail=6.0, roughness=0.5)
    rramp = add_ramp(nt, n_fine.outputs['Fac'],
                     [(0.2, rough_lo), (0.8, rough_hi)])
    nt.links.new(rramp.outputs['Color'], bsdf.inputs['Roughness'])

    # micro relief
    add_bump(nt, bsdf, n_fine.outputs['Fac'], strength=bump_strength, distance=0.015)
    return mat

def build_concrete(name, base=(0.44, 0.43, 0.40), base2=(0.56, 0.55, 0.52),
                   rough=(0.62, 0.86), noise=0.30):
    return build_surface(name, base, base2, rough[0], rough[1], noise,
                         bump_strength=0.28, detail=10.0, bump_scale=3.5)

def build_render_wall(name, base=(0.360, 0.348, 0.320), base2=(0.455, 0.442, 0.408)):
    return build_surface(name, base, base2, 0.72, 0.92, 0.45,
                         bump_strength=0.55, detail=12.0, bump_scale=22.0)

def build_timber(name, base=(0.175, 0.084, 0.034), base2=(0.360, 0.190, 0.078),
                 rough=(0.40, 0.66), vertical=True):
    """Warm timber -- fins, pergola, decking. Grain runs along the member."""
    mat, nt = fresh_material(name)
    coords = add_coords(nt, scale=(1.0, 1.0, 0.06) if vertical else (1.0, 0.06, 1.0))
    bsdf = add_principled(nt, base, 0.55, spec=0.42)
    add_output(nt, bsdf)

    wave = nt.nodes.new('ShaderNodeTexWave')
    safe_set(wave, 'wave_type', 'BANDS')
    safe_set(wave, 'bands_direction', 'Z' if vertical else 'Y')
    safe_input(wave, 'Scale', 2.6)
    safe_input(wave, 'Distortion', 9.0)
    safe_input(wave, 'Detail', 4.0)
    safe_input(wave, 'Detail Scale', 2.0)
    nt.links.new(coords.outputs['Vector'], wave.inputs['Vector'])

    ramp = add_ramp(nt, wave.outputs['Fac'],
                    [(0.15, base), (0.55, base2), (0.95, base)])
    nt.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    grain = add_noise(nt, coords.outputs['Vector'], 3.2, detail=8.0, roughness=0.55)
    rramp = add_ramp(nt, grain.outputs['Fac'], [(0.15, rough[0]), (0.85, rough[1])])
    nt.links.new(rramp.outputs['Color'], bsdf.inputs['Roughness'])
    add_bump(nt, bsdf, grain.outputs['Fac'], strength=0.30, distance=0.008)
    return mat

def build_issb(name, base=(0.300, 0.150, 0.092), base2=(0.372, 0.196, 0.120),
               mortar=(0.400, 0.360, 0.320), scale=2.4):
    """Interlocking stabilised soil blocks -- warm terracotta, fair-faced."""
    mat, nt = fresh_material(name)
    coords = add_coords(nt)
    bsdf = add_principled(nt, base, 0.90, spec=0.32)
    add_output(nt, bsdf)

    brick = nt.nodes.new('ShaderNodeTexBrick')
    safe_input(brick, 'Color1', (base[0], base[1], base[2], 1.0))
    safe_input(brick, 'Color2', (base2[0], base2[1], base2[2], 1.0))
    safe_input(brick, 'Mortar', (mortar[0], mortar[1], mortar[2], 1.0))
    safe_input(brick, 'Scale', scale)
    safe_input(brick, 'Mortar Size', 0.02)
    safe_input(brick, 'Mortar Smooth', 0.5)
    safe_input(brick, 'Brick Width', 0.30)
    safe_input(brick, 'Row Height', 0.11)
    safe_input(brick, 'Bias', 0.0)
    nt.links.new(coords.outputs['Vector'], brick.inputs['Vector'])

    grime = add_noise(nt, coords.outputs['Vector'], 1.1, detail=8.0, roughness=0.55)
    rramp = add_ramp(nt, grime.outputs['Fac'], [(0.2, 0.82), (0.8, 0.96)])
    nt.links.new(rramp.outputs['Color'], bsdf.inputs['Roughness'])
    add_bump(nt, bsdf, brick.outputs['Fac'], strength=0.35, distance=0.010)
    return mat

def build_stone(name, base=(0.400, 0.388, 0.352), base2=(0.470, 0.458, 0.420)):
    """Rendered quarry stone -- coursed, off-white. Mortar kept low-contrast so
    the coursing reads as texture rather than stripes."""
    mat, nt = fresh_material(name)
    coords = add_coords(nt)
    bsdf = add_principled(nt, base, 0.86, spec=0.38)
    add_output(nt, bsdf)

    brick = nt.nodes.new('ShaderNodeTexBrick')
    safe_input(brick, 'Color1', (base[0], base[1], base[2], 1.0))
    safe_input(brick, 'Color2', (base2[0], base2[1], base2[2], 1.0))
    safe_input(brick, 'Mortar', (base[0] * 1.06, base[1] * 1.06, base[2] * 1.06, 1.0))
    safe_input(brick, 'Scale', 1.15)
    safe_input(brick, 'Mortar Size', 0.008)
    safe_input(brick, 'Mortar Smooth', 0.6)
    safe_input(brick, 'Brick Width', 0.40)
    safe_input(brick, 'Row Height', 0.20)
    nt.links.new(coords.outputs['Vector'], brick.inputs['Vector'])

    stipple = add_noise(nt, coords.outputs['Vector'], 18.0, detail=6.0, roughness=0.5)
    mixed = mix_rgb(nt, stipple.outputs['Fac'], brick.outputs['Color'],
                    (base2[0] * 1.06, base2[1] * 1.06, base2[2] * 1.06))
    safe_input(mixed, 'Fac', 0.35)
    nt.links.new(mixed.outputs['Color'], bsdf.inputs['Base Color'])
    add_bump(nt, bsdf, stipple.outputs['Fac'], strength=0.30, distance=0.005)
    return mat

def build_metal(name, base=(0.055, 0.058, 0.062), rough=(0.28, 0.48), metallic=0.85):
    return build_surface(name, base, (base[0] * 2.6, base[1] * 2.6, base[2] * 2.6),
                         rough[0], rough[1], 2.2, bump_strength=0.10,
                         metallic=metallic, detail=6.0, bump_scale=9.0)

def build_glass(name, tint=(0.43, 0.53, 0.58), alpha=0.20):
    """EEVEE-friendly architectural glass: blended + raytraced reflection."""
    mat, nt = fresh_material(name)
    coords = add_coords(nt)
    bsdf = add_principled(nt, tint, 0.05, spec=1.0, ior=1.52, alpha=alpha)
    add_output(nt, bsdf)

    smear = add_noise(nt, coords.outputs['Vector'], 6.0, detail=4.0, roughness=0.5)
    rramp = add_ramp(nt, smear.outputs['Fac'], [(0.1, 0.02), (0.9, 0.09)])
    nt.links.new(rramp.outputs['Color'], bsdf.inputs['Roughness'])

    safe_set(mat, 'blend_method', 'BLEND', 'blend_method')
    safe_set(mat, 'surface_render_method', 'BLENDED', 'surface_render_method')
    safe_set(mat, 'use_backface_culling', False)
    safe_set(mat, 'show_transparent_back', False)
    safe_set(mat, 'use_raytrace_refraction', True, 'use_raytrace_refraction')
    return mat

def build_lawn(name, base=(0.042, 0.058, 0.028), base2=(0.092, 0.118, 0.055)):
    """Turf. Kept deliberately desaturated -- a vivid green reads as astroturf
    under a strong sun, real mown grass does not."""
    mat, nt = fresh_material(name)
    coords = add_coords(nt)
    bsdf = add_principled(nt, base, 0.96, spec=0.22)
    add_output(nt, bsdf)

    # two octaves of mottling so the field is never a flat slab of colour
    blotch = add_noise(nt, coords.outputs['Vector'], 0.32, detail=10.0, roughness=0.65)
    ramp = add_ramp(nt, blotch.outputs['Fac'], [(0.10, base), (0.90, base2)])
    patch = add_noise(nt, coords.outputs['Vector'], 4.5, detail=8.0, roughness=0.6)
    mixed = mix_rgb(nt, patch.outputs['Fac'], ramp.outputs['Color'],
                    (base[0] * 1.9, base[1] * 1.9, base[2] * 1.9))
    safe_input(mixed, 'Fac', 0.45)
    nt.links.new(mixed.outputs['Color'], bsdf.inputs['Base Color'])

    blade = add_noise(nt, coords.outputs['Vector'], 48.0, detail=9.0, roughness=0.6)
    add_bump(nt, bsdf, blade.outputs['Fac'], strength=0.85, distance=0.014)
    return mat

def build_leaf(name, base=(0.024, 0.058, 0.017), base2=(0.062, 0.118, 0.042)):
    mat, nt = fresh_material(name)
    coords = add_coords(nt)
    bsdf = add_principled(nt, base, 0.78, spec=0.42, sheen=0.35)
    add_output(nt, bsdf)

    blotch = add_noise(nt, coords.outputs['Vector'], 2.4, detail=9.0, roughness=0.6)
    ramp = add_ramp(nt, blotch.outputs['Fac'], [(0.15, base), (0.85, base2)])
    nt.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])

    fine = add_noise(nt, coords.outputs['Vector'], 30.0, detail=6.0, roughness=0.5)
    add_bump(nt, bsdf, fine.outputs['Fac'], strength=0.5, distance=0.01)
    # a touch of translucency so back-lit leaves glow instead of going black
    safe_input(bsdf, 'Subsurface Weight', 0.18)
    safe_input(bsdf, 'Subsurface Radius', (0.35, 0.22, 0.08))
    safe_input(bsdf, 'Subsurface Scale', 0.06)
    return mat

def build_paver(name, base=(0.36, 0.355, 0.34), base2=(0.47, 0.46, 0.445)):
    mat, nt = fresh_material(name)
    coords = add_coords(nt)
    bsdf = add_principled(nt, base, 0.86, spec=0.35)
    add_output(nt, bsdf)

    grid = nt.nodes.new('ShaderNodeTexBrick')
    safe_input(grid, 'Color1', (base[0], base[1], base[2], 1.0))
    safe_input(grid, 'Color2', (base2[0], base2[1], base2[2], 1.0))
    safe_input(grid, 'Mortar', (0.24, 0.235, 0.225, 1.0))
    safe_input(grid, 'Scale', 1.1)
    safe_input(grid, 'Mortar Size', 0.02)
    safe_input(grid, 'Brick Width', 0.42)
    safe_input(grid, 'Row Height', 0.42)
    nt.links.new(coords.outputs['Vector'], grid.inputs['Vector'])

    dirt = add_noise(nt, coords.outputs['Vector'], 1.3, detail=8.0, roughness=0.55)
    mixed = mix_rgb(nt, dirt.outputs['Fac'], grid.outputs['Color'], (0.28, 0.27, 0.26))
    safe_input(mixed, 'Fac', 0.22)
    nt.links.new(mixed.outputs['Color'], bsdf.inputs['Base Color'])
    add_bump(nt, bsdf, grid.outputs['Fac'], strength=0.45, distance=0.01)
    return mat

def build_epoxy(name, base=(0.42, 0.43, 0.44), base2=(0.52, 0.53, 0.54)):
    return build_surface(name, base, base2, 0.22, 0.42, 1.6,
                         bump_strength=0.05, spec=0.6, detail=6.0, bump_scale=12.0)

def build_asphalt(name):
    return build_surface(name, (0.078, 0.080, 0.083), (0.125, 0.127, 0.13),
                         0.72, 0.95, 0.9, bump_strength=0.30,
                         detail=12.0, bump_scale=26.0)

def build_plain(name, base, rough=0.7, metallic=0.0, spec=0.4):
    mat, nt = fresh_material(name)
    bsdf = add_principled(nt, base, rough, metallic=metallic, spec=spec)
    add_output(nt, bsdf)
    return mat

def build_emissive(name, colour, strength):
    mat, nt = fresh_material(name)
    em = nt.nodes.new('ShaderNodeEmission')
    safe_input(em, 'Color', (colour[0], colour[1], colour[2], 1.0))
    safe_input(em, 'Strength', strength)
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(em.outputs['Emission'], out.inputs['Surface'])
    return mat

def build_materials():
    """Rebuild every architectural material with procedural detail."""
    specs = {
        'Mat_Concrete':        lambda: build_concrete('Mat_Concrete',
                                                      base=(0.330, 0.325, 0.308),
                                                      base2=(0.430, 0.422, 0.400)),
        'Mat_RC_Slab':         lambda: build_concrete('Mat_RC_Slab',
                                                      base=(0.400, 0.395, 0.378),
                                                      base2=(0.505, 0.498, 0.478), noise=0.35),
        'Mat_Stone_Render':    lambda: build_stone('Mat_Stone_Render'),
        'Mat_ISSB_Terracotta': lambda: build_issb('Mat_ISSB_Terracotta'),
        'Mat_Warm_Timber':     lambda: build_timber('Mat_Warm_Timber'),
        'Mat_Tree_Trunk':      lambda: build_timber('Mat_Tree_Trunk',
                                                    base=(0.13, 0.095, 0.062),
                                                    base2=(0.24, 0.175, 0.115),
                                                    rough=(0.70, 0.92), vertical=False),
        'Mat_Dark_Steel':      lambda: build_metal('Mat_Dark_Steel'),
        'Mat_Roller_Shutter':  lambda: build_metal('Mat_Roller_Shutter',
                                                   base=(0.14, 0.145, 0.15),
                                                   rough=(0.35, 0.55), metallic=0.7),
        'Mat_Glass_Arch':      lambda: build_glass('Mat_Glass_Arch'),
        'Mat_Courtyard_Lawn':  lambda: build_lawn('Mat_Courtyard_Lawn'),
        'Mat_Garden_Foliage':  lambda: build_leaf('Mat_Garden_Foliage'),
        'Mat_Permeable_Paver': lambda: build_paver('Mat_Permeable_Paver'),
        'Mat_Epoxy_Floor':     lambda: build_epoxy('Mat_Epoxy_Floor'),
        'Mat_Hazard_Yellow':   lambda: build_plain('Mat_Hazard_Yellow', (0.72, 0.50, 0.035), 0.60),
        'Mat_Line_White':      lambda: build_plain('Mat_Line_White', (0.80, 0.79, 0.75), 0.72),
        'Mat_Bay_Accessible':  lambda: build_plain('Mat_Bay_Accessible', (0.045, 0.14, 0.34), 0.68),
        'Mat_Bay_EV':          lambda: build_plain('Mat_Bay_EV', (0.035, 0.22, 0.10), 0.68),
        'Mat_Ramp_Groove':     lambda: build_plain('Mat_Ramp_Groove', (0.16, 0.16, 0.16), 0.85),
        # site context materials (new)
        'Mat_Site_Asphalt':    lambda: build_asphalt('Mat_Site_Asphalt'),
        'Mat_Site_Paving':     lambda: build_render_wall('Mat_Site_Paving',
                                                         base=(0.300, 0.292, 0.272),
                                                         base2=(0.382, 0.372, 0.348)),
        'Mat_Site_Kerb':       lambda: build_concrete('Mat_Site_Kerb',
                                                      base=(0.400, 0.395, 0.378),
                                                      base2=(0.500, 0.494, 0.474), noise=0.6),
        'Mat_Neighbour_A':     lambda: build_render_wall('Mat_Neighbour_A',
                                                         base=(0.240, 0.222, 0.198),
                                                         base2=(0.320, 0.300, 0.272)),
        'Mat_Neighbour_B':     lambda: build_render_wall('Mat_Neighbour_B',
                                                         base=(0.208, 0.216, 0.220),
                                                         base2=(0.290, 0.298, 0.302)),
        'Mat_Neighbour_C':     lambda: build_concrete('Mat_Neighbour_C',
                                                      base=(0.262, 0.252, 0.238),
                                                      base2=(0.348, 0.336, 0.318)),
    }

    built, failed = [], []
    for name, fn in specs.items():
        try:
            fn()
            built.append(name)
        except Exception as exc:
            failed.append(f"{name}: {exc}")
    log(f"materials rebuilt: {len(built)} ok, {len(failed)} failed")
    for f in failed:
        log(f"   MATERIAL FAIL {f}")

# ═══════════════════════════════════════════════════════════════════════════
#  4.  SITE CONTEXT  (ground, street, kerb, neighbours, sun disc)
# ═══════════════════════════════════════════════════════════════════════════
def _link(obj, coll_name='Site_Context'):
    coll = bpy.data.collections.get(coll_name)
    if coll is None:
        coll = bpy.data.collections.new(coll_name)
        SCENE.collection.children.link(coll)
    coll.objects.link(obj)
    return obj

def _box(name, x0, x1, y0, y1, z0, z1, mat):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x = x0 + (v.co.x + 0.5) * (x1 - x0)
        v.co.y = y0 + (v.co.y + 0.5) * (y1 - y0)
        v.co.z = z0 + (v.co.z + 0.5) * (z1 - z0)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    obj.data.materials.append(mat)
    return _link(obj)

def _plane(name, size, z, mat):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    s = size / 2.0
    vs = [bm.verts.new((-s, -s, z)), bm.verts.new((s, -s, z)),
          bm.verts.new((s, s, z)), bm.verts.new((-s, s, z))]
    bm.faces.new(vs)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    obj.data.materials.append(mat)
    return _link(obj)

def build_context():
    for existing in list(bpy.data.objects):
        if existing.name.startswith('Site_'):
            bpy.data.objects.remove(existing, do_unlink=True)

    asphalt = bpy.data.materials['Mat_Site_Asphalt']
    paving = bpy.data.materials['Mat_Site_Paving']
    kerb = bpy.data.materials['Mat_Site_Kerb']
    line = bpy.data.materials['Mat_Line_White']

    # ---- ground plane: distant terrain, sits just under the street -------
    _plane('Site_Ground', 900.0, -0.18, asphalt)

    # ---- carriageway, in front of the west (street) boundary -------------
    road = _box('Site_Road', -140.0, 170.0, -58.0, -1.70, -0.16, -0.02, asphalt)

    # ---- kerb + footway against the plot boundary ------------------------
    _box('Site_Kerb', -140.0, 170.0, -1.72, -1.48, -0.16, 0.00, kerb)
    _box('Site_Footway', -140.0, 170.0, -1.48, 0.00, -0.16, 0.005, paving)

    # ---- far footway across the carriageway ------------------------------
    _box('Site_FarKerb', -140.0, 170.0, -22.0, -21.76, -0.16, 0.00, kerb)
    _box('Site_FarFootway', -140.0, 170.0, -21.76, -20.2, -0.16, 0.005, paving)

    # ---- lane markings ---------------------------------------------------
    for i in range(26):
        x = -120.0 + i * 6.0
        _box(f'Site_Lane_{i:02d}', x, x + 3.0, -11.9, -11.75, -0.015, -0.005, line)

    # ---- neighbouring massing: gives the building scale and a skyline ----
    # IMPORTANT: nothing may encroach on the street corridor the cameras stand
    # in (roughly Y -40..0 across the full X range), or a shot renders blank.
    n_mats = [bpy.data.materials[m] for m in
              ('Mat_Neighbour_A', 'Mat_Neighbour_B', 'Mat_Neighbour_C')]
    # adjacent plots flanking the subject plot -- outside the boundary walls,
    # kept low and well clear so they read as context rather than blank slabs
    for x_start, direction in ((-9.0, -1.0), (24.0, 1.0)):
        y = -4.0
        while y < 36.0:
            w = random.uniform(10.0, 16.0)
            h = random.uniform(4.0, 9.5)
            d = random.uniform(10.0, 17.0)
            x0 = min(x_start, x_start + direction * w)
            x1 = max(x_start, x_start + direction * w)
            _box(f'Site_Nbr_{len(bpy.data.objects)}',
                 x0, x1, y, y + d, 0.0, h, random.choice(n_mats))
            y += d + random.uniform(1.5, 4.0)
    # terrace across the carriageway -- front faces start at Y = -46
    x = -150.0
    while x < 175.0:
        w = random.uniform(11.0, 22.0)
        h = random.uniform(5.0, 12.5)
        d = random.uniform(10.0, 18.0)
        _box(f'Site_NbrF_{len(bpy.data.objects)}',
             x, x + w, -46.0, -46.0 + d, 0.0, h, random.choice(n_mats))
        x += w + random.uniform(2.0, 6.0)

    log(f"site context built: {len([o for o in bpy.data.objects if o.name.startswith('Site_')])} objects")

def check_camera_clearance():
    """Warn loudly if any hero camera sits inside site geometry."""
    problems = 0
    for obj in bpy.data.objects:
        if not obj.name.startswith('Site_'):
            continue
        bbox = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
        lo = Vector((min(p.x for p in bbox), min(p.y for p in bbox), min(p.z for p in bbox)))
        hi = Vector((max(p.x for p in bbox), max(p.y for p in bbox), max(p.z for p in bbox)))
        for shot in SHOTS:
            p = Vector(shot['loc'])
            if all(lo[i] <= p[i] <= hi[i] for i in range(3)):
                log(f"  !! CAMERA {shot['name']} is INSIDE {obj.name}")
                problems += 1
    log(f"camera clearance check: {problems} problem(s)")
    return problems

def build_sun_disc(rig):
    """A physical sun disc perfectly aligned with the key light."""
    obj = bpy.data.objects.get('Site_SunDisc')
    if obj:
        bpy.data.objects.remove(obj, do_unlink=True)
    mat = build_emissive('Mat_SunDisc', (1.0, 0.86, 0.66), 60.0)

    me = bpy.data.meshes.new('Site_SunDisc')
    bm = bmesh.new()
    try:
        bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=12, radius=1.0)
    except TypeError:
        bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=12, diameter=1.0)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new('Site_SunDisc', me)
    obj.scale = (11.0, 11.0, 11.0)
    obj.data.materials.append(mat)
    obj.visible_shadow = False
    obj.visible_diffuse = False
    obj.visible_glossy = False
    obj.visible_transmission = False
    obj.visible_volume_scatter = False
    _link(obj, 'Site_Context')
    return obj

# ═══════════════════════════════════════════════════════════════════════════
#  5.  FOLIAGE ENHANCEMENT  (break up the low-poly blobs)
# ═══════════════════════════════════════════════════════════════════════════
def enhance_foliage():
    targets = []
    for obj in bpy.data.objects:
        if obj.type != 'MESH' or obj.hide_render:
            continue
        names = [m.name for m in obj.data.materials if m]
        if any(n in ('Mat_Garden_Foliage',) for n in names):
            targets.append(obj)

    # clouds texture drives the displacement
    tex = bpy.data.textures.get('FoliageNoise')
    if tex is None:
        tex = bpy.data.textures.new('FoliageNoise', type='CLOUDS')
    tex.noise_scale = 0.9
    tex.noise_depth = 3

    done = 0
    for obj in targets:
        if obj.name.startswith('Hero_Leaf'):
            continue
        try:
            sub = obj.modifiers.new('HeroSub', 'SUBSURF')
            sub.levels = 1
            sub.render_levels = 1
            dis = obj.modifiers.new('HeroDisp', 'DISPLACE')
            dis.texture = tex
            dis.strength = 0.30
            dis.mid_level = 0.5
            dis.texture_coords = 'GLOBAL'
            bpy.context.view_layer.objects.active = obj
            for mod_name in ('HeroSub', 'HeroDisp'):
                bpy.ops.object.modifier_apply(modifier=mod_name)
            done += 1
        except Exception as exc:
            log(f"  foliage enhance skipped for {obj.name}: {exc}")
            for m in list(obj.modifiers):
                try:
                    obj.modifiers.remove(m)
                except Exception:
                    pass
    log(f"foliage meshes subdivided + displaced: {done}")

    # ---- leaf clusters over every planting mass, not just the tree --------
    foliage = [o for o in bpy.data.objects
               if o.type == 'MESH' and not o.hide_render
               and not o.name.startswith('Hero_Leaf')
               and any(m and m.name == 'Mat_Garden_Foliage' for m in o.data.materials)]
    if not foliage:
        log("no foliage objects found -- skipping leaf clusters")
        return

    leaf_mat = bpy.data.materials.get('Mat_Garden_Foliage')
    verts, faces = [], []
    try:
        tmpl = bmesh.new()
        try:
            bmesh.ops.create_icosphere(tmpl, subdivisions=1, radius=1.0)
        except TypeError:
            bmesh.ops.create_icosphere(tmpl, subdivisions=1, diameter=1.0)
        t_v = [v.co.copy() for v in tmpl.verts]
        tmpl.verts.ensure_lookup_table()
        t_f = [[v.index for v in f.verts] for f in tmpl.faces]
        tmpl.free()
    except Exception as exc:
        log(f"leaf template failed: {exc}")
        return

    total = 0
    for can in foliage:
        bbox = [can.matrix_world @ Vector(c) for c in can.bound_box]
        lo = Vector((min(p.x for p in bbox), min(p.y for p in bbox), min(p.z for p in bbox)))
        hi = Vector((max(p.x for p in bbox), max(p.y for p in bbox), max(p.z for p in bbox)))
        ctr = (lo + hi) * 0.5
        rad = (hi - lo) * 0.5
        if (hi - lo).length < 0.35:
            continue
        n = int(max(8, min(150, 40.0 * (rad.x + rad.y + rad.z))))
        # Clump size follows the SMALLEST radius of the mass: a 4 m tree canopy
        # and a 0.3 m planter need very different leaf scale. Anything above
        # ~0.4 m across stops reading as foliage and becomes a green rock.
        s_lo = max(0.05, min(0.20, 0.50 * min(rad.x, rad.y, rad.z)))
        for _ in range(n):
            u = random.random() ** (1.0 / 3.0)
            u = 0.58 + 0.46 * u
            theta = math.acos(1.0 - 2.0 * random.random())
            phi = random.random() * 2.0 * math.pi
            dirv = Vector((math.sin(theta) * math.cos(phi),
                           math.sin(theta) * math.sin(phi),
                           math.cos(theta)))
            pos = ctr + Vector((dirv.x * rad.x, dirv.y * rad.y, dirv.z * rad.z)) * u
            s = random.uniform(s_lo, s_lo * 1.8)
            jitter = Matrix.Rotation(random.uniform(0, math.pi), 4, dirv)
            base = len(verts)
            for co in t_v:
                verts.append(pos + (jitter @ (co * s)))
            for f in t_f:
                faces.append([base + i for i in f])
        total += n

    me = bpy.data.meshes.new('Hero_LeafClusters')
    me.from_pydata([tuple(v) for v in verts], [], faces)
    me.update()
    obj = bpy.data.objects.new('Hero_LeafClusters', me)
    obj.data.materials.append(leaf_mat)
    _link(obj, 'Site_Context')
    log(f"leaf clusters added: {len(faces)} faces / {total} clumps over {len(foliage)} planting masses")

    # The base blobs stay as the shaded core of each planting mass. Changing
    # them to a very dark green stops a flat box reading as painted plastic and
    # makes the lit leaf clusters sit on top of a believable shadowed interior.
    core, core_nt = fresh_material('Mat_Foliage_Core')
    cbsdf = add_principled(core_nt, (0.020, 0.029, 0.015), 0.98, spec=0.15)
    add_output(core_nt, cbsdf)
    swapped = 0
    for o in foliage:
        o.data.materials.clear()
        o.data.materials.append(core)
        swapped += 1
    log(f"planting cores darkened: {swapped} mesh(es) -> Mat_Foliage_Core")

# ═══════════════════════════════════════════════════════════════════════════
#  5b.  OPEN THE GLAZED WALLS
#       In the saved model every window/door panel is embedded *inside* a
#       solid wall box -- there is no actual opening, so no daylight reaches
#       any room (and the s.143 glazing claim is not reflected in the geometry).
#       For each glazing panel that sits inside a wall, cut the matching
#       opening and stretch the glass to fill the reveal.
# ═══════════════════════════════════════════════════════════════════════════
STRUCT_MATS = {'Mat_ISSB_Terracotta', 'Mat_Stone_Render', 'Mat_Concrete', 'Mat_RC_Slab'}
GLASS_MATS = {'Mat_Glass_Arch'}
SKIP_WORDS = ('Frame', 'frame', 'Balustrade', 'Rail', 'Handrail', 'Shutter', 'Post',
              'Lintel', 'Coping', 'Sill', 'Screen', 'Groove', 'Line', 'Slab',
              'Threshold', 'Head', 'Cill')
PANEL_WORDS = ('Glaz', 'Glaze', 'Glass', 'Win_', '_Win', 'Door')

def _bbox(obj):
    pts = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi

def open_glazed_walls():
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    panels = []
    for obj in bpy.data.objects:
        if obj.type != 'MESH' or obj.hide_render:
            continue
        mats = {m.name for m in obj.data.materials if m}
        if not mats:
            continue
        if not (mats & GLASS_MATS):
            continue
        if any(w in obj.name for w in SKIP_WORDS):
            continue
        lo, hi = _bbox(obj)
        ext = hi - lo
        thin = min(range(3), key=lambda i: ext[i])
        panels.append(dict(obj=obj, lo=lo, hi=hi, ext=ext, thin=thin))

    hosts = [o for o in bpy.data.objects
             if o.type == 'MESH' and not o.hide_render
             and (STRUCT_MATS & {m.name for m in o.data.materials if m})]

    host_bbox = {h.name: _bbox(h) for h in hosts}
    groups = {}          # host name -> list of panel dicts
    skipped = 0
    for p in panels:
        best, best_vol = None, None
        for h in hosts:
            if h is p['obj']:
                continue
            hlo, hhi = host_bbox[h.name]
            hext = hhi - hlo
            # host must be thicker than the panel along the panel's thin axis
            if hext[p['thin']] < p['ext'][p['thin']] - 1e-4:
                continue
            # and must contain the panel on the other two axes
            ok = True
            for ax in range(3):
                if ax == p['thin']:
                    continue
                if p['lo'][ax] < hlo[ax] - 0.02 or p['hi'][ax] > hhi[ax] + 0.02:
                    ok = False
                    break
            if not ok:
                continue
            vol = hext.x * hext.y * hext.z
            if best_vol is None or vol < best_vol:
                best, best_vol = h, vol
        if best is None:
            skipped += 1
            continue
        groups.setdefault(best.name, []).append(p)

    made = 0
    for host_name, plist in groups.items():
        host = bpy.data.objects[host_name]
        hlo, hhi = host_bbox[host_name]

        # one combined cutter covering every opening in this wall
        bm = bmesh.new()
        for p in plist:
            src = bmesh.new()
            src.from_mesh(p['obj'].data)
            src.transform(p['obj'].matrix_world)
            ax = p['thin']
            c_lo, c_hi = p['lo'][ax], p['hi'][ax]
            n_lo, n_hi = hlo[ax] - 0.05, hhi[ax] + 0.05
            span = max(c_hi - c_lo, 1e-6)
            for v in src.verts:
                t = (v.co[ax] - c_lo) / span
                v.co[ax] = n_lo + t * (n_hi - n_lo)
            me_tmp = bpy.data.meshes.new('tmp_cutter')
            src.to_mesh(me_tmp)
            src.free()
            bm.from_mesh(me_tmp)
            bpy.data.meshes.remove(me_tmp)

            # stretch the glass itself so it fills the reveal
            gme = p['obj'].data
            if not gme.get('hero_stretched'):
                lo_w = p['obj'].matrix_world.inverted()
                for v in gme.vertices:
                    wco = p['obj'].matrix_world @ v.co
                    t = (wco[ax] - c_lo) / span
                    wco[ax] = hlo[ax] + t * (hhi[ax] - hlo[ax])
                    v.co = lo_w @ wco
                gme['hero_stretched'] = 1
                gme.update()

        cutter_me = bpy.data.meshes.new(f'{host_name}_Cutter')
        bm.to_mesh(cutter_me)
        bm.free()
        cutter = bpy.data.objects.new(f'{host_name}_Cutter', cutter_me)
        SCENE.collection.objects.link(cutter)

        try:
            mod = host.modifiers.new('HeroOpenings', 'BOOLEAN')
            mod.operation = 'DIFFERENCE'
            mod.object = cutter
            try:
                mod.solver = 'EXACT'
            except Exception:
                pass
            bpy.context.view_layer.objects.active = host
            bpy.ops.object.modifier_apply(modifier='HeroOpenings')
            made += len(plist)
        except Exception as exc:
            log(f"  opening cut failed on {host_name}: {exc}")
            for m in list(host.modifiers):
                try:
                    host.modifiers.remove(m)
                except Exception:
                    pass
        finally:
            bpy.data.objects.remove(cutter, do_unlink=True)

    log(f"glazed wall openings cut: {made} panel(s) across {len(groups)} wall(s); "
        f"{skipped} panel(s) were already in an opening")
    return made

def dress_furniture():
    """The block furniture is currently textured as timber, which reads as logs.
    Give each piece a plausible material."""
    fabrics = build_surface('Mat_Furniture_Fabric', (0.105, 0.098, 0.092),
                            (0.150, 0.140, 0.130), 0.88, 0.99, 9.0,
                            bump_strength=0.9, spec=0.25, sheen=0.30)
    linen = build_surface('Mat_Furniture_Linen', (0.470, 0.455, 0.425),
                          (0.560, 0.545, 0.515), 0.90, 0.99, 12.0,
                          bump_strength=0.6, spec=0.30)
    wood = build_timber('Mat_Furniture_Wood',
                        base=(0.115, 0.055, 0.020), base2=(0.235, 0.120, 0.045),
                        rough=(0.38, 0.58), vertical=False)
    stone = build_surface('Mat_Furniture_Stone', (0.230, 0.228, 0.225),
                          (0.300, 0.298, 0.295), 0.18, 0.34, 2.0,
                          bump_strength=0.05, spec=0.6)

    rules = [
        (('Sofa', 'Armchair', 'Chair', 'Ottoman', 'Stool'), fabrics),
        (('Bed', 'Bed2', 'BedMaster', 'Mattress', 'Pillow', 'Headboard'), linen),
        (('DiningTable', 'Table', 'Desk', 'Wardrobe', 'Shelf', 'TV',
          'Counter', 'Kitchen_Counter', 'Cabinet', 'Nightstand'), wood),
    ]
    # Any name containing one of these is building fabric, never furniture.
    never = ('Wall', 'Slab', 'Glaz', 'Glaze', 'Glass', 'Win', 'Door', 'Rail',
             'Balustrade', 'Floor', 'Planter', 'Part_', 'Boundary', 'Gallery',
             'Col_', 'Beam', 'Coping', 'Parapet', 'Shaft', 'Screen', 'Hood',
             'Stair', 'Ramp', 'Roof', 'Ceiling', 'Store', 'Lobby', 'Sill',
             'Bench', 'Colonnade', 'Lintel', 'Trellis', 'Balc', 'Balcony',
             'Lawn', 'Plant', 'Foliage', 'Water', 'Tank', 'Groove', 'Frame')

    def is_furniture(name):
        if any(x in name for x in never):
            return None
        for tok in name.split('_'):
            if not tok or tok[0].isdigit():
                continue        # 1Bed / 2BedL / 2BedR are unit descriptors
            for keys, mat in rules:
                if tok in keys:
                    return mat
        return None

    changed = 0
    level_colls = ('L1_Floor', 'L2_Floor', 'L3_Floor', 'L4_Floor', 'GF_Ground')
    for coll_name in level_colls:
        coll = bpy.data.collections.get(coll_name)
        if not coll:
            continue
        for obj in coll.objects:
            if obj.type != 'MESH' or obj.hide_render:
                continue
            mat = is_furniture(obj.name)
            if mat is not None:
                obj.data.materials.clear()
                obj.data.materials.append(mat)
                changed += 1
    log(f"furniture re-dressed: {changed} object(s)")

# ═══════════════════════════════════════════════════════════════════════════
#  6.  LIGHTING RIGS
# ═══════════════════════════════════════════════════════════════════════════
#  bearing is a compass bearing in the PROJECT's frame:
#     N = 0 (points -X),  E = 90 (points +Y),  S = 180 (points +X),  W = 270 (points -Y)
def sun_vector(bearing_deg, elev_deg):
    b = math.radians(bearing_deg)
    e = math.radians(elev_deg)
    h = Vector((-math.cos(b), math.sin(b), 0.0))
    return Vector((h.x * math.cos(e), h.y * math.cos(e), math.sin(e)))

RIGS = {
    # High afternoon sun from the south-south-west. The courtyard is a 7.1 m wide,
    # 15 m deep slot, so only a sun above ~65 deg puts light on the courtyard floor
    # (tan(65) ~ 15.3/7.1). At 73 deg the floor is lit except a shadow band under the
    # south gallery, the north wing and the rear block read lit, the gallery reads
    # shaded -- real modelling without a black courtyard.
    'courtyard': dict(bearing=231.0, elev=73.0,
                      sun_energy=6.4, sun_colour=(1.0, 0.960, 0.905), sun_angle=0.0092,
                      sky_strength=0.25, sky_air=1.0, sky_aerosol=1.0, sky_ozone=1.0,
                      sun_intensity=1.0, exposure=-0.10, bloom=0.0,
                      disc=(1.0, 0.94, 0.84), disc_strength=25.0),

    # Late afternoon golden hour: low sun in the west-south-west. Rakes across
    # the west street facade and back-lights the roof pergola.
    'golden':  dict(bearing=236.0, elev=13.0,
                    sun_energy=5.6, sun_colour=(1.0, 0.635, 0.315), sun_angle=0.018,
                    sky_strength=0.22, sky_air=1.0, sky_aerosol=1.5, sky_ozone=1.2,
                    sun_intensity=1.0, exposure=0.10, bloom=0.55,
                    disc=(1.0, 0.70, 0.40), disc_strength=90.0),

    # Late-morning sun from the south-south-east, used for the interior. The
    # north wing's courtyard glazing faces due south, but the 0.6 m sun hood
    # above it and the 16 m south gallery opposite both cut direct sun out of
    # the window unless the sun is high AND well round to the south. At 168/64
    # a band of the glazing receives direct light.
    'interior': dict(bearing=168.0, elev=64.0,
                     sun_energy=6.0, sun_colour=(1.0, 0.945, 0.865), sun_angle=0.0092,
                     sky_strength=0.30, sky_air=1.0, sky_aerosol=1.0, sky_ozone=1.0,
                     sun_intensity=1.0, exposure=0.10, bloom=0.0,
                     disc=(1.0, 0.92, 0.80), disc_strength=25.0),

    # Neutral high daylight for documentation-style views.
    'noon':    dict(bearing=90.0, elev=78.0,
                    sun_energy=6.4, sun_colour=(1.0, 0.985, 0.960), sun_angle=0.0092,
                    sky_strength=0.30, sky_air=1.0, sky_aerosol=0.8, sky_ozone=1.0,
                    sun_intensity=1.0, exposure=-0.10, bloom=0.0,
                    disc=(1.0, 0.95, 0.88), disc_strength=25.0),
}

def build_world():
    world = SCENE.world
    if world is None:
        world = bpy.data.worlds.new('World')
        SCENE.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()

    sky = nt.nodes.new('ShaderNodeTexSky')
    safe_set(sky, 'sky_type', 'MULTIPLE_SCATTERING')
    safe_set(sky, 'sun_disc', False)      # we place our own aligned disc instead
    safe_set(sky, 'altitude', 1795.0)     # Nairobi
    safe_set(sky, 'ground_albedo', 0.22)

    bg = nt.nodes.new('ShaderNodeBackground')
    safe_input(bg, 'Strength', 1.0)
    out = nt.nodes.new('ShaderNodeOutputWorld')
    nt.links.new(sky.outputs['Color'], bg.inputs['Color'])
    nt.links.new(bg.outputs['Background'], out.inputs['Surface'])
    return sky, bg

SKY_NODE = None
BG_NODE = None

def build_lights():
    for name in ('Sun_Nairobi', 'Sky_Fill'):
        obj = bpy.data.objects.get(name)
        if obj:
            bpy.data.objects.remove(obj, do_unlink=True)

    key = bpy.data.objects.get('Hero_Key_Sun')
    if key is None:
        ld = bpy.data.lights.new('Hero_Key_Sun', type='SUN')
        key = bpy.data.objects.new('Hero_Key_Sun', ld)
        SCENE.collection.objects.link(key)
    key.data.use_shadow = True
    safe_set(key.data, 'use_soft_falloff', True)
    safe_set(key.data, 'shadow_maximum_resolution', 0.0005)

    # Interior fill lights -- hidden unless a shot asks for them.
    # NOTE: use POINT lights with shadows off. Area lights combined with EEVEE
    # raytracing reproducibly hang this machine (render sits at ~1 s CPU per
    # minute indefinitely), and shadowless points are effectively free.
    fills = []
    for i, (loc, energy) in enumerate([
        ((4.60, 10.20, 12.30), 45.0),
        ((4.00, 11.90, 11.80), 28.0),
    ]):
        nm = f'Hero_Fill_{i}'
        old = bpy.data.objects.get(nm)
        if old:
            bpy.data.objects.remove(old, do_unlink=True)
        ld = bpy.data.lights.new(nm, type='POINT')
        ld.energy = energy
        ld.shadow_soft_size = 0.02
        ld.color = (1.0, 0.905, 0.795)
        # kill the specular lobe: a hard point light otherwise leaves a visible
        # bright dot on every flat wall it can see
        try:
            ld.specular_factor = 0.0
        except Exception:
            pass
        try:
            ld.use_shadow = False
        except Exception:
            pass
        o = bpy.data.objects.new(nm, ld)
        o.location = loc
        o.hide_render = True
        SCENE.collection.objects.link(o)
        fills.append(o)
    return key, fills

def set_rig(name, key, fills, sun_disc, override=None):
    rig = dict(RIGS[name])
    if override:
        rig.update(override)
    u = sun_vector(rig['bearing'], rig['elev'])

    # key sun: local -Z is the light travel direction
    key.location = u * 60.0
    key.rotation_euler = u.to_track_quat('Z', 'Y').to_euler()
    key.data.energy = rig['sun_energy'] * SUNMUL
    key.data.color = rig['sun_colour']
    key.data.angle = rig['sun_angle']

    # sky
    if SKY_NODE is not None:
        safe_set(SKY_NODE, 'sun_elevation', math.radians(rig['elev']))
        # Blender's sky rotation convention: 0 = sun due +Y (east), increasing toward +X.
        safe_set(SKY_NODE, 'sun_rotation', math.radians(rig['bearing'] - 90.0))
        safe_set(SKY_NODE, 'air_density', rig['sky_air'])
        safe_set(SKY_NODE, 'aerosol_density', rig['sky_aerosol'])
        safe_set(SKY_NODE, 'ozone_density', rig['sky_ozone'])
        safe_set(SKY_NODE, 'sun_intensity', rig['sun_intensity'])
    if BG_NODE is not None:
        safe_input(BG_NODE, 'Strength', rig['sky_strength'] * SKYMUL)

    # sun disc
    if sun_disc is not None:
        sun_disc.location = u * 900.0
        mat = sun_disc.data.materials[0]
        for n in mat.node_tree.nodes:
            if n.type == 'EMISSION':
                safe_input(n, 'Color', (rig['disc'][0], rig['disc'][1], rig['disc'][2], 1.0))
                safe_input(n, 'Strength', rig['disc_strength'])

    safe_set(SCENE.view_settings, 'exposure', rig['exposure'] + EXPADD)
    set_bloom(rig['bloom'])
    log(f"rig '{name}': sun bearing={rig['bearing']} elev={rig['elev']} "
        f"dir=({u.x:.3f},{u.y:.3f},{u.z:.3f}) energy={key.data.energy:.2f} "
        f"sky={rig['sky_strength'] * SKYMUL:.2f} exp={rig['exposure'] + EXPADD:+.2f}")

# ═══════════════════════════════════════════════════════════════════════════
#  7.  CAMERAS  -- compositions derived from the measured model geometry
# ═══════════════════════════════════════════════════════════════════════════
SHOTS = [
    dict(id='01', name='01_Courtyard_Garden', rig='courtyard', lens=20.0,
         loc=(11.60, 7.45, 2.30), target=(8.60, 20.00, 4.20), dof=None,
         note="Eye level on the podium at the courtyard's west end, looking east "
              "under the feature tree down the light-well: lawn, north-wing "
              "colonnade and stacked balconies left, south gallery right."),

    dict(id='02', name='02_Courtyard_Void_Aerial', rig='courtyard', lens=45.0, roll=90.0,
         loc=(9.85, 8.50, 19.00), target=(9.85, 15.00, 0.90), dof=None,
         note="High above the west end looking down the void (camera rolled 90 deg so "
              "the 15.7 m slot runs across the 16:9 frame): garden layout, tree "
              "canopy from above, all four balcony tiers and the colonnade arcade."),

    dict(id='03', name='03_Street_Facade', rig='golden', lens=28.0,
         rig_override=dict(bearing=214.0, elev=11.0),
         loc=(13.50, -30.00, 3.60), target=(7.00, 0.00, 8.80), dof=None,
         note="From the carriageway at golden hour: the full 20 m west elevation, "
              "timber fins, car portal, guardhouse, pedestrian gate."),

    dict(id='04', name='04_LivingRoom_L3_Courtyard', rig='interior', lens=24.0,
         rig_override=dict(sky_strength=0.30, exposure=0.05),
         loc=(2.90, 13.10, 11.60), target=(6.26, 10.25, 11.40), dof=None,
         note="Inside the north-wing L3 living room (clear space X 2.55-6.15, "
              "Y 7.30-13.50), looking through the 3.5 m glazed wall across the void.",
         fills=True),

    dict(id='05', name='05_L3_Gallery_Overlook', rig='courtyard', lens=28.0,
         loc=(13.80, 12.00, 12.10), target=(7.00, 15.00, 8.20), dof=None,
         note="From the L3 south gallery looking north-west over the balustrade "
              "into the courtyard: north-wing staggered balconies, sun hoods, "
              "colonnade below, feature tree."),

    dict(id='06', name='06_Roof_Pergola_Sunset', rig='golden', lens=22.0,
         rig_override=dict(bearing=262.0, elev=11.0),
         loc=(4.60, 17.20, 17.75), target=(1.40, 4.60, 17.20), dof=None,
         note="Under the roof pergola at golden hour, looking west over the roof "
              "garden, water tanks and the city beyond."),
]

def debug_rays():
    """Cast along each camera axis and report what is actually in the way."""
    dg = bpy.context.evaluated_depsgraph_get()
    for shot in SHOTS:
        o = Vector(shot['loc'])
        d = (Vector(shot['target']) - o).normalized()
        cur, hits = o, []
        for _ in range(7):
            hit, hloc, hnor, idx, obj, mw = SCENE.ray_cast(dg, cur, d)
            if not hit:
                hits.append("sky")
                break
            mat = obj.data.materials[0].name if (obj.type == 'MESH' and obj.data.materials) else '-'
            hits.append(f"{obj.name}({mat})@{(hloc - o).length:.1f}m")
            cur = hloc + d * 0.02
        log(f"  ray {shot['id']}: " + " -> ".join(hits))
    for nm in ('L3_2BedL_Courtyard_Wall', 'L2_2BedL_Courtyard_Wall'):
        w = bpy.data.objects.get(nm)
        if w and w.type == 'MESH':
            log(f"  {nm}: {len(w.data.polygons)} polys after opening cuts")


def build_cameras():
    for shot in SHOTS:
        old = bpy.data.objects.get('HeroCam_' + shot['name'])
        if old:
            bpy.data.objects.remove(old, do_unlink=True)
        cd = bpy.data.cameras.new('HeroCam_' + shot['name'])
        cd.lens = shot['lens']
        cd.sensor_width = 36.0
        cd.sensor_fit = 'AUTO'
        cd.clip_start = 0.08
        cd.clip_end = 3000.0
        cam = bpy.data.objects.new('HeroCam_' + shot['name'], cd)
        SCENE.collection.objects.link(cam)
        cam.location = shot['loc']
        direction = Vector(shot['target']) - Vector(shot['loc'])
        quat = direction.to_track_quat('-Z', 'Y')
        roll = shot.get('roll')
        if roll:
            from mathutils import Quaternion
            quat = quat @ Quaternion((0.0, 0.0, 1.0), math.radians(roll))
        cam.rotation_euler = quat.to_euler()
        shot['cam'] = cam
        if shot.get('dof'):
            fstop, focus = shot['dof']
            cd.dof.use_dof = True
            cd.dof.aperture_fstop = fstop
            cd.dof.focus_distance = focus
    log(f"{len(SHOTS)} hero cameras placed")

# ═══════════════════════════════════════════════════════════════════════════
#  8.  MAIN
# ═══════════════════════════════════════════════════════════════════════════
def main():
    global BLOOM_NODE, SKY_NODE, BG_NODE

    t_start = time.time()
    log(f"output -> {OUTDIR}")
    log(f"shot filter: {ONLY if ONLY else 'all'}")

    hide_annotations()
    configure_render()
    BLOOM_NODE = configure_compositor()
    build_materials()
    open_glazed_walls()
    dress_furniture()
    build_context()
    enhance_foliage()
    SKY_NODE, BG_NODE = build_world()
    key, fills = build_lights()
    sun_disc = build_sun_disc('morning')
    build_cameras()
    check_camera_clearance()
    debug_rays()

    todo = [s for s in SHOTS if not ONLY or s['id'] in ONLY]
    log(f"rendering {len(todo)} shot(s)")

    for shot in todo:
        log("")
        log("=" * 74)
        log(f"  {shot['name']}  ({shot['rig']} rig, {shot['lens']:.0f} mm)")
        log(f"  {shot['note']}")
        log("=" * 74)

        set_rig(shot['rig'], key, fills, sun_disc, shot.get('rig_override'))
        for f in fills:
            f.hide_render = not shot.get('fills', False)

        cam = shot['cam']
        SCENE.camera = cam
        path = os.path.join(OUTDIR, shot['name'] + '.png')
        SCENE.render.filepath = path

        t0 = time.time()
        bpy.ops.render.render(write_still=True)
        dt = time.time() - t0
        kb = os.path.getsize(path) / 1024.0 if os.path.exists(path) else 0.0
        log(f"  -> {path}  ({kb:.0f} KB, {dt:.1f}s)")

    log("")
    log("=" * 74)
    log(f"  COMPLETE in {(time.time() - t_start) / 60.0:.1f} min")
    for shot in todo:
        p = os.path.join(OUTDIR, shot['name'] + '.png')
        state = f"{os.path.getsize(p) / 1024.0:.0f} KB" if os.path.exists(p) else "MISSING"
        log(f"    {shot['name']:34s} {state}")
    log("=" * 74)

main()
