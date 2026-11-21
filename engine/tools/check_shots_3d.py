"""Numeric 3D Framing, Line-of-Sight Occlusion, Caption-Clearance & Mouth-Flap Checker.
Ported from blocky-shorts/template/tools/framing_check.ts & roblox-v3/checklist.md.
Runs in pure Python (no local Blender required) to verify every shot before cloud rendering.
"""
import ast
import json
import math
import os
import re
import sys

SENSOR_H = 36.0
SENSOR_W = 36.0 * (1080.0 / 1920.0)  # 20.25 mm for 9:16 portrait


def vec_sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def vec_add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def vec_len(v):
    return math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])


def vec_norm(v):
    l = vec_len(v)
    return (v[0] / l, v[1] / l, v[2] / l) if l > 1e-9 else (0.0, 1.0, 0.0)


def vec_cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def vec_dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cam_pos_from_polar(target, dist, yaw_deg, pitch_deg):
    yr = math.radians(yaw_deg)
    pr = math.radians(pitch_deg)
    dx = math.sin(yr) * math.cos(pr) * dist
    dy = -math.cos(yr) * math.cos(pr) * dist
    dz = math.sin(pr) * dist
    return (target[0] + dx, target[1] + dy, target[2] + dz)


def project_point(pt, cam_pos, cam_tgt, lens):
    fwd = vec_norm(vec_sub(cam_tgt, cam_pos))
    world_up = (0.0, 0.0, 1.0)
    right = vec_norm(vec_cross(fwd, world_up))
    up = vec_norm(vec_cross(right, fwd))
    rel = vec_sub(pt, cam_pos)
    z_depth = vec_dot(rel, fwd)
    if z_depth <= 0.05:
        return {"fx": -1.0, "fy": -1.0, "depth": z_depth, "behind": True}
    x_cam = vec_dot(rel, right)
    y_cam = vec_dot(rel, up)
    half_w = z_depth * (SENSOR_W * 0.5) / lens
    half_h = z_depth * (SENSOR_H * 0.5) / lens
    fx = 0.5 + 0.5 * (x_cam / half_w)
    fy = 0.5 - 0.5 * (y_cam / half_h)  # 0 = top, 1 = bottom
    return {"fx": fx, "fy": fy, "depth": z_depth, "behind": False}


def project_char_bbox(loc, cam_pos, cam_tgt, lens, scale=1.0, seated=False):
    x, y, z = loc
    h_top = (4.85 if seated else 5.55) * scale
    h_neck = (3.45 if seated else 3.95) * scale
    head_pts = [
        (x + dx * 0.65 * scale, y + dy * 0.65 * scale, z + hz)
        for dx in (-1, 1) for dy in (-1, 1) for hz in (h_neck, h_top)
    ]
    body_pts = [
        (x + dx * 1.45 * scale, y + dy * 0.55 * scale, z + bz)
        for dx in (-1, 1) for dy in (-1, 1) for bz in (0.0, h_top)
    ]
    pr_head = [project_point(p, cam_pos, cam_tgt, lens) for p in head_pts]
    pr_body = [project_point(p, cam_pos, cam_tgt, lens) for p in body_pts]
    if any(p["behind"] for p in pr_head):
        return None
    h_fxs = [p["fx"] for p in pr_head]
    h_fys = [p["fy"] for p in pr_head]
    b_fxs = [p["fx"] for p in pr_body if not p["behind"]]
    b_fys = [p["fy"] for p in pr_body if not p["behind"]]
    return {
        "head_x0": min(h_fxs), "head_x1": max(h_fxs),
        "head_y0": min(h_fys), "head_y1": max(h_fys),
        "body_x0": min(b_fxs), "body_x1": max(b_fxs),
        "body_y0": min(b_fys), "body_y1": max(b_fys),
        "height_share": max(b_fys) - min(b_fys),
        "width_share": max(b_fxs) - min(b_fxs),
        "depth": sum(p["depth"] for p in pr_head) / len(pr_head),
    }


