"""
Courtyard Apartments on a 50x100 ft Plot (v3, 5 Storeys, Gate Faces West)
Nairobi, Kenya — Compliant with Kenya National Building Code 2024 (LN 47/2024)

Parametric Generator Script: build_courtyard_apartments_v3.py
"""

import bpy
import bmesh
import math
from mathutils import Vector, Euler

# ==============================================================================
# 0. PARAMETRIC CONFIGURATION & CONSTANTS
# ==============================================================================

# Plot Dimensions (50 ft x 100 ft = 15.24 m x 30.48 m)
PLOT_W_X = 15.24                  # 50 ft plot width along street (West)
PLOT_L_Y = 30.48                  # 100 ft plot depth (East)
STREET_LEVEL_Z = 0.00             # Street datum (z = 0.00)

# Levels & Heights
BASEMENT_FFL = -2.00              # Split-level basement floor level (-2.00 m)
GF_RAISE = 0.90                   # Ground floor podium level (+0.90 m)
GF_FTF = 3.30                     # Ground floor floor-to-floor height
UPPER_FTF = 3.00                  # Upper floor-to-floor height (L1 to L4)
N_UPPER = 4                       # L1, L2, L3, L4 (Total storeys: GF + 4 = 5)
PARAPET = 1.10                    # Roof parapet height (1.10 m)

# Derived Storey Levels
L1_FFL = GF_RAISE + GF_FTF        # +4.20 m
L2_FFL = L1_FFL + UPPER_FTF       # +7.20 m
L3_FFL = L2_FFL + UPPER_FTF       # +10.20 m
L4_FFL = L3_FFL + UPPER_FTF       # +13.20 m
ROOF_SLAB_Z = L4_FFL + UPPER_FTF  # +16.20 m
PARAPET_TOP_Z = ROOF_SLAB_Z + PARAPET  # +17.30 m

# Architectural & Structural Sizing
WALL_THICK_EXT = 0.30             # Boundary retaining walls / external stone (300 mm)
WALL_THICK_INT = 0.15             # Internal partitions (150 mm)
PODIUM_SLAB_THICK = 0.25          # 250 mm flat-slab podium
UPPER_SLAB_THICK = 0.20           # 200 mm upper RC slabs
RAFT_THICK = 0.30                 # 300 mm foundation raft

COL_BASE_SIZE = 0.40              # 400x400 mm RC columns B1 to GF
COL_UPPER_SIZE = 0.30             # 300x300 mm RC columns L1 to L4

WING_DEPTH = 6.30                 # Left (North) upper wing depth (x = 0 to 6.30 m)
BALCONY_PROJ = 1.20               # Balcony projection into courtyard (1.20 m)

# Ramp Profile Parameters
RAMP_LANE_WIDTH = 3.18            # Clear ramp width (x = 0.30 to 3.48)
RAMP_KERB_H = 0.45                # 450 mm kerb / barrier

# ==============================================================================
# 1. HELPER FUNCTIONS: COLLECTIONS, MATERIALS, MESHES, TEXT
# ==============================================================================

def get_or_create_collection(col_name, parent_col=None):
    if col_name in bpy.data.collections:
        col = bpy.data.collections[col_name]
    else:
        col = bpy.data.collections.new(col_name)
        if parent_col is None:
            parent_col = bpy.context.scene.collection
        parent_col.children.link(col)
    return col

def init_material(name, color=(0.8, 0.8, 0.8, 1.0), roughness=0.5, metallic=0.0):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.diffuse_color = color
    nodes = mat.node_tree.nodes
    principled = next((n for n in nodes if n.type == "BSDF_PRINCIPLED"), None)
    if principled:
        for inp in principled.inputs:
            if inp.name == "Base Color": inp.default_value = color
            elif inp.name == "Roughness": inp.default_value = roughness
            elif inp.name == "Metallic": inp.default_value = metallic
    return mat

def create_box(name, min_pt, size, col_name, mat=None):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    sx, sy, sz = size
    for v in bm.verts:
        v.co.x = (v.co.x + 0.5) * sx
        v.co.y = (v.co.y + 0.5) * sy
        v.co.z = (v.co.z + 0.5) * sz
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    obj.location = min_pt
    if mat: obj.data.materials.append(mat)
    col = get_or_create_collection(col_name)
    col.objects.link(obj)
    return obj

def create_plane(name, p1, p2, p3, p4, col_name, mat=None):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    v1 = bm.verts.new(p1)
    v2 = bm.verts.new(p2)
    v3 = bm.verts.new(p3)
    v4 = bm.verts.new(p4)
    bm.faces.new((v1, v2, v3, v4))
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    if mat: obj.data.materials.append(mat)
    col = get_or_create_collection(col_name)
    col.objects.link(obj)
    return obj

def create_3d_text(name, text_str, loc, size=0.30, rot=(0,0,0), col_name="Annotations", mat=None):
    curve = bpy.data.curves.new(name=name, type='FONT')
    curve.body = text_str
    curve.size = size
    curve.extrude = 0.015
    curve.align_x = 'CENTER'
    curve.align_y = 'CENTER'
    
    obj = bpy.data.objects.new(name, curve)
    obj.location = loc
    obj.rotation_euler = rot
    if mat: obj.data.materials.append(mat)
    col = get_or_create_collection(col_name)
    col.objects.link(obj)
    return obj

def create_cylinder(name, loc, radius, height, col_name, mat=None, segments=16):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments, radius1=radius, radius2=radius, depth=height)
    for v in bm.verts:
        v.co.z += height / 2.0
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    if mat: obj.data.materials.append(mat)
    col = get_or_create_collection(col_name)
    col.objects.link(obj)
    return obj

def create_icosphere(name, loc, radius, col_name, mat=None, subdivisions=2):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdivisions, radius=radius)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    if mat: obj.data.materials.append(mat)
    col = get_or_create_collection(col_name)
    col.objects.link(obj)
    return obj

# ==============================================================================
# 2. STAGES 1 & 2: BASEMENT, STRUCTURE FRAME & VERTICAL CORE
# ==============================================================================

