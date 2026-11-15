"""dont_sneeze: "Don't Sneeze. You'll Disappear." — 53 shots keyed to script word indices (0..385)."""
from shotkit import *
from rbx import story
from rbx.story import *
import math, os, random
from mathutils import Vector

V = Video(__file__)
story.bind(V)
BOARD = "chalk_sneeze.png"


# ------------------------------------------------------------------ cast & scene lighting helpers
def bright_town():
    """Town street with warm front & rim lighting so characters at y=-26 are bright and never silhouetted."""
    R = town_scene()
    W.sun(4.5, rot=(48, 0, 20))
    light("tw_front_key", "AREA", (0, -42, 14), 9000, (1.0, 0.98, 0.94), 22, target=(0, -25, 3.5))
    light("tw_rim_fill", "AREA", (0, -10, 14), 4500, (0.9, 0.95, 1.0), 18, target=(0, -26, 3.5))
    return R


def bedroom_scene():
    """Brightly lit bedroom set."""
    world((0.88, 0.92, 1.0), 0.6)
    B = sets.bedroom()
    light("br_key", "AREA", (0, -2, 11.5), 8500, (1.0, 0.97, 0.92), 14, target=(0, 3.5, 2.5))
    light("br_fill", "AREA", (0, -10, 6.0), 3500, (0.9, 0.95, 1.0), 10, target=(0, 3.5, 3.0))
    return B


def space_scene():
    """Brightly lit outer-space quarantine room/deck."""
    W.space_world(1.0)
    W.sun(5.5, rot=(48, 0, 25))
    light("sp_key", "AREA", (0, -10, 8), 5000, (0.92, 0.96, 1.0), 12, target=(0, 0, 3.5))
    light("sp_fill", "AREA", (-8, -6, 4), 2500, (0.8, 0.9, 1.0), 8, target=(0, 0, 3.0))
    box("sp_pad", (10, 10, 0.4), (0, 0, -0.2), mat("sp_deck", hexc("#3a4252"), 0.4, metal=0.5), 0.08)


def mia(t0, t1, expr="happy", **kw):
    return story._live(
        chars.Char("Mia", skin="#f2dbc6", shirt="#f09ac2", pants="#31496b", hair="bob",
                   hair_color="#5b3f2e", face="girl", sleeves="short", **kw),
        t0, t1, expr
    )


def photographer(t0, t1, expr="happy", **kw):
    return story._live(
        chars.Char("Photographer", skin="#e8c7a4", shirt="#e8b520", shirt_kind="checker", shirt_c2="#c8761e",
                   pants="#2b2f3a", hair="cap", hair_color="#2b2f3a", face="mustache", extras=("glasses",), **kw),
        t0, t1, expr
    )


def higgins(t0, t1, expr="neutral", scale=1.0, loc=(0, -26, 0), rot=0):
    H = chars.Char("Higgins", skin="#efd6be", shirt="#4a7ab5", pants="#353a45", hair="short",
                   hair_color="#dcdcdc", face="mustache", sleeves="long",
                   extras=("glasses", "beard:#e5e5e5"), scale=scale, loc=loc, rot=rot)
    story._live(H, t0, t1, expr, br=0.5)
    return H


def uncle(t0, t1, expr="neutral", **kw):
    return story._live(
        chars.Char("Uncle", skin="#e9c7a6", shirt="#4a7ab5", shirt_kind="stripes", shirt_c2="#f0f4f8",
                   pants="#3b3f4a", hair="messy", hair_color="#5a3a22", face="mustache", **kw),
        t0, t1, expr
    )


def nurse(t0, t1, expr="happy", **kw):
    return story._live(
        chars.Char("Nurse", skin="#f2dbc6", shirt="#f4f8fc", pants="#f4f8fc", hair="bun",
                   hair_color="#8a5a3a", face="girl", sleeves="long", extras=("collar:#d83434",), **kw),
        t0, t1, expr
    )


def shrink_to(ch, t_hit, s0=1.0, s1=0.18, dur=0.22):
    """Squash-and-stretch pop shrink on sneeze."""
    ch.root.scale = (s0, s0, s0)
    ch.root.keyframe_insert("scale", frame=F(max(0.0, t_hit - 0.03)))
    ch.root.scale = (s0 * 1.18, s0 * 1.18, s0 * 0.82)
    ch.root.keyframe_insert("scale", frame=F(t_hit + 0.05))
    ch.root.scale = (s1, s1, s1)
    ch.root.keyframe_insert("scale", frame=F(t_hit + dur))
    p = Vector(ch.root.location) + Vector((0, 0, 2.2 * s0))
    W2.poof("poof_" + ch.name, tuple(p), t_hit + 0.03, max(0.25, 0.55 * s0))


def grow_to(ch, t_hit, s0=0.18, s1=1.0, dur=0.28):
    """Pop back up to normal size."""
    ch.root.scale = (s0, s0, s0)
    ch.root.keyframe_insert("scale", frame=F(max(0.0, t_hit - 0.03)))
    ch.root.scale = (s1 * 1.12, s1 * 1.12, s1 * 1.08)
    ch.root.keyframe_insert("scale", frame=F(t_hit + dur * 0.75))
    ch.root.scale = (s1, s1, s1)
    ch.root.keyframe_insert("scale", frame=F(t_hit + dur))


def camera_tripod(loc=(0, 10.5, 0), rot=0, scale=1.0):
    root = empty("tripod", loc, rot=(0, 0, rot))
    root.scale = (scale,) * 3
    M_dark = mat("cam_dark", hexc("#2b303c"), 0.35, metal=0.4)
    M_lens = mat("cam_lens", hexc("#111318"), 0.15, metal=0.8)
    M_flash = mat("cam_flash", (1.0, 0.98, 0.88), 0.2, emit=(1.0, 0.96, 0.8), estr=2.5)
    for ang in (-28, 0, 28):
        cyl(f"tri_leg_{ang}", 0.08, 3.8, (math.sin(math.radians(ang)) * 0.7, math.cos(math.radians(ang)) * 0.4, 1.8),
            M_dark, 12, parent=root, rot=(12, ang * 0.4, 0))
    box("cam_body", (1.1, 0.8, 0.85), (0, 0, 3.8), M_dark, 0.06, parent=root)
    cyl("cam_barrel", 0.32, 0.55, (0, -0.55, 3.8), M_lens, 24, parent=root, rot=(90, 0, 0))
    fl = sphere("cam_flash_bulb", 0.24, (0, -0.45, 4.45), M_flash, seg=16, parent=root)
    return root, fl


