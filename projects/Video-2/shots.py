"""truth_disappear: "Don't Tell The Truth. You'll Vanish." — 36 shots keyed to script word indices (0..250)."""
from shotkit import *
from rbx import story
from rbx.story import *
import math, os, random
from mathutils import Vector

V = Video(__file__)
story.bind(V)
ST = sets


# ------------------------------------------------------------------ cast helpers
def mom(t0, t1, expr="neutral", **kw):
    return story._live(
        chars.Char("Mom", skin="#f2dbc6", shirt="#d96b8a", pants="#3a4c6e", hair="bun",
                   hair_color="#6b3e26", face="girl", sleeves="short", vneck="#f8e8ee", **kw),
        t0, t1, expr
    )


def therapist(t0, t1, expr="talk", **kw):
    return story._live(
        chars.Char("Therapist", skin="#e8c7a4", shirt="#2b6cb0", pants="#243044", hair="slick",
                   hair_color="#3b2f2f", face="mustache", sleeves="long", extras=("glasses",), **kw),
        t0, t1, expr
    )


def judge_woman(t0, t1, expr="angry", **kw):
    return story._live(
        chars.Char("Judge", skin="#e8b896", shirt="#111827", pants="#111827", hair="bun",
                   hair_color="#d4d4d8", face="girl", sleeves="long", vneck="#ffffff",
                   extras=("glasses",), **kw),
        t0, t1, expr
    )


def bailiff(t0, t1, expr="neutral", **kw):
    ch = LIB.police_officer(name="Bailiff", **kw)
    story._live(ch, t0, t1, expr)
    return ch


def reporter(t0, t1, expr="neutral", **kw):
    return story._live(
        chars.Char("Reporter", skin="#f4d2b8", shirt="#e2e8f0", pants="#334155", hair="bob",
                   hair_color="#4a3222", face="girl", sleeves="short", extras=("glasses",), **kw),
        t0, t1, expr
    )


# ------------------------------------------------------------------ fixed courtroom coordinates
# LIB.courtroom(): X=[-10..10], Y=[-8..8], Z=[0..10], window back-left, Justice Seal (0, 7.72, 6.6)
# Dais (0, 5.2, 0..1.0), Judge bench (0, 4.2, 3.85), Witness box (-5.2, 2.6, 2.3), Rail y=-4.6
JUDGE_LOC = (0.0, 5.5, 1.0)
WITNESS_LOC = (-5.2, 4.2, 0.35)
LEO_GAL_LOC = (-2.4, -6.3, 0.25)
BAILIFF_LOC = (5.3, 3.2, 0.0)
REPORTER_LOC = (-2.3, 1.7, 0.2)
EXHIBIT_LOC = (0.2, 0.6, 0.0)
JUROR_SLOTS = [
    (7.3, -1.6 + j * 1.15, 0.25) for j in range(6)
] + [
    (8.6, -1.6 + j * 1.15, 0.75) for j in range(6)
]


# ------------------------------------------------------------------ custom reusable props & set extensions
def cookie_plate(loc=(0.6, 0.5, 2.2), cookies=1):
    root = empty("cookie_plate", loc)
    Mp = mat("plate_w", hexc("#f8fafc"), 0.25)
    Mc = mat("cookie_dough", hexc("#c68b45"), 0.7)
    Mch = mat("choc_chip", hexc("#3b2314"), 0.5)
    cyl("pl_dish", 0.75, 0.08, (0, 0, 0.04), Mp, 20, parent=root)
    if cookies >= 1:
        cyl("ck_1", 0.28, 0.1, (0.05, -0.05, 0.13), Mc, 14, parent=root)
        for dx, dy in ((-0.08, 0.06), (0.1, 0.02), (0.0, -0.1)):
            sphere(f"ck_ch_{dx}_{dy}", 0.045, (0.05 + dx, -0.05 + dy, 0.18), Mch, seg=8, parent=root)
    for idx, (cx, cy) in enumerate(((-0.26, 0.14), (0.22, 0.22), (-0.1, -0.26))):
        box(f"ck_crumb_{idx}", (0.08, 0.07, 0.05), (cx, cy, 0.1), Mc, 0.01, parent=root)
    return root


def bible_prop(loc=(-4.6, 2.45, 2.31), rot=(0, 0, 14)):
    root = empty("bible", loc, rot=rot)
    M_cov = mat("bib_cov", hexc("#1e293b"), 0.5)
    M_pg = mat("bib_pg", hexc("#fef3c7"), 0.6)
    M_gold = mat("bib_g", hexc("#e0b84c"), 0.25, metal=0.8)
    box("bib_b", (0.72, 0.92, 0.24), (0, 0, 0.12), M_cov, 0.03, parent=root)
    box("bib_p", (0.64, 0.84, 0.18), (0.02, 0, 0.12), M_pg, 0.01, parent=root)
    box("bib_c1", (0.08, 0.42, 0.03), (0, 0, 0.25), M_gold, 0.005, parent=root)
    box("bib_c2", (0.28, 0.08, 0.03), (0, 0.06, 0.25), M_gold, 0.005, parent=root)
    return root


