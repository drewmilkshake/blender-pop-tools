import bpy
import math


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for block in (bpy.data.meshes, bpy.data.materials):
        for item in list(block):
            if item.users == 0:
                block.remove(item)


# ---------- Matériaux ----------
def vinyl_material(name, color, roughness=0.18):
    """Plastique vinyle brillant, comme une vraie Pop."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    bsdf.inputs['Roughness'].default_value = roughness
    return mat


def neon_material(name, color, strength):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    emi = nodes.new("ShaderNodeEmission")
    emi.inputs['Color'].default_value = (*color, 1.0)
    emi.inputs['Strength'].default_value = strength
    links.new(emi.outputs['Emission'], out.inputs['Surface'])
    return mat


# ---------- Helper de création ----------
def add(prim, name, loc, scale=(1, 1, 1), rot=(0, 0, 0), mat=None,
        bevel=0.0, smooth=True, **kw):
    getattr(bpy.ops.mesh, f"primitive_{prim}_add")(location=loc, rotation=rot, **kw)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(scale=True)
    if smooth:
        bpy.ops.object.shade_smooth()
    if bevel > 0:
        b = obj.modifiers.new("Bevel", 'BEVEL')
        b.width = bevel
        b.segments = 5
        b.limit_method = 'ANGLE'
        s = obj.modifiers.new("Subsurf", 'SUBSURF')
        s.levels = 2
        s.render_levels = 2
    if mat:
        obj.data.materials.append(mat)
    return obj


def create_cyber_pop_knight():
    clear_scene()

    # Matériaux
    white = vinyl_material("Vinyl_White", (0.85, 0.87, 0.95))
    dark = vinyl_material("Vinyl_Dark", (0.04, 0.04, 0.07), 0.12)
    black = vinyl_material("Vinyl_Eyes", (0.0, 0.0, 0.0), 0.05)
    base_m = vinyl_material("Vinyl_Base", (0.02, 0.02, 0.04), 0.3)
    cyan = neon_material("Neon_Cyan", (0.0, 1.0, 0.9), 8.0)
    magenta = neon_material("Neon_Magenta", (1.0, 0.0, 0.6), 10.0)

    # Socle
    add("cylinder", "Pop_Base", (0, 0, 0.05), mat=base_m, bevel=0.03,
        radius=0.9, depth=0.1, vertices=48)
    add("torus", "Pop_Base_Ring", (0, 0, 0.1), mat=cyan,
        major_radius=0.82, minor_radius=0.025)

    # Jambes (courtes)
    for side, x in (("L", -0.22), ("R", 0.22)):
        add("cylinder", f"Leg_{side}", (x, 0, 0.38), mat=dark, bevel=0.04,
            radius=0.17, depth=0.56, vertices=32)
        add("cube", f"Foot_{side}", (x, -0.07, 0.17), scale=(0.34, 0.5, 0.18),
            mat=white, bevel=0.06, size=1)

    # Corps (petit)
    add("cube", "Body", (0, 0, 1.0), scale=(0.9, 0.6, 0.75), mat=white,
        bevel=0.12, size=1)
    add("cube", "Chest_Plate", (0, -0.31, 1.05), scale=(0.5, 0.05, 0.4), mat=dark,
        bevel=0.02, size=1)
    add("cube", "Chest_Core", (0, -0.34, 1.05), scale=(0.18, 0.03, 0.18), mat=cyan,
        smooth=False, size=1)
    add("cube", "Belt", (0, 0, 0.7), scale=(0.93, 0.63, 0.1), mat=magenta,
        smooth=False, size=1)

    # Bras (petits)
    for side, x in (("L", -0.6), ("R", 0.6)):
        add("uv_sphere", f"Arm_{side}", (x, 0, 1.05), scale=(0.17, 0.17, 0.33),
            mat=dark, radius=1, segments=32, ring_count=16)

    # Tête (grosse, carrée arrondie)
    add("cube", "Head", (0, 0, 1.92), scale=(1.5, 1.3, 1.25), mat=white,
        bevel=0.35, size=1)

    # Bandeau LED / visière
    add("cube", "Visor_Band", (0, 0, 2.18), scale=(1.53, 1.33, 0.14), mat=cyan,
        bevel=0.03, smooth=False, size=1)

    # Yeux noirs de figurine Pop
    for side, x in (("L", -0.32), ("R", 0.32)):
        add("uv_sphere", f"Eye_{side}", (x, -0.62, 1.82), scale=(1, 0.55, 1),
            mat=black, radius=0.11, segments=32, ring_count=16)

    # Crête du casque
    add("cube", "Helmet_Crest", (0, 0, 2.68), scale=(0.1, 0.9, 0.3), mat=magenta,
        bevel=0.03, size=1)

    # Épée énergétique (main droite)
    add("cube", "Sword_Guard", (0.82, -0.05, 1.0), scale=(0.34, 0.09, 0.07),
        mat=dark, bevel=0.015, size=1)
    add("cube", "Sword_Blade", (0.82, -0.05, 1.75), scale=(0.08, 0.05, 1.4),
        mat=magenta, smooth=False, size=1)

    # Bouclier holographique (bras gauche)
    add("cylinder", "Shield_Holo", (-0.82, -0.15, 1.1), rot=(0, math.pi / 2, 0),
        mat=cyan, radius=0.42, depth=0.05, vertices=6, smooth=False)
    add("cylinder", "Shield_Rim", (-0.8, -0.15, 1.1), rot=(0, math.pi / 2, 0),
        mat=dark, radius=0.46, depth=0.03, vertices=6, smooth=False)

    # ---------- Scène : caméra, lumières, fond ----------
    scene = bpy.context.scene

    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs['Color'].default_value = (0.01, 0.01, 0.03, 1)

    bpy.ops.object.camera_add(location=(0, -8.5, 2.3), rotation=(math.radians(88), 0, 0))
    scene.camera = bpy.context.active_object
    scene.camera.data.lens = 85

    bpy.ops.object.light_add(type='AREA', location=(3, -4, 5))
    key = bpy.context.active_object
    key.data.energy = 600
    key.data.size = 4
    key.rotation_euler = (math.radians(55), 0, math.radians(30))

    bpy.ops.object.light_add(type='AREA', location=(-4, -3, 3))
    fill = bpy.context.active_object
    fill.data.energy = 250
    fill.data.size = 4
    fill.rotation_euler = (math.radians(70), 0, math.radians(-40))

    # Rendu Cycles : le néon (émission) y rayonne naturellement
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 96
    scene.render.resolution_x = 1080
    scene.render.resolution_y = 1350

    print("Figurine Pop Cyber Knight générée !")


create_cyber_pop_knight()