"""
import os as _os
_PROJ = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), ".."))
render_v4.py -- photorealistic render pipeline for the Courtyard Apartments.

Supersedes render_hero_v3.py. Adds over v3:
  * real CC0 HDRI skies (Poly Haven) for environment lighting + reflections,
    with the HDRI's own sun located numerically and a matching shadow-casting
    Sun lamp
  * real CC0 PBR texture sets (diffuse + normal + AO/rough/metal) on every
    architectural surface, correctly scaled in metres
  * real CC0 3-D planting (jacaranda, small tree, potted plants) replacing the
    low-poly blobs where it matters
  * geometry detail pass: bevelled structural edges, window frames/reveals,
    vertical-bar balustrades, downpipes, AC units, street cars
  * multi-format output: 16:9 masters, 4:5 Instagram crops, 9:16 verticals
  * video mode that renders a camera path frame by frame, paced in batches so
    the machine is not cooked

Run:
  blender.exe -b "Courtyard Apartments 50x100 v3.blend" --python scripts\\render_v4.py -- ^
      mode=stills shots=all resx=1920 resy=1080 samples=96 quality=final
"""

import bpy
import bmesh
import json
import math
import os
import random
import sys
import time
from mathutils import Vector, Matrix, Quaternion

# ═══════════════════════════════════════════════════════════════════════════
#  0.  CONFIG
# ═══════════════════════════════════════════════════════════════════════════
PROJ = _PROJ
ASSETS = os.path.join(PROJ, "assets")
HDRI_DIR = os.path.join(ASSETS, "hdri")
TEX_DIR = os.path.join(ASSETS, "textures")
MODEL_DIR = os.path.join(ASSETS, "models")
OUTDIR = os.path.join(PROJ, "render", "v4")

_argv = sys.argv
_extra = _argv[_argv.index('--') + 1:] if '--' in _argv else []
A = {}
for _t in _extra:
    if '=' in _t:
        k, v = _t.split('=', 1)
        A[k.strip()] = v.strip()

MODE = A.get('mode', 'stills')          # stills | video | test
ONLY = [s.strip() for s in A.get('shots', 'all').split(',') if s.strip() and s.strip() != 'all']
RES_X = int(A.get('resx', 1920))
RES_Y = int(A.get('resy', 1080))
SAMPLES = int(A.get('samples', 96))
QUALITY = A.get('quality', 'final')     # final | draft | fast
OUTDIR = A.get('out', OUTDIR)
if not os.path.isabs(OUTDIR):
    OUTDIR = os.path.join(PROJ, OUTDIR)
VIDEO = A.get('video', 'fly')           # fly | orbit
FRAMES = int(A.get('frames', 288))
VSTART = int(A.get('vstart', 1))
BATCH = int(A.get('batch', 24))         # frames per burst before a cooldown
COOLDOWN = int(A.get('cooldown', 12))   # seconds of rest between bursts
ASPECT = A.get('aspect', 'wide')        # wide | ig | vertical
SKYMUL = float(A.get('skymul', 1.0))
SUNMUL = float(A.get('sunmul', 1.0))
EXPADD = float(A.get('expadd', 0.0))
BASE_EXPOSURE = float(A.get('baseexp', 1.05))

random.seed(20261015)
os.makedirs(OUTDIR, exist_ok=True)
SCENE = bpy.context.scene
_T0 = time.time()

def log(m):
    print(f"[v4 {time.time()-_T0:7.1f}s] {m}", flush=True)

def sset(holder, attr, val, label=None):
    try:
        setattr(holder, attr, val); return True
    except Exception as e:
        log(f"  (skip) {label or attr}: {e}"); return False

def sin(node, name, val):
    try:
        node.inputs[name].default_value = val; return True
    except Exception:
        return False

# ═══════════════════════════════════════════════════════════════════════════
#  1.  HIDE ANNOTATIONS / HELPERS
# ═══════════════════════════════════════════════════════════════════════════
def hide_annotations():
    n = 0
    for cname in ('Annotations',):
        c = bpy.data.collections.get(cname)
        if c:
            sset(c, 'hide_render', True)
            for o in c.objects:
                o.hide_render = True; n += 1
    kill = ('CONFLICT', 'Annotation', 'annotation', 'Label_', 'North_Arrow',
            'Walkthrough_Path', 'Car_Descent_Path', 'Swept_Path',
            'Camera_Walkthrough', 'Camera_CarDescent', 'Camera_0', 'Prod_',
            'HeroCam_')
    for o in bpy.data.objects:
        if any(w in o.name for w in kill):
            o.hide_render = True; n += 1
        elif o.type in ('FONT', 'CURVE'):
            o.hide_render = True; n += 1
    log(f"annotations/helpers hidden: {n}")

# ═══════════════════════════════════════════════════════════════════════════
#  2.  RENDER SETTINGS
# ═══════════════════════════════════════════════════════════════════════════
def configure_render():
    r = SCENE.render
    r.engine = 'BLENDER_EEVEE'
    r.resolution_x, r.resolution_y = RES_X, RES_Y
    r.resolution_percentage = 100
    r.image_settings.file_format = 'PNG'
    r.image_settings.color_mode = 'RGB'
    r.film_transparent = False
    r.use_compositing = False
    r.dither_intensity = 1.0
    r.filter_size = 1.5

    ee = SCENE.eevee
    ee.taa_render_samples = SAMPLES
    sset(ee, 'use_shadows', True)
    sset(ee, 'use_raytracing', QUALITY != 'fast')
    sset(ee, 'ray_tracing_method', 'SCREEN')
    sset(ee, 'shadow_ray_count', 4 if QUALITY == 'final' else 2)
    sset(ee, 'shadow_step_count', 12 if QUALITY == 'final' else 6)
    sset(ee, 'shadow_resolution_scale', 2.0 if QUALITY == 'final' else 1.0)
    sset(ee, 'use_fast_gi', True)
    sset(ee, 'fast_gi_method', 'GLOBAL_ILLUMINATION')
    sset(ee, 'fast_gi_resolution', '1')
    sset(ee, 'fast_gi_ray_count', 4)
    sset(ee, 'fast_gi_step_count', 16)
    sset(ee, 'fast_gi_distance', 4.0)
    sset(ee, 'fast_gi_bias', 0.04)
    sset(ee, 'clamp_surface_indirect', 6.0)
    sset(ee, 'indirect_light_intensity', 1.35)
    sset(ee, 'use_volumetric_shadows', False)
    rt = getattr(ee, 'ray_tracing_options', None)
    if rt:
        sset(rt, 'resolution_scale', '1' if QUALITY == 'final' else '2')
        sset(rt, 'use_denoise', True)
        sset(rt, 'screen_trace_quality', 0.5 if QUALITY == 'final' else 0.25)
        sset(rt, 'screen_trace_thickness', 0.15)
        sset(rt, 'trace_max_roughness', 0.6)

    vs = SCENE.view_settings
    sset(vs, 'view_transform', 'Khronos PBR Neutral')   # grade happens in post
    sset(vs, 'look', 'None')
    sset(vs, 'exposure', 0.0)
    log(f"engine={r.engine} {RES_X}x{RES_Y} samples={SAMPLES} quality={QUALITY} aspect={ASPECT}")

# ═══════════════════════════════════════════════════════════════════════════
#  3.  TEXTURE + MATERIAL LIBRARY
# ═══════════════════════════════════════════════════════════════════════════
TEX_INFO = {}
try:
    with open(os.path.join(ASSETS, "texture_info.json"), encoding="utf-8") as f:
        TEX_INFO = json.load(f)
except Exception:
    pass

_IMG = {}

def img(path, non_color=False):
    key = (path, non_color)
    if key in _IMG:
        return _IMG[key]
    if not os.path.exists(path):
        return None
    im = bpy.data.images.load(path, check_existing=True)
    im.colorspace_settings.name = 'Non-Color' if non_color else 'sRGB'
    _IMG[key] = im
    return im

def tex_path(slug, mapname, res='2k', ext='jpg'):
    return os.path.join(TEX_DIR, slug, f"{slug}_{mapname}_{res}.{ext}")

def tex_size_m(slug, default=2.0):
    rec = TEX_INFO.get(slug) or {}
    d = rec.get('dim_x') or 0
    return (d / 1000.0) if d else default

def fresh(name):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.node_tree.nodes.clear()
    return m, m.node_tree

def out_node(nt, bsdf):
    o = nt.nodes.new('ShaderNodeOutputMaterial')
    nt.links.new(bsdf.outputs['BSDF'], o.inputs['Surface'])
    return o

def principled(nt, base=(0.5, 0.5, 0.5), rough=0.7, metallic=0.0, spec=0.5,
               ior=1.45, transmission=0.0, alpha=1.0, sheen=0.0):
    b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    sin(b, 'Base Color', (*base, 1.0))
    sin(b, 'Roughness', rough)
    sin(b, 'Metallic', metallic)
    sin(b, 'Specular IOR Level', spec)
    sin(b, 'IOR', ior)
    sin(b, 'Transmission Weight', transmission)
    sin(b, 'Alpha', alpha)
    sin(b, 'Sheen Weight', sheen)
    return b

