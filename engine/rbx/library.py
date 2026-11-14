"""Expanded Roblox 3D Asset Library:
- 12 pre-lit, open-front 3D environments (camera-ready with zero dark rooms)
- 12 distinct character presets built on chars.Char + custom 3D headgear/props
- 10 reusable 3D props (gavel, burger tray, shopping cart, basketball, phone, etc.)
"""
import math
import bpy
from . import core as C, chars as CH, sets as ST, world as W

hexc, mat, box, cyl, sphere, plane, text, light, world = (
    C.hexc, C.mat, C.box, C.cyl, C.sphere, C.plane, C.text, C.light, C.world
)


def _coll(name):
    return C.collection(name)


def _room_shell(name, width=18.0, depth=14.0, height=9.0, wall_col="#f2efe8",
                floor_col="#c9b08e", trim_col="#5b4636", coll=None):
    """Build an open-front (-Y open) 3-wall room with floor, ceiling, and baseboard trim."""
    c = coll or _coll(name)
    mw = mat(name + "_wall", hexc(wall_col), 0.72)
    mf = mat(name + "_floor", hexc(floor_col), 0.45)
    mt = mat(name + "_trim", hexc(trim_col), 0.5)
    hw, hd = width / 2.0, depth / 2.0
    box(name + "_floor", (width, depth, 0.3), (0, 0, -0.15), mf, 0.02, coll=c)
    box(name + "_ceil", (width, depth, 0.3), (0, 0, height + 0.15), mw, 0.02, coll=c)
    box(name + "_back", (width, 0.4, height), (0, hd, height / 2), mw, 0.02, coll=c)
    box(name + "_left", (0.4, depth, height), (-hw, 0, height / 2), mw, 0.02, coll=c)
    box(name + "_right", (0.4, depth, height), (hw, 0, height / 2), mw, 0.02, coll=c)
    box(name + "_trim_b", (width, 0.15, 0.35), (0, hd - 0.22, 0.17), mt, 0.02, coll=c)
    return c


def _room_lights(name, coll, key_z=7.6, energy=1600, color="#fff7ea", fill_energy=900):
    """Standard bright overhead + front-fill lighting so faces are never dark."""
    light(name + "_key", "AREA", (0, -2.5, key_z), hexc(color), energy, size=10.0,
          rot=(22, 0, 0), coll=coll)
    light(name + "_back_fill", "AREA", (0, 2.5, key_z), hexc("#eef4ff"), fill_energy,
          size=9.0, rot=(-15, 0, 0), coll=coll)


# =====================================================================
# 12 NEW PRE-LIT 3D ENVIRONMENTS
# =====================================================================

def nurse_office():
    """Bright school nurse's office with exam bed, curtain, medicine cabinet, and sign."""
    c = _room_shell("NurseOffice", 16, 12, 8.5, "#eef7f5", "#dce8e6", "#7da8a1")
    world(hexc("#d7ecea"), 0.8)
    _room_lights("NO", c, energy=1800, color="#ffffff")
    m_white = mat("NO_white", hexc("#ffffff"), 0.35)
    m_teal = mat("NO_teal", hexc("#2b9eb3"), 0.45)
    m_red = mat("NO_red", hexc("#e63946"), 0.35)
    m_wood = mat("NO_wood", hexc("#c89f74"), 0.5)
    m_metal = mat("NO_metal", hexc("#b5bec7"), 0.25, metal=0.7)
    # Exam bed on right
    box("NO_bed_frame", (2.6, 5.2, 0.6), (4.6, 2.2, 0.9), m_metal, 0.04, coll=c)
    box("NO_bed_pad", (2.5, 5.0, 0.35), (4.6, 2.2, 1.35), m_white, 0.06, coll=c)
    box("NO_pillow", (1.8, 1.0, 0.28), (4.6, 4.1, 1.62), m_teal, 0.08, coll=c)
    # Medicine cabinet + red cross on back wall
    box("NO_cab", (2.8, 0.7, 3.0), (-3.8, 5.5, 4.4), m_white, 0.04, coll=c)
    box("NO_cross_v", (0.35, 0.08, 1.1), (-3.8, 5.12, 4.4), m_red, 0.01, coll=c)
    box("NO_cross_h", (1.1, 0.08, 0.35), (-3.8, 5.12, 4.4), m_red, 0.01, coll=c)
    # Nurse desk on left
    box("NO_desk", (3.6, 1.8, 2.0), (-4.0, 1.8, 1.0), m_wood, 0.04, coll=c)
    # Sign on back wall facing -Y
    box("NO_sign_bg", (5.2, 0.14, 1.2), (0.8, 5.75, 6.2), m_teal, 0.04, coll=c)
    text("NO_sign_txt", "NURSE OFFICE", (0.8, 5.65, 6.0), m_white, 0.62, rot=(90, 0, 0), coll=c)
    return c