def broken_trophy_case(loc=EXHIBIT_LOC):
    root = empty("trophy_exhibit", loc)
    M_ped = ST.wood("ex_ped", "#5a3824", "#8a5a3a", 1.8)
    M_gl = mat("ex_glass", (0.82, 0.94, 1.0), 0.08, alpha=0.28, spec=1.0)
    M_gold = mat("ex_gold", hexc("#facc15"), 0.2, metal=0.9)
    M_tb = mat("ex_tbase", hexc("#451a03"), 0.4)
    box("ex_base", (1.8, 1.4, 1.8), (0, 0, 0.9), M_ped, 0.04, parent=root)
    # shattered left/back glass walls + knocked over trophy on pedestal top (z=1.8)
    box("ex_gl_back", (1.6, 0.06, 1.4), (0, 0.6, 2.5), M_gl, 0.01, parent=root)
    box("ex_gl_left", (0.06, 1.2, 1.4), (-0.75, 0, 2.5), M_gl, 0.01, parent=root)
    for k, (sx, sy, rz) in enumerate(((-0.3, -0.5, 22), (0.4, -0.7, -34), (-0.7, -0.3, 48), (0.6, 0.2, -18))):
        box(f"ex_shard_{k}", (0.35, 0.28, 0.04), (sx, sy, 0.03), M_gl, 0.005, rot=(8, 4, rz), parent=root)
    tr = empty("ex_tr", (0.1, -0.1, 2.05), parent=root, rot=(78, 0, -28))
    box("ex_tr_b", (0.5, 0.5, 0.25), (0, 0, 0.12), M_tb, 0.02, parent=tr)
    cyl("ex_tr_s", 0.1, 0.4, (0, 0, 0.45), M_gold, 12, parent=tr)
    cyl("ex_tr_c", 0.32, 0.5, (0, 0, 0.9), M_gold, 16, parent=tr)
    return root


def empty_judge_robe(loc=JUDGE_LOC):
    """Hollow upright black judge robe & white collar hovering motionless behind the bench."""
    root = empty("EmptyRobe", loc)
    Mr = mat("er_black", hexc("#111827"), 0.52)
    Mw = mat("er_white", hexc("#f8fafc"), 0.35)
    # lower skirt & upright torso column
    box("er_skirt", (2.1, 1.1, 2.0), (0, 0, 1.0), Mr, 0.08, parent=root)
    box("er_torso", (2.0, 1.0, 2.0), (0, 0, 3.0), Mr, 0.09, parent=root)
    # hollow sleeves hanging empty
    box("er_slvL", (0.95, 0.95, 1.4), (1.5, 0, 2.85), Mr, 0.08, rot=(0, 8, 0), parent=root)
    box("er_slvR", (0.95, 0.95, 1.4), (-1.5, 0, 2.85), Mr, 0.08, rot=(0, -8, 0), parent=root)
    # white collar v-neck
    poly_extrude("er_collar", [(-0.46, 0.0), (0.46, 0.0), (0.0, -0.58)], 0.04, (0, -0.51, 3.98), Mw,
                 rot=(90, 0, 0), parent=root)
    return root


def remove_prefix(prefix):
    for ob in list(D.objects):
        if ob.name.startswith(prefix):
            D.objects.remove(ob, do_unlink=True)


def bright_town():
    R = town_scene()
    W.sun(4.5, rot=(48, 0, 20))
    light("tw_front_key", "AREA", (0, -42, 14), 9000, (1.0, 0.98, 0.94), 22, target=(0, -25, 3.5))
    light("tw_rim_fill", "AREA", (0, -10, 14), 4500, (0.9, 0.95, 1.0), 18, target=(0, -26, 3.5))
    return R