def build_scene():
    print("=== BUILDING COURTYARD APARTMENTS V3 ===")
    
    # 1. Clean scene completely
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for col in list(bpy.data.collections):
        bpy.data.collections.remove(col)
    for block in list(bpy.data.meshes):
        bpy.data.meshes.remove(block)
    for block in list(bpy.data.materials):
        bpy.data.materials.remove(block)
    for block in list(bpy.data.curves):
        bpy.data.curves.remove(block)

    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.length_unit = 'METERS'
    scene.unit_settings.scale_length = 1.0

    # 2. Collections Setup per level + annotations + structure
    cols = ["Annotations", "B1_Basement", "GF_Ground", "L1_Floor", "L2_Floor", "L3_Floor", "L4_Floor", "Roof", "Structure"]
    for c in cols:
        get_or_create_collection(c)

    # 3. Materials
    mat_conc = init_material("Mat_Concrete", (0.58, 0.60, 0.62, 1.0), roughness=0.7)
    mat_floor = init_material("Mat_Epoxy_Floor", (0.26, 0.28, 0.30, 1.0), roughness=0.25)
    mat_ramp_groove = init_material("Mat_Ramp_Groove", (0.40, 0.42, 0.44, 1.0), roughness=0.85)
    mat_hazard = init_material("Mat_Hazard_Yellow", (0.95, 0.78, 0.05, 1.0), roughness=0.35)
    mat_white_line = init_material("Mat_Line_White", (0.96, 0.96, 0.98, 1.0), roughness=0.20)
    mat_bay_blue = init_material("Mat_Bay_Accessible", (0.08, 0.38, 0.80, 1.0), roughness=0.30)
    mat_bay_green = init_material("Mat_Bay_EV", (0.10, 0.70, 0.32, 1.0), roughness=0.30)
    mat_text = init_material("Mat_Annotation_Text", (0.95, 0.95, 0.95, 1.0), roughness=0.1)
    mat_slab = init_material("Mat_RC_Slab", (0.65, 0.67, 0.70, 1.0), roughness=0.6)
    # Architectural Finishes & Kenyan Palette:
    mat_issb = init_material("Mat_ISSB_Terracotta", (0.74, 0.36, 0.20, 1.0), roughness=0.85)
    mat_stone_render = init_material("Mat_Stone_Render", (0.88, 0.86, 0.82, 1.0), roughness=0.75)
    mat_steel_dark = init_material("Mat_Dark_Steel", (0.12, 0.12, 0.14, 1.0), roughness=0.35, metallic=0.8)
    mat_wood = init_material("Mat_Warm_Timber", (0.45, 0.26, 0.14, 1.0), roughness=0.55)
    mat_glass = init_material("Mat_Glass_Arch", (0.85, 0.92, 0.95, 0.3), roughness=0.05)
    mat_shutter = init_material("Mat_Roller_Shutter", (0.55, 0.56, 0.58, 1.0), roughness=0.4, metallic=0.7)
    mat_lawn = init_material("Mat_Courtyard_Lawn", (0.22, 0.48, 0.15, 1.0), roughness=0.9)
    mat_shrub = init_material("Mat_Garden_Foliage", (0.18, 0.38, 0.12, 1.0), roughness=0.8)
    mat_paver = init_material("Mat_Permeable_Paver", (0.76, 0.73, 0.68, 1.0), roughness=0.8)
    mat_trunk = init_material("Mat_Tree_Trunk", (0.32, 0.22, 0.16, 1.0), roughness=0.85)


    # 4. North Arrow (in Annotations, points along -X in Blender world)
    north_arrow_mesh = bpy.data.meshes.new("North_Arrow_Mesh")
    bm_na = bmesh.new()
    v_tip = bm_na.verts.new((-1.5, 0.0, 0.1))
    v_l = bm_na.verts.new((-0.8, -0.4, 0.1))
    v_r = bm_na.verts.new((-0.8, 0.4, 0.1))
    v_c = bm_na.verts.new((-1.0, 0.0, 0.1))
    bm_na.faces.new((v_tip, v_l, v_c))
    bm_na.faces.new((v_tip, v_c, v_r))
    bm_na.to_mesh(north_arrow_mesh)
    bm_na.free()
    
    obj_na = bpy.data.objects.new("North_Arrow", north_arrow_mesh)
    obj_na.location = (-1.0, -2.0, 0.0)
    obj_na.data.materials.append(mat_hazard)
    get_or_create_collection("Annotations").objects.link(obj_na)
    create_3d_text("North_Arrow_Label", "N (WEST GATE)", (-2.2, -2.0, 0.12), size=0.40, col_name="Annotations", mat=mat_text)

    # Print Levels Table
    print("\n================ LEVEL SCHEDULE ================")
    levels_table = [
        ("Street Level Datum", STREET_LEVEL_Z),
        ("Basement Floor (FFL)", BASEMENT_FFL),
        ("Ground Floor Podium (FFL)", GF_RAISE),
        ("Level 1 Floor (FFL)", L1_FFL),
        ("Level 2 Floor (FFL)", L2_FFL),
        ("Level 3 Floor (FFL)", L3_FFL),
        ("Level 4 Floor (FFL)", L4_FFL),
        ("Roof Slab Top", ROOF_SLAB_Z),
        ("Roof Parapet Top", PARAPET_TOP_Z)
    ]
    for name, lvl in levels_table:
        print(f"{name:<28} | {lvl:+6.2f} m")
    print("================================================\n")

    # --------------------------------------------------------------------------
    # A. BASEMENT (B1) GEOMETRY & RAMP
    # --------------------------------------------------------------------------
    # Raft
    create_box("Slab_Basement_Raft", (0.0, 0.0, BASEMENT_FFL - RAFT_THICK), (PLOT_W_X, PLOT_L_Y, RAFT_THICK), "B1_Basement", mat_conc)
    # Floor Finish
    create_box("Floor_Basement_Finish", (WALL_THICK_EXT, WALL_THICK_EXT, BASEMENT_FFL), (PLOT_W_X - 2*WALL_THICK_EXT, PLOT_L_Y - 2*WALL_THICK_EXT, 0.02), "B1_Basement", mat_floor)
    # Solid ground under shop/guard
    create_box("Solid_Ground_Front_Block", (3.48, 0.0, BASEMENT_FFL), (10.49 - 3.48, 5.20, abs(BASEMENT_FFL)), "B1_Basement", mat_conc)

    # Perimeter Boundary Retaining Walls (Full Height to Ground Level / Podium)
    create_box("Wall_Retaining_North", (0.0, 0.0, BASEMENT_FFL), (WALL_THICK_EXT, PLOT_L_Y, abs(BASEMENT_FFL) + GF_RAISE), "Structure", mat_conc)
    create_box("Wall_Retaining_South", (PLOT_W_X - WALL_THICK_EXT, 0.0, BASEMENT_FFL), (WALL_THICK_EXT, PLOT_L_Y, abs(BASEMENT_FFL) + GF_RAISE), "Structure", mat_conc)
    create_box("Wall_Retaining_East", (0.0, PLOT_L_Y - WALL_THICK_EXT, BASEMENT_FFL), (PLOT_W_X, WALL_THICK_EXT, abs(BASEMENT_FFL) + GF_RAISE), "Structure", mat_conc)
    create_box("Wall_Retaining_West", (3.48, 0.0, BASEMENT_FFL), (PLOT_W_X - 3.48, WALL_THICK_EXT, abs(BASEMENT_FFL)), "Structure", mat_conc)

    # Ramp Slices (Touchdown at y = 23.0m)
    rx1, rx2 = 0.30, 3.48
    r_pts = [(0.0, 0.0), (1.0, 0.15), (6.0, -0.05), (8.4, -0.20), (20.6, -1.85), (23.0, -2.00)]
    for i in range(len(r_pts) - 1):
        y_a, z_a = r_pts[i]
        y_b, z_b = r_pts[i+1]
        mesh_r = bpy.data.meshes.new(f"Ramp_Slice_{i+1}")
        bm_r = bmesh.new()
        v1 = bm_r.verts.new((rx1, y_a, z_a))
        v2 = bm_r.verts.new((rx2, y_a, z_a))
        v3 = bm_r.verts.new((rx2, y_b, z_b))
        v4 = bm_r.verts.new((rx1, y_b, z_b))
        v5 = bm_r.verts.new((rx1, y_a, z_a - 0.25))
        v6 = bm_r.verts.new((rx2, y_a, z_a - 0.25))
        v7 = bm_r.verts.new((rx2, y_b, z_b - 0.25))
        v8 = bm_r.verts.new((rx1, y_b, z_b - 0.25))
        bm_r.faces.new((v1, v2, v3, v4))
        bm_r.faces.new((v8, v7, v6, v5))
        bm_r.faces.new((v1, v4, v8, v5))
        bm_r.faces.new((v2, v6, v7, v3))
        bm_r.faces.new((v1, v5, v6, v2))
        bm_r.faces.new((v4, v3, v7, v8))
        bm_r.to_mesh(mesh_r)
        bm_r.free()
        obj_r = bpy.data.objects.new(f"Ramp_Slice_{i+1}", mesh_r)
        obj_r.data.materials.append(mat_ramp_groove)
        get_or_create_collection("B1_Basement").objects.link(obj_r)

    # Ramp Kerb Barrier (450 mm high)
    mesh_kb = bpy.data.meshes.new("Ramp_Kerb_Barrier")
    bm_kb = bmesh.new()
    for i in range(len(r_pts) - 1):
        y_a, z_a = r_pts[i]
        y_b, z_b = r_pts[i+1]
        kx1, kx2 = 3.48, 3.70
        v1 = bm_kb.verts.new((kx1, y_a, z_a + RAMP_KERB_H))
        v2 = bm_kb.verts.new((kx2, y_a, z_a + RAMP_KERB_H))
        v3 = bm_kb.verts.new((kx2, y_b, z_b + RAMP_KERB_H))
        v4 = bm_kb.verts.new((kx1, y_b, z_b + RAMP_KERB_H))
        v5 = bm_kb.verts.new((kx1, y_a, BASEMENT_FFL))
        v6 = bm_kb.verts.new((kx2, y_a, BASEMENT_FFL))
        v7 = bm_kb.verts.new((kx2, y_b, BASEMENT_FFL))
        v8 = bm_kb.verts.new((kx1, y_b, BASEMENT_FFL))
        bm_kb.faces.new((v1, v2, v3, v4))
        bm_kb.faces.new((v8, v7, v6, v5))
        bm_kb.faces.new((v1, v4, v8, v5))
        bm_kb.faces.new((v2, v6, v7, v3))
        bm_kb.faces.new((v1, v5, v6, v2))
        bm_kb.faces.new((v4, v3, v7, v8))
    bm_kb.to_mesh(mesh_kb)
    bm_kb.free()
    obj_kb = bpy.data.objects.new("Ramp_Kerb_Barrier", mesh_kb)
    obj_kb.data.materials.append(mat_hazard)
    get_or_create_collection("B1_Basement").objects.link(obj_kb)

    # Sunken Water Tank
    create_box("Tank_Water_Sunken", (0.50, 3.00, -3.00), (2.70, 10.00, 1.00), "B1_Basement", mat_conc)

    # Lift Lobby & Server Room in B1
    create_plane("Floor_Lift_Lobby_B1", (8.48, 5.20, BASEMENT_FFL + 0.01), (12.00, 5.20, BASEMENT_FFL + 0.01), (12.00, 8.00, BASEMENT_FFL + 0.01), (8.48, 8.00, BASEMENT_FFL + 0.01), "B1_Basement", mat_floor)
    create_box("Room_Server_Utility_B1", (12.00, 5.20, BASEMENT_FFL), (2.94, 2.80, abs(BASEMENT_FFL) + GF_RAISE), "B1_Basement", mat_conc)

    # 9 Parking Bays
    # Left row (5 bays)
    create_plane("Bay_01_Accessible", (3.48, 5.20, BASEMENT_FFL + 0.005), (8.48, 5.20, BASEMENT_FFL + 0.005), (8.48, 8.80, BASEMENT_FFL + 0.005), (3.48, 8.80, BASEMENT_FFL + 0.005), "B1_Basement", mat_bay_blue)
    bay_y_divs = [8.80, 11.375, 13.95, 16.525, 19.10]
    for b_idx in range(4):
        y1, y2 = bay_y_divs[b_idx], bay_y_divs[b_idx+1]
        create_plane(f"Bay_0{b_idx+2}", (3.48, y1, BASEMENT_FFL + 0.005), (8.48, y1, BASEMENT_FFL + 0.005), (8.48, y2, BASEMENT_FFL + 0.005), (3.48, y2, BASEMENT_FFL + 0.005), "B1_Basement", mat_floor)
        create_plane(f"Bay_0{b_idx+2}_Line", (3.48, y1, BASEMENT_FFL + 0.008), (8.48, y1, BASEMENT_FFL + 0.008), (8.48, y1 + 0.10, BASEMENT_FFL + 0.008), (3.48, y1 + 0.10, BASEMENT_FFL + 0.008), "B1_Basement", mat_white_line)

    # Rear row (4 bays)
    rear_x_divs = [3.48, 6.345, 9.21, 12.075, 14.94]
    for r_idx in range(4):
        x1, x2 = rear_x_divs[r_idx], rear_x_divs[r_idx+1]
        bay_num = 6 + r_idx
        b_mat = mat_bay_green if bay_num == 9 else mat_floor
        create_plane(f"Bay_0{bay_num}", (x1, 25.20, BASEMENT_FFL + 0.005), (x2, 25.20, BASEMENT_FFL + 0.005), (x2, 30.18, BASEMENT_FFL + 0.005), (x1, 30.18, BASEMENT_FFL + 0.005), "B1_Basement", b_mat)
        create_plane(f"Bay_0{bay_num}_Line", (x1, 25.20, BASEMENT_FFL + 0.008), (x1 + 0.10, 25.20, BASEMENT_FFL + 0.008), (x1 + 0.10, 30.18, BASEMENT_FFL + 0.008), (x1, 30.18, BASEMENT_FFL + 0.008), "B1_Basement", mat_white_line)

    # Protected Walkway
    create_plane("Pedestrian_Walkway_B1", (8.48, 8.00, BASEMENT_FFL + 0.006), (9.68, 8.00, BASEMENT_FFL + 0.006), (9.68, 19.10, BASEMENT_FFL + 0.006), (8.48, 19.10, BASEMENT_FFL + 0.006), "B1_Basement", mat_hazard)

    # Sump Pit
    create_box("Sump_Pit_Basement", (0.50, 28.50, BASEMENT_FFL - 1.20), (1.00, 1.00, 1.20), "B1_Basement", mat_conc)

    # Swept Path Curve
    curve_data = bpy.data.curves.new("Swept_Path_Curve", type='CURVE')
    curve_data.dimensions = '3D'
    spline = curve_data.splines.new('BEZIER')
    sweep_pts = [(1.89, 21.00, BASEMENT_FFL + 0.05), (1.89, 23.50, BASEMENT_FFL + 0.05), (3.50, 25.20, BASEMENT_FFL + 0.05), (6.00, 24.50, BASEMENT_FFL + 0.05), (8.50, 22.15, BASEMENT_FFL + 0.05), (11.71, 19.10, BASEMENT_FFL + 0.05)]
    spline.bezier_points.add(len(sweep_pts) - 1)
    for i, pt in enumerate(sweep_pts):
        bp = spline.bezier_points[i]
        bp.co = pt
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
    curve_obj = bpy.data.objects.new("Swept_Path_Trajectory", curve_data)
    get_or_create_collection("Annotations").objects.link(curve_obj)
    curve_data.bevel_depth = 0.05
    curve_obj.data.materials.append(mat_hazard)

    # --------------------------------------------------------------------------
    # B. VERTICAL CORE (STAIR + LIFT) RISING THROUGH ALL STOREYS TO ROOF
    # --------------------------------------------------------------------------
    # Total Core Height: from BASEMENT_FFL (-2.00) up to ROOF_SLAB_Z + 3.60 m (+19.80 m)
    total_core_h = (ROOF_SLAB_Z + 3.60) - BASEMENT_FFL
    
    # Lift Shaft: x 10.49 to 12.69, y 0.30 to 2.50 (2.0 x 2.0 m internal, 200 mm RC walls)
    create_box("Core_Lift_Shaft_FullHeight",
               (10.49, 0.30, BASEMENT_FFL),
               (2.20, 2.20, total_core_h),
               "Structure", mat_conc)

    # Stair Enclosure: x 12.69 to 14.94, y 0.30 to 5.20 (2.25 m x 4.90 m)
    # Rises to Roof Level + Stair Headroom (ROOF_SLAB_Z + 2.80 = +19.00 m) per s.194(2)
    stair_headroom_h = (ROOF_SLAB_Z + 2.80) - BASEMENT_FFL
    create_box("Core_Stair_Enclosure_FullHeight",
               (12.69, 0.30, BASEMENT_FFL),
               (2.25, 4.90, stair_headroom_h),
               "Structure", mat_conc)

    # --------------------------------------------------------------------------
    # C. STRUCTURAL COLUMNS (B1 to Roof)
    # --------------------------------------------------------------------------
    # Column grid positions:
    # 1. Line x = 3.48 (Ramp wall / left wing): cy in [0.30, 5.20, 8.80, 13.95, 19.10, 23.00, 30.18]
    # 2. Line x = 6.30 (Colonnade / upper wing face): cy in [5.20, 8.80, 13.95, 19.10, 23.00, 30.18]
    # 3. Line x = 8.48 (Basement bay front): cy in [8.80, 13.95, 19.10] (terminates at podium slab)
    # 4. Line x = 10.49 (Core / right wing): cy in [0.30, 5.20, 8.00, 23.00, 30.18]
    # 5. Boundary lines x = 0.00 and x = 15.24: embedded in walls

    # Basement Columns (400x400 mm, -2.00 to +0.90)
    for cy in [5.20, 8.80, 13.95, 19.10, 23.00, 30.18]:
        create_box(f"Col_B1_x3.48_y{cy:.1f}", (3.48 - 0.20, cy - 0.20, BASEMENT_FFL), (COL_BASE_SIZE, COL_BASE_SIZE, GF_RAISE - BASEMENT_FFL), "Structure", mat_conc)
        create_box(f"Col_B1_x6.30_y{cy:.1f}", (6.30 - 0.20, cy - 0.20, BASEMENT_FFL), (COL_BASE_SIZE, COL_BASE_SIZE, GF_RAISE - BASEMENT_FFL), "Structure", mat_conc)
    for cy in [8.80, 13.95, 19.10]:
        create_box(f"Col_B1_x8.48_y{cy:.1f}", (8.48 - 0.20, cy - 0.20, BASEMENT_FFL), (COL_BASE_SIZE, COL_BASE_SIZE, GF_RAISE - BASEMENT_FFL), "Structure", mat_conc)

    # GF Columns (400x400 mm, +0.90 to +4.20)
    # Line x = 6.30 forms the GF courtyard shaded colonnade!
    for cy in [5.20, 8.80, 13.95, 19.10, 23.00]:
        create_box(f"Col_GF_Colonnade_x6.30_y{cy:.1f}", (6.30 - 0.20, cy - 0.20, GF_RAISE), (COL_BASE_SIZE, COL_BASE_SIZE, GF_FTF), "Structure", mat_conc)
    for cy in [0.30, 5.20, 23.00, 30.18]:
        create_box(f"Col_GF_x3.48_y{cy:.1f}", (3.48 - 0.20, cy - 0.20, GF_RAISE), (COL_BASE_SIZE, COL_BASE_SIZE, GF_FTF), "Structure", mat_conc)
        create_box(f"Col_GF_x10.49_y{cy:.1f}", (10.49 - 0.20, cy - 0.20, GF_RAISE), (COL_BASE_SIZE, COL_BASE_SIZE, GF_FTF), "Structure", mat_conc)

    # Upper Storey Columns (300x300 mm, rising through L1, L2, L3, L4 to Roof +16.20)
    upper_levels = [("L1", L1_FFL), ("L2", L2_FFL), ("L3", L3_FFL), ("L4", L4_FFL)]
    for lvl_name, lvl_z in upper_levels:
        # Line x = 6.30 (Left wing courtyard face)
        for cy in [7.30, 11.20, 15.10, 19.10, 23.00]:
            create_box(f"Col_{lvl_name}_x6.30_y{cy:.1f}", (6.30 - 0.15, cy - 0.15, lvl_z), (COL_UPPER_SIZE, COL_UPPER_SIZE, UPPER_FTF), "Structure", mat_conc)
        # Line x = 3.48 (Left wing spine / Front block)
        for cy in [0.30, 5.80, 7.30, 23.00, 30.18]:
            create_box(f"Col_{lvl_name}_x3.48_y{cy:.1f}", (3.48 - 0.15, cy - 0.15, lvl_z), (COL_UPPER_SIZE, COL_UPPER_SIZE, UPPER_FTF), "Structure", mat_conc)
        # Line x = 10.49 (Core / Front block divide / Rear block)
        for cy in [0.30, 5.80, 23.00, 30.18]:
            create_box(f"Col_{lvl_name}_x10.49_y{cy:.1f}", (10.49 - 0.15, cy - 0.15, lvl_z), (COL_UPPER_SIZE, COL_UPPER_SIZE, UPPER_FTF), "Structure", mat_conc)
        # Line x = 13.44 (Right gallery colonnade)
        for cy in [7.30, 15.10, 23.00]:
            create_box(f"Col_{lvl_name}_x13.44_y{cy:.1f}", (13.44 - 0.15, cy - 0.15, lvl_z), (COL_UPPER_SIZE, COL_UPPER_SIZE, UPPER_FTF), "Structure", mat_conc)

    # --------------------------------------------------------------------------
    # D. RC FLOOR SLABS (Podium GF, L1, L2, L3, L4, Roof)
    # --------------------------------------------------------------------------
    
    # 1. Ground Floor Podium Slab (+0.90 FFL, 250 mm thick: z in [0.65, 0.90])
    # Openings:
    # - Ramp slot: x in [0.0, 3.48], y in [0.0, 23.0]
    # - Core: x in [10.49, 14.94], y in [0.30, 5.20]
    # Slabs built as modular structural zones:
    # Zone GF 1: Front entrance podium (x: 3.48 to 10.49, y: 0.0 to 5.20)
    create_box("Slab_Podium_Front", (3.48, 0.0, GF_RAISE - PODIUM_SLAB_THICK), (10.49 - 3.48, 5.20, PODIUM_SLAB_THICK), "GF_Ground", mat_slab)
    # Zone GF 2: Courtyard podium slab (x: 3.48 to 15.24, y: 5.20 to 23.00)
    create_box("Slab_Podium_Courtyard", (3.48, 5.20, GF_RAISE - PODIUM_SLAB_THICK), (PLOT_W_X - 3.48, 23.00 - 5.20, PODIUM_SLAB_THICK), "GF_Ground", mat_slab)
    # Zone GF 3: Rear 2-bed apartment podium slab (x: 0.0 to 15.24, y: 23.00 to 30.48)
    create_box("Slab_Podium_RearBlock", (0.0, 23.00, GF_RAISE - PODIUM_SLAB_THICK), (PLOT_W_X, PLOT_L_Y - 23.00, PODIUM_SLAB_THICK), "GF_Ground", mat_slab)

    # 2. Upper Floor Slabs (L1, L2, L3, L4: 200 mm thick)
    # Courtyard void open to sky: x in [6.30, 13.44], y in [7.30, 23.00] (~112 m² void)
    for lvl_idx, (lvl_name, lvl_z) in enumerate(upper_levels):
        col_lvl = f"{lvl_name}_Floor"
        slab_bot = lvl_z - UPPER_SLAB_THICK
        
        # Block 1: Front Block (1-bed + gallery + store): x 0.0 to 15.24, y 0.0 to 7.30 (except core penetration)
        create_box(f"Slab_{lvl_name}_FrontBlock", (0.0, 0.0, slab_bot), (10.49, 7.30, UPPER_SLAB_THICK), col_lvl, mat_slab)
        # Front gallery link to core: x 10.49 to 15.24, y 5.20 to 7.30
        create_box(f"Slab_{lvl_name}_Gallery_FrontCore", (10.49, 5.20, slab_bot), (PLOT_W_X - 10.49, 7.30 - 5.20, UPPER_SLAB_THICK), col_lvl, mat_slab)
        
        # Block 2: Left/North Wing (Thicker 2-bed): x 0.0 to 6.30, y 7.30 to 23.00
        create_box(f"Slab_{lvl_name}_LeftWing", (0.0, 7.30, slab_bot), (WING_DEPTH, 23.00 - 7.30, UPPER_SLAB_THICK), col_lvl, mat_slab)
        
        # Block 3: Right/South Gallery (1.8m circulation): x 13.44 to 15.24, y 7.30 to 23.00
        create_box(f"Slab_{lvl_name}_RightGallery", (13.44, 7.30, slab_bot), (PLOT_W_X - 13.44, 23.00 - 7.30, UPPER_SLAB_THICK), col_lvl, mat_slab)
        
        # Block 4: Rear/East Block (2-bed premium): x 0.0 to 15.24, y 23.00 to 30.48
        create_box(f"Slab_{lvl_name}_RearBlock", (0.0, 23.00, slab_bot), (PLOT_W_X, PLOT_L_Y - 23.00, UPPER_SLAB_THICK), col_lvl, mat_slab)

    # 3. Roof Slab (+16.20 m, 200 mm thick)
    # Same footprint covering front block, left wing, right gallery, rear block with central courtyard void
    slab_roof_bot = ROOF_SLAB_Z - UPPER_SLAB_THICK
    create_box("Slab_Roof_FrontBlock", (0.0, 0.0, slab_roof_bot), (10.49, 7.30, UPPER_SLAB_THICK), "Roof", mat_slab)
    create_box("Slab_Roof_Gallery_FrontCore", (10.49, 5.20, slab_roof_bot), (PLOT_W_X - 10.49, 7.30 - 5.20, UPPER_SLAB_THICK), "Roof", mat_slab)
    create_box("Slab_Roof_LeftWing", (0.0, 7.30, slab_roof_bot), (WING_DEPTH, 23.00 - 7.30, UPPER_SLAB_THICK), "Roof", mat_slab)
    create_box("Slab_Roof_RightGallery", (13.44, 7.30, slab_roof_bot), (PLOT_W_X - 13.44, 23.00 - 7.30, UPPER_SLAB_THICK), "Roof", mat_slab)
    create_box("Slab_Roof_RearBlock", (0.0, 23.00, slab_roof_bot), (PLOT_W_X, PLOT_L_Y - 23.00, UPPER_SLAB_THICK), "Roof", mat_slab)

    # Roof Parapet (1.10 m high on all perimeter and courtyard edges)
    # Perimeter North, South, East, West parapets
    create_box("Parapet_Roof_North", (0.0, 0.0, ROOF_SLAB_Z), (WALL_THICK_EXT, PLOT_L_Y, PARAPET), "Roof", mat_conc)
    create_box("Parapet_Roof_South", (PLOT_W_X - WALL_THICK_EXT, 0.0, ROOF_SLAB_Z), (WALL_THICK_EXT, PLOT_L_Y, PARAPET), "Roof", mat_conc)
    create_box("Parapet_Roof_East", (0.0, PLOT_L_Y - WALL_THICK_EXT, ROOF_SLAB_Z), (PLOT_W_X, WALL_THICK_EXT, PARAPET), "Roof", mat_conc)
    create_box("Parapet_Roof_West", (0.0, 0.0, ROOF_SLAB_Z), (PLOT_W_X, WALL_THICK_EXT, PARAPET), "Roof", mat_conc)
    # Courtyard void parapet edges:
    create_box("Parapet_Roof_Courtyard_West", (WING_DEPTH, 7.30, ROOF_SLAB_Z), (WALL_THICK_EXT, 23.00 - 7.30, PARAPET), "Roof", mat_conc)
    create_box("Parapet_Roof_Courtyard_East", (13.44 - WALL_THICK_EXT, 7.30, ROOF_SLAB_Z), (WALL_THICK_EXT, 23.00 - 7.30, PARAPET), "Roof", mat_conc)

    # Pack materials dictionary
    mats = {
        "conc": mat_conc, "floor": mat_floor, "ramp": mat_ramp_groove,
        "hazard": mat_hazard, "line": mat_white_line, "bay_blue": mat_bay_blue,
        "bay_green": mat_bay_green, "text": mat_text, "slab": mat_slab,
        "issb": mat_issb, "stone": mat_stone_render, "steel": mat_steel_dark,
        "wood": mat_wood, "glass": mat_glass, "shutter": mat_shutter,
        "lawn": mat_lawn, "shrub": mat_shrub, "paver": mat_paver, "trunk": mat_trunk
    }

    # --------------------------------------------------------------------------
    # E. STAGE 3: GROUND FLOOR ARCHITECTURE, FRONTAGE & COURTYARD LANDSCAPING
    # --------------------------------------------------------------------------
    build_ground_floor(mats)

    # --------------------------------------------------------------------------
    # F. STAGE 4: TYPICAL UPPER FLOORS (L1 to L4)
    # --------------------------------------------------------------------------
    build_upper_floors(mats)

    # --------------------------------------------------------------------------
    # G. STAGE 5: ROOF AMENITIES & GARDEN
    # --------------------------------------------------------------------------
    build_roof(mats)

    # --------------------------------------------------------------------------
    # H. STAGE 6: MATERIALS & SUN SHADING (TIMBER FINS, HOODS, BREEZE BLOCKS)
    # --------------------------------------------------------------------------
    build_sun_shading(mats)

    # --------------------------------------------------------------------------
    # I. STAGE 7: LIGHTING, 8 CAMERAS & ANIMATION PATHS
    # --------------------------------------------------------------------------
    setup_lighting_and_cameras()

    # Save to Courtyard Apartments 50x100 v3.blend
    save_path = r"_PROJ\Courtyard Apartments 50x100 v3.blend"
    bpy.ops.wm.save_as_mainfile(filepath=save_path)
    print(f"Scene successfully saved to: {save_path}")
    print("ALL STAGES (1 through 7) BUILT SUCCESSFULLY!")