def uv_coords(nt, size_m, rotate_z=0.0):
    """UV coords (box-projected in metres at build time) scaled so one texture
    tile spans size_m metres. 3-D object coords cannot be used directly: on an
    axis-aligned wall one of the two sampled components is constant, which is
    what produced the vertical smearing stripes."""
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping')
    s = 1.0 / max(size_m, 0.001)
    sin(mp, 'Scale', (s, s, s))
    sin(mp, 'Rotation', (0.0, 0.0, math.radians(rotate_z)))
    nt.links.new(tc.outputs['UV'], mp.inputs['Vector'])
    return mp

def cube_project_all():
    """Per-face box projection using object-space metres, so every surface gets
    a correctly oriented, real-world-scaled UV. Skipped for imported assets,
    which bring their own UVs."""
    n_obj = n_face = 0
    for o in bpy.data.objects:
        if o.type != 'MESH' or o.hide_render:
            continue
        if o.get('v4_imported'):
            continue
        me = o.data
        if len(me.polygons) == 0:
            continue
        try:
            uvl = me.uv_layers.active or me.uv_layers.new(name='UVMap')
        except Exception:
            continue
        verts = me.vertices
        loops = me.loops
        data = uvl.data
        for poly in me.polygons:
            nx, ny, nz = poly.normal
            ax, ay, az = abs(nx), abs(ny), abs(nz)
            if ax >= ay and ax >= az:
                mode = 0
            elif ay >= az:
                mode = 1
            else:
                mode = 2
            for li in poly.loop_indices:
                co = verts[loops[li].vertex_index].co
                if mode == 0:
                    data[li].uv = (co.y, co.z)
                elif mode == 1:
                    data[li].uv = (co.x, co.z)
                else:
                    data[li].uv = (co.x, co.y)
        n_obj += 1
        n_face += len(me.polygons)
    log(f"box-projected UVs: {n_obj} meshes / {n_face} faces")

def pbr_material(name, slug, size_m=None, tint=(1.0, 1.0, 1.0), rough_mul=1.0,
                 metallic=0.0, bump=0.35, normal_strength=1.0, rough_floor=0.04,
                 rotate=0.0, spec=0.5, extra_break=0.0):
    """Build a full PBR material from a Poly Haven texture set."""
    mat, nt = fresh(name)
    if size_m is None:
        size_m = tex_size_m(slug)
    coords = uv_coords(nt, size_m, rotate)
    bsdf = principled(nt, rough=0.7, metallic=metallic, spec=spec)
    out_node(nt, bsdf)

    d = img(tex_path(slug, 'Diffuse'))
    n = img(tex_path(slug, 'nor_dx'), non_color=True)
    a = img(tex_path(slug, 'arm'), non_color=True)

    if d:
        tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = d
        tex.interpolation = 'Smart'
        nt.links.new(coords.outputs['Vector'], tex.inputs['Vector'])
        if tint != (1.0, 1.0, 1.0):
            mix = nt.nodes.new('ShaderNodeMixRGB')
            mix.blend_type = 'MULTIPLY'
            sin(mix, 'Fac', 1.0)
            nt.links.new(tex.outputs['Color'], mix.inputs['Color1'])
            sin(mix, 'Color2', (*tint, 1.0))
            nt.links.new(mix.outputs['Color'], bsdf.inputs['Base Color'])
        else:
            nt.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    else:
        sin(bsdf, 'Base Color', (*tint, 1.0))

    # large-scale break-up so tiling never reads as wallpaper: multiply the
    # base colour by a slow 2-3 m noise so big walls gain patchiness
    if extra_break > 0 and bsdf.inputs['Base Color'].is_linked:
        src = bsdf.inputs['Base Color'].links[0].from_socket
        big = nt.nodes.new('ShaderNodeTexNoise')
        sin(big, 'Scale', 0.32); sin(big, 'Detail', 5.0); sin(big, 'Roughness', 0.55)
        nt.links.new(coords.outputs['Vector'], big.inputs['Vector'])
        rampb = nt.nodes.new('ShaderNodeValToRGB')
        crb = rampb.color_ramp
        v = 1.0 - extra_break * 0.55
        crb.elements[0].position = 0.15
        crb.elements[0].color = (v, v, v, 1.0)
        crb.elements[1].position = 0.85
        crb.elements[1].color = (1.06, 1.05, 1.03, 1.0)
        nt.links.new(big.outputs['Fac'], rampb.inputs['Fac'])
        mixb = nt.nodes.new('ShaderNodeMixRGB')
        mixb.blend_type = 'MULTIPLY'
        sin(mixb, 'Fac', 1.0)
        nt.links.new(src, mixb.inputs['Color1'])
        nt.links.new(rampb.outputs['Color'], mixb.inputs['Color2'])
        nt.links.new(mixb.outputs['Color'], bsdf.inputs['Base Color'])

    if a:
        arm = nt.nodes.new('ShaderNodeTexImage'); arm.image = a
        arm.interpolation = 'Smart'
        nt.links.new(coords.outputs['Vector'], arm.inputs['Vector'])
        sep = nt.nodes.new('ShaderNodeSeparateColor')
        nt.links.new(arm.outputs['Color'], sep.inputs['Color'])
        # Poly Haven ARM: R = ambient occlusion, G = roughness, B = metallic
        if not bsdf.inputs['Roughness'].is_linked:
            if rough_mul != 1.0:
                mr = nt.nodes.new('ShaderNodeMath'); mr.operation = 'MULTIPLY'
                sin(mr, 'Inputs[1]', rough_mul)
                nt.links.new(sep.outputs['Green'], mr.inputs[0])
                nt.links.new(mr.outputs['Value'], bsdf.inputs['Roughness'])
            else:
                nt.links.new(sep.outputs['Green'], bsdf.inputs['Roughness'])
        if metallic == 0.0:
            nt.links.new(sep.outputs['Blue'], bsdf.inputs['Metallic'])

    if n:
        ntex = nt.nodes.new('ShaderNodeTexImage'); ntex.image = n
        ntex.interpolation = 'Smart'
        nt.links.new(coords.outputs['Vector'], ntex.inputs['Vector'])
        nm = nt.nodes.new('ShaderNodeNormalMap')
        sin(nm, 'Strength', normal_strength)
        nt.links.new(ntex.outputs['Color'], nm.inputs['Color'])
        nt.links.new(nm.outputs['Normal'], bsdf.inputs['Normal'])

    return mat

def plain_material(name, base, rough=0.6, metallic=0.0, spec=0.5, emission=None,
                   emission_strength=1.0):
    mat, nt = fresh(name)
    b = principled(nt, base, rough, metallic=metallic, spec=spec)
    out_node(nt, b)
    if emission:
        sin(b, 'Emission Color', (*emission, 1.0))
        sin(b, 'Emission Strength', emission_strength)
    return mat

def glass_material(name, tint=(0.34, 0.42, 0.45), alpha=0.16, rough=0.03):
    mat, nt = fresh(name)
    b = principled(nt, tint, rough, spec=1.0, ior=1.52, alpha=alpha)
    out_node(nt, b)
    smear = nt.nodes.new('ShaderNodeTexNoise')
    sin(smear, 'Scale', 5.0); sin(smear, 'Detail', 4.0)
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    cr = ramp.color_ramp
    cr.elements[0].position = 0.1; cr.elements[0].color = (0.015,) * 3 + (1,)
    cr.elements[1].position = 0.9; cr.elements[1].color = (0.06,) * 3 + (1,)
    nt.links.new(smear.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], b.inputs['Roughness'])
    sset(mat, 'blend_method', 'BLEND')
    sset(mat, 'surface_render_method', 'BLENDED')
    sset(mat, 'show_transparent_back', False)
    sset(mat, 'use_backtrace', True)
    return mat

MAT = {}