def build_courtroom(t0, t1, *, eddie=True, leo=True, judge=True, bailiff_on=True,
                    reporter_on=True, jurors=12, spectators=True, trophy_exhibit=True,
                    static_gavel=True, empty_robe=False, float_mics=False):
    """Consistent courtroom world builder with fixed landmarks across every shot."""
    c = LIB.courtroom()
    if not static_gavel:
        remove_prefix("CR_gavel")
    m_oak = ST.wood("CR_oak2", "#6e4229", "#a06a45", 2.0)
    m_dark = ST.wood("CR_dark2", "#3e2414", "#623b22", 2.4)
    # Witness riser step behind CR_witness so character upper torso/arms sit cleanly above bench
    box("CR_wit_step", (2.4, 1.8, 0.35), (-5.2, 4.2, 0.175), m_dark, 0.03, coll=c)
    bible_prop((-4.6, 2.45, 2.31))
    # Stenographer desk for Court Reporter
    box("CR_steno_tbl", (1.9, 1.2, 0.18), (-2.3, 0.65, 1.95), m_oak, 0.03, coll=c)
    for lx in (-0.8, 0.8):
        box(f"CR_stl_{lx}", (0.14, 0.14, 1.9), (-2.3 + lx, 0.65, 0.95), m_dark, 0.02, coll=c)
    box("CR_steno_pad", (0.6, 0.45, 0.08), (-2.3, 0.65, 2.08), mat("st_pad", hexc("#f8fafc"), 0.4), 0.01, coll=c)
    # Gallery benches behind rail y=-4.6
    for gx in (-3.6, 3.6):
        box(f"CR_gbench_{gx}", (6.0, 1.4, 0.22), (gx, -6.3, 1.15), m_oak, 0.03, coll=c)
        box(f"CR_gbk_{gx}", (6.0, 0.2, 1.2), (gx, -6.95, 1.8), m_oak, 0.03, coll=c)
    # 12-seat two-tier Jury Box along right side (x=7.0..9.3, y=-2.2..4.6)
    box("CR_jury_base", (2.8, 7.2, 0.25), (8.0, 1.25, 0.125), m_dark, 0.03, coll=c)
    box("CR_jury_tier2", (1.4, 7.2, 0.5), (8.7, 1.25, 0.5), m_dark, 0.03, coll=c)
    box("CR_jury_rail", (0.2, 7.2, 1.9), (6.6, 1.25, 0.95), m_oak, 0.03, coll=c)
    for ky in (-2.3, 4.8):
        box(f"CR_jend_{ky}", (2.8, 0.2, 1.9), (8.0, ky, 0.95), m_oak, 0.03, coll=c)
    if trophy_exhibit:
        broken_trophy_case()
    # Extra counsel desk mics (one on witness stand already at CR_wmic)
    LIB.prop_desk_mic("CR_cmic_L", (-4.2, -1.6, 2.21), coll=c)
    LIB.prop_desk_mic("CR_cmic_R", (4.2, -1.6, 2.21), coll=c)
    if float_mics:
        for pref in ("CR_wmic", "CR_cmic_L", "CR_cmic_R"):
            for ob in D.objects:
                if ob.name.startswith(pref):
                    ob.location.z += 1.35
                    noise(ob, "location", 2, 0.12, 8)
    if empty_robe:
        empty_judge_robe(JUDGE_LOC)

    cast = {"jurors": [], "specs": []}
    if eddie:
        E = story.eddie(t0, t1, "worried", loc=WITNESS_LOC, rot=12)
        cast["eddie"] = E
    if leo:
        L = story.leo(t0, t1, "worried", loc=LEO_GAL_LOC, rot=165)
        L.pose(t0, loc=LEO_GAL_LOC, rot=165, legL=(82, 4), legR=(82, -4))
        cast["leo"] = L
    if judge:
        J = judge_woman(t0, t1, "angry", loc=JUDGE_LOC, rot=0)
        cast["judge"] = J
    if bailiff_on:
        B = bailiff(t0, t1, "neutral", loc=BAILIFF_LOC, rot=-18)
        cast["bailiff"] = B
    if reporter_on:
        R = reporter(t0, t1, "neutral", loc=REPORTER_LOC, rot=0)
        R.pose(t0, loc=REPORTER_LOC, rot=0, legL=(80, 4), legR=(80, -4))
        cast["reporter"] = R
    if jurors > 0:
        for i in range(min(jurors, 12)):
            jl = JUROR_SLOTS[i]
            jr = townie(10 + i, t0, t1, "neutral", scale=0.88)
            jr.pose(t0, loc=jl, rot=-88, legL=(78, 3), legR=(78, -3))
            cast["jurors"].append(jr)
    if spectators:
        for idx, (sx, sd) in enumerate(((-4.6, 20), (-0.4, 21), (2.4, 22), (4.8, 23))):
            sp = townie(sd, t0, t1, "neutral", scale=0.92)
            sp.pose(t0, loc=(sx, -6.3, 0.25), rot=180, legL=(82, 3), legR=(82, -3))
            cast["specs"].append(sp)
    return c, cast


def build_elevator_lobby():
    """Courthouse marble hallway with open/plummeting elevator bay & warning beacon."""
    c = W.hallway_day()["coll"]
    # Add elevator steel shaft doors & floor dial at back-center y=18
    Ms = mat("el_steel", hexc("#94a3b8"), 0.25, metal=0.85)
    Md = mat("el_dark", hexc("#0f172a"), 0.85)
    Mg = mat("el_gold", hexc("#e0b84c"), 0.25, metal=0.85)
    Mr = ST.emit_mat("el_red", hexc("#ef4444"), 7.0)
    Ma = ST.emit_mat("el_amber", hexc("#f59e0b"), 4.5)
    box("el_jambL", (0.7, 0.5, 8.6), (-2.75, 17.3, 4.3), Mg, 0.04, coll=c)
    box("el_jambR", (0.7, 0.5, 8.6), (2.75, 17.3, 4.3), Mg, 0.04, coll=c)
    box("el_header", (6.2, 0.5, 0.8), (0, 17.3, 8.5), Mg, 0.04, coll=c)
    box("el_void", (4.8, 1.4, 8.2), (0, 18.2, 4.1), Md, 0.01, coll=c)
    # elevator doors slightly pried open showing dark empty shaft inside
    box("el_doorL", (2.1, 0.22, 8.0), (-1.55, 17.4, 4.0), Ms, 0.03, coll=c)
    box("el_doorR", (2.1, 0.22, 8.0), (1.55, 17.4, 4.0), Ms, 0.03, coll=c)
    # empty operator stool sitting outside shaft
    box("el_stool_top", (1.2, 1.2, 0.18), (3.8, 15.6, 1.4), Ms, 0.03, coll=c)
    cyl("el_stool_leg", 0.14, 1.4, (3.8, 15.6, 0.7), Ms, 12, coll=c)
    # Overhead floor indicator ("DOWN / OUT OF ORDER") + alarm beacon
    box("el_ind_bg", (2.6, 0.2, 0.9), (0, 17.1, 9.3), Md, 0.03, coll=c)
    text("el_ind_txt", "FLOOR 1 !", (0, 16.95, 9.15), 0.42, Mr, rot=(90, 0, 0), coll=c)
    sphere("el_beacon", 0.35, (0, 17.1, 10.2), Mr, seg=14, coll=c)
    box("el_rope1", (0.08, 0.08, 8.2), (-0.35, 18.0, 4.1), Ma, 0.01, coll=c)
    box("el_rope2", (0.08, 0.08, 8.2), (0.35, 18.0, 4.1), Ma, 0.01, coll=c)
    lt = light("el_alarm_lt", "POINT", (0, 16.0, 9.5), 2400, (1.0, 0.25, 0.2), 1.5, coll=c)
    fx.flicker(lt, 0.7, 8.0)
    return c


