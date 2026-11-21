"""Expressive acting layer on top of rbx.chars.Char: layered faces (eyes + mouth), named
expressions, blinks, lip flaps, gestures with overshoot, nods, head turns, jumps, run cycles.
Import order: chars first, then acting (it patches methods onto Char)."""
import math, os, random
from mathutils import Vector
from . import ASSETS
from .core import D, F, fcurves, set_interp
from . import chars as C

# eye / mouth cell indices (see tools/make_faces_layered.py)
EYE = dict(normal=0, wide=1, half=2, closed=3, happy=4, squint=5, side_l=6, side_r=7, terror=8,
           worried=9, angry=10, scared=11, wink=12, up=13, down=14, cry=15)
MOUTH = dict(flat=0, smile=1, open_smile=2, laugh=3, frown=4, o=5, talk=6, talk_wide=7, grimace=8,
             grimace_wide=9, scream=10, smirk=11, wavy=12, yawn=13, grin=14, ah=15)
EXPR = {
    "neutral": ("normal", "flat"), "happy": ("normal", "open_smile"), "joy": ("happy", "laugh"),
    "smile": ("normal", "smile"), "grin": ("happy", "grin"), "shock": ("wide", "grimace"),
    "gasp": ("wide", "o"), "terror": ("terror", "grimace_wide"), "scream": ("scared", "scream"),
    "worried": ("worried", "frown"), "angry": ("angry", "grimace"), "furious": ("angry", "scream"),
    "smug": ("half", "smirk"), "bored": ("half", "flat"), "sleepy": ("half", "wavy"),
    "yawn": ("closed", "yawn"), "sus": ("squint", "wavy"), "side_l": ("side_l", "frown"),
    "side_r": ("side_r", "frown"), "wink": ("wink", "smirk"), "cry": ("cry", "ah"),
    "scared": ("scared", "frown"), "talk": ("normal", "talk"), "shout": ("angry", "talk_wide"),
    "determined": ("angry", "flat"), "relief": ("closed", "smile"), "confused": ("squint", "o"),
    "lookup": ("up", "o"), "lookdown": ("down", "frown"), "panic": ("terror", "scream"),
}


# ------------------------------------------------------------------ roblox-v3 24-face toon atlas material (style-toon.md §4)
V3_FACES = [
    "neutral", "happy", "sad", "cry", "angry", "shocked",
    "scared", "sleepy", "talk", "smirk", "blink", "creepy",
    "smile", "laugh", "nervous", "dizzy", "squeeze", "wink",
    "oh", "content", "sparkle", "sparkle_oh", "nerd", "stare",
]
V3_COLS, V3_ROWS = 6, 4
V3_ALIAS = {
    "neutral": "neutral", "happy": "happy", "joy": "laugh", "smile": "smile", "grin": "happy",
    "shock": "shocked", "shocked": "shocked", "gasp": "oh", "oh": "oh",
    "terror": "scared", "scream": "scared", "scared": "scared", "panic": "scared",
    "worried": "nervous", "nervous": "nervous", "sus": "nervous",
    "angry": "angry", "furious": "angry", "shout": "angry", "determined": "angry",
    "smug": "smirk", "smirk": "smirk", "bored": "sleepy", "sleepy": "sleepy", "yawn": "sleepy",
    "side_l": "nervous", "side_r": "nervous", "wink": "wink", "cry": "cry", "sad": "sad",
    "talk": "talk", "relief": "content", "content": "content", "confused": "nerd",
    "lookup": "oh", "lookdown": "sad", "blink": "blink", "sparkle": "sparkle",
    "sparkle_oh": "sparkle_oh", "nerd": "nerd", "stare": "stare", "dizzy": "dizzy",
    "squeeze": "squeeze", "brace": "squeeze", "laugh": "laugh", "creepy": "creepy",
}