def build_materials():
    MAT['concrete'] = pbr_material('Mat_Concrete', 'concrete_layers_02',
                                   size_m=2.4, tint=(0.86, 0.85, 0.83),
                                   rough_mul=1.0, bump=0.2, extra_break=0.12)
    MAT['slab'] = pbr_material('Mat_RC_Slab', 'concrete_layers_02',
                               size_m=2.8, tint=(1.02, 1.01, 0.99), extra_break=0.10)
    MAT['stone'] = pbr_material('Mat_Stone_Render', 'white_plaster_02',
                                size_m=1.9, tint=(0.94, 0.925, 0.885),
                                bump=0.5, extra_break=0.10)
    MAT['issb'] = pbr_material('Mat_ISSB_Terracotta', 'red_brick_03',
                               size_m=2.1, tint=(1.02, 0.74, 0.58),
                               rough_mul=1.05, bump=0.55, extra_break=0.18)
    MAT['timber'] = pbr_material('Mat_Warm_Timber', 'oak_veneer_01',
                                 size_m=1.5, tint=(0.78, 0.62, 0.44),
                                 rough_mul=0.85, bump=0.3, extra_break=0.10)
    MAT['deck'] = pbr_material('Mat_Timber_Deck', 'weathered_brown_planks',
                               size_m=1.9, tint=(0.80, 0.68, 0.54), extra_break=0.10)
    MAT['paver'] = pbr_material('Mat_Permeable_Paver', 'brick_pavement_03',
                                size_m=2.4, tint=(0.90, 0.89, 0.87), extra_break=0.12)
    MAT['paving'] = pbr_material('Mat_Site_Paving', 'pavement_02',
                                 size_m=2.1, tint=(0.88, 0.87, 0.84), extra_break=0.12)
    MAT['asphalt'] = pbr_material('Mat_Site_Asphalt', 'asphalt_02',
                                  size_m=3.2, tint=(0.46, 0.46, 0.48), extra_break=0.14)
    MAT['lawn'] = pbr_material('Mat_Courtyard_Lawn', 'leafy_grass',
                               size_m=2.0, tint=(0.62, 0.72, 0.48),
                               rough_mul=1.1, bump=0.8, extra_break=0.16)
    MAT['steel'] = pbr_material('Mat_Dark_Steel', 'metal_plate',
                                size_m=0.9, tint=(0.115, 0.118, 0.125),
                                rough_mul=1.0, metallic=0.85, bump=0.35)
    MAT['steel_light'] = pbr_material('Mat_Aluminium', 'metal_plate',
                                      size_m=1.2, tint=(0.52, 0.53, 0.55),
                                      metallic=0.9, bump=0.25)
    MAT['epoxy'] = pbr_material('Mat_Epoxy_Floor', 'concrete_floor_worn_001',
                                size_m=3.0, tint=(0.68, 0.69, 0.70), rough_mul=0.35)
    MAT['glass'] = glass_material('Mat_Glass_Arch')
    MAT['kerb'] = pbr_material('Mat_Site_Kerb', 'concrete_layers_02',
                               size_m=1.6, tint=(0.95, 0.94, 0.91), extra_break=0.12)
    MAT['nbr_a'] = pbr_material('Mat_Neighbour_A', 'white_plaster_02',
                                size_m=2.4, tint=(0.62, 0.585, 0.53), extra_break=0.14)
    MAT['nbr_b'] = pbr_material('Mat_Neighbour_B', 'white_plaster_02',
                                size_m=2.4, tint=(0.53, 0.55, 0.55), extra_break=0.14)
    MAT['nbr_c'] = pbr_material('Mat_Neighbour_C', 'concrete_layers_02',
                                size_m=2.4, tint=(0.60, 0.585, 0.55), extra_break=0.14)
    MAT['line'] = plain_material('Mat_Line_White', (0.62, 0.615, 0.59), 0.72)
    MAT['fabric'] = pbr_material('Mat_Furniture_Fabric', 'white_plaster_02',
                                 size_m=0.6, tint=(0.20, 0.185, 0.17), bump=0.9)
    MAT['linen'] = pbr_material('Mat_Furniture_Linen', 'white_plaster_02',
                                size_m=0.5, tint=(0.74, 0.72, 0.68), bump=0.6)
    MAT['wood'] = pbr_material('Mat_Furniture_Wood', 'oak_veneer_01',
                               size_m=1.1, tint=(0.55, 0.40, 0.26), bump=0.3)
    MAT['foliage'] = plain_material('Mat_Garden_Foliage', (0.055, 0.115, 0.028), 0.72, spec=0.4)
    MAT['foliage_core'] = plain_material('Mat_Foliage_Core', (0.020, 0.032, 0.014), 0.96, spec=0.15)
    MAT['trunk'] = pbr_material('Mat_Tree_Trunk', 'weathered_brown_planks',
                                size_m=0.7, tint=(0.44, 0.36, 0.26), bump=0.6)
    MAT['car_a'] = plain_material('Mat_Car_A', (0.30, 0.31, 0.33), 0.22, metallic=0.55, spec=0.85)
    MAT['car_b'] = plain_material('Mat_Car_B', (0.52, 0.10, 0.09), 0.24, metallic=0.5, spec=0.85)
    MAT['car_glass'] = plain_material('Mat_Car_Glass', (0.045, 0.055, 0.06), 0.10, spec=1.0)
    MAT['tyre'] = plain_material('Mat_Tyre', (0.022, 0.022, 0.024), 0.75)
    MAT['shutter'] = pbr_material('Mat_Roller_Shutter', 'metal_plate',
                                  size_m=0.5, tint=(0.28, 0.28, 0.29), metallic=0.7)
    MAT['sun'] = plain_material('Mat_SunDisc', (1, 1, 1), 0.5,
                                emission=(1.0, 0.90, 0.76), emission_strength=40.0)
    log(f"materials built: {len(MAT)}")

# ═══════════════════════════════════════════════════════════════════════════
#  4.  RE-ASSIGN MATERIALS ON THE EXISTING MODEL
# ═══════════════════════════════════════════════════════════════════════════
MAT_MAP = {
    'Mat_Concrete': 'concrete', 'Mat_RC_Slab': 'slab',
    'Mat_Stone_Render': 'stone', 'Mat_ISSB_Terracotta': 'issb',
    'Mat_Warm_Timber': 'timber', 'Mat_Dark_Steel': 'steel',
    'Mat_Glass_Arch': 'glass', 'Mat_Courtyard_Lawn': 'lawn',
    'Mat_Garden_Foliage': 'foliage', 'Mat_Permeable_Paver': 'paver',
    'Mat_Epoxy_Floor': 'epoxy', 'Mat_Tree_Trunk': 'trunk',
    'Mat_Roller_Shutter': 'shutter', 'Mat_Line_White': 'line',
    'Mat_Hazard_Yellow': None, 'Mat_Bay_Accessible': None, 'Mat_Bay_EV': None,
    'Mat_Ramp_Groove': None, 'Mat_Annotation_Text': None, 'CONFLICT_Red': None,
}

def restyle_model():
    """Swap every model material for its textured v4 equivalent, keeping the
    small utility materials (bay markings, hazard paint) flat."""
    special = {
        'Mat_Hazard_Yellow': plain_material('Mat_Hazard_Yellow', (0.62, 0.44, 0.03), 0.6),
        'Mat_Bay_Accessible': plain_material('Mat_Bay_Accessible', (0.035, 0.12, 0.30), 0.68),
        'Mat_Bay_EV': plain_material('Mat_Bay_EV', (0.03, 0.20, 0.09), 0.68),
        'Mat_Ramp_Groove': plain_material('Mat_Ramp_Groove', (0.13, 0.13, 0.13), 0.85),
    }
    replaced = 0
    for o in bpy.data.objects:
        if o.type != 'MESH' or o.hide_render:
            continue
        for i, m in enumerate(o.data.materials):
            if not m:
                continue
            key = MAT_MAP.get(m.name, 'KEEP')
            if key == 'KEEP':
                continue
            if key is None:
                nm = special.get(m.name)
                if nm is None:
                    continue
            else:
                nm = MAT.get(key)
            if nm is not None:
                o.data.materials[i] = nm
                replaced += 1
    log(f"material slots re-styled: {replaced}")

    # Internal partitions read as exposed brick, which looks unfinished. Real
    # ISSB partitions here would be plastered, so give them the render finish.
    plaster = MAT['stone']
    n = 0
    for o in bpy.data.objects:
        if o.type != 'MESH' or o.hide_render:
            continue
        if 'Part_' in o.name or 'Partition' in o.name:
            for i, m in enumerate(o.data.materials):
                if m and m.name == 'Mat_ISSB_Terracotta':
                    o.data.materials[i] = plaster
                    n += 1
    log(f"internal partitions plastered: {n}")

# ═══════════════════════════════════════════════════════════════════════════
#  5.  OPEN THE GLAZED WALLS  (defect fix carried over from v3)
# ═══════════════════════════════════════════════════════════════════════════
STRUCT_HINT = ('Mat_Concrete', 'Mat_RC_Slab', 'Mat_Stone_Render', 'Mat_ISSB_Terracotta')
SKIP_WORDS = ('Frame', 'frame', 'Balustrade', 'Rail', 'Handrail', 'Shutter', 'Post',
              'Lintel', 'Coping', 'Sill', 'Screen', 'Groove', 'Line', 'Slab',
              'Threshold', 'Head', 'Cill')

def bbox_of(o):
    p = [o.matrix_world @ Vector(c) for c in o.bound_box]
    lo = Vector((min(q.x for q in p), min(q.y for q in p), min(q.z for q in p)))
    hi = Vector((max(q.x for q in p), max(q.y for q in p), max(q.z for q in p)))
    return lo, hi