# ================================================================== 0-6s HOOK (Words 0..18)
@S(1, 0, 6, "HOOK: Kitchen/Living room — Eddie insists he didn't eat the last cookie")
def s01(t0, t1):
    locs.living_room()
    cookie_plate((0.4, 0.4, 2.2), cookies=1)
    M = mom(t0, t1, "angry", loc=(-1.6, 3.5, 0), rot=-24)
    M.act(t0 + 0.05, "cross")
    E = eddie(t0, t1, "worried", loc=(1.4, 3.3, 0), rot=20)
    E.act(t0 + 0.04, "shrug", expr="worried")
    lips(E, t0, t1)
    cam = Cam()
    cam.push(t0, t1, (0.0, 3.2, 3.5), 7.8, 6.4, yaw=-6, pitch=6, lens=24)
    cam.handheld(1.0)


@S(2, 6, 11, "Medium past Mom onto Eddie eyeing the cookie crumb plate nervously")
def s02(t0, t1):
    locs.living_room()
    cookie_plate((0.4, 0.4, 2.2), cookies=0)
    M = mom(t0, t1, "furious", loc=(-1.6, 3.5, 0), rot=-28)
    M.act(t0 + 0.03, "point_l")
    E = eddie(t0, t1, "sus", loc=(1.4, 3.3, 0), rot=14)
    lips(E, t0, t1)
    E.face(w(9), "panic")
    cam = Cam()
    cam.push(t0, t1, (0.8, 3.2, 3.8), 6.2, 4.9, yaw=18, pitch=5, lens=26)
    sfx(t0 + 0.06, "chat")


@S(3, 11, 15, "Eddie vanishes mid-sentence! Mom recoils staring at empty space")
def s03(t0, t1):
    locs.living_room()
    cookie_plate((0.4, 0.4, 2.2), cookies=0)
    M = mom(t0, t1, "shock", loc=(-1.6, 3.5, 0), rot=-32)
    E = eddie(t0, t1, "terror", loc=(1.4, 3.3, 0), rot=14)
    tv = w(12)
    W2.vanish(E, tv)
    W2.poof("ed_hook", (1.4, 3.3, 2.4), tv, s=0.95)
    M.act(tv + 0.05, "hands_head", expr="terror")
    cam = Cam()
    cam.push(t0, t1, (0.1, 3.4, 3.5), 7.4, 6.0, yaw=0, pitch=5, lens=24)
    cam.crash(tv, 24, 32, 0.08)
    cam.handheld(1.4)
    sfx(tv, "poof")
    sfx(tv + 0.08, "gasp")


@S(4, 15, 18, "For eleven seconds — empty spot beside clock card ticking; faint shimmer")
def s04(t0, t1):
    locs.living_room()
    cookie_plate((0.4, 0.4, 2.2), cookies=0)
    box("clk11_fr", (2.4, 0.14, 2.4), (2.2, 8.6, 7.6), mat("clk_f", hexc("#1e293b"), 0.4), 0.03)
    card("clk11", 2.1, 2.1, (2.2, 8.5, 7.6), img_mat("clock12", os.path.join(W.TEX, "clock_1200.png"), 0.45), "-Y")
    M = mom(t0, t1, "terror", loc=(-1.6, 3.5, 0), rot=-40)
    M.act(t0, "hands_face", expr="terror")
    M.shake(t0 + 0.1, 16)
    cam = Cam()
    cam.orbit(t0, t1, (0.1, 3.8, 3.8), 7.8, -10, 10, pitch=5, lens=23)
    sfx(t0 + 0.05, "ding")


# ================================================================== 6-11s WORLD RULE (Words 18..37)
@S(5, 18, 23, "RULE: Sunny town street — two kids chatting on sidewalk")
def s05(t0, t1):
    bright_town()
    E = eddie(t0, t1, "talk", loc=(-1.4, -26.5, 0), rot=-24)
    L = story.leo(t0, t1, "happy", loc=(1.4, -26.5, 0), rot=24)
    lips(E, t0, t1)
    cam = Cam()
    cam.push(t0, t1, (0.0, -26.5, 3.4), 8.2, 6.8, yaw=-8, pitch=6, lens=24)
    cam.handheld(0.8)


@S(6, 23, 29, "Telling the truth makes you disappear right on the sidewalk")
def s06(t0, t1):
    bright_town()
    E = eddie(t0, t1, "shock", loc=(-1.4, -26.5, 0), rot=-24)
    L = story.leo(t0, t1, "neutral", loc=(1.4, -26.5, 0), rot=24)
    tv = w(28)
    W2.vanish(E, tv)
    W2.poof("rule_v1", (-1.4, -26.5, 2.4), tv, s=0.9)
    L.act(tv + 0.04, "recoil", expr="shock")
    cam = Cam()
    cam.push(t0, t1, (0.0, -26.5, 3.4), 7.4, 5.8, yaw=8, pitch=5, lens=24)
    cam.crash(tv, 24, 32, 0.08)
    sfx(tv, "teleport")


@S(7, 29, 37, "Park: Big truth = huge flash vanish, hat drops behind")
def s07(t0, t1):
    LIB.park_day()
    P = story.pickle(t0, t1, "worried")
    P.pose(t0, loc=(0.0, -0.8, 0), rot=-8)
    lips(P, t0, w(34))
    P.act(w(32), "hands_head", expr="terror")
    tv = w(35)
    W2.vanish(P, tv)
    W2.poof("rule_big", (0.0, -0.8, 2.4), tv, s=1.4)
    cam = Cam()
    cam.orbit(t0, t1, (0.0, -0.5, 3.3), 7.6, -14, 14, pitch=6, lens=24)
    sfx(tv, "poof")
    sfx(w(36), "thud")


