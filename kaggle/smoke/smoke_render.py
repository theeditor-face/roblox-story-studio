import os, shutil, subprocess, time

t_start = time.time()
print("=== 1. Checking GPU ===")
subprocess.run(["nvidia-smi"], check=False)

print("=== 2. Installing system libs & Blender 4.3.2 ===")
subprocess.run("apt-get update -qq && apt-get install -y -qq libx11-6 libxi6 libxfixes3 libxrender1 libxxf86vm1 libxkbcommon0 libsm6 libice6 libgl1 libegl1 > /dev/null 2>&1", shell=True, check=False)

bdir = "/tmp/blender"
if not os.path.exists(os.path.join(bdir, "blender")):
    os.makedirs(bdir, exist_ok=True)
    subprocess.run("curl -L -s https://download.blender.org/release/Blender4.3/blender-4.3.2-linux-x64.tar.xz -o /tmp/bl.tar.xz && tar -xf /tmp/bl.tar.xz --strip-components=1 -C /tmp/blender && rm -f /tmp/bl.tar.xz", shell=True, check=True)
subprocess.run([os.path.join(bdir, "blender"), "--version"], check=True)

print("=== 3. Cloning roblox-story-studio ===")
repo = "/tmp/roblox-story-studio"
if os.path.exists(repo):
    shutil.rmtree(repo)
subprocess.run(["git", "clone", "--depth", "1", "https://github.com/theeditor-face/roblox-story-studio.git", repo], check=True)

eng = os.path.join(repo, "engine")
vdir = os.path.join(eng, "videos", "active")
if os.path.exists(vdir):
    shutil.rmtree(vdir)
shutil.copytree(os.path.join(repo, "projects", "Video-1"), vdir)

print("=== 4. Rendering 1 test frame on Kaggle GPU (Cycles + OIDN) ===")
t_r = time.time()
subprocess.run([
    os.path.join(bdir, "blender"), "-b", "--factory-startup",
    "-P", "tools/render.py", "--", "active", "still:1.0", "1", "8"
], cwd=eng, check=True)
print(f"Render call took {time.time() - t_r:.2f}s")

for fn in os.listdir(os.path.join(vdir, "preview")):
    if fn.endswith(".png"):
        shutil.copy2(os.path.join(vdir, "preview", fn), "/kaggle/working/smoke_frame.png")
        print("Saved /kaggle/working/smoke_frame.png")
print(f"Total kernel time: {time.time() - t_start:.1f}s")
