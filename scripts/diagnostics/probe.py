"""probe.py - discover exact Blender 5.2 API surface relevant to a photoreal setup."""
import bpy, math

print("\n" + "#" * 90)
print("# API PROBE")
print("#" * 90)

print("\n--- World ---")
w = bpy.context.scene.world
print("  world:", w, "use_nodes:", w.use_nodes if w else None)
if w and w.use_nodes:
    for n in w.node_tree.nodes:
        print(f"    node {n.type} '{n.name}'")
        for i in n.inputs:
            try:
                v = i.default_value
                if hasattr(v, '__len__'):
                    v = tuple(round(x, 3) for x in v)
                else:
                    v = round(v, 3)
                print(f"       in  {i.name:20s} = {v}")
            except Exception:
                print(f"       in  {i.name:20s} = <no default>")

print("\n--- Sky texture enum options ---")
try:
    prop = bpy.types.ShaderNodeTexSky.bl_rna.properties['sky_type']
    for e in prop.enum_items:
        print("   ", e.identifier, "|", e.name)
except Exception as e:
    print("   err:", e)

print("\n--- EEVEE properties (Blender 5.2) ---")
for attr in sorted(dir(bpy.context.scene.eevee)):
    if attr.startswith('_'):
        continue
    try:
        v = getattr(bpy.context.scene.eevee, attr)
        if callable(v):
            continue
        if hasattr(v, '__len__'):
            v = tuple(round(x, 3) for x in v)
        elif isinstance(v, float):
            v = round(v, 3)
        print(f"   {attr:42s} = {v}")
    except Exception as e:
        print(f"   {attr:42s} ! {e}")

print("\n--- scene.eevee.ray_tracing_options ---")
rt = getattr(bpy.context.scene.eevee, 'ray_tracing_options', None)
print("   ", rt)
if rt:
    for attr in sorted(dir(rt)):
        if attr.startswith('_'):
            continue
        try:
            v = getattr(rt, attr)
            if callable(v):
                continue
            print(f"   {attr:42s} = {v}")
        except Exception:
            pass

print("\n--- view_transform / look enum ---")
try:
    for e in bpy.types.ColorManagedViewSettings.bl_rna.properties['view_transform'].enum_items:
        print("   VT:", e.identifier)
except Exception as e:
    print("   ", e)
try:
    cm = bpy.context.scene.view_settings
    print("   look options via bl_rna:")
    for e in bpy.types.ColorManagedViewSettings.bl_rna.properties['look'].enum_items:
        print("   LOOK:", e.identifier)
except Exception as e:
    print("   ", e)

print("\n--- Materials: node inventory ---")
for m in sorted(bpy.data.materials, key=lambda m: m.name):
    if not m.use_nodes:
        print(f"   {m.name}: NO NODES  diffuse={tuple(round(c,3) for c in m.diffuse_color)}")
        continue
    types = {}
    for n in m.node_tree.nodes:
        types[n.type] = types.get(n.type, 0) + 1
    print(f"   {m.name:26s} nodes={types} blend={getattr(m,'blend_method','n/a')}")

print("\n--- One material in detail (Mat_Concrete) ---")
m = bpy.data.materials.get('Mat_Concrete')
if m and m.use_nodes:
    for n in m.node_tree.nodes:
        print(f"   node {n.type} '{n.name}'")
        for i in n.inputs:
            try:
                dv = i.default_value
                if hasattr(dv, '__len__'):
                    dv = tuple(round(x, 3) for x in dv)
                else:
                    dv = round(dv, 3)
                linked = " <-LINKED" if i.is_linked else ""
                print(f"      {i.name:22s} = {dv}{linked}")
            except Exception:
                print(f"      {i.name:22s} = ?")
    for l in m.node_tree.links:
        print(f"   link {l.from_node.name}.{l.from_socket.name} -> {l.to_node.name}.{l.to_socket.name}")

print("\n--- Image textures loaded ---")
for im in bpy.data.images:
    print(f"   {im.name:50s} size={tuple(im.size)} src={im.source}")
print("#" * 90 + "\n")