def courtroom():
    """Wood-paneled courtroom with judge's bench, witness stand, and jury rail."""
    c = _room_shell("Courtroom", 20, 16, 10.0, "#7c5338", "#5a3d2b", "#3d271a")
    world(hexc("#2b1e16"), 0.5)
    _room_lights("CR", c, key_z=8.8, energy=2200, color="#ffe8c4", fill_energy=1000)
    m_oak = mat("CR_oak", hexc("#8b5a2b"), 0.4)
    m_dark = mat("CR_dark", hexc("#4a2e16"), 0.38)
    m_gold = mat("CR_gold", hexc("#e0b84c"), 0.25, metal=0.8)
    m_red = mat("CR_carpet", hexc("#7a1f24"), 0.85)
    # Center red carpet runner
    box("CR_carpet", (4.5, 13.0, 0.06), (0, -0.5, 0.03), m_red, 0.01, coll=c)
    # Raised judge platform + bench at back
    box("CR_dais", (9.5, 4.2, 1.0), (0, 5.2, 0.5), m_dark, 0.04, coll=c)
    box("CR_bench", (7.6, 1.6, 2.6), (0, 4.2, 2.3), m_oak, 0.05, coll=c)
    box("CR_seal", (1.2, 0.1, 1.2), (0, 3.35, 2.4), m_gold, 0.03, coll=c)
    # Witness stand (left of judge)
    box("CR_witness", (2.4, 2.2, 2.2), (-4.6, 2.5, 1.1), m_oak, 0.04, coll=c)
    # Defense & prosecution tables
    box("CR_tbl_L", (3.6, 1.6, 1.8), (-4.0, -2.0, 0.9), m_oak, 0.04, coll=c)
    box("CR_tbl_R", (3.6, 1.6, 1.8), (4.0, -2.0, 0.9), m_oak, 0.04, coll=c)
    return c


def diner():
    """Retro burger diner with checkered floor, red booths, counter, and neon sign."""
    c = _room_shell("Diner", 18, 14, 8.5, "#f8edd9", "#e6e6e6", "#d63838")
    world(hexc("#ffd7a8"), 0.7)
    _room_lights("DN", c, energy=1900, color="#fff0d4")
    m_chk = ST.checker_mat("DN_floor_chk", hexc("#1b1b1e"), hexc("#f4f4f4"), 0.65)
    for o in c.objects:
        if o.name.endswith("_floor"):
            o.data.materials[0] = m_chk
    m_red = mat("DN_red", hexc("#d62828"), 0.35)
    m_chrome = mat("DN_chrome", hexc("#d0d7de"), 0.2, metal=0.85)
    m_neon = ST.emit_mat("DN_neon", hexc("#ff4d6d"), 6.0)
    m_table = mat("DN_table", hexc("#f1f5f9"), 0.25)
    # Counter at back
    box("DN_counter", (10.0, 1.8, 2.1), (0, 4.0, 1.05), m_red, 0.04, coll=c)
    box("DN_counter_top", (10.3, 2.1, 0.18), (0, 4.0, 2.15), m_chrome, 0.02, coll=c)
    for sx in (-3.6, -1.2, 1.2, 3.6):
        cyl(f"DN_stool_{sx}", 0.55, 1.45, (sx, 2.3, 0.72), m_chrome, 16, coll=c)
        cyl(f"DN_seat_{sx}", 0.62, 0.25, (sx, 2.3, 1.5), m_red, 16, coll=c)
    # Side booth
    box("DN_booth_t", (2.6, 2.0, 1.6), (-5.8, -1.0, 0.8), m_table, 0.04, coll=c)
    box("DN_booth_s1", (2.6, 1.2, 1.8), (-5.8, -2.8, 0.9), m_red, 0.06, coll=c)
    box("DN_booth_s2", (2.6, 1.2, 1.8), (-5.8, 0.8, 0.9), m_red, 0.06, coll=c)
    # Neon menu sign
    box("DN_menu_bg", (6.2, 0.16, 1.6), (0, 6.75, 5.6), mat("DN_blk", hexc("#1b1b24"), 0.4), 0.04, coll=c)
    text("DN_menu_txt", "BLOX BURGER", (0, 6.62, 5.3), m_neon, 0.68, rot=(90, 0, 0), coll=c)
    return c


