"""Expanded Roblox 3D Asset Library:
- 12 pre-lit, open-front 3D environments (camera-ready with zero dark rooms)
- 12 distinct character presets built on chars.Char + custom 3D headgear/props
- 10 reusable 3D props (gavel, burger tray, shopping cart, basketball, phone, etc.)
"""
import math
import os
import bpy
from . import core as C, chars as CH, sets as ST, world as W, acting as _acting  # noqa: F401

hexc, mat, box, cyl, sphere, plane, card, text, light, world = (
    C.hexc, C.mat, C.box, C.cyl, C.sphere, C.plane, C.card, C.text, C.light, C.world
)
TEX = ST.TEX


def _coll(name):
    return C.collection(name)


def _room_shell(name, width=18.0, depth=14.0, height=9.0, wall_col="#f2efe8",
                floor_col="#c9b08e", trim_col="#5b4636", coll=None, tiled_floor=True,
                skip_walls=()):
    """Build an open-front (-Y open) 3-wall room with floor, ceiling, and baseboard trim.

    Uses tiled flooring by default and baseboard trim around all three walls. Pass
    skip_walls=('back'|'left'|'right') when replacing a wall with ST.wall_with_hole().
    """
    c = coll or _coll(name)
    mw = mat(name + "_wall", hexc(wall_col), 0.72)
    mf = ST.tiles(name + "_floor", floor_col, trim_col, 0.3, 1.1, 1.1, 0.4, axis="XY") if tiled_floor \
        else mat(name + "_floor", hexc(floor_col), 0.45)
    mt = mat(name + "_trim", hexc(trim_col), 0.5)
    hw, hd = width / 2.0, depth / 2.0
    box(name + "_floor", (width, depth, 0.3), (0, 0, -0.15), mf, 0.02, coll=c)
    shell_obs = [box(name + "_ceil", (width, depth, 0.3), (0, 0, height + 0.15), mw, 0.02, coll=c)]
    if "back" not in skip_walls:
        shell_obs.append(box(name + "_back", (width, 0.4, height), (0, hd, height / 2), mw, 0.02, coll=c))
    if "left" not in skip_walls:
        shell_obs.append(box(name + "_left", (0.4, depth, height), (-hw, 0, height / 2), mw, 0.02, coll=c))
    if "right" not in skip_walls:
        shell_obs.append(box(name + "_right", (0.4, depth, height), (hw, 0, height / 2), mw, 0.02, coll=c))
    for ob in shell_obs:
        try:
            ob.visible_shadow = False
        except Exception:
            pass
    box(name + "_trim_b", (width, 0.15, 0.35), (0, hd - 0.22, 0.17), mt, 0.02, coll=c)
    box(name + "_trim_l", (0.15, depth, 0.35), (-hw + 0.22, 0, 0.17), mt, 0.02, coll=c)
    box(name + "_trim_r", (0.15, depth, 0.35), (hw - 0.22, 0, 0.17), mt, 0.02, coll=c)
    return c


def _room_lights(name, coll, key_z=7.6, energy=1600, color="#fff7ea", fill_energy=900):
    """Standard bright overhead + front-fill lighting so faces are never dark."""
    light(name + "_key", "AREA", (0, -2.5, key_z), energy, hexc(color), size=10.0,
          rot=(22, 0, 0), coll=coll)
    light(name + "_back_fill", "AREA", (0, 2.5, key_z), fill_energy, hexc("#eef4ff"),
          size=9.0, rot=(-15, 0, 0), coll=coll)


def _tex_panel(name, w, h, loc, fname, facing="-Y", emit=0.0, coll=None,
               frame_col="#3b281c", border=0.14):
    """Framed wall sign/poster backed by a 3D beveled frame board."""
    offsets = {"-Y": (0, 0.06, 0), "+Y": (0, -0.06, 0), "+X": (-0.06, 0, 0), "-X": (0.06, 0, 0)}
    dx, dy, dz = offsets[facing]
    mf = mat(name + "_fr", hexc(frame_col), 0.45)
    if facing in ("-Y", "+Y"):
        box(name + "_bk", (w + border * 2, 0.1, h + border * 2),
            (loc[0] + dx, loc[1] + dy, loc[2] + dz), mf, 0.02, coll=coll)
    else:
        box(name + "_bk", (0.1, w + border * 2, h + border * 2),
            (loc[0] + dx, loc[1] + dy, loc[2] + dz), mf, 0.02, coll=coll)
    return card(name, w, h, loc, C.img_mat(name + "_im", os.path.join(TEX, fname), 0.45, emit=emit),
                facing=facing, coll=coll)


def _window_wall(name, axis, pos, span, height, hole, wall_m, trim_m, coll,
                 inner_sign=1, sky_col=(0.62, 0.82, 1.0), estr=2.2, outside_trees=True, glass=True):
    """Cut a window bay with ST.wall_with_hole(), add sill/mullion trim, glass, and outside view."""
    ST.wall_with_hole(name, axis, pos, span, (0, height), hole, 0.4, wall_m, coll, inner_sign=inner_sign)
    if hole is None:
        return
    h0, h1, z0, z1 = hole
    hc, zc = (h0 + h1) / 2.0, (z0 + z1) / 2.0
    hw, hh = h1 - h0, z1 - z0
    wf = pos + inner_sign * 0.2
    ms = mat(name + "_sky", sky_col, emit=sky_col, estr=estr)
    mg = mat(name + "_gl", (0.85, 0.94, 1.0), 0.05, alpha=0.16, spec=1.0)
    if axis == "y":
        box(name + "_top", (hw + 0.3, 0.5, 0.2), (hc, wf, z1), trim_m, 0.02, coll=coll)
        box(name + "_bot", (hw + 0.3, 0.56, 0.22), (hc, wf, z0), trim_m, 0.02, coll=coll)
        box(name + "_l", (0.2, 0.5, hh), (h0, wf, zc), trim_m, 0.02, coll=coll)
        box(name + "_r", (0.2, 0.5, hh), (h1, wf, zc), trim_m, 0.02, coll=coll)
        box(name + "_mv", (0.12, 0.35, hh), (hc, wf, zc), trim_m, 0.01, coll=coll)
        box(name + "_mh", (hw, 0.35, 0.12), (hc, wf, zc), trim_m, 0.01, coll=coll)
        if glass:
            card(name + "_glass", hw - 0.1, hh - 0.1, (hc, wf, zc), mg, "-Y" if inner_sign > 0 else "+Y", coll=coll)
        card(name + "_out", hw + 8.0, hh + 6.0, (hc, wf + inner_sign * 7.5, zc), ms,
             "-Y" if inner_sign > 0 else "+Y", coll=coll)
        if outside_trees:
            ml = mat(name + "_leaf", hexc("#4f9f45"), 0.85)
            for k in (-1, 0, 1):
                sphere(f"{name}_tr{k}", 1.5, (hc + k * 2.2, wf + inner_sign * 4.2, z0 + 0.6), ml, (1, 1, 1.15), coll=coll)
    else:
        box(name + "_top", (0.5, hw + 0.3, 0.2), (wf, hc, z1), trim_m, 0.02, coll=coll)
        box(name + "_bot", (0.56, hw + 0.3, 0.22), (wf, hc, z0), trim_m, 0.02, coll=coll)
        box(name + "_l", (0.5, 0.2, hh), (wf, h0, zc), trim_m, 0.02, coll=coll)
        box(name + "_r", (0.5, 0.2, hh), (wf, h1, zc), trim_m, 0.02, coll=coll)
        box(name + "_mv", (0.35, 0.12, hh), (wf, hc, zc), trim_m, 0.01, coll=coll)
        box(name + "_mh", (0.35, hw, 0.12), (wf, hc, zc), trim_m, 0.01, coll=coll)
        if glass:
            card(name + "_glass", hw - 0.1, hh - 0.1, (wf, hc, zc), mg, "-X" if inner_sign > 0 else "+X", coll=coll)
        card(name + "_out", hw + 8.0, hh + 6.0, (wf + inner_sign * 7.5, hc, zc), ms,
             "-X" if inner_sign > 0 else "+X", coll=coll)
        if outside_trees:
            ml = mat(name + "_leaf", hexc("#4f9f45"), 0.85)
            for k in (-1, 0, 1):
                sphere(f"{name}_tr{k}", 1.5, (wf + inner_sign * 4.2, hc + k * 2.2, z0 + 0.6), ml, (1, 1, 1.15), coll=coll)


