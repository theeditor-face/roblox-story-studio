"""Settings and machine lookups shared by the studio tools (plain python, not Blender).

config.json next to rbx/ overrides any key in DEFAULTS. Nothing here is required: with no
config.json every tool behaves as before (auto-detects Blender, fonts, whisper)."""
import glob, json, os, platform, re, shutil, subprocess, sys

STUDIO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYSTEM = platform.system()  # Windows / Darwin / Linux

DEFAULTS = {
    "blender": "",                        # Blender executable; empty = auto-detect
    "flashloop_voice_id": "",             # the narrator cloned into this user's Flashloop account (set on first use)
    "flashloop_voice_model": "",          # empty = Flashloop's v4 voiceover model (see SKILL.md step 3)
    "fallback_voice_id": "AaOhDHYJ1XLZk74lXhdE",  # Flashloop built-in "Caleb", used only if the clone is unavailable
    "image_model": "nano-banana-2",       # Flashloop model for character sheets, textures and covers
    "whisper_python": "",                 # a python that has faster-whisper; empty = the python running the tool
    "whisper_model": "base.en",           # fast 140MB model (aligns to script.txt in ~5s instead of 400s)
    "music_url": "https://www.youtube.com/watch?v=ecvbCDTcAco",  # TEMPOREX - Numbers
    "music_speed": 1.5,
    "music_mode": "tempo",                # tempo = same pitch, speed = pitched up
    "caption_font": "",                   # empty = Segoe UI Black on Windows, Arial Black elsewhere
}


def cfg():
    c = dict(DEFAULTS)
    p = os.path.join(STUDIO, "config.json")
    if os.path.exists(p):
        c.update(json.load(open(p, encoding="utf-8")))
    return c


def save_cfg(c):
    json.dump(c, open(os.path.join(STUDIO, "config.json"), "w", encoding="utf-8"), indent=2)


def caption_font(c=None):
    c = c or cfg()
    return c.get("caption_font") or ("Segoe UI Black" if SYSTEM == "Windows" else "Arial Black")


# ---- Blender ---------------------------------------------------------------------------
def _ver_key(path):
    m = re.search(r"(\d+)\.(\d+)", path)
    return (int(m.group(1)), int(m.group(2))) if m else (0, 0)


def blender_candidates():
    out = []
    if os.environ.get("BLENDER"):
        out.append(os.environ["BLENDER"])
    w = shutil.which("blender")
    if w:
        out.append(w)
    if SYSTEM == "Windows":
        roots = [os.environ.get("ProgramFiles", r"C:\Program Files"), os.environ.get("ProgramFiles(x86)", ""),
                 os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs")]
        found = []
        for r in roots:
            if r:
                found += glob.glob(os.path.join(r, "Blender Foundation", "Blender*", "blender.exe"))
        found += glob.glob(r"C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe")
        out += sorted(found, key=_ver_key, reverse=True)
    elif SYSTEM == "Darwin":
        out += sorted(glob.glob("/Applications/Blender*.app/Contents/MacOS/Blender")
                      + glob.glob(os.path.expanduser("~/Applications/Blender*.app/Contents/MacOS/Blender")),
                      key=_ver_key, reverse=True)
    else:
        out += sorted(glob.glob(os.path.expanduser("~/blender*/blender")) + glob.glob("/opt/blender*/blender")
                      + ["/snap/bin/blender", "/usr/bin/blender"], key=_ver_key, reverse=True)
    seen, res = set(), []
    for p in out:
        if p and p not in seen and os.path.isfile(p):
            seen.add(p); res.append(p)
    return res


def find_blender(c=None):
    c = c or cfg()
    if c.get("blender") and os.path.isfile(c["blender"]):
        return c["blender"]
    cands = blender_candidates()
    return cands[0] if cands else None


def blender_version(path):
    try:
        r = subprocess.run([path, "-b", "--factory-startup", "--version"], capture_output=True, text=True, timeout=120)
        m = re.search(r"Blender\s+(\d+)\.(\d+)(?:\.(\d+))?", r.stdout)
        return tuple(int(x or 0) for x in m.groups()) if m else None
    except Exception:
        return None


# ---- fonts (for Pillow textures and contact sheets) -------------------------------------
_ROLE = {"ariblk.ttf": "black", "arialbd.ttf": "bold", "arial.ttf": "regular", "segoeprb.ttf": "hand",
         "segoepr.ttf": "hand", "inkfree.ttf": "hand", "impact.ttf": "black"}
_CHAIN = {
    "black": ["ariblk.ttf", "Arial Black.ttf", "Impact.ttf", "impact.ttf", "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"],
    "bold": ["arialbd.ttf", "Arial Bold.ttf", "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"],
    "regular": ["arial.ttf", "Arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"],
    "hand": ["segoeprb.ttf", "segoepr.ttf", "Inkfree.ttf", "Chalkduster.ttf", "Bradley Hand Bold.ttf",
             "Comic Sans MS Bold.ttf", "comicbd.ttf", "DejaVuSans-Bold.ttf"],
}
_index = None


def _font_index():
    global _index
    if _index is None:
        dirs = []
        if SYSTEM == "Windows":
            dirs = [os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts"),
                    os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "Windows", "Fonts")]
        elif SYSTEM == "Darwin":
            dirs = ["/System/Library/Fonts/Supplemental", "/System/Library/Fonts", "/Library/Fonts",
                    os.path.expanduser("~/Library/Fonts")]
        else:
            dirs = ["/usr/share/fonts", "/usr/local/share/fonts", os.path.expanduser("~/.local/share/fonts"),
                    os.path.expanduser("~/.fonts")]
        dirs.insert(0, os.path.join(STUDIO, "assets", "fonts"))
        _index = {}
        for d in dirs:
            if os.path.isdir(d):
                for root, _, files in os.walk(d):
                    for f in files:
                        _index.setdefault(f.lower(), os.path.join(root, f))
    return _index


def font_path(name):
    idx = _font_index()
    for n in [name] + _CHAIN.get(_ROLE.get(name.lower(), "bold"), []):
        if n.lower() in idx:
            return idx[n.lower()]
    return None


def font(name, size):
    from PIL import ImageFont
    p = font_path(name)
    if p:
        return ImageFont.truetype(p, size)
    try:
        return ImageFont.load_default(size)
    except TypeError:
        return ImageFont.load_default()


if __name__ == "__main__":
    # python tools/kit.py get <key>  |  python tools/kit.py set <key> <value>  |  python tools/kit.py show
    a = sys.argv[1:]
    c = cfg()
    if a[:1] == ["set"] and len(a) == 3:
        v = a[2]
        try:
            v = json.loads(v)
        except ValueError:
            pass
        p = os.path.join(STUDIO, "config.json")
        cur = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
        cur[a[1]] = v
        save_cfg(cur)
        print(f"{a[1]} = {v}")
    elif a[:1] == ["get"] and len(a) == 2:
        print(c.get(a[1], ""))
    else:
        print(json.dumps(c, indent=2))