def grocery_store():
    """Bright supermarket aisle with colorful stocked shelves and checkout counter."""
    c = _room_shell("GroceryStore", 20, 16, 9.0, "#f3f6f8", "#d8dee6", "#3b82f6")
    world(hexc("#eaf4ff"), 0.85)
    _room_lights("GS", c, key_z=8.2, energy=2100, color="#ffffff")
    m_shelf = mat("GS_shelf", hexc("#cbd5e1"), 0.35, metal=0.4)
    colors = ["#ef4444", "#f59e0b", "#10b981", "#3b82f6", "#ec4899", "#8b5cf6"]
    mats = [mat(f"GS_p_{i}", hexc(col), 0.45) for i, col in enumerate(colors)]
    for side_x in (-5.6, 5.6):
        box(f"GS_rack_{side_x}", (2.2, 10.0, 5.6), (side_x, 1.0, 2.8), m_shelf, 0.04, coll=c)
        for row_z in (1.2, 2.6, 4.0, 5.2):
            for idx, py in enumerate((-2.8, -1.0, 0.8, 2.6, 4.4)):
                box(f"GS_box_{side_x}_{row_z}_{idx}", (1.5, 1.2, 0.85),
                    (side_x, py, row_z), mats[(idx + int(row_z)) % len(mats)], 0.03, coll=c)
    # Checkout counter at back-center
    box("GS_chk", (4.8, 1.8, 1.9), (0, 4.8, 0.95), mat("GS_blue", hexc("#2563eb"), 0.4), 0.04, coll=c)
    box("GS_belt", (3.0, 1.4, 0.1), (-0.4, 4.8, 1.95), mat("GS_belt", hexc("#1e293b"), 0.6), 0.01, coll=c)
    return c


def gym():
    """School basketball gym with hardwood court, hoops, and bleachers."""
    c = _room_shell("SchoolGym", 24, 18, 11.0, "#e6dfd3", "#d49b57", "#1e3a8a")
    world(hexc("#e8f0fa"), 0.8)
    _room_lights("GY", c, key_z=9.8, energy=2600, color="#fff9ee")
    m_line = mat("GY_line", hexc("#ffffff"), 0.4)
    m_wood = mat("GY_bleach", hexc("#b87e42"), 0.5)
    m_board = mat("GY_board", hexc("#ffffff"), 0.25)
    m_rim = mat("GY_rim", hexc("#f97316"), 0.3, metal=0.6)
    # Court markings
    box("GY_midline", (20.0, 0.22, 0.02), (0, 0, 0.01), m_line, 0, coll=c)
    cyl("GY_circle", 2.4, 0.02, (0, 0, 0.01), m_line, 24, coll=c)
    # Backboard & hoop
    box("GY_pole", (0.4, 0.4, 7.2), (0, 7.6, 3.6), mat("GY_st", hexc("#334155"), 0.4, metal=0.6), 0.02, coll=c)
    box("GY_bboard", (3.6, 0.16, 2.4), (0, 7.0, 6.8), m_board, 0.03, coll=c)
    box("GY_hoop", (1.1, 1.1, 0.12), (0, 6.2, 6.0), m_rim, 0.02, coll=c)
    # Bleachers left
    for step in range(4):
        box(f"GY_bl_{step}", (2.2, 12.0, 0.8), (-10.2 + step * 1.1, 0, 0.4 + step * 0.8), m_wood, 0.03, coll=c)
    return c


def police_station():
    """Police precinct with booking height chart, front desk, and WANTED board."""
    c = _room_shell("PoliceStation", 18, 14, 8.5, "#dbe4ee", "#94a3b8", "#1e3a8a")
    world(hexc("#cbd5e1"), 0.75)
    _room_lights("PS", c, energy=1900, color="#f4f8ff")
    m_desk = mat("PS_desk", hexc("#334155"), 0.4)
    m_white = mat("PS_white", hexc("#ffffff"), 0.35)
    m_line = mat("PS_line", hexc("#1e293b"), 0.5)
    m_blue = mat("PS_blue", hexc("#1d4ed8"), 0.4)
    # Front booking desk
    box("PS_desk", (6.5, 1.8, 2.2), (-2.5, 3.5, 1.1), m_desk, 0.04, coll=c)
    # Booking height wall on right
    box("PS_chart_bg", (4.5, 0.12, 6.5), (4.5, 6.65, 3.25), m_white, 0.02, coll=c)
    for ft in range(1, 7):
        box(f"PS_ft_{ft}", (4.2, 0.04, 0.06), (4.5, 6.56, ft * 0.95), m_line, 0, coll=c)
    text("PS_hdr", "POLICE DEPT", (-2.5, 6.6, 6.4), m_blue, 0.65, rot=(90, 0, 0), coll=c)
    return c