def _chair(name, loc, coll, seat_col="#2563eb", rot=0):
    mc = mat(name + "_ch", hexc(seat_col), 0.45)
    ml = mat(name + "_lg", hexc("#334155"), 0.35, metal=0.7)
    x, y, z = loc
    box(name + "_st", (1.3, 1.2, 0.18), (x, y, z + 1.05), mc, 0.04, rot=(0, 0, rot), coll=coll)
    rad = math.radians(rot)
    bx, by = x + math.sin(rad) * 0.55, y + math.cos(rad) * 0.55
    box(name + "_bk", (1.3, 0.18, 1.2), (bx, by, z + 1.7), mc, 0.04, rot=(0, 0, rot), coll=coll)
    for sx in (-0.5, 0.5):
        for sy in (-0.45, 0.45):
            cyl(f"{name}_l{sx}_{sy}", 0.06, 1.0, (x + sx, y + sy, z + 0.5), ml, 8, coll=coll)


# =====================================================================
# 12 PRE-LIT 3D ENVIRONMENTS (Classroom-parity architectural detail)
# =====================================================================

def nurse_office():
    """Bright school nurse's office with sunlit window bay, privacy screen, vision chart & wood desk."""
    c = _room_shell("NurseOffice", 16, 12, 8.5, "#eef7f5", "#dce8e6", "#7da8a1", skip_walls=("back",))
    world(hexc("#d7ecea"), 0.55)
    _room_lights("NO", c, energy=1250, color="#ffffff", fill_energy=650)
    mw = mat("NO_wall_b", hexc("#eef7f5"), 0.72)
    m_trim = mat("NO_wtrim", hexc("#ffffff"), 0.45)
    # 1 & 5: Back-left window bay looking out to sky & trees
    _window_wall("NO_win", "y", 5.8, (-8.0, 8.0), 8.5, (-6.2, -2.4, 3.0, 6.8),
                 mw, m_trim, c, inner_sign=1, sky_col=(0.68, 0.88, 1.0))
    m_white = mat("NO_white", hexc("#ffffff"), 0.35)
    m_teal = mat("NO_teal", hexc("#2b9eb3"), 0.45)
    m_red = mat("NO_red", hexc("#e63946"), 0.35)
    m_wood = ST.wood("NO_wood", "#8a5634", "#c48a58", 1.8)
    m_metal = mat("NO_metal", hexc("#b5bec7"), 0.2, metal=0.8)
    # 2: Real PNG texture signage (Vision eye chart + Clinic banner)
    _tex_panel("NO_chart", 2.0, 2.7, (-0.4, 5.74, 4.4), "nurse_chart.png", "-Y", coll=c, frame_col="#2b9eb3")
    box("NO_sign_bg", (4.8, 0.14, 1.0), (0.0, 5.74, 6.8), m_teal, 0.04, coll=c)
    text("NO_sign_txt", "NURSE OFFICE", (0.0, 5.64, 6.68), 0.54, m_white, rot=(90, 0, 0), coll=c)
    # Exam bed on right with steel legs, paper roll dispenser & IV stand
    box("NO_bed_frame", (2.8, 5.2, 0.42), (4.6, 2.0, 1.0), m_metal, 0.04, coll=c)
    for lx in (3.4, 5.8):
        for ly in (-0.3, 4.3):
            cyl(f"NO_bl_{lx}_{ly}", 0.09, 0.9, (lx, ly, 0.45), m_metal, 10, coll=c)
    box("NO_bed_pad", (2.6, 5.0, 0.38), (4.6, 2.0, 1.4), m_white, 0.06, coll=c)
    box("NO_pillow", (1.9, 1.05, 0.28), (4.6, 3.9, 1.72), m_teal, 0.08, coll=c)
    cyl("NO_iv_pole", 0.06, 5.2, (6.5, 4.3, 2.6), m_metal, 10, coll=c)
    cyl("NO_iv_base", 0.55, 0.1, (6.5, 4.3, 0.05), m_metal, 12, coll=c)
    box("NO_screen", (0.14, 2.8, 4.6), (2.2, 3.8, 2.3), m_teal, 0.03, rot=(0, 0, -14), coll=c)
    # Medicine cabinet + red cross + bottles/jars clutter
    box("NO_cab", (2.6, 0.8, 3.2), (3.8, 5.35, 4.4), m_white, 0.04, coll=c)
    box("NO_cross_v", (0.32, 0.08, 1.05), (3.8, 4.92, 4.4), m_red, 0.01, coll=c)
    box("NO_cross_h", (1.05, 0.08, 0.32), (3.8, 4.92, 4.4), m_red, 0.01, coll=c)
    # 3: Wood-grain hero nurse desk + stool + books + clipboard + bottles
    box("NO_desk_top", (4.0, 2.0, 0.25), (-4.0, 1.8, 2.2), m_wood, 0.04, coll=c)
    for sx in (-1, 1):
        for sy in (-1, 1):
            box(f"NO_dl_{sx}_{sy}", (0.18, 0.18, 2.1), (-4.0 + sx * 1.7, 1.8 + sy * 0.75, 1.05), m_metal, 0.02, coll=c)
    _chair("NO_chair", (-4.0, 3.1, 0), c, seat_col="#2b9eb3", rot=180)
    ST.books("NO_books", (-5.2, 1.8, 2.33), c, n=4, lie=True)
    for k, col in enumerate(("#ef4444", "#3b82f6", "#10b981")):
        cyl(f"NO_jar_{k}", 0.16, 0.45, (-2.8 + k * 0.45, 1.7, 2.55), mat(f"NO_j{k}", hexc(col), 0.25), 12, coll=c)
    cyl("NO_trash", 0.42, 0.9, (-1.4, 2.2, 0.45), m_metal, 14, r2=0.35, coll=c)
    # 5: Corner plant
    ST.plant("NO_plant", (-6.8, 4.6, 0), c, s=1.2)
    return c