def bouquet_prop(name="bouquet", loc=(0, 0, 0), parent=None, scale=1.0):
    root = empty(name, loc, parent=parent)
    root.scale = (scale,) * 3
    cyl(name + "_wrap", 0.12, 0.9, (0, 0, 0.45), mat("wrap_green", hexc("#4da856"), 0.5), 16, parent=root, r2=0.36)
    cols = ("#ff5c8a", "#ffd23a", "#ff884d", "#a66cff", "#ff4757")
    for i, c in enumerate(cols):
        a = i / len(cols) * math.tau
        sphere(f"{name}_fl{i}", 0.22, (math.cos(a) * 0.22, math.sin(a) * 0.22, 0.95),
               mat(f"fl_{c}", hexc(c), 0.4, emit=hexc(c), estr=0.2), seg=14, parent=root)
    return root


def pollen_cloud(center, t0, t1, n=35, spread=3.5, seed=1):
    rnd = random.Random(seed)
    Mp = mat("pollen_gold", hexc("#ffe047"), 0.3, emit=hexc("#ffd23a"), estr=1.8)
    for i in range(n):
        p0 = (center[0] + rnd.uniform(-0.6, 0.6), center[1] + rnd.uniform(-0.6, 0.6), center[2] + rnd.uniform(-0.3, 0.5))
        p1 = (center[0] + rnd.uniform(-spread, spread), center[1] + rnd.uniform(-spread, spread), center[2] + rnd.uniform(-1.0, 2.2))
        ob = sphere(f"pollen_{seed}_{i}", rnd.uniform(0.06, 0.13), p0, Mp, seg=10)
        ob.keyframe_insert("location", frame=F(t0))
        ob.location = p1
        ob.keyframe_insert("location", frame=F(t1))


def shoe_prop(name="shoe", loc=(0, 0, 0), scale=1.0, color="#2f6fd0", rot=0):
    root = empty(name, loc, rot=(0, 0, rot))
    root.scale = (scale,) * 3
    Ms = mat(name + "_mat", hexc(color), 0.4)
    Mw = mat(name + "_sole", (0.95, 0.95, 0.95), 0.5)
    box(name + "_sole", (1.2, 2.4, 0.35), (0, 0, 0.18), Mw, 0.06, parent=root)
    box(name + "_upper", (1.15, 1.6, 0.95), (0, 0.25, 0.75), Ms, 0.12, parent=root)
    box(name + "_toe", (1.12, 0.9, 0.6), (0, -0.65, 0.55), Mw, 0.14, parent=root)
    return root


def vacuum_prop(loc=(0, 0, 0), tipped=False):
    root = empty("vacuum", loc, rot=(0, 78 if tipped else 0, 0))
    Mr = mat("vac_red", hexc("#d93829"), 0.35)
    Mg = mat("vac_grey", hexc("#4a505c"), 0.4, metal=0.3)
    box("vac_base", (1.3, 1.5, 0.5), (0, 0, 0.25), Mr, 0.08, parent=root)
    cyl("vac_bag", 0.42, 2.4, (0, 0.2, 1.6), Mr, 20, parent=root)
    cyl("vac_stick", 0.09, 3.4, (0, 0.35, 2.1), Mg, 12, parent=root, rot=(-8, 0, 0))
    return root


def syringe_prop(loc=(0, 0, 0), scale=1.0, rot=(0, -25, 0)):
    root = empty("syringe", loc, rot=rot)
    root.scale = (scale,) * 3
    M_glass = mat("syr_glass", (0.85, 0.95, 1.0), 0.15, alpha=0.45)
    M_liq = mat("syr_liq", hexc("#38d962"), 0.25, emit=hexc("#38d962"), estr=0.6)
    M_met = mat("syr_met", (0.82, 0.85, 0.88), 0.2, metal=0.8)
    cyl("syr_barrel", 0.45, 2.4, (0, 0, 2.0), M_glass, 24, parent=root)
    cyl("syr_fluid", 0.38, 1.7, (0, 0, 1.8), M_liq, 20, parent=root)
    cyl("syr_plunger", 0.18, 1.4, (0, 0, 3.6), M_met, 16, parent=root)
    cyl("syr_needle", 0.05, 1.0, (0, 0, 0.3), M_met, 12, parent=root)
    return root


def streetlamp_prop(loc=(-2.2, -26, 0)):
    root = empty("streetlamp", loc)
    Mp = mat("lamp_post_mat", hexc("#3a404d"), 0.35, metal=0.7)
    Mg = mat("lamp_bulb_mat", (1.0, 0.95, 0.75), 0.2, emit=(1.0, 0.92, 0.65), estr=3.5)
    cyl("lamp_pole", 0.18, 7.5, (0, 0, 3.75), Mp, 16, parent=root)
    box("lamp_arm", (1.4, 0.22, 0.22), (0.6, 0, 7.4), Mp, 0.04, parent=root)
    sphere("lamp_bulb", 0.42, (1.2, 0, 7.1), Mg, seg=16, parent=root)
    return root


# ================================================================== 0-3s HOOK (Words 0..30)
@S(1, 0, 6, "HOOK: Picture Day classroom, Eddie sneezes in front of tripod camera")
def s01(t0, t1):
    R, ks = class_scene(t0, t1, kids=8, board=BOARD)
    camera_tripod((0.2, 10.8, 0), rot=0)
    E = eddie(t0, t1, "shock")
    E.pose(t0, loc=(2.5, 9.0, 0), rot=180)
    tsn = w(1) + 0.05
    W2.sneeze(E, t0, tsn)
    for k in ks[:4]:
        k.face(tsn, "gasp")
    cam = Cam()
    cam.push(t0, t1, (2.5, 9.0, 3.5), 4.6, 4.0, yaw=186, pitch=4, lens=20, yaw1=176)
    cam.crash(tsn, 20, 26, 0.08)
    cam.handheld(1.4)
    sfx(tsn, "sneeze")


@S(2, 6, 15, "Eddie shrinks down to the size of a thumbtack on the open classroom floor")
def s02(t0, t1):
    R, ks = class_scene(t0, t1, kids=6, board=BOARD)
    E = eddie(t0, t1, "terror")
    E.pose(t0, loc=(2.5, 9.5, 0), rot=180)
    t_sh = t0 + 0.08
    shrink_to(E, t_sh, s0=1.0, s1=0.16, dur=0.22)
    E.act(t_sh + 0.1, "hands_head", expr="terror")
    cam = Cam()
    cam.key(t0, (2.5, 13.2, 3.8), (2.5, 9.5, 2.4), lens=24)
    cam.key(t1, (2.5, 11.4, 1.1), (2.5, 9.5, 0.45), lens=28)
    cam.handheld(1.3)
    sfx(t_sh, "poof")
    sfx(t_sh + 0.12, "boing")


@S(3, 15, 23, "Leo next to Eddie sneezes violently")
def s03(t0, t1):
    R, ks = class_scene(t0, t1, kids=6, board=BOARD)
    L = leo(t0, t1, "shock")
    L.pose(t0, loc=(-1.8, 9.2, 0), rot=180)
    shoe_prop("leo_shoe", (-0.6, 9.2, 0), scale=0.95, color="#2f5fd0", rot=180)
    tsn = w(21)
    W2.sneeze(L, t0 + 0.05, tsn)
    cam = Cam()
    cam.push(t0, t1, (-1.8, 9.2, 3.5), 4.5, 4.0, yaw=174, pitch=4, lens=20)
    cam.crash(tsn, 20, 26, 0.08)
    cam.handheld(1.2)
    sfx(tsn, "sneeze")


