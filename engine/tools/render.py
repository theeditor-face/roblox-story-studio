"""Headless shot renderer for a studio video.
blender -b --factory-startup -P tools/render.py -- <slug> <mode> [ids] [samples]
  mode: preview  middle frame of each shot, 25% res  -> videos/<slug>/preview/shot_XX.png
        still:T   one frame at time T, 50% res       -> videos/<slug>/preview/still_XX_T.png
        final     every frame, full res              -> videos/<slug>/frames/####.png (+ blend/shot_XX.blend)
        cues      build every shot, collect sfx() cues -> videos/<slug>/audio/cues.json (no rendering)
  ids : "all" (default), "1-20", "3,5,9-12"."""
import importlib.util, json, os, sys, time, traceback
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import shotkit
from rbx.core import F, CUES

argv = sys.argv[sys.argv.index("--") + 1:]
slug, mode = argv[0], argv[1]
sel = argv[2] if len(argv) > 2 else "all"
samples = int(argv[3]) if len(argv) > 3 else None
vdir = os.path.join(shotkit.STUDIO, "videos", slug)
spec = importlib.util.spec_from_file_location("video_shots", os.path.join(vdir, "shots.py"))
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
V = mod.V
ids = sorted(V.shots)
if sel != "all":
    ids = []
    for part in sel.split(","):
        if "-" in part:
            a, b = part.split("-"); ids += [i for i in range(int(a), int(b) + 1) if i in V.shots]
        else:
            ids.append(int(part))
for d in ("preview", "frames", "blend", "audio"):
    os.makedirs(os.path.join(vdir, d), exist_ok=True)
log = open(os.path.join(vdir, f"render_log_{mode.split(':')[0]}.txt"), "a", encoding="utf-8")


def say(*a):
    m = " ".join(str(x) for x in a); print(m, flush=True); log.write(m + "\n"); log.flush()


probs = V.check()
for p in probs:
    say("TIMELINE:", p)
all_cues = []
for i in ids:
    t0 = time.time()
    try:
        if mode == "preview":
            S = V.build(i, samples=samples or 8, pct=25)
            sc = bpy.context.scene; sc.render.use_motion_blur = False
            f0, f1 = F(S["t0"]), F(S["t1"]) - 1
            # Sample at 12% into the shot so characters that vanish mid-shot are still visible in the preview contact sheet
            sc.frame_set(min(f1, f0 + max(1, (f1 - f0) // 8)))
            sc.render.filepath = os.path.join(vdir, "preview", f"shot_{i:02d}.png")
            bpy.ops.render.render(write_still=True)
        elif mode.startswith("still"):
            t = float(mode.split(":")[1])
            S = V.build(i, samples=samples or 16, pct=50)
            sc = bpy.context.scene; sc.frame_set(F(t))
            sc.render.filepath = os.path.join(vdir, "preview", f"still_{i:02d}_{t:.2f}.png")
            bpy.ops.render.render(write_still=True)
        elif mode == "final":
            S = V.build(i, samples=samples or 24, pct=100)
            all_cues += [dict(c, shot=i) for c in CUES]
            sc = bpy.context.scene
            sc.render.filepath = os.path.join(vdir, "frames", "")
            try:
                bpy.ops.render.render(animation=True)
            except RuntimeError as e:
                if "denois" not in str(e).lower():
                    raise
                say(f"shot {i:02d}: denoiser failed ({e}) -> retrying with CPU denoise")
                try:
                    sc.cycles.denoiser = "OPENIMAGEDENOISE"; sc.cycles.denoising_use_gpu = False
                    bpy.ops.render.render(animation=True)
                except RuntimeError:
                    say(f"shot {i:02d}: retrying with denoising OFF")
                    sc.cycles.use_denoising = False
                    bpy.ops.render.render(animation=True)
        elif mode == "cues":
            S = V.build(i, samples=1, pct=10)
            all_cues += [dict(c, shot=i) for c in CUES]
        say(f"shot {i:02d} ok {time.time() - t0:.1f}s")
    except Exception:
        say(f"shot {i:02d} FAILED\n" + traceback.format_exc())
if mode in ("cues", "final"):
    all_cues.sort(key=lambda c: c["t"])
    cues_file = "cues.json" if sel == "all" else f"cues_part_{sel.replace(',', '_')}.json"
    json.dump(all_cues, open(os.path.join(vdir, "audio", cues_file), "w"), indent=1)
    say(f"cues: {len(all_cues)} -> audio/{cues_file}")
log.close()