def build_ground_floor(mats):
    """
    Stage 3: Ground Floor Frontage, Guard House, Shop, Colonnade, Landscaped Courtyard & Rear 2-Bed Flat.
    """
    col_name = "GF_Ground"
    mat_conc = mats["conc"]
    mat_issb = mats["issb"]
    mat_stone = mats["stone"]
    mat_steel = mats["steel"]
    mat_wood = mats["wood"]
    mat_glass = mats["glass"]
    mat_shutter = mats["shutter"]
    mat_lawn = mats["lawn"]
    mat_shrub = mats["shrub"]
    mat_paver = mats["paver"]
    mat_trunk = mats["trunk"]
    mat_hazard = mats["hazard"]
    
    # --------------------------------------------------------------------------
    # 1. STREET FRONTAGE (y = 0.0 to 5.20)
    # --------------------------------------------------------------------------
    # A. Car Portal (x: 0.0 to 3.48, y: 0.0 to 2.0)
    create_box("GF_Portal_Pier_North", (0.00, 0.00, STREET_LEVEL_Z), (WALL_THICK_EXT, 0.60, 3.40), col_name, mat_conc)
    create_box("GF_Portal_Pier_South", (3.18, 0.00, STREET_LEVEL_Z), (WALL_THICK_EXT, 0.60, 3.40), col_name, mat_conc)
    create_box("GF_Portal_Lintel_Beam", (0.00, 0.00, 3.10), (3.48, 0.60, 0.30), col_name, mat_conc)
    # Motorized Sectional Overhead Door (x: 0.30 to 3.18, y: 1.80, z: 0.0 to 2.90)
    create_box("GF_Portal_Sectional_Door", (0.30, 1.80, STREET_LEVEL_Z), (2.88, 0.06, 2.90), col_name, mat_steel)
    # Traffic Signal Housing & Amber Flasher
    create_box("GF_Portal_Traffic_Signal", (3.22, 0.55, 2.40), (0.15, 0.15, 0.40), col_name, mat_steel)
    create_box("GF_Portal_Signal_Red", (3.20, 0.57, 2.62), (0.04, 0.11, 0.11), col_name, mat_hazard)
    create_box("GF_Portal_Signal_Green", (3.20, 0.57, 2.45), (0.04, 0.11, 0.11), col_name, mats["bay_green"])
    
    # B. Guard House (x: 3.48 to 5.68, y: 0.0 to 3.0, z: 0.0 to 3.20) at Street Level (z = 0.00)
    create_box("GF_Guard_Plinth", (3.48, 0.00, STREET_LEVEL_Z), (2.20, 3.00, 0.15), col_name, mat_conc)
    # ISSB Outer Walls (height 3.05 m, up to z = 3.20)
    create_box("GF_Guard_Wall_West", (3.80, 0.00, 0.15), (1.88, 0.15, 3.05), col_name, mat_issb)
    create_box("GF_Guard_Wall_East_Courtyard", (3.48, 2.85, 0.15), (2.20, 0.15, 3.05), col_name, mat_issb)
    create_box("GF_Guard_Wall_South", (5.53, 0.00, 0.15), (0.15, 3.00, 3.05), col_name, mat_issb)
    create_box("GF_Guard_Wall_North", (3.48, 0.60, 0.15), (0.15, 2.40, 3.05), col_name, mat_issb)
    # Chamfered corner wall (NW) overlooking vehicle portal
    create_plane("GF_Guard_Chamfer_Wall", (3.48, 0.60, 0.15), (3.80, 0.00, 0.15), (3.80, 0.00, 3.20), (3.48, 0.60, 3.20), col_name, mat_issb)
    # Inspection Windows
    create_plane("GF_Guard_Window_Ramp", (3.52, 0.50, 1.00), (3.75, 0.08, 1.00), (3.75, 0.08, 2.20), (3.52, 0.50, 2.20), col_name, mat_glass)
    create_box("GF_Guard_Window_Gate", (5.51, 0.80, 1.00), (0.19, 1.20, 1.20), col_name, mat_glass)
    create_box("GF_Guard_Window_Courtyard", (4.00, 2.83, 1.10), (1.10, 0.19, 1.10), col_name, mat_glass)
    # Internal WC partition (1.0 x 1.4 m)
    create_box("GF_Guard_WC_Wall", (3.48, 1.60, 0.15), (1.20, 0.12, 2.50), col_name, mat_issb)
    # Guard Desk & CCTV Console
    create_box("GF_Guard_Desk", (4.10, 0.40, 0.15), (1.20, 0.60, 0.75), col_name, mat_wood)
    create_box("GF_Guard_CCTV_Monitor", (4.40, 0.60, 0.90), (0.50, 0.15, 0.35), col_name, mat_steel)
    
    # C. Storage / Bin & Meter Niche (x: 3.48 to 5.68, y: 3.0 to 5.20)
    create_box("GF_Store_Wall_South", (5.53, 3.00, 0.15), (0.15, 2.20, 3.05), col_name, mat_issb)
    create_box("GF_Store_Wall_East", (3.48, 5.05, 0.15), (2.20, 0.15, 3.05), col_name, mat_issb)
    create_box("GF_Store_Louver_Door", (5.51, 3.40, 0.15), (0.19, 1.40, 2.20), col_name, mat_steel)
    create_box("GF_Store_Meter_Box", (3.65, 3.20, 1.00), (0.25, 1.20, 1.00), col_name, mat_steel)
    create_box("GF_Store_Waste_Bins", (3.80, 4.30, 0.15), (1.20, 0.70, 0.90), col_name, mat_conc)
    
    # D. Pedestrian Gate & Covered Entry (x: 5.68 to 7.28, y: 0.0 to 5.20)
    create_plane("GF_Pedestrian_Entry_Floor", (5.68, 0.00, STREET_LEVEL_Z + 0.01), (7.28, 0.00, STREET_LEVEL_Z + 0.01), (7.28, 5.20, STREET_LEVEL_Z + 0.01), (5.68, 5.20, STREET_LEVEL_Z + 0.01), col_name, mat_paver)
    create_box("GF_Pedestrian_Gate_Frame", (5.75, 0.00, STREET_LEVEL_Z), (1.45, 0.08, 2.40), col_name, mat_steel)
    create_box("GF_Pedestrian_Intercom_Post", (5.70, -0.10, STREET_LEVEL_Z), (0.15, 0.15, 1.40), col_name, mat_steel)
    # Accessible Ramp (<= 1:12 slope) up to Podium +0.90m
    create_plane("GF_Access_Ramp_Part1", (5.80, 1.20, 0.01), (7.00, 1.20, 0.01), (7.00, 5.20, 0.45), (5.80, 5.20, 0.45), col_name, mat_paver)
    create_plane("GF_Access_Ramp_Part2", (7.00, 5.20, 0.45), (7.00, 6.40, 0.45), (10.50, 6.40, 0.90), (10.50, 5.20, 0.90), col_name, mat_paver)
    create_box("GF_Ramp_Rail_1", (5.78, 1.20, 0.00), (0.05, 4.00, 1.20), col_name, mat_steel)
    create_box("GF_Ramp_Rail_2", (7.00, 5.20, 0.45), (3.50, 0.05, 1.35), col_name, mat_steel)
    # Direct access concrete steps
    for stp in range(5):
        sz = stp * 0.18
        create_box(f"GF_Entry_Step_{stp+1}", (6.00, 3.20 + stp*0.35, 0.00), (1.20, 0.35, sz + 0.18), col_name, mat_conc)
        
    # E. Commercial Shop (x: 7.28 to 10.49, y: 0.0 to 5.20, z: 0.0 to 4.00) at Street Level (z = 0.00)
    create_plane("GF_Shop_Floor", (7.28, 0.00, 0.01), (10.49, 0.00, 0.01), (10.49, 5.20, 0.01), (7.28, 5.20, 0.01), col_name, mat_paver)
    create_box("GF_Shop_Wall_Rear_Courtyard", (7.28, 5.00, 0.00), (3.21, 0.20, 4.00), col_name, mat_issb)
    create_box("GF_Shop_Wall_West_Side", (7.28, 0.00, 0.00), (0.15, 5.00, 4.00), col_name, mat_issb)
    create_box("GF_Shop_Wall_East_Side", (10.34, 0.00, 0.00), (0.15, 5.00, 4.00), col_name, mat_issb)
    create_box("GF_Shop_Roller_Shutter", (7.45, 0.00, 0.00), (2.85, 0.08, 3.20), col_name, mat_shutter)
    create_box("GF_Shop_Glazed_Door", (7.50, 0.15, 0.00), (2.75, 0.05, 3.00), col_name, mat_glass)
    create_box("GF_Shop_Counter", (7.80, 2.50, 0.00), (2.00, 0.60, 0.90), col_name, mat_wood)
    create_box("GF_Shop_Display_Shelves", (10.15, 1.00, 0.00), (0.18, 3.50, 2.40), col_name, mat_wood)

    # F. Core Ground Entrance (x: 10.49 to 15.24, y: 0.3 to 5.20)
    create_box("GF_Core_Glass_Entry", (10.80, 5.15, GF_RAISE), (2.20, 0.10, 2.60), col_name, mat_glass)
    create_box("GF_Core_Entry_Frame", (10.75, 5.12, GF_RAISE), (2.30, 0.16, 2.70), col_name, mat_steel)

    # --------------------------------------------------------------------------
    # 2. CAR RAMP SCREEN WALL (CORDON OFF THE RAMP FROM COURTYARD)
    # --------------------------------------------------------------------------
    create_box("GF_Ramp_Screen_Wall", (3.60, 0.00, GF_RAISE), (0.15, 23.00, GF_FTF - PODIUM_SLAB_THICK), col_name, mat_issb)
    create_box("GF_Ramp_Screen_Coping", (3.58, 0.00, GF_RAISE + GF_FTF - PODIUM_SLAB_THICK), (0.19, 23.00, 0.08), col_name, mat_conc)
    create_box("GF_Ramp_Climbers_Trellis", (3.75, 5.20, GF_RAISE + 0.30), (0.05, 17.80, 2.40), col_name, mat_shrub)

    # --------------------------------------------------------------------------
    # 3. GF COURTYARD SHADED COLONNADE (x: 3.60 to 6.30, y: 5.20 to 23.00)
    # --------------------------------------------------------------------------
    create_plane("GF_Colonnade_Floor", (3.60, 5.20, GF_RAISE + 0.01), (6.30, 5.20, GF_RAISE + 0.01), (6.30, 23.00, GF_RAISE + 0.01), (3.60, 23.00, GF_RAISE + 0.01), col_name, mat_paver)
    bench_spans = [(5.60, 8.40), (9.20, 13.55), (14.35, 18.70), (19.50, 22.60)]
    for idx, (by1, by2) in enumerate(bench_spans):
        blen = by2 - by1
        create_box(f"GF_Colonnade_Bench_Base_{idx+1}", (6.05, by1, GF_RAISE), (0.50, blen, 0.42), col_name, mat_issb)
        create_box(f"GF_Colonnade_Bench_Seat_{idx+1}", (6.02, by1, GF_RAISE + 0.42), (0.56, blen, 0.04), col_name, mat_wood)
        create_box(f"GF_Colonnade_Planter_{idx+1}", (5.80, by1 - 0.35, GF_RAISE), (0.60, 0.35, 0.60), col_name, mat_issb)
        create_box(f"GF_Colonnade_Foliage_{idx+1}", (5.82, by1 - 0.33, GF_RAISE + 0.50), (0.56, 0.31, 0.30), col_name, mat_shrub)

    # --------------------------------------------------------------------------
    # 4. GROUND FLOOR REAR 2-BEDROOM APARTMENT (x: 3.60 to 15.24, y: 23.00 to 30.48)
    # --------------------------------------------------------------------------
    create_box("GF_Rear_Wall_Boundary_South", (PLOT_W_X - WALL_THICK_EXT, 23.00, GF_RAISE), (WALL_THICK_EXT, PLOT_L_Y - 23.00, GF_FTF), col_name, mat_stone)
    create_box("GF_Rear_Wall_Boundary_East", (0.00, PLOT_L_Y - WALL_THICK_EXT, GF_RAISE), (PLOT_W_X, WALL_THICK_EXT, GF_FTF), col_name, mat_stone)
    create_box("GF_Rear_Wall_Boundary_North", (0.00, 23.00, GF_RAISE), (WALL_THICK_EXT, PLOT_L_Y - 23.00, GF_FTF), col_name, mat_stone)
    
    # Courtyard Facing Facade Wall at y = 23.00
    create_box("GF_Rear_Entry_Door", (6.30, 22.95, GF_RAISE), (0.90, 0.10, 2.20), col_name, mat_wood)
    create_box("GF_Rear_Living_Glazing", (7.50, 22.95, GF_RAISE), (3.00, 0.08, 2.50), col_name, mat_glass)
    create_box("GF_Rear_Living_Glazing_Frame", (7.45, 22.92, GF_RAISE), (3.10, 0.14, 2.55), col_name, mat_steel)
    create_box("GF_Rear_Master_Window", (11.50, 22.95, GF_RAISE + 0.90), (2.50, 0.08, 1.50), col_name, mat_glass)
    create_box("GF_Rear_Wall_Courtyard_1", (3.60, 22.90, GF_RAISE), (2.70, 0.15, GF_FTF - PODIUM_SLAB_THICK), col_name, mat_issb)
    create_box("GF_Rear_Wall_Courtyard_2", (7.20, 22.90, GF_RAISE), (0.30, 0.15, GF_FTF - PODIUM_SLAB_THICK), col_name, mat_issb)
    create_box("GF_Rear_Wall_Courtyard_3", (10.50, 22.90, GF_RAISE), (1.00, 0.15, GF_FTF - PODIUM_SLAB_THICK), col_name, mat_issb)
    create_box("GF_Rear_Wall_Courtyard_4", (14.00, 22.90, GF_RAISE), (1.24 - WALL_THICK_EXT, 0.15, GF_FTF - PODIUM_SLAB_THICK), col_name, mat_issb)
    
    # Internal Partitions (150 mm ISSB)
    create_box("GF_Rear_Part_Spine", (3.60, 27.00, GF_RAISE), (7.00, WALL_THICK_INT, 2.80), col_name, mat_issb)
    create_box("GF_Rear_Part_BedMaster", (11.00, 23.00, GF_RAISE), (WALL_THICK_INT, 4.00, 2.80), col_name, mat_issb)
    create_box("GF_Rear_Part_Bed2", (6.30, 27.00, GF_RAISE), (WALL_THICK_INT, 3.18, 2.80), col_name, mat_issb)
    create_box("GF_Rear_Part_BathMaster", (12.50, 27.00, GF_RAISE), (WALL_THICK_INT, 3.18, 2.80), col_name, mat_issb)
    
    # Kitchen & Laundry Yard (x: 0.30 to 3.60, y: 23.00 to 30.18)
    create_box("GF_Rear_Kitchen_Wall_West", (3.60, 23.00, GF_RAISE), (WALL_THICK_INT, 4.00, 2.80), col_name, mat_issb)
    create_box("GF_Rear_Kitchen_Counter", (3.75, 23.20, GF_RAISE), (2.20, 0.60, 0.90), col_name, mat_conc)
    create_plane("GF_Laundry_Yard_Floor", (0.30, 23.00, GF_RAISE + 0.01), (3.60, 23.00, GF_RAISE + 0.01), (3.60, 30.18, GF_RAISE + 0.01), (0.30, 30.18, GF_RAISE + 0.01), col_name, mat_paver)
    create_box("GF_Laundry_Sink_Bench", (0.50, 28.00, GF_RAISE), (0.80, 1.80, 0.85), col_name, mat_conc)

    # --------------------------------------------------------------------------
    # 5. LANDSCAPED COURTYARD (x: 3.60 to 15.24, y: 5.20 to 23.00)
    # --------------------------------------------------------------------------
    # A. Raised Central Lawn (300 mm build-up, top at +1.20m)
    create_box("GF_Courtyard_Lawn_Soil", (7.20, 8.50, GF_RAISE), (5.30, 11.00, 0.30), col_name, mat_conc)
    create_plane("GF_Courtyard_Lawn_Turf", (7.20, 8.50, GF_RAISE + 0.305), (12.50, 8.50, GF_RAISE + 0.305), (12.50, 19.50, GF_RAISE + 0.305), (7.20, 19.50, GF_RAISE + 0.305), col_name, mat_lawn)
    # Lawn ISSB Retaining Edge / Seat Wall (450 mm above podium = +1.35m)
    create_box("GF_Lawn_Seat_Wall_West", (6.90, 8.50, GF_RAISE), (0.30, 11.00, 0.45), col_name, mat_issb)
    create_box("GF_Lawn_Seat_Wall_East", (12.50, 8.50, GF_RAISE), (0.30, 11.00, 0.45), col_name, mat_issb)
    create_box("GF_Lawn_Seat_Wall_North", (6.90, 8.20, GF_RAISE), (5.90, 0.30, 0.45), col_name, mat_issb)
    create_box("GF_Lawn_Seat_Wall_South", (6.90, 19.50, GF_RAISE), (5.90, 0.30, 0.45), col_name, mat_issb)
    # Timber Bench Slats
    create_box("GF_Lawn_Bench_Wood_1", (6.88, 10.00, GF_RAISE + 0.45), (0.34, 3.00, 0.04), col_name, mat_wood)
    create_box("GF_Lawn_Bench_Wood_2", (12.48, 12.00, GF_RAISE + 0.45), (0.34, 3.00, 0.04), col_name, mat_wood)

    # B. Raised Shrub Beds (600 mm deep, top at +1.50m) along South Boundary Wall
    create_box("GF_Shrub_Bed_Wall", (13.44, 7.30, GF_RAISE), (0.20, 14.70, 0.60), col_name, mat_issb)
    create_box("GF_Shrub_Bed_Soil", (13.64, 7.30, GF_RAISE), (1.30, 14.70, 0.55), col_name, mat_conc)
    create_box("GF_Shrub_Bed_Plants", (13.64, 7.30, GF_RAISE + 0.55), (1.30, 14.70, 0.60), col_name, mat_shrub)

    # C. Feature Tree Planter & Architectural Multi-Stem Tree (at x = 9.85, y = 14.50)
    create_box("GF_Tree_Planter_Box", (8.65, 13.30, GF_RAISE), (2.40, 2.40, 1.20), col_name, mat_issb)
    create_box("GF_Tree_Planter_Coping", (8.60, 13.25, GF_RAISE + 1.20), (2.50, 2.50, 0.08), col_name, mat_conc)
    create_box("GF_Tree_Planter_Soil", (8.80, 13.45, GF_RAISE + 1.10), (2.10, 2.10, 0.10), col_name, mat_conc)
    tree_base_z = GF_RAISE + 1.20
    create_cylinder("GF_Tree_Stem_1", (9.85, 14.50, tree_base_z), 0.12, 3.20, col_name, mat_trunk)
    create_cylinder("GF_Tree_Stem_2", (9.70, 14.35, tree_base_z), 0.09, 3.50, col_name, mat_trunk)
    create_cylinder("GF_Tree_Stem_3", (10.00, 14.65, tree_base_z), 0.10, 3.00, col_name, mat_trunk)
    create_icosphere("GF_Tree_Canopy_1", (9.85, 14.50, tree_base_z + 3.80), 2.20, col_name, mat_shrub, subdivisions=2)
    create_icosphere("GF_Tree_Canopy_2", (9.50, 14.20, tree_base_z + 4.20), 1.70, col_name, mat_shrub, subdivisions=2)
    create_icosphere("GF_Tree_Canopy_3", (10.20, 14.80, tree_base_z + 3.90), 1.80, col_name, mat_shrub, subdivisions=2)

    # D. Permeable Paver Loop Walkways
    create_plane("GF_Path_North_Cross", (6.30, 7.30, GF_RAISE + 0.01), (13.44, 7.30, GF_RAISE + 0.01), (13.44, 8.50, GF_RAISE + 0.01), (6.30, 8.50, GF_RAISE + 0.01), col_name, mat_paver)
    create_plane("GF_Path_South_Cross", (6.30, 19.50, GF_RAISE + 0.01), (13.44, 19.50, GF_RAISE + 0.01), (13.44, 23.00, GF_RAISE + 0.01), (6.30, 23.00, GF_RAISE + 0.01), col_name, mat_paver)
    create_plane("GF_Path_East_Gallery", (12.50, 8.50, GF_RAISE + 0.01), (13.44, 8.50, GF_RAISE + 0.01), (13.44, 19.50, GF_RAISE + 0.01), (12.50, 19.50, GF_RAISE + 0.01), col_name, mat_paver)

    # E. Rain Garden Bioswale
    create_box("GF_Rain_Garden_Bed", (7.20, 19.80, GF_RAISE), (1.60, 2.70, 0.20), col_name, mat_conc)
    create_box("GF_Rain_Garden_Plants", (7.25, 19.85, GF_RAISE + 0.20), (1.50, 2.60, 0.35), col_name, mat_shrub)

    print("Stage 3 Ground Floor build complete: Frontage, Guard, Shop, Cordon Wall, Colonnade, Rear 2-Bed, Courtyard Landscaping.")