def park_day():
    """Sunny daytime city park with grass, paved path, bench, trees, and bright sun."""
    c = _coll("ParkDay")
    world(hexc("#7ec8f8"), 1.0)
    W.sun(5.5, (48, -22, 35))
    light("PK_fill", "AREA", (0, -10, 12), hexc("#fff8eb"), 1200, size=18.0, rot=(35, 0, 0), coll=c)
    m_grass = mat("PK_grass", hexc("#4ade80"), 0.85)
    m_path = mat("PK_path", hexc("#d6d3d1"), 0.75)
    m_wood = mat("PK_wood", hexc("#92400e"), 0.55)
    m_trunk = mat("PK_trunk", hexc("#78350f"), 0.8)
    m_leaf = mat("PK_leaf", hexc("#16a34a"), 0.7)
    box("PK_ground", (60, 60, 0.4), (0, 0, -0.2), m_grass, 0, coll=c)
    box("PK_path", (5.5, 45, 0.06), (0, 0, 0.03), m_path, 0.01, coll=c)
    # Park bench
    box("PK_bench_s", (4.2, 1.3, 0.25), (4.2, 3.0, 1.0), m_wood, 0.03, coll=c)
    box("PK_bench_b", (4.2, 0.22, 1.2), (4.2, 3.6, 1.7), m_wood, 0.03, coll=c)
    # Blocky Roblox trees
    for tx, ty in ((-6.5, 6.0), (7.5, 8.0), (-8.0, 14.0), (6.0, 15.0)):
        cyl(f"PK_tr_{tx}", 0.55, 4.0, (tx, ty, 2.0), m_trunk, 10, coll=c)
        box(f"PK_lf_{tx}", (3.6, 3.6, 3.2), (tx, ty, 5.2), m_leaf, 0.25, coll=c)
    return c


def rooftop_night():
    """City rooftop at night with glowing skyline buildings, parapet wall, and cool moon rim."""
    c = _coll("RooftopNight")
    world(hexc("#0c1428"), 0.45)
    light("RT_moon", "SUN", (10, 15, 25), hexc("#9ec5ff"), 2.4, rot=(42, 0, -25), coll=c)
    light("RT_fill", "AREA", (0, -8, 9), hexc("#ffd8a8"), 900, size=14.0, rot=(30, 0, 0), coll=c)
    m_conc = mat("RT_conc", hexc("#475569"), 0.8)
    m_wall = mat("RT_wall", hexc("#64748b"), 0.75)
    m_bldg = mat("RT_bldg", hexc("#1e293b"), 0.6)
    m_win = ST.emit_mat("RT_win", hexc("#fde047"), 3.5)
    box("RT_deck", (22, 20, 0.5), (0, 0, -0.25), m_conc, 0.04, coll=c)
    box("RT_parapet", (22, 0.8, 1.6), (0, 9.6, 0.8), m_wall, 0.04, coll=c)
    box("RT_ac", (2.8, 2.2, 2.0), (-6.5, 6.0, 1.0), m_wall, 0.05, coll=c)
    # Distant skyline blocks
    for i, (bx, by, bh) in enumerate([(-16, 26, 22), (-7, 30, 28), (4, 28, 24), (15, 25, 20)]):
        box(f"RT_sky_{i}", (7.0, 7.0, bh), (bx, by, bh / 2 - 12), m_bldg, 0.05, coll=c)
        box(f"RT_win_{i}", (4.5, 0.2, bh * 0.5), (bx, by - 3.6, bh * 0.2), m_win, 0, coll=c)
    return c


def subway_station():
    """Underground metro platform with yellow safety stripe, pillars, and subway train."""
    c = _room_shell("Subway", 24, 14, 8.5, "#cbd5e1", "#64748b", "#334155")
    world(hexc("#1e293b"), 0.5)
    _room_lights("SB", c, energy=1800, color="#f8fafc")
    m_yel = mat("SB_yel", hexc("#facc15"), 0.4)
    m_train = mat("SB_train", hexc("#94a3b8"), 0.25, metal=0.7)
    m_blue = mat("SB_tblue", hexc("#2563eb"), 0.35)
    box("SB_safety", (22, 0.6, 0.04), (0, 3.2, 0.02), m_yel, 0, coll=c)
    for px in (-6.5, 0.0, 6.5):
        box(f"SB_pil_{px}", (0.9, 0.9, 8.5), (px, 1.5, 4.25), m_blue, 0.04, coll=c)
    # Subway train car at back
    box("SB_car", (18.0, 3.6, 5.2), (0, 5.2, 2.7), m_train, 0.12, coll=c)
    box("SB_stripe", (18.05, 3.65, 0.7), (0, 5.2, 2.2), m_blue, 0.02, coll=c)
    return c


