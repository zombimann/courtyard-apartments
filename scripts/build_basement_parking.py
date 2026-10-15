"""
Concept Design of One Basement Parking Level (50 ft x 100 ft Plot, Nairobi Kenya)
Compliant with Kenya National Building Code 2024 (LN 47/2024)

Architect-Engineer Parametric Generator Script for Blender
"""

import bpy
import bmesh
import math
from mathutils import Vector, Euler

# ==============================================================================
# 1. PARAMETRIC CONFIGURATION / VARIABLES
# ==============================================================================

# Site / Plot Dimensions (50 ft x 100 ft = 15.24 m x 30.48 m in Nairobi, Kenya)
PLOT_WIDTH_X = 15.24              # Plot width along road frontage (short edge at Y = 0)
PLOT_LENGTH_Y = 30.48             # Plot depth (long edge Y = 0 to 30.48 m)
GROUND_LEVEL_Z = 0.00             # Ground datum / top of podium slab
FLOOR_TO_FLOOR_H = 3.30           # Floor-to-floor height (m)
BASEMENT_FFL_Z = GROUND_LEVEL_Z - FLOOR_TO_FLOOR_H  # -3.30 m

# Structural Assumptions (Engineered for 4-5 Storeys Above)
RETAINING_WALL_THICKNESS = 0.30   # 300 mm reinforced concrete retaining wall
FOUNDATION_RAFT_THICKNESS = 0.30  # 300 mm RC raft foundation slab
GROUND_SLAB_THICKNESS = 0.25      # 250 mm RC podium slab
BEAM_WIDTH = 0.40                 # 400 mm RC beams
BEAM_DEPTH = 0.60                 # 600 mm deep beams (soffit at -0.60 m)
COLUMN_SIZE_X = 0.40              # 400 x 400 mm RC columns
COLUMN_SIZE_Y = 0.40
CLEAR_HEADROOM_TARGET = 2.40      # Minimum clear headroom under beams (m)
# Actual clear headroom under beams = 3.30 - 0.60 = 2.70 m >= 2.40 m PASS!

# Access Ramp Parameters (LN 47/2024 s.42a, s.44, s.41)
RAMP_LANE_WIDTH = 3.20            # One-way clear width (code s.44 min 3.0 m)
RAMP_BARRIER_WIDTH = 0.25         # Concrete kerb/barrier width (m)
RAMP_BARRIER_HEIGHT = 0.45        # 450 mm kerb/barrier (code s.41: 375 - 610 mm)
RAMP_APPROACH_LENGTH = 5.00       # 5.0 m road approach (s.42a: max 1:25)
RAMP_APPROACH_SLOPE = 0.040       # 1:25 (4.0%)
RAMP_TRANSITION_LEN = 2.50        # Transition length top & bottom (2-3 m)
RAMP_SLAB_THICKNESS = 0.25        # 250 mm RC ramp slab

# Parking Bays Parameters (LN 47/2024 Second Schedule Fig. 1c, s.353, s.38)
BAY_DEPTH = 5.00                  # 5.0 m deep bays (code min 4.6 m)
BAY_WIDTH_STD = 2.50              # 2.5 m wide standard bays (code min 2.4 m)
BAY_WIDTH_ACC = 3.60              # 3.6 m accessible bay incl. transfer zone (KS ISO 21542)
AISLE_WIDTH = 6.10                # 6.1 m clear aisle width (LN 47/2024 Fig. 1c)
COLUMN_SETBACK_AISLE = 0.60       # Setback of columns from aisle edge (0.6 m for door swing)

# Vertical Escape Core & Circulation (s.400, s.201)
CORE_WIDTH_X = 4.45               # Stair & lift core width
CORE_LENGTH_Y = 5.00              # Core depth at front right
LIFT_SHAFT_X = 2.00               # 2.0 x 2.0 m internal lift shaft
LIFT_SHAFT_Y = 2.00
STAIR_FLIGHT_WIDTH = 1.20         # Min 1.2 m flight width (s.400)
PEDESTRIAN_WALKWAY_WIDTH = 1.20   # 1.2 m painted/kerbed walkway (s.201)

# Services & Drainage Parameters (s.156)
VENT_SHAFT_SIZE = 0.80            # 0.8 x 0.8 m mechanical extract shafts (x2)
SUMP_PIT_SIZE = 1.00              # 1.0 x 1.0 m sump pit
SUMP_PIT_DEPTH = 1.20             # 1.2 m depth below basement floor
FLOOR_FALL_RATIO = 0.010          # 1:100 floor fall towards sump

# Placeholder Vehicle Dimensions
CAR_LENGTH = 4.50
CAR_WIDTH = 1.80
CAR_HEIGHT = 1.50

# ==============================================================================
# 2. HELPER FUNCTIONS: COLLECTIONS, MATERIALS, MESHES, TEXT
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