@S(4, 23, 30, "Leo shrinks and disappears straight inside his own giant sneaker")
def s04(t0, t1):
    R, ks = class_scene(t0, t1, kids=4, board=BOARD)
    sh = shoe_prop("giant_shoe", (-1.2, 9.5, 0), scale=1.35, color="#2f5fd0", rot=180)
    L = leo(t0, t1, "terror")
    L.pose(t0, loc=(-1.2, 9.5, 0.95), rot=180)
    t_sh = t0 + 0.06
    shrink_to(L, t_sh, s0=0.75, s1=0.12, dur=0.20)
    W2.vanish(L, t_sh + 0.28)
    cam = Cam()
    cam.push(t0, t1, (-1.2, 9.5, 1.2), 4.2, 2.8, yaw=188, pitch=16, lens=26)
    cam.handheld(1.2)
    sfx(t_sh, "poof")
    sfx(t_sh + 0.18, "pop")


# ================================================================== 3-8s WORLD RULE (Words 30..47)
@S(5, 30, 39, "RULE: On the town street, a kid sneezes and pops down smaller")
def s05(t0, t1):
    bright_town()
    E = eddie(t0, t1, "shock")
    E.pose(t0, loc=(0, -26, 0), rot=0)
    tsn = w(35)
    W2.sneeze(E, t0 + 0.04, tsn)
    shrink_to(E, tsn + 0.05, s0=1.0, s1=0.42, dur=0.20)
    cam = Cam()
    cam.push(t0, t1, (0, -26, 3.2), 7.8, 5.6, yaw=8, pitch=8, lens=24)
    cam.handheld(1.0)
    sfx(tsn, "sneeze")
    sfx(tsn + 0.08, "boing")


@S(6, 39, 47, "Rule part 2: Another huge sneeze shrinks him down to insect size")
def s06(t0, t1):
    bright_town()
    E = eddie(t0, t1, "terror")
    E.pose(t0, loc=(0, -26, 0), rot=0)
    E.root.scale = (0.42, 0.42, 0.42)
    tsn = w(42)
    W2.sneeze(E, t0 + 0.02, tsn)
    shrink_to(E, tsn + 0.04, s0=0.42, s1=0.14, dur=0.18)
    cam = Cam()
    cam.push(t0, t1, (0, -26, 1.3), 4.8, 3.0, yaw=-12, pitch=14, lens=26)
    cam.crash(tsn, 26, 35, 0.08)
    sfx(tsn, "sneeze")
    sfx(tsn + 0.06, "poof")


# ================================================================== 8-15s SOCIETY EXAMPLES (Words 47..80)
@S(7, 47, 55, "Hospital cafeteria: Doctor points at BANNED PEPPER sign & pepper jail")
def s07(t0, t1):
    world((0.65, 0.72, 0.85), 0.5)
    J = W2.pepper_jail()
    card("pepper_sign", 4.2, 2.8, (-2.8, 6.65, 7.2), img_mat("no_pepper", os.path.join(W.TEX, "no_pepper.png"), 0.5), "-Y")
    doc = chars.Char("Doc", skin="#f0dcc3", shirt="#f4f8fc", pants="#2c3e50", hair="slick",
                     hair_color="#4a4a4a", face="mustache", sleeves="long", extras=("glasses",))
    story._live(doc, t0, t1, "determined")
    doc.pose(t0, loc=(3.2, -5.2, 0), rot=15)
    doc.act(t0 + 0.1, "point")
    lips(doc, t0, t1)
    sh = J["shaker"]
    noise(sh, "rotation_euler", 1, 0.05, 6)
    cam = Cam()
    cam.key(t0, (0.5, -12.5, 4.4), (0.2, 3.0, 3.2), lens=26, focus=14.0, fstop=4)
    cam.key(t1, (0.3, -7.2, 3.8), (0.2, 3.0, 3.0), lens=26, focus=9.5, fstop=4)
    cam.handheld(0.8)
    sfx(t0 + 0.08, "buzzer")


@S(8, 55, 66, "Astronaut in helmet quarantining in space room away from floating dust")
def s08(t0, t1):
    space_scene()
    W2.earth("earth", (6, 48, 8), r=22)
    astro = pilot(t0, t1, "shock", name="Astro", shirt="#f0f4f8")
    W2.astronaut_helmet(astro)
    astro.pose(t0, loc=(0, 0, 0), rot=0)
    astro.act(t0 + 0.1, "recoil")
    pollen_cloud((0, -2.2, 3.8), t0, t1, n=22, spread=2.2, seed=9)
    cam = Cam()
    cam.orbit(t0, t1, (0, 0, 4.2), 6.4, -18, 18, pitch=6, lens=24)
    sfx(t0 + 0.05, "whoosh")


@S(9, 66, 74, "Uncle sleeping in bedroom next to an unplugged upright vacuum")
def s09(t0, t1):
    bedroom_scene()
    U = uncle(t0, t1, "neutral")
    U.pose(t0, loc=(-1.4, 3.2, 0), rot=0)
    U.face(t0, eyes="closed", mouth="frown")
    vacuum_prop((1.5, 3.2, 0), tipped=False)
    cam = Cam()
    cam.push(t0, t1, (0.0, 3.2, 3.2), 7.2, 5.6, yaw=-6, pitch=8, lens=24)
    sfx(t0 + 0.1, "snort")


@S(10, 74, 80, "The vacuum tips over with a dust puff; Uncle panics")
def s10(t0, t1):
    bedroom_scene()
    U = uncle(t0, t1, "terror")
    U.pose(t0, loc=(-1.4, 3.2, 0), rot=0)
    U.act(t0 + 0.08, "hands_head", expr="terror")
    vacuum_prop((1.5, 3.2, 0), tipped=True)
    puff("vac_dust", (1.8, 3.5, 0.9), t0 + 0.08, r=1.1)
    cam = Cam()
    cam.push(t0, t1, (0.0, 3.2, 3.0), 6.2, 4.8, yaw=8, pitch=10, lens=24)
    cam.crash(t0 + 0.08, 24, 32, 0.08)
    sfx(t0 + 0.06, "thud")
    sfx(t0 + 0.12, "gasp")


# ================================================================== 15s THE "BUT" PIVOT (Words 80..109)
@S(11, 80, 88, "Eddie in classroom pointing to himself, worried")
def s11(t0, t1):
    R, ks = class_scene(t0, t1, kids=6, board=BOARD)
    E = eddie(t0, t1, "worried")
    W.sit(E, t0, E_DESK)
    E.act(t0 + 0.06, "hands_face")
    lips(E, t0, t1)
    cam = Cam()
    cam.push(t0, t1, up(E_SEAT, 4.2), 5.4, 4.1, yaw=188, pitch=4, lens=26)
    sfx(t0 + 0.05, "pop")


