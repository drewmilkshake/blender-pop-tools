import bpy
import math
from mathutils import Vector

# =====================================================
#  Figurine Pop style GLADIATEUR (socle sable)
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


def create_gladiator_pop():
    clear_scene()
    rad = math.radians

    # ---------- Matériaux ----------
    skin = vinyl("Vinyl_Peau", (0.8, 0.55, 0.38), 0.3)
    bronze = vinyl("Bronze", (0.8, 0.48, 0.15), 0.3, metal=1.0)
    gold = vinyl("Or", (1.0, 0.75, 0.2), 0.25, metal=1.0)
    steel = vinyl("Acier", (0.85, 0.88, 0.93), 0.12, metal=1.0)
    leather = vinyl("Cuir", (0.25, 0.1, 0.04), 0.5)
    dark_l = vinyl("Cuir_Sombre", (0.08, 0.04, 0.02), 0.5)
    red = vinyl("Rouge_Romain", (0.6, 0.03, 0.03), 0.35)
    brown = vinyl("Barbe", (0.12, 0.06, 0.03), 0.6)
    black = vinyl("Noir", (0.02, 0.02, 0.02), 0.25)
    shine = vinyl("Reflet", (1.0, 1.0, 1.0), 0.1)
    eye_m = vinyl("Oeil", (0.0, 0.0, 0.0), 0.05)
    sand = vinyl("Sable", (0.62, 0.46, 0.26), 0.8)

    # ---------- Socle d'arène ----------
    add("cylinder", "Socle_Sable", (0, 0, 0.05), mat=sand, bevel=0.03,
        radius=0.9, depth=0.1, vertices=48)
    add("torus", "Socle_Anneau_Bronze", (0, 0, 0.11), mat=bronze,
        major_radius=0.82, minor_radius=0.025)
    add("torus", "Socle_Anneau_Rouge", (0, 0, 0.11), mat=red,
        major_radius=0.7, minor_radius=0.018)

    # ---------- Jambes + jambières + sandales ----------
    for s, x in (("G", -0.22), ("D", 0.22)):
        add("cylinder", f"Jambe_{s}", (x, 0, 0.4), mat=skin, bevel=0.04,
            radius=0.17, depth=0.56, vertices=32)
        add("cylinder", f"Jambiere_{s}", (x, 0, 0.3), mat=bronze, bevel=0.02,
            radius=0.2, depth=0.3, vertices=32)
        add("cube", f"Pied_{s}", (x, -0.07, 0.21), scale=(0.3, 0.5, 0.12),
            mat=skin, bevel=0.04, size=1)
        add("cube", f"Semelle_{s}", (x, -0.07, 0.125), scale=(0.36, 0.52, 0.05),
            mat=leather, bevel=0.012, size=1)
        for j, y in enumerate((-0.2, -0.02)):
            add("cube", f"Lanière_{s}{j}", (x, y, 0.28), scale=(0.33, 0.06, 0.03),
                mat=leather, smooth=False, size=1)

    # ---------- Corps : torse nu musclé ----------
    add("cube", "Torse", (0, 0, 1.0), scale=(0.9, 0.6, 0.75), mat=skin,
        bevel=0.12, size=1)
    for s, x in (("G", -0.2), ("D", 0.2)):
        add("uv_sphere", f"Pec_{s}", (x, -0.28, 1.15), scale=(0.2, 0.09, 0.15), mat=skin,
            radius=1, segments=24, ring_count=12)
        for j, z in enumerate((0.98, 0.84)):
            add("uv_sphere", f"Abdo_{s}{j}", (x * 0.5, -0.31, z), scale=(0.1, 0.04, 0.06),
                mat=skin, radius=1, segments=16, ring_count=8)

    # Harnais de cuir croisé + médaillon
    add("cube", "Harnais_A", (0, 0, 1.0), scale=(0.1, 0.64, 0.85), rot=(0, rad(35), 0),
        mat=leather, smooth=False, size=1)
    add("cube", "Harnais_B", (0, 0, 1.0), scale=(0.1, 0.64, 0.85), rot=(0, rad(-35), 0),
        mat=leather, smooth=False, size=1)
    add("cylinder", "Medaillon", (0, -0.335, 1.0), rot=(rad(90), 0, 0), mat=bronze,
        radius=0.09, depth=0.04, vertices=32)

    # Ceinturon (balteus) + boucle
    add("cube", "Ceinturon", (0, 0, 0.7), scale=(0.93, 0.63, 0.1), mat=leather,
        bevel=0.02, size=1)
    add("cube", "Boucle", (0, -0.33, 0.7), scale=(0.2, 0.04, 0.13), mat=bronze,
        bevel=0.012, size=1)

    # Pagne rouge + lanières de cuir (pteruges)
    add("cube", "Subligaculum", (0, 0, 0.5), scale=(0.88, 0.58, 0.3), mat=red,
        bevel=0.06, size=1)
    for i in range(7):
        x = -0.36 + 0.12 * i
        yf = -0.31 + 0.1 * (abs(x) / 0.36) ** 2
        yb = 0.31 - 0.1 * (abs(x) / 0.36) ** 2
        for side, y in (("Av", yf), ("Ar", yb)):
            m = leather if i % 2 == 0 else dark_l
            add("cube", f"Pteruge_{side}{i}", (x, y, 0.5), scale=(0.115, 0.04, 0.3),
                mat=m, bevel=0.012, size=1)
        add("uv_sphere", f"Clou_{i}", (x, yf - 0.025, 0.6), mat=bronze,
            radius=0.022, segments=12, ring_count=6)
    for i, y in enumerate((-0.18, 0.0, 0.18)):
        for s, x in (("G", -0.46), ("D", 0.46)):
            add("cube", f"Pteruge_Cote_{s}{i}", (x, y, 0.5), scale=(0.04, 0.115, 0.3),
                mat=(leather if i % 2 == 0 else dark_l), bevel=0.012, size=1)

    # ---------- Épaule gauche : galerus bronze ----------
    add("cube", "Galerus", (-0.6, 0, 1.4), scale=(0.44, 0.5, 0.14), rot=(0, rad(-20), 0),
        mat=bronze, bevel=0.04, size=1)
    add("cube", "Galerus_Aile", (-0.42, 0, 1.58), scale=(0.05, 0.5, 0.28),
        rot=(0, rad(-12), 0), mat=bronze, bevel=0.015, size=1)

    # ---------- Bras gauche : manica + bouclier ----------
    add("uv_sphere", "Bras_G", (-0.62, 0, 1.05), scale=(0.17, 0.17, 0.33), mat=skin,
        radius=1, segments=32, ring_count=16)
    add("cylinder", "Manica_G", (-0.62, 0, 0.92), mat=bronze, bevel=0.03,
        radius=0.2, depth=0.5, vertices=32)
    for i, z in enumerate((0.8, 1.02)):
        add("torus", f"Manica_Sangle_{i}", (-0.62, 0, z), mat=leather,
            major_radius=0.205, minor_radius=0.015)
    # Avant-bras vers le bouclier + main
    add("cylinder", "Avant_Bras_G", (-0.66, -0.15, 0.85), rot=(rad(90), 0, 0), mat=skin,
        radius=0.1, depth=0.35, vertices=24)
    add("uv_sphere", "Main_G", (-0.66, -0.33, 0.85), mat=skin,
        radius=0.11, segments=24, ring_count=12)

    # Bouclier rectangulaire (scutum)
    sc = (-0.98, -0.40, 0.98)
    add("cube", "Bouclier", sc, scale=(0.65, 0.1, 1.1), mat=red, bevel=0.03, size=1)
    add("cube", "Bouclier_Cadre_Haut", (sc[0], sc[1], sc[2] + 0.55), scale=(0.7, 0.12, 0.06),
        mat=bronze, smooth=False, size=1)
    add("cube", "Bouclier_Cadre_Bas", (sc[0], sc[1], sc[2] - 0.55), scale=(0.7, 0.12, 0.06),
        mat=bronze, smooth=False, size=1)
    add("cube", "Bouclier_Cadre_G", (sc[0] - 0.325, sc[1], sc[2]), scale=(0.06, 0.12, 1.16),
        mat=bronze, smooth=False, size=1)
    add("cube", "Bouclier_Cadre_D", (sc[0] + 0.325, sc[1], sc[2]), scale=(0.06, 0.12, 1.16),
        mat=bronze, smooth=False, size=1)
    add("cube", "Bouclier_Croix_V", (sc[0], sc[1] - 0.005, sc[2]), scale=(0.1, 0.11, 0.8),
        mat=gold, smooth=False, size=1)
    add("cube", "Bouclier_Croix_H", (sc[0], sc[1] - 0.005, sc[2]), scale=(0.45, 0.11, 0.1),
        mat=gold, smooth=False, size=1)
    add("uv_sphere", "Bouclier_Ombon", (sc[0], sc[1] - 0.06, sc[2]), scale=(1, 0.5, 1),
        mat=bronze, radius=0.13, segments=32, ring_count=16)

    # ---------- Bras droit + gladius ----------
    add("uv_sphere", "Bras_D", (0.62, 0, 1.05), scale=(0.17, 0.17, 0.33), mat=skin,
        radius=1, segments=32, ring_count=16)
    add("cylinder", "Bracelet_Cuir", (0.62, 0, 0.84), mat=leather, bevel=0.02,
        radius=0.18, depth=0.15, vertices=32)
    add("torus", "Bracelet_Bronze", (0.62, 0, 0.94), mat=bronze,
        major_radius=0.18, minor_radius=0.025)
    H = Vector((0.66, -0.12, 0.74))
    add("uv_sphere", "Main_D", tuple(H), mat=skin, radius=0.11, segments=24, ring_count=12)

    tilt = (0, rad(20), 0)
    d = Vector((math.sin(rad(20)), 0, math.cos(rad(20))))
    add("cube", "Gladius_Manche", tuple(H), scale=(0.05, 0.05, 0.3), rot=tilt,
        mat=dark_l, bevel=0.01, size=1)
    add("uv_sphere", "Gladius_Pommeau", tuple(H - d * 0.17), mat=bronze,
        radius=0.06, segments=16, ring_count=8)
    add("cube", "Gladius_Garde", tuple(H + d * 0.17), scale=(0.22, 0.08, 0.04), rot=tilt,
        mat=bronze, bevel=0.01, size=1)
    add("cube", "Gladius_Lame", tuple(H + d * 0.615), scale=(0.13, 0.025, 0.85), rot=tilt,
        mat=steel, smooth=False, size=1)
    add("cone", "Gladius_Pointe", tuple(H + d * 1.15), scale=(1, 0.2, 1), rot=tilt,
        mat=steel, radius1=0.065, radius2=0.0, depth=0.22, vertices=24)

    # ---------- Tête ----------
    add("cube", "Tete", (0, 0, 1.92), scale=(1.5, 1.3, 1.25), mat=skin,
        bevel=0.35, size=1)
    for s, x in (("G", -0.3), ("D", 0.3)):
        add("uv_sphere", f"Oeil_{s}", (x, -0.65, 1.88), scale=(1, 0.5, 1), mat=eye_m,
            radius=0.09, segments=24, ring_count=12)
        add("uv_sphere", f"Oeil_Reflet_{s}", (x - 0.03, -0.69, 1.92), scale=(1, 0.5, 1),
            mat=shine, radius=0.025, segments=12, ring_count=6)
    # Sourcils épais et féroces
    add("cube", "Sourcil_G", (-0.3, -0.66, 2.02), scale=(0.25, 0.05, 0.07),
        rot=(0, rad(18), 0), mat=black, bevel=0.015, size=1)
    add("cube", "Sourcil_D", (0.3, -0.66, 2.02), scale=(0.25, 0.05, 0.07),
        rot=(0, rad(-18), 0), mat=black, bevel=0.015, size=1)
    # Barbe + moustache
    add("uv_sphere", "Barbe", (0, -0.5, 1.45), scale=(0.5, 0.15, 0.25), mat=brown,
        radius=1, segments=32, ring_count=16)
    for s, x, a in (("G", -0.12, 12), ("D", 0.12, -12)):
        add("cube", f"Moustache_{s}", (x, -0.64, 1.62), scale=(0.2, 0.05, 0.05),
            rot=(0, rad(a), 0), mat=brown, bevel=0.015, size=1)

    # ---------- Casque (galea) ----------
    add("uv_sphere", "Galea_Dome", (0, 0, 2.3), scale=(0.85, 0.75, 0.6), mat=bronze,
        radius=1, segments=48, ring_count=24)
    add("cylinder", "Galea_Visiere", (0, -0.02, 2.18), scale=(1, 0.9, 1), mat=bronze,
        radius=0.86, depth=0.05, vertices=48)
    for s, x in (("G", -0.72), ("D", 0.72)):
        add("cube", f"Galea_Joue_{s}", (x, -0.15, 1.85), scale=(0.08, 0.45, 0.6),
            mat=bronze, bevel=0.025, size=1)
    # Crête + plumet rouge
    add("cube", "Galea_Crete", (0, 0, 2.88), scale=(0.12, 1.1, 0.1), mat=bronze,
        bevel=0.02, size=1)
    add("cube", "Galea_Plumet", (0, 0, 3.15), scale=(0.14, 1.0, 0.4), mat=red,
        bevel=0.04, size=1)

    # ---------- Caméra ----------
    scene = bpy.context.scene
    bpy.ops.object.camera_add(location=(0, -10, 1.7), rotation=(rad(90), 0, 0))
    scene.camera = bpy.context.active_object
    scene.camera.data.lens = 50

    # ---------- Lumières studio (soleil d'arène) ----------
    lamp("Cle_Soleil", (-3, -5, 4.5), (1.0, 0.82, 0.55), 500, 4)
    lamp("Contre_Orange", (-4, 3, 3), (1.0, 0.45, 0.1), 650, 3)
    lamp("Contre_Froid", (4, 3, 3), (0.6, 0.75, 1.0), 450, 3)
    lamp("Remplissage", (3, -4, 1), (1.0, 0.95, 0.9), 130, 4)

    # ---------- Monde + rendu ----------
    world = scene.world or bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs['Color'].default_value = (0.04, 0.025, 0.015, 1)

    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 128
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 1080
    scene.render.resolution_y = 1350

    print("Gladiateur Pop généré avec succès !")


create_gladiator_pop()