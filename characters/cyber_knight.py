import bpy
import math

# =====================================================
#  Figurine Pop style CYBERPUNK (Sans décor)
#  Blender 3.x / 4.x  -  Scripting > Run Script
# =====================================================


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.curves):
        for item in list(block):
            if item.users == 0:
                block.remove(item)


# ---------- Matériaux ----------
def vinyl(name, color, rough=0.2, metal=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    b = mat.node_tree.nodes["Principled BSDF"]
    b.inputs['Base Color'].default_value = (*color, 1.0)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    return mat


def neon(name, color, strength):
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


def cable(name, p0, p1, p2, mat, thickness=0.025):
    bpy.ops.curve.primitive_bezier_curve_add(location=(0, 0, 0))
    c = bpy.context.active_object
    c.name = name
    sp = c.data.splines[0]
    sp.bezier_points.add(1)
    for pt, co in zip(sp.bezier_points, (p0, p1, p2)):
        pt.co = co
        pt.handle_left_type = 'AUTO'
        pt.handle_right_type = 'AUTO'
    c.data.bevel_depth = thickness
    c.data.bevel_resolution = 4
    c.data.materials.append(mat)
    return c


def point_light(kind, name, loc, rot, color, energy, size):
    bpy.ops.object.light_add(type=kind, location=loc, rotation=rot)
    l = bpy.context.active_object
    l.name = name
    l.data.color = color
    l.data.energy = energy
    if kind == 'AREA':
        l.data.size = size
    return l


def create_cyberpunk_pop():
    clear_scene()
    rad = math.radians

    # ---------- Palette ----------
    CYAN = (0.0, 0.95, 1.0)
    MAGENTA = (1.0, 0.0, 0.55)
    PURPLE = (0.45, 0.1, 1.0)

    skin = vinyl("Vinyl_Skin", (0.75, 0.6, 0.56), 0.22)
    jacket = vinyl("Vinyl_Jacket", (0.05, 0.02, 0.1), 0.28)
    dark = vinyl("Vinyl_Dark", (0.02, 0.02, 0.04), 0.15)
    chrome = vinyl("Chrome", (0.75, 0.78, 0.85), 0.12, metal=1.0)
    base_m = vinyl("Base_Mat", (0.01, 0.01, 0.03), 0.2, metal=0.6)

    n_cyan = neon("Neon_Cyan", CYAN, 9.0)
    n_mag = neon("Neon_Magenta", MAGENTA, 11.0)
    n_pur = neon("Neon_Purple", PURPLE, 9.0)

    # ---------- Socle ----------
    add("cylinder", "Pop_Base", (0, 0, 0.05), mat=base_m, bevel=0.03,
        radius=0.9, depth=0.1, vertices=48)
    add("torus", "Base_Ring_Cyan", (0, 0, 0.11), mat=n_cyan,
        major_radius=0.82, minor_radius=0.025)
    add("torus", "Base_Ring_Magenta", (0, 0, 0.11), mat=n_mag,
        major_radius=0.7, minor_radius=0.015)

    # ---------- Jambes + bottes ----------
    for s, x in (("L", -0.22), ("R", 0.22)):
        add("cylinder", f"Leg_{s}", (x, 0, 0.4), mat=dark, bevel=0.04,
            radius=0.17, depth=0.56, vertices=32)
        add("cube", f"Leg_Stripe_{s}", (x * 1.75, 0, 0.42), scale=(0.03, 0.04, 0.5),
            mat=n_cyan, smooth=False, size=1)
        add("cube", f"Boot_{s}", (x, -0.07, 0.19), scale=(0.36, 0.52, 0.2),
            mat=chrome, bevel=0.06, size=1)
        add("cube", f"Boot_Sole_{s}", (x, -0.07, 0.115), scale=(0.38, 0.54, 0.04),
            mat=n_mag, smooth=False, size=1)

    # ---------- Corps : blouson ----------
    add("cube", "Body", (0, 0, 1.0), scale=(0.9, 0.6, 0.75), mat=jacket,
        bevel=0.12, size=1)
    for x in (-0.25, 0.25):
        add("cube", f"Jacket_Stripe_{x}", (x, -0.31, 1.0), scale=(0.03, 0.03, 0.6),
            mat=n_cyan, smooth=False, size=1)
    add("cube", "Chest_Core", (0, -0.33, 1.08), scale=(0.16, 0.03, 0.16),
        mat=n_mag, smooth=False, size=1)
    add("cube", "Belt", (0, 0, 0.7), scale=(0.93, 0.63, 0.08), mat=n_pur,
        smooth=False, size=1)

    # Col montant
    add("cube", "High_Collar", (0, 0.12, 1.45), scale=(1.0, 0.7, 0.3), mat=jacket,
        bevel=0.08, size=1)

    # Épaulette gauche
    add("cube", "Shoulder_Pad", (-0.58, 0, 1.34), scale=(0.4, 0.5, 0.14), rot=(0, rad(-20), 0),
        mat=dark, bevel=0.04, size=1)
    add("cube", "Shoulder_Neon", (-0.6, 0, 1.4), scale=(0.34, 0.04, 0.03), rot=(0, rad(-20), 0),
        mat=n_mag, smooth=False, size=1)

    # Sac à dos + câble
    add("cube", "Backpack", (0, 0.45, 1.05), scale=(0.6, 0.25, 0.6), mat=dark,
        bevel=0.05, size=1)
    add("cube", "Backpack_Vent", (0, 0.58, 1.05), scale=(0.4, 0.02, 0.05),
        mat=n_cyan, smooth=False, size=1)
    cable("Neck_Cable", (0.3, 0.6, 1.9), (0.6, 0.8, 1.5), (0.2, 0.5, 1.3), n_pur)

    # ---------- Bras ----------
    # Gauche : organique
    add("uv_sphere", "Arm_L", (-0.62, 0, 1.05), scale=(0.17, 0.17, 0.33), mat=jacket,
        radius=1, segments=32, ring_count=16)
    # Droit : cybernétique chromé
    add("uv_sphere", "Arm_R_Cyber", (0.62, 0, 1.05), scale=(0.18, 0.18, 0.34), mat=chrome,
        radius=1, segments=32, ring_count=16)
    add("torus", "Arm_R_Ring_A", (0.62, 0, 1.18), mat=n_cyan,
        major_radius=0.19, minor_radius=0.02)
    add("torus", "Arm_R_Ring_B", (0.62, 0, 0.95), mat=n_cyan,
        major_radius=0.18, minor_radius=0.02)

    # ---------- Tête ----------
    add("cube", "Head", (0, 0, 1.92), scale=(1.5, 1.3, 1.25), mat=skin,
        bevel=0.35, size=1)

    # Visière cyber (remplace les yeux)
    add("cube", "Visor", (0, -0.64, 1.9), scale=(1.1, 0.12, 0.26), mat=n_mag,
        bevel=0.03, size=1)
    add("uv_sphere", "Cyber_Eye", (0.4, -0.72, 1.9), scale=(1, 0.5, 1), mat=n_cyan,
        radius=0.07, segments=24, ring_count=12)

    # Masque bas du visage avec fentes
    add("cube", "Face_Mask", (0, -0.62, 1.52), scale=(0.95, 0.12, 0.4), mat=dark,
        bevel=0.04, size=1)
    for i, z in enumerate((1.45, 1.52, 1.59)):
        add("cube", f"Mask_Slit_{i}", (0, -0.7, z), scale=(0.6, 0.02, 0.03),
            mat=n_cyan, smooth=False, size=1)

    # Crête mohawk néon
    spikes = [(-0.5, 0.35), (-0.33, 0.45), (-0.16, 0.55), (0, 0.6),
              (0.16, 0.55), (0.33, 0.45), (0.5, 0.35)]
    for i, (y, h) in enumerate(spikes):
        add("cone", f"Mohawk_{i}", (0, y, 2.5 + h / 2),
            mat=(n_cyan if i % 2 == 0 else n_mag),
            radius1=0.1, radius2=0.0, depth=h, vertices=16)

    # Antenne latérale
    add("cylinder", "Antenna", (-0.78, 0.1, 2.15), mat=chrome,
        radius=0.025, depth=0.5, vertices=12)
    add("uv_sphere", "Antenna_Tip", (-0.78, 0.1, 2.42), mat=n_mag,
        radius=0.06, segments=16, ring_count=8)
    add("cylinder", "Ear_Piece", (-0.77, 0, 1.92), rot=(0, rad(90), 0), mat=dark,
        radius=0.2, depth=0.1, vertices=24)

    # ---------- Katana néon ----------
    tilt = (0, rad(25), 0)
    add("cube", "Katana_Handle", (0.8, -0.1, 0.95), scale=(0.05, 0.05, 0.3), rot=tilt,
        mat=dark, bevel=0.01, size=1)
    add("cube", "Katana_Guard", (0.88, -0.1, 1.12), scale=(0.28, 0.1, 0.04), rot=tilt,
        mat=chrome, bevel=0.01, size=1)
    add("cube", "Katana_Blade", (1.22, -0.1, 1.8), scale=(0.05, 0.03, 1.5), rot=tilt,
        mat=n_cyan, smooth=False, size=1)

    # ---------- Caméra ----------
    scene = bpy.context.scene
    bpy.ops.object.camera_add(location=(0, -9, 1.9), rotation=(rad(90), 0, 0))
    scene.camera = bpy.context.active_object
    scene.camera.data.lens = 50

    # ---------- Lumières studio ----------
    point_light('AREA', "Rim_Magenta", (-4, 2, 3), (rad(70), 0, rad(-60)), MAGENTA, 900, 3)
    point_light('AREA', "Rim_Cyan", (4, 2, 3), (rad(70), 0, rad(60)), CYAN, 900, 3)
    point_light('AREA', "Key_Soft", (0, -5, 4), (rad(60), 0, 0), (0.8, 0.8, 1.0), 250, 4)

    # ---------- Monde + rendu ----------
    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs['Color'].default_value = (0.015, 0.0, 0.035, 1)

    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 128
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1080
    scene.render.resolution_y = 1350

    print("Neon Runner (Figurine seule) généré avec succès !")


create_cyberpunk_pop()