@S(12, 88, 94, "Pollen, cat, and dust swirling around terrified Eddie")
def s12(t0, t1):
    R, ks = class_scene(t0, t1, kids=4, board=BOARD)
    E = eddie(t0, t1, "terror")
    W.sit(E, t0, E_DESK)
    W2.cat("allergy_cat", (3.6, 6.4, 3.42), rot=160)
    pollen_cloud(up(E_SEAT, 4.2), t0, t1, n=28, spread=2.4, seed=3)
    E.act(t0 + 0.05, "recoil")
    lips(E, t0, t1)
    cam = Cam()
    cam.orbit(t0, t1, up(E_SEAT, 4.2), 5.0, 170, 196, pitch=6, lens=24)
    sfx(t0 + 0.05, "meow")


@S(13, 94, 102, "Picture Day photographer stands in front of chalkboard beside tripod camera")
def s13(t0, t1):
    R, ks = class_scene(t0, t1, kids=6, board=BOARD)
    camera_tripod((-1.8, 11.2, 0), rot=0)
    ph = photographer(t0, t1, "joy")
    ph.pose(t0, loc=(1.2, 11.2, 0), rot=0)
    ph.act(t0 + 0.08, "wave")
    cam = Cam()
    cam.push(t0, t1, (-0.2, 11.2, 4.2), 6.2, 4.8, yaw=8, pitch=4, lens=24)
    sfx(t0 + 0.05, "door")


@S(14, 102, 109, "Close-up: Photographer holds huge glowing spring flower bouquet")
def s14(t0, t1):
    R, ks = class_scene(t0, t1, kids=4, board=BOARD)
    ph = photographer(t0, t1, "joy")
    ph.pose(t0, loc=(1.2, 11.2, 0), rot=0)
    ph.pose(t0, armR=(75, 15))
    bouquet_prop("spring_bouquet", (0.4, 10.1, 3.8), scale=1.35)
    pollen_cloud((0.4, 10.1, 4.5), t0, t1, n=25, spread=1.8, seed=14)
    cam = Cam()
    cam.push(t0, t1, (0.8, 10.6, 4.2), 4.6, 3.4, yaw=-10, pitch=4, lens=28)
    sfx(t0 + 0.05, "sparkle")


# ================================================================== ESCALATION 1: CLASSROOM (Words 109..196)
@S(15, 109, 113, "Eddie sniffs and — ACHOO! Massive sneeze wind-up and blast")
def s15(t0, t1):
    R, ks = class_scene(t0, t1, kids=6, board=BOARD)
    E = eddie(t0, t1, "shock")
    W.sit(E, t0, E_DESK)
    tsn = w(112)
    W2.sneeze(E, t0, tsn)
    cam = Cam()
    cam.push(t0, t1, up(E_SEAT, 4.4), 4.8, 3.5, yaw=182, pitch=4, lens=28)
    cam.crash(tsn, 28, 38, 0.06)
    cam.handheld(1.8)
    sfx(t0 + 0.03, "snort")
    sfx(tsn, "sneeze")


@S(16, 113, 122, "Eddie shrinks down onto the open classroom floor tiles")
def s16(t0, t1):
    R, ks = class_scene(t0, t1, kids=6, board=BOARD)
    E = eddie(t0, t1, "terror")
    E.pose(t0, loc=(2.5, 9.6, 1.8), rot=180)
    E.pose(t1, loc=(2.5, 9.6, 0.02), rot=180)
    shrink_to(E, t0 + 0.05, s0=0.85, s1=0.16, dur=min(0.45, (t1 - t0) * 0.7))
    E.panic(t0, t1, rate=6.0)
    cam = Cam()
    cam.key(t0, (2.5, 13.0, 3.6), (2.5, 9.6, 2.0), lens=24)
    cam.key(t1, (2.5, 11.4, 1.0), (2.5, 9.6, 0.4), lens=28)
    cam.handheld(1.5)
    sfx(t0 + 0.04, "whoosh")
    sfx(t0 + 0.18, "boing")


@S(17, 122, 132, "Floor-level POV: Tiny raisin-sized Eddie looking up at giant desks and chairs")
def s17(t0, t1):
    R, ks = class_scene(t0, t1, kids=4, board=BOARD)
    E = eddie(t0, t1, "terror")
    E.pose(t0, loc=(2.5, 9.5, 0), rot=180)
    E.root.scale = (0.14, 0.14, 0.14)
    E.act(t0 + 0.05, "hands_head", expr="terror")
    cam = Cam()
    cam.push(t0, t1, (2.5, 9.5, 0.45), 2.4, 1.6, yaw=192, pitch=12, lens=26)
    cam.handheld(1.0)
    sfx(t0 + 0.04, "pop")


@S(18, 132, 138, "Mia looks down at the floor and gasps in shock")
def s18(t0, t1):
    R, ks = class_scene(t0, t1, kids=6, board=BOARD)
    M = mia(t0, t1, "gasp")
    W.sit(M, t0, L_DESK)
    M.pose(t0 + 0.05, head=(0, 22, 0))
    M.act(t0 + 0.08, "shock")
    cam = Cam()
    cam.push(t0, t1, up(L_SEAT, 4.3), 5.2, 3.9, yaw=172, pitch=-4, lens=26)
    sfx(t0 + 0.06, "gasp")


@S(19, 138, 143, "Mia sneezes from the shock — ACHOO!")
def s19(t0, t1):
    R, ks = class_scene(t0, t1, kids=6, board=BOARD)
    M = mia(t0, t1, "shock")
    W.sit(M, t0, L_DESK)
    tsn = w(139) + 0.04
    W2.sneeze(M, t0, tsn)
    cam = Cam()
    cam.push(t0, t1, up(L_SEAT, 4.3), 4.8, 3.6, yaw=180, pitch=4, lens=28)
    cam.crash(tsn, 28, 38, 0.07)
    sfx(tsn, "sneeze")


@S(20, 143, 155, "Mia pops down right beside tiny Eddie on the floor tiles")
def s20(t0, t1):
    R, ks = class_scene(t0, t1, kids=4, board=BOARD)
    E = eddie(t0, t1, "shock")
    E.pose(t0, loc=(2.1, 9.5, 0), rot=165)
    E.root.scale = (0.14, 0.14, 0.14)
    M = mia(t0, t1, "shock")
    M.pose(t0, loc=(2.9, 9.5, 0), rot=195)
    shrink_to(M, t0 + 0.06, s0=0.45, s1=0.15, dur=0.18)
    cam = Cam()
    cam.push(t0, t1, (2.5, 9.5, 0.5), 2.8, 1.9, yaw=180, pitch=14, lens=26)
    sfx(t0 + 0.05, "poof")
    sfx(t0 + 0.14, "pop")