def space_station():
    """Sci-fi space station bridge with metallic floor, glowing consoles, and star window."""
    c = _room_shell("SpaceStation", 18, 14, 8.5, "#334155", "#1e293b", "#0ea5e9")
    W.space_world()
    _room_lights("SS", c, energy=1700, color="#e0f2fe")
    m_deck = mat("SS_deck", hexc("#475569"), 0.3, metal=0.75)
    m_cyan = ST.emit_mat("SS_cyan", hexc("#38bdf8"), 4.5)
    m_org = ST.emit_mat("SS_org", hexc("#fb923c"), 4.0)
    box("SS_console", (7.5, 1.8, 2.0), (0, 3.8, 1.0), m_deck, 0.06, coll=c)
    box("SS_scr1", (2.4, 0.12, 1.2), (-2.0, 3.5, 2.6), m_cyan, 0.02, rot=(-25, 0, 0), coll=c)
    box("SS_scr2", (2.4, 0.12, 1.2), (2.0, 3.5, 2.6), m_org, 0.02, rot=(-25, 0, 0), coll=c)
    return c


def haunted_house():
    """Spooky mansion foyer with crooked frames, pillars, and eerie purple/green lighting."""
    c = _room_shell("HauntedHouse", 18, 14, 9.5, "#2e2438", "#3d2c2e", "#1a1420")
    world(hexc("#120d1a"), 0.4)
    light("HH_purp", "AREA", (-3, -2, 7.5), hexc("#a855f7"), 1400, size=9.0, rot=(20, 0, 0), coll=c)
    light("HH_grn", "AREA", (3, 1, 6.5), hexc("#4ade80"), 900, size=8.0, rot=(10, 0, 0), coll=c)
    m_wood = mat("HH_wood", hexc("#4a3228"), 0.65)
    m_gold = mat("HH_gold", hexc("#b4933b"), 0.4, metal=0.6)
    for px in (-5.5, 5.5):
        cyl(f"HH_pil_{px}", 0.65, 9.5, (px, 4.5, 4.75), m_wood, 12, coll=c)
    box("HH_clock", (1.8, 1.2, 5.6), (0, 6.0, 2.8), m_wood, 0.05, coll=c)
    cyl("HH_face", 0.55, 0.12, (0, 5.35, 4.4), m_gold, 16, rot=(90, 0, 0), coll=c)
    return c


def beach():
    """Sunny tropical beach with golden sand, turquoise ocean, palm tree, and umbrella."""
    c = _coll("Beach")
    world(hexc("#60c5ff"), 1.0)
    W.sun(6.0, (45, -18, 30))
    light("BC_fill", "AREA", (0, -8, 10), hexc("#fff9e6"), 1100, size=16.0, rot=(30, 0, 0), coll=c)
    m_sand = mat("BC_sand", hexc("#f6d58e"), 0.85)
    m_sea = mat("BC_sea", hexc("#06b6d4"), 0.2)
    m_trunk = mat("BC_trunk", hexc("#92400e"), 0.75)
    m_leaf = mat("BC_leaf", hexc("#22c55e"), 0.65)
    m_red = mat("BC_red", hexc("#ef4444"), 0.45)
    box("BC_sand", (50, 24, 0.4), (0, -2, -0.2), m_sand, 0, coll=c)
    box("BC_ocean", (60, 30, 0.3), (0, 24, -0.25), m_sea, 0, coll=c)
    # Palm tree
    cyl("BC_palm", 0.45, 5.5, (-5.5, 5.0, 2.7), m_trunk, 10, rot=(0, 8, 0), coll=c)
    for ang in (0, 90, 180, 270):
        box(f"BC_frond_{ang}", (3.2, 0.9, 0.2), (-5.0, 5.0, 5.4), m_leaf, 0.05, rot=(0, 14, ang), coll=c)
    # Umbrella
    cyl("BC_pole", 0.1, 4.0, (4.8, 3.5, 2.0), mat("BC_w", hexc("#ffffff"), 0.3), 10, coll=c)
    cyl("BC_umb", 2.4, 0.8, (4.8, 3.5, 4.0), m_red, 8, coll=c)
    return c


# =====================================================================
# 12 NEW CHARACTER PRESETS
# =====================================================================

def _hat_cap(ch, color="#1d4ed8", badge_col="#facc15"):
    m = mat(ch.name + "_cap", hexc(color), 0.45)
    box(ch.name + "_crown", (1.36, 1.36, 0.55), (0, 0, 1.38), m, 0.08, parent=ch.neck, coll=ch.coll)
    box(ch.name + "_brim", (1.36, 0.7, 0.14), (0, -0.78, 1.15), m, 0.03, parent=ch.neck, coll=ch.coll)
    if badge_col:
        box(ch.name + "_badge", (0.28, 0.08, 0.28), (0, -0.7, 1.4), mat(ch.name + "_bdg", hexc(badge_col), 0.25, metal=0.8),
            0.02, parent=ch.neck, coll=ch.coll)


