"""Render labeled visual contact sheets for all assets in engine/rbx/library.py."""
import os, sys
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
STUDIO = os.path.dirname(HERE)
if STUDIO not in sys.path:
    sys.path.insert(0, STUDIO)

from rbx import core as C, library as LIB, world as W

OUT = os.path.join(STUDIO, "catalog_previews")
os.makedirs(OUT, exist_ok=True)


def _snap(name, setup_fn, cam_pos, target):
    C.reset()
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE_NEXT"
    try:
        sc.eevee.taa_render_samples = 4
        sc.eevee.use_shadows = True
        sc.eevee.use_raytracing = False
    except Exception:
        pass
    sc.render.resolution_x, sc.render.resolution_y = 480, 360
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "PNG"
    setup_fn()
    cam = C.Cam("CatCam", lens=32)
    cam.key(0.0, cam_pos, target)
    sc.camera = cam.ob
    p = os.path.join(OUT, f"{name}.png")
    sc.render.filepath = p
    bpy.ops.render.render(write_still=True)
    return p


ENVS = [
    ("nurse_office", LIB.nurse_office, (0, -8.5, 4.0), (0, 2.5, 2.5)),
    ("courtroom", LIB.courtroom, (0, -10.5, 4.8), (0, 3.0, 2.6)),
    ("diner", LIB.diner, (0, -9.5, 4.2), (0, 2.5, 2.6)),
    ("grocery_store", LIB.grocery_store, (0, -9.5, 4.2), (0, 2.5, 2.6)),
    ("gym", LIB.gym, (0, -12.0, 5.2), (0, 3.0, 3.0)),
    ("police_station", LIB.police_station, (0, -9.5, 4.2), (0, 3.0, 2.6)),
    ("park_day", LIB.park_day, (0, -12.0, 4.8), (0, 5.0, 2.5)),
    ("rooftop_night", LIB.rooftop_night, (0, -11.0, 4.5), (0, 6.0, 2.8)),
    ("subway_station", LIB.subway_station, (0, -9.5, 4.0), (0, 3.5, 2.5)),
    ("space_station", LIB.space_station, (0, -9.5, 4.2), (0, 2.5, 2.4)),
    ("haunted_house", LIB.haunted_house, (0, -9.5, 4.2), (0, 3.0, 2.8)),
    ("beach", LIB.beach, (0, -11.0, 4.5), (0, 5.0, 2.2)),
]

env_imgs = []
for name, fn, cp, tg in ENVS:
    p = _snap("env_" + name, fn, cp, tg)
    env_imgs.append((name, p))


def _char_lineup_1():
    C.world(C.hexc("#dbeafe"), 1.0)
    W.sun(4.5, (35, -20, 25))
    C.light("CL_fill", "AREA", (0, -10, 6), 1200, C.hexc("#ffffff"), size=14, rot=(15, 0, 0))
    C.box("CL_floor", (30, 12, 0.3), (0, 0, -0.15), C.mat("CL_fl", C.hexc("#cbd5e1"), 0.5))
    roster = [
        ("police_officer", LIB.police_officer),
        ("judge", LIB.judge),
        ("doctor_nurse", LIB.doctor_nurse),
        ("chef", LIB.chef),
        ("astronaut", LIB.astronaut),
        ("bully", LIB.bully),
    ]
    for i, (nm, fn) in enumerate(roster):
        fn(nm, loc=(-7.5 + i * 3.0, 0, 0), rot=0)


def _char_lineup_2():
    C.world(C.hexc("#dbeafe"), 1.0)
    W.sun(4.5, (35, -20, 25))
    C.light("CL2_fill", "AREA", (0, -10, 6), 1200, C.hexc("#ffffff"), size=14, rot=(15, 0, 0))
    C.box("CL2_floor", (30, 12, 0.3), (0, 0, -0.15), C.mat("CL2_fl", C.hexc("#cbd5e1"), 0.5))
    roster = [
        ("nerd", LIB.nerd),
        ("rich_kid", LIB.rich_kid),
        ("ninja", LIB.ninja),
        ("robber", LIB.robber),
        ("alien", LIB.alien),
        ("robot", LIB.robot),
    ]
    for i, (nm, fn) in enumerate(roster):
        fn(nm, loc=(-7.5 + i * 3.0, 0, 0), rot=0)


def _props_lineup():
    C.world(C.hexc("#f1f5f9"), 1.0)
    W.sun(4.5, (35, -20, 25))
    C.light("PL_fill", "AREA", (0, -8, 6), 1100, C.hexc("#ffffff"), size=12, rot=(20, 0, 0))
    C.box("PL_tbl", (22, 6, 0.4), (0, 0, -0.2), C.mat("PL_tb", C.hexc("#e2e8f0"), 0.4))
    props = [
        LIB.prop_gavel, LIB.prop_burger_tray, LIB.prop_shopping_cart,
        LIB.prop_basketball, LIB.prop_treasure_chest, LIB.prop_phone,
        LIB.prop_trophy, LIB.prop_megaphone, LIB.prop_skateboard, LIB.prop_desk_mic,
    ]
    for i, fn in enumerate(props):
        x = -9.0 + (i % 5) * 4.5
        y = -1.2 if i < 5 else 1.5
        fn(f"P{i}", loc=(x, y, 0))


c1 = _snap("chars_1", _char_lineup_1, (0, -13.5, 3.2), (0, 0, 2.5))
c2 = _snap("chars_2", _char_lineup_2, (0, -13.5, 3.2), (0, 0, 2.5))
pr = _snap("props_all", _props_lineup, (0, -11.0, 4.2), (0, 0.2, 0.8))
print("Rendered all catalog PNGs in", OUT)
