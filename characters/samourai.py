import bpy
import math
from mathutils import Vector

# =====================================================
#  Figurine Pop style SAMOURAÏ (socle + sashimono)
#  Blender 3.x / 4.x  -  Scripting > Run Script
# =====================================================


def clear_scene():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.curves, bpy.data.lights):
        for item in list(block):
            if item.users == 0:
                block.remove(item)


# ---------- Matériaux ----------
def vinyl(name, color, rough=0.3, metal=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    b = mat.node_tree.nodes["Principled BSDF"]
    b.inputs['Base Color'].default_value = (*color, 1.0)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
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


def lamp(name, loc, color, energy, size, target=(0, 0, 1.6)):
    bpy.ops.object.light_add(type='AREA', location=loc)
    l = bpy.context.active_object
    l.name = name
    l.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    l.data.color = color
    l.data.energy = energy
    l.data.size = size
    return l


def create_samurai_pop():
    clear_scene()
    rad = math.radians

    # ---------- Matériaux ----------
    skin = vinyl("Vinyl_Peau", (0.85, 0.62, 0.48), 0.28)
    red = vinyl("Vinyl_Rouge", (0.55, 0.03, 0.04), 0.3)
    black = vinyl("Vinyl_Noir", (0.02, 0.02, 0.03), 0.25)
    navy = vinyl("Vinyl_Indigo", (0.03, 0.05, 0.16), 0.4)
    white = vinyl("Tissu_Blanc", (0.9, 0.88, 0.8), 0.5)
    wood = vinyl("Bois", (0.3, 0.17, 0.08), 0.5)
    gold = vinyl("Or", (1.0, 0.72, 0.2), 0.25, metal=1.0)
    steel = vinyl("Acier", (0.88, 0.9, 0.95), 0.1, metal=1.0)
    eye_m = vinyl("Oeil", (0.0, 0.0, 0.0), 0.05)
    shine = vinyl("Reflet", (1.0, 1.0, 1.0), 0.1)
    base_m = vinyl("Socle", (0.04, 0.015, 0.015), 0.3, metal=0.4)

    # ---------- Socle ----------
    add("cylinder", "Socle", (0, 0, 0.05), mat=base_m, bevel=0.03,
        radius=0.9, depth=0.1, vertices=48)
    add("torus", "Socle_Anneau_Or", (0, 0, 0.11), mat=gold,
        major_radius=0.82, minor_radius=0.025)
    add("torus", "Socle_Anneau_Rouge", (0, 0, 0.11), mat=red,
        major_radius=0.7, minor_radius=0.018)

    # ---------- Jambes (hakama) + geta ----------
    for s, x in (("G", -0.22), ("D", 0.22)):
        add("cylinder", f"Hakama_{s}", (x, 0, 0.4), mat=navy, bevel=0.04,
            radius=0.19, depth=0.56, vertices=32)
        add("cube", f"Tabi_{s}", (x, -0.07, 0.255), scale=(0.3, 0.46, 0.1),
            mat=white, bevel=0.03, size=1)
        add("cube", f"Geta_Plateau_{s}", (x, -0.07, 0.19), scale=(0.34, 0.5, 0.04),
            mat=wood, bevel=0.012, size=1)
        for j, y in enumerate((-0.22, 0.08)):
            add("cube", f"Geta_Dent_{s}{j}", (x, y, 0.13), scale=(0.3, 0.08, 0.06),
                mat=wood, smooth=False, size=1)

    # ---------- Corps : armure rouge (dō) ----------
    add("cube", "Corps", (0, 0, 1.0), scale=(0.9, 0.6, 0.75), mat=red,
        bevel=0.12, size=1)
    for i, z in enumerate((0.85, 1.0, 1.15)):
        add("cube", f"Laçage_Or_{i}", (0, -0.31, z), scale=(0.8, 0.03, 0.04),
            mat=gold, smooth=False, size=1)
    # Col de kimono blanc en V
    for s, x, a in (("G", -0.1, -25), ("D", 0.1, 25)):
        add("cube", f"Col_Kimono_{s}", (x, -0.31, 1.24), scale=(0.1, 0.03, 0.3),
            rot=(0, rad(a), 0), mat=white, smooth=False, size=1)

    # Obi + nœud doré
    add("cube", "Obi", (0, 0, 0.7), scale=(0.93, 0.63, 0.1), mat=black,
        bevel=0.02, size=1)
    add("cube", "Obi_Noeud", (0, -0.34, 0.7), scale=(0.16, 0.05, 0.13), mat=gold,
        bevel=0.02, size=1)

    # Kusazuri (jupe de plaques) devant + derrière
    for i, x in enumerate((-0.3, 0.0, 0.3)):
        for side, y in (("Av", -0.31), ("Ar", 0.31)):
            add("cube", f"Kusazuri_{side}{i}", (x, y, 0.52), scale=(0.28, 0.05, 0.28),
                mat=red, bevel=0.02, size=1)
            add("cube", f"Kusazuri_Bord_{side}{i}", (x, y * 1.03, 0.39),
                scale=(0.28, 0.055, 0.03), mat=gold, smooth=False, size=1)

    # Wakizashi glissé dans l'obi (côté gauche)
    add("cube", "Wakizashi_Saya", (-0.35, 0.15, 0.72), scale=(0.07, 0.9, 0.07),
        mat=black, bevel=0.01, size=1)
    add("cube", "Wakizashi_Poignee", (-0.35, -0.45, 0.72), scale=(0.08, 0.3, 0.08),
        mat=navy, bevel=0.01, size=1)
    add("cube", "Wakizashi_Garde", (-0.35, -0.31, 0.72), scale=(0.13, 0.025, 0.13),
        mat=gold, smooth=False, size=1)

    # ---------- Épaulières (sode) ----------
    for s, x, a in (("G", -0.62, -20), ("D", 0.62, 20)):
        add("cube", f"Sode_{s}", (x, 0, 1.34), scale=(0.4, 0.5, 0.22), rot=(0, rad(a), 0),
            mat=red, bevel=0.05, size=1)
        add("cube", f"Sode_Or_{s}", (x * 1.04, 0, 1.23), scale=(0.42, 0.52, 0.03),
            rot=(0, rad(a), 0), mat=gold, smooth=False, size=1)

    # ---------- Bras ----------
    for s, x in (("G", -0.62), ("D", 0.62)):
        add("uv_sphere", f"Bras_{s}", (x, 0, 1.05), scale=(0.17, 0.17, 0.33), mat=navy,
            radius=1, segments=32, ring_count=16)
        add("torus", f"Kote_{s}", (x, 0, 0.86), mat=gold,
            major_radius=0.17, minor_radius=0.025)
    add("uv_sphere", "Main_G", (-0.62, -0.02, 0.66), mat=skin,
        radius=0.1, segments=24, ring_count=12)
    add("uv_sphere", "Main_D", (0.66, -0.12, 0.72), mat=skin,
        radius=0.11, segments=24, ring_count=12)

    # ---------- Katana (main droite) ----------
    tilt = (0, rad(25), 0)
    d = Vector((math.sin(rad(25)), 0, math.cos(rad(25))))
    H = Vector((0.66, -0.12, 0.72))
    add("cube", "Katana_Manche", tuple(H), scale=(0.06, 0.06, 0.4), rot=tilt,
        mat=black, bevel=0.01, size=1)
    add("cube", "Katana_Kashira", tuple(H - d * 0.21), scale=(0.08, 0.08, 0.04),
        rot=tilt, mat=gold, smooth=False, size=1)
    add("cylinder", "Katana_Tsuba", tuple(H + d * 0.22), rot=tilt, mat=gold,
        radius=0.12, depth=0.025, vertices=32)
    add("cube", "Katana_Lame", tuple(H + d * 1.03), scale=(0.07, 0.025, 1.6), rot=tilt,
        mat=steel, smooth=False, size=1)

    # ---------- Tête ----------
    add("cube", "Tete", (0, 0, 1.92), scale=(1.5, 1.3, 1.25), mat=skin,
        bevel=0.35, size=1)
    for s, x in (("G", -0.3), ("D", 0.3)):
        add("uv_sphere", f"Oeil_{s}", (x, -0.65, 1.88), scale=(1, 0.5, 1), mat=eye_m,
            radius=0.09, segments=24, ring_count=12)
        add("uv_sphere", f"Oeil_Reflet_{s}", (x - 0.03, -0.69, 1.92), scale=(1, 0.5, 1),
            mat=shine, radius=0.025, segments=12, ring_count=6)
    # Sourcils sévères (bout intérieur plus bas)
    add("cube", "Sourcil_G", (-0.3, -0.66, 2.03), scale=(0.22, 0.04, 0.05),
        rot=(0, rad(15), 0), mat=black, bevel=0.01, size=1)
    add("cube", "Sourcil_D", (0.3, -0.66, 2.03), scale=(0.22, 0.04, 0.05),
        rot=(0, rad(-15), 0), mat=black, bevel=0.01, size=1)
    # Fine moustache
    for s, x, a in (("G", -0.1, 12), ("D", 0.1, -12)):
        add("cube", f"Moustache_{s}", (x, -0.64, 1.62), scale=(0.17, 0.04, 0.04),
            rot=(0, rad(a), 0), mat=black, bevel=0.01, size=1)

    # ---------- Casque kabuto ----------
    add("uv_sphere", "Kabuto_Dome", (0, 0, 2.3), scale=(0.82, 0.72, 0.55), mat=red,
        radius=1, segments=48, ring_count=24)
    add("cylinder", "Kabuto_Visiere", (0, -0.02, 2.12), scale=(1, 0.88, 1), mat=black,
        radius=0.88, depth=0.06, vertices=48)
    add("torus", "Kabuto_Bordure_Or", (0, -0.02, 2.15), scale=(1, 0.88, 1), mat=gold,
        major_radius=0.88, minor_radius=0.018)
    # Fukigaeshi (ailes latérales)
    for s, x, a in (("G", -0.8, -25), ("D", 0.8, 25)):
        add("cube", f"Kabuto_Aile_{s}", (x, -0.15, 2.22), scale=(0.1, 0.5, 0.34),
            rot=(0, rad(a), 0), mat=red, bevel=0.03, size=1)
    # Shikoro (protège-nuque en lamelles)
    for i, (z, w) in enumerate(((2.0, 1.25), (1.84, 1.35), (1.68, 1.45))):
        add("cube", f"Shikoro_{i}", (0, 0.68, z), scale=(w, 0.1, 0.18),
            mat=(red if i % 2 == 0 else black), bevel=0.02, size=1)
    # Maedate : losange + cornes dorées
    add("cube", "Maedate_Losange", (0, -0.62, 2.62), scale=(0.22, 0.04, 0.22),
        rot=(0, rad(45), 0), mat=gold, bevel=0.01, size=1)
    for s, x, a in (("G", -0.28, -28), ("D", 0.28, 28)):
        add("cone", f"Corne_{s}", (x, -0.5, 3.0), rot=(0, rad(a), 0), mat=gold,
            radius1=0.06, radius2=0.0, depth=0.75, vertices=16)

    # ---------- Sashimono (bannière dans le dos) ----------
    add("cube", "Banniere_Support", (0.4, 0.55, 1.1), scale=(0.06, 0.6, 0.06),
        mat=wood, smooth=False, size=1)
    add("cylinder", "Banniere_Mat", (0.4, 0.85, 2.1), mat=wood,
        radius=0.025, depth=2.2, vertices=16)
    add("cube", "Banniere_Drapeau", (0.7, 0.85, 2.65), scale=(0.55, 0.02, 1.0),
        mat=red, smooth=False, size=1)
    add("cylinder", "Banniere_Disque_Or", (0.7, 0.835, 2.65), rot=(rad(90), 0, 0),
        mat=gold, radius=0.17, depth=0.03, vertices=32)
    add("cylinder", "Banniere_Disque_Noir", (0.7, 0.82, 2.65), rot=(rad(90), 0, 0),
        mat=black, radius=0.09, depth=0.035, vertices=32)

    # ---------- Caméra ----------
    scene = bpy.context.scene
    bpy.ops.object.camera_add(location=(0, -10, 1.7), rotation=(rad(90), 0, 0))
    scene.camera = bpy.context.active_object
    scene.camera.data.lens = 50

    # ---------- Lumières studio ----------
    lamp("Cle_Chaude", (-3, -5, 4), (1.0, 0.85, 0.7), 450, 4)
    lamp("Contre_Rouge", (-4, 3, 3), (1.0, 0.15, 0.1), 700, 3)
    lamp("Contre_Froid", (4, 3, 3), (0.5, 0.7, 1.0), 700, 3)
    lamp("Remplissage", (3, -4, 1), (1.0, 1.0, 1.0), 120, 4)

    # ---------- Monde + rendu ----------
    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs['Color'].default_value = (0.03, 0.012, 0.012, 1)

    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 128
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1080
    scene.render.resolution_y = 1350

    print("Samouraï Pop généré avec succès !")


create_samurai_pop()