def courtroom():
    """High-key pastel courtroom (roblox-v3 style-toon.md §1-2): cream walls, warm oak trim & bench, tall windows, gold Justice seal."""
    c = _room_shell("Courtroom", 20, 16, 10.0, "#f4ead5", "#e8d5b5", "#6e4229", skip_walls=("back",))
    world(hexc("#f7eedf"), 0.55)
    _room_lights("CR", c, key_z=8.8, energy=1450, color="#fff6e8", fill_energy=750)
    mw = mat("CR_wall_b", hexc("#f4ead5"), 0.78)
    m_wtrim = mat("CR_wtrim", hexc("#6e4229"), 0.45)
    # 1 & 5: Tall courtroom window bay on back-left wall with outside trees
    _window_wall("CR_win", "y", 7.8, (-10.0, 10.0), 10.0, (-7.8, -4.4, 3.2, 8.2),
                 mw, m_wtrim, c, inner_sign=1, sky_col=(0.75, 0.88, 1.0))
    m_oak = mat("CR_oak", hexc("#c98b5e"), 0.58)
    m_dark = mat("CR_dark", hexc("#8c5834"), 0.62)
    m_gold = mat("CR_gold", hexc("#e0b84c"), 0.28, metal=0.75)
    m_red = mat("CR_carpet", hexc("#d95b5b"), 0.75)
    # Wainscoting wood paneling on right & back
    box("CR_wain_r", (0.16, 15.6, 3.6), (9.7, 0, 1.8), m_dark, 0.02, coll=c)
    box("CR_wain_l", (0.16, 15.6, 3.6), (-9.7, 0, 1.8), m_dark, 0.02, coll=c)
    box("CR_wain_b", (19.6, 0.16, 3.6), (0, 7.72, 1.8), m_dark, 0.02, coll=c)
    box("CR_carpet", (4.5, 13.5, 0.06), (0, -0.5, 0.03), m_red, 0.01, coll=c)
    # 2: Real PNG Justice Seal behind judge & on front of bench
    _tex_panel("CR_seal_wall", 3.0, 3.0, (0, 7.72, 6.6), "court_seal.png", "-Y", coll=c, frame_col="#e0b84c")
    # 3: Judge dais, carved oak bench (height 2.85 so Judge's torso/arms/collar sit clearly above top), gavel, lamp, witness box
    box("CR_dais", (10.0, 4.4, 1.0), (0, 5.2, 0.5), m_dark, 0.04, coll=c)
    box("CR_bench", (7.8, 1.8, 1.75), (0, 4.2, 1.875), m_oak, 0.05, coll=c)
    box("CR_bench_top", (8.1, 2.1, 0.16), (0, 4.2, 2.83), m_dark, 0.04, coll=c)
    cyl("CR_bench_seal", 0.62, 0.1, (0, 3.26, 1.9), m_gold, 24, rot=(90, 0, 0), coll=c)
    prop_gavel("CR_gavel", (1.6, 3.6, 2.92), coll=c)
    _chair("CR_jchair", (0, 5.7, 1.0), c, seat_col="#3d271a", rot=180)
    # Witness stand with mic
    box("CR_witness", (2.6, 2.4, 2.1), (-5.2, 2.6, 1.05), m_oak, 0.04, coll=c)
    prop_desk_mic("CR_wmic", (-4.8, 1.8, 2.11), coll=c)
    # 4: Counsel tables + stacked law books + brass rail + chairs
    for sx, x in (("L", -4.2), ("R", 4.2)):
        box(f"CR_tbl_{sx}", (3.8, 1.7, 0.22), (x, -2.0, 2.1), m_oak, 0.04, coll=c)
        for lx in (-1.6, 1.6):
            for ly in (-0.6, 0.6):
                box(f"CR_tl_{sx}_{lx}_{ly}", (0.2, 0.2, 2.0), (x + lx, -2.0 + ly, 1.0), m_dark, 0.02, coll=c)
        _chair(f"CR_ch_{sx}", (x, -3.2, 0), c, seat_col="#7a1f24", rot=0)
        ST.books(f"CR_bk_{sx}", (x - 0.6, -2.0, 2.22), c, n=3, lie=True)
    # Brass dividing rail + courtroom lamps + corner flag/plant
    box("CR_rail_L", (6.5, 0.14, 0.14), (-6.2, -4.6, 1.8), m_gold, 0.02, coll=c)
    box("CR_rail_R", (6.5, 0.14, 0.14), (6.2, -4.6, 1.8), m_gold, 0.02, coll=c)
    cyl("CR_flag_pole", 0.08, 6.2, (7.6, 6.2, 3.1), m_gold, 12, coll=c)
    box("CR_flag", (0.25, 1.4, 3.2), (7.3, 6.2, 4.4), m_red, 0.06, coll=c)
    ST.plant("CR_plant", (8.2, 6.2, 0), c, s=1.3)
    return c


def diner():
    """Retro burger diner with kitchen pass-through hatch, neon menu PNG, wood booths & burger trays."""
    c = _room_shell("Diner", 18, 14, 8.5, "#f8edd9", "#e6e6e6", "#d63838", skip_walls=("back",))
    world(hexc("#ffd7a8"), 0.75)
    _room_lights("DN", c, energy=1950, color="#fff0d4")
    m_chk = ST.checker_mat("DN_floor_chk", "#1b1b1e", "#f4f4f4", 0.65)
    for o in c.objects:
        if o.name.endswith("_floor"):
            o.data.materials[0] = m_chk
    mw = mat("DN_wall_b", hexc("#f8edd9"), 0.72)
    m_red = mat("DN_red", hexc("#d62828"), 0.35)
    m_chrome = mat("DN_chrome", hexc("#d0d7de"), 0.18, metal=0.88)
    m_wood = ST.wood("DN_wood", "#925a34", "#c68b58", 1.8)
    # 1: Kitchen pass-through service hatch cutout in back wall
    _window_wall("DN_hatch", "y", 6.8, (-9.0, 9.0), 8.5, (-3.4, 3.4, 2.2, 4.6),
                 mw, m_chrome, c, inner_sign=1, sky_col=(1.0, 0.94, 0.78), estr=1.4, outside_trees=False, glass=False)
    box("DN_kitch_s", (7.4, 1.4, 0.2), (0, 7.6, 2.2), m_chrome, 0.02, coll=c)
    # 2: Framed PNG Diner Menu Board mounted above pass-through
    _tex_panel("DN_menu", 5.8, 2.1, (0, 6.72, 6.2), "diner_menu.png", "-Y", emit=1.1, coll=c, frame_col="#d62828")
    # Counter at back + wood top + chrome swivel stools
    box("DN_counter", (10.4, 1.8, 2.1), (0, 4.0, 1.05), m_red, 0.04, coll=c)
    box("DN_counter_top", (10.7, 2.1, 0.2), (0, 4.0, 2.15), m_chrome, 0.02, coll=c)
    for sx in (-3.6, -1.2, 1.2, 3.6):
        cyl(f"DN_stool_{sx}", 0.16, 1.45, (sx, 2.3, 0.72), m_chrome, 16, coll=c)
        cyl(f"DN_sbase_{sx}", 0.55, 0.08, (sx, 2.3, 0.04), m_chrome, 16, coll=c)
        cyl(f"DN_seat_{sx}", 0.62, 0.25, (sx, 2.3, 1.5), m_red, 16, coll=c)
    # 3 & 4: Booths on left and right with ST.wood tables, burger trays & condiment bottles
    for side, bx in (("L", -6.0), ("R", 6.0)):
        box(f"DN_b_{side}_t", (2.8, 2.1, 0.22), (bx, -0.6, 1.7), m_wood, 0.04, coll=c)
        cyl(f"DN_b_{side}_leg", 0.16, 1.6, (bx, -0.6, 0.8), m_chrome, 12, coll=c)
        box(f"DN_b_{side}_s1", (2.8, 1.2, 1.85), (bx, -2.5, 0.92), m_red, 0.06, coll=c)
        box(f"DN_b_{side}_s2", (2.8, 1.2, 1.85), (bx, 1.3, 0.92), m_red, 0.06, coll=c)
    prop_burger_tray("DN_tray1", (-5.8, -0.6, 1.82), coll=c)
    prop_burger_tray("DN_tray2", (1.2, 4.0, 2.26), coll=c)
    cyl("DN_ketchup", 0.12, 0.45, (-5.1, -0.2, 2.04), m_red, 10, coll=c)
    cyl("DN_mustard", 0.12, 0.45, (-4.8, -0.2, 2.04), mat("DN_must", hexc("#facc15"), 0.35), 10, coll=c)
    # Jukebox on right rear + corner plant
    box("DN_juke", (2.0, 1.4, 3.6), (6.6, 5.5, 1.8), m_red, 0.12, coll=c)
    box("DN_juke_gl", (1.3, 0.1, 1.6), (6.6, 4.78, 2.3), ST.emit_mat("DN_jk", hexc("#38bdf8"), 2.5), 0.04, coll=c)
    ST.plant("DN_plant", (-7.6, 5.4, 0), c, s=1.2)
    return c


