"""diag_model.py -- inspect an appended Poly Haven model: are its textures
packed, and are the materials alpha-driven?"""
import bpy, os, sys

path = sys.argv[-1]
print("=== importing", path)
before = set(bpy.data.objects.keys())
imgs_before = set(bpy.data.images.keys())
with bpy.data.libraries.load(path, link=False) as (src, dst):
    dst.objects = [n for n in src.objects]
new = [bpy.data.objects[n] for n in bpy.data.objects.keys() if n not in before]
print(f"objects imported: {len(new)}")
meshes = [o for o in new if o.type == 'MESH']
tot_v = sum(len(o.data.vertices) for o in meshes)
tot_p = sum(len(o.data.polygons) for o in meshes)
print(f"meshes={len(meshes)} verts={tot_v} polys={tot_p}")
for o in meshes[:8]:
    print(f"   {o.name[:44]:44s} v={len(o.data.vertices):6d} p={len(o.data.polygons):6d} "
          f"mats={[m.name if m else None for m in o.data.materials]}")

print("\n--- materials ---")
mats = {m.name: m for o in meshes for m in o.data.materials if m}
for name, m in list(mats.items())[:10]:
    if not m.use_nodes:
        print(f"  {name}: NO NODES")
        continue
    imgs = [(n.image.name if n.image else None,
             (n.image.filepath if n.image else ''),
             (n.image.packed_file is not None) if (n.image and hasattr(n.image, 'packed_file')) else None,
             (tuple(n.image.size) if n.image else None))
            for n in m.node_tree.nodes if n.type == 'TEX_IMAGE']
    bsdf = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    alpha_linked = bool(bsdf and bsdf.inputs['Alpha'].is_linked)
    base_linked = bool(bsdf and bsdf.inputs['Base Color'].is_linked)
    print(f"  {name[:34]:34s} blend={getattr(m,'blend_method','?')} "
          f"alpha_linked={alpha_linked} base_linked={base_linked}")
    for i in imgs:
        print(f"      img name={i[0]} packed={i[2]} size={i[3]}")
        print(f"          path={i[1][:110]}")

print("\n--- new images ---")
for n in bpy.data.images:
    if n.name in imgs_before:
        continue
    try:
        sz = tuple(n.size)
    except Exception:
        sz = '?'
    print(f"  {n.name[:40]:40s} size={sz} packed={n.packed_file is not None} "
          f"exists={os.path.exists(bpy.path.abspath(n.filepath))} path={n.filepath[:90]}")
print("=== done")