def v3_face_material(name, skin):
    """Head material projecting roblox-v3 face_atlas_v3.png (6x4 grid of 24 thick-ink 2D toon faces)."""
    m = D.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree; N, L = nt.nodes, nt.links
    b = next(n for n in N if n.type == "BSDF_PRINCIPLED")
    tc = N.new("ShaderNodeTexCoord"); sep = N.new("ShaderNodeSeparateXYZ")
    L.new(tc.outputs["Object"], sep.inputs[0])

    def M(op, a, bv=None):
        n = N.new("ShaderNodeMath"); n.operation = op
        (L.new(a, n.inputs[0]) if not isinstance(a, float) else setattr(n.inputs[0], "default_value", a))
        if bv is not None:
            (L.new(bv, n.inputs[1]) if not isinstance(bv, float) else setattr(n.inputs[1], "default_value", bv))
        return n.outputs[0]

    # Map head front (-0.54..+0.54 in X, -0.52..+0.52 in Z) to [0..1] UV cell
    u = M("ADD", M("DIVIDE", sep.outputs["X"], 1.08), 0.5)
    v = M("ADD", M("DIVIDE", M("SUBTRACT", sep.outputs["Z"], -0.02), 1.04), 0.5)
    mask = M("MULTIPLY", M("MULTIPLY", M("MULTIPLY", M("GREATER_THAN", u, 0.0), M("LESS_THAN", u, 1.0)),
                              M("MULTIPLY", M("GREATER_THAN", v, 0.0), M("LESS_THAN", v, 1.0))),
             M("LESS_THAN", sep.outputs["Y"], -0.05))
    cmb = N.new("ShaderNodeCombineXYZ"); L.new(u, cmb.inputs[0]); L.new(v, cmb.inputs[1])
    col = N.new("ShaderNodeRGB"); col.name = "Skin"; col.outputs[0].default_value = (*skin, 1)

    mp = N.new("ShaderNodeMapping"); mp.name = "V3FaceMap"
    mp.vector_type = "POINT"
    mp.inputs["Scale"].default_value = (1.0 / V3_COLS, 1.0 / V3_ROWS, 1.0)
    mp.inputs["Location"].default_value = (0.0, (V3_ROWS - 1) / V3_ROWS, 0.0)
    L.new(cmb.outputs[0], mp.inputs[0])

    tx = N.new("ShaderNodeTexImage")
    tx.image = D.images.load(os.path.join(ASSETS, "faces", "face_atlas_v3.png"), check_existing=True)
    tx.extension = "CLIP"; tx.interpolation = "Cubic"
    L.new(mp.outputs[0], tx.inputs[0])

    a = M("MULTIPLY", tx.outputs["Alpha"], mask)
    mix = N.new("ShaderNodeMix"); mix.data_type = "RGBA"
    L.new(a, mix.inputs[0]); L.new(col.outputs[0], mix.inputs[6]); L.new(tx.outputs["Color"], mix.inputs[7])
    L.new(mix.outputs[2], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.58
    try:
        b.inputs["Specular IOR Level"].default_value = 0.25
    except KeyError:
        pass
    m.diffuse_color = (*skin, 1)
    return m


def _v3_cell(face_name):
    fn = V3_ALIAS.get(face_name, "neutral") if isinstance(face_name, str) else V3_FACES[int(face_name) % len(V3_FACES)]
    idx = V3_FACES.index(fn) if fn in V3_FACES else 0
    col, row = idx % V3_COLS, idx // V3_COLS
    return (col / V3_COLS, (V3_ROWS - 1 - row) / V3_ROWS, 0.0)


def _key_v3_face(ch, face_name, t):
    nt = ch.face_mat.node_tree
    mp = nt.nodes["V3FaceMap"]
    mp.inputs["Location"].default_value = _v3_cell(face_name)
    mp.inputs["Location"].keyframe_insert("default_value", frame=F(t))
    if nt.animation_data and nt.animation_data.action:
        for fc in fcurves(nt.animation_data.action):
            for kp in fc.keyframe_points:
                kp.interpolation = "CONSTANT"


def _is_v3(ch):
    return ch.face_mat is not None and "V3FaceMap" in ch.face_mat.node_tree.nodes
def layered_face_material(name, style, skin):
    """Head material that projects an eyes atlas and a mouth atlas onto the head front."""
    m = D.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree; N, L = nt.nodes, nt.links
    b = next(n for n in N if n.type == "BSDF_PRINCIPLED")
    tc = N.new("ShaderNodeTexCoord"); sep = N.new("ShaderNodeSeparateXYZ")
    L.new(tc.outputs["Object"], sep.inputs[0])

    def M(op, a, bv=None):
        n = N.new("ShaderNodeMath"); n.operation = op
        (L.new(a, n.inputs[0]) if not isinstance(a, float) else setattr(n.inputs[0], "default_value", a))
        if bv is not None:
            (L.new(bv, n.inputs[1]) if not isinstance(bv, float) else setattr(n.inputs[1], "default_value", bv))
        return n.outputs[0]
    u = M("ADD", M("DIVIDE", sep.outputs["X"], C.FACE_W), 0.5)
    v = M("ADD", M("DIVIDE", M("SUBTRACT", sep.outputs["Z"], C.FACE_Z), C.FACE_H), 0.5)
    mask = M("MULTIPLY", M("MULTIPLY", M("MULTIPLY", M("GREATER_THAN", u, 0.0), M("LESS_THAN", u, 1.0)),
                              M("MULTIPLY", M("GREATER_THAN", v, 0.0), M("LESS_THAN", v, 1.0))),
             M("LESS_THAN", sep.outputs["Y"], -0.05))
    cmb = N.new("ShaderNodeCombineXYZ"); L.new(u, cmb.inputs[0]); L.new(v, cmb.inputs[1])
    col = N.new("ShaderNodeRGB"); col.name = "Skin"; col.outputs[0].default_value = (*skin, 1)
    cur = col.outputs[0]
    alphas = []
    for layer in ("eyes", "mouth"):
        mp = N.new("ShaderNodeMapping"); mp.name = "EyeMap" if layer == "eyes" else "MouthMap"
        mp.vector_type = "POINT"; mp.inputs["Scale"].default_value = (0.25, 0.25, 1)
        mp.inputs["Location"].default_value = (0.0, 0.75, 0)
        L.new(cmb.outputs[0], mp.inputs[0])
        tx = N.new("ShaderNodeTexImage")
        tx.image = D.images.load(os.path.join(ASSETS, "faces", f"{style}_{layer}.png"), check_existing=True)
        tx.extension = "CLIP"; tx.interpolation = "Cubic"
        L.new(mp.outputs[0], tx.inputs[0])
        a = M("MULTIPLY", tx.outputs["Alpha"], mask)
        mix = N.new("ShaderNodeMix"); mix.data_type = "RGBA"
        L.new(a, mix.inputs[0]); L.new(cur, mix.inputs[6]); L.new(tx.outputs["Color"], mix.inputs[7])
        cur = mix.outputs[2]; alphas.append(a)
    L.new(cur, b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.62
    try:
        b.inputs["Specular IOR Level"].default_value = 0.3
    except KeyError:
        pass
    m.diffuse_color = (*skin, 1)
    return m


def _cell(idx):
    return ((idx % 4) * 0.25, (3 - idx // 4) * 0.25, 0)


def _key_map(ch, node, idx, t):
    nt = ch.face_mat.node_tree
    mp = nt.nodes[node]
    mp.inputs["Location"].default_value = _cell(idx)
    mp.inputs["Location"].keyframe_insert("default_value", frame=F(t))
    for fc in fcurves(nt.animation_data.action):
        for kp in fc.keyframe_points:
            kp.interpolation = "CONSTANT"


def _layered(ch):
    return ch.face_mat is not None and "EyeMap" in ch.face_mat.node_tree.nodes


def face(ch, t, expr=None, eyes=None, mouth=None):
    """face(t, "shock") | face(t, eyes="wide", mouth="scream") | legacy int index."""
    if _is_v3(ch):
        fname = expr or mouth or eyes or "neutral"
        _key_v3_face(ch, fname, t)
        ch._v3_track.append((t, fname))
        return ch
    if not _layered(ch):
        return C.Char._face_legacy(ch, t, expr)
    if isinstance(expr, str):
        e, m_ = EXPR[expr]
        eyes = eyes or e; mouth = mouth or m_
    if eyes is not None:
        ei = EYE[eyes] if isinstance(eyes, str) else eyes
        _key_map(ch, "EyeMap", ei, t); ch._eye_track.append((t, ei))
    if mouth is not None:
        mi = MOUTH[mouth] if isinstance(mouth, str) else mouth
        _key_map(ch, "MouthMap", mi, t); ch._mouth_track.append((t, mi))
    return ch


def _eye_at(ch, t):
    best = (-1e9, EYE["normal"])
    for tt, e in ch._eye_track:
        if tt <= t and tt >= best[0]:
            best = (tt, e)
    return best[1]


def _v3_at(ch, t):
    best = (-1e9, "neutral")
    for tt, fn in getattr(ch, "_v3_track", []):
        if tt <= t and tt >= best[0]:
            best = (tt, fn)
    return best[1]


def blink(ch, t0, t1, every=(1.8, 3.6), seed=None):
    """Auto blinks (3 frames closed) where the eyes are open."""
    if _is_v3(ch):
        rnd = random.Random(seed if seed is not None else hash(ch.name) % 1000)
        t = t0 + rnd.uniform(0.4, every[0])
        while t < t1 - 0.15:
            cur = _v3_at(ch, t)
            nxt = [tt for tt, _ in ch._v3_track if t - 0.05 < tt < t + 0.18]
            if cur not in ("blink", "happy", "laugh", "wink", "squeeze", "content") and not nxt:
                _key_v3_face(ch, "blink", t)
                _key_v3_face(ch, cur, t + 0.1)
            t += rnd.uniform(*every)
        return ch
    if not _layered(ch):
        return ch
    rnd = random.Random(seed if seed is not None else hash(ch.name) % 1000)
    t = t0 + rnd.uniform(0.3, every[0])
    while t < t1 - 0.12:
        cur = _eye_at(ch, t)
        nxt = [tt for tt, _ in ch._eye_track if t - 0.02 < tt < t + 0.15]
        if cur not in (EYE["closed"], EYE["happy"], EYE["wink"]) and not nxt:
            _key_map(ch, "EyeMap", EYE["closed"], t)
            _key_map(ch, "EyeMap", cur, t + 0.1)
        t += rnd.uniform(*every)
    return ch


def talk(ch, t0, t1, words=None, open_m="talk", wide_m="talk_wide", rest="flat", syll=0.12):
    """Lip flaps. With words ([{start,end}] or [{s,e}]) flap per word, else at a syllable rate."""
    if _is_v3(ch):
        base_f = _v3_at(ch, t0)
        if base_f == "talk":
            base_f = "neutral"
        k = 0
        t = t0
        while t < t1:
            _key_v3_face(ch, "talk" if k % 2 == 0 else base_f, t)
            k += 1
            t += 0.12
        _key_v3_face(ch, base_f, t1)
        return ch
    if not _layered(ch):
        return ch
    k = 0
    if words:
        for w in words:
            s = w.get("start", w.get("s")); e = w.get("end", w.get("e"))
            if s is None or s < t0 or s >= t1:
                continue
            face(ch, s, mouth=open_m if k % 3 else wide_m)
            if e - s > 0.22:
                face(ch, s + (e - s) * 0.5, mouth=rest)
                face(ch, s + (e - s) * 0.7, mouth=open_m)
            k += 1
        face(ch, t1, mouth=rest)
    else:
        t = t0
        while t < t1:
            face(ch, t, mouth=(open_m, wide_m, rest, open_m)[k % 4]); k += 1; t += syll
        face(ch, t1, mouth=rest)
    return ch


# ------------------------------------------------------------------ gestures
G = {
    "idle": dict(armL=(0, 4), armR=(0, 4), torso=(0, 0, 0), head=(0, 0, 0)),
    "shock": dict(armL=(35, 55), armR=(35, 55), torso=(0, -8, 0), head=(0, -10, 0)),
    "hands_head": dict(armL=(155, 30), armR=(155, 30), torso=(0, -4, 0), head=(0, 4, 0)),
    "hands_face": dict(armL=(140, -25), armR=(140, -25), head=(0, 6, 0)),
    "cheer": dict(armL=(170, 30), armR=(170, 30), head=(0, -18, 0), torso=(0, -6, 0)),
    "point": dict(armR=(92, -6), armL=(10, 8), head=(-8, 0, 0)),
    "point_l": dict(armL=(92, -6), armR=(10, 8), head=(8, 0, 0)),
    "shrug": dict(armL=(35, 38), armR=(35, 38), head=(0, 0, 12), torso=(0, 0, 4)),
    "recoil": dict(armL=(55, 30), armR=(55, 30), torso=(0, -14, 0), head=(0, -12, 0)),
    "lean": dict(torso=(0, 16, 0), head=(0, -10, 0), armL=(20, 8), armR=(20, 8)),
    "slump": dict(torso=(0, 20, 0), head=(0, 28, 0), armL=(0, 2), armR=(0, 2)),
    "think": dict(armR=(125, -38), armL=(40, -30), head=(12, 6, 8)),
    "cross": dict(armL=(80, -48), armR=(80, -48), head=(0, -4, 0)),
    "phone": dict(armR=(150, -42), armL=(15, 10), head=(-10, 0, 8)),
    "reach": dict(armR=(95, 4), armL=(70, 10), torso=(0, 12, 0)),
    "push": dict(armL=(90, -8), armR=(90, -8), torso=(0, 14, 0)),
    "hold": dict(armL=(75, -14), armR=(75, -14)),
    "wave": dict(armR=(165, 25), armL=(5, 6)),
    "fists": dict(armL=(60, 20), armR=(60, 20), torso=(0, 6, 0), head=(0, 4, 0)),
    "facepalm": dict(armR=(140, -30), head=(0, 18, 0), torso=(0, 8, 0)),
    "brace": dict(armL=(80, 40), armR=(80, 40), torso=(0, -10, 0), head=(0, 10, 0), hipz=-0.25),
}


def _scale(v, k):
    return tuple(x * k for x in v)


def act(ch, t, name, strength=1.0, settle=0.22, overshoot=0.18, expr=None, **extra):
    """Pose pop: reaches 1+overshoot at ~40% of settle, settles to the pose at t+settle."""
    p = dict(G[name]); p.update(extra)
    k_over = 1.0 + overshoot
    over = {k: (_scale(v, strength * k_over) if isinstance(v, tuple) else v * strength * k_over) for k, v in p.items()}
    final = {k: (_scale(v, strength) if isinstance(v, tuple) else v * strength) for k, v in p.items()}
    ch.pose(t + settle * 0.45, **over)
    ch.pose(t + settle, **final)
    if expr:
        face(ch, t, expr)
    return ch


def hold_pose(ch, t, name=None, **kw):
    """Key the current pose at t (to hold it until a later act)."""
    p = dict(G[name]) if name else {}
    p.update(kw)
    ch.pose(t, **p)
    return ch


def wiggle(ch, t0, t1, part="armL", amp=(25, 15), rate=7.0, base=(140, 30)):
    """Oscillating limb (panic flail, waving)."""
    t, k = t0, 0
    while t <= t1:
        s = 1 if k % 2 == 0 else -1
        ch.pose(t, **{part: (base[0] + amp[0] * s, base[1] + amp[1] * s)})
        t += 1.0 / rate; k += 1
    return ch


def panic(ch, t0, t1, rate=7.0):
    wiggle(ch, t0, t1, "armL", (30, 20), rate, (140, 35))
    wiggle(ch, t0 + 0.5 / rate, t1, "armR", (30, 20), rate, (140, 35))
    return ch


def nod(ch, t, n=2, amp=12, rate=6.0):
    for i in range(n):
        ch.pose(t + i / rate, head=(0, amp, 0)); ch.pose(t + (i + 0.5) / rate, head=(0, -amp * 0.3, 0))
    ch.pose(t + n / rate, head=(0, 0, 0))
    return ch


def shake(ch, t, n=3, amp=18, rate=7.0):
    for i in range(n):
        s = 1 if i % 2 == 0 else -1
        ch.pose(t + i / rate, head=(amp * s, 0, 0))
    ch.pose(t + n / rate, head=(0, 0, 0))
    return ch


def look(ch, t, yaw=0, pitch=0, roll=0, settle=0.18):
    """Head snap with overshoot."""
    ch.pose(t + settle * 0.5, head=(yaw * 1.15, pitch * 1.15, roll))
    ch.pose(t + settle, head=(yaw, pitch, roll))
    return ch


def jump(ch, t, height=1.6, dur=0.5, loc=None):
    """Hop in place (or from loc) with crouch anticipation and landing squash."""
    base = Vector(loc) if loc else Vector(ch.root.location)
    ch.pose(t, hipz=-0.35, armL=(-20, 10), armR=(-20, 10), loc=tuple(base))
    ch.pose(t + dur * 0.15, hipz=0.0)
    ch.pose(t + dur * 0.5, loc=tuple(base + Vector((0, 0, height))), armL=(150, 30), armR=(150, 30),
            legL=(25, 0), legR=(-15, 0))
    ch.pose(t + dur, loc=tuple(base), hipz=-0.3, armL=(40, 30), armR=(40, 30), legL=(0, 0), legR=(0, 0))
    ch.pose(t + dur + 0.12, hipz=0.0, armL=(5, 6), armR=(5, 6))
    return ch


def run(ch, t0, t1, p0, p1, rate=3.6):
    """Full-energy run: wide swings, forward lean, bounce."""
    ch.walk(t0, t1, p0, p1, rate=rate, swing=48, arm=55, bob=0.3)
    ch.pose(t0, torso=(0, 10, 0)); ch.pose(t1, torso=(0, 10, 0))
    return ch


def breathe(ch, strength=1.0):
    """Stronger idle than Char.idle: breathing hip bob + head drift + arm sway."""
    from .core import noise
    noise(ch.hip, "location", 2, 0.04 * strength, 18)
    noise(ch.neck, "rotation_euler", 2, 0.07 * strength, 22)
    noise(ch.neck, "rotation_euler", 0, 0.04 * strength, 26)
    noise(ch.shL, "rotation_euler", 0, 0.05 * strength, 30)
    noise(ch.shR, "rotation_euler", 0, 0.05 * strength, 33)
    return ch


# ------------------------------------------------------------------ patch onto Char
def install():
    if getattr(C.Char, "_acting_installed", False):
        return
    C.Char._face_legacy = C.Char.face
    orig_init = C.Char.__init__

    def init(self, name, *a, **kw):
        style = kw.get("face", "hero")
        v3_path = os.path.join(ASSETS, "faces", "face_atlas_v3.png")
        use_v3 = bool(style) and os.path.exists(v3_path)
        layered = (not use_v3) and style and os.path.exists(os.path.join(ASSETS, "faces", f"{style}_eyes.png"))
        if use_v3 or layered:
            kw["face"] = None
        orig_init(self, name, *a, **kw)
        self._eye_track, self._mouth_track, self._v3_track = [], [], []
        if use_v3:
            self.face_mat = v3_face_material(name + "_face", self.skin_c)
            self.head.data.materials.clear(); self.head.data.materials.append(self.face_mat)
            face(self, -10.0, "neutral")
        elif layered:
            self.face_mat = layered_face_material(name + "_face", style, self.skin_c)
            self.head.data.materials.clear(); self.head.data.materials.append(self.face_mat)
            face(self, -10.0, "neutral")
    C.Char.__init__ = init
    for fn in (face, blink, talk, act, hold_pose, wiggle, panic, nod, shake, look, jump, run, breathe):
        setattr(C.Char, fn.__name__, fn)
    C.Char._acting_installed = True


install()
