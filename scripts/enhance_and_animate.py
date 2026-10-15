"""
Enhance Basement Parking Concept Design in Blender:
- Realistic Materials (Exposed concrete, epoxy floor, hazard stripes, galvanised steel)
- Lighting (LED aisle batten strips, emergency exit signs, ramp opening daylight)
- 20s 24fps Walkthrough / Drive-through Camera Animation on Bezier Path with Look-Ahead Target
- EEVEE Render Settings (1920x1080, //render/ output)
"""

import bpy
import bmesh
import math
from mathutils import Vector, Euler

def setup_enhanced_scene():
    scene = bpy.context.scene
    
    # --------------------------------------------------------------------------
    # 1. RENDER SETTINGS (EEVEE, 1920x1080, 24fps, 480 frames, //render/)
    # --------------------------------------------------------------------------
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.fps = 24
    scene.frame_start = 1
    scene.frame_end = 480  # 20 seconds at 24 fps
    scene.render.filepath = "//render/"
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.color_depth = '8'

    # --------------------------------------------------------------------------
    # 2. ADVANCED REALISTIC MATERIALS
    # --------------------------------------------------------------------------
    
    # Helper: Clear and get node tree
    def init_mat(name):
        mat = bpy.data.materials.get(name)
        if mat is None:
            mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()
        return mat, nodes, links

    # A. Exposed Grey Concrete (Walls, Beams, Soffit)
    mat_conc, nodes, links = init_mat("Mat_Concrete_Structure")
    mat_conc.diffuse_color = (0.55, 0.57, 0.59, 1.0)
    
    tex_coord = nodes.new("ShaderNodeTexCoord")
    noise_tex = nodes.new("ShaderNodeTexNoise")
    noise_tex.inputs['Scale'].default_value = 18.0
    noise_tex.inputs['Detail'].default_value = 4.0
    noise_tex.inputs['Roughness'].default_value = 0.65
    
    ramp_conc = nodes.new("ShaderNodeValToRGB")
    ramp_conc.color_ramp.elements[0].position = 0.15
    ramp_conc.color_ramp.elements[0].color = (0.48, 0.50, 0.52, 1.0)
    ramp_conc.color_ramp.elements[1].position = 0.85
    ramp_conc.color_ramp.elements[1].color = (0.62, 0.64, 0.66, 1.0)
    
    bump_conc = nodes.new("ShaderNodeBump")
    bump_conc.inputs['Distance'].default_value = 0.004
    bump_conc.inputs['Strength'].default_value = 0.35
    
    bsdf_conc = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf_conc.inputs['Roughness'].default_value = 0.72
    
    out_conc = nodes.new("ShaderNodeOutputMaterial")
    
    links.new(tex_coord.outputs['Object'], noise_tex.inputs['Vector'])
    links.new(noise_tex.outputs['Fac'], ramp_conc.inputs['Fac'])
    links.new(ramp_conc.outputs['Color'], bsdf_conc.inputs['Base Color'])
    links.new(noise_tex.outputs['Fac'], bump_conc.inputs['Height'])
    links.new(bump_conc.outputs['Normal'], bsdf_conc.inputs['Normal'])
    links.new(bsdf_conc.outputs['BSDF'], out_conc.inputs['Surface'])

    # B. Epoxy Grey Floor (Reflective Industrial Finish)
    mat_floor, nodes, links = init_mat("Mat_Concrete_Floor")
    mat_floor.diffuse_color = (0.24, 0.26, 0.28, 1.0)
    
    tex_coord_f = nodes.new("ShaderNodeTexCoord")
    noise_f = nodes.new("ShaderNodeTexNoise")
    noise_f.inputs['Scale'].default_value = 35.0
    noise_f.inputs['Detail'].default_value = 2.0
    
    ramp_f = nodes.new("ShaderNodeValToRGB")
    ramp_f.color_ramp.elements[0].position = 0.2
    ramp_f.color_ramp.elements[0].color = (0.22, 0.24, 0.26, 1.0)
    ramp_f.color_ramp.elements[1].position = 0.8
    ramp_f.color_ramp.elements[1].color = (0.27, 0.29, 0.31, 1.0)
    
    bsdf_floor = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf_floor.inputs['Roughness'].default_value = 0.24  # Glossy industrial epoxy
    
    out_floor = nodes.new("ShaderNodeOutputMaterial")
    
    links.new(tex_coord_f.outputs['Object'], noise_f.inputs['Vector'])
    links.new(noise_f.outputs['Fac'], ramp_f.inputs['Fac'])
    links.new(ramp_f.outputs['Color'], bsdf_floor.inputs['Base Color'])
    links.new(bsdf_floor.outputs['BSDF'], out_floor.inputs['Surface'])

    # C. Height-Masked Columns: Yellow-Black Hazard Stripes on Bottom 0.9m + Concrete Above
    mat_col_hazard, nodes, links = init_mat("Mat_Column_Hazard_Concrete")
    mat_col_hazard.diffuse_color = (0.95, 0.80, 0.05, 1.0)
    
    coord_c = nodes.new("ShaderNodeTexCoord")
    sep_c = nodes.new("ShaderNodeSeparateXYZ")
    
    # 45 deg diagonal coordinates for stripes
    mapping_diag = nodes.new("ShaderNodeMapping")
    mapping_diag.vector_type = 'POINT'
    mapping_diag.inputs['Rotation'].default_value = (0.785398, 0.0, 0.785398) # 45 deg
    
    sep_diag = nodes.new("ShaderNodeSeparateXYZ")
    mod_c = nodes.new("ShaderNodeMath")
    mod_c.operation = 'MODULO'
    mod_c.inputs[1].default_value = 0.20 # 20cm stripes
    
    gt_c = nodes.new("ShaderNodeMath")
    gt_c.operation = 'GREATER_THAN'
    gt_c.inputs[1].default_value = 0.10
    
    ramp_hazard = nodes.new("ShaderNodeValToRGB")
    ramp_hazard.color_ramp.elements[0].position = 0.0
    ramp_hazard.color_ramp.elements[0].color = (0.04, 0.04, 0.04, 1.0) # Black
    ramp_hazard.color_ramp.elements[1].position = 1.0
    ramp_hazard.color_ramp.elements[1].color = (0.96, 0.82, 0.04, 1.0) # Safety Yellow
    
    # Height mask: bottom 0.9m
    mask_height = nodes.new("ShaderNodeMath")
    mask_height.operation = 'LESS_THAN'
    mask_height.inputs[1].default_value = 0.90
    
    mix_col = nodes.new("ShaderNodeMix")
    mix_col.data_type = 'RGBA'
    
    # Connect
    links.new(coord_c.outputs['Object'], sep_c.inputs['Vector'])
    links.new(sep_c.outputs['Z'], mask_height.inputs[0])
    
    links.new(coord_c.outputs['Object'], mapping_diag.inputs['Vector'])
    links.new(mapping_diag.outputs['Vector'], sep_diag.inputs['Vector'])
    links.new(sep_diag.outputs['X'], mod_c.inputs[0])
    links.new(mod_c.outputs['Value'], gt_c.inputs[0])
    links.new(gt_c.outputs['Value'], ramp_hazard.inputs['Fac'])
    
    # Concrete color for upper column
    mix_col.inputs[6].default_value = (0.56, 0.58, 0.60, 1.0) # A: Concrete
    links.new(ramp_hazard.outputs['Color'], mix_col.inputs[7])  # B: Hazard
    links.new(mask_height.outputs['Value'], mix_col.inputs['Factor'])
    
    bsdf_col = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf_col.inputs['Roughness'].default_value = 0.50
    links.new(mix_col.outputs[2], bsdf_col.inputs['Base Color'])
    
    out_col = nodes.new("ShaderNodeOutputMaterial")
    links.new(bsdf_col.outputs['BSDF'], out_col.inputs['Surface'])

    # Apply this material to all columns
    for obj in bpy.data.objects:
        if obj.name.startswith("Column_"):
            obj.data.materials.clear()
            obj.data.materials.append(mat_col_hazard)

    # D. Hazard Stripes for Ramp Kerbs
    mat_kerb_hazard, nodes, links = init_mat("Mat_Barrier_Hazard")
    mat_kerb_hazard.diffuse_color = (0.95, 0.80, 0.05, 1.0)
    
    coord_k = nodes.new("ShaderNodeTexCoord")
    map_k = nodes.new("ShaderNodeMapping")
    map_k.inputs['Rotation'].default_value = (0.785398, 0.0, 0.785398)
    sep_k = nodes.new("ShaderNodeSeparateXYZ")
    mod_k = nodes.new("ShaderNodeMath")
    mod_k.operation = 'MODULO'
    mod_k.inputs[1].default_value = 0.22
    gt_k = nodes.new("ShaderNodeMath")
    gt_k.operation = 'GREATER_THAN'
    gt_k.inputs[1].default_value = 0.11
    ramp_kh = nodes.new("ShaderNodeValToRGB")
    ramp_kh.color_ramp.elements[0].position = 0.0
    ramp_kh.color_ramp.elements[0].color = (0.04, 0.04, 0.04, 1.0)
    ramp_kh.color_ramp.elements[1].position = 1.0
    ramp_kh.color_ramp.elements[1].color = (0.96, 0.82, 0.04, 1.0)
    bsdf_k = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf_k.inputs['Roughness'].default_value = 0.40
    out_k = nodes.new("ShaderNodeOutputMaterial")
    
    links.new(coord_k.outputs['Object'], map_k.inputs['Vector'])
    links.new(map_k.outputs['Vector'], sep_k.inputs['Vector'])
    links.new(sep_k.outputs['X'], mod_k.inputs[0])
    links.new(mod_k.outputs['Value'], gt_k.inputs[0])
    links.new(gt_k.outputs['Value'], ramp_kh.inputs['Fac'])
    links.new(ramp_kh.outputs['Color'], bsdf_k.inputs['Base Color'])
    links.new(bsdf_k.outputs['BSDF'], out_k.inputs['Surface'])

    barrier_obj = bpy.data.objects.get("Ramp_Vehicle_Barrier")
    if barrier_obj:
        barrier_obj.data.materials.clear()
        barrier_obj.data.materials.append(mat_kerb_hazard)

    # E. Galvanised Steel (Barriers, Gratings, Metal Frames)
    mat_steel, nodes, links = init_mat("Mat_Galvanised_Steel")
    mat_steel.diffuse_color = (0.76, 0.78, 0.80, 1.0)
    bsdf_steel = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf_steel.inputs['Base Color'].default_value = (0.76, 0.78, 0.80, 1.0)
    bsdf_steel.inputs['Metallic'].default_value = 0.94
    bsdf_steel.inputs['Roughness'].default_value = 0.28
    out_steel = nodes.new("ShaderNodeOutputMaterial")
    links.new(bsdf_steel.outputs['BSDF'], out_steel.inputs['Surface'])

    # Apply steel to Sump Grating, Door Frames, Pump
    for steel_name in ["Sump_Pit_Cover_Grating", "Lift_Basement_Doors"]:
        so = bpy.data.objects.get(steel_name)
        if so:
            so.data.materials.clear()
            so.data.materials.append(mat_steel)

    # --------------------------------------------------------------------------
    # 3. LIGHTING (LED Aisle Strips, Emergency Exit Signs, Ramp Daylight)
    # --------------------------------------------------------------------------
    col_lights = bpy.data.collections.get("Services")
    if not col_lights:
        col_lights = scene.collection

    # A. Emissive LED fixture material
    mat_led_emissive, nodes, links = init_mat("Mat_LED_Diffuser")
    mat_led_emissive.diffuse_color = (0.95, 0.98, 1.0, 1.0)
    bsdf_led = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf_led.inputs['Base Color'].default_value = (0.95, 0.98, 1.0, 1.0)
    bsdf_led.inputs['Emission Color'].default_value = (0.95, 0.98, 1.0, 1.0)
    bsdf_led.inputs['Emission Strength'].default_value = 12.0
    out_led = nodes.new("ShaderNodeOutputMaterial")
    links.new(bsdf_led.outputs['BSDF'], out_led.inputs['Surface'])

    # 5 LED Strip Lights along the 6.1m central aisle (X = 6.85, Z = -0.55m)
    led_y_positions = [3.50, 9.50, 15.50, 21.50, 27.50]
    for i, y_pos in enumerate(led_y_positions):
        # Physical Fixture Mesh
        fixture_mesh = bpy.data.meshes.new(f"LED_Fixture_{i+1}")
        bm_fix = bmesh.new()
        bmesh.ops.create_cube(bm_fix, size=1.0)
        # Scale to 0.20m x 2.20m x 0.06m
        for v in bm_fix.verts:
            v.co.x *= 0.20
            v.co.y *= 2.20
            v.co.z *= 0.06
        bm_fix.to_mesh(fixture_mesh)
        bm_fix.free()
        
        fix_obj = bpy.data.objects.new(f"LED_Fixture_{i+1}", fixture_mesh)
        fix_obj.location = (6.85, y_pos, -0.55)
        fix_obj.data.materials.append(mat_led_emissive)
        col_lights.objects.link(fix_obj)

        # Actual Area Light
        light_data = bpy.data.lights.new(f"LED_Light_{i+1}", type='AREA')
        light_data.shape = 'RECTANGLE'
        light_data.size = 0.25
        light_data.size_y = 2.20
        light_data.energy = 220.0 # Watts
        light_data.color = (0.96, 0.98, 1.0)
        
        light_obj = bpy.data.objects.new(f"LED_Light_{i+1}", light_data)
        light_obj.location = (6.85, y_pos, -0.58)
        light_obj.rotation_euler = (0, 0, 0) # pointing downwards (-Z)
        col_lights.objects.link(light_obj)

    # B. Emergency EXIT Signs over Stair & Lift
    mat_exit_green, nodes, links = init_mat("Mat_Emergency_Exit")
    mat_exit_green.diffuse_color = (0.05, 0.85, 0.25, 1.0)
    bsdf_exit = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf_exit.inputs['Base Color'].default_value = (0.05, 0.85, 0.25, 1.0)
    bsdf_exit.inputs['Emission Color'].default_value = (0.05, 0.90, 0.30, 1.0)
    bsdf_exit.inputs['Emission Strength'].default_value = 10.0
    out_exit = nodes.new("ShaderNodeOutputMaterial")
    links.new(bsdf_exit.outputs['BSDF'], out_exit.inputs['Surface'])

    # Exit sign over Stair Door
    mesh_ex1 = bpy.data.meshes.new("Exit_Sign_Stair")
    bm_ex = bmesh.new()
    bmesh.ops.create_cube(bm_ex, size=1.0)
    for v in bm_ex.verts:
        v.co.x *= 0.50
        v.co.y *= 0.08
        v.co.z *= 0.25
    bm_ex.to_mesh(mesh_ex1)
    bm_ex.free()
    
    obj_ex1 = bpy.data.objects.new("Exit_Sign_Stair", mesh_ex1)
    obj_ex1.location = (13.35, 5.28, -1.05)
    obj_ex1.data.materials.append(mat_exit_green)
    col_lights.objects.link(obj_ex1)

    # Text "EXIT" on the sign
    curve_exit = bpy.data.curves.new("Exit_Sign_Text", type='FONT')
    curve_exit.body = "EXIT >"
    curve_exit.size = 0.14
    curve_exit.extrude = 0.01
    curve_exit.align_x = 'CENTER'
    curve_exit.align_y = 'CENTER'
    obj_extxt = bpy.data.objects.new("Exit_Sign_Text", curve_exit)
    obj_extxt.location = (13.35, 5.33, -1.05)
    obj_extxt.rotation_euler = (math.pi/2, 0, 0)
    col_lights.objects.link(obj_extxt)

    # C. Soft Daylight at Ramp Opening (Y = 0, X in [0, 3.8m])
    daylight_data = bpy.data.lights.new("Daylight_Ramp_Portal", type='AREA')
    daylight_data.shape = 'RECTANGLE'
    daylight_data.size = 3.60
    daylight_data.size_y = 2.50
    daylight_data.energy = 850.0 # Watts
    daylight_data.color = (1.0, 0.96, 0.92)
    
    daylight_obj = bpy.data.objects.new("Daylight_Ramp_Portal", daylight_data)
    daylight_obj.location = (1.90, -0.50, 1.20)
    # Angled down into the ramp portal (+Y, -Z)
    daylight_obj.rotation_euler = (math.radians(50), 0, 0)
    col_lights.objects.link(daylight_obj)

    # --------------------------------------------------------------------------
    # 4. CAMERA AT 1.6m EYE HEIGHT & ANIMATION ON BEZIER PATH
    # --------------------------------------------------------------------------
    # Path coordinates (1.6m eye height above road, sloping ramp, and basement floor):
    # 1. Road approach: X=1.90, Y=-3.0, Z=1.60
    # 2. Ramp crest: Y=0.0, Z=1.60
    # 3. Approach 1:25: Y=5.0, Z=1.40
    # 4. Ramp descent mid: Y=16.0, Z=0.18
    # 5. Ramp bottom: Y=27.5, Z=-1.26
    # 6. Basement FFL arrival: Y=29.2, Z=-1.70 (-3.30 + 1.60)
    # 7. Rear turning court arc: X=4.5, Y=29.0, Z=-1.70
    # 8. Align with central aisle: X=6.85, Y=26.5, Z=-1.70
    # 9. Drive down aisle mid: X=6.85, Y=16.0, Z=-1.70
    # 10. Approaching core/accessible bay: X=6.85, Y=7.5, Z=-1.70
    # 11. Turn toward pedestrian walkway: X=8.80, Y=5.5, Z=-1.70
    # 12. Walk to lift lobby: X=10.80, Y=4.2, Z=-1.70
    # 13. Arrive facing lift doors: X=11.20, Y=3.2, Z=-1.70
    
    path_points = [
        (1.90, -4.00,  1.60),
        (1.90,  0.00,  1.60),
        (1.90,  5.00,  1.40),
        (1.90, 16.00,  0.18),
        (1.90, 27.50, -1.26),
        (2.30, 29.20, -1.70),
        (4.80, 29.00, -1.70),
        (6.85, 26.50, -1.70),
        (6.85, 16.00, -1.70),
        (6.85,  7.50, -1.70),
        (8.80,  5.50, -1.70),
        (10.80, 4.20, -1.70),
        (11.20, 3.20, -1.70)
    ]

    # Create Bezier Curve
    walk_curve_data = bpy.data.curves.new("Camera_Walkthrough_Path", type='CURVE')
    walk_curve_data.dimensions = '3D'
    spline = walk_curve_data.splines.new('BEZIER')
    spline.bezier_points.add(len(path_points) - 1)
    
    for i, pt in enumerate(path_points):
        bp = spline.bezier_points[i]
        bp.co = pt
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'

    walk_curve_obj = bpy.data.objects.new("Camera_Walkthrough_Path", walk_curve_data)
    scene.collection.objects.link(walk_curve_obj)

    # Create Look-Ahead Target (Empty)
    target_empty = bpy.data.objects.new("Camera_LookAhead_Target", None)
    target_empty.empty_display_type = 'SPHERE'
    target_empty.empty_display_size = 0.3
    scene.collection.objects.link(target_empty)

    # Animate Empty on Path slightly leading the camera
    con_empty = target_empty.constraints.new('FOLLOW_PATH')
    con_empty.target = walk_curve_obj
    con_empty.use_fixed_location = True
    con_empty.offset_factor = 0.04 # starts slightly ahead
    con_empty.keyframe_insert(data_path="offset_factor", frame=1)
    con_empty.offset_factor = 1.00
    con_empty.keyframe_insert(data_path="offset_factor", frame=480)

    # Create Walkthrough Camera
    cam_walk_data = bpy.data.cameras.new("Camera_Walkthrough")
    cam_walk_data.lens = 24 # Wide angle 24mm for realistic interior driver/pedestrian FOV
    cam_walk_data.clip_start = 0.1
    cam_walk_data.clip_end = 150.0
    cam_walk_obj = bpy.data.objects.new("Camera_Walkthrough", cam_walk_data)
    scene.collection.objects.link(cam_walk_obj)

    # Animate Camera on Path with Follow Path & Track To
    con_cam_path = cam_walk_obj.constraints.new('FOLLOW_PATH')
    con_cam_path.target = walk_curve_obj
    con_cam_path.use_fixed_location = True
    con_cam_path.offset_factor = 0.00
    con_cam_path.keyframe_insert(data_path="offset_factor", frame=1)
    con_cam_path.offset_factor = 0.98 # ends right at lift
    con_cam_path.keyframe_insert(data_path="offset_factor", frame=480)

    con_cam_track = cam_walk_obj.constraints.new('TRACK_TO')
    con_cam_track.target = target_empty
    con_cam_track.track_axis = 'TRACK_NEGATIVE_Z'
    con_cam_track.up_axis = 'UP_Y'

    # Set as active scene camera
    scene.camera = cam_walk_obj
    print("Enhanced scene setup complete. Camera animated over 480 frames.")

setup_enhanced_scene()