def police_officer(name="Officer", loc=(0, 0, 0), rot=0, scale=1.0):
    ch = CH.Char(name, skin="#f1c7a5", shirt="#1e3a8a", pants="#0f172a", hair="none",
                 face="mustache", sleeves="long", loc=loc, rot=rot, scale=scale)
    _hat_cap(ch, "#1e3a8a", "#facc15")
    box(name + "_chest_bdg", (0.32, 0.08, 0.36), (-0.5, -0.52, 1.45),
        mat(name + "_gold", hexc("#facc15"), 0.2, metal=0.85), 0.02, parent=ch.hip, coll=ch.coll)
    return ch


def judge(name="Judge", loc=(0, 0, 0), rot=0, scale=1.0):
    ch = CH.Char(name, skin="#e8b896", shirt="#111827", pants="#111827", hair="curly",
                 hair_color="#e5e7eb", face="mustache", sleeves="long", vneck="#ffffff",
                 loc=loc, rot=rot, scale=scale)
    return ch


def doctor_nurse(name="Nurse", loc=(0, 0, 0), rot=0, scale=1.0):
    ch = CH.Char(name, skin="#f4d2b8", shirt="#f8fafc", pants="#38bdf8", hair="bun",
                 hair_color="#6b3e26", face="girl", sleeves="short", vneck="#38bdf8",
                 loc=loc, rot=rot, scale=scale)
    box(name + "_ncap", (0.9, 0.4, 0.45), (0, 0.15, 1.42), mat(name + "_w", hexc("#ffffff"), 0.4),
        0.04, parent=ch.neck, coll=ch.coll)
    return ch


def chef(name="Chef", loc=(0, 0, 0), rot=0, scale=1.0):
    ch = CH.Char(name, skin="#f0c8a0", shirt="#ffffff", pants="#1f2937", hair="none",
                 face="mustache", sleeves="long", pants_kind="checker", pants_c2="#9ca3af",
                 loc=loc, rot=rot, scale=scale)
    mw = mat(name + "_toque", hexc("#ffffff"), 0.45)
    cyl(name + "_toque_b", 0.68, 0.45, (0, 0, 1.38), mw, 16, parent=ch.neck, coll=ch.coll)
    cyl(name + "_toque_t", 0.82, 0.75, (0, 0, 1.88), mw, 16, parent=ch.neck, coll=ch.coll)
    return ch


def astronaut(name="Astro", loc=(0, 0, 0), rot=0, scale=1.0):
    ch = CH.Char(name, skin="#f1dfc6", shirt="#f8fafc", pants="#e2e8f0", hair="none",
                 face="hero", sleeves="long", loc=loc, rot=rot, scale=scale)
    box(name + "_pack", (1.6, 0.7, 1.7), (0, 0.85, 1.0), mat(name + "_pk", hexc("#cbd5e1"), 0.35),
        0.08, parent=ch.hip, coll=ch.coll)
    W2_glass = mat(name + "_visor", hexc("#38bdf8"), 0.1, metal=0.4)
    box(name + "_helm", (1.65, 1.65, 1.55), (0, 0, 0.65), mat(name + "_hw", hexc("#ffffff"), 0.3),
        0.2, parent=ch.neck, coll=ch.coll)
    box(name + "_vis", (1.25, 0.15, 0.9), (0, -0.82, 0.65), W2_glass, 0.08, parent=ch.neck, coll=ch.coll)
    return ch


def bully(name="Bully", loc=(0, 0, 0), rot=0, scale=1.08):
    return CH.Char(name, skin="#e4b58f", shirt="#991b1b", pants="#1f2937", hair="spiky",
                   hair_color="#292524", face="villain", sleeves="none", loc=loc, rot=rot, scale=scale)


def nerd(name="Nerd", loc=(0, 0, 0), rot=0, scale=0.95):
    return CH.Char(name, skin="#f5d9c4", shirt="#fef08a", pants="#78350f", hair="parted",
                   hair_color="#451a03", face="kid", sleeves="short", extras=("glasses",),
                   loc=loc, rot=rot, scale=scale)


def rich_kid(name="RichKid", loc=(0, 0, 0), rot=0, scale=1.0):
    ch = CH.Char(name, skin="#f3d2b3", shirt="#7e22ce", pants="#1e1b4b", hair="pompadour",
                 hair_color="#eab308", face="hero", sleeves="long", vneck="#facc15",
                 loc=loc, rot=rot, scale=scale)
    return ch