def build_upper_floors(mats):
    """
    Stage 4: Typical Upper Floors (L1, L2, L3, L4).
    Each floor contains:
    - Front 1-bed flat (~55 m² net) with recessed street balcony
    - Extract shafts & tenant store
    - Front gallery (1.5 m)
    - Thicker 2-bed left wing (~88 m² net) with two-zone plan
    - Staggered cantilevered balconies (1.2 m projection) into courtyard
    - Right gallery (1.8 m) with balustrade and planters
    - Rear 2-bed premium flat (~100 m² net) with loggia
    - Furniture blocks
    """
    mat_conc = mats["conc"]
    mat_issb = mats["issb"]
    mat_stone = mats["stone"]
    mat_steel = mats["steel"]
    mat_wood = mats["wood"]
    mat_glass = mats["glass"]
    mat_shrub = mats["shrub"]
    mat_paver = mats["paver"]

    upper_floors = [
        ("L1", L1_FFL, 1),
        ("L2", L2_FFL, 2),
        ("L3", L3_FFL, 3),
        ("L4", L4_FFL, 4),
    ]

    for lvl_name, lvl_z, f_num in upper_floors:
        col_lvl = f"{lvl_name}_Floor"
        room_h = UPPER_FTF - UPPER_SLAB_THICK  # 2.80 m clear

        # 1. PERIMETER BOUNDARY WALLS (Solid Machine-Cut Stone Rendered, NO windows)
        create_box(f"{lvl_name}_Boundary_Wall_North", (0.00, 0.00, lvl_z), (WALL_THICK_EXT, PLOT_L_Y, room_h), col_lvl, mat_stone)
        create_box(f"{lvl_name}_Boundary_Wall_South", (PLOT_W_X - WALL_THICK_EXT, 0.00, lvl_z), (WALL_THICK_EXT, PLOT_L_Y, room_h), col_lvl, mat_stone)
        create_box(f"{lvl_name}_Boundary_Wall_East", (0.00, PLOT_L_Y - WALL_THICK_EXT, lvl_z), (PLOT_W_X, WALL_THICK_EXT, room_h), col_lvl, mat_stone)

        # 2. FRONT 1-BED APARTMENT (x: 0.0 to 10.49, y: 0.0 to 5.80, ~55 m² net)
        # Street West Façade: Recessed Balcony at x: [3.48, 7.00], recessed 1.2 m
        create_box(f"{lvl_name}_1Bed_Wall_Street_Bed", (WALL_THICK_EXT, 0.00, lvl_z), (3.48 - WALL_THICK_EXT, 0.20, room_h), col_lvl, mat_stone)
        create_box(f"{lvl_name}_1Bed_Win_Street_Bed", (0.80, 0.02, lvl_z + 0.90), (2.00, 0.10, 1.50), col_lvl, mat_glass)
        
        # Recessed Balcony balustrade along street boundary y = 0.0
        create_box(f"{lvl_name}_1Bed_Balc_Balustrade", (3.48, 0.00, lvl_z), (3.52, 0.05, 1.10), col_lvl, mat_steel)
        create_box(f"{lvl_name}_1Bed_Balc_Planter", (3.50, 0.05, lvl_z), (3.48, 0.35, 0.40), col_lvl, mat_issb)
        create_box(f"{lvl_name}_1Bed_Balc_Plants", (3.52, 0.07, lvl_z + 0.35), (3.44, 0.31, 0.25), col_lvl, mat_shrub)
        create_plane(f"{lvl_name}_1Bed_Balc_Floor", (3.48, 0.00, lvl_z + 0.01), (7.00, 0.00, lvl_z + 0.01), (7.00, 1.20, lvl_z + 0.01), (3.48, 1.20, lvl_z + 0.01), col_lvl, mat_paver)
        create_box(f"{lvl_name}_1Bed_Living_Glazing", (3.60, 1.15, lvl_z), (3.20, 0.08, 2.40), col_lvl, mat_glass)
        create_box(f"{lvl_name}_1Bed_Living_Wall_Recess", (3.48, 1.10, lvl_z), (3.52, 0.15, room_h), col_lvl, mat_issb)

        create_box(f"{lvl_name}_1Bed_Wall_Street_Kit", (7.00, 0.00, lvl_z), (3.49, 0.20, room_h), col_lvl, mat_stone)
        create_box(f"{lvl_name}_1Bed_Win_Street_Kit", (7.60, 0.02, lvl_z + 1.10), (1.80, 0.10, 1.30), col_lvl, mat_glass)

        create_box(f"{lvl_name}_1Bed_Wall_Gallery_Rear", (3.00, 5.65, lvl_z), (7.49, 0.15, room_h), col_lvl, mat_issb)
        create_box(f"{lvl_name}_1Bed_Entry_Door", (6.80, 5.60, lvl_z), (0.90, 0.08, 2.10), col_lvl, mat_wood)

        # Partitions inside 1-bed
        create_box(f"{lvl_name}_1Bed_Part_Bed", (3.48, 1.20, lvl_z), (WALL_THICK_INT, 4.60, room_h), col_lvl, mat_issb)
        create_box(f"{lvl_name}_1Bed_Part_Bath_Y", (7.50, 3.60, lvl_z), (2.99, WALL_THICK_INT, room_h), col_lvl, mat_issb)
        create_box(f"{lvl_name}_1Bed_Part_Bath_X", (7.50, 3.60, lvl_z), (WALL_THICK_INT, 2.20, room_h), col_lvl, mat_issb)

        # Furniture in 1-bed
        create_box(f"{lvl_name}_1Bed_Bed", (0.80, 2.00, lvl_z), (1.80, 2.00, 0.55), col_lvl, mat_wood)
        create_box(f"{lvl_name}_1Bed_Sofa", (3.90, 2.80, lvl_z), (2.00, 0.85, 0.75), col_lvl, mat_wood)
        create_box(f"{lvl_name}_1Bed_DiningTable", (7.50, 1.50, lvl_z), (1.40, 0.80, 0.75), col_lvl, mat_wood)

        # 3. STORE & EXTRACT SHAFTS (x: 0.0 to 3.0, y: 5.80 to 7.30)
        create_box(f"{lvl_name}_Vent_Shaft_1", (0.30, 5.90, lvl_z), (0.80, 0.80, room_h), col_lvl, mat_conc)
        create_box(f"{lvl_name}_Vent_Shaft_2", (1.30, 5.90, lvl_z), (0.80, 0.80, room_h), col_lvl, mat_conc)
        create_box(f"{lvl_name}_Store_Wall_East", (2.85, 5.80, lvl_z), (0.15, 1.50, room_h), col_lvl, mat_issb)
        create_box(f"{lvl_name}_Store_Door", (2.80, 6.20, lvl_z), (0.10, 0.80, 2.10), col_lvl, mat_wood)

        # 4. FRONT GALLERY (x: 3.0 to 15.24, y: 5.80 to 7.30)
        create_plane(f"{lvl_name}_Front_Gallery_Floor", (3.00, 5.80, lvl_z + 0.01), (10.49, 5.80, lvl_z + 0.01), (10.49, 7.30, lvl_z + 0.01), (3.00, 7.30, lvl_z + 0.01), col_lvl, mat_paver)
        create_box(f"{lvl_name}_Front_Gallery_Balustrade", (6.30, 7.25, lvl_z), (7.14, 0.05, 1.10), col_lvl, mat_steel)
        create_box(f"{lvl_name}_Front_Gallery_Planter", (6.35, 7.00, lvl_z), (7.04, 0.25, 0.40), col_lvl, mat_issb)
        create_box(f"{lvl_name}_Front_Gallery_Plants", (6.37, 7.02, lvl_z + 0.35), (7.00, 0.21, 0.20), col_lvl, mat_shrub)

        # 5. LEFT WING THICKER 2-BED (x: 0.0 to 6.30, y: 7.30 to 23.00, ~88 m² net)
        create_box(f"{lvl_name}_2BedL_Entry_Door", (3.50, 7.25, lvl_z), (0.90, 0.10, 2.10), col_lvl, mat_wood)
        create_box(f"{lvl_name}_2BedL_Wall_Gallery", (0.00, 7.15, lvl_z), (6.30, 0.15, room_h), col_lvl, mat_issb)

        # Service Spine Wall
        create_box(f"{lvl_name}_2BedL_Spine_Wall", (2.40, 7.30, lvl_z), (WALL_THICK_INT, 15.70, room_h), col_lvl, mat_issb)
        create_box(f"{lvl_name}_2BedL_Kitchen_Counter", (0.35, 7.50, lvl_z), (0.60, 3.20, 0.90), col_lvl, mat_conc)
        create_box(f"{lvl_name}_2BedL_Part_Bath1", (0.30, 11.00, lvl_z), (2.10, WALL_THICK_INT, room_h), col_lvl, mat_issb)
        create_box(f"{lvl_name}_2BedL_Part_Bath2", (0.30, 13.50, lvl_z), (2.10, WALL_THICK_INT, room_h), col_lvl, mat_issb)
        create_box(f"{lvl_name}_2BedL_Part_DryingYard", (0.30, 16.00, lvl_z), (2.10, WALL_THICK_INT, room_h), col_lvl, mat_issb)

        # Room Dividers
        create_box(f"{lvl_name}_2BedL_Part_Living_Bed2", (2.40, 13.50, lvl_z), (3.90, WALL_THICK_INT, room_h), col_lvl, mat_issb)
        create_box(f"{lvl_name}_2BedL_Part_Bed2_Master", (2.40, 17.50, lvl_z), (3.90, WALL_THICK_INT, room_h), col_lvl, mat_issb)

        # Courtyard Façade Wall at x = 6.30
        create_box(f"{lvl_name}_2BedL_Courtyard_Wall", (6.15, 7.30, lvl_z), (0.15, 15.70, room_h), col_lvl, mat_issb)
        create_box(f"{lvl_name}_2BedL_Living_Glaze", (6.22, 8.50, lvl_z), (0.08, 3.00, 2.40), col_lvl, mat_glass)
        create_box(f"{lvl_name}_2BedL_Bed2_Win", (6.22, 14.50, lvl_z + 0.90), (0.08, 2.00, 1.50), col_lvl, mat_glass)
        create_box(f"{lvl_name}_2BedL_Master_Glaze", (6.22, 19.00, lvl_z), (0.08, 3.00, 2.40), col_lvl, mat_glass)

        # Furniture in Left 2-bed
        create_box(f"{lvl_name}_2BedL_Sofa", (3.00, 9.00, lvl_z), (2.10, 0.90, 0.75), col_lvl, mat_wood)
        create_box(f"{lvl_name}_2BedL_DiningTable", (3.00, 11.80, lvl_z), (1.60, 0.90, 0.75), col_lvl, mat_wood)
        create_box(f"{lvl_name}_2BedL_Bed2", (3.00, 14.50, lvl_z), (1.60, 2.00, 0.55), col_lvl, mat_wood)
        create_box(f"{lvl_name}_2BedL_BedMaster", (3.00, 19.50, lvl_z), (1.80, 2.00, 0.55), col_lvl, mat_wood)

        # 6. STAGGERED CANTILEVERED BALCONIES INTO COURTYARD (1.20 m PROJECTION)
        if f_num in [1, 3]:
            balc_spans = [
                (f"{lvl_name}_Balc_Living", 8.20, 11.40),
                (f"{lvl_name}_Balc_Master", 19.20, 22.40)
            ]
        else:
            balc_spans = [
                (f"{lvl_name}_Balc_Living", 9.80, 13.00),
                (f"{lvl_name}_Balc_Master", 17.60, 20.80)
            ]

        for b_name, by1, by2 in balc_spans:
            blen = by2 - by1
            create_box(f"{b_name}_Slab", (6.30, by1, lvl_z - UPPER_SLAB_THICK), (BALCONY_PROJ, blen, UPPER_SLAB_THICK), col_lvl, mats["slab"])
            create_plane(f"{b_name}_Floor", (6.30, by1, lvl_z + 0.01), (7.50, by1, lvl_z + 0.01), (7.50, by2, lvl_z + 0.01), (6.30, by2, lvl_z + 0.01), col_lvl, mat_paver)
            create_box(f"{b_name}_Rail_East", (7.45, by1, lvl_z), (0.05, blen, 1.10), col_lvl, mat_steel)
            create_box(f"{b_name}_Rail_North", (6.30, by1, lvl_z), (BALCONY_PROJ, 0.05, 1.10), col_lvl, mat_steel)
            create_box(f"{b_name}_Rail_South", (6.30, by2 - 0.05, lvl_z), (BALCONY_PROJ, 0.05, 1.10), col_lvl, mat_steel)
            create_box(f"{b_name}_Planter", (7.20, by1, lvl_z), (0.25, blen, 0.40), col_lvl, mat_issb)
            create_box(f"{b_name}_Plants", (7.22, by1 + 0.05, lvl_z + 0.35), (0.21, blen - 0.10, 0.25), col_lvl, mat_shrub)

        # 7. RIGHT GALLERY (x: 13.44 to 15.24, y: 7.30 to 23.00, 1.8 m wide)
        create_plane(f"{lvl_name}_Right_Gallery_Floor", (13.44, 7.30, lvl_z + 0.01), (15.24 - WALL_THICK_EXT, 7.30, lvl_z + 0.01), (15.24 - WALL_THICK_EXT, 23.00, lvl_z + 0.01), (13.44, 23.00, lvl_z + 0.01), col_lvl, mat_paver)
        create_box(f"{lvl_name}_Right_Gallery_Balustrade", (13.44, 7.30, lvl_z), (0.05, 15.70, 1.10), col_lvl, mat_steel)
        create_box(f"{lvl_name}_Right_Gallery_Planter", (13.49, 7.30, lvl_z), (0.30, 15.70, 0.40), col_lvl, mat_issb)
        create_box(f"{lvl_name}_Right_Gallery_Plants", (13.51, 7.35, lvl_z + 0.35), (0.26, 15.60, 0.25), col_lvl, mat_shrub)

        # 8. REAR 2-BED PREMIUM APARTMENT (x: 0.0 to 15.24, y: 23.00 to 30.48, ~100 m² net)
        create_box(f"{lvl_name}_2BedR_Entry_Door", (13.50, 23.00, lvl_z), (0.90, 0.10, 2.10), col_lvl, mat_wood)
        create_box(f"{lvl_name}_2BedR_Courtyard_Wall_1", (0.30, 22.85, lvl_z), (6.00, 0.15, room_h), col_lvl, mat_issb)
        create_box(f"{lvl_name}_2BedR_Courtyard_Wall_2", (11.50, 22.85, lvl_z), (1.94, 0.15, room_h), col_lvl, mat_issb)
        create_box(f"{lvl_name}_2BedR_Bed2_Win", (2.00, 22.88, lvl_z + 0.90), (2.50, 0.08, 1.50), col_lvl, mat_glass)
        create_box(f"{lvl_name}_2BedR_Master_Win", (11.80, 22.88, lvl_z + 0.90), (2.20, 0.08, 1.50), col_lvl, mat_glass)

        # Recessed Loggia / Balcony: x: [6.50, 11.20], y: [21.80, 23.00]
        create_box(f"{lvl_name}_2BedR_Loggia_Slab", (6.50, 21.80, lvl_z - UPPER_SLAB_THICK), (4.70, 1.20, UPPER_SLAB_THICK), col_lvl, mats["slab"])
        create_plane(f"{lvl_name}_2BedR_Loggia_Floor", (6.50, 21.80, lvl_z + 0.01), (11.20, 21.80, lvl_z + 0.01), (11.20, 23.00, lvl_z + 0.01), (6.50, 23.00, lvl_z + 0.01), col_lvl, mat_paver)
        create_box(f"{lvl_name}_2BedR_Loggia_Rail_South", (6.50, 21.80, lvl_z), (4.70, 0.05, 1.10), col_lvl, mat_steel)
        create_box(f"{lvl_name}_2BedR_Loggia_Rail_West", (6.50, 21.80, lvl_z), (0.05, 1.20, 1.10), col_lvl, mat_steel)
        create_box(f"{lvl_name}_2BedR_Loggia_Rail_East", (11.15, 21.80, lvl_z), (0.05, 1.20, 1.10), col_lvl, mat_steel)
        create_box(f"{lvl_name}_2BedR_Loggia_Planter", (6.55, 21.85, lvl_z), (4.60, 0.30, 0.40), col_lvl, mat_issb)
        create_box(f"{lvl_name}_2BedR_Loggia_Plants", (6.57, 21.87, lvl_z + 0.35), (4.56, 0.26, 0.25), col_lvl, mat_shrub)
        create_box(f"{lvl_name}_2BedR_Living_Glaze", (7.00, 22.92, lvl_z), (3.80, 0.08, 2.40), col_lvl, mat_glass)

        # Internal Partitions
        create_box(f"{lvl_name}_2BedR_Part_Living_Bed2", (6.30, 23.00, lvl_z), (WALL_THICK_INT, 4.00, room_h), col_lvl, mat_issb)
        create_box(f"{lvl_name}_2BedR_Part_Living_Master", (11.20, 23.00, lvl_z), (WALL_THICK_INT, 4.00, room_h), col_lvl, mat_issb)
        create_box(f"{lvl_name}_2BedR_Part_Spine_Rear", (0.30, 27.00, lvl_z), (14.64, WALL_THICK_INT, room_h), col_lvl, mat_issb)
        create_box(f"{lvl_name}_2BedR_Part_Kitchen", (6.30, 27.00, lvl_z), (WALL_THICK_INT, 3.18, room_h), col_lvl, mat_issb)
        create_box(f"{lvl_name}_2BedR_Part_Baths", (10.50, 27.00, lvl_z), (WALL_THICK_INT, 3.18, room_h), col_lvl, mat_issb)

    print("Stage 4 Upper Floors (L1-L4) build complete: 1-Bed, Thicker 2-Bed, Staggered Balconies, Rear Premium 2-Bed, Furniture.")