# ================================================================== 11-20s SOCIETY EXAMPLES (Words 37..71)
@S(8, 37, 45, "Couples therapist working by phone beside empty chair")
def s08(t0, t1):
    LIB.nurse_office()
    remove_prefix("NO_sign")
    remove_prefix("NO_chart")
    remove_prefix("NO_cross")
    box("TH_sign_bg", (5.2, 0.14, 1.0), (0.0, 5.74, 6.8), mat("th_bg", hexc("#2b6cb0"), 0.4), 0.04)
    text("TH_sign_txt", "COUPLES THERAPY", (0.0, 5.64, 6.68), 0.42, mat("th_w", (1, 1, 1), 0.35), rot=(90, 0, 0))
    th = therapist(t0, t1, "talk", loc=(-4.0, 3.1, 0.15), rot=-8)
    th.pose(t0, loc=(-4.0, 3.1, 0.15), rot=-8, legL=(80, 4), legR=(80, -4))
    th.act(t0 + 0.04, "phone", expr="worried")
    lips(th, t0, t1)
    LIB.prop_phone("th_ph1", (-3.3, 1.4, 2.42))
    LIB.prop_phone("th_ph2", (-2.7, 1.6, 2.42))
    cam = Cam()
    cam.push(t0, t1, (-3.1, 2.6, 3.2), 7.4, 5.8, yaw=-14, pitch=6, lens=24)
    sfx(w(43), "click")


@S(9, 45, 56, "Police station: Officer calmly waits for suspect instead of lie detector")
def s09(t0, t1):
    LIB.police_station()
    ofc = LIB.police_officer("Det", loc=(-2.2, 1.0, 0), rot=-24)
    story._live(ofc, t0, t1, "smug")
    ofc.act(t0 + 0.06, "cross", expr="bored")
    sus = LIB.robber("Suspect", loc=(2.0, 1.0, 0), rot=26)
    story._live(sus, t0, t1, "scared")
    sus.shake(t0 + 0.2, 16)
    cam = Cam()
    cam.orbit(t0, t1, (0.0, 1.2, 3.2), 8.2, -10, 12, pitch=6, lens=23)
    sfx(w(52), "crickets")


@S(10, 56, 61, "Bedroom: Mom asks Dad outfit question in front of vanity")
def s10(t0, t1):
    world((0.88, 0.92, 1.0), 0.6)
    sets.bedroom()
    M = mom(t0, t1, "happy", loc=(-1.7, 2.0, 0), rot=-26)
    M.act(t0 + 0.05, "lean")
    D_ch = chars.dad()
    story._live(D_ch, t0, t1, "worried")
    D_ch.pose(t0, loc=(1.7, 2.0, 0), rot=26)
    cam = Cam()
    cam.push(t0, t1, (0.0, 2.2, 3.4), 7.8, 6.4, yaw=6, pitch=6, lens=24)


@S(11, 61, 67, "Mom tilts head asking 'does this make me look old'")
def s11(t0, t1):
    world((0.88, 0.92, 1.0), 0.6)
    sets.bedroom()
    M = mom(t0, t1, "sus", loc=(-1.4, 2.2, 0), rot=-16)
    lips(M, t0, t1)
    M.act(t0 + 0.04, "shrug", expr="sus")
    cam = Cam()
    cam.push(t0, t1, (-1.3, 2.2, 3.9), 5.6, 4.4, yaw=14, pitch=4, lens=26)


@S(12, 67, 71, "Dad sweats forcing fake grin & shaking head honestly-free")
def s12(t0, t1):
    world((0.88, 0.92, 1.0), 0.6)
    sets.bedroom()
    D_ch = chars.dad()
    story._live(D_ch, t0, t1, "panic")
    D_ch.pose(t0, loc=(1.4, 2.2, 0), rot=16)
    D_ch.face(t0 + 0.15, "grin")
    D_ch.act(t0 + 0.15, "cheer", expr="grin")
    D_ch.shake(t0 + 0.25, 18)
    cam = Cam()
    cam.push(t0, t1, (1.3, 2.2, 3.9), 5.6, 4.4, yaw=-14, pitch=4, lens=26)
    sfx(t0 + 0.15, "rimshot")


# ================================================================== 20-29s PIVOT & COURTROOM SETUP (Words 71..108)
@S(13, 71, 79, "PIVOT: Wide establishing courtroom — Eddie escorted in as witness")
def s13(t0, t1):
    _, cast = build_courtroom(t0, t1, eddie=False)
    E = story.eddie(t0, t1, "scared", loc=(-1.4, -3.5, 0), rot=150)
    E.walk(t0, t1, (-1.2, -3.6, 0), (-4.4, 1.6, 0.2), rate=2.2)
    cam = Cam()
    cam.push(t0, t1, (-0.4, 1.2, 3.6), 11.8, 9.4, yaw=-10, pitch=12, lens=21)
    sfx(t0 + 0.04, "whoosh")


@S(14, 79, 85, "Courtroom low pan across Justice seal, jury box, broken trophy exhibit")
def s14(t0, t1):
    build_courtroom(t0, t1, eddie=True)
    cam = Cam()
    cam.orbit(t0, t1, (0.0, 2.6, 3.8), 10.6, 20, -16, pitch=8, lens=21)
    sfx(w(81), "door")