def open_glazed_walls():
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    panels = []
    for o in bpy.data.objects:
        if o.type != 'MESH' or o.hide_render:
            continue
        mats = {m.name for m in o.data.materials if m}
        if 'Mat_Glass_Arch' not in mats:
            continue
        if any(w in o.name for w in SKIP_WORDS):
            continue
        lo, hi = bbox_of(o)
        ext = hi - lo
        panels.append(dict(obj=o, lo=lo, hi=hi, ext=ext,
                           thin=min(range(3), key=lambda i: ext[i])))
    hosts = [o for o in bpy.data.objects
             if o.type == 'MESH' and not o.hide_render
             and (set(STRUCT_HINT) & {m.name for m in o.data.materials if m})]
    hb = {h.name: bbox_of(h) for h in hosts}
    groups, skipped = {}, 0
    for p in panels:
        best, bvol = None, None
        for h in hosts:
            if h is p['obj']:
                continue
            hlo, hhi = hb[h.name]
            hext = hhi - hlo
            if hext[p['thin']] < p['ext'][p['thin']] - 1e-4:
                continue
            ok = True
            for ax in range(3):
                if ax == p['thin']:
                    continue
                if p['lo'][ax] < hlo[ax] - 0.02 or p['hi'][ax] > hhi[ax] + 0.02:
                    ok = False; break
            if not ok:
                continue
            v = hext.x * hext.y * hext.z
            if bvol is None or v < bvol:
                best, bvol = h, v
        if best is None:
            skipped += 1; continue
        groups.setdefault(best.name, []).append(p)

    made = 0
    for hn, plist in groups.items():
        host = bpy.data.objects[hn]
        hlo, hhi = hb[hn]
        bm = bmesh.new()
        for p in plist:
            src = bmesh.new(); src.from_mesh(p['obj'].data)
            src.transform(p['obj'].matrix_world)
            ax = p['thin']
            c_lo, c_hi = p['lo'][ax], p['hi'][ax]
            n_lo, n_hi = hlo[ax] - 0.05, hhi[ax] + 0.05
            span = max(c_hi - c_lo, 1e-6)
            for v in src.verts:
                t = (v.co[ax] - c_lo) / span
                v.co[ax] = n_lo + t * (n_hi - n_lo)
            tmp = bpy.data.meshes.new('tmpc'); src.to_mesh(tmp); src.free()
            bm.from_mesh(tmp); bpy.data.meshes.remove(tmp)
            g = p['obj'].data
            if not g.get('v4_stretch'):
                inv = p['obj'].matrix_world.inverted()
                for v in g.vertices:
                    w = p['obj'].matrix_world @ v.co
                    t = (w[ax] - c_lo) / span
                    w[ax] = hlo[ax] + t * (hhi[ax] - hlo[ax])
                    v.co = inv @ w
                g['v4_stretch'] = 1
                g.update()
        cm = bpy.data.meshes.new(f'{hn}_cut')
        bm.to_mesh(cm); bm.free()
        cut = bpy.data.objects.new(f'{hn}_cut', cm)
        SCENE.collection.objects.link(cut)
        try:
            mod = host.modifiers.new('V4Open', 'BOOLEAN')
            mod.operation = 'DIFFERENCE'; mod.object = cut
            try:
                mod.solver = 'EXACT'
            except Exception:
                pass
            bpy.context.view_layer.objects.active = host
            bpy.ops.object.modifier_apply(modifier='V4Open')
            made += len(plist)
        except Exception as e:
            log(f"  opening cut failed on {hn}: {e}")
            for m in list(host.modifiers):
                try:
                    host.modifiers.remove(m)
                except Exception:
                    pass
        finally:
            bpy.data.objects.remove(cut, do_unlink=True)
    log(f"glazed openings cut: {made} panels across {len(groups)} walls ({skipped} already open)")

# ═══════════════════════════════════════════════════════════════════════════
#  6.  FURNITURE RE-DRESS
# ═══════════════════════════════════════════════════════════════════════════
def dress_furniture():
    rules = [('fabric', ('Sofa', 'Armchair', 'Chair', 'Ottoman', 'Stool')),
             ('linen', ('Bed', 'Bed2', 'BedMaster', 'Mattress', 'Pillow', 'Headboard')),
             ('wood', ('DiningTable', 'Table', 'Desk', 'Wardrobe', 'Shelf', 'TV',
                       'Counter', 'Kitchen_Counter', 'Cabinet', 'Nightstand'))]
    never = ('Wall', 'Slab', 'Glaz', 'Glaze', 'Glass', 'Win', 'Door', 'Rail',
             'Balustrade', 'Floor', 'Planter', 'Part_', 'Boundary', 'Gallery',
             'Col_', 'Beam', 'Coping', 'Parapet', 'Shaft', 'Screen', 'Hood',
             'Stair', 'Ramp', 'Roof', 'Ceiling', 'Store', 'Lobby', 'Sill',
             'Bench', 'Colonnade', 'Lintel', 'Trellis', 'Balc', 'Balcony',
             'Lawn', 'Plant', 'Foliage', 'Water', 'Tank', 'Groove', 'Frame')

    def pick(name):
        if any(x in name for x in never):
            return None
        for tok in name.split('_'):
            if not tok or tok[0].isdigit():
                continue
            for key, toks in rules:
                if tok in toks:
                    return MAT[key]
        return None

    n = 0
    for cn in ('L1_Floor', 'L2_Floor', 'L3_Floor', 'L4_Floor', 'GF_Ground'):
        c = bpy.data.collections.get(cn)
        if not c:
            continue
        for o in c.objects:
            if o.type != 'MESH' or o.hide_render:
                continue
            m = pick(o.name)
            if m is not None:
                o.data.materials.clear(); o.data.materials.append(m); n += 1
    log(f"furniture re-dressed: {n}")

# ═══════════════════════════════════════════════════════════════════════════
#  7.  GEOMETRY DETAIL PASS
# ═══════════════════════════════════════════════════════════════════════════
def _link(o, coll='V4_Detail'):
    c = bpy.data.collections.get(coll)
    if c is None:
        c = bpy.data.collections.new(coll)
        SCENE.collection.children.link(c)
    c.objects.link(o)
    return o

def new_mesh_obj(name, bm, mat, coll='V4_Detail'):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me)
    if mat:
        o.data.materials.append(mat)
    return _link(o, coll)

def box(name, x0, x1, y0, y1, z0, z1, mat, coll='V4_Detail'):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x = x0 + (v.co.x + 0.5) * (x1 - x0)
        v.co.y = y0 + (v.co.y + 0.5) * (y1 - y0)
        v.co.z = z0 + (v.co.z + 0.5) * (z1 - z0)
    return new_mesh_obj(name, bm, mat, coll)

def cylinder(name, cx, cy, z0, z1, r, mat, seg=16, coll='V4_Detail'):
    bm = bmesh.new()
    try:
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg,
                              radius1=r, radius2=r, depth=(z1 - z0))
    except TypeError:
        bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg,
                              diameter1=r * 2, diameter2=r * 2, depth=(z1 - z0))
    for v in bm.verts:
        v.co.x += cx; v.co.y += cy; v.co.z += (z0 + z1) * 0.5
    return new_mesh_obj(name, bm, mat, coll)

def clear_detail():
    c = bpy.data.collections.get('V4_Detail')
    if c:
        for o in list(c.objects):
            bpy.data.objects.remove(o, do_unlink=True)

def bevel_structure():
    """Small bevel on structural edges -- catches light the way real arrises do."""
    pats = ('Col_', 'Beam_', 'Slab_', 'Parapet', 'GF_Portal', 'GF_Gate_Post',
            'GF_Core_Entry', 'Roof_Pergola', 'Fin_', 'GF_Colonnade_Bench')
    n = 0
    for o in bpy.data.objects:
        if o.type != 'MESH' or o.hide_render:
            continue
        if o.name.startswith(('V4_', 'Site_', 'Hero_')):
            continue
        if not any(o.name.startswith(p) for p in pats):
            continue
        if len(o.data.polygons) > 400:
            continue
        try:
            m = o.modifiers.new('V4Bevel', 'BEVEL')
            m.width = 0.012
            m.segments = 2
            m.limit_method = 'ANGLE'
            m.angle_limit = math.radians(35)
            bpy.context.view_layer.objects.active = o
            bpy.ops.object.modifier_apply(modifier='V4Bevel')
            n += 1
        except Exception:
            for mm in list(o.modifiers):
                try:
                    o.modifiers.remove(mm)
                except Exception:
                    pass
    log(f"bevelled structural objects: {n}")