def grocery_store():
    """Bright supermarket aisle with storefront glass entrance, overhead sign PNG, carts & crates."""
    c = _room_shell("GroceryStore", 20, 16, 9.0, "#f3f6f8", "#d8dee6", "#3b82f6", skip_walls=("back",))
    world(hexc("#eaf4ff"), 0.85)
    _room_lights("GS", c, key_z=8.2, energy=2150, color="#ffffff")
    mw = mat("GS_wall_b", hexc("#f3f6f8"), 0.72)
    m_trim = mat("GS_trim_b", hexc("#3b82f6"), 0.35)
    m_shelf = mat("GS_shelf", hexc("#cbd5e1"), 0.25, metal=0.6)
    m_wood = ST.wood("GS_wood", "#a87042", "#d49b62", 1.8)
    # 1 & 5: Storefront glass window bay on back-right looking out to sunny street/trees
    _window_wall("GS_win", "y", 7.8, (-10.0, 10.0), 9.0, (2.2, 7.6, 1.0, 6.6),
                 mw, m_trim, c, inner_sign=1, sky_col=(0.68, 0.88, 1.0))
    # 2: Overhead Market Aisle Banner PNG
    _tex_panel("GS_sign", 6.2, 1.8, (-3.2, 7.7, 6.4), "grocery_sign.png", "-Y", coll=c, frame_col="#2563eb")
    colors = ["#ef4444", "#f59e0b", "#10b981", "#3b82f6", "#ec4899", "#8b5cf6"]
    mats = [mat(f"GS_p_{i}", hexc(col), 0.45) for i, col in enumerate(colors)]
    for side_x in (-5.8, 5.8):
        box(f"GS_rack_{side_x}", (2.2, 10.4, 5.6), (side_x, 0.5, 2.8), m_shelf, 0.04, coll=c)
        for row_z in (1.2, 2.6, 4.0, 5.2):
            box(f"GS_shlf_{side_x}_{row_z}", (2.4, 10.4, 0.14), (side_x, 0.5, row_z - 0.48), m_wood, 0.01, coll=c)
            for idx, py in enumerate((-3.2, -1.4, 0.4, 2.2, 4.0)):
                if (idx + int(row_z)) % 2 == 0:
                    box(f"GS_box_{side_x}_{row_z}_{idx}", (1.5, 1.15, 0.85),
                        (side_x, py, row_z), mats[(idx + int(row_z)) % len(mats)], 0.03, coll=c)
                else:
                    cyl(f"GS_can_{side_x}_{row_z}_{idx}", 0.45, 0.9,
                        (side_x, py, row_z), mats[(idx + int(row_z)) % len(mats)], 12, coll=c)
    # 3 & 4: Wood & metal checkout counter + belt + register + shopping cart + produce crates
    box("GS_chk", (4.8, 1.9, 1.9), (-2.8, 4.6, 0.95), m_wood, 0.04, coll=c)
    box("GS_chk_trim", (4.9, 2.0, 0.18), (-2.8, 4.6, 1.92), mat("GS_blue", hexc("#2563eb"), 0.35), 0.02, coll=c)
    box("GS_belt", (2.8, 1.4, 0.1), (-3.4, 4.6, 2.05), mat("GS_belt", hexc("#1e293b"), 0.6), 0.01, coll=c)
    box("GS_reg", (0.9, 0.9, 0.65), (-1.2, 4.6, 2.35), m_shelf, 0.03, coll=c)
    prop_shopping_cart("GS_cart", (-1.8, -1.2, 0), coll=c)
    # 5: Potted produce corner plant
    ST.plant("GS_plant", (-8.2, 5.8, 0), c, s=1.25)
    return c