def build_roof(mats):
    """
    Stage 5: Roof Amenities (Stair enclosure to roof per s.194(2), Lift overrun,
    Elevated water tanks, Solar PV + Solar water heaters, Communal roof garden,
    Pergola, Seating, Drying yard, Drainage).
    """
    col_name = "Roof"
    mat_conc = mats["conc"]
    mat_issb = mats["issb"]
    mat_steel = mats["steel"]
    mat_wood = mats["wood"]
    mat_shrub = mats["shrub"]
    mat_paver = mats["paver"]
    
    # 1. Extended Stairwell Enclosure to Roof (s.194(2))
    create_box("Roof_Stair_Roof_Slab", (12.69, 0.30, ROOF_SLAB_Z + 2.80), (2.25, 4.90, 0.20), col_name, mat_conc)
    create_box("Roof_Stair_Exit_Door", (12.75, 5.15, ROOF_SLAB_Z), (1.00, 0.10, 2.10), col_name, mat_steel)
    
    # 2. Lift Overrun Shaft (+19.80 m)
    create_box("Roof_Lift_Motor_Slab", (10.49, 0.30, ROOF_SLAB_Z + 3.60), (2.20, 2.20, 0.20), col_name, mat_conc)
    create_box("Roof_Lift_Louver_Vent", (10.45, 1.00, ROOF_SLAB_Z + 2.50), (0.10, 0.80, 0.80), col_name, mat_steel)

    # 3. Elevated Water Tanks on Steel Stand
    stand_base_z = ROOF_SLAB_Z
    tank_base_z = ROOF_SLAB_Z + 2.00
    create_cylinder("Roof_Tank_Leg_1", (1.20, 2.20, stand_base_z), 0.06, 2.00, col_name, mat_steel)
    create_cylinder("Roof_Tank_Leg_2", (3.00, 2.20, stand_base_z), 0.06, 2.00, col_name, mat_steel)
    create_cylinder("Roof_Tank_Leg_3", (1.20, 4.20, stand_base_z), 0.06, 2.00, col_name, mat_steel)
    create_cylinder("Roof_Tank_Leg_4", (3.00, 4.20, stand_base_z), 0.06, 2.00, col_name, mat_steel)
    create_box("Roof_Tank_Platform", (1.00, 2.00, tank_base_z - 0.10), (2.20, 2.40, 0.10), col_name, mat_steel)
    create_cylinder("Roof_Water_Tank_Domestic", (2.10, 2.60, tank_base_z), 0.70, 1.90, col_name, mat_steel)
    create_cylinder("Roof_Water_Tank_Rainwater", (2.10, 3.80, tank_base_z), 0.70, 1.90, col_name, mat_steel)

    # 4. Solar PV Array & Solar Water Heaters (x: 4.0 to 10.0, y: 0.5 to 5.0)
    for pv_idx in range(6):
        pv_x = 4.0 + (pv_idx % 3) * 1.8
        pv_y = 1.0 + (pv_idx // 3) * 2.2
        create_box(f"Roof_Solar_PV_{pv_idx+1}", (pv_x, pv_y, ROOF_SLAB_Z + 0.30), (1.60, 1.10, 0.06), col_name, mat_steel)
    create_box("Roof_SWH_Collector_1", (4.0, 3.8, ROOF_SLAB_Z + 0.35), (2.00, 1.20, 0.10), col_name, mat_steel)
    create_cylinder("Roof_SWH_Cylinder_1", (5.0, 3.7, ROOF_SLAB_Z + 0.90), 0.25, 1.80, col_name, mat_steel)
    create_box("Roof_SWH_Collector_2", (6.5, 3.8, ROOF_SLAB_Z + 0.35), (2.00, 1.20, 0.10), col_name, mat_steel)
    create_cylinder("Roof_SWH_Cylinder_2", (7.5, 3.7, ROOF_SLAB_Z + 0.90), 0.25, 1.80, col_name, mat_steel)

    # 5. Communal Roof Garden & Pergola (x: 0.5 to 6.0, y: 8.0 to 18.0)
    create_plane("Roof_Garden_Terrace_Floor", (0.30, 8.00, ROOF_SLAB_Z + 0.01), (6.00, 8.00, ROOF_SLAB_Z + 0.01), (6.00, 18.00, ROOF_SLAB_Z + 0.01), (0.30, 18.00, ROOF_SLAB_Z + 0.01), col_name, mat_paver)
    perg_base_z = ROOF_SLAB_Z
    perg_h = 2.60
    for px in [1.2, 5.2]:
        for py in [10.2, 13.0, 15.8]:
            create_box(f"Roof_Pergola_Post_x{px}_y{py}", (px - 0.08, py - 0.08, perg_base_z), (0.16, 0.16, perg_h), col_name, mat_wood)
    create_box("Roof_Pergola_Beam_1", (1.0, 10.1, perg_base_z + perg_h), (4.4, 0.15, 0.20), col_name, mat_wood)
    create_box("Roof_Pergola_Beam_2", (1.0, 15.7, perg_base_z + perg_h), (4.4, 0.15, 0.20), col_name, mat_wood)
    for ry in [10.5, 11.5, 12.5, 13.5, 14.5, 15.5]:
        create_box(f"Roof_Pergola_Rafter_{ry}", (0.8, ry, perg_base_z + perg_h + 0.15), (4.8, 0.08, 0.15), col_name, mat_wood)
    
    # Roof Planters and Benches
    create_box("Roof_Planter_Bed_1", (0.50, 8.20, ROOF_SLAB_Z), (5.20, 0.60, 0.50), col_name, mat_issb)
    create_box("Roof_Planter_Plants_1", (0.55, 8.25, ROOF_SLAB_Z + 0.50), (5.10, 0.50, 0.40), col_name, mat_shrub)
    create_box("Roof_Planter_Bed_2", (0.50, 17.20, ROOF_SLAB_Z), (5.20, 0.60, 0.50), col_name, mat_issb)
    create_box("Roof_Planter_Plants_2", (0.55, 17.25, ROOF_SLAB_Z + 0.50), (5.10, 0.50, 0.40), col_name, mat_shrub)
    create_box("Roof_Garden_Bench_1", (2.00, 12.00, ROOF_SLAB_Z), (2.00, 0.50, 0.45), col_name, mat_wood)

    # 6. Covered Laundry Drying Yard (x: 1.0 to 14.0, y: 24.0 to 29.5)
    create_box("Roof_Drying_Screen_Wall", (0.30, 24.00, ROOF_SLAB_Z), (14.64, 0.10, 2.00), col_name, mat_steel)
    create_box("Roof_Drying_Louvers", (1.00, 24.05, ROOF_SLAB_Z), (13.00, 0.05, 1.80), col_name, mat_wood)

    # 7. Drainage Gullies
    for g_pos in [(0.5, 7.5), (14.8, 7.5), (0.5, 23.5), (14.8, 23.5)]:
        gx, gy = g_pos
        create_box(f"Roof_Drain_Gully_{gx}_{gy}", (gx, gy, ROOF_SLAB_Z), (0.25, 0.25, 0.05), col_name, mat_steel)

    print("Stage 5 Roof Amenities build complete: Stair to roof, Lift overrun, Water tanks, PV, SWH, Pergola, Drying yard.")


def build_sun_shading(mats):
    """
    Stage 6: Materials & Sun Shading.
    - West street façade: Deep vertical timber sun fins (cutting afternoon sun).
    - Rear block West-facing courtyard façade: Vertical timber sun fins.
    - Left wing South-facing courtyard façade: 600 mm horizontal hoods over windows.
    - Core courtyard face: Perforated breeze-block screen panel.
    """
    col_name = "Structure"
    mat_wood = mats["wood"]
    mat_conc = mats["conc"]
    mat_issb = mats["issb"]

    # 1. West Street Façade Vertical Timber Sun Fins (y = 0.0, L1 to L4: z = 4.20 to 16.20)
    fin_x_positions = [
        0.8, 1.4, 2.0, 2.6, 3.2,
        3.8, 4.4, 5.0, 5.6, 6.2, 6.8,
        7.6, 8.2, 8.8, 9.4, 10.0
    ]
    fin_h = ROOF_SLAB_Z - L1_FFL
    for idx, fx in enumerate(fin_x_positions):
        create_box(f"SunFin_Street_West_{idx+1}", (fx - 0.03, -0.30, L1_FFL), (0.06, 0.30, fin_h), col_name, mat_wood)

    # 2. Rear Block Courtyard Façade Vertical Timber Fins (y = 23.00, L1 to L4)
    rear_fin_x = [6.8, 7.4, 8.0, 8.6, 9.2, 9.8, 10.4, 11.0]
    for idx, fx in enumerate(rear_fin_x):
        create_box(f"SunFin_RearCourtyard_{idx+1}", (fx - 0.03, 22.70, L1_FFL), (0.06, 0.30, fin_h), col_name, mat_wood)

    # 3. Left Wing South-Facing Courtyard Façade Horizontal Sun Hoods (x = 6.30, L1 to L4)
    for lvl_idx, lvl_z in enumerate([L1_FFL, L2_FFL, L3_FFL, L4_FFL]):
        create_box(f"SunHood_L{lvl_idx+1}_Living", (6.30, 8.00, lvl_z + 2.50), (0.60, 4.00, 0.12), col_name, mat_wood)
        create_box(f"SunHood_L{lvl_idx+1}_Bed2", (6.30, 14.00, lvl_z + 2.50), (0.60, 2.80, 0.12), col_name, mat_wood)
        create_box(f"SunHood_L{lvl_idx+1}_Master", (6.30, 18.50, lvl_z + 2.50), (0.60, 4.00, 0.12), col_name, mat_wood)

    # 4. Core Courtyard Face Breeze-Block Panel
    breeze_h = ROOF_SLAB_Z - GF_RAISE
    create_box("Core_Breeze_Block_Screen", (10.49, 5.15, GF_RAISE), (2.20, 0.15, breeze_h), col_name, mat_issb)
    for b_z in range(int(GF_RAISE), int(ROOF_SLAB_Z), 1):
        create_box(f"Core_Breeze_Band_{b_z}", (10.45, 5.12, float(b_z)), (2.28, 0.21, 0.06), col_name, mat_conc)

    print("Stage 6 Sun Shading build complete: West timber fins, Rear fins, South horizontal hoods, Breeze-blocks.")


def setup_lighting_and_cameras():
    """
    Stage 7: Lighting, Cameras, Render Setups & Walkthrough Camera Animation.
    - Nairobi Sun Position (-1.29 lat, 36.82 long, UTC+3, north = -X).
    - 8 Standard Architectural Cameras.
    - 30s pedestrian walkthrough + 10s car descent animations.
    """
    scene = bpy.context.scene
    col_annot = get_or_create_collection("Annotations")
    col_struct = get_or_create_collection("Structure")

    # 1. Environment & Sun Light (Nairobi afternoon equatorial lighting)
    sun_data = bpy.data.lights.new(name="Sun_Nairobi", type='SUN')
    sun_data.energy = 4.5
    sun_data.angle = math.radians(0.5)
    sun_data.color = (1.0, 0.96, 0.90)
    sun_obj = bpy.data.objects.new("Sun_Nairobi", sun_data)
    sun_obj.location = (7.62, -20.0, 25.0)
    sun_obj.rotation_euler = (math.radians(50.0), math.radians(15.0), math.radians(-20.0))
    col_struct.objects.link(sun_obj)

    fill_data = bpy.data.lights.new(name="Sky_Fill", type='SUN')
    fill_data.energy = 1.2
    fill_data.color = (0.75, 0.85, 1.0)
    fill_obj = bpy.data.objects.new("Sky_Fill", fill_data)
    fill_obj.location = (7.62, 15.0, 30.0)
    fill_obj.rotation_euler = (math.radians(10.0), math.radians(0.0), math.radians(180.0))
    col_struct.objects.link(fill_obj)

    # 2. 8 Cameras Setup
    cameras_config = [
        ("Camera_01_Street_View", (7.62, -18.0, 1.65), (7.62, 0.0, 8.0), 24, False, 0.0),
        ("Camera_02_Aerial_34", (-22.0, -18.0, 26.0), (7.62, 15.24, 7.0), 28, False, 0.0),
        ("Camera_03_Courtyard_Eye", (10.00, 8.00, GF_RAISE + 1.60), (9.85, 23.00, GF_RAISE + 1.60), 28, False, 0.0),
        ("Camera_04_L3_Gallery", (14.20, 9.00, L3_FFL + 1.60), (6.30, 16.00, GF_RAISE + 2.00), 24, False, 0.0),
        ("Camera_05_Roof_Garden", (3.00, 9.00, ROOF_SLAB_Z + 1.65), (9.85, 20.00, ROOF_SLAB_Z + 1.65), 28, False, 0.0),
        ("Camera_06_Section_Cutaway", (-26.00, 15.24, 8.00), (7.62, 15.24, 8.00), 24, False, 0.0),
        ("Camera_07_Floor_Plans", (7.62, 15.24, 40.00), (7.62, 15.24, 0.00), 50, True, 34.0),
        ("Camera_08_Long_Section", (7.62, -35.00, 8.00), (7.62, 15.24, 8.00), 50, True, 36.0),
    ]

    for cam_name, cam_loc, target_pt, focal, is_ortho, ortho_scale in cameras_config:
        cam_d = bpy.data.cameras.new(cam_name)
        if is_ortho:
            cam_d.type = 'ORTHO'
            cam_d.ortho_scale = ortho_scale
        else:
            cam_d.type = 'PERSP'
            cam_d.lens = focal
        cam_o = bpy.data.objects.new(cam_name, cam_d)
        cam_o.location = cam_loc
        t_vec = Vector(target_pt)
        cam_o.rotation_euler = (t_vec - Vector(cam_loc)).to_track_quat('-Z', 'Y').to_euler()
        col_struct.objects.link(cam_o)

    # Set active camera to Aerial 3/4
    scene.camera = bpy.data.objects.get("Camera_02_Aerial_34")

    # 3. Camera Walkthrough Path (30 s = 720 frames at 24 fps)
    walk_curve = bpy.data.curves.new("Walkthrough_Path_Data", type='CURVE')
    walk_curve.dimensions = '3D'
    spline_w = walk_curve.splines.new('BEZIER')
    walk_pts = [
        (6.48, -4.00, 1.60),
        (6.48, 1.50, 1.60),
        (6.48, 5.00, 1.90),
        (6.00, 8.00, GF_RAISE + 1.60),
        (6.00, 14.00, GF_RAISE + 1.60),
        (10.00, 7.50, GF_RAISE + 1.60),
        (13.80, 9.00, L2_FFL + 1.60),
        (13.80, 16.00, L2_FFL + 1.60),
        (3.00, 12.00, ROOF_SLAB_Z + 1.65)
    ]
    spline_w.bezier_points.add(len(walk_pts) - 1)
    for i, pt in enumerate(walk_pts):
        bp = spline_w.bezier_points[i]
        bp.co = pt
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
    walk_obj = bpy.data.objects.new("Walkthrough_Path", walk_curve)
    col_annot.objects.link(walk_obj)

    # 4. Car Ramp Descent Path (10 s = 240 frames at 24 fps)
    descent_curve = bpy.data.curves.new("Car_Descent_Path_Data", type='CURVE')
    descent_curve.dimensions = '3D'
    spline_d = descent_curve.splines.new('BEZIER')
    descent_pts = [
        (1.89, -3.00, 1.20),
        (1.89, 1.00, 1.35),
        (1.89, 6.00, 1.15),
        (1.89, 15.00, 0.00),
        (1.89, 23.00, BASEMENT_FFL + 1.20),
        (5.00, 24.50, BASEMENT_FFL + 1.20),
        (9.00, 22.00, BASEMENT_FFL + 1.20),
        (11.00, 14.00, BASEMENT_FFL + 1.20)
    ]
    spline_d.bezier_points.add(len(descent_pts) - 1)
    for i, pt in enumerate(descent_pts):
        bp = spline_d.bezier_points[i]
        bp.co = pt
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
    descent_obj = bpy.data.objects.new("Car_Descent_Path", descent_curve)
    col_annot.objects.link(descent_obj)

    # Animation Frame Settings
    scene.frame_start = 1
    scene.frame_end = 720
    scene.render.fps = 24
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100

    print("Stage 7 Lighting, 8 Cameras & Animation trajectories setup complete.")


build_scene()