@S(21, 155, 161, "Camera tripod flash explodes with bright light")
def s21(t0, t1):
    R, ks = class_scene(t0, t1, kids=6, board=BOARD)
    tri, fl = camera_tripod((-0.8, 11.2, 0), rot=0, scale=1.15)
    ph = photographer(t0, t1, "joy")
    ph.pose(t0, loc=(1.4, 11.2, 0), rot=0)
    fl.scale = (1.0, 1.0, 1.0)
    fl.keyframe_insert("scale", frame=F(t0))
    fl.scale = (3.2, 3.2, 3.2)
    fl.keyframe_insert("scale", frame=F(t0 + 0.12))
    fl.scale = (1.1, 1.1, 1.1)
    fl.keyframe_insert("scale", frame=F(t1))
    cam = Cam()
    cam.push(t0, t1, (0.2, 11.2, 4.1), 5.6, 4.0, yaw=8, pitch=4, lens=24)
    cam.crash(t0 + 0.08, 24, 34, 0.08)
    sfx(t0 + 0.06, "click")
    sfx(t0 + 0.08, "sparkle")


@S(22, 161, 166, "Golden pollen puffs out of the bouquet into the classroom air")
def s22(t0, t1):
    R, ks = class_scene(t0, t1, kids=8, board=BOARD)
    bouquet_prop("bouquet_burst", (0.0, 10.5, 3.5), scale=1.4)
    puff("pollen_puff", (0.0, 10.8, 4.2), t0 + 0.05, r=1.4)
    pollen_cloud((0.0, 9.2, 4.2), t0, t1, n=45, spread=5.5, seed=22)
    cam = Cam()
    cam.push(t0, t1, (0.0, 10.2, 4.0), 6.2, 4.8, yaw=0, pitch=8, lens=24)
    sfx(t0 + 0.04, "poof")
    sfx(t0 + 0.10, "wind")


@S(23, 166, 174, "The whole class inhales at once with wide shocked eyes")
def s23(t0, t1):
    R, ks = class_scene(t0, t1, kids=8, board=BOARD)
    pollen_cloud((0.0, 5.5, 4.2), t0, t1, n=40, spread=6.0, seed=23)
    for k in ks:
        k.face(t0 + 0.04, "gasp")
        k.act(t0 + 0.06, "shock")
    cam = Cam()
    cam.key(t0, (-2.8, 12.6, 5.8), (0.0, 3.8, 3.2), lens=20)
    cam.key(t1, (2.8, 12.2, 5.4), (0.0, 3.8, 3.2), lens=22)
    cam.handheld(0.8)
    sfx(t0 + 0.05, "gasp")


@S(24, 174, 181, "Thirty kids sneeze in one giant chorus!")
def s24(t0, t1):
    R, ks = class_scene(t0, t1, kids=8, board=BOARD)
    tsn = w(176)
    for i, k in enumerate(ks):
        W2.sneeze(k, t0, tsn + (i % 3) * 0.03)
    cam = Cam()
    cam.key(t0, (0.0, 12.8, 5.8), (0.0, 4.2, 3.2), lens=20)
    cam.key(t1, (0.0, 11.2, 4.8), (0.0, 4.2, 3.0), lens=24)
    cam.crash(tsn, 20, 28, 0.08)
    cam.handheld(2.0)
    sfx(tsn, "sneeze")
    sfx(tsn + 0.05, "boom")


@S(25, 181, 187, "All the classmates pop and shrink down like popped balloons")
def s25(t0, t1):
    R, ks = class_scene(t0, t1, kids=8, board=BOARD)
    for i, k in enumerate(ks):
        t_hit = t0 + 0.04 + (i % 4) * 0.06
        shrink_to(k, t_hit, s0=1.0, s1=0.16, dur=0.18)
    cam = Cam()
    cam.key(t0, (1.5, 12.5, 5.4), (0.0, 4.2, 2.6), lens=22)
    cam.key(t1, (-1.2, 11.0, 4.2), (0.0, 4.2, 2.0), lens=24)
    cam.handheld(1.5)
    sfx(t0 + 0.04, "pop")
    sfx(t0 + 0.12, "poof")
    sfx(t0 + 0.22, "boing")


@S(26, 187, 196, "Low-angle worm's-eye view: Backpacks and tripod tower like skyscrapers")
def s26(t0, t1):
    R, ks = class_scene(t0, t1, kids=4, board=BOARD)
    camera_tripod((0.0, 9.2, 0), rot=0, scale=1.35)
    backpack("giant_bp1", (-1.5, 9.4, 0.85), "#e8574a")
    backpack("giant_bp2", (1.5, 9.4, 0.85), "#4aa5e8")
    E = eddie(t0, t1, "shock")
    E.pose(t0, loc=(-0.5, 10.6, 0), rot=180)
    E.root.scale = (0.14, 0.14, 0.14)
    M = mia(t0, t1, "shock")
    M.pose(t0, loc=(0.5, 10.6, 0), rot=180)
    M.root.scale = (0.14, 0.14, 0.14)
    cam = Cam()
    cam.key(t0, (0.0, 12.6, 0.65), (0.0, 9.2, 2.6), lens=20)
    cam.key(t1, (0.0, 12.0, 0.55), (0.0, 9.2, 3.2), lens=20)
    sfx(t0 + 0.05, "rise")


# ================================================================== ESCALATION 2: HALLWAY & TOWN (Words 196..244)
@S(27, 196, 204, "Pollen cloud drifts down the school corridor")
def s27(t0, t1):
    world((0.88, 0.92, 1.0), 0.55)
    W.hallway_day()
    pollen_cloud((0, 8.0, 3.8), t0, t1, n=45, spread=4.5, seed=27)
    puff("door_puff", (0, 10.5, 3.5), t0 + 0.08, r=1.5)
    cam = Cam()
    cam.push(t0, t1, (0, 8.0, 3.6), 8.5, 6.0, yaw=0, pitch=4, lens=24)
    sfx(t0 + 0.05, "wind")


@S(28, 204, 212, "School hallway: teachers and students sneeze and shrink as pollen rolls through")
def s28(t0, t1):
    world((0.88, 0.92, 1.0), 0.55)
    W.hallway_day()
    pollen_cloud((0, 8.0, 3.5), t0, t1, n=45, spread=5.5, seed=28)
    for i, x in enumerate((-2.2, 0.0, 2.2)):
        k = townie(10 + i, t0, t1, "shock")
        k.pose(t0, loc=(x, 7.0 + i * 1.2, 0), rot=0)
        shrink_to(k, t0 + 0.12 + i * 0.08, s0=1.0, s1=0.22, dur=0.18)
    cam = Cam()
    cam.push(t0, t1, (0, 8.0, 2.6), 8.2, 5.8, yaw=0, pitch=6, lens=24)
    sfx(t0 + 0.10, "sneeze")
    sfx(t0 + 0.18, "pop")


