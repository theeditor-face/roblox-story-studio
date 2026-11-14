import os, sys, time, importlib.util
import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import shotkit

vdir = os.path.join(shotkit.STUDIO, "videos", "active")
spec = importlib.util.spec_from_file_location("video_shots", os.path.join(vdir, "shots.py"))
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
V = mod.V

S = V.build(1, samples=8, pct=75)
sc = bpy.context.scene
sc.frame_start = 1
sc.frame_end = 2

for name, setup_fn in [
    ("EEVEE_NEXT_75pct_4taa", lambda: (
        setattr(sc.render, "engine", "BLENDER_EEVEE_NEXT"),
        setattr(sc.render, "resolution_percentage", 75),
        setattr(sc.eevee, "taa_render_samples", 4),
        setattr(sc.eevee, "use_raytracing", False),
    )),
    ("CYCLES_CPU_55pct_4smp_OIDN", lambda: (
        setattr(sc.render, "engine", "CYCLES"),
        setattr(sc.cycles, "device", "CPU"),
        setattr(sc.render, "resolution_percentage", 55),
        setattr(sc.cycles, "samples", 4),
        setattr(sc.cycles, "adaptive_threshold", 0.12),
        setattr(sc.cycles, "use_denoising", True),
        setattr(sc.cycles, "denoiser", "OPENIMAGEDENOISE"),
    )),
    ("CYCLES_CPU_55pct_4smp_NoDenoise", lambda: (
        setattr(sc.render, "engine", "CYCLES"),
        setattr(sc.cycles, "device", "CPU"),
        setattr(sc.render, "resolution_percentage", 55),
        setattr(sc.cycles, "samples", 4),
        setattr(sc.cycles, "adaptive_threshold", 0.12),
        setattr(sc.cycles, "use_denoising", False),
    )),
]:
    try:
        setup_fn()
        for f in (1, 2):
            t0 = time.time()
            sc.frame_set(f)
            sc.render.filepath = f"/tmp/bench_{name}_{f}.png"
            bpy.ops.render.render(write_still=True)
            print(f"BENCH {name} frame {f}: {time.time()-t0:.2f}s", flush=True)
    except Exception as e:
        print(f"BENCH {name} ERROR: {e}", flush=True)