def get_or_create_material(name, color, roughness=0.6, metallic=0.0):
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    mat.diffuse_color = color
    principled = next((n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if principled:
        for inp in principled.inputs:
            if inp.name == "Base Color":
                inp.default_value = color
            elif inp.name == "Roughness":
                inp.default_value = roughness
            elif inp.name == "Metallic":
                inp.default_value = metallic
    return mat

def create_box(name, min_corner, size, col_name, mat=None):
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
    obj.location = min_corner
    if mat:
        obj.data.materials.append(mat)
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
    if mat:
        obj.data.materials.append(mat)
    col = get_or_create_collection(col_name)
    col.objects.link(obj)
    return obj

def create_3d_text(name, text_str, loc, size=0.35, rot=(0,0,0), col_name="Parking", mat=None):
    curve = bpy.data.curves.new(name=name, type='FONT')
    curve.body = text_str
    curve.size = size
    curve.extrude = 0.02
    curve.align_x = 'CENTER'
    curve.align_y = 'CENTER'
    
    obj = bpy.data.objects.new(name, curve)
    obj.location = loc
    obj.rotation_euler = rot
    if mat:
        obj.data.materials.append(mat)
    col = get_or_create_collection(col_name)
    col.objects.link(obj)
    return obj

def create_cylinder(name, loc, radius, depth, rot=(0,0,0), col_name="Basement_Structure", mat=None):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=radius, radius2=radius, depth=depth)
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    obj.rotation_euler = rot
    if mat:
        obj.data.materials.append(mat)
    col = get_or_create_collection(col_name)
    col.objects.link(obj)
    return obj

# ==============================================================================
# 3. BUILD COMPLETE CONCEPT DESIGN
# ==============================================================================

def build_entire_model():
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.length_unit = 'METERS'
    scene.unit_settings.scale_length = 1.0

    # Clean all existing objects and collections
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

    # Architectural Materials
    mat_conc_struct = get_or_create_material("Mat_Concrete_Structure", (0.58, 0.60, 0.62, 1.0), roughness=0.65)
    mat_conc_floor  = get_or_create_material("Mat_Concrete_Floor", (0.28, 0.30, 0.32, 1.0), roughness=0.45)
    mat_ramp_groove = get_or_create_material("Mat_Ramp_Grooved", (0.38, 0.40, 0.42, 1.0), roughness=0.85)
    mat_barrier_ylw = get_or_create_material("Mat_Barrier_SafetyYellow", (0.95, 0.78, 0.08, 1.0), roughness=0.35)
    mat_white_line  = get_or_create_material("Mat_Line_White", (0.98, 0.98, 0.98, 1.0), roughness=0.15)
    mat_yellow_line = get_or_create_material("Mat_Line_Yellow", (0.95, 0.85, 0.10, 1.0), roughness=0.15)
    mat_bay_blue    = get_or_create_material("Mat_Bay_Accessible_Blue", (0.05, 0.35, 0.80, 1.0), roughness=0.30)
    mat_bay_green   = get_or_create_material("Mat_Bay_EV_Green", (0.10, 0.70, 0.30, 1.0), roughness=0.30)
    mat_walkway     = get_or_create_material("Mat_Pedestrian_Walkway", (0.12, 0.60, 0.38, 1.0), roughness=0.40)
    mat_podium      = get_or_create_material("Mat_Podium_Slab", (0.76, 0.78, 0.80, 1.0), roughness=0.50)
    mat_grid_bubble = get_or_create_material("Mat_Grid_Bubble", (0.85, 0.15, 0.15, 1.0), roughness=0.25)
    mat_text_white  = get_or_create_material("Mat_Text_White", (0.98, 0.98, 0.98, 1.0), roughness=0.10)
    mat_drain_grate = get_or_create_material("Mat_Drainage_Grating", (0.15, 0.15, 0.16, 1.0), roughness=0.30, metallic=0.8)

    # Ground Utility materials
    mat_water_tank  = get_or_create_material("Mat_Util_WaterTank", (0.10, 0.45, 0.85, 1.0), roughness=0.30)
    mat_generator   = get_or_create_material("Mat_Util_Generator", (0.88, 0.72, 0.12, 1.0), roughness=0.40)
    mat_kplc_trans  = get_or_create_material("Mat_Util_Transformer", (0.92, 0.42, 0.08, 1.0), roughness=0.35)
    mat_refuse      = get_or_create_material("Mat_Util_Refuse", (0.28, 0.28, 0.30, 1.0), roughness=0.60)
    mat_septic      = get_or_create_material("Mat_Util_Septic", (0.15, 0.52, 0.48, 1.0), roughness=0.50)

    # Automotive colors
    car_colors = [
        ("Mat_Car_Accessible", (0.18, 0.35, 0.70, 1.0), 0.8),
        ("Mat_Car_EV",         (0.05, 0.75, 0.70, 1.0), 0.8),
        ("Mat_Car_White",      (0.92, 0.92, 0.92, 1.0), 0.3),
        ("Mat_Car_Crimson",    (0.75, 0.10, 0.12, 1.0), 0.7),
        ("Mat_Car_Graphite",   (0.25, 0.26, 0.28, 1.0), 0.8),
        ("Mat_Car_Navy",       (0.08, 0.15, 0.32, 1.0), 0.8),
        ("Mat_Car_Silver",     (0.72, 0.74, 0.76, 1.0), 0.9),
        ("Mat_Car_Charcoal",   (0.18, 0.18, 0.20, 1.0), 0.7),
    ]
    mat_cars = [get_or_create_material(c[0], c[1], roughness=0.25, metallic=c[2]) for c in car_colors]

    # --------------------------------------------------------------------------
    # A. COLLECTION: Basement_Structure
    # --------------------------------------------------------------------------
    col_struct = "Basement_Structure"

    # Raft Foundation Slab
    create_box("Slab_Basement_Raft", 
               (0.0, 0.0, BASEMENT_FFL_Z - FOUNDATION_RAFT_THICKNESS), 
               (PLOT_WIDTH_X, PLOT_LENGTH_Y, FOUNDATION_RAFT_THICKNESS), 
               col_struct, mat_conc_struct)

    # Basement Floor Finish (Dark high-contrast industrial concrete)
    create_box("Floor_Basement_Slab",
               (RETAINING_WALL_THICKNESS, RETAINING_WALL_THICKNESS, BASEMENT_FFL_Z),
               (PLOT_WIDTH_X - 2*RETAINING_WALL_THICKNESS, PLOT_LENGTH_Y - 2*RETAINING_WALL_THICKNESS, 0.02),
               col_struct, mat_conc_floor)

    # Perimeter Retaining Walls (300 mm RC)
    create_box("Wall_Retaining_Left",
               (0.0, 0.0, BASEMENT_FFL_Z),
               (RETAINING_WALL_THICKNESS, PLOT_LENGTH_Y, FLOOR_TO_FLOOR_H),
               col_struct, mat_conc_struct)
    create_box("Wall_Retaining_Right",
               (PLOT_WIDTH_X - RETAINING_WALL_THICKNESS, 0.0, BASEMENT_FFL_Z),
               (RETAINING_WALL_THICKNESS, PLOT_LENGTH_Y, FLOOR_TO_FLOOR_H),
               col_struct, mat_conc_struct)
    create_box("Wall_Retaining_Rear",
               (0.0, PLOT_LENGTH_Y - RETAINING_WALL_THICKNESS, BASEMENT_FFL_Z),
               (PLOT_WIDTH_X, RETAINING_WALL_THICKNESS, FLOOR_TO_FLOOR_H),
               col_struct, mat_conc_struct)
    create_box("Wall_Retaining_Front",
               (3.75, 0.0, BASEMENT_FFL_Z),
               (PLOT_WIDTH_X - 3.75, RETAINING_WALL_THICKNESS, FLOOR_TO_FLOOR_H),
               col_struct, mat_conc_struct)

    # Structural Grid Definitions:
    grid_x = {'A': 0.15, 'B': 3.65, 'C': 10.45, 'D': 15.09}
    grid_y = {'1': 0.15, '2': 5.30, '3': 13.90, '4': 21.40, '5': 30.33}

    # RC Columns (400 x 400 mm RC)
    col_positions = [
        ('B', '1'), ('B', '2'), ('B', '3'), ('B', '4'), ('B', '5'),
        ('C', '2'), ('C', '3'), ('C', '4'), ('C', '5'),
        ('A', '1'), ('A', '2'), ('A', '3'), ('A', '4'), ('A', '5'),
        ('D', '1'), ('D', '2'), ('D', '3'), ('D', '4'), ('D', '5'),
    ]

    for gx, gy in col_positions:
        x_pos = grid_x[gx] - COLUMN_SIZE_X / 2.0
        y_pos = grid_y[gy] - COLUMN_SIZE_Y / 2.0
        create_box(f"Column_{gx}_{gy}",
                   (x_pos, y_pos, BASEMENT_FFL_Z),
                   (COLUMN_SIZE_X, COLUMN_SIZE_Y, FLOOR_TO_FLOOR_H),
                   col_struct, mat_conc_struct)

    # RC Beams (400 mm wide x 600 mm deep, top at Z = 0, soffit at Z = -0.60)
    for gy_name, gy_val in grid_y.items():
        create_box(f"Beam_Transverse_Grid_{gy_name}",
                   (0.0, gy_val - BEAM_WIDTH/2.0, GROUND_LEVEL_Z - BEAM_DEPTH),
                   (PLOT_WIDTH_X, BEAM_WIDTH, BEAM_DEPTH),
                   col_struct, mat_conc_struct)

    for gx_name, gx_val in grid_x.items():
        create_box(f"Beam_Longitudinal_Grid_{gx_name}",
                   (gx_val - BEAM_WIDTH/2.0, 0.0, GROUND_LEVEL_Z - BEAM_DEPTH),
                   (BEAM_WIDTH, PLOT_LENGTH_Y, BEAM_DEPTH),
                   col_struct, mat_conc_struct)

    # Structural Grid Lines & Bubbles
    for gx_name, gx_val in grid_x.items():
        create_cylinder(f"GridLine_X_{gx_name}", (gx_val, PLOT_LENGTH_Y/2.0, 0.1), 0.03, PLOT_LENGTH_Y, 
                        rot=(math.pi/2, 0, 0), col_name=col_struct, mat=mat_grid_bubble)
        create_cylinder(f"GridBubble_{gx_name}", (gx_val, -1.2, 0.1), 0.45, 0.08, col_name=col_struct, mat=mat_grid_bubble)
        create_3d_text(f"GridText_{gx_name}", gx_name, (gx_val, -1.2, 0.16), size=0.45, col_name=col_struct, mat=mat_text_white)

    for gy_name, gy_val in grid_y.items():
        create_cylinder(f"GridLine_Y_{gy_name}", (PLOT_WIDTH_X/2.0, gy_val, 0.1), 0.03, PLOT_WIDTH_X,
                        rot=(0, math.pi/2, 0), col_name=col_struct, mat=mat_grid_bubble)
        create_cylinder(f"GridBubble_{gy_name}", (-1.2, gy_val, 0.1), 0.45, 0.08, col_name=col_struct, mat=mat_grid_bubble)
        create_3d_text(f"GridText_{gy_name}", gy_name, (-1.2, gy_val, 0.16), size=0.45, col_name=col_struct, mat=mat_text_white)

    # --------------------------------------------------------------------------
    # B. COLLECTION: Ramp
    # --------------------------------------------------------------------------
    col_ramp = "Ramp"
    
    ramp_y_pts = [0.00, 5.00, 7.50, 27.50, 29.80]
    ramp_z_pts = [0.00, -0.20, -0.36, -2.86, BASEMENT_FFL_Z]
    rx1, rx2 = RETAINING_WALL_THICKNESS, 3.50
    
    for i in range(len(ramp_y_pts) - 1):
        y_a, y_b = ramp_y_pts[i], ramp_y_pts[i+1]
        z_a, z_b = ramp_z_pts[i], ramp_z_pts[i+1]
        
        mesh_r = bpy.data.meshes.new(f"Ramp_Slab_Segment_{i+1}")
        bm_r = bmesh.new()
        v1 = bm_r.verts.new((rx1, y_a, z_a))
        v2 = bm_r.verts.new((rx2, y_a, z_a))
        v3 = bm_r.verts.new((rx2, y_b, z_b))
        v4 = bm_r.verts.new((rx1, y_b, z_b))
        v5 = bm_r.verts.new((rx1, y_a, z_a - RAMP_SLAB_THICKNESS))
        v6 = bm_r.verts.new((rx2, y_a, z_a - RAMP_SLAB_THICKNESS))
        v7 = bm_r.verts.new((rx2, y_b, z_b - RAMP_SLAB_THICKNESS))
        v8 = bm_r.verts.new((rx1, y_b, z_b - RAMP_SLAB_THICKNESS))
        bm_r.faces.new((v1, v2, v3, v4))
        bm_r.faces.new((v8, v7, v6, v5))
        bm_r.faces.new((v1, v4, v8, v5))
        bm_r.faces.new((v2, v6, v7, v3))
        bm_r.faces.new((v1, v5, v6, v2))
        bm_r.faces.new((v4, v3, v7, v8))
        bm_r.to_mesh(mesh_r)
        bm_r.free()
        
        obj_r = bpy.data.objects.new(f"Ramp_Slab_Segment_{i+1}", mesh_r)
        obj_r.data.materials.append(mat_ramp_groove)
        get_or_create_collection(col_ramp).objects.link(obj_r)

    # Vehicle Barrier / Kerb (s.41: 375 - 610 mm high)
    mesh_b = bpy.data.meshes.new("Ramp_Vehicle_Barrier")
    bm_b = bmesh.new()
    for i in range(len(ramp_y_pts) - 1):
        y_a, y_b = ramp_y_pts[i], ramp_y_pts[i+1]
        z_a, z_b = ramp_z_pts[i], ramp_z_pts[i+1]
        top_za = z_a + RAMP_BARRIER_HEIGHT
        top_zb = z_b + RAMP_BARRIER_HEIGHT
        bot_z = BASEMENT_FFL_Z
        bx1, bx2 = 3.50, 3.75
        v1 = bm_b.verts.new((bx1, y_a, top_za))
        v2 = bm_b.verts.new((bx2, y_a, top_za))
        v3 = bm_b.verts.new((bx2, y_b, top_zb))
        v4 = bm_b.verts.new((bx1, y_b, top_zb))
        v5 = bm_b.verts.new((bx1, y_a, bot_z))
        v6 = bm_b.verts.new((bx2, y_a, bot_z))
        v7 = bm_b.verts.new((bx2, y_b, bot_z))
        v8 = bm_b.verts.new((bx1, y_b, bot_z))
        bm_b.faces.new((v1, v2, v3, v4))
        bm_b.faces.new((v8, v7, v6, v5))
        bm_b.faces.new((v1, v4, v8, v5))
        bm_b.faces.new((v2, v6, v7, v3))
        bm_b.faces.new((v1, v5, v6, v2))
        bm_b.faces.new((v4, v3, v7, v8))
    bm_b.to_mesh(mesh_b)
    bm_b.free()
    
    obj_b = bpy.data.objects.new("Ramp_Vehicle_Barrier", mesh_b)
    obj_b.data.materials.append(mat_barrier_ylw)
    get_or_create_collection(col_ramp).objects.link(obj_b)

    # Ramp Markings
    create_3d_text("Ramp_Text_Entry", "VEHICLE RAMP ENTRY (1:25 APPROACH)", (1.90, 2.50, 0.05), size=0.25, rot=(0,0,0), col_name=col_ramp, mat=mat_white_line)
    create_3d_text("Ramp_Text_MaxSlope", "MAIN DESCENT (12.5% / 1:8 MAX SLOPE)", (1.90, 15.0, -1.55), size=0.25, rot=(0.125, 0, 0), col_name=col_ramp, mat=mat_white_line)

    # --------------------------------------------------------------------------
    # C. COLLECTION: Core (Stair, Lift, Walkway)
    # --------------------------------------------------------------------------
    col_core = "Core"
    core_x_min, core_x_max = 10.40, PLOT_WIDTH_X - RETAINING_WALL_THICKNESS
    core_y_min, core_y_max = RETAINING_WALL_THICKNESS, 5.30

    # Lift Shaft Enclosure
    create_box("Lift_Shaft_Enclosure",
               (10.40, 0.30, BASEMENT_FFL_Z),
               (2.20, 2.20, FLOOR_TO_FLOOR_H + 1.20),
               col_core, mat_conc_struct)
    create_box("Lift_Basement_Doors",
               (10.60, 2.51, BASEMENT_FFL_Z),
               (1.20, 0.05, 2.10),
               col_core, mat_drain_grate)
    create_3d_text("Lift_Text_Sign", "PASSENGER LIFT (2.0 x 2.0 m)", (11.20, 2.65, BASEMENT_FFL_Z + 2.30), size=0.20, col_name=col_core, mat=mat_text_white)

    # Enclosed Escape Staircase
    create_box("Stair_Enclosure_Walls",
               (12.60, 0.30, BASEMENT_FFL_Z),
               (core_x_max - 12.60, 5.00, FLOOR_TO_FLOOR_H + 1.20),
               col_core, mat_conc_struct)
    
    num_steps_1 = 10
    step_rise = 1.65 / num_steps_1
    step_tread = 2.50 / num_steps_1
    for s in range(num_steps_1):
        create_box(f"Stair_Flight1_Step_{s+1}",
                   (12.70, 5.00 - (s+1)*step_tread, BASEMENT_FFL_Z + s*step_rise),
                   (STAIR_FLIGHT_WIDTH, step_tread, step_rise),
                   col_core, mat_conc_floor)
        
    create_box("Stair_Intermediate_Landing",
               (12.70, 0.40, BASEMENT_FFL_Z + 1.65),
               (2.10, 1.40, 0.20),
               col_core, mat_conc_struct)

    for s in range(num_steps_1):
        create_box(f"Stair_Flight2_Step_{s+1}",
                   (13.95, 1.80 + s*step_tread, BASEMENT_FFL_Z + 1.65 + s*step_rise),
                   (STAIR_FLIGHT_WIDTH, step_tread, step_rise),
                   col_core, mat_conc_floor)

    create_box("Stair_Fire_Exit_Door",
               (12.80, 5.25, BASEMENT_FFL_Z),
               (1.10, 0.08, 2.10),
               col_core, mat_barrier_ylw)
    create_3d_text("Stair_Door_Sign", "ESCAPE STAIR (MIN 1.2m FLIGHTS)", (13.35, 5.40, BASEMENT_FFL_Z + 2.30), size=0.20, col_name=col_core, mat=mat_text_white)

    # Pedestrian Walkway (s.201: 1.2 m painted/kerbed walkway)
    create_plane("Pedestrian_Walkway_Surface",
                 (9.85, 5.30, BASEMENT_FFL_Z + 0.01),
                 (11.05, 5.30, BASEMENT_FFL_Z + 0.01),
                 (11.05, 8.90, BASEMENT_FFL_Z + 0.01),
                 (9.85, 8.90, BASEMENT_FFL_Z + 0.01),
                 col_core, mat_walkway)
    create_3d_text("Pedestrian_Walkway_Text", "PEDESTRIAN ROUTE (1.2m PROTECTED - s.201)", 
                   (10.45, 7.10, BASEMENT_FFL_Z + 0.02), size=0.18, rot=(0,0,math.pi/2), col_name=col_core, mat=mat_white_line)

    # --------------------------------------------------------------------------
    # D. COLLECTION: Parking (Option A: 8 Bays, Accessible, EV, Cars)
    # --------------------------------------------------------------------------
    col_parking = "Parking"
    bay_x_start = 9.85
    bay_x_end = 14.85
    
    bays_config = [
        ("Bay_01_Accessible", 5.30, 8.90,  "ACCESSIBLE", mat_bay_blue,  "BAY 1 (ACCESSIBLE 3.6m)"),
        ("Bay_02_EV",         8.90, 11.40, "EV",         mat_bay_green, "BAY 2 (EV CHARGING)"),
        ("Bay_03_Standard",   11.40, 13.90, "STD",        mat_conc_floor,"BAY 3"),
        ("Bay_04_Standard",   13.90, 16.40, "STD",        mat_conc_floor,"BAY 4"),
        ("Bay_05_Standard",   16.40, 18.90, "STD",        mat_conc_floor,"BAY 5"),
        ("Bay_06_Standard",   18.90, 21.40, "STD",        mat_conc_floor,"BAY 6"),
        ("Bay_07_Standard",   21.40, 23.90, "STD",        mat_conc_floor,"BAY 7"),
        ("Bay_08_Standard",   23.90, 26.40, "STD",        mat_conc_floor,"BAY 8"),
    ]

    for idx, (b_name, by1, by2, b_type, b_mat, b_lbl) in enumerate(bays_config):
        # Bay Floor Surface
        create_plane(f"{b_name}_Floor",
                     (bay_x_start, by1, BASEMENT_FFL_Z + 0.005),
                     (bay_x_end, by1, BASEMENT_FFL_Z + 0.005),
                     (bay_x_end, by2, BASEMENT_FFL_Z + 0.005),
                     (bay_x_start, by2, BASEMENT_FFL_Z + 0.005),
                     col_parking, b_mat)

        # White Boundary Lines (100 mm wide)
        create_plane(f"{b_name}_Line_Front",
                     (bay_x_start, by1, BASEMENT_FFL_Z + 0.008),
                     (bay_x_end, by1, BASEMENT_FFL_Z + 0.008),
                     (bay_x_end, by1 + 0.10, BASEMENT_FFL_Z + 0.008),
                     (bay_x_start, by1 + 0.10, BASEMENT_FFL_Z + 0.008),
                     col_parking, mat_white_line)
        create_plane(f"{b_name}_Line_Back",
                     (bay_x_start, by2 - 0.10, BASEMENT_FFL_Z + 0.008),
                     (bay_x_end, by2 - 0.10, BASEMENT_FFL_Z + 0.008),
                     (bay_x_end, by2, BASEMENT_FFL_Z + 0.008),
                     (bay_x_start, by2, BASEMENT_FFL_Z + 0.008),
                     col_parking, mat_white_line)

        # 3D Text Label in Bay
        create_3d_text(f"{b_name}_Text", b_lbl, 
                       (bay_x_start + 1.20, (by1 + by2)/2.0, BASEMENT_FFL_Z + 0.015), 
                       size=0.22, rot=(0,0,math.pi/2), col_name=col_parking, mat=mat_text_white)

        # Concrete Wheel Stop
        create_box(f"{b_name}_WheelStop",
                   (bay_x_end - 0.80, (by1 + by2)/2.0 - 0.90, BASEMENT_FFL_Z + 0.01),
                   (0.15, 1.80, 0.12),
                   col_parking, mat_conc_struct)

        # Placeholder Car Model (4.5 x 1.8 x 1.5 m)
        car_cx = (bay_x_start + bay_x_end) / 2.0
        car_cy = (by1 + by2) / 2.0
        create_box(f"Car_{idx+1}_Chassis",
                   (car_cx - CAR_LENGTH/2.0, car_cy - CAR_WIDTH/2.0, BASEMENT_FFL_Z + 0.15),
                   (CAR_LENGTH, CAR_WIDTH, 0.70),
                   col_parking, mat_cars[idx])
        create_box(f"Car_{idx+1}_Cabin",
                   (car_cx - 1.20, car_cy - 0.75, BASEMENT_FFL_Z + 0.85),
                   (2.50, 1.50, 0.65),
                   col_parking, mat_cars[idx])

    # Accessible Transfer Zone Hatched Area
    create_plane("Accessible_Transfer_Zone",
                 (bay_x_start, 5.30, BASEMENT_FFL_Z + 0.007),
                 (bay_x_start + 1.20, 5.30, BASEMENT_FFL_Z + 0.007),
                 (bay_x_start + 1.20, 8.90, BASEMENT_FFL_Z + 0.007),
                 (bay_x_start, 8.90, BASEMENT_FFL_Z + 0.007),
                 col_parking, mat_yellow_line)
    create_3d_text("Accessible_Symbol_Text", "ACCESSIBLE TRANSFER ZONE (1.2m)", 
                   (bay_x_start + 0.60, 7.10, BASEMENT_FFL_Z + 0.016), size=0.20, rot=(0,0,math.pi/2), col_name=col_parking, mat=mat_white_line)

    # EV Charger Wall Unit
    create_box("EV_Charger_Unit",
               (PLOT_WIDTH_X - RETAINING_WALL_THICKNESS - 0.25, 10.15 - 0.30, BASEMENT_FFL_Z + 1.10),
               (0.20, 0.60, 0.80),
               col_parking, mat_bay_green)
    create_3d_text("EV_Charger_Sign", "EV CHARGING STATION (s.38)", 
                   (PLOT_WIDTH_X - RETAINING_WALL_THICKNESS - 0.26, 10.15, BASEMENT_FFL_Z + 2.05), size=0.18, rot=(0,0,math.pi), col_name=col_parking, mat=mat_text_white)

    # Driving Aisle Markings (6.1 m clear aisle)
    create_3d_text("Aisle_Dimension_Text", "CLEAR AISLE 6.10 m (LN 47/2024 FIG. 1c)", 
                   (6.80, 15.00, BASEMENT_FFL_Z + 0.02), size=0.30, rot=(0,0,math.pi/2), col_name=col_parking, mat=mat_white_line)
    create_3d_text("Aisle_Arrow_Front", "^ ONE-WAY AISLE CIRCULATION ^", 
                   (6.80, 22.00, BASEMENT_FFL_Z + 0.02), size=0.28, rot=(0,0,-math.pi/2), col_name=col_parking, mat=mat_yellow_line)

    # Rear Turning Court & Hammerhead
    create_plane("Turning_Court_Area",
                 (RETAINING_WALL_THICKNESS, 26.40, BASEMENT_FFL_Z + 0.005),
                 (PLOT_WIDTH_X - RETAINING_WALL_THICKNESS, 26.40, BASEMENT_FFL_Z + 0.005),
                 (PLOT_WIDTH_X - RETAINING_WALL_THICKNESS, PLOT_LENGTH_Y - RETAINING_WALL_THICKNESS, BASEMENT_FFL_Z + 0.005),
                 (RETAINING_WALL_THICKNESS, PLOT_LENGTH_Y - RETAINING_WALL_THICKNESS, BASEMENT_FFL_Z + 0.005),
                 col_parking, mat_conc_floor)
    create_3d_text("Turning_Court_Text", "REAR TURNING AREA & HAMMERHEAD MANEUVERING COURT", 
                   (7.50, 28.20, BASEMENT_FFL_Z + 0.02), size=0.28, col_name=col_parking, mat=mat_yellow_line)

    # --------------------------------------------------------------------------
    # E. COLLECTION: Services (Vent Shafts, Sump Pit, Ground Utility Zones)
    # --------------------------------------------------------------------------
    col_services = "Services"

    # Ventilation Shaft 1 (Ramp queue 10 ACH extract)
    create_box("Vent_Shaft_01_RampQueue",
               (0.40, 5.20, BASEMENT_FFL_Z),
               (VENT_SHAFT_SIZE, VENT_SHAFT_SIZE, FLOOR_TO_FLOOR_H + 1.20),
               col_services, mat_conc_struct)
    create_3d_text("Vent_Shaft_01_Label", "VENT SHAFT 1 (RAMP QUEUE - 10 ACH)", 
                   (0.80, 5.60, 1.30), size=0.20, col_name=col_services, mat=mat_text_white)

    # Ventilation Shaft 2 (Rear basement 6 ACH extract)
    create_box("Vent_Shaft_02_RearExtract",
               (0.40, 28.50, BASEMENT_FFL_Z),
               (VENT_SHAFT_SIZE, VENT_SHAFT_SIZE, FLOOR_TO_FLOOR_H + 1.20),
               col_services, mat_conc_struct)
    create_3d_text("Vent_Shaft_02_Label", "VENT SHAFT 2 (BASEMENT EXTRACT - 6 ACH)", 
                   (0.80, 28.90, 1.30), size=0.20, col_name=col_services, mat=mat_text_white)

    # Drainage Sump Pit
    create_box("Drainage_Sump_Pit",
               (4.20, 28.50, BASEMENT_FFL_Z - SUMP_PIT_DEPTH),
               (SUMP_PIT_SIZE, SUMP_PIT_SIZE, SUMP_PIT_DEPTH),
               col_services, mat_conc_struct)
    create_box("Sump_Pit_Cover_Grating",
               (4.20, 28.50, BASEMENT_FFL_Z),
               (SUMP_PIT_SIZE, SUMP_PIT_SIZE, 0.04),
               col_services, mat_drain_grate)
    create_box("Sump_Pump_Unit",
               (4.50, 28.80, BASEMENT_FFL_Z - SUMP_PIT_DEPTH + 0.10),
               (0.40, 0.40, 0.60),
               col_services, mat_generator)
    create_3d_text("Sump_Pit_Label", "SUMP PIT 1.0x1.0x1.2m (FLOOR FALL 1:100)", 
                   (4.70, 28.20, BASEMENT_FFL_Z + 0.05), size=0.20, col_name=col_services, mat=mat_white_line)

    # Ground Level Utility Zones (Modelled as labelled boxes on ground slab)
    create_box("Util_Water_Tank",
               (4.20, 1.00, GROUND_LEVEL_Z),
               (4.00, 2.80, 2.20),
               col_services, mat_water_tank)
    create_3d_text("Util_Water_Tank_Label", "WATER TANK - 24,000 L\n(POTABLE & FIRE RESERVE)", 
                   (6.20, 2.40, 2.30), size=0.24, col_name=col_services, mat=mat_text_white)

    create_box("Util_Standby_Generator",
               (4.20, 5.20, GROUND_LEVEL_Z),
               (3.20, 1.80, 2.00),
               col_services, mat_generator)
    create_3d_text("Util_Generator_Label", "STANDBY GENERATOR - 150 kVA\n(SOUNDPROOF ENCLOSURE)", 
                   (5.80, 6.10, 2.10), size=0.22, col_name=col_services, mat=mat_text_white)

    create_box("Util_KPLC_Substation",
               (4.20, 8.50, GROUND_LEVEL_Z),
               (3.20, 2.40, 2.20),
               col_services, mat_kplc_trans)
    create_3d_text("Util_KPLC_Label", "KPLC TRANSFORMER & METER ROOM\n(DIRECT ROAD ACCESS)", 
                   (5.80, 9.70, 2.30), size=0.22, col_name=col_services, mat=mat_text_white)

    create_box("Util_Refuse_Chamber",
               (4.20, 12.50, GROUND_LEVEL_Z),
               (2.60, 2.00, 2.00),
               col_services, mat_refuse)
    create_3d_text("Util_Refuse_Label", "REFUSE & RECYCLING CHAMBER", 
                   (5.50, 13.50, 2.10), size=0.22, col_name=col_services, mat=mat_text_white)

    create_box("Util_Septic_Biodigester",
               (4.20, 16.00, GROUND_LEVEL_Z),
               (3.50, 2.40, 1.50),
               col_services, mat_septic)
    create_3d_text("Util_Septic_Label", "BIODIGESTER & SOAK PIT ZONE", 
                   (5.95, 17.20, 1.60), size=0.22, col_name=col_services, mat=mat_text_white)

    # --------------------------------------------------------------------------
    # F. COLLECTION: Ground_Level (Podium Slab with Open Ramp Cutout)
    # --------------------------------------------------------------------------
    col_ground = "Ground_Level"
    
    create_box("Podium_Slab_Main",
               (3.80, 5.30, GROUND_LEVEL_Z - GROUND_SLAB_THICKNESS),
               (PLOT_WIDTH_X - 3.80, PLOT_LENGTH_Y - 5.30, GROUND_SLAB_THICKNESS),
               col_ground, mat_podium)
    create_box("Podium_Slab_Front_Utilities",
               (3.80, 0.0, GROUND_LEVEL_Z - GROUND_SLAB_THICKNESS),
               (10.40 - 3.80, 5.30, GROUND_SLAB_THICKNESS),
               col_ground, mat_podium)
    create_box("Podium_Slab_Rear_Corner",
               (0.0, 27.50, GROUND_LEVEL_Z - GROUND_SLAB_THICKNESS),
               (3.80, PLOT_LENGTH_Y - 27.50, GROUND_SLAB_THICKNESS),
               col_ground, mat_podium)

    create_3d_text("Podium_Slab_Label", "GROUND LEVEL PODIUM SLAB (FREE FOR UTILITIES & BUILDING FOYER)",
                   (9.50, 20.00, 0.05), size=0.35, rot=(0,0,math.pi/2), col_name=col_ground, mat=mat_white_line)

    # --------------------------------------------------------------------------
    # G. CAMERAS & LIGHTING FOR ARCHITECTURAL PRESENTATION
    # --------------------------------------------------------------------------
    col_view = "Basement_Structure"
    
    # 1. Orthographic Top View Camera
    cam_top_data = bpy.data.cameras.new("Camera_Top")
    cam_top_data.type = 'ORTHO'
    cam_top_data.ortho_scale = 34.0
    cam_top_obj = bpy.data.objects.new("Camera_Top", cam_top_data)
    cam_top_obj.location = (PLOT_WIDTH_X / 2.0, PLOT_LENGTH_Y / 2.0, 25.0)
    cam_top_obj.rotation_euler = (0, 0, 0)
    get_or_create_collection(col_view).objects.link(cam_top_obj)

    # 2. Isometric 3D View Camera (Positioned to see down ramp, aisle, and bays)
    cam_iso_data = bpy.data.cameras.new("Camera_Isometric")
    cam_iso_data.type = 'PERSP'
    cam_iso_data.lens = 28
    cam_iso_obj = bpy.data.objects.new("Camera_Isometric", cam_iso_data)
    cam_iso_obj.location = (-12.0, -12.0, 16.0)
    dir_vec = Vector((PLOT_WIDTH_X / 2.0 + 1.0, PLOT_LENGTH_Y / 2.0 - 2.0, -2.0)) - cam_iso_obj.location
    cam_iso_obj.rotation_euler = dir_vec.to_track_quat('-Z', 'Y').to_euler()
    get_or_create_collection(col_view).objects.link(cam_iso_obj)

    scene.camera = cam_iso_obj

    # Sun Light
    sun_data = bpy.data.lights.new("Sun_Light", type='SUN')
    sun_data.energy = 4.0
    sun_data.color = (1.0, 0.98, 0.95)
    sun_obj = bpy.data.objects.new("Sun_Light", sun_data)
    sun_obj.location = (20.0, -10.0, 30.0)
    sun_obj.rotation_euler = (math.radians(50), math.radians(20), math.radians(-40))
    get_or_create_collection(col_view).objects.link(sun_obj)

    # Fill Light
    fill_data = bpy.data.lights.new("Fill_Light", type='SUN')
    fill_data.energy = 1.5
    fill_data.color = (0.85, 0.90, 1.0)
    fill_obj = bpy.data.objects.new("Fill_Light", fill_data)
    fill_obj.location = (-20.0, 40.0, 25.0)
    fill_obj.rotation_euler = (math.radians(45), math.radians(-30), math.radians(130))
    get_or_create_collection(col_view).objects.link(fill_obj)

    print("Model construction complete. Objects:", len(bpy.data.objects))

# Execute build
build_entire_model()