def gym():
    """School basketball gym with hardwood planks, clerestory windows, scoreboard PNG & lockers."""
    c = _room_shell("SchoolGym", 24, 18, 11.0, "#e6dfd3", "#d49b57", "#1e3a8a", tiled_floor=False, skip_walls=("back",))
    world(hexc("#e8f0fa"), 0.85)
    _room_lights("GY", c, key_z=9.8, energy=2650, color="#fff9ee")
    # Real hardwood court planks
    for o in c.objects:
        if o.name.endswith("_floor"):
            o.data.materials[0] = ST.planks("GY_court_planks", "#d89f5c", "#c68c48", "#8b5e34")
    mw = mat("GY_wall_b", hexc("#e6dfd3"), 0.72)
    m_navy = mat("GY_navy", hexc("#1e3a8a"), 0.35)
    # 1 & 5: Back-left clerestory window bay
    _window_wall("GY_win", "y", 8.8, (-12.0, 12.0), 11.0, (-9.8, -4.6, 5.8, 9.4),
                 mw, m_navy, c, inner_sign=1, sky_col=(0.68, 0.88, 1.0))
    m_line = mat("GY_line", hexc("#ffffff"), 0.4)
    m_wood = ST.wood("GY_bleach", "#8c5429", "#c2864f", 1.8)
    m_board = mat("GY_board", hexc("#ffffff"), 0.22)
    m_rim = mat("GY_rim", hexc("#f97316"), 0.25, metal=0.7)
    m_lock = mat("GY_lock", hexc("#3b82f6"), 0.35, metal=0.5)
    # Court markings + key box
    box("GY_midline", (20.0, 0.22, 0.02), (0, -2.0, 0.01), m_line, 0, coll=c)
    cyl("GY_circle", 2.4, 0.02, (0, -2.0, 0.01), m_line, 24, coll=c)
    box("GY_keyL", (0.2, 6.0, 0.02), (-3.0, 5.5, 0.01), m_line, 0, coll=c)
    box("GY_keyR", (0.2, 6.0, 0.02), (3.0, 5.5, 0.01), m_line, 0, coll=c)
    # 2: Scoreboard banner PNG above hoop
    _tex_panel("GY_score", 6.2, 2.0, (0, 8.72, 9.2), "gym_banner.png", "-Y", coll=c, frame_col="#1e3a8a")
    # Backboard with shooter square, hoop & net + basketball prop
    box("GY_pole", (0.45, 0.45, 7.2), (0, 7.6, 3.6), mat("GY_st", hexc("#334155"), 0.35, metal=0.7), 0.02, coll=c)
    box("GY_bboard", (3.8, 0.16, 2.5), (0, 7.0, 6.6), m_board, 0.03, coll=c)
    box("GY_sq", (1.3, 0.04, 1.0), (0, 6.9, 6.4), m_rim, 0.01, coll=c)
    box("GY_hoop", (1.2, 1.2, 0.12), (0, 6.1, 5.8), m_rim, 0.02, coll=c)
    prop_basketball("GY_ball", (1.8, 0.6, 0), coll=c)
    # 3 & 4: Wood-grain stepped bleachers (left) & team lockers + bench + trophies (right)
    for step in range(4):
        box(f"GY_bl_{step}", (2.2, 12.0, 0.8), (-10.4 + step * 1.1, 0, 0.4 + step * 0.8), m_wood, 0.03, coll=c)
    for lk in range(4):
        box(f"GY_lk_{lk}", (1.4, 1.6, 5.2), (10.8, -2.0 + lk * 1.8, 2.6), m_lock, 0.04, coll=c)
    box("GY_bench", (1.4, 6.0, 0.22), (8.2, 1.0, 1.1), m_wood, 0.03, coll=c)
    prop_trophy("GY_tr1", (5.5, 8.0, 0.0), coll=c)
    ST.plant("GY_plant", (9.6, 7.2, 0), c, s=1.25)
    return c


def police_station():
    """Police precinct with barred holding cell opening, mugshot height chart & WANTED PNGs."""
    c = _room_shell("PoliceStation", 18, 14, 8.5, "#dbe4ee", "#94a3b8", "#1e3a8a", skip_walls=("back",))
    world(hexc("#cbd5e1"), 0.55)
    _room_lights("PS", c, energy=1350, color="#f4f8ff", fill_energy=700)
    mw = mat("PS_wall_b", hexc("#dbe4ee"), 0.72)
    m_steel = mat("PS_steel", hexc("#475569"), 0.25, metal=0.8)
    m_wood = ST.wood("PS_wood", "#5a3a24", "#8f613f", 1.8)
    m_blue = mat("PS_blue", hexc("#1d4ed8"), 0.4)
    # 1: Barred holding cell opening in back-right via wall_with_hole
    _window_wall("PS_cell", "y", 6.8, (-9.0, 9.0), 8.5, (2.6, 7.0, 0.2, 6.2),
                 mw, m_steel, c, inner_sign=1, sky_col=(0.45, 0.52, 0.62), estr=1.2, outside_trees=False, glass=False)
    for bx in (3.3, 4.05, 4.8, 5.55, 6.3):
        cyl(f"PS_bar_{bx}", 0.08, 6.0, (bx, 6.8, 3.2), m_steel, 10, coll=c)
    # 2: Crisp Mugshot Height Chart PNG + WANTED Pepper poster PNG
    _tex_panel("PS_chart", 3.4, 4.5, (0.2, 6.72, 3.2), "police_chart.png", "-Y", coll=c, frame_col="#1e3a8a")
    _tex_panel("PS_wanted", 3.2, 1.8, (-5.2, 6.72, 4.8), "wanted_pepper.png", "-Y", coll=c, frame_col="#5b4636")
    # 3 & 4: Wood & steel booking desk + monitor + mic + chairs + books + water cooler
    box("PS_desk", (6.5, 1.9, 2.2), (-3.8, 2.5, 1.1), m_wood, 0.04, coll=c)
    box("PS_desk_top", (6.7, 2.1, 0.18), (-3.8, 2.5, 2.25), m_steel, 0.02, coll=c)
    box("PS_mon", (1.6, 0.14, 1.05), (-5.2, 2.4, 3.0), mat("PS_mon", hexc("#0f172a"), 0.2), 0.02, coll=c)
    box("PS_scr", (1.42, 0.04, 0.88), (-5.2, 2.31, 3.0), ST.emit_mat("PS_scr", hexc("#38bdf8"), 2.2), 0.01, coll=c)
    prop_desk_mic("PS_mic", (-3.2, 2.1, 2.34), coll=c)
    ST.books("PS_files", (-1.6, 2.5, 2.34), c, n=4, lie=True)
    _chair("PS_chair", (-4.2, 4.0, 0), c, seat_col="#1e3a8a", rot=180)
    cyl("PS_cooler_b", 0.55, 2.0, (-7.4, 5.2, 1.0), mat("PS_w", hexc("#f8fafc"), 0.35), 14, coll=c)
    cyl("PS_cooler_w", 0.45, 1.0, (-7.4, 5.2, 2.5), mat("PS_aq", hexc("#38bdf8"), 0.15, alpha=0.6), 14, coll=c)
    # 5: Corner plant
    ST.plant("PS_plant", (-7.6, 0.5, 0), c, s=1.2)
    return c


