"""Colour & exposure QA checker for rendered stills or contact sheets (zero OpenCV dependency).
Ported from roblox-v3/tools/measure.py & blocky-shorts/scripts/measure.py using Pillow + NumPy.
Checks brightness (HSV V), saturation (HSV S), contrast, warmth, p1, p99, and highlight clipping (clip%).
"""
import glob
import os
import sys
import numpy as np
from PIL import Image


def measure_image(path):
    im = Image.open(path).convert("RGB")
    arr = np.asarray(im, dtype=np.float32) / 255.0
    h = arr.shape[0]
    arr = arr[int(h * 0.08):int(h * 0.92)]
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    v = np.maximum(np.maximum(r, g), b)
    cmin = np.minimum(np.minimum(r, g), b)
    delta = v - cmin
    s = np.where(v > 1e-5, delta / np.maximum(v, 1e-5), 0.0)
    gray = (0.299 * r + 0.587 * g + 0.114 * b) * 255.0
    warm = float((r - b).mean())
    return {
        "name": os.path.basename(path),
        "bright": float(v.mean()),
        "sat": float(s.mean()),
        "contrast": float(gray.std() / 255.0),
        "warm": warm,
        "p1": float(np.percentile(gray, 1)),
        "p99": float(np.percentile(gray, 99)),
        "clip": float((gray >= 250.0).mean() * 100.0),
        "crush": float((gray <= 12.0).mean() * 100.0),
    }


if __name__ == "__main__":
    files = sorted(f for arg in sys.argv[1:] for f in (glob.glob(arg) or ([arg] if os.path.isfile(arg) else [])))
    if not files:
        sys.exit("Usage: python measure_stills.py <image1.png/jpg> ...")
    print(f"{'FILE':36s} {'BRIGHT':7s} {'SAT':7s} {'CONTR':7s} {'WARM':7s} {'P1':5s} {'P99':5s} {'CLIP%':6s} {'CRUSH%':6s}")
    print("-" * 96)
    for f in files:
        m = measure_image(f)
        print(f"{m['name'][:36]:36s} {m['bright']:7.3f} {m['sat']:7.3f} {m['contrast']:7.3f} "
              f"{m['warm']:+7.3f} {m['p1']:5.0f} {m['p99']:5.0f} {m['clip']:6.1f} {m['crush']:6.1f}")