@S(15, 85, 91, "The judge looks sternly down from the dais bench")
def s15(t0, t1):
    _, cast = build_courtroom(t0, t1)
    J = cast["judge"]
    J.face(t0, "angry")
    J.act(t0 + 0.05, "lean", expr="angry")
    cam = Cam()
    cam.key(t0, (1.8, 0.4, 4.3), up(JUDGE_LOC, 3.8), lens=25)
    cam.key(t1, (1.4, 1.6, 4.2), up(JUDGE_LOC, 3.8), lens=25)


@S(16, 91, 103, "Judge points toward witness stand & shattered trophy case exhibit")
def s16(t0, t1):
    _, cast = build_courtroom(t0, t1)
    J = cast["judge"]
    J.act(t0 + 0.05, "point_l", expr="furious")
    lips(J, t0, t1, mode="shout")
    cam = Cam()
    cam.key(t0, (2.2, 0.2, 4.2), (0.0, 3.8, 3.6), lens=23)
    cam.key(t1, (1.6, 1.2, 4.1), (0.0, 3.8, 3.6), lens=23)
    sfx(w(99), "hammer")


@S(17, 103, 108, "FLASHBACK: School hallway — Leo stands panicked over smashed trophy case")
def s17(t0, t1):
    W.hallway_day()
    broken_trophy_case((0.0, 4.5, 0))
    L = story.leo(t0, t1, "terror", loc=(-1.3, 5.2, 0), rot=-25)
    L.act(t0 + 0.04, "recoil", expr="terror")
    cam = Cam()
    cam.push(t0, t1, (-0.5, 4.8, 3.4), 7.2, 5.6, yaw=12, pitch=6, lens=24)
    cam.crash(w(105), 24, 32, 0.08)
    sfx(t0 + 0.02, "whoosh")
    sfx(w(106), "window")


# ================================================================== 29-35.5s CONFESSION & VANISH (Words 108..131)
@S(18, 108, 118, "Witness stand: Eddie places hand on Bible, mouth opens nervously")
def s18(t0, t1):
    _, cast = build_courtroom(t0, t1)
    E = cast["eddie"]
    E.act(t0 + 0.05, "reach", expr="worried")
    E.face(w(115), "gasp")
    cam = Cam()
    cam.push(t0, t1, up(WITNESS_LOC, 3.5), 6.2, 5.0, yaw=22, pitch=5, lens=24)


@S(19, 118, 126, "Eddie strains trying to lie 'no' — glancing between Judge & Leo")
def s19(t0, t1):
    _, cast = build_courtroom(t0, t1)
    E = cast["eddie"]
    E.face(t0, "panic")
    E.shake(t0 + 0.06, 20)
    E.face(w(122), "side_r")
    lips(E, w(121), w(124))
    cam = Cam()
    cam.push(t0, t1, up(WITNESS_LOC, 4.0), 5.0, 4.1, yaw=16, pitch=4, lens=27)
    cam.handheld(1.1)
    sfx(w(122), "snort")


@S(20, 126, 131, "'...Leo.' Gone! Eddie pops away leaving empty witness stand")
def s20(t0, t1):
    _, cast = build_courtroom(t0, t1)
    E = cast["eddie"]
    E.face(t0, "scared")
    lips(E, t0, w(127))
    tv = w(127)
    W2.vanish(E, tv)
    W2.poof("ed_court", up(WITNESS_LOC, 2.6), tv, s=1.0)
    cam = Cam()
    cam.push(t0, t1, up(WITNESS_LOC, 3.6), 5.8, 4.6, yaw=20, pitch=5, lens=25)
    cam.crash(tv, 25, 34, 0.08)
    sfx(tv, "poof")
    sfx(tv + 0.06, "pop")


# ================================================================== 35.5-42s CHAIN REACTION & LEO VANISHES (Words 131..159)
@S(21, 131, 142, "The whole courtroom flickers as witness stand sits empty")
def s21(t0, t1):
    c, cast = build_courtroom(t0, t1, eddie=False)
    for ob in c.objects:
        if ob.type == "LIGHT":
            fx.flicker(ob, 0.65, 9.0)
    cast["judge"].act(t0 + 0.1, "shock")
    cast["bailiff"].act(t0 + 0.12, "shock")
    for jr in cast["jurors"][:6]:
        jr.face(t0 + 0.1, "gasp")
    cam = Cam()
    cam.orbit(t0, t1, (0.0, 2.0, 3.6), 11.4, -16, 16, pitch=10, lens=21)
    cam.handheld(1.3)
    sfx(w(140), "glitch")


@S(22, 142, 151, "Leo shoots up from gallery yelling 'WAIT THAT'S NOT—'")
def s22(t0, t1):
    _, cast = build_courtroom(t0, t1, eddie=False)
    L = cast["leo"]
    L.pose(t0, loc=LEO_GAL_LOC, rot=165, legL=(82, 4), legR=(82, -4))
    L.pose(t0 + 0.12, loc=(LEO_GAL_LOC[0], LEO_GAL_LOC[1], 0.25), rot=165,
           legL=(0, 0), legR=(0, 0), armL=(-120, 10), armR=(-95, -12))
    L.act(t0 + 0.16, "point", expr="panic")
    lips(L, w(147), t1, mode="shout")
    for sp in cast["specs"]:
        sp.face(t0 + 0.15, "gasp")
    cam = Cam()
    cam.push(t0, t1, up(LEO_GAL_LOC, 3.6), 6.2, 4.9, yaw=158, pitch=6, lens=25)
    cam.handheld(1.2)
    sfx(w(143), "gasp")


