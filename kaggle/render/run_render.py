import json
import os
import shutil
import subprocess
import sys
import time

t_start = time.time()
cfg = {"project": "Video-1", "samples": 16}
for cand in ("render_config.json", "/kaggle/src/render_config.json", "/kaggle/working/render_config.json"):
    if os.path.isfile(cand):
        with open(cand, encoding="utf-8") as f:
            cfg.update(json.load(f))
        break

PROJ = cfg.get("project", "Video-1")
SAMPLES = int(cfg.get("samples", 16))
print(f"=== Roblox 3D Kaggle Dual-T4 Render: project={PROJ}, samples={SAMPLES} ===", flush=True)

print("=== 1. Checking GPU ===")
subprocess.run(["nvidia-smi"], check=False)

print("=== 2. Installing system libs, FFmpeg & Blender 4.3.2 ===")
subprocess.run(
    "apt-get update -qq && apt-get install -y -qq ffmpeg libsndfile1 libx11-6 libxi6 libxfixes3 "
    "libxrender1 libxxf86vm1 libxkbcommon0 libsm6 libice6 libgl1 libegl1 > /dev/null 2>&1",
    shell=True,
    check=False,
)
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "numpy", "pillow"], check=False)

bdir = "/tmp/blender"
if not os.path.exists(os.path.join(bdir, "blender")):
    os.makedirs(bdir, exist_ok=True)
    subprocess.run(
        "curl -L -s https://download.blender.org/release/Blender4.3/blender-4.3.2-linux-x64.tar.xz -o /tmp/bl.tar.xz "
        "&& tar -xf /tmp/bl.tar.xz --strip-components=1 -C /tmp/blender && rm -f /tmp/bl.tar.xz",
        shell=True,
        check=True,
    )
subprocess.run([os.path.join(bdir, "blender"), "--version"], check=True)

print("=== 3. Cloning roblox-story-studio ===")
repo = "/tmp/roblox-story-studio"
if os.path.exists(repo):
    shutil.rmtree(repo)
subprocess.run(["git", "clone", "--depth", "1", "https://github.com/theeditor-face/roblox-story-studio.git", repo], check=True)

eng = os.path.join(repo, "engine")
pdir = os.path.join(repo, "projects", PROJ)
if not os.path.isdir(pdir):
    raise SystemExit(f"Project not found: {pdir}")

vdir = os.path.join(eng, "videos", "active")
if os.path.exists(vdir):
    shutil.rmtree(vdir)
shutil.copytree(pdir, vdir)

proj_tex = os.path.join(vdir, "tex")
if os.path.isdir(proj_tex):
    for fn in os.listdir(proj_tex):
        if fn.lower().endswith(".png"):
            shutil.copy2(os.path.join(proj_tex, fn), os.path.join(eng, "assets", "tex", fn))

print(f"=== 4. Rendering all shots (Cycles Dual-T4 GPU + OptiX, samples={SAMPLES}, 1080x1920) ===", flush=True)
os.chdir(eng)
t_render = time.time()
subprocess.run(
    [
        os.path.join(bdir, "blender"),
        "-b",
        "--factory-startup",
        "-P",
        os.path.join(eng, "tools", "render.py"),
        "--",
        "active",
        "final",
        "all",
        str(SAMPLES),
    ],
    cwd=eng,
    check=True,
)
render_elapsed = time.time() - t_render
frames_dir = os.path.join(vdir, "frames")
n_frames = len([f for f in os.listdir(frames_dir) if f.endswith(".png")])
print(f"=== Render complete: {n_frames} frames in {render_elapsed / 60:.1f} min ===", flush=True)

print("=== 5. Mixing voice + 44 SFX + music & burning captions -> final.mp4 ===", flush=True)
subprocess.run([sys.executable, os.path.join(eng, "tools", "finish.py"), "active"], cwd=eng, check=True)

out_mp4 = os.path.join(vdir, "out", "final.mp4")
qa_sheet = os.path.join(vdir, "out", "qa_contact_sheet.jpg")
subprocess.run(
    [
        "ffmpeg",
        "-y",
        "-v",
        "error",
        "-i",
        out_mp4,
        "-vf",
        "fps=1/2,scale=216:384,tile=9x6",
        "-frames:v",
        "1",
        qa_sheet,
    ],
    check=False,
)

os.chdir("/kaggle/working")
shutil.copy2(out_mp4, "/kaggle/working/final.mp4")
if os.path.isfile(qa_sheet):
    shutil.copy2(qa_sheet, "/kaggle/working/qa_contact_sheet.jpg")
log_src = os.path.join(vdir, "render_log_final.txt")
if os.path.isfile(log_src):
    shutil.copy2(log_src, "/kaggle/working/render_log_final.txt")

mp4_mb = os.path.getsize("/kaggle/working/final.mp4") / (1024 * 1024)
print(f"Saved /kaggle/working/final.mp4 ({mp4_mb:.1f} MB). Total Kaggle time: {(time.time() - t_start) / 60:.1f} min", flush=True)