@S(29, 212, 219, "Exterior wide shot of town: golden pollen bursting above streets and roofs")
def s29(t0, t1):
    bright_town()
    pollen_cloud((0, -22, 8.0), t0, t1, n=60, spread=18.0, seed=29)
    cam = Cam()
    cam.orbit(t0, t1, (0, -18, 5.0), 26.0, -22, 22, pitch=16, lens=22)
    sfx(t0 + 0.04, "whoosh")


@S(30, 219, 224, "Town street: Dog barking and car swerving as horns blare")
def s30(t0, t1):
    bright_town()
    W.dog("town_dog", (-2.8, -25, 0))
    W.car("town_car", (3.8, -23, 0), rot=25, color="#d93829")
    k = townie(30, t0, t1, "terror")
    k.pose(t0, loc=(0, -26, 0), rot=0)
    k.panic(t0, t1)
    cam = Cam()
    cam.push(t0, t1, (0, -25, 3.0), 10.5, 7.8, yaw=-8, pitch=8, lens=24)
    cam.handheld(1.6)
    sfx(t0 + 0.04, "alarm")


@S(31, 224, 231, "Then — ACHOO, a thousand times at once! Crowd of townspeople sneezing")
def s31(t0, t1):
    bright_town()
    for i in range(12):
        k = townie(31 + i, t0, t1, "shock")
        kx = -9.0 + (i % 6) * 3.6
        ky = -24.0 - (i // 6) * 3.5
        k.pose(t0, loc=(kx, ky, 0), rot=0)
        W2.sneeze(k, t0, w(225) + (i % 3) * 0.03)
    tsn = w(225)
    puff("mega_sneeze1", (-5, -22, 4.5), tsn, r=1.8)
    puff("mega_sneeze2", (5, -22, 4.5), tsn + 0.04, r=1.8)
    cam = Cam()
    cam.push(t0, t1, (0, -25.5, 3.8), 15.0, 11.0, yaw=0, pitch=14, lens=22)
    cam.crash(tsn, 22, 30, 0.08)
    cam.handheld(2.0)
    sfx(tsn, "sneeze")
    sfx(tsn + 0.04, "boom")


@S(32, 231, 236, "The whole town crowd shrinks down together in a wave of poofs")
def s32(t0, t1):
    bright_town()
    for i in range(12):
        k = townie(40 + i, t0, t1, "terror")
        kx = -9.0 + (i % 6) * 3.6
        ky = -24.0 - (i // 6) * 3.5
        k.pose(t0, loc=(kx, ky, 0), rot=0)
        shrink_to(k, t0 + 0.05 + (i % 4) * 0.04, s0=1.0, s1=0.18, dur=0.18)
    cam = Cam()
    cam.push(t0, t1, (0, -25.5, 2.5), 14.0, 10.0, yaw=0, pitch=14, lens=22)
    sfx(t0 + 0.05, "poof")
    sfx(t0 + 0.14, "pop")


@S(33, 236, 240, "Tiny townspeople looking up as school and buildings tower like mountains")
def s33(t0, t1):
    bright_town()
    for i, x in enumerate((-1.4, 0.0, 1.4)):
        k = townie(55 + i, t0, t1, "shock")
        k.pose(t0, loc=(x, -22, 0), rot=0)
        k.root.scale = (0.18, 0.18, 0.18)
    cam = Cam()
    cam.key(t0, (0, -26.0, 0.7), (0, -4, 11.0), lens=20)
    cam.key(t1, (0, -25.0, 0.6), (0, -4, 14.0), lens=20)
    sfx(t0 + 0.04, "rise")


@S(34, 240, 244, "A street puddle looks like a massive ocean next to tiny Eddie and Mia")
def s34(t0, t1):
    bright_town()
    cyl("ocean_puddle", 4.5, 0.06, (1.5, -25, 0.03), mat("puddle_blue", hexc("#2b7de9"), 0.08, spec=1.0), 32)
    E = eddie(t0, t1, "shock")
    E.pose(t0, loc=(-2.2, -26, 0), rot=0)
    E.root.scale = (0.22, 0.22, 0.22)
    M = mia(t0, t1, "shock")
    M.pose(t0, loc=(-1.2, -26, 0), rot=0)
    M.root.scale = (0.22, 0.22, 0.22)
    cam = Cam()
    cam.push(t0, t1, (-1.2, -26, 0.8), 4.2, 3.0, yaw=-15, pitch=14, lens=24)
    sfx(t0 + 0.04, "splat")


# ================================================================== OLD MAN HIGGINS (Words 244..286)
@S(35, 244, 252, "Heroic reveal: Old Man Higgins standing tall and unfazed in the street")
def s35(t0, t1):
    bright_town()
    H = higgins(t0, t1, expr="determined", scale=1.15, loc=(0, -26, 0), rot=0)
    H.act(t0 + 0.08, "cross")
    cam = Cam()
    cam.push(t0, t1, (0, -26, 4.4), 7.8, 5.6, yaw=0, pitch=4, lens=24)
    sfx(t0 + 0.05, "ding")


@S(36, 252, 259, "Close-up on Old Man Higgins: stern glasses and beard, immune to pollen")
def s36(t0, t1):
    bright_town()
    H = higgins(t0, t1, expr="determined", scale=1.15, loc=(0, -26, 0), rot=0)
    pollen_cloud((0, -26, 4.8), t0, t1, n=25, spread=2.0, seed=36)
    H.shake(t0 + 0.08, 12, 0.45)
    cam = Cam()
    cam.push(t0, t1, (0, -26, 5.0), 4.8, 3.6, yaw=-8, pitch=4, lens=28)
    sfx(t0 + 0.06, "thud")


@S(37, 259, 265, "Cats, flowers, and dust bounce harmlessly off Higgins")
def s37(t0, t1):
    bright_town()
    H = higgins(t0, t1, expr="happy", scale=1.15, loc=(0, -26, 0), rot=0)
    H.act(t0 + 0.05, "cross")
    W2.cat("hig_cat", (-1.8, -26.8, 0), rot=20)
    bouquet_prop("hig_flowers", (1.8, -26.8, 0), scale=1.2)
    pollen_cloud((0, -26, 4.2), t0, t1, n=30, spread=2.8, seed=37)
    cam = Cam()
    cam.orbit(t0, t1, (0, -26, 4.2), 6.8, -18, 18, pitch=8, lens=24)
    sfx(t0 + 0.05, "sparkle")


@S(38, 265, 272, "Everybody around Higgins shrinks down to tiny ants at his boots")
def s38(t0, t1):
    bright_town()
    H = higgins(t0, t1, expr="shock", scale=1.55, loc=(0, -25, 0), rot=0)
    for i, dx in enumerate((-3.2, -1.8, 1.8, 3.2)):
        k = townie(60 + i, t0, t1, "terror")
        k.pose(t0, loc=(dx, -26.5, 0), rot=0)
        shrink_to(k, t0 + 0.05 + i * 0.05, s0=0.85, s1=0.18, dur=0.18)
    cam = Cam()
    cam.push(t0, t1, (0, -25.5, 3.8), 11.5, 8.8, yaw=0, pitch=8, lens=22)
    sfx(t0 + 0.06, "poof")


@S(39, 272, 278, "Higgins looks down at his feet in disbelief, still full normal size")
def s39(t0, t1):
    bright_town()
    H = higgins(t0, t1, expr="shock", scale=1.4, loc=(0, -26, 0), rot=0)
    H.pose(t0 + 0.05, head=(0, 18, 0))
    H.act(t0 + 0.08, "shrug")
    cam = Cam()
    cam.push(t0, t1, (0, -26, 5.6), 7.2, 5.4, yaw=8, pitch=4, lens=24)
    sfx(t0 + 0.05, "pop")


@S(40, 278, 286, "Low angle from tiny Eddie & Mia: Giant Higgins looming like a colossus")
def s40(t0, t1):
    bright_town()
    H = higgins(t0, t1, expr="shock", scale=1.9, loc=(0, -23.5, 0), rot=0)
    E = eddie(t0, t1, "shock")
    E.pose(t0, loc=(-1.2, -27.5, 0), rot=0)
    E.root.scale = (0.22, 0.22, 0.22)
    M = mia(t0, t1, "shock")
    M.pose(t0, loc=(1.2, -27.5, 0), rot=0)
    M.root.scale = (0.22, 0.22, 0.22)
    cam = Cam()
    cam.key(t0, (0, -32.5, 2.2), (0, -24.5, 5.2), lens=22)
    cam.key(t1, (0, -30.5, 1.8), (0, -24.5, 5.8), lens=22)
    sfx(t0 + 0.04, "rise")


# ================================================================== "THEN I NOTICED SOMETHING" (Words 286..347)
@S(41, 286, 290, "Close-up on Eddie: lightbulb moment, determined grin")
def s41(t0, t1):
    bright_town()
    E = eddie(t0, t1, "joy")
    E.pose(t0, loc=(0, -26, 0), rot=0)
    E.act(t0 + 0.04, "point")
    lips(E, t0, t1)
    cam = Cam()
    cam.push(t0, t1, (0, -26, 4.3), 5.2, 3.8, yaw=0, pitch=4, lens=26)
    cam.crash(t0 + 0.05, 26, 34, 0.08)
    sfx(t0 + 0.04, "ding")


@S(42, 290, 301, "Higgins stands tall next to the school while tiny townspeople wave up at him")
def s42(t0, t1):
    bright_town()
    H = higgins(t0, t1, expr="happy", scale=1.75, loc=(0, -24.5, 0), rot=0)
    for i, dx in enumerate((-2.8, -1.4, 1.4, 2.8)):
        k = townie(70 + i, t0, t1, "joy")
        k.pose(t0, loc=(dx, -27.2, 0), rot=0)
        k.root.scale = (0.24, 0.24, 0.24)
        k.act(t0 + 0.05, "wave")
    cam = Cam()
    cam.orbit(t0, t1, (0, -25.5, 4.4), 12.0, -18, 18, pitch=8, lens=22)


@S(43, 301, 310, "Tiny Eddie climbs up Higgins's giant sneaker shoelace and cups his hands")
def s43(t0, t1):
    bright_town()
    shoe_prop("higgins_boot", (0.8, -26, 0), scale=1.8, color="#c87628", rot=0)
    E = eddie(t0, t1, "determined")
    E.root.scale = (0.32, 0.32, 0.32)
    E.pose(t0, loc=(-0.6, -26.8, 0.4), rot=0)
    E.pose(t1, loc=(0.2, -26.5, 1.85), rot=0)
    E.act(t0 + 0.2, "hands_face")
    cam = Cam()
    cam.push(t0, t1, (0.2, -26.5, 1.6), 5.2, 3.8, yaw=-12, pitch=10, lens=26)
    sfx(t0 + 0.05, "footsteps")


@S(44, 310, 315, "Tiny Eddie shouts up: HIGGINS! WE NEED A LIFT!")
def s44(t0, t1):
    bright_town()
    E = eddie(t0, t1, "shock")
    E.pose(t0, loc=(0, -26, 0), rot=0)
    E.act(t0 + 0.04, "cheer")
    lips(E, t0, t1, mode="shout")
    cam = Cam()
    cam.push(t0, t1, (0, -26, 4.3), 5.0, 3.6, yaw=0, pitch=4, lens=26)
    cam.crash(t0 + 0.05, 26, 35, 0.08)
    sfx(t0 + 0.04, "cheer")


@S(45, 315, 325, "Giant Higgins kneels and scoops up the shrunken townspeople in his hands")
def s45(t0, t1):
    bright_town()
    H = higgins(t0, t1, expr="happy", scale=1.65, loc=(0, -24.5, 0), rot=0)
    H.pose(t0, torso=(18, 0, 0), armL=(65, 20), armR=(65, -20))
    for i, dx in enumerate((-1.4, 0.0, 1.4)):
        k = townie(80 + i, t0, t1, "joy")
        k.root.scale = (0.26, 0.26, 0.26)
        k.pose(t0, loc=(dx, -26.8, 2.0), rot=0)
    cam = Cam()
    cam.push(t0, t1, (0, -25.5, 4.2), 11.2, 8.6, yaw=8, pitch=10, lens=22)
    sfx(t0 + 0.06, "whoosh")


@S(46, 325, 332, "Close-up of Higgins's palms holding tiny car, dog, Mayor, and Eddie")
def s46(t0, t1):
    bright_town()
    box("palm_platform", (6.5, 4.5, 0.55), (0, -26, 2.2), mat("skin_palm", hexc("#efd6be"), 0.45), 0.15)
    M = mayor(t0, t1, "joy")
    M.root.scale = (0.35, 0.35, 0.35)
    M.pose(t0, loc=(-1.2, -26, 2.5), rot=0)
    E = eddie(t0, t1, "joy")
    E.root.scale = (0.35, 0.35, 0.35)
    E.pose(t0, loc=(0.5, -26, 2.5), rot=0)
    d = W.dog("tiny_dog", (1.9, -26, 2.5))
    d.scale = (0.35, 0.35, 0.35)
    c = W.car("tiny_car", (-2.4, -26.2, 2.5), rot=20, color="#3880d9")
    c.scale = (0.22, 0.22, 0.22)
    cam = Cam()
    cam.push(t0, t1, (0, -26, 3.2), 6.5, 4.8, yaw=0, pitch=16, lens=24)
    sfx(t0 + 0.05, "pop")


@S(47, 332, 340, "Higgins marches down the school hallway toward the NURSE OFFICE sign")
def s47(t0, t1):
    world((0.9, 0.94, 1.0), 0.55)
    W.hallway_day()
    card("nurse_banner", 5.2, 1.8, (0, 13.5, 6.8), img_mat("nurse_sign", os.path.join(W.TEX, "nurse_sign.png"), 0.5), "-Y")
    H = higgins(t0, t1, expr="determined", scale=1.15, loc=(0, 8.5, 0), rot=0)
    H.run(t0, t1, (0, 10.5, 0), (0, 6.5, 0), rate=2.8)
    cam = Cam()
    cam.push(t0, t1, (0, 8.5, 4.2), 8.8, 6.5, yaw=0, pitch=6, lens=22)
    sfx(t0 + 0.04, "footsteps")


@S(48, 340, 347, "School Nurse holds the biggest glowing green allergy shot syringe in history")
def s48(t0, t1):
    world((0.9, 0.95, 1.0), 0.6)
    W.hallway_day()
    N = nurse(t0, t1, "joy")
    N.pose(t0, loc=(-1.0, 8.0, 0), rot=0)
    N.pose(t0, armR=(75, 10))
    syringe_prop((1.1, 7.6, 1.6), scale=1.25, rot=(0, -18, 0))
    cam = Cam()
    cam.push(t0, t1, (0.0, 8.0, 3.8), 6.8, 5.0, yaw=0, pitch=6, lens=24)
    cam.crash(t0 + 0.08, 24, 32, 0.08)
    sfx(t0 + 0.05, "sparkle")
    sfx(t0 + 0.12, "rise")


# ================================================================== PAYOFF + BUTTON (Words 347..386)
@S(49, 347, 353, "Townspeople, Eddie, and Mia pop back up to full normal size!")
def s49(t0, t1):
    bright_town()
    E = eddie(t0, t1, "joy")
    E.pose(t0, loc=(-2.0, -26, 0), rot=0)
    grow_to(E, t0 + 0.05, s0=0.22, s1=1.0, dur=0.25)
    M = mia(t0, t1, "joy")
    M.pose(t0, loc=(2.0, -26, 0), rot=0)
    grow_to(M, t0 + 0.10, s0=0.22, s1=1.0, dur=0.25)
    my = mayor(t0, t1, "joy")
    my.pose(t0, loc=(0, -25.2, 0), rot=0)
    grow_to(my, t0 + 0.15, s0=0.22, s1=1.0, dur=0.25)
    cam = Cam()
    cam.push(t0, t1, (0, -25.8, 3.8), 9.0, 6.8, yaw=0, pitch=8, lens=22)
    sfx(t0 + 0.04, "boing")
    sfx(t0 + 0.12, "pop")


@S(50, 353, 359, "The whole town cheers for Higgins with confetti falling")
def s50(t0, t1):
    bright_town()
    H = higgins(t0, t1, expr="joy", scale=1.1, loc=(0, -25, 0), rot=0)
    H.act(t0 + 0.05, "cheer")
    for i, dx in enumerate((-4.2, -2.2, 2.2, 4.2)):
        k = townie(90 + i, t0, t1, "joy")
        k.pose(t0, loc=(dx, -26.2, 0), rot=0)
        k.act(t0 + 0.05, "cheer")
        k.jump(t0 + (i % 2) * 0.12, 1.1, 0.4)
    confetti("win_conf", (0, -25, 8.0), (8, 5, 3), t0, dur=t1 - t0, n=75, seed=50)
    cam = Cam()
    cam.orbit(t0, t1, (0, -25.5, 4.0), 10.2, -16, 16, pitch=8, lens=22)
    sfx(t0 + 0.04, "cheer")
    sfx(t0 + 0.08, "confetti")


@S(51, 359, 372, "Close-up on Higgins smiling wide — then his red nose twitches!")
def s51(t0, t1):
    bright_town()
    H = higgins(t0, t1, expr="joy", scale=1.15, loc=(0, -26, 0), rot=0)
    rn = sphere("hig_rednose", 0.15, (0, -0.64, -0.06), mat("rednose", hexc("#e03a34"), 0.3, emit=hexc("#e03a34"), estr=0.5),
                parent=H.head, coll=H.coll)
    t_tw = w(370)
    H.face(t_tw, "shock")
    rn.scale = (1.0, 1.0, 1.0)
    rn.keyframe_insert("scale", frame=F(t0))
    rn.scale = (1.65, 1.65, 1.65)
    rn.keyframe_insert("scale", frame=F(t_tw))
    cam = Cam()
    cam.push(t0, t1, (0, -26, 4.9), 5.2, 3.6, yaw=0, pitch=4, lens=28)
    cam.crash(t_tw, 28, 36, 0.08)
    sfx(t_tw - 0.05, "pop")
    sfx(t_tw, "snort")


@S(52, 372, 382, "Higgins unleashes the biggest sneeze in history — shockwave poof!")
def s52(t0, t1):
    bright_town()
    H = higgins(t0, t1, expr="shock", scale=1.2, loc=(0, -25, 0), rot=0)
    E = eddie(t0, t1, "terror")
    E.pose(t0, loc=(-2.6, -26.5, 0), rot=0)
    M = mia(t0, t1, "terror")
    M.pose(t0, loc=(2.6, -26.5, 0), rot=0)
    tsn = w(374)
    W2.sneeze(H, t0, tsn)
    shrink_to(H, tsn + 0.08, s0=1.2, s1=0.08, dur=0.22)
    puff("mega_blast", (0, -22.5, 5.2), tsn + 0.05, r=2.0)
    cam = Cam()
    cam.push(t0, t1, (0, -25.8, 4.2), 8.2, 5.8, yaw=0, pitch=8, lens=24)
    cam.crash(tsn, 24, 34, 0.07)
    cam.handheld(2.4)
    sfx(tsn, "sneeze")
    sfx(tsn + 0.04, "boom")


@S(53, 382, None, "BUTTON: Eddie and Mia grab a streetlamp as the whole street shakes!")
def s53(t0, t1):
    bright_town()
    streetlamp_prop((0, -25.5, 0))
    E = eddie(t0, t1, "terror")
    E.pose(t0, loc=(-1.3, -26, 0), rot=0)
    E.act(t0 + 0.03, "hands_head", expr="terror")
    lips(E, t0, t1, mode="shout")
    M = mia(t0, t1, "terror")
    M.pose(t0, loc=(1.3, -26, 0), rot=0)
    M.act(t0 + 0.03, "hands_head", expr="terror")
    puff("final_wave", (0, -21, 5.5), t0 + 0.04, r=2.2)
    cam = Cam()
    cam.push(t0, t1, (0, -26, 4.0), 6.5, 4.6, yaw=0, pitch=6, lens=24)
    cam.handheld(2.6)
    sfx(t0 + 0.02, "wind")
    sfx(t0 + 0.08, "gasp")