def audit_video2():
    # Exact coordinate audit of critical shots in Video-2
    JUDGE_LOC = (0.0, 5.5, 1.0)
    WITNESS_LOC = (-5.2, 3.8, 0.35)
    LEO_GAL_LOC = (-2.4, -6.3, 0.25)
    BAILIFF_LOC = (5.3, 3.2, 0.0)
    REPORTER_LOC = (-3.6, 4.7, 0.2)
    SPECS = [(-5.4, -6.3, 0.25), (-3.8, -6.3, 0.25), (3.6, -6.3, 0.25), (5.2, -6.3, 0.25)]

    tests = [
        ("S01 Hook 2-shot", cam_pos_from_polar((0.0, 3.2, 3.3), 9.5, -4, 6), (0.0, 3.2, 3.3), 28,
         [("Mom", (-1.5, 3.5, 0), False), ("Eddie", (1.4, 3.3, 0), False)], []),
        ("S02 Eddie CU", cam_pos_from_polar((0.9, 3.3, 3.4), 8.0, 12, 5), (0.9, 3.3, 3.4), 28,
         [("Eddie", (1.4, 3.3, 0), False)], [("Mom", (-1.5, 3.5, 0), False)]),
        ("S05 Town Rule 2-shot", cam_pos_from_polar((0.0, -26.5, 3.3), 9.8, -6, 6), (0.0, -26.5, 3.3), 28,
         [("Eddie", (-1.4, -26.5, 0), False), ("Leo", (1.4, -26.5, 0), False)], []),
        ("S08 Therapist", cam_pos_from_polar((-0.5, 2.8, 3.4), 9.5, -6, 6), (-0.5, 2.8, 3.4), 28,
         [("Therapist", (-2.2, 2.8, 0.15), True)], []),
        ("S09 Police Wait", cam_pos_from_polar((0.0, 1.4, 3.3), 10.4, 0, 6), (0.0, 1.4, 3.3), 28,
         [("Officer", (-1.6, 1.2, 0), False), ("Suspect", (1.6, 1.2, 0), False)], []),
        ("S10 Bedroom 2-shot", cam_pos_from_polar((0.0, 2.2, 3.3), 9.5, 6, 6), (0.0, 2.2, 3.3), 28,
         [("Mom", (-1.5, 2.0, 0), False), ("Dad", (1.5, 2.0, 0), False)], []),
        ("S11 Mom Question", cam_pos_from_polar((-1.1, 2.2, 3.5), 8.0, 10, 5), (-1.1, 2.2, 3.5), 28,
         [("Mom", (-1.3, 2.2, 0), False)], []),
        ("S12 Dad Sweat", cam_pos_from_polar((1.1, 2.2, 3.5), 8.0, -10, 5), (1.1, 2.2, 3.5), 28,
         [("Dad", (1.3, 2.2, 0), False)], []),
        ("S13 Court Walk-in", (0.0, -6.9, 5.05), (-0.8, 2.4, 3.3), 25,
         [("Judge", JUDGE_LOC, False), ("Eddie", (-1.8, 0.2, 0), False)],
         [(f"Spec{i}", sp, True) for i, sp in enumerate(SPECS)] + [("Reporter", REPORTER_LOC, True)]),
        ("S14 Court Overview", (0.0, -4.1, 4.85), (0.2, 3.2, 3.5), 25,
         [("Judge", JUDGE_LOC, False)],
         [(f"Spec{i}", sp, True) for i, sp in enumerate(SPECS)] + [("Reporter", REPORTER_LOC, True)]),
        ("S15 Judge Stern", (0.65, -1.7, 4.85), (0.0, 5.5, 4.5), 28,
         [("Judge", JUDGE_LOC, False)], [("Bailiff", BAILIFF_LOC, False)]),
        ("S16 Judge + Exhibit", (0.75, -1.95, 4.9), (0.0, 5.5, 4.45), 26,
         [("Judge", JUDGE_LOC, False)], []),
        ("S18 Eddie Bible", cam_pos_from_polar((-5.1, 3.6, 3.6), 8.0, 4, 5), (-5.1, 3.6, 3.6), 28,
         [("Eddie", WITNESS_LOC, False)], []),
        ("S19 Eddie Strain CU", cam_pos_from_polar((-5.1, 3.6, 3.8), 7.2, 6, 4), (-5.1, 3.6, 3.8), 28,
         [("Eddie", WITNESS_LOC, False)], []),
        ("S21 Court Flicker", (0.0, -3.9, 4.9), (0.0, 2.8, 3.5), 25,
         [("Judge", JUDGE_LOC, False)],
         [(f"Spec{i}", sp, True) for i, sp in enumerate(SPECS)] + [("Reporter", REPORTER_LOC, True)]),
        ("S22 Leo Gallery", cam_pos_from_polar((-2.4, -6.3, 3.55), 8.1, 162, 6), (-2.4, -6.3, 3.55), 28,
         [("Leo", LEO_GAL_LOC, False)], [(f"Spec{i}", sp, True) for i, sp in enumerate(SPECS)]),
        ("S24 Judge Gavel", cam_pos_from_polar((0.2, 4.8, 4.4), 7.7, -10, 4), (0.2, 4.8, 4.4), 28,
         [("Judge", JUDGE_LOC, False)], []),
        ("S25 Judge Shouts", cam_pos_from_polar((0.0, 4.8, 4.4), 7.9, 12, 5), (0.0, 4.8, 4.4), 28,
         [("Judge", JUDGE_LOC, False)], []),
        ("S26 Judge Vanish", cam_pos_from_polar((0.0, 5.0, 4.4), 7.5, -8, 4), (0.0, 5.0, 4.4), 28,
         [("Judge", JUDGE_LOC, False)], []),
        ("S27 Bailiff Pop", cam_pos_from_polar((5.2, 3.2, 3.3), 7.2, -6, 5), (5.2, 3.2, 3.3), 28,
         [("Bailiff", BAILIFF_LOC, False)], [("Reporter", REPORTER_LOC, True)]),
        ("S28 Reporter Pop", cam_pos_from_polar((-3.6, 4.6, 3.1), 7.0, 6, 6), (-3.6, 4.6, 3.1), 28,
         [("Reporter", REPORTER_LOC, True)], []),
    ]

    fails = 0
    print(f"{'SHOT':22s} {'FOCAL':10s} {'HEAD_Y (top..bot)':18s} {'HEAD_X (L..R)':16s} {'H_SHARE':8s} {'OCCL':6s} {'STATUS'}")
    print("-" * 92)
    for sname, cpos, ctgt, lens, focals, extras in tests:
        for fname, floc, fseat in focals:
            fb = project_char_bbox(floc, cpos, ctgt, lens, seated=fseat)
            if not fb:
                print(f"{sname:22s} {fname:10s} BEHIND CAMERA -> FAIL")
                fails += 1
                continue
            occl_by = []
            for ename, eloc, eseat in extras:
                eb = project_char_bbox(eloc, cpos, ctgt, lens, seated=eseat)
                if not eb or eb["depth"] >= fb["depth"] - 0.3:
                    continue
                # Check if foreground extra overlaps focal character's head OR torso box
                ox = max(0.0, min(fb["body_x1"], eb["body_x1"]) - max(fb["body_x0"], eb["body_x0"]))
                oy = max(0.0, min(fb["body_y1"], eb["body_y1"]) - max(fb["body_y0"], eb["body_y0"]))
                if ox * oy > 0.008:
                    occl_by.append(ename)
            issues = []
            if fb["head_y0"] < 0.04:
                issues.append(f"HEAD_CUT_TOP({fb['head_y0']:.2f})")
            if fb["head_y1"] > 0.68:
                issues.append(f"IN_CAPTION_BAND({fb['head_y1']:.2f})")
            if fb["head_x0"] < 0.04 or fb["head_x1"] > 0.96:
                issues.append(f"HEAD_EDGE_X({fb['head_x0']:.2f}..{fb['head_x1']:.2f})")
            if fb["height_share"] > 0.72:
                issues.append(f"TOO_BIG({fb['height_share']*100:.0f}%)")
            if occl_by:
                issues.append(f"BLOCKED_BY({','.join(occl_by)})")
            status = "PASS" if not issues else "FAIL: " + " ".join(issues)
            if issues:
                fails += 1
            print(f"{sname:22s} {fname:10s} {fb['head_y0']*100:5.1f}%..{fb['head_y1']*100:5.1f}%     "
                  f"{fb['head_x0']*100:5.1f}%..{fb['head_x1']*100:5.1f}%   {fb['height_share']*100:5.1f}%   "
                  f"{len(occl_by):2d}     {status}")

    # Check mouth-flap rule in shots.py
    shots_path = os.path.join(os.path.dirname(__file__), "..", "..", "projects", "Video-2", "shots.py")
    txt = open(shots_path, encoding="utf-8").read()
    blocks = re.split(r"@S\(\s*(\d+)\s*,", txt)[1:]
    quoted_shots = {11, 16, 19, 20, 22, 25, 27, 28, 30}
    flap_Violations = []
    for i in range(0, len(blocks), 2):
        sid = int(blocks[i])
        body = blocks[i + 1]
        if "lips(" in body and sid not in quoted_shots:
            flap_Violations.append(sid)
    print("-" * 92)
    print(f"MOUTH-FLAP RULE (style-toon.md §4 Rule 5): lips() in non-dialogue shots = {flap_Violations} -> "
          f"{'PASS' if not flap_Violations else 'FAIL'}")
    if flap_Violations:
        fails += len(flap_Violations)
    print(f"\nTOTAL AUDIT RESULT: {fails} FAIL(s)")
    return fails


if __name__ == "__main__":
    sys.exit(1 if audit_video2() > 0 else 0)