def park_day():
    """Sunny city park with low brick arch wall, welcome sign PNG, fountain, lamps, benches & trees."""
    c = _coll("ParkDay")
    world(hexc("#7ec8f8"), 0.85)
    W.sun(2.6, (48, -22, 35))
    light("PK_fill", "AREA", (0, -10, 12), 750, hexc("#fff8eb"), size=18.0, rot=(35, 0, 0), coll=c)
    m_grass = mat("PK_grass", hexc("#4ade80"), 0.85)
    m_path = ST.tiles("PK_path", "#d6d3d1", "#9ca3af", 0.35, 1.2, 1.2, 0.65, axis="XY")
    m_wood = ST.wood("PK_wood", "#78350f", "#b06d38", 1.8)
    m_brick = ST.tiles("PK_brick", "#9f4a3b", "#cbd5e1", 0.5, 1.4, 0.6, 0.7, axis="XZ")
    m_iron = mat("PK_iron", hexc("#1e293b"), 0.35, metal=0.75)
    m_trunk = ST.wood("PK_trunk", "#5a2a0c", "#7c3f1d", 2.5)
    m_leaf = mat("PK_leaf", hexc("#16a34a"), 0.7)
    box("PK_ground", (60, 60, 0.4), (0, 0, -0.2), m_grass, 0, coll=c)
    box("PK_path", (5.8, 45, 0.08), (0, 0, 0.04), m_path, 0.01, coll=c)
    # 1: Park stone/brick entrance wall with archway gate cutout
    ST.wall_with_hole("PK_gate", "y", 11.5, (-14, 14), (0, 3.6), (-3.2, 3.2, 0, 3.6), 0.7, m_brick, c, inner_sign=1)
    for gx in (-3.2, 3.2):
        box(f"PK_pil_{gx}", (1.1, 1.1, 4.4), (gx, 11.8, 2.2), m_brick, 0.04, coll=c)
    # 2: Welcome Signboard PNG on wooden posts
    cyl("PK_sp1", 0.12, 3.4, (-6.2, 2.2, 1.7), m_wood, 10, coll=c)
    cyl("PK_sp2", 0.12, 3.4, (-3.4, 2.2, 1.7), m_wood, 10, coll=c)
    _tex_panel("PK_sign", 3.4, 1.8, (-4.8, 2.1, 2.7), "park_sign.png", "-Y", coll=c, frame_col="#5a2a0c")
    # 3 & 4: Wood park benches + iron legs + water fountain + streetlamps + trash bin
    for bx, rot in ((4.8, 0), (-4.8, 0)):
        box(f"PK_bs_{bx}", (4.2, 1.3, 0.24), (bx, 5.0, 1.0), m_wood, 0.03, coll=c)
        box(f"PK_bb_{bx}", (4.2, 0.22, 1.15), (bx, 5.6, 1.65), m_wood, 0.03, coll=c)
        for lx in (-1.6, 1.6):
            box(f"PK_bl_{bx}_{lx}", (0.18, 1.2, 0.9), (bx + lx, 5.0, 0.45), m_iron, 0.02, coll=c)
    # Stone water fountain center-back
    cyl("PK_fount_b", 2.6, 0.75, (0, 8.2, 0.37), m_brick, 24, coll=c)
    cyl("PK_fount_w", 2.2, 0.15, (0, 8.2, 0.76), mat("PK_wat", hexc("#38bdf8"), 0.12), 24, coll=c)
    cyl("PK_fount_c", 0.5, 2.2, (0, 8.2, 1.2), m_brick, 16, coll=c)
    # Streetlamps
    for lx in (-3.4, 3.4):
        cyl(f"PK_lp_{lx}", 0.12, 5.8, (lx, -1.5, 2.9), m_iron, 10, coll=c)
        sphere(f"PK_lb_{lx}", 0.38, (lx, -1.5, 6.0), ST.emit_mat(f"PK_lm{lx}", hexc("#fef08a"), 2.5), coll=c)
    # 5: Multi-tiered trees, bushes & clouds
    for tx, ty in ((-7.5, 6.5), (7.8, 7.5), (-8.5, 14.5), (7.2, 15.0), (-4.0, 17.5), (4.5, 18.0)):
        cyl(f"PK_tr_{tx}_{ty}", 0.55, 4.0, (tx, ty, 2.0), m_trunk, 10, coll=c)
        box(f"PK_lf_{tx}_{ty}", (3.6, 3.6, 3.0), (tx, ty, 5.0), m_leaf, 0.25, coll=c)
        box(f"PK_lf2_{tx}_{ty}", (2.4, 2.4, 1.8), (tx, ty, 6.9), m_leaf, 0.2, coll=c)
    ST.plant("PK_shrub1", (3.8, 1.5, 0), c, s=1.2)
    ST.plant("PK_shrub2", (-3.5, 7.2, 0), c, s=1.1)
    return c


def rooftop_night():
    """City rooftop at night with stairwell bulkhead doorway, lit neon billboard PNG, HVAC & skyline."""
    c = _coll("RooftopNight")
    world(hexc("#0c1428"), 0.5)
    light("RT_moon", "SUN", (10, 15, 25), 2.5, hexc("#9ec5ff"), rot=(42, 0, -25), coll=c)
    light("RT_fill", "AREA", (0, -8, 9), 950, hexc("#ffd8a8"), size=14.0, rot=(30, 0, 0), coll=c)
    m_conc = ST.tiles("RT_conc", "#475569", "#334155", 0.35, 1.8, 1.8, 0.75, axis="XY")
    m_wall = mat("RT_wall", hexc("#64748b"), 0.7)
    m_metal = mat("RT_metal", hexc("#94a3b8"), 0.25, metal=0.75)
    m_bldg = mat("RT_bldg", hexc("#1e293b"), 0.6)
    m_win = ST.emit_mat("RT_win", hexc("#fde047"), 3.5)
    box("RT_deck", (22, 20, 0.5), (0, 0, -0.25), m_conc, 0.04, coll=c)
    box("RT_parapet", (22, 0.8, 1.6), (0, 9.6, 0.8), m_wall, 0.04, coll=c)
    # 1: Rooftop stairwell bulkhead with recessed lit doorway cutout
    ST.wall_with_hole("RT_bulk_f", "y", 5.2, (-8.5, -2.5), (0, 5.2), (-6.8, -4.4, 0, 4.2),
                      0.5, m_wall, c, inner_sign=1)
    box("RT_bulk_side", (0.5, 3.6, 5.2), (-2.5, 7.0, 2.6), m_wall, 0.03, coll=c)
    box("RT_bulk_roof", (6.5, 4.0, 0.4), (-5.5, 7.0, 5.2), m_metal, 0.03, coll=c)
    card("RT_door_gl", 2.2, 4.0, (-5.6, 5.8, 2.1), ST.emit_mat("RT_dr", hexc("#fbbf24"), 1.6), "-Y", coll=c)
    # 2: Lit rooftop neon billboard PNG on steel truss legs
    for lx in (3.2, 7.6):
        cyl(f"RT_bl_{lx}", 0.14, 5.2, (lx, 7.4, 2.6), m_metal, 10, coll=c)
    _tex_panel("RT_bill", 5.8, 2.5, (5.4, 7.2, 4.4), "rooftop_billboard.png", "-Y", emit=1.5, coll=c, frame_col="#334155")
    # 3 & 4: Metal HVAC unit with spinning fan hub, silver ducts, parapet posts & water tower
    box("RT_ac", (3.2, 2.4, 2.2), (-0.8, 6.0, 1.1), m_metal, 0.05, coll=c)
    cyl("RT_fan", 0.75, 0.18, (-0.8, 4.75, 1.2), mat("RT_fn", hexc("#1e293b"), 0.3, metal=0.8), 16, rot=(90, 0, 0), coll=c)
    box("RT_duct", (4.5, 0.8, 0.8), (1.8, 6.2, 0.5), m_metal, 0.04, coll=c)
    for px in range(-9, 10, 3):
        cyl(f"RT_post_{px}", 0.09, 1.2, (px, 9.6, 2.0), m_metal, 8, coll=c)
    box("RT_rail", (20, 0.1, 0.1), (0, 9.6, 2.6), m_metal, 0.01, coll=c)
    # 5: Planter + Distant skyline towers with emissive windows
    ST.plant("RT_plant", (-2.0, 4.8, 0), c, s=1.1)
    for i, (bx, by, bh) in enumerate([(-16, 26, 22), (-7, 30, 28), (4, 28, 24), (15, 25, 20)]):
        box(f"RT_sky_{i}", (7.0, 7.0, bh), (bx, by, bh / 2 - 12), m_bldg, 0.05, coll=c)
        box(f"RT_win_{i}", (4.5, 0.2, bh * 0.5), (bx, by - 3.6, bh * 0.2), m_win, 0, coll=c)
    return c