def ninja(name="Ninja", loc=(0, 0, 0), rot=0, scale=1.0):
    ch = CH.Char(name, skin="#e8be9e", shirt="#0f172a", pants="#0f172a", hair="none",
                 face="villain", sleeves="long", loc=loc, rot=rot, scale=scale)
    box(name + "_band", (1.38, 1.38, 0.35), (0, 0, 0.98), mat(name + "_red", hexc("#dc2626"), 0.5),
        0.04, parent=ch.neck, coll=ch.coll)
    return ch


def robber(name="Robber", loc=(0, 0, 0), rot=0, scale=1.0):
    ch = CH.Char(name, skin="#e6bea0", shirt="#111827", pants="#1f2937", hair="none",
                 face="villain", sleeves="long", shirt_kind="stripes", shirt_c2="#e5e7eb",
                 loc=loc, rot=rot, scale=scale)
    _hat_cap(ch, "#111827", None)
    return ch


def alien(name="Alien", loc=(0, 0, 0), rot=0, scale=1.0):
    ch = CH.Char(name, skin="#4ade80", shirt="#4338ca", pants="#1e1b4b", hair="none",
                 face="plain", sleeves="long", loc=loc, rot=rot, scale=scale)
    mg = mat(name + "_ant", hexc("#22c55e"), 0.3)
    for ax in (-0.42, 0.42):
        cyl(f"{name}_st_{ax}", 0.06, 0.65, (ax, 0, 1.48), mg, 8, parent=ch.neck, coll=ch.coll)
        sphere(f"{name}_orb_{ax}", 0.16, (ax, 0, 1.85), ST.emit_mat(name + "_g", hexc("#a3e635"), 3.0),
               parent=ch.neck, coll=ch.coll)
    return ch


def robot(name="Robot", loc=(0, 0, 0), rot=0, scale=1.0):
    ch = CH.Char(name, skin="#94a3b8", shirt="#64748b", pants="#334155", hair="none",
                 face="plain", sleeves="long", loc=loc, rot=rot, scale=scale)
    cyl(name + "_ant", 0.05, 0.6, (0, 0, 1.5), mat(name + "_m", hexc("#cbd5e1"), 0.2, metal=0.9),
        8, parent=ch.neck, coll=ch.coll)
    sphere(name + "_led", 0.14, (0, 0, 1.82), ST.emit_mat(name + "_led", hexc("#ef4444"), 5.0),
           parent=ch.neck, coll=ch.coll)
    return ch


# =====================================================================
# 10 REUSABLE 3D PROPS
# =====================================================================

def prop_gavel(name="Gavel", loc=(0, 0, 0), coll=None):
    c = coll or _coll("PR_" + name)
    mw = mat(name + "_w", hexc("#78350f"), 0.4)
    cyl(name + "_head", 0.22, 0.75, (loc[0], loc[1], loc[2] + 0.22), mw, 14, rot=(0, 90, 0), coll=c)
    cyl(name + "_hdl", 0.07, 1.1, (loc[0], loc[1] - 0.55, loc[2] + 0.22), mw, 10, rot=(90, 0, 0), coll=c)
    return c


def prop_burger_tray(name="BurgerTray", loc=(0, 0, 0), coll=None):
    c = coll or _coll("PR_" + name)
    box(name + "_tray", (1.2, 0.9, 0.06), loc, mat(name + "_r", hexc("#dc2626"), 0.4), 0.02, coll=c)
    cyl(name + "_bunB", 0.24, 0.12, (loc[0] - 0.2, loc[1], loc[2] + 0.09), mat(name + "_bn", hexc("#d97706"), 0.6), 12, coll=c)
    cyl(name + "_patty", 0.23, 0.09, (loc[0] - 0.2, loc[1], loc[2] + 0.19), mat(name + "_pt", hexc("#7c2d12"), 0.7), 12, coll=c)
    cyl(name + "_bunT", 0.24, 0.14, (loc[0] - 0.2, loc[1], loc[2] + 0.30), mat(name + "_bn2", hexc("#f59e0b"), 0.55), 12, coll=c)
    cyl(name + "_cup", 0.16, 0.48, (loc[0] + 0.28, loc[1], loc[2] + 0.27), mat(name + "_cp", hexc("#3b82f6"), 0.3), 12, coll=c)
    return c


def prop_shopping_cart(name="Cart", loc=(0, 0, 0), coll=None):
    c = coll or _coll("PR_" + name)
    mm = mat(name + "_m", hexc("#cbd5e1"), 0.25, metal=0.85)
    box(name + "_basket", (1.4, 1.8, 0.9), (loc[0], loc[1], loc[2] + 1.1), mm, 0.04, coll=c)
    box(name + "_hdl", (1.4, 0.12, 0.12), (loc[0], loc[1] - 1.0, loc[2] + 1.65), mat(name + "_r", hexc("#ef4444"), 0.4), 0.02, coll=c)
    for wx in (-0.55, 0.55):
        for wy in (-0.7, 0.7):
            cyl(f"{name}_w_{wx}_{wy}", 0.16, 0.1, (loc[0] + wx, loc[1] + wy, loc[2] + 0.16), mat(name + "_blk", hexc("#1e293b"), 0.7), 10, rot=(0, 90, 0), coll=c)
    return c


