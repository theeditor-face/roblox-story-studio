"""rbxkit — free Blender kit for blocky "Roblox-look" story reels.

Original blocky hero (not the Roblox classic/noob avatar, no Roblox logo),
rigid bone rig, 12-face atlas, pose/walk/talk helpers, camera moves,
cinematic light presets, vertical render settings.

Use from a shot script run by Blender:
    blender -b -P shots/my_shot.py            (render, no window)
    blender -P shots/my_shot.py               (open and look)
In the shot script:
    import sys, os; sys.path.insert(0, "<path to this scripts folder>")
    import rbxkit as k

Works on Blender 4.2 LTS and newer (tested on 5.2 LTS).
"""
import math
import os
import random

import bpy
from mathutils import Matrix, Vector, Euler

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.normpath(os.path.join(HERE, "..", "assets"))
FACE_ATLAS = os.path.join(ASSETS, "face_atlas.png")
FACES = ["neutral", "happy", "sad", "cry", "angry", "shocked",
         "scared", "sleepy", "talk", "smirk", "blink", "creepy",
         "smile", "laugh", "nervous", "dizzy", "squeeze", "wink",
         "oh", "content", "sparkle", "sparkle_oh", "nerd", "stare"]
FACE_COLS, FACE_ROWS = 6, 4                      # must match faces.py
FACE_ALIAS = {"panic": "scared", "surprised": "shocked", "unimpressed": "sleepy",
              "relieved": "content", "glasses": "nerd", "brace": "squeeze", "deadpan": "neutral"}

# pastel set colours for the bright-toon style (style-toon.md)
PASTEL = dict(cream="#F4EAD5", butter="#F3C94C", coral="#EE6F5E", mint="#A9D8BE", teal="#4FB9AF",
              deep_teal="#2E7F7A", sky="#5C9BD8", navy="#2B3A67", lilac="#B9A5E0", pink="#F3A6B5",
              wood="#C98B5E", light_wood="#E3B98A", white="#FAFAF7", grey="#B8BEC6", charcoal="#2E3138",
              tile_a="#F1E3C6", tile_b="#E9D2A8", clinic_a="#DDEDEA", clinic_b="#BFDCD6")


# --------------------------------------------------------------------------
# scene
# --------------------------------------------------------------------------
def clean_scene():
    """Empty the file: objects, meshes, materials, actions, lights, cameras."""
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.armatures,
                 bpy.data.actions, bpy.data.lights, bpy.data.cameras,
                 bpy.data.curves):
        for b in list(coll):
            coll.remove(b)
    return bpy.context.scene


def hexcol(h, a=1.0):
    """'#RRGGBB' -> linear RGBA for Blender colour sockets."""
    h = h.lstrip("#")
    srgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb]
    return (*lin, a)