def subway_station():
    """Underground metro platform with ceramic tiled walls, ticket booth hatch, map PNG & train."""
    c = _room_shell("Subway", 24, 14, 8.5, "#cbd5e1", "#64748b", "#334155", skip_walls=("back",))
    world(hexc("#1e293b"), 0.55)
    _room_lights("SB", c, energy=1900, color="#f8fafc")
    m_wall_tile = ST.tiles("SB_wtiles", "#e2e8f0", "#64748b", 0.5, 1.4, 0.7, 0.3, axis="XZ")
    m_frame = mat("SB_tfr", hexc("#334155"), 0.35, metal=0.6)
    # 1: Recessed ticket booth / passage cutout behind platform
    _window_wall("SB_booth", "y", 6.8, (-12.0, 12.0), 8.5, (4.2, 8.6, 2.2, 5.2),
                 m_wall_tile, m_frame, c, inner_sign=1, sky_col=(0.95, 0.9, 0.7), estr=1.4, outside_trees=False)
    # 2: Central Station Metro Map PNG framed on back wall left
    _tex_panel("SB_map", 5.2, 2.8, (-5.4, 6.72, 4.6), "subway_map.png", "-Y", coll=c, frame_col="#1e3a8a")
    m_yel = mat("SB_yel", hexc("#facc15"), 0.4)
    m_train = mat("SB_train", hexc("#94a3b8"), 0.22, metal=0.78)
    m_blue = mat("SB_tblue", hexc("#2563eb"), 0.35)
    m_wood = ST.wood("SB_wood", "#854d27", "#b87a48", 1.8)
    m_glow = ST.emit_mat("SB_tw", hexc("#fef08a"), 2.4)
    # Yellow tactile safety stripe & dots
    box("SB_safety", (22, 0.6, 0.05), (0, 2.8, 0.025), m_yel, 0, coll=c)
    for px in (-6.5, 0.0, 6.5):
        box(f"SB_pil_{px}", (0.9, 0.9, 8.5), (px, 0.8, 4.25), m_blue, 0.04, coll=c)
        box(f"SB_pbase_{px}", (1.15, 1.15, 0.45), (px, 0.8, 0.22), m_frame, 0.02, coll=c)
    # 3 & 4: Wood & steel platform benches, ticket kiosk, trash bins
    for bx in (-3.2, 3.2):
        box(f"SB_bnch_{bx}", (3.4, 1.3, 0.2), (bx, 0.4, 1.0), m_wood, 0.03, coll=c)
        box(f"SB_bnch_b_{bx}", (3.4, 0.18, 0.95), (bx, 1.0, 1.55), m_wood, 0.03, coll=c)
        for lx in (-1.3, 1.3):
            box(f"SB_bl_{bx}_{lx}", (0.16, 1.0, 0.95), (bx + lx, 0.4, 0.47), m_frame, 0.02, coll=c)
    box("SB_kiosk", (1.6, 1.2, 3.6), (8.8, -1.0, 1.8), m_blue, 0.05, coll=c)
    cyl("SB_bin", 0.55, 1.4, (-8.8, 0.6, 0.7), m_frame, 14, coll=c)
    # Subway train car with glowing windows & headlight
    box("SB_car", (18.0, 3.4, 5.0), (0, 4.8, 2.6), m_train, 0.12, coll=c)
    box("SB_stripe", (18.05, 3.45, 0.7), (0, 4.8, 2.0), m_blue, 0.02, coll=c)
    for wx in (-6.0, -3.0, 0.0, 3.0, 6.0):
        box(f"SB_cw_{wx}", (1.9, 0.1, 1.4), (wx, 3.06, 3.5), m_glow, 0.03, coll=c)
    # 5: Platform corner planter box
    ST.plant("SB_plant", (-10.2, 2.0, 0), c, s=1.15)
    return c


def space_station():
    """Sci-fi space station bridge with wide Earth viewport cutout, HUD PNG & metallic consoles."""
    c = _room_shell("SpaceStation", 18, 14, 8.5, "#334155", "#1e293b", "#0ea5e9", skip_walls=("back",))
    W.space_world()
    _room_lights("SS", c, energy=1800, color="#e0f2fe")
    mw = mat("SS_wall_b", hexc("#334155"), 0.5, metal=0.45)
    m_deck = mat("SS_deck", hexc("#475569"), 0.25, metal=0.8)
    m_cyan = ST.emit_mat("SS_cyan", hexc("#38bdf8"), 4.0)
    m_org = ST.emit_mat("SS_org", hexc("#fb923c"), 3.5)
    # 1 & 5: Wide bridge viewport cutout showing outer space + planet Earth!
    _window_wall("SS_view", "y", 6.8, (-9.0, 9.0), 8.5, (-5.2, 5.2, 2.6, 6.8),
                 mw, m_deck, c, inner_sign=1, sky_col=(0.02, 0.04, 0.12), estr=0.6, outside_trees=False)
    W.cloud("SS_neb", (-5.5, 16.0, 5.5), 0.7, c, seed=7)
    sphere("SS_planet", 3.4, (3.2, 16.5, 4.5), mat("SS_earth", hexc("#1d4ed8"), 0.55), coll=c)
    # 2: Glowing HUD radar monitor PNG center console
    _tex_panel("SS_hud", 4.4, 2.2, (0, 4.0, 3.0), "space_hud.png", "-Y", emit=1.1, coll=c, frame_col="#0ea5e9")
    # 3 & 4: Metallic bridge command console, flanking glowing screens, comms rack, chairs & hydro-pod plant
    box("SS_console", (8.2, 2.0, 1.9), (0, 3.2, 0.95), m_deck, 0.06, coll=c)
    box("SS_scr1", (2.2, 0.12, 1.1), (-3.2, 2.9, 2.4), m_cyan, 0.02, rot=(-25, 0, 12), coll=c)
    box("SS_scr2", (2.2, 0.12, 1.1), (3.2, 2.9, 2.4), m_org, 0.02, rot=(-25, 0, -12), coll=c)
    for bx in (-2.0, -0.8, 0.8, 2.0):
        cyl(f"SS_btn_{bx}", 0.12, 0.14, (bx, 2.5, 1.96), m_cyan if bx < 0 else m_org, 10, coll=c)
    _chair("SS_p1", (-2.6, 1.0, 0), c, seat_col="#0ea5e9", rot=180)
    _chair("SS_p2", (2.6, 1.0, 0), c, seat_col="#0ea5e9", rot=180)
    box("SS_rack", (1.6, 1.4, 5.2), (-7.2, 4.6, 2.6), m_deck, 0.04, coll=c)
    box("SS_r_led", (1.2, 0.08, 0.25), (-7.2, 3.86, 4.2), m_cyan, 0.01, coll=c)
    # 5: Hydroponics bio-pod plant on right
    ST.plant("SS_plant", (7.0, 4.8, 0), c, s=1.2)
    return c