def prop_basketball(name="Ball", loc=(0, 0, 0), coll=None):
    c = coll or _coll("PR_" + name)
    return sphere(name, 0.38, (loc[0], loc[1], loc[2] + 0.38), mat(name + "_o", hexc("#ea580c"), 0.5), coll=c)


def prop_treasure_chest(name="Chest", loc=(0, 0, 0), coll=None):
    c = coll or _coll("PR_" + name)
    mw = mat(name + "_w", hexc("#92400e"), 0.55)
    mg = mat(name + "_g", hexc("#facc15"), 0.25, metal=0.85)
    box(name + "_base", (1.8, 1.2, 0.9), (loc[0], loc[1], loc[2] + 0.45), mw, 0.04, coll=c)
    box(name + "_lid", (1.84, 1.24, 0.45), (loc[0], loc[1], loc[2] + 1.1), mw, 0.08, coll=c)
    box(name + "_lock", (0.28, 0.12, 0.36), (loc[0], loc[1] - 0.62, loc[2] + 0.88), mg, 0.02, coll=c)
    return c


def prop_phone(name="Phone", loc=(0, 0, 0), coll=None):
    c = coll or _coll("PR_" + name)
    box(name + "_body", (0.28, 0.05, 0.52), loc, mat(name + "_b", hexc("#0f172a"), 0.25), 0.02, coll=c)
    box(name + "_scr", (0.24, 0.01, 0.44), (loc[0], loc[1] - 0.03, loc[2]), ST.emit_mat(name + "_s", hexc("#38bdf8"), 2.5), 0.01, coll=c)
    return c


def prop_trophy(name="Trophy", loc=(0, 0, 0), coll=None):
    c = coll or _coll("PR_" + name)
    mg = mat(name + "_g", hexc("#facc15"), 0.2, metal=0.9)
    box(name + "_base", (0.5, 0.5, 0.25), (loc[0], loc[1], loc[2] + 0.12), mat(name + "_b", hexc("#451a03"), 0.4), 0.02, coll=c)
    cyl(name + "_stem", 0.1, 0.4, (loc[0], loc[1], loc[2] + 0.45), mg, 12, coll=c)
    cyl(name + "_cup", 0.32, 0.5, (loc[0], loc[1], loc[2] + 0.9), mg, 16, coll=c)
    return c


def prop_megaphone(name="Megaphone", loc=(0, 0, 0), coll=None):
    c = coll or _coll("PR_" + name)
    mr = mat(name + "_r", hexc("#ef4444"), 0.35)
    mw = mat(name + "_w", hexc("#f8fafc"), 0.35)
    cyl(name + "_cone", 0.28, 0.7, loc, mw, 14, rot=(90, 0, 0), coll=c)
    box(name + "_hdl", (0.1, 0.12, 0.36), (loc[0], loc[1], loc[2] - 0.28), mr, 0.02, coll=c)
    return c


def prop_skateboard(name="Skateboard", loc=(0, 0, 0), coll=None):
    c = coll or _coll("PR_" + name)
    box(name + "_deck", (0.65, 2.1, 0.08), (loc[0], loc[1], loc[2] + 0.2), mat(name + "_d", hexc("#8b5cf6"), 0.4), 0.03, coll=c)
    mw = mat(name + "_w", hexc("#facc15"), 0.3)
    for wx in (-0.25, 0.25):
        for wy in (-0.7, 0.7):
            cyl(f"{name}_w_{wx}_{wy}", 0.1, 0.08, (loc[0] + wx, loc[1] + wy, loc[2] + 0.1), mw, 10, rot=(0, 90, 0), coll=c)
    return c


def prop_desk_mic(name="DeskMic", loc=(0, 0, 0), coll=None):
    c = coll or _coll("PR_" + name)
    mb = mat(name + "_b", hexc("#1e293b"), 0.3, metal=0.7)
    cyl(name + "_base", 0.22, 0.06, (loc[0], loc[1], loc[2] + 0.03), mb, 12, coll=c)
    cyl(name + "_stem", 0.04, 0.5, (loc[0], loc[1], loc[2] + 0.28), mb, 8, coll=c)
    sphere(name + "_head", 0.11, (loc[0], loc[1], loc[2] + 0.56), mat(name + "_m", hexc("#94a3b8"), 0.25, metal=0.8), coll=c)
    return c