def mat(name, color, rough=0.55, metal=0.0, emit=None, emit_strength=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = hexcol(color) if isinstance(color, str) else color
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if emit:
        bsdf.inputs["Emission Color"].default_value = hexcol(emit)
        bsdf.inputs["Emission Strength"].default_value = emit_strength
    return m


def box(name, size, loc, material=None, bevel=0.0, segs=3, collection=None):
    """Axis-aligned box. size=(x,y,z) full size. bevel rounds the edges."""
    me = bpy.data.meshes.new(name)
    sx, sy, sz = (s / 2 for s in size)
    v = [(-sx, -sy, -sz), (sx, -sy, -sz), (sx, sy, -sz), (-sx, sy, -sz),
         (-sx, -sy, sz), (sx, -sy, sz), (sx, sy, sz), (-sx, sy, sz)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    me.from_pydata(v, [], f)
    me.update()
    ob = bpy.data.objects.new(name, me)
    (collection or bpy.context.scene.collection).objects.link(ob)
    ob.location = loc
    if material:
        me.materials.append(material)
    if bevel > 0:
        b = ob.modifiers.new("bevel", "BEVEL")
        b.width, b.segments, b.limit_method = bevel, segs, "NONE"
        for p in me.polygons:
            p.use_smooth = True
        try:
            me.shade_smooth_by_angle(angle=math.radians(40))
        except Exception:
            pass
    return ob


# --------------------------------------------------------------------------
# hero character
# --------------------------------------------------------------------------
HERO_DEFAULT = dict(skin="#F1C9A5", shirt="#2E5E8C", pants="#2B2B33",
                    shoes="#1A1A1E", hair="#3A2618", sleeves=True, hair_style="block")


def _face_material(name, atlas_path):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    tex = nt.nodes.new("ShaderNodeTexImage")
    mapn = nt.nodes.new("ShaderNodeMapping")
    uv = nt.nodes.new("ShaderNodeTexCoord")
    mapn.name = "FACE_MAP"
    img = bpy.data.images.load(atlas_path, check_existing=True)
    tex.image = img
    tex.interpolation = "Cubic"
    tex.extension = "CLIP"
    mapn.inputs["Scale"].default_value = (1 / FACE_COLS, 1 / FACE_ROWS, 1)
    nt.links.new(uv.outputs["UV"], mapn.inputs["Vector"])
    nt.links.new(mapn.outputs["Vector"], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
    bsdf.inputs["Roughness"].default_value = 0.6
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    for attr, val in (("blend_method", "HASHED"), ("surface_render_method", "DITHERED")):
        try:
            setattr(m, attr, val)
        except Exception:
            pass
    return m


def make_hero(name="Hero", at=(0, 0, 0), facing=0.0, atlas=None, **style):
    """Build an original blocky character and return its armature object.

    Size: about 5.3 units tall (1 unit ~ 1 Roblox stud). Facing 0 = looks
    toward -Y (toward a camera placed at -Y). Colours: skin, shirt, pants,
    shoes, hair (hex). hair_style: "block", "spiky", "none".
    """
    s = dict(HERO_DEFAULT, **style)
    coll = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(coll)

    arm_data = bpy.data.armatures.new(name + "_rig")
    rig = bpy.data.objects.new(name, arm_data)
    coll.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm_data.edit_bones

    def bone(n, head, tail, parent=None):
        b = eb.new(n)
        b.head, b.tail = head, tail
        b.roll = 0
        if parent:
            b.parent = eb[parent]
        return b

    bone("root", (0, 0, 0), (0, 0.8, 0))
    bone("hips", (0, 0, 2.0), (0, 0, 2.3), "root")
    bone("torso", (0, 0, 2.0), (0, 0, 4.0), "hips")
    bone("head", (0, 0, 4.0), (0, 0, 5.3), "torso")
    bone("arm.L", (1.5, 0, 3.75), (1.5, 0, 2.0), "torso")
    bone("arm.R", (-1.5, 0, 3.75), (-1.5, 0, 2.0), "torso")
    bone("leg.L", (0.5, 0, 2.0), (0.5, 0, 0.0), "hips")
    bone("leg.R", (-0.5, 0, 2.0), (-0.5, 0, 0.0), "hips")
    bpy.ops.object.mode_set(mode="OBJECT")

    m_skin = mat(name + "_skin", s["skin"], 0.5)
    m_shirt = mat(name + "_shirt", s["shirt"], 0.7)
    m_pants = mat(name + "_pants", s["pants"], 0.75)
    m_shoes = mat(name + "_shoes", s["shoes"], 0.6)
    m_hair = mat(name + "_hair", s["hair"], 0.65)

    parts = []

    def part(pname, size, loc, m, bone_name, bevel=0.08):
        ob = box(f"{name}_{pname}", size, loc, m, bevel, collection=coll)
        parts.append((ob, bone_name))
        return ob

    part("torso", (2.0, 1.0, 2.0), (0, 0, 3.0), m_shirt, "torso")
    part("head", (1.25, 1.2, 1.2), (0, 0, 4.62), m_skin, "head", bevel=0.28)
    part("neck", (0.5, 0.5, 0.2), (0, 0, 4.05), m_skin, "head", bevel=0.04)
    arm_mat = m_shirt if s["sleeves"] else m_skin
    for side, x in (("L", 1.5), ("R", -1.5)):
        part(f"arm.{side}", (0.95, 0.95, 1.35), (x, 0, 3.12), arm_mat, f"arm.{side}")
        part(f"hand.{side}", (0.93, 0.93, 0.6), (x, 0, 2.27), m_skin, f"arm.{side}")
        part(f"leg.{side}", (0.97, 0.97, 1.65), (x / 3, 0, 1.18), m_pants, f"leg.{side}")
        part(f"shoe.{side}", (0.99, 1.05, 0.38), (x / 3, -0.03, 0.19), m_shoes, f"leg.{side}")
    if s["hair_style"] == "block":
        part("hair_top", (1.38, 1.3, 0.38), (0, 0.04, 5.25), m_hair, "head", bevel=0.14)
        part("hair_back", (1.38, 0.35, 0.95), (0, 0.5, 4.85), m_hair, "head", bevel=0.12)
        sw = part("swoop", (0.8, 0.28, 0.3), (0.22, -0.55, 5.12), m_hair, "head", bevel=0.1)
        sw.rotation_euler = (0, math.radians(-12), 0)
    elif s["hair_style"] == "fluffy":            # messy curls: many soft tufts (toon style)
        rnd = random.Random(sum(map(ord, name)))
        part("hair_top", (1.34, 1.26, 0.34), (0, 0.05, 5.22), m_hair, "head", bevel=0.14)
        part("hair_back", (1.36, 0.4, 0.9), (0, 0.48, 4.9), m_hair, "head", bevel=0.14)
        spots = [(x, y, 5.36 + 0.1 * (1 - abs(x))) for x in (-0.5, -0.17, 0.17, 0.5) for y in (-0.42, -0.05, 0.35)]
        spots += [(x, -0.6, 5.12) for x in (-0.48, -0.16, 0.16, 0.48)]            # fringe
        spots += [(sx * 0.7, y, 4.95) for sx in (-1, 1) for y in (-0.2, 0.25)]     # sides
        for i, (x, y, z) in enumerate(spots):
            t = part(f"tuft{i}", (0.46, 0.46, 0.4), (x + rnd.uniform(-0.05, 0.05), y, z + rnd.uniform(-0.04, 0.06)),
                     m_hair, "head", bevel=0.18)
            t.rotation_euler = tuple(math.radians(rnd.uniform(-28, 28)) for _ in range(3))
    elif s["hair_style"] == "long":              # long straight hair with bangs
        part("hair_top", (1.42, 1.34, 0.4), (0, 0.04, 5.26), m_hair, "head", bevel=0.16)
        part("hair_back", (1.46, 0.42, 2.3), (0, 0.52, 4.2), m_hair, "torso", bevel=0.16)
        for sx in (-1, 1):
            part(f"hair_side{sx}", (0.26, 0.9, 1.9), (sx * 0.72, 0.1, 4.3), m_hair, "torso", bevel=0.1)
        for i, x in enumerate((-0.44, -0.15, 0.15, 0.44)):
            bang = part(f"bang{i}", (0.3, 0.2, 0.42), (x, -0.6, 5.02), m_hair, "head", bevel=0.08)
            bang.rotation_euler = (0, math.radians(x * 18), 0)
    elif s["hair_style"] == "bob":               # short bob with side flaps
        part("hair_top", (1.42, 1.34, 0.42), (0, 0.04, 5.26), m_hair, "head", bevel=0.16)
        part("hair_back", (1.44, 0.4, 1.05), (0, 0.5, 4.8), m_hair, "head", bevel=0.14)
        for sx in (-1, 1):
            fl = part(f"hair_side{sx}", (0.3, 1.0, 0.95), (sx * 0.72, 0.05, 4.72), m_hair, "head", bevel=0.12)
            fl.rotation_euler = (0, math.radians(sx * 10), 0)
        sw = part("swoop", (1.0, 0.24, 0.3), (0.12, -0.58, 5.12), m_hair, "head", bevel=0.1)
        sw.rotation_euler = (0, math.radians(-10), 0)
    elif s["hair_style"] == "spiky":
        part("hair_top", (1.36, 1.28, 0.3), (0, 0.04, 5.22), m_hair, "head", bevel=0.1)
        for i, x in enumerate((-0.42, 0, 0.42)):
            sp = part(f"spike{i}", (0.42, 0.9, 0.5), (x, 0.1, 5.45), m_hair, "head", bevel=0.1)
            sp.rotation_euler = (math.radians(-15), math.radians(x * 30), 0)

    # face decal: a plane just in front of the head
    fm = _face_material(name + "_face", atlas or FACE_ATLAS)
    me = bpy.data.meshes.new(name + "_face")
    w, h = 1.05, 1.0
    me.from_pydata([(-w / 2, 0, -h / 2), (w / 2, 0, -h / 2), (w / 2, 0, h / 2), (-w / 2, 0, h / 2)],
                   [], [(0, 1, 2, 3)])
    uvl = me.uv_layers.new()
    for li, uvc in zip(range(4), [(0, 0), (1, 0), (1, 1), (0, 1)]):
        uvl.data[li].uv = uvc
    me.materials.append(fm)
    face = bpy.data.objects.new(name + "_face", me)
    coll.objects.link(face)
    face.location = (0, -0.612, 4.6)
    parts.append((face, "head"))

    # rigid-parent every part to its bone (no weight painting needed)
    for ob, bname in parts:
        b = arm_data.bones[bname]
        basis = ob.matrix_basis.copy()           # world placement (no parent yet)
        ob.parent = rig
        ob.parent_type = "BONE"
        ob.parent_bone = bname
        ob.matrix_parent_inverse = (rig.matrix_world @ b.matrix_local @
                                    Matrix.Translation((0, b.length, 0))).inverted()
        ob.matrix_basis = basis

    rig.location = at
    rig.rotation_euler = (0, 0, math.radians(facing))
    for pb in rig.pose.bones:                   # limbs: forward, then out, then across
        pb.rotation_mode = "XZY" if pb.name.startswith(("arm", "leg")) else "XYZ"
    rig["face_material"] = fm.name
    arm_data.display_type = "STICK"
    rig.show_in_front = True
    set_face(rig, 0, "neutral", key=True)
    return rig


# --------------------------------------------------------------------------
# keyframing helpers (Blender 4.x and 5.x action APIs)
# --------------------------------------------------------------------------
def fcurves_of(id_block):
    ad = getattr(id_block, "animation_data", None)
    if not ad or not ad.action:
        return []
    act = ad.action
    try:                                         # Blender 4.4+ slotted actions
        out = []
        for layer in act.layers:
            for strip in layer.strips:
                cb = strip.channelbag(ad.action_slot)
                if cb:
                    out.extend(cb.fcurves)
        if out:
            return out
    except Exception:
        pass
    return list(getattr(act, "fcurves", []))


def set_interp(id_block, kind="BEZIER", path_contains=None):
    for fc in fcurves_of(id_block):
        if path_contains and path_contains not in fc.data_path:
            continue
        for kp in fc.keyframe_points:
            kp.interpolation = kind


def ease_all(id_block, easing="AUTO"):
    for fc in fcurves_of(id_block):
        for kp in fc.keyframe_points:
            kp.easing = easing


# --------------------------------------------------------------------------
# faces
# --------------------------------------------------------------------------
def set_face(rig, frame, name, key=True):
    """Swap expression at a frame (hard cut). name in FACES or an int index."""
    idx = FACES.index(FACE_ALIAS.get(name, name)) if isinstance(name, str) else int(name)
    col, row = idx % FACE_COLS, idx // FACE_COLS
    m = bpy.data.materials[rig["face_material"]]
    mp = m.node_tree.nodes["FACE_MAP"]
    mp.inputs["Location"].default_value = (col / FACE_COLS, (FACE_ROWS - 1 - row) / FACE_ROWS, 0)
    if key:
        mp.inputs["Location"].keyframe_insert("default_value", frame=frame)
        set_interp(m.node_tree, "CONSTANT")


# --------------------------------------------------------------------------
# posing
# --------------------------------------------------------------------------
# Angles in degrees, same meaning on both sides of the body:
#   arms / legs : (forward, across, out)  forward + = swing to the front,
#                 across + = swing in toward the chest (after forward),
#                 out + = away from the body / up to the side
#   head / torso: (nod, turn, tilt)       nod + = look down / lean forward,
#                 turn + = turn to its left, tilt + = lean to its right
def _to_bone(bn, v):
    a, b, c = v
    if bn.startswith(("arm", "leg")):
        side = -1 if bn.endswith(".L") else 1
        return (-a, -b * side, c * side)
    return (a, b, c)


def pose(rig, frame, key=True, **bones):
    """pose(rig, 10, arm_R=(85,0,0), head=(10,20,0)). Write arm.L as arm_L."""
    for k, v in bones.items():
        bn = k.replace("_L", ".L").replace("_R", ".R")
        pb = rig.pose.bones[bn]
        pb.rotation_euler = Euler([math.radians(x) for x in _to_bone(bn, v)], pb.rotation_mode)
        if key:
            pb.keyframe_insert("rotation_euler", frame=frame)


def move(rig, frame, loc=None, turn=None, lift=None):
    """Key the whole character: loc=(x,y,z) world, turn=degrees, lift=hip bounce."""
    if loc is not None:
        rig.location = loc
        rig.keyframe_insert("location", frame=frame)
    if turn is not None:
        rig.rotation_euler.z = math.radians(turn)
        rig.keyframe_insert("rotation_euler", index=2, frame=frame)
    if lift is not None:
        pb = rig.pose.bones["hips"]
        pb.location = (0, lift, 0)               # bone Y = world up for hips
        pb.keyframe_insert("location", frame=frame)


POSES = {
    "rest":      dict(arm_L=(0, 0, 0), arm_R=(0, 0, 0), leg_L=(0, 0, 0), leg_R=(0, 0, 0),
                      head=(0, 0, 0), torso=(0, 0, 0)),
    "arms_out":  dict(arm_L=(0, 0, 80), arm_R=(0, 0, 80)),
    "point":     dict(arm_R=(85, 0, 0)),
    "wave":      dict(arm_R=(0, 0, 150)),
    "think":     dict(arm_R=(100, 45, 0), head=(-8, 0, 6)),
    "facepalm":  dict(arm_R=(118, 50, 0), head=(18, 0, 0)),
    "hug_self":  dict(arm_L=(70, 55, 0), arm_R=(70, 55, 0), head=(15, 0, 0)),
    "shrug":     dict(arm_L=(25, 0, 30), arm_R=(25, 0, 30), head=(0, 0, 12)),
    "hands_up":  dict(arm_L=(0, 0, 165), arm_R=(0, 0, 165)),
    "sad":       dict(head=(25, 0, 0), torso=(8, 0, 0), arm_L=(-4, 0, 2), arm_R=(-4, 0, 2)),
    "sit":       dict(leg_L=(90, 0, 0), leg_R=(90, 0, 0), arm_L=(30, 0, 0), arm_R=(30, 0, 0)),
    "run_ready": dict(torso=(15, 0, 0), arm_L=(-30, 0, 0), arm_R=(40, 0, 0)),
    "cover_face": dict(arm_L=(118, 33, 0), arm_R=(118, 33, 0), head=(15, 0, 0)),
    "reach":     dict(arm_L=(80, 0, 10), arm_R=(80, 0, 10), torso=(10, 0, 0)),
}


def hold(rig, frame, name, **extra):
    """Key a named pose (from POSES) plus any extra bone angles."""
    p = dict(POSES[name])
    p.update(extra)
    pose(rig, frame, **p)


# --------------------------------------------------------------------------
# moves (all keyframe based, editable later in the Graph Editor)
# --------------------------------------------------------------------------
def idle(rig, start, end, amount=1.0, seed=0):
    """Breathing + small head drift so a still character never looks frozen."""
    rnd = random.Random(seed)
    f = start
    while f <= end:
        a = amount * (1 if ((f - start) // 30) % 2 == 0 else -1)
        pose(rig, f, torso=(1.5 * a, 0, 0),
             head=(rnd.uniform(-3, 3) * amount, rnd.uniform(-2, 2) * amount, rnd.uniform(-5, 5) * amount),
             arm_L=(0, 0, 2 + 2 * a), arm_R=(0, 0, 2 + 2 * a))
        f += 30


def blink(rig, frame, face_after="neutral"):
    set_face(rig, frame, "blink")
    set_face(rig, frame + 3, face_after)


def talk(rig, start, end, base="neutral", rate=5, seed=1, nod=4):
    """Mouth flaps (talk/base faces) + head nods. rate = frames per mouth shape."""
    rnd = random.Random(seed)
    f = start
    open_ = True
    while f < end:
        set_face(rig, f, "talk" if open_ else base)
        open_ = not open_
        f += rate + rnd.choice((0, 0, 1, 2))
    set_face(rig, end, base)
    f = start
    while f <= end:
        pose(rig, f, head=(rnd.uniform(-nod, nod), rnd.uniform(-2, 2), rnd.uniform(-nod, nod)))
        f += 12


def walk(rig, start, end, to, stride_frames=16, swing=35, run=False):
    """Walk from the current location to `to` (x,y,z) between start and end.
    Faces the walk direction. run=True: bigger swing, lean, hip bounce."""
    frm = Vector(rig.location)
    to = Vector(to)
    d = to - frm
    heading = math.degrees(math.atan2(d.x, -d.y))       # 0 = toward -Y
    move(rig, start, loc=frm, turn=heading)
    move(rig, end, loc=to)
    if run:
        swing, stride_frames = swing * 1.6, int(stride_frames * 0.6)
    lean = 14 if run else 3
    f, s = start, 1
    while f <= end:
        pose(rig, f, leg_L=(swing * s, 0, 0), leg_R=(-swing * s, 0, 0),
             arm_L=(-swing * s * 0.9, 0, 0), arm_R=(swing * s * 0.9, 0, 0), torso=(lean, 0, 0))
        move(rig, f, lift=0.0)
        mid = f + stride_frames // 2
        if mid <= end:
            pose(rig, mid, leg_L=(0, 0, 0), leg_R=(0, 0, 0), arm_L=(0, 0, 0), arm_R=(0, 0, 0))
            move(rig, mid, lift=0.18 if run else 0.08)
        f += stride_frames
        s = -s
    hold(rig, end + 4, "rest")
    move(rig, end + 4, lift=0.0)
    set_interp(rig, "LINEAR", "location")              # steady travel speed


def turn_to(rig, frame, degrees, frames=8):
    move(rig, frame, turn=math.degrees(rig.rotation_euler.z))
    move(rig, frame + frames, turn=degrees)


def recoil(rig, frame, face="shocked"):
    """Jump-scare reaction: snap back, arms up, face swap on the same frame."""
    set_face(rig, frame, face)
    pose(rig, frame, torso=(0, 0, 0), head=(0, 0, 0), arm_L=(0, 0, 0), arm_R=(0, 0, 0))
    pose(rig, frame + 3, torso=(-14, 0, 0), head=(-12, 0, 0), arm_L=(60, 0, 40), arm_R=(60, 0, 40))
    move(rig, frame, lift=0.0)
    move(rig, frame + 3, lift=0.25)
    move(rig, frame + 9, lift=0.0)
    pose(rig, frame + 14, torso=(-6, 0, 0), head=(-5, 0, 0), arm_L=(45, 0, 30), arm_R=(45, 0, 30))


def shake(rig, start, end, bone="torso", amp=3.0, every=2, seed=3):
    """Crying / shivering / laughing tremble on one bone."""
    rnd = random.Random(seed)
    for f in range(start, end + 1, every):
        pose(rig, f, **{bone.replace(".", "_"): (rnd.uniform(-amp, amp), rnd.uniform(-amp, amp), 0)})


# --------------------------------------------------------------------------
# cameras
# --------------------------------------------------------------------------
def camera(name, loc, look_at, lens=50, dof_target=None, fstop=2.0):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.sensor_width = 36
    cam = bpy.data.objects.new(name, cd)
    bpy.context.scene.collection.objects.link(cam)
    cam.location = loc
    aim(cam, look_at)
    if dof_target is not None:
        cd.dof.use_dof = True
        cd.dof.aperture_fstop = fstop
        if isinstance(dof_target, bpy.types.Object):
            cd.dof.focus_object = dof_target
        else:
            cd.dof.focus_distance = (Vector(loc) - Vector(dof_target)).length
    if bpy.context.scene.camera is None:
        bpy.context.scene.camera = cam
    return cam


def aim(ob, target):
    d = Vector(target) - Vector(ob.location)
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def head_target(rig, z_off=0.0):
    """World point at the hero's eyes (for aim / focus)."""
    bpy.context.view_layer.update()              # matrix_world is stale right after make_hero / move
    return rig.matrix_world @ Vector((0, 0, 4.65 + z_off))


def face_cam(name, rig, dist=3.6, height=-0.2, side=0.0, lens=32, look_z=-0.15):
    """Camera straight in front of a character's face (the toon-style close-up: wide lens, close,
    a little below eye level). dist 3-4 = close-up, 5-6 = medium close-up. side shifts it left/right."""
    bpy.context.view_layer.update()
    eye = rig.matrix_world @ Vector((0, 0, 4.65))
    rot = rig.matrix_world.to_3x3()
    fwd = (rot @ Vector((0, -1, 0))).normalized()
    right = (rot @ Vector((1, 0, 0))).normalized()
    loc = eye + fwd * dist + right * side + Vector((0, 0, height))
    return camera(name, tuple(loc), tuple(eye + Vector((0, 0, look_z))), lens=lens)


def push_in(cam, start, end, amount=1.5, lens_to=None):
    """Slow dolly forward along view direction (the refs' main move)."""
    fwd = cam.rotation_euler.to_quaternion() @ Vector((0, 0, -1))
    cam.keyframe_insert("location", frame=start)
    cam.location = Vector(cam.location) + fwd * amount
    cam.keyframe_insert("location", frame=end)
    if lens_to:
        cam.data.keyframe_insert("lens", frame=start)
        cam.data.lens = lens_to
        cam.data.keyframe_insert("lens", frame=end)
    for fc in fcurves_of(cam):
        for kp in fc.keyframe_points:
            kp.interpolation = "SINE"
            kp.easing = "EASE_IN_OUT"


def handheld(cam, strength=0.02, speed=20.0):
    """Subtle noise on rotation (handheld feel). Works on top of keyframes."""
    if not (cam.animation_data and cam.animation_data.action):
        cam.keyframe_insert("rotation_euler", frame=1)
    for fc in fcurves_of(cam):
        if fc.data_path == "rotation_euler":
            mod = fc.modifiers.new("NOISE")
            mod.strength = strength
            mod.scale = speed
            mod.phase = random.uniform(0, 100)
    have = {fc.array_index for fc in fcurves_of(cam) if fc.data_path == "rotation_euler"}
    for i in {0, 1, 2} - have:
        cam.keyframe_insert("rotation_euler", index=i, frame=1)
    for fc in fcurves_of(cam):
        if fc.data_path == "rotation_euler" and not fc.modifiers:
            mod = fc.modifiers.new("NOISE")
            mod.strength, mod.scale, mod.phase = strength, speed, random.uniform(0, 100)


def cut_to(cam, frame):
    """Multi-camera edit inside one file: switch active camera at `frame`."""
    sc = bpy.context.scene
    mk = sc.timeline_markers.new(f"cut_{cam.name}_{frame}", frame=frame)
    mk.camera = cam


# --------------------------------------------------------------------------
# lights & look presets
# --------------------------------------------------------------------------
def light(name, kind, loc, look_at=(0, 0, 3), energy=500, color="#FFFFFF", size=1.0, spot_deg=50):
    ld = bpy.data.lights.new(name, kind)
    ld.energy = energy
    ld.color = hexcol(color)[:3]
    if kind in ("AREA",):
        ld.size = size
    if kind in ("POINT", "SPOT"):
        ld.shadow_soft_size = size
    if kind == "SPOT":
        ld.spot_size = math.radians(spot_deg)
        ld.spot_blend = 0.4
    ob = bpy.data.objects.new(name, ld)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    aim(ob, look_at)
    return ob


def world(color="#101318", strength=1.0, fog=0.0, fog_color="#B8C4D6", hdri=None):
    """World background + optional volumetric fog (fog 0.002-0.02 is plenty)."""
    sc = bpy.context.scene
    w = sc.world or bpy.data.worlds.new("World")
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = strength
    if hdri and os.path.exists(hdri):
        env = nt.nodes.new("ShaderNodeTexEnvironment")
        env.image = bpy.data.images.load(hdri, check_existing=True)
        nt.links.new(env.outputs["Color"], bg.inputs["Color"])
    else:
        bg.inputs["Color"].default_value = hexcol(color)
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
    if fog > 0:
        vs = nt.nodes.new("ShaderNodeVolumeScatter")
        vs.inputs["Density"].default_value = fog
        vs.inputs["Color"].default_value = hexcol(fog_color)
        nt.links.new(vs.outputs["Volume"], out.inputs["Volume"])
    return w


def _bloom(strength=0.6, threshold=0.9, size=7):
    """Bloom via the compositor Glare node (Eevee's old bloom toggle is gone)."""
    sc = bpy.context.scene
    try:                                          # Blender 5.x compositor
        ng = sc.compositing_node_group
        if ng is None:
            ng = bpy.data.node_groups.new("Compositor", "CompositorNodeTree")
            sc.compositing_node_group = ng
        nodes = ng.nodes
        nodes.clear()
        rl = nodes.new("CompositorNodeRLayers")
        gl = nodes.new("CompositorNodeGlare")
        out = nodes.new("NodeGroupOutput")
        if not ng.interface.items_tree:
            ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        for nm, val in (("Type", "Bloom"), ("Quality", "High")):
            if nm in gl.inputs:
                gl.inputs[nm].default_value = val
        for nm, val in (("Threshold", threshold), ("Strength", strength), ("Size", size / 9)):
            if nm in gl.inputs:
                gl.inputs[nm].default_value = val
        ng.links.new(rl.outputs["Image"], gl.inputs["Image"])
        ng.links.new(gl.outputs["Image"], out.inputs[0])
        return True
    except AttributeError:
        pass
    sc.use_nodes = True                           # Blender 4.2-4.5
    nt = sc.node_tree
    nt.nodes.clear()
    rl = nt.nodes.new("CompositorNodeRLayers")
    gl = nt.nodes.new("CompositorNodeGlare")
    comp = nt.nodes.new("CompositorNodeComposite")
    gl.glare_type = "BLOOM" if "BLOOM" in [i.identifier for i in gl.bl_rna.properties["glare_type"].enum_items] else "FOG_GLOW"
    gl.threshold = threshold
    gl.size = size
    try:
        gl.mix = strength - 1
    except Exception:
        pass
    nt.links.new(rl.outputs["Image"], gl.inputs["Image"])
    nt.links.new(gl.outputs["Image"], comp.inputs["Image"])
    return True


LOOKS = {
    # name: world colour, fog, key (colour, energy), rim colour, fill colour, exposure, look
    "warm_interior": dict(bg="#1B140F", fog=0.004, fog_col="#FFD7A8", key=("#FFC88A", 900),
                          rim=("#8FB8FF", 500), fill=("#FF9E6B", 120), exposure=0.0, look="AgX - Medium High Contrast"),
    "school_day":    dict(bg="#AFC8E8", fog=0.002, fog_col="#E8F0FF", key=("#FFF2DD", 1100),
                          rim=("#FFFFFF", 400), fill=("#BBD4FF", 250), exposure=0.3, look="AgX - Base Contrast"),
    "night_horror":  dict(bg="#04060B", fog=0.012, fog_col="#6E86B8", key=("#7FA2FF", 650),
                          rim=("#FF3B30", 700), fill=("#1B2238", 60), exposure=-0.3, look="AgX - High Contrast"),
    "dreamy_train":  dict(bg="#1A1020", fog=0.006, fog_col="#FFB8E0", key=("#FFD9A0", 1000),
                          rim=("#FFB0F0", 800), fill=("#9A7BFF", 200), exposure=0.15, look="AgX - Medium High Contrast"),
    "sad_rain":      dict(bg="#1C232C", fog=0.009, fog_col="#9AA9BA", key=("#C9D6E6", 600),
                          rim=("#E8F0FF", 300), fill=("#4A5A70", 120), exposure=-0.1, look="AgX - Medium Low Contrast"),
}


LOOKS.update({
    # bright-toon style (style-toon.md): high key, pastel, soft shadows, no fog, no bloom
    # name: world colour + ambient strength, sun (colour, strength), fill (colour, watts), exposure
    "toon_day":   dict(toon=True, bg="#EDF3FA", amb=0.55, key=("#FFF6E8", 1.7), fill=("#E3ECFF", 90), exposure=0.0),
    "toon_warm":  dict(toon=True, bg="#F7EEDF", amb=0.52, key=("#FFEBCB", 1.6), fill=("#FFE6C8", 80), exposure=0.0),
    "toon_cool":  dict(toon=True, bg="#E4F2F0", amb=0.55, key=("#F4FFFD", 1.6), fill=("#D8F0EC", 90), exposure=0.0),
    "toon_night": dict(toon=True, bg="#2A3C6C", amb=0.6, key=("#A9BEF5", 0.9), fill=("#6D88D8", 70), exposure=0.0),
})


def _no_compositor():
    sc = bpy.context.scene
    try:
        sc.compositing_node_group = None
    except AttributeError:
        try:
            sc.use_nodes = False
        except Exception:
            pass


def _toon_look(L, subject):
    sx, sy, sz = subject
    world(L["bg"], L["amb"], 0.0)
    sun = light("LOOK_key", "SUN", (sx - 6, sy - 9, sz + 12), subject, L["key"][1], L["key"][0])
    sun.data.angle = math.radians(28)            # big sun disc = soft shadow edges
    light("LOOK_fill", "AREA", (sx + 4, sy - 9, sz + 2), subject, L["fill"][1], L["fill"][0], size=10)
    vs = bpy.context.scene.view_settings
    vs.view_transform = "Standard"                # true pastel colours (AgX greys them out)
    try:
        vs.look = "None"
    except TypeError:
        pass
    vs.exposure = L["exposure"]
    _no_compositor()


def apply_look(name, subject=(0, 0, 3), bloom=True):
    """Three-point light rig + world + fog + colour management for a mood.
    Re-run per scene; it replaces the lights it made before."""
    L = LOOKS[name]
    for ob in [o for o in bpy.data.objects if o.name.startswith("LOOK_")]:
        bpy.data.objects.remove(ob, do_unlink=True)
    if L.get("toon"):
        return _toon_look(L, subject)
    world(L["bg"], 1.0, L["fog"], L["fog_col"])
    sx, sy, sz = subject
    light("LOOK_key", "AREA", (sx - 4, sy - 5, sz + 5), subject, L["key"][1], L["key"][0], size=3)
    light("LOOK_rim", "SPOT", (sx + 3, sy + 5, sz + 4), subject, L["rim"][1], L["rim"][0], size=0.4, spot_deg=40)
    light("LOOK_fill", "AREA", (sx + 5, sy - 3, sz + 1), subject, L["fill"][1], L["fill"][0], size=5)
    vs = bpy.context.scene.view_settings
    vs.view_transform = "AgX"
    try:
        vs.look = L["look"]
    except TypeError:
        pass
    vs.exposure = L["exposure"]
    if bloom:
        _bloom()


# --------------------------------------------------------------------------
# quick sets (stand-ins until you drop in free models)
# --------------------------------------------------------------------------
def room(w=16, d=14, h=8, floor="#7A5A3E", walls="#D9CBB5", window=True):
    """Simple room open toward -Y (where the camera is)."""
    mf = mat("set_floor", floor, 0.45)
    mw = mat("set_wall", walls, 0.85)
    box("set_floor", (w, d, 0.4), (0, 0, -0.2), mf)
    box("set_wall_back", (w, 0.4, h), (0, d / 2, h / 2), mw)
    box("set_wall_L", (0.4, d, h), (-w / 2, 0, h / 2), mw)
    box("set_wall_R", (0.4, d, h), (w / 2, 0, h / 2), mw)
    if window:
        glow = mat("set_window", "#FFE7C2", 0.2, emit="#FFE7C2", emit_strength=6)
        box("set_window", (3.5, 0.1, 3), (-3, d / 2 - 0.25, 4.5), glow)
        box("set_window_bar", (0.15, 0.15, 3), (-3, d / 2 - 0.32, 4.5), mat("set_wood", "#3B2A1D", 0.6))


def checker_mat(name, a="#F1E3C6", b="#E9D2A8", tile=2.0, rough=0.6):
    """Two-colour floor tiles (tile = tile size in units). Works on any flat box."""
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    ck = nt.nodes.new("ShaderNodeTexChecker")
    mp.inputs["Location"].default_value = (0.013, 0.017, 0.37)     # keep faces off cell borders
    ck.inputs["Scale"].default_value = 1.0 / tile
    ck.inputs["Color1"].default_value = hexcol(a)
    ck.inputs["Color2"].default_value = hexcol(b)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], ck.inputs["Vector"])
    nt.links.new(ck.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = rough
    return m


def _bold_font():
    for path in ("/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf",
                 "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                 "/Library/Fonts/Arial Bold.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
        if os.path.exists(path):
            try:
                return bpy.data.fonts.load(path, check_existing=True)
            except Exception:
                pass
    return None


def text(name, body, loc, size=0.4, color="#2E3138", align="CENTER", rot_z=0.0, glow=0.0):
    """Flat text facing -Y (toward the camera side). glow > 0 keeps it readable at night."""
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body
    cu.size = size
    cu.align_x, cu.align_y = align, "CENTER"
    cu.extrude = 0.008
    f = _bold_font()
    if f:
        cu.font = f
    ob = bpy.data.objects.new(name, cu)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.rotation_euler = (math.radians(90), 0, math.radians(rot_z))
    cu.materials.append(mat(name + "_m", color, 0.6, emit=color if glow else None, emit_strength=glow))
    return ob


def sign(name, lines, loc, w=4.0, h=2.2, bg="#FAFAF7", border="#4FB9AF", colors=None, sizes=None):
    """Wall sign / poster / form: a board with centred lines of text, facing -Y.
    lines: list of strings (top to bottom). colors / sizes: one per line (optional).
    Signs carry the jokes and the world rule in this style: keep them short and readable."""
    x, y, z = loc
    box(name + "_frame", (w + 0.24, 0.08, h + 0.24), (x, y + 0.03, z), mat(name + "_b", border, 0.6), bevel=0.03)
    box(name + "_board", (w, 0.08, h), (x, y, z), mat(name + "_bg", bg, 0.7))
    n = len(lines)
    colors = colors or ["#2E3138"] * n
    sizes = sizes or [min(0.5, h / (n + 1) * 0.62)] * n
    step = h / (n + 1)
    out = []
    for i, ln in enumerate(lines):
        t = text(f"{name}_t{i}", ln, (x, y - 0.06, z + h / 2 - step * (i + 1)), size=sizes[i], color=colors[i])
        out.append(t)
    return out


def toon_room(w=18, d=14, h=9, wall="#DDEDEA", floor=("#F1E3C6", "#E9D2A8"), tile=2.0, trim="#FAFAF7",
              band=None, ceiling=True):
    """Clean pastel room open toward -Y (camera side): tiled floor, walls, white trim,
    optional colour band on the walls, drop ceiling with light panels.
    The shell casts no shadows, so the sun keeps the inside bright and even."""
    shell = []
    fl = box("set_floor", (w, d, 0.4), (0, 0, -0.2), checker_mat("set_floor_tiles", floor[0], floor[1], tile))
    mw = mat("set_wall", wall, 0.85)
    shell.append(box("set_wall_back", (w, 0.4, h), (0, d / 2, h / 2), mw))
    shell.append(box("set_wall_L", (0.4, d, h), (-w / 2, 0, h / 2), mw))
    shell.append(box("set_wall_R", (0.4, d, h), (w / 2, 0, h / 2), mw))
    mt = mat("set_trim", trim, 0.6)
    for nm, size, loc in (("back", (w, 0.1, 0.5), (0, d / 2 - 0.24, 0.25)),
                          ("L", (0.1, d, 0.5), (-w / 2 + 0.24, 0, 0.25)),
                          ("R", (0.1, d, 0.5), (w / 2 - 0.24, 0, 0.25))):
        shell.append(box("set_base_" + nm, size, loc, mt))
    if band:
        mb = mat("set_band", band, 0.7)
        shell.append(box("set_band_back", (w, 0.06, 0.6), (0, d / 2 - 0.23, h * 0.42), mb))
        shell.append(box("set_band_L", (0.06, d, 0.6), (-w / 2 + 0.23, 0, h * 0.42), mb))
        shell.append(box("set_band_R", (0.06, d, 0.6), (w / 2 - 0.23, 0, h * 0.42), mb))
    if ceiling:
        shell.append(box("set_ceiling", (w, d, 0.3), (0, 0, h + 0.15),
                         mat("set_ceil", "#F4F4F0", 0.9, emit="#F4F4F0", emit_strength=0.45)))
        mg = mat("set_ceil_grid", "#C9CFD4", 0.8)
        for i in range(1, int(w // 3)):
            shell.append(box(f"set_grid_x{i}", (0.08, d, 0.06), (-w / 2 + i * 3, 0, h - 0.02), mg))
        for j in range(1, int(d // 3)):
            shell.append(box(f"set_grid_y{j}", (w, 0.08, 0.06), (0, -d / 2 + j * 3, h - 0.02), mg))
        mp = mat("set_panel", "#FFFFFF", 0.4, emit="#FFFFFF", emit_strength=1.0)
        for px in (-w / 4, w / 4):
            for py in (-d / 5, d / 4):
                shell.append(box(f"set_panel{px}{py}", (2.6, 2.6, 0.08), (px, py, h - 0.04), mp))
    for ob in shell:
        try:
            ob.visible_shadow = False
        except Exception:
            pass
    return fl


def import_model(path, loc=(0, 0, 0), scale=1.0, rot_z=0.0):
    """Import a free model (.glb/.gltf/.fbx/.obj) from Poly Haven, Poly Pizza,
    Sketchfab (CC licence), Kenney, or a Roblox Studio 'Export Selection'."""
    ext = os.path.splitext(path)[1].lower()
    before = set(bpy.data.objects)
    if ext in (".glb", ".gltf"):
        bpy.ops.import_scene.gltf(filepath=path)
    elif ext == ".fbx":
        bpy.ops.import_scene.fbx(filepath=path)
    elif ext == ".obj":
        bpy.ops.wm.obj_import(filepath=path)
    elif ext == ".blend":
        with bpy.data.libraries.load(path) as (src, dst):
            dst.objects = src.objects
        for ob in dst.objects:
            bpy.context.scene.collection.objects.link(ob)
    new = [o for o in bpy.data.objects if o not in before]
    roots = [o for o in new if o.parent is None or o.parent not in new]
    for r in roots:
        r.location = Vector(r.location) * scale + Vector(loc)
        r.scale = Vector(r.scale) * scale
        r.rotation_euler.z += math.radians(rot_z)
    return new


# --------------------------------------------------------------------------
# render
# --------------------------------------------------------------------------
def render_setup(out_path, start=1, end=120, fps=30, vertical=True, quality="final",
                 engine="EEVEE", res=(1080, 1920)):
    """quality: 'draft' (fast check) | 'final'. engine: EEVEE | CYCLES.
    Writes PNG frames to out_path (folder). Join them with ffmpeg:
      ffmpeg -framerate 30 -i out/%04d.png -c:v libx264 -crf 16 -pix_fmt yuv420p shot.mp4"""
    sc = bpy.context.scene
    items = [e.identifier for e in sc.render.bl_rna.properties["engine"].enum_items]
    if engine == "EEVEE":
        sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in items else "BLENDER_EEVEE"
    else:
        sc.render.engine = "CYCLES"
    w, h = res if vertical else (res[1], res[0])
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.resolution_percentage = 50 if quality == "draft" else 100
    sc.render.fps = fps
    sc.frame_start, sc.frame_end = start, end
    sc.render.film_transparent = False
    sc.render.use_motion_blur = quality == "final"
    ee = sc.eevee
    for attr, val in (("taa_render_samples", 16 if quality == "draft" else 64),
                      ("use_shadows", True), ("use_raytracing", quality == "final"),
                      ("use_volumetric_shadows", True), ("volumetric_tile_size", "4"),
                      ("use_gtao", True), ("shadow_ray_count", 2), ("shadow_step_count", 8)):
        try:
            setattr(ee, attr, val)
        except Exception:
            pass
    if sc.render.engine == "CYCLES":
        sc.cycles.samples = 24 if quality == "draft" else 160
        sc.cycles.use_denoising = True
        try:
            prefs = bpy.context.preferences.addons["cycles"].preferences
            prefs.compute_device_type = "METAL"
            prefs.get_devices()
            for d in prefs.devices:
                d.use = True
            sc.cycles.device = "GPU"
        except Exception:
            pass
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGB"
    sc.render.filepath = os.path.join(out_path, "")
    sc.render.use_overwrite = False                # resume a stopped render
    sc.render.use_placeholder = True
    return sc


def save(path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=path)