def haunted_house():
    """Spooky mansion foyer with moonlit gothic window cutout, portrait PNG, wood clock & bookshelves."""
    c = _room_shell("HauntedHouse", 18, 14, 9.5, "#2e2438", "#3d2c2e", "#1a1420", tiled_floor=False, skip_walls=("back",))
    world(hexc("#120d1a"), 0.45)
    for o in c.objects:
        if o.name.endswith("_floor"):
            o.data.materials[0] = ST.planks("HH_planks", "#4a3228", "#3d2820", "#1a1210")
    light("HH_purp", "AREA", (-3, -2, 7.5), 1450, hexc("#a855f7"), size=9.0, rot=(20, 0, 0), coll=c)
    light("HH_grn", "AREA", (3, 1, 6.5), 950, hexc("#4ade80"), size=8.0, rot=(10, 0, 0), coll=c)
    mw = mat("HH_wall_b", hexc("#2e2438"), 0.72)
    m_wood = ST.wood("HH_wood", "#3c261d", "#634031", 2.0)
    m_gold = mat("HH_gold", hexc("#b4933b"), 0.35, metal=0.7)
    m_red = mat("HH_rug", hexc("#5b1929"), 0.85)
    # 1 & 5: Moonlit gothic arched window cutout in back-right showing night sky & moonbeams
    _window_wall("HH_win", "y", 6.8, (-9.0, 9.0), 9.5, (2.8, 6.2, 2.4, 7.2),
                 mw, m_wood, c, inner_sign=1, sky_col=(0.18, 0.24, 0.48), estr=1.6, outside_trees=False)
    # 2: Crooked Haunted Portrait PNG in ornate gold frame
    pt = _tex_panel("HH_portrait", 2.8, 3.6, (-4.8, 6.7, 5.0), "haunted_portrait.png", "-Y", emit=0.25, coll=c, frame_col="#b4933b")
    pt.rotation_euler = (math.radians(90), math.radians(-8), 0)
    # Carpet runner + fluted wooden pillars
    box("HH_rug", (4.0, 12.0, 0.05), (0, 0.0, 0.025), m_red, 0.01, coll=c)
    for px in (-6.6, 6.6):
        cyl(f"HH_pil_{px}", 0.65, 9.5, (px, 4.2, 4.75), m_wood, 12, coll=c)
    # 3 & 4: Carved grandfather clock, bookshelf with books, candelabra table, withered potted plant
    box("HH_clock", (2.0, 1.3, 5.8), (0, 5.8, 2.9), m_wood, 0.05, coll=c)
    cyl("HH_face", 0.62, 0.14, (0, 5.1, 4.5), m_gold, 18, rot=(90, 0, 0), coll=c)
    box("HH_pend", (0.14, 0.08, 1.6), (0, 5.1, 2.6), m_gold, 0.01, coll=c)
    box("HH_shelf", (3.2, 1.2, 4.8), (-4.5, 4.2, 2.4), m_wood, 0.04, coll=c)
    ST.books("HH_bks", (-5.4, 3.8, 2.6), c, n=4)
    ST.books("HH_bks2", (-4.2, 3.8, 1.3), c, n=3)
    ST.plant("HH_plant", (6.8, 1.8, 0), c, s=1.2)
    return c


def beach():
    """Sunny tropical beach with tiki boardwalk pier, surf shop PNG, lifeguard tower, palms & umbrellas."""
    c = _coll("Beach")
    world(hexc("#60c5ff"), 1.0)
    W.sun(6.0, (45, -18, 30))
    light("BC_fill", "AREA", (0, -8, 10), 1200, hexc("#fff9e6"), size=16.0, rot=(30, 0, 0), coll=c)
    m_sand = mat("BC_sand", hexc("#f6d58e"), 0.85)
    m_sea = mat("BC_sea", hexc("#06b6d4"), 0.18)
    m_foam = mat("BC_foam", hexc("#e0f2fe"), 0.6)
    m_wood = ST.wood("BC_wood", "#854d27", "#b97c46", 1.8)
    m_trunk = ST.wood("BC_trunk", "#6b3818", "#94562a", 2.5)
    m_leaf = mat("BC_leaf", hexc("#22c55e"), 0.65)
    m_red = mat("BC_red", hexc("#ef4444"), 0.45)
    m_white = mat("BC_w", hexc("#ffffff"), 0.35)
    box("BC_sand", (52, 24, 0.4), (0, -2, -0.2), m_sand, 0, coll=c)
    box("BC_ocean", (60, 30, 0.3), (0, 23, -0.25), m_sea, 0, coll=c)
    box("BC_foam", (54, 1.4, 0.06), (0, 9.5, 0.02), m_foam, 0.02, coll=c)
    # 1 & 3: Open-air wood boardwalk pier + lifeguard lookout station with window bay
    box("BC_pier", (4.2, 14.0, 0.24), (-0.8, 6.0, 0.14), m_wood, 0.02, coll=c)
    for px in (-2.6, 1.0):
        for py in (2.0, 7.0, 11.5):
            cyl(f"BC_post_{px}_{py}", 0.18, 1.4, (px, py, 0.7), m_trunk, 10, coll=c)
    # Lifeguard tower with window cutout on left
    box("BC_lg_legs", (3.0, 3.0, 2.2), (-6.8, 5.5, 1.1), m_wood, 0.03, coll=c)
    ST.wall_with_hole("BC_lg_cab", "y", 4.1, (-8.3, -5.3), (2.2, 4.8), (-7.7, -5.9, 2.8, 4.3),
                      0.25, m_white, c, inner_sign=1)
    box("BC_lg_roof", (3.6, 3.6, 0.35), (-6.8, 5.5, 5.0), m_red, 0.04, coll=c)
    # 2: Surf Shop Beach Signboard PNG on right
    cyl("BC_sp1", 0.12, 3.2, (4.2, 4.0, 1.6), m_wood, 10, coll=c)
    cyl("BC_sp2", 0.12, 3.2, (7.0, 4.0, 1.6), m_wood, 10, coll=c)
    _tex_panel("BC_sign", 3.4, 1.8, (5.6, 3.9, 2.6), "beach_sign.png", "-Y", coll=c, frame_col="#854d27")
    # 4: Umbrella + lounge chair + cooler + leaning surfboards
    cyl("BC_pole", 0.1, 4.0, (4.4, 1.0, 2.0), m_white, 10, coll=c)
    cyl("BC_umb", 2.4, 0.8, (4.4, 1.0, 4.0), m_red, 8, coll=c)
    box("BC_lounge", (1.6, 3.0, 0.35), (3.4, 0.2, 0.35), m_white, 0.04, rot=(0, 0, -12), coll=c)
    box("BC_cooler", (1.1, 0.7, 0.75), (5.6, 0.5, 0.37), mat("BC_cool", hexc("#2563eb"), 0.35), 0.04, coll=c)
    box("BC_surf1", (0.7, 0.14, 3.6), (2.2, 4.2, 1.8), mat("BC_sb1", hexc("#facc15"), 0.3), 0.04, rot=(-10, 8, 0), coll=c)
    # 5: Palm trees + tropical plants + clouds
    for px, py in ((-4.2, 1.2), (8.2, 6.2)):
        cyl(f"BC_palm_{px}", 0.42, 5.5, (px, py, 2.7), m_trunk, 10, rot=(0, 8, 0), coll=c)
        for ang in (0, 60, 120, 180, 240, 300):
            box(f"BC_fr_{px}_{ang}", (3.2, 0.85, 0.18), (px + 0.4, py, 5.4), m_leaf, 0.05, rot=(0, 14, ang), coll=c)
    ST.plant("BC_tplant", (-3.5, 2.8, 0), c, s=1.1)
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