def box_axes(name, rng, mat, coll='V4_Detail'):
    """rng: dict axis-index -> (lo, hi)."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        for ax in range(3):
            lo, hi = rng[ax]
            v.co[ax] = lo + (v.co[ax] + 0.5) * (hi - lo)
    return new_mesh_obj(name, bm, mat, coll)

def add_window_frames():
    """Slim reveal lining + frame around every opening cut in section 5."""
    n = 0
    for o in list(bpy.data.objects):
        if o.type != 'MESH' or o.hide_render:
            continue
        if o.name.startswith(('V4_', 'Site_', 'Hero_')):
            continue
        mats = {m.name for m in o.data.materials if m}
        if 'Mat_Glass_Arch' not in mats or any(w in o.name for w in SKIP_WORDS):
            continue
        lo, hi = bbox_of(o)
        ext = hi - lo
        ax = min(range(3), key=lambda i: ext[i])
        if ext[ax] > 0.30:
            continue
        a1, a2 = [i for i in range(3) if i != ax]
        t = 0.040
        d = (lo[ax] - 0.055, hi[ax] + 0.055)
        runs = [
            (a1, lo[a1], lo[a1] + t, a2, lo[a2], hi[a2]),
            (a1, hi[a1] - t, hi[a1], a2, lo[a2], hi[a2]),
            (a2, lo[a2], hi[a2], a1, lo[a1], lo[a1] + t),
            (a2, hi[a2] - t, hi[a2], a1, lo[a1], hi[a1]),
        ]
        for i, (ka, va0, va1, kb, vb0, vb1) in enumerate(runs):
            rng = {ax: d, ka: (va0, va1), kb: (vb0, vb1)}
            box_axes(f'{o.name}_v4fr{i}', rng, MAT['steel_light'])
        n += 1
    log(f"glazing units given reveal frames: {n}")

def add_balustrades():
    """Vertical-bar infill on balustrades (s.17: gaps < 100 mm)."""
    made = 0
    for o in list(bpy.data.objects):
        if o.type != 'MESH' or o.hide_render:
            continue
        if 'Balustrade' not in o.name or o.name.startswith('V4_'):
            continue
        lo, hi = bbox_of(o)
        ext = hi - lo
        if ext.z < 0.6:
            continue
        run = 0 if ext.x >= ext.y else 1
        length = ext[run]
        if length < 1.0:
            continue
        nb = max(2, int(length / 0.085))
        thin = 1 - run
        c = (lo[thin] + hi[thin]) * 0.5
        for i in range(nb):
            t = (i + 0.5) / nb
            p = lo[run] + t * ext[run]
            rng = {}
            rng[run] = (p - 0.009, p + 0.009)
            rng[thin] = (c - ext[thin] * 0.16, c + ext[thin] * 0.16)
            rng[2] = (lo.z + 0.05, hi.z - 0.02)
            box_axes(f'{o.name}_v4bar{i}', rng, MAT['steel'])
        made += 1
    log(f"balustrades given vertical-bar infill: {made}")

def add_car(name, cx, cy, angle_deg, mat_body, scale=1.0):
    """Simple believable car built directly in world space."""
    L, W, H = 4.35 * scale, 1.82 * scale, 0.70 * scale
    ca, sa = math.cos(math.radians(angle_deg)), math.sin(math.radians(angle_deg))

    def place(bm, mat, nm):
        for v in bm.verts:
            x, y, z = v.co.x, v.co.y, v.co.z
            v.co.x = cx + x * ca - y * sa
            v.co.y = cy + x * sa + y * ca
            v.co.z = z
        return new_mesh_obj(nm, bm, mat)

    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= L; v.co.y *= W; v.co.z = v.co.z * H * 0.62 + H * 0.42
    bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                    offset=0.06 * scale, segments=2, affect='EDGES')
    body = place(bm, mat_body, name + '_body')

    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= L * 0.50; v.co.y *= W * 0.84
        v.co.z = v.co.z * H * 0.50 + H * 0.72
        if v.co.x > 0:
            v.co.x *= 0.84
    bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                    offset=0.05 * scale, segments=2, affect='EDGES')
    place(bm, MAT['car_glass'], name + '_cabin')

    for sx in (-L * 0.33, L * 0.33):
        for sy in (-W * 0.50, W * 0.50):
            bm = bmesh.new()
            try:
                bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16,
                                      radius1=0.33 * scale, radius2=0.33 * scale,
                                      depth=0.20 * scale)
            except TypeError:
                bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16,
                                      diameter1=0.66 * scale, diameter2=0.66 * scale,
                                      depth=0.20 * scale)
            for v in bm.verts:
                x, y, z = v.co.x, v.co.y, v.co.z
                v.co.x = sx + z
                v.co.y = sy
                v.co.z = 0.33 * scale + x
            place(bm, MAT['tyre'], f'{name}_w')
    return body

def join_detail():
    """Collapse the detail collection down to a handful of objects -- 1400+
    objects would otherwise dominate depsgraph evaluation on this CPU."""
    c = bpy.data.collections.get('V4_Detail')
    if not c or len(c.objects) < 2:
        return
    buckets = {}
    for o in list(c.objects):
        if o.type != 'MESH':
            continue
        key = o.data.materials[0].name if o.data.materials else 'none'
        buckets.setdefault(key, []).append(o)

    def join(objs, newname):
        if len(objs) < 2:
            return
        for o in bpy.data.objects:
            o.select_set(False)
        for o in objs:
            o.select_set(True)
        bpy.context.view_layer.objects.active = objs[0]
        try:
            bpy.ops.object.join()
        except Exception as e:
            log(f"  join failed for {newname}: {e}")
            return
        objs[0].name = newname

    for key, objs in buckets.items():
        join(objs, f'V4_Joined_{key[:24]}')
    log(f"detail joined to {len(bpy.data.collections['V4_Detail'].objects)} objects")

def build_detail():
    clear_detail()
    add_window_frames()
    add_balustrades()
    # downpipes on the street elevation
    for i, x in enumerate((2.2, 9.6, 14.4)):
        cylinder(f'V4_Downpipe_{i}', x, -0.22, 0.0, 16.0, 0.055, MAT['steel_light'])
    # AC condenser units on the roof plant zone
    for i in range(3):
        box(f'V4_AC_{i}', 12.0 + i * 1.1, 12.7 + i * 1.1, 20.0, 20.8, 16.30, 17.05, MAT['steel_light'])
    # a couple of cars on the street and one at the portal
    add_car('V4_Car_1', -6.5, -7.4, 92, MAT['car_a'])
    add_car('V4_Car_2', 9.5, -13.2, 268, MAT['car_b'])
    add_car('V4_Car_3', 1.7, -9.4, 178, MAT['car_a'], scale=0.97)
    join_detail()
    log(f"detail objects: {len(bpy.data.collections['V4_Detail'].objects)}")

# ═══════════════════════════════════════════════════════════════════════════
#  8.  PLANTING  (real models where available, clumps otherwise)
# ═══════════════════════════════════════════════════════════════════════════
def _import_blend(path, names_filter=None):
    """Append objects from a Poly Haven .blend, return the new objects."""
    before = set(bpy.data.objects.keys())
    try:
        with bpy.data.libraries.load(path, link=False) as (src, dst):
            want = [n for n in src.objects if not names_filter or names_filter(n)]
            dst.objects = want
    except Exception as e:
        log(f"  model import failed {os.path.basename(path)}: {e}")
        return []
    new = [bpy.data.objects[n] for n in bpy.data.objects.keys() if n not in before]
    for o in new:
        o['v4_imported'] = 1
    return new

def _bbox_all(objs):
    pts = []
    for o in objs:
        if o.type == 'MESH':
            pts += [o.matrix_world @ Vector(c) for c in o.bound_box]
    if not pts:
        return None
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi

def _group_bounds(objs):
    """World-space bounds of a group, evaluated (bound_box on the evaluated
    object, so modifiers and parenting are respected)."""
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for o in objs:
        if o.type != 'MESH':
            continue
        try:
            ev = o.evaluated_get(dg)
            mw = ev.matrix_world
            for c in ev.bound_box:
                pts.append(mw @ Vector(c))
        except Exception:
            continue
    if not pts:
        return None
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi

def place_model_group(objs, target_center, target_height, rot_z=0.0, tag='mdl'):
    """Scale a group to a target height and put its base at a point.

    Applies the transform straight onto each top-level object's world matrix --
    parenting through an empty proved unreliable with appended Poly Haven files.
    """
    meshes = [o for o in objs if o.type == 'MESH']
    if not meshes:
        log(f"    '{tag}': no mesh objects to place")
        return None
    bb = _group_bounds(meshes)
    if not bb:
        return None
    lo, hi = bb
    h = hi.z - lo.z
    if h < 0.05:
        log(f"    '{tag}': degenerate bounds (h={h:.3f}) -- skipped")
        for o in meshes:
            o.hide_render = True
        return None
    s = target_height / h
    ctr = (lo + hi) * 0.5

    R = Matrix.Rotation(math.radians(rot_z), 4, 'Z')
    S = Matrix.Diagonal((s, s, s, 1.0))
    # move group centre to the target in X/Y and its base to target Z
    off = Vector((target_center[0], target_center[1],
                  target_center[2] + target_height * 0.5)) - (R @ (S @ ctr))
    M = Matrix.Translation(off) @ R @ S

    tops = [o for o in objs if o.parent is None]
    for o in tops:
        o.matrix_world = M @ o.matrix_world
    bpy.context.view_layer.update()
    bb2 = _group_bounds(meshes)
    if bb2:
        log(f"    placed '{tag}': scale={s:.3f} bbox "
            f"X[{bb2[0].x:.2f},{bb2[1].x:.2f}] Y[{bb2[0].y:.2f},{bb2[1].y:.2f}] "
            f"Z[{bb2[0].z:.2f},{bb2[1].z:.2f}]")
    return tops[0] if tops else None

def alpha_material(name, texpath, tint=(1.0, 1.0, 1.0), rough=0.62, translucency=0.30):
    """Alphacut card material for foliage."""
    mat, nt = fresh(name)
    b = principled(nt, tint, rough, spec=0.35)
    out_node(nt, b)
    im = img(texpath)
    if im:
        t = nt.nodes.new('ShaderNodeTexImage')
        t.image = im
        t.interpolation = 'Smart'
        t.extension = 'CLIP'
        nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
        nt.links.new(t.outputs['Alpha'], b.inputs['Alpha'])
    sin(b, 'Subsurface Weight', translucency)
    sin(b, 'Subsurface Radius', (0.9, 0.55, 0.22))
    sin(b, 'Subsurface Scale', 0.10)
    # EEVEE Next uses surface_render_method. Setting the legacy blend_method too
    # appears to be what deadlocked the renderer (CPU froze, no progress), so
    # only the modern property is touched here.
    sset(mat, 'surface_render_method', 'DITHERED')
    sset(mat, 'use_backface_culling', False)
    return mat

def build_leaf_cards(volumes, mat, size_lo, size_hi, density, tag,
                     shells=(0.72, 1.04), upward_bias=0.0):
    """Scatter alpha-cut leaf cards through a set of canopy volumes and return a
    single joined mesh. A few hundred quads read as real foliage."""
    bm = bmesh.new()
    uv_layer = bm.loops.layers.uv.new('UVMap')
    made = 0
    for vol in volumes:
        lo, hi = bbox_of(vol)
        rad = (hi - lo) * 0.5
        ctr = (lo + hi) * 0.5
        if (hi - lo).length < 0.25:
            continue
        n = int(max(14, min(420, density * (4.0 / 3.0) * math.pi *
                            rad.x * rad.y * rad.z)))
        for _ in range(n):
            u = random.random() ** (1.0 / 3.0)
            u = shells[0] + (shells[1] - shells[0]) * u
            th = math.acos(1.0 - 2.0 * random.random())
            ph = random.random() * 2 * math.pi
            d = Vector((math.sin(th) * math.cos(ph),
                        math.sin(th) * math.sin(ph),
                        math.cos(th)))
            pos = ctr + Vector((d.x * rad.x, d.y * rad.y, d.z * rad.z)) * u
            s = random.uniform(size_lo, size_hi)
            if upward_bias > 0:
                tilt = (1.0 - upward_bias) * (random.random() - 0.5) * math.pi
                rot = Matrix.Rotation(random.random() * 2 * math.pi, 4, 'Z') @ \
                      Matrix.Rotation(tilt, 4, 'X')
            else:
                rot = (Matrix.Rotation(random.random() * 2 * math.pi, 4, 'Z') @
                       Matrix.Rotation((random.random() - 0.5) * math.pi, 4, 'Y') @
                       Matrix.Rotation(random.random() * 2 * math.pi, 4, 'X'))
            h = s * 0.5
            corners = [Vector((-h, -h, 0)), Vector((h, -h, 0)),
                       Vector((h, h, 0)), Vector((-h, h, 0))]
            vs = [bm.verts.new(pos + (rot @ c)) for c in corners]
            f = bm.faces.new(vs)
            f.smooth = False
            uvs = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
            for lp, uv in zip(f.loops, uvs):
                lp[uv_layer].uv = uv
            made += 1
    me = bpy.data.meshes.new(f'V4_Cards_{tag}')
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(f'V4_Cards_{tag}', me)
    o.data.materials.append(mat)
    o['v4_imported'] = 1          # keep the box-projection pass off our UVs
    # Alpha-cut geometry is expensive in the shadow pass and the dark canopy
    # core underneath still casts, so the cards themselves do not.
    try:
        o.visible_shadow = False
    except Exception:
        pass
    # NB: must NOT go into V4_Detail -- build_detail() clears that collection,
    # which silently deleted every card on the first attempt.
    _link(o, 'V4_Planting')
    log(f"    leaf cards '{tag}': {made} cards")
    return o

def enhance_planting():
    """Subdivide + displace the existing low-poly planting, add scatter clumps,
    then swap the courtyard feature tree for a real jacaranda if we have one."""
    # darken the base blobs first
    core = MAT['foliage_core']
    targets = []
    for o in bpy.data.objects:
        if o.type != 'MESH' or o.hide_render:
            continue
        if any(m and m.name == 'Mat_Garden_Foliage' for m in o.data.materials):
            targets.append(o)
    for o in targets:
        o.data.materials.clear()
        o.data.materials.append(core)
    log(f"planting cores darkened: {len(targets)}")

    # ---- leaf cards replace the icosphere clumps -------------------------
    foliage = targets
    gen = os.path.join(ASSETS, 'generated')
    mat_tree = alpha_material('Mat_Leaf_Tree', os.path.join(gen, 'leaf_tree.png'),
                              tint=(1.0, 1.0, 1.0), rough=0.58)
    mat_shrub = alpha_material('Mat_Leaf_Shrub', os.path.join(gen, 'leaf_shrub.png'),
                               tint=(0.92, 0.96, 0.90), rough=0.64)
    mat_hang = alpha_material('Mat_Leaf_Hanging', os.path.join(gen, 'leaf_hanging.png'),
                              tint=(0.94, 0.98, 0.92), rough=0.60)

    canopies = [o for o in bpy.data.objects
                if o.type == 'MESH' and o.name.startswith('GF_Tree_Canopy')]
    beds = [o for o in foliage if o not in canopies and min(
        (bbox_of(o)[1] - bbox_of(o)[0]).x, (bbox_of(o)[1] - bbox_of(o)[0]).y,
        (bbox_of(o)[1] - bbox_of(o)[0]).z) < 1.2]
    bulky = [o for o in foliage if o not in canopies and o not in beds]

    if canopies:
        build_leaf_cards(canopies, mat_tree, 1.6, 2.8, 14.0, 'tree',
                         shells=(0.60, 1.02))
    if bulky:
        build_leaf_cards(bulky, mat_shrub, 0.42, 0.78, 9.0, 'shrub',
                         shells=(0.55, 1.05))
    if beds:
        build_leaf_cards(beds, mat_hang, 0.34, 0.62, 8.0, 'bed',
                         shells=(0.40, 1.15), upward_bias=0.35)

    # ---- courtyard feature tree: cards over the existing canopy volumes ---
    p = os.path.join(MODEL_DIR, 'potted_plant_02_1k.blend')
    if os.path.exists(p):
        spots = [(7.95, 9.20, 1.36), (11.60, 10.60, 1.36), (7.95, 19.10, 1.36),
                 (11.60, 18.30, 1.36), (3.10, 11.60, 16.30), (4.90, 14.40, 16.30)]
        for i, sp in enumerate(spots):
            objs = _import_blend(p, lambda n: not n.startswith('_'))
            if not objs:
                break
            place_model_group([o for o in objs if o.type == 'MESH'], sp,
                              random.uniform(0.75, 1.15), rot_z=random.uniform(0, 360),
                              tag=f'pot{i}')
        log(f"potted plants placed: {len(spots)}")

# ═══════════════════════════════════════════════════════════════════════════
#  9.  SITE CONTEXT
# ═══════════════════════════════════════════════════════════════════════════
def build_context():
    c = bpy.data.collections.get('V4_Site')
    if c:
        for o in list(c.objects):
            bpy.data.objects.remove(o, do_unlink=True)
    else:
        c = bpy.data.collections.new('V4_Site')
        SCENE.collection.children.link(c)

    def bx(name, x0, x1, y0, y1, z0, z1, mat):
        return box(name, x0, x1, y0, y1, z0, z1, mat, coll='V4_Site')

    bm = bmesh.new()
    s = 450.0
    vs = [bm.verts.new((-s, -s, -0.20)), bm.verts.new((s, -s, -0.20)),
          bm.verts.new((s, s, -0.20)), bm.verts.new((-s, s, -0.20))]
    bm.faces.new(vs)
    new_mesh_obj('V4_Ground', bm, MAT['asphalt'], 'V4_Site')

    bx('V4_Road', -150, 180, -60, -1.70, -0.16, -0.02, MAT['asphalt'])
    bx('V4_Kerb', -150, 180, -1.72, -1.48, -0.16, 0.00, MAT['kerb'])
    bx('V4_Footway', -150, 180, -1.48, 0.00, -0.16, 0.005, MAT['paving'])
    bx('V4_FarKerb', -150, 180, -22.0, -21.76, -0.16, 0.00, MAT['kerb'])
    bx('V4_FarFootway', -150, 180, -21.76, -20.2, -0.16, 0.005, MAT['paving'])
    for i in range(26):
        x = -120.0 + i * 6.0
        bx(f'V4_Lane_{i}', x, x + 3.0, -11.9, -11.75, -0.015, -0.005, MAT['line'])
    # zebra crossing near the gate
    for i in range(9):
        y = -6.4 + i * 0.62
        bx(f'V4_Zebra_{i}', 4.4, 8.6, y, y + 0.34, -0.014, -0.006, MAT['line'])

    nmat = [MAT['nbr_a'], MAT['nbr_b'], MAT['nbr_c']]
    for x0, direction in ((-9.0, -1.0), (24.0, 1.0)):
        y = -4.0
        while y < 36.0:
            w = random.uniform(10.0, 16.0); h = random.uniform(4.0, 9.5)
            d = random.uniform(10.0, 17.0)
            a, b = sorted((x0, x0 + direction * w))
            bx(f'V4_Nbr_{len(c.objects)}', a, b, y, y + d, 0.0, h, random.choice(nmat))
            y += d + random.uniform(1.5, 4.0)
    x = -150.0
    while x < 180.0:
        w = random.uniform(11.0, 22.0); h = random.uniform(5.0, 12.5)
        d = random.uniform(10.0, 18.0)
        bx(f'V4_NbrF_{len(c.objects)}', x, x + w, -46.0, -46.0 + d, 0.0, h, random.choice(nmat))
        x += w + random.uniform(2.0, 6.0)
    log(f"site context: {len(c.objects)} objects")

def check_clearance(shots):
    bad = 0
    for o in bpy.data.objects:
        if not o.name.startswith(('V4_', 'Site_')):
            continue
        if 'Joined' in o.name or 'LeafClusters' in o.name:
            continue        # union meshes span the building; bbox test is meaningless
        lo, hi = bbox_of(o)
        for s in shots:
            p = Vector(s['loc'])
            if all(lo[i] <= p[i] <= hi[i] for i in range(3)):
                log(f"  !! camera {s.get('name')} inside {o.name}"); bad += 1
    log(f"camera clearance: {bad} problem(s)")

# ═══════════════════════════════════════════════════════════════════════════
#  10.  WORLD / SKY
# ═══════════════════════════════════════════════════════════════════════════
def hdri_sun_direction(path):
    """Find the brightest direction in an equirectangular HDRI (numpy)."""
    try:
        import numpy as np
    except Exception:
        return None
    try:
        im = bpy.data.images.load(path, check_existing=False)
        w, h = im.size
        n = w * h * 4
        buf = np.empty(n, dtype=np.float32)
        im.pixels.foreach_get(buf)
        arr = buf.reshape(h, w, 4)[:, :, :3]
        lum = arr[:, :, 0] * 0.2126 + arr[:, :, 1] * 0.7152 + arr[:, :, 2] * 0.0722
        # ignore the top/bottom 6% where equirect distortion blows up
        lo = int(h * 0.06); hi = int(h * 0.94)
        sub = lum[lo:hi, :]
        iy, ix = np.unravel_index(int(np.argmax(sub)), sub.shape)
        iy += lo
        # Blender image rows run bottom-to-top
        u = (ix + 0.5) / w
        v = (iy + 0.5) / h
        theta = (1.0 - v) * math.pi          # polar from +Z
        phi = (u - 0.5) * 2.0 * math.pi      # azimuth
        d = Vector((math.sin(theta) * math.cos(phi),
                    math.sin(theta) * math.sin(phi),
                    math.cos(theta)))
        bpy.data.images.remove(im)
        return d, math.degrees(math.asin(max(-1, min(1, d.z))))
    except Exception as e:
        log(f"  hdri sun detect failed: {e}")
        return None

SKY = {'node': None, 'bg': None, 'tex': None}

def build_world():
    w = SCENE.world or bpy.data.worlds.new('World')
    SCENE.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping')
    tex = nt.nodes.new('ShaderNodeTexEnvironment')
    bg = nt.nodes.new('ShaderNodeBackground')
    outn = nt.nodes.new('ShaderNodeOutputWorld')
    nt.links.new(tc.outputs['Generated'], mp.inputs['Vector'])
    nt.links.new(mp.outputs['Vector'], tex.inputs['Vector'])
    nt.links.new(tex.outputs['Color'], bg.inputs['Color'])
    nt.links.new(bg.outputs['Background'], outn.inputs['Surface'])
    sin(bg, 'Strength', 1.0)
    SKY.update(node=mp, bg=bg, tex=tex)
    return mp, bg, tex

def set_sky(hdri_file, rot_z_deg=0.0, strength=1.0, sun_align=True):
    p = os.path.join(HDRI_DIR, hdri_file)
    if not os.path.exists(p):
        log(f"  !! missing HDRI {hdri_file}")
        return None
    if SKY['tex'].image is None or os.path.basename(
            SKY['tex'].image.filepath or '') != hdri_file:
        SKY['tex'].image = img(p)
    sin(SKY['node'], 'Rotation', (0.0, 0.0, math.radians(rot_z_deg)))
    sin(SKY['bg'], 'Strength', strength)
    return p

# ═══════════════════════════════════════════════════════════════════════════
#  11.  LIGHTS
# ═══════════════════════════════════════════════════════════════════════════
def bearing_vec(bearing_deg, elev_deg):
    """Compass bearing in the project frame: -X = N, +Y = E, +X = S, -Y = W."""
    b = math.radians(bearing_deg); e = math.radians(elev_deg)
    h = Vector((-math.cos(b), math.sin(b), 0.0))
    return Vector((h.x * math.cos(e), h.y * math.cos(e), math.sin(e)))

def build_lights():
    for n in ('Sun_Nairobi', 'Sky_Fill', 'Hero_Key_Sun'):
        o = bpy.data.objects.get(n)
        if o:
            bpy.data.objects.remove(o, do_unlink=True)
    ld = bpy.data.lights.new('V4_Key_Sun', type='SUN')
    key = bpy.data.objects.new('V4_Key_Sun', ld)
    SCENE.collection.objects.link(key)
    ld.use_shadow = True
    # soft interior fill (shadowless points only: area lights hang EEVEE here)
    fills = []
    for i, (loc, en) in enumerate([((4.60, 10.20, 12.30), 90.0),
                                   ((4.00, 11.90, 11.80), 55.0)]):
        nm = f'V4_Fill_{i}'
        old = bpy.data.objects.get(nm)
        if old:
            bpy.data.objects.remove(old, do_unlink=True)
        f = bpy.data.lights.new(nm, type='POINT')
        f.energy = en; f.shadow_soft_size = 0.02
        f.color = (1.0, 0.905, 0.795)
        try:
            f.specular_factor = 0.0
        except Exception:
            pass
        try:
            f.use_shadow = False
        except Exception:
            pass
        fo = bpy.data.objects.new(nm, f)
        fo.location = loc; fo.hide_render = True
        SCENE.collection.objects.link(fo)
        fills.append(fo)
    return key, fills

# ═══════════════════════════════════════════════════════════════════════════
#  12.  SHOT LIST
# ═══════════════════════════════════════════════════════════════════════════
SHOTS = [
    dict(id='01', name='01_Courtyard_Garden', lens=20.0,
         hdri='kloofendal_48d_partly_cloudy_puresky_4k.hdr', bearing=231, elev=73,
         sky_rot=0.0, sky_strength=1.55, sun_energy=5.4, sun_color=(1.0, 0.96, 0.905),
         loc=(11.60, 7.45, 2.30), target=(8.60, 20.00, 4.20),
         note='Courtyard at eye level: tree, lawn, colonnade, stacked balconies'),

    dict(id='02', name='02_Courtyard_Void_Aerial', lens=45.0, roll=90.0,
         hdri='kloofendal_48d_partly_cloudy_puresky_4k.hdr', bearing=231, elev=73,
         sky_rot=0.0, sky_strength=1.55, sun_energy=5.4, sun_color=(1.0, 0.96, 0.905),
         loc=(9.85, 8.50, 19.00), target=(9.85, 15.00, 0.90),
         note='Looking down the void: garden, tree from above, four balcony tiers'),

    dict(id='03', name='03_Street_Facade', lens=28.0,
         hdri='belfast_sunset_puresky_4k.hdr', bearing=214, elev=11,
         sky_rot=0.0, sky_strength=0.95, sun_energy=6.5, sun_color=(1.0, 0.62, 0.34),
         loc=(13.50, -30.00, 3.60), target=(7.00, 0.00, 8.80),
         note='Golden hour on the west elevation: fins, portal, guardhouse, gate'),

    dict(id='04', name='04_LivingRoom_L3', lens=24.0,
         hdri='overcast_soil_puresky_4k.hdr', bearing=168, elev=64,
         sky_rot=0.0, sky_strength=1.15, sun_energy=4.2, sun_color=(1.0, 0.95, 0.88),
         loc=(2.90, 13.10, 11.60), target=(6.26, 10.25, 11.40), fills=True,
         note='Inside the L3 living room looking through the glazed wall'),

    dict(id='05', name='05_L3_Gallery_Overlook', lens=28.0,
         hdri='kloofendal_48d_partly_cloudy_puresky_4k.hdr', bearing=231, elev=73,
         sky_rot=0.0, sky_strength=1.55, sun_energy=5.4, sun_color=(1.0, 0.96, 0.905),
         loc=(13.80, 12.00, 12.10), target=(7.00, 15.00, 8.20),
         note='From the L3 gallery over the balustrade into the courtyard'),

    dict(id='06', name='06_Roof_Pergola_Sunset', lens=22.0,
         hdri='kloppenheim_06_puresky_4k.hdr', bearing=262, elev=11,
         sky_rot=0.0, sky_strength=1.0, sun_energy=6.0, sun_color=(1.0, 0.63, 0.35),
         loc=(4.60, 17.20, 17.75), target=(1.40, 4.60, 17.20),
         note='Roof garden under the pergola at golden hour'),

    # ---- two new strategic frames -------------------------------------
    dict(id='07', name='07_Twilight_Street', lens=30.0,
         hdri='satara_night_4k.hdr', bearing=250, elev=4,
         sky_rot=0.0, sky_strength=0.75, sun_energy=0.10, sun_color=(1.0, 0.70, 0.45),
         exposure=-0.80,
         loc=(11.00, -27.00, 3.20), target=(6.60, 0.00, 8.40), dusk=True,
         note='Blue-hour street elevation with the interior lights on'),

    dict(id='08', name='08_Aerial_Hero', lens=30.0,
         hdri='kloofendal_48d_partly_cloudy_puresky_4k.hdr', bearing=248, elev=44,
         sky_rot=18.0, sky_strength=1.15, sun_energy=5.2, sun_color=(1.0, 0.94, 0.86),
         exposure=-1.20,
         loc=(1.50, -37.00, 27.00), target=(8.60, 10.50, 6.20),
         note='Aerial three-quarter of the whole building and its courtyard'),
]

def make_cameras():
    for s in SHOTS:
        old = bpy.data.objects.get('V4Cam_' + s['name'])
        if old:
            bpy.data.objects.remove(old, do_unlink=True)
        cd = bpy.data.cameras.new('V4Cam_' + s['name'])
        cd.lens = s['lens']; cd.sensor_width = 36.0; cd.sensor_fit = 'AUTO'
        cd.clip_start = 0.06; cd.clip_end = 5000.0
        cam = bpy.data.objects.new('V4Cam_' + s['name'], cd)
        SCENE.collection.objects.link(cam)
        cam.location = s['loc']
        d = Vector(s['target']) - Vector(s['loc'])
        q = d.to_track_quat('-Z', 'Y')
        if s.get('roll'):
            q = q @ Quaternion((0, 0, 1), math.radians(s['roll']))
        cam.rotation_euler = q.to_euler()
        s['cam'] = cam
    log(f"{len(SHOTS)} cameras placed")

# ═══════════════════════════════════════════════════════════════════════════
#  13.  RIG APPLICATION
# ═══════════════════════════════════════════════════════════════════════════
def apply_shot_rig(s, key, fills, dusk_lights):
    set_sky(s['hdri'], s.get('sky_rot', 0.0), s['sky_strength'] * SKYMUL)
    u = bearing_vec(s['bearing'], s['elev'])
    key.location = u * 80.0
    key.rotation_euler = u.to_track_quat('Z', 'Y').to_euler()
    key.data.energy = s['sun_energy'] * SUNMUL
    key.data.color = s['sun_color']
    key.data.angle = math.radians(0.6 if s['elev'] > 30 else 1.1)
    for f in fills:
        f.hide_render = not s.get('fills', False)
    for d in dusk_lights:
        d.hide_render = not s.get('dusk', False)
    sset(SCENE.view_settings, 'exposure', s.get('exposure', BASE_EXPOSURE) + EXPADD)

def build_dusk_lights():
    """Warm interior practicals that only show in the twilight frame."""
    made = []
    spots = [(6.60, 9.00, 5.20), (6.60, 12.00, 5.20), (6.60, 16.00, 5.20),
             (6.60, 20.00, 5.20), (6.60, 9.00, 8.20), (6.60, 14.00, 8.20),
             (6.60, 19.00, 8.20), (6.60, 11.00, 11.20), (6.60, 17.00, 11.20),
             (6.60, 12.00, 14.20), (12.00, 3.60, 2.40), (8.80, 2.60, 2.40),
             (14.60, 10.00, 11.20), (14.60, 17.00, 14.20)]
    for i, p in enumerate(spots):
        nm = f'V4_Dusk_{i}'
        old = bpy.data.objects.get(nm)
        if old:
            bpy.data.objects.remove(old, do_unlink=True)
        ld = bpy.data.lights.new(nm, type='POINT')
        ld.energy = 58.0
        ld.color = (1.0, 0.80, 0.58)
        ld.shadow_soft_size = 0.25
        try:
            ld.use_shadow = False
        except Exception:
            pass
        o = bpy.data.objects.new(nm, ld)
        o.location = p; o.hide_render = True
        SCENE.collection.objects.link(o)
        made.append(o)
    return made

# ═══════════════════════════════════════════════════════════════════════════
#  14.  MAIN
# ═══════════════════════════════════════════════════════════════════════════
def build_scene():
    hide_annotations()
    configure_render()
    build_materials()
    restyle_model()
    open_glazed_walls()
    dress_furniture()
    build_context()
    key, fills = build_lights()
    dusk = build_dusk_lights()
    enhance_planting()
    build_detail()
    bevel_structure()
    cube_project_all()
    build_world()
    make_cameras()
    check_clearance(SHOTS)
    return key, fills, dusk

# ═══════════════════════════════════════════════════════════════════════════
#  15.  VIDEO MODE  -- camera path rendered frame by frame, paced in bursts
# ═══════════════════════════════════════════════════════════════════════════
def _catmull(p0, p1, p2, p3, t):
    t2, t3 = t * t, t * t * t
    return 0.5 * ((2 * p1) + (-p0 + p2) * t +
                  (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 +
                  (-p0 + 3 * p1 - 3 * p2 + p3) * t3)

def _path(points, t):
    pts = [Vector(p) for p in points]
    n = len(pts) - 1
    x = max(0.0, min(0.999999, t)) * n
    i = int(x); f = x - i
    p0 = pts[max(i - 1, 0)]; p1 = pts[i]
    p2 = pts[min(i + 1, n)]; p3 = pts[min(i + 2, n)]
    return _catmull(p0, p1, p2, p3, f)

# Fly-through: street -> pedestrian gate -> up into the courtyard -> roof.
FLY_PATH = [
    (6.40, -26.0, 1.75), (6.45, -14.0, 1.80), (6.48, -5.0, 1.95),
    (6.60, 2.0, 2.35), (7.20, 8.0, 2.55), (8.60, 12.0, 3.20),
    (10.60, 14.6, 4.60), (11.60, 17.5, 7.40), (11.00, 19.0, 11.0),
    (9.40, 18.0, 15.2), (6.00, 15.0, 17.6), (3.20, 12.6, 17.9),
]
FLY_TARGET = [
    (6.50, 0.0, 2.2), (6.50, -2.0, 2.4), (6.60, 4.0, 3.0),
    (7.20, 10.0, 3.4), (8.60, 13.0, 4.2), (10.0, 15.0, 5.6),
    (10.6, 16.0, 7.0), (10.4, 18.0, 9.6), (8.60, 18.0, 13.0),
    (5.60, 15.5, 16.6), (3.20, 12.0, 17.4), (2.20, 7.0, 16.8),
]

# Orbit: a slow arc around the whole building, rising and settling.
def orbit_points(cx, cy, r, z, a0, a1, n):
    pts, tgts = [], []
    for i in range(n):
        t = i / (n - 1)
        a = math.radians(a0 + (a1 - a0) * t)
        zz = z + 6.0 * math.sin(math.pi * t)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a), zz))
        tgts.append((cx, cy, 6.0 + 3.0 * math.sin(math.pi * t)))
    return pts, tgts

ORBIT_PTS, ORBIT_TGT = orbit_points(7.6, 14.0, 40.0, 19.0, 205.0, 300.0, 12)

def run_video(key, fills, dusk):
    spp = 1
    s = dict(id='V', name='video', lens=24.0,
             hdri='kloofendal_48d_partly_cloudy_puresky_4k.hdr' if VIDEO == 'fly'
                  else 'belfast_sunset_puresky_4k.hdr',
             bearing=214 if VIDEO == 'fly' else 236,
             elev=52 if VIDEO == 'fly' else 12,
             sky_rot=10.0, sky_strength=0.85 if VIDEO == 'fly' else 0.95,
             sun_energy=6.0 if VIDEO == 'fly' else 6.6,
             sun_color=(1.0, 0.94, 0.86) if VIDEO == 'fly' else (1.0, 0.63, 0.35),
             loc=(0, 0, 0), target=(1, 0, 0),
             note=f'{VIDEO} video path')
    cd = bpy.data.cameras.new('V4Cam_Video')
    cd.lens = 22.0 if VIDEO == 'fly' else 30.0
    cd.sensor_width = 36.0; cd.clip_start = 0.06; cd.clip_end = 5000.0
    cam = bpy.data.objects.new('V4Cam_Video', cd)
    SCENE.collection.objects.link(cam)
    SCENE.camera = cam
    s['cam'] = cam
    apply_shot_rig(s, key, fills, dusk)

    pts = FLY_PATH if VIDEO == 'fly' else ORBIT_PTS
    tgts = FLY_TARGET if VIDEO == 'fly' else ORBIT_TGT
    out = os.path.join(OUTDIR, f'video_{VIDEO}')
    os.makedirs(out, exist_ok=True)
    log(f"video '{VIDEO}': {FRAMES} frames from {VSTART}, {RES_X}x{RES_Y}, out={out}")

    t_start = time.time()
    for i in range(VSTART - 1, FRAMES):
        t = i / max(FRAMES - 1, 1)
        # ease in/out so the move does not start and stop abruptly
        e = t * t * (3 - 2 * t)
        p = _path(pts, e)
        q = _path(tgts, e)
        cam.location = p
        cam.rotation_euler = (q - p).to_track_quat('-Z', 'Y').to_euler()
        SCENE.render.filepath = os.path.join(out, f'f{i+1:05d}.png')
        t0 = time.time()
        bpy.ops.render.render(write_still=True)
        dt = time.time() - t0
        if (i + 1) % 8 == 0 or i == 0:
            done = i + 1
            el = time.time() - t_start
            eta = el / max(done - (VSTART - 1), 1) * (FRAMES - done)
            log(f"  frame {done}/{FRAMES}  {dt:.1f}s  elapsed {el/60:.1f} min  eta {eta/60:.1f} min")
        # paced bursts: rest the machine between batches
        if (i + 1) % BATCH == 0 and i + 1 < FRAMES:
            log(f"  cooldown {COOLDOWN}s after {i+1} frames")
            time.sleep(COOLDOWN)
    log(f"video frames complete in {(time.time()-t_start)/60:.1f} min")

def main():
    log(f"mode={MODE} out={OUTDIR} shots={ONLY or 'all'}")
    key, fills, dusk = build_scene()
    if MODE == 'video':
        run_video(key, fills, dusk)
        log("video done")
        return
    todo = [s for s in SHOTS if not ONLY or s['id'] in ONLY]
    if MODE == 'test':
        todo = todo[:1]
    for s in todo:
        log("=" * 70)
        log(f"  {s['name']}  {s['lens']:.0f}mm  {s['note']}")
        apply_shot_rig(s, key, fills, dusk)
        SCENE.camera = s['cam']
        path = os.path.join(OUTDIR, s['name'] + '.png')
        SCENE.render.filepath = path
        t0 = time.time()
        bpy.ops.render.render(write_still=True)
        kb = os.path.getsize(path) / 1024.0 if os.path.exists(path) else 0
        log(f"  -> {s['name']}.png  {kb:.0f} KB  {time.time()-t0:.0f}s")
        time.sleep(4)
    log("stills done")

main()