@S(23, 151, 159, "Leo vanishes mid-denial, admitting it by accident!")
def s23(t0, t1):
    _, cast = build_courtroom(t0, t1, eddie=False)
    L = cast["leo"]
    L.act(t0, "point", expr="terror")
    tv = w(153)
    W2.vanish(L, tv)
    W2.poof("leo_gal", up(LEO_GAL_LOC, 2.6), tv, s=1.0)
    for sp in cast["specs"]:
        sp.act(tv + 0.05, "hands_face", expr="terror")
    cam = Cam()
    cam.push(t0, t1, up(LEO_GAL_LOC, 3.6), 5.8, 4.6, yaw=162, pitch=6, lens=25)
    cam.crash(tv, 25, 33, 0.08)
    sfx(tv, "poof")
    sfx(tv + 0.05, "pop")


# ================================================================== 42-47.4s JUDGE VANISHES (Words 159..178)
@S(24, 159, 164, "Judge raises gavel high and SLAMS it onto the oak bench")
def s24(t0, t1):
    c, cast = build_courtroom(t0, t1, eddie=False, leo=False, static_gavel=False)
    J = cast["judge"]
    J.pose(t0, loc=JUDGE_LOC, rot=0, armR=(-135, -8))
    J.pose(w(161), loc=JUDGE_LOC, rot=0, armR=(-35, -4))
    gv = LIB.prop_gavel("AnimGavel", (1.4, 3.6, 4.4), coll=c)
    for ob in gv.objects:
        if ob.name.startswith("AnimGavel"):
            ob.keyframe_insert("location", frame=F(t0))
            ob.location.z -= 0.55
            ob.keyframe_insert("location", frame=F(w(161)))
    cam = Cam()
    cam.push(t0, t1, (0.2, 4.6, 4.3), 5.8, 4.6, yaw=-14, pitch=4, lens=25)
    cam.handheld(1.2)
    sfx(w(161), "hammer")


@S(25, 164, 175, "Judge shouts 'ORDER! Both witnesses are invisible, we cannot have—'")
def s25(t0, t1):
    _, cast = build_courtroom(t0, t1, eddie=False, leo=False)
    J = cast["judge"]
    J.act(t0 + 0.04, "fists", expr="furious")
    lips(J, t0, t1, mode="shout")
    cam = Cam()
    cam.push(t0, t1, (-0.2, 4.4, 4.2), 7.2, 5.8, yaw=16, pitch=5, lens=24)
    cam.handheld(1.1)


@S(26, 175, 178, "Judge vanishes mid-sentence leaving her upright empty robe!")
def s26(t0, t1):
    c, cast = build_courtroom(t0, t1, eddie=False, leo=False)
    J = cast["judge"]
    er = empty_judge_robe(JUDGE_LOC)
    tv = w(176)
    for ob in er.children:
        sets.set_obj_visible(ob, t0, False)
        sets.set_obj_visible(ob, tv - 1.0 / 30, False)
        sets.set_obj_visible(ob, tv, True)
    W2.vanish(J, tv)
    W2.poof("judge_pop", up(JUDGE_LOC, 2.8), tv, s=1.05)
    cam = Cam()
    cam.push(t0, t1, up(JUDGE_LOC, 3.6), 6.0, 4.8, yaw=-10, pitch=4, lens=25)
    cam.crash(tv, 25, 33, 0.08)
    sfx(tv, "poof")
    sfx(tv + 0.05, "pop")


# ================================================================== 47.4-54.5s DOMINO VANISHES (Words 178..209)
@S(27, 178, 181, "Then the bailiff pops out beside the dais")
def s27(t0, t1):
    _, cast = build_courtroom(t0, t1, eddie=False, leo=False, judge=False, empty_robe=True)
    B = cast["bailiff"]
    B.face(t0, "worried")
    lips(B, t0, w(180))
    tv = w(180)
    W2.vanish(B, tv)
    W2.poof("bail_pop", up(BAILIFF_LOC, 2.2), tv, s=0.85)
    cam = Cam()
    cam.key(t0, (2.2, -1.2, 3.9), up(BAILIFF_LOC, 3.2), lens=24)
    cam.key(t1, (2.6, -0.2, 3.8), up(BAILIFF_LOC, 3.2), lens=24)
    sfx(tv, "pop")


@S(28, 181, 185, "Then the court reporter vanishes at the stenographer desk")
def s28(t0, t1):
    _, cast = build_courtroom(t0, t1, eddie=False, leo=False, judge=False, bailiff_on=False, empty_robe=True)
    R = cast["reporter"]
    R.face(t0, "gasp")
    lips(R, t0, w(184))
    tv = w(184)
    W2.vanish(R, tv)
    W2.poof("rep_pop", up(REPORTER_LOC, 2.0), tv, s=0.85)
    cam = Cam()
    cam.key(t0, (1.4, -1.8, 3.9), up(REPORTER_LOC, 2.8), lens=24)
    cam.key(t1, (0.8, -0.8, 3.8), up(REPORTER_LOC, 2.8), lens=24)
    sfx(tv, "pop")


@S(29, 185, 198, "Jury box front row (jurors 1-6) vanish like dominoes!")
def s29(t0, t1):
    _, cast = build_courtroom(t0, t1, eddie=False, leo=False, judge=False,
                              bailiff_on=False, reporter_on=False, empty_robe=True)
    jrs = cast["jurors"]
    dt = (t1 - t0) / 6.5
    for idx in range(6):
        tv = t0 + 0.15 + idx * dt
        jrs[idx].face(max(t0, tv - 0.18), "gasp")
        W2.vanish(jrs[idx], tv)
        W2.poof(f"jpop_{idx}", up(JUROR_SLOTS[idx], 2.0), tv, s=0.55)
        sfx(tv, "pop", 0.75)
    for jr in jrs[6:]:
        jr.face(t0 + 0.2, "panic")
    cam = Cam()
    cam.key(t0, (0.2, -2.0, 4.1), (8.0, 1.2, 2.8), lens=21)
    cam.key(t1, (1.5, -0.8, 3.9), (8.0, 1.2, 2.8), lens=21)


@S(30, 198, 209, "Jury box back row (jurors 7-12) whisper truths & vanish one by one")
def s30(t0, t1):
    _, cast = build_courtroom(t0, t1, eddie=False, leo=False, judge=False,
                              bailiff_on=False, reporter_on=False, empty_robe=True)
    jrs = cast["jurors"]
    for jr in jrs[:6]:
        jr.set_visible(t0, False)
    dt = (t1 - t0) / 6.5
    for k, idx in enumerate(range(6, 12)):
        tv = t0 + 0.15 + k * dt
        jrs[idx].face(max(t0, tv - 0.2), "worried")
        lips(jrs[idx], max(t0, tv - 0.3), tv)
        W2.vanish(jrs[idx], tv)
        W2.poof(f"jpop_{idx}", up(JUROR_SLOTS[idx], 2.0), tv, s=0.55)
        sfx(tv, "pop", 0.75)
    cam = Cam()
    cam.key(t0, (1.6, -1.8, 4.3), (8.6, 1.6, 3.1), lens=21)
    cam.key(t1, (2.6, 0.2, 4.1), (8.6, 1.6, 3.1), lens=21)


# ================================================================== 54.5-59.2s EMPTY COURTROOM VISUALS (Words 209..225)
@S(31, 209, 214, "High sweeping overview of the completely empty courtroom")
def s31(t0, t1):
    build_courtroom(t0, t1, eddie=False, leo=False, judge=False, bailiff_on=False,
                    reporter_on=False, jurors=0, spectators=False, empty_robe=True)
    cam = Cam()
    cam.orbit(t0, t1, (0.0, 1.8, 3.4), 12.6, -14, 14, pitch=14, lens=20)


@S(32, 214, 219, "Floating microphones bob gently in empty courtroom air")
def s32(t0, t1):
    build_courtroom(t0, t1, eddie=False, leo=False, judge=False, bailiff_on=False,
                    reporter_on=False, jurors=0, spectators=False, empty_robe=True, float_mics=True)
    cam = Cam()
    cam.push(t0, t1, (-4.5, 1.6, 3.5), 5.6, 4.4, yaw=18, pitch=5, lens=24)
    sfx(t0 + 0.08, "sparkle")


@S(33, 219, 225, "Push in on empty black judge robe standing upright behind dais")
def s33(t0, t1):
    build_courtroom(t0, t1, eddie=False, leo=False, judge=False, bailiff_on=False,
                    reporter_on=False, jurors=0, spectators=False, empty_robe=True, float_mics=True)
    cam = Cam()
    cam.push(t0, t1, up(JUDGE_LOC, 3.0), 6.4, 4.8, yaw=-12, pitch=5, lens=24)
    sfx(t0 + 0.05, "wind")


# ================================================================== 59.2-65.8s ELEVATOR BUTTON (Words 225..250)
@S(34, 225, 235, "Floating witness mic vibrates as invisible Leo panics right next to me")
def s34(t0, t1):
    build_courtroom(t0, t1, eddie=False, leo=False, judge=False, bailiff_on=False,
                    reporter_on=False, jurors=0, spectators=False, empty_robe=True, float_mics=True)
    for ob in D.objects:
        if ob.name.startswith("CR_wmic"):
            noise(ob, "rotation_euler", 0, 0.14, 4)
            noise(ob, "rotation_euler", 1, 0.14, 4)
    cam = Cam()
    cam.push(t0, t1, (-4.8, 1.8, 3.6), 5.2, 4.0, yaw=-22, pitch=4, lens=25)
    cam.handheld(1.4)
    sfx(w(227), "gasp")


@S(35, 235, 244, "Whip pan across deserted jury box & gallery benches")
def s35(t0, t1):
    build_courtroom(t0, t1, eddie=False, leo=False, judge=False, bailiff_on=False,
                    reporter_on=False, jurors=0, spectators=False, empty_robe=True, float_mics=True)
    cam = Cam()
    cam.whip(t0, t1, (2.0, -7.5, 4.6), (6.5, 1.2, 2.5), (-2.0, -8.5, 4.8), (-3.0, -4.0, 2.2), lens=21)


@S(36, 244, None, "BUTTON: Courthouse hallway — empty elevator stool, ajar doors, plunging dial & alarm!")
def s36(t0, t1):
    build_elevator_lobby()
    # elevator floor indicator cable shaking violently
    for ob in D.objects:
        if ob.name.startswith(("el_door", "el_rope", "el_ind")):
            noise(ob, "location", 0, 0.09, 3)
            noise(ob, "location", 2, 0.09, 3)
    cam = Cam()
    cam.push(t0, t1, (0.2, 16.5, 4.4), 9.6, 6.2, yaw=-6, pitch=4, lens=22)
    cam.crash(w(248), 22, 30, 0.09)
    cam.handheld(2.4)
    sfx(w(246), "alarm")
    sfx(w(249), "boom")
