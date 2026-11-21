# Roblox classic clothing templates (585x559) for the Monster Test cast. One shirt + one pants per look, colours baked in.
from PIL import Image, ImageDraw, ImageFilter
import random
import numpy as np
import json, colorsys
W, H = 585, 559
TORSO = dict(F=(231, 74, 128, 128), B=(427, 74, 128, 128), R=(165, 74, 64, 128), L=(361, 74, 64, 128), U=(231, 8, 128, 64), D=(231, 204, 128, 64))
RLIMB = dict(L=(19, 355, 64, 128), B=(85, 355, 64, 128), R=(151, 355, 64, 128), F=(217, 355, 64, 128), U=(217, 289, 64, 64), D=(217, 485, 64, 64))
LLIMB = dict(F=(308, 355, 64, 128), L=(374, 355, 64, 128), B=(440, 355, 64, 128), R=(506, 355, 64, 128), U=(308, 289, 64, 64), D=(308, 485, 64, 64))
def hx(h): h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
def shade(c, f):
    r, g, b = [x / 255 for x in c]; h, l, s = colorsys.rgb_to_hls(r, g, b)
    l = max(0, min(1, l * f if f < 1 else l + (1 - l) * (f - 1)))
    return tuple(int(x * 255) for x in colorsys.hls_to_rgb(h, l, s)) + (255,)
def fillgrad(d, box, c, top=1.06, bot=0.9, side=True):
    x, y, w, h = box
    for j in range(h):
        f = top + (bot - top) * j / max(1, h - 1)
        d.line([(x, y + j), (x + w - 1, y + j)], fill=shade(c, f))
    if side:
        for i in range(4):
            a = 0.93 + i * 0.015
            d.line([(x + i, y), (x + i, y + h - 1)], fill=shade(c, a * (top + bot) / 2))
            d.line([(x + w - 1 - i, y), (x + w - 1 - i, y + h - 1)], fill=shade(c, a * (top + bot) / 2))
def hem(d, box, c, y0, th=5):
    x, y, w, h = box; d.rectangle([x, y + y0, x + w - 1, y + y0 + th], fill=shade(c, 0.82))
def shirt(col, style, accent="#FFFFFF"):
    c = hx(col); a = hx(accent)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for k, b in TORSO.items(): fillgrad(d, b, c, side=k in "FBLR")
    hem(d, TORSO["F"], c, 118, 9); hem(d, TORSO["B"], c, 118, 9); hem(d, TORSO["L"], c, 118, 9); hem(d, TORSO["R"], c, 118, 9)
    long = style in ("hoodie", "collar", "cardigan", "suit", "blouse")
    for limb in (RLIMB, LLIMB):
        for k, (x, y, w, h) in limb.items():
            if k == "D":
                if long: fillgrad(d, (x, y, w, h), c, 0.85, 0.85, False)
                continue
            if k == "U": fillgrad(d, (x, y, w, h), c, 1.08, 1.0, False); continue
            hh = h if long else 46
            fillgrad(d, (x, y, w, hh), c, 1.04, 0.9)
            if long: d.rectangle([x, y + h - 14, x + w - 1, y + h - 1], fill=shade(c, 0.8))  # cuff
            else: d.rectangle([x, y + hh - 6, x + w - 1, y + hh - 1], fill=shade(c, 0.8))  # sleeve hem
    fx, fy, fw, fh = TORSO["F"]; bx, by, bw, bh = TORSO["B"]
    if style == "tee":
        d.chord([fx + 40, fy - 22, fx + 88, fy + 22], 0, 180, fill=shade(c, 0.72)); d.chord([fx + 45, fy - 16, fx + 83, fy + 15], 0, 180, fill=shade(c, 1.0))
    if style == "tee_heart":
        d.chord([fx + 40, fy - 22, fx + 88, fy + 22], 0, 180, fill=shade(c, 0.72)); d.chord([fx + 45, fy - 16, fx + 83, fy + 15], 0, 180, fill=shade(c, 1.0))
        cx, cy = fx + 64, fy + 64
        d.ellipse([cx - 22, cy - 18, cx + 2, cy + 6], fill=a + (255,)); d.ellipse([cx - 2, cy - 18, cx + 22, cy + 6], fill=a + (255,))
        d.polygon([(cx - 21, cy - 2), (cx + 21, cy - 2), (cx, cy + 24)], fill=a + (255,))
    if style == "tee_stripe":
        d.chord([fx + 40, fy - 22, fx + 88, fy + 22], 0, 180, fill=shade(c, 0.72))
        for b in ("F", "B", "L", "R"):
            x, y, w, h = TORSO[b]; d.rectangle([x, y + 50, x + w - 1, y + 66], fill=a + (255,))
    if style == "hoodie":
        d.rectangle([fx + 30, fy + 74, fx + 98, fy + 112], fill=shade(c, 0.9)); d.line([(fx + 30, fy + 74), (fx + 98, fy + 74)], fill=shade(c, 0.7), width=3)
        d.line([(fx + 30, fy + 74), (fx + 22, fy + 112)], fill=shade(c, 0.7), width=3); d.line([(fx + 98, fy + 74), (fx + 106, fy + 112)], fill=shade(c, 0.7), width=3)
        d.chord([fx + 30, fy - 30, fx + 98, fy + 30], 0, 180, fill=shade(c, 0.78))
        for sx in (52, 76): d.line([(fx + sx, fy + 26), (fx + sx, fy + 58)], fill=(245, 245, 240, 255), width=4); d.ellipse([fx + sx - 4, fy + 56, fx + sx + 4, fy + 64], fill=(245, 245, 240, 255))
        d.chord([bx + 18, by - 20, bx + 110, by + 70], 0, 180, fill=shade(c, 0.86)); d.arc([bx + 18, by - 20, bx + 110, by + 70], 0, 180, fill=shade(c, 0.68), width=4)
    if style == "collar":
        d.polygon([(fx + 44, fy), (fx + 64, fy + 26), (fx + 84, fy)], fill=shade(c, 0.6))
        d.polygon([(fx + 34, fy), (fx + 58, fy + 30), (fx + 64, fy + 14)], fill=shade(c, 1.12)); d.polygon([(fx + 94, fy), (fx + 70, fy + 30), (fx + 64, fy + 14)], fill=shade(c, 1.12))
        d.line([(fx + 64, fy + 26), (fx + 64, fy + 118)], fill=shade(c, 0.78), width=3)
        for yy in range(40, 118, 22): d.ellipse([fx + 69, fy + yy, fx + 75, fy + yy + 6], fill=(240, 240, 235, 255))
        d.rectangle([fx + 18, fy + 30, fx + 40, fy + 50], outline=shade(c, 0.75), width=2)
    if style == "blouse" or style == "cardigan":
        if style == "cardigan":
            d.rectangle([fx + 50, fy, fx + 78, fy + 128], fill=a + (255,)); d.line([(fx + 50, fy), (fx + 50, fy + 128)], fill=shade(c, 0.7), width=3); d.line([(fx + 78, fy), (fx + 78, fy + 128)], fill=shade(c, 0.7), width=3)
            for yy in range(30, 118, 24): d.ellipse([fx + 82, fy + yy, fx + 88, fy + yy + 6], fill=shade(c, 0.6))
        else:
            d.polygon([(fx + 44, fy), (fx + 64, fy + 34), (fx + 84, fy)], fill=shade(c, 0.66)); d.polygon([(fx + 49, fy), (fx + 64, fy + 26), (fx + 79, fy)], fill=(234, 188, 150, 255))
            d.line([(fx + 6, fy + 86), (fx + 122, fy + 86)], fill=shade(c, 0.8), width=4)
    if style == "suit":
        d.polygon([(fx + 40, fy), (fx + 64, fy + 70), (fx + 88, fy)], fill=(244, 244, 240, 255))
        d.polygon([(fx + 60, fy + 8), (fx + 68, fy + 8), (fx + 70, fy + 56), (fx + 64, fy + 66), (fx + 58, fy + 56)], fill=a + (255,))
        d.polygon([(fx + 40, fy), (fx + 30, fy + 20), (fx + 60, fy + 76)], fill=shade(c, 0.75)); d.polygon([(fx + 88, fy), (fx + 98, fy + 20), (fx + 68, fy + 76)], fill=shade(c, 0.75))
        for yy in (84, 104): d.ellipse([fx + 60, fy + yy, fx + 68, fy + yy + 8], fill=(30, 30, 34, 255))
        d.rectangle([fx + 92, fy + 30, fx + 112, fy + 36], fill=(240, 240, 235, 255))
    return im.filter(ImageFilter.SMOOTH)
def pants(col, shoe, style="jeans"):
    c = hx(col); s = hx(shoe)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for k in ("F", "B", "L", "R"):
        x, y, w, h = TORSO[k]; fillgrad(d, (x, y + 98, w, 30), c, 1.0, 0.92, False)
        d.rectangle([x, y + 98, x + w - 1, y + 106], fill=shade(c, 0.72))
    x, y, w, h = TORSO["F"]; d.rectangle([x + 56, y + 98, x + 72, y + 107], fill=(200, 170, 90, 255))
    fillgrad(d, TORSO["D"], c, 0.9, 0.9, False)
    for limb, inner in ((RLIMB, "L"), (LLIMB, "R")):
        for k, (x, y, w, h) in limb.items():
            if k == "U": fillgrad(d, (x, y, w, h), c, 1.0, 1.0, False); continue
            if k == "D": d.rectangle([x, y, x + w - 1, y + h - 1], fill=shade(s, 0.7)); continue
            fillgrad(d, (x, y, w, h - 24), c, 1.02, 0.86)
            if style == "jeans": d.line([(x + w // 2, y + 4), (x + w // 2, y + h - 30)], fill=shade(c, 0.78), width=2) if k in "LR" else None
            d.rectangle([x, y + h - 30, x + w - 1, y + h - 25], fill=shade(c, 0.75))
            d.rectangle([x, y + h - 24, x + w - 1, y + h - 1], fill=shade(s, 1.0)); d.rectangle([x, y + h - 7, x + w - 1, y + h - 1], fill=shade(s, 0.78) if sum(s) < 600 else (205, 205, 200, 255))
            if k == "F": d.rectangle([x + 10, y + h - 21, x + w - 11, y + h - 15], fill=shade(s, 1.12) if sum(s) < 600 else (230, 230, 226, 255))
    return im.filter(ImageFilter.SMOOTH)

def fabric(im, seed=1, strength=1.0):
    """Folds and cloth grain: blurred dark/light strokes per face region, multiplied into the colours."""
    rnd = random.Random(seed)
    m = Image.new("L", (W, H), 128); d = ImageDraw.Draw(m)
    regions = list(TORSO.values()) + list(RLIMB.values()) + list(LLIMB.values())
    for (x, y, w, h) in regions:
        if h < 100: continue
        for _ in range(5 if w > 100 else 3):   # long soft folds, mostly vertical and slightly diagonal
            x0 = x + rnd.uniform(0.1, 0.9) * w; dx = rnd.uniform(-0.25, 0.25) * w
            d.line([(x0, y + rnd.uniform(0, 0.3) * h), (x0 + dx, y + rnd.uniform(0.7, 1.0) * h)], fill=rnd.choice([92, 100, 150]), width=rnd.randint(3, 7))
        for _ in range(3):                      # small creases near the bottom/elbow line
            yy = y + rnd.uniform(0.55, 0.95) * h
            d.line([(x + rnd.uniform(0, 0.4) * w, yy), (x + rnd.uniform(0.6, 1) * w, yy + rnd.uniform(-6, 6))], fill=104, width=3)
    m = m.filter(ImageFilter.GaussianBlur(4))
    a = np.asarray(m).astype(np.float32) / 128.0
    a = 1 + (a - 1) * 0.55 * strength
    noise = np.random.default_rng(seed).normal(1.0, 0.018, (H, W)).astype(np.float32)
    arr = np.asarray(im).astype(np.float32)
    arr[..., :3] = np.clip(arr[..., :3] * (a * noise)[..., None], 0, 255)
    return Image.fromarray(arr.astype(np.uint8), "RGBA")
P = dict(butter="#F7D96B", teal="#3FB8AF", lilac="#C9B6E4", navy="#3A4E8C", pink="#F4A6B8", mint="#9ED9B6", coral="#F28B6E", sky="#8FC9F0", white="#F2F2EE", wood="#C99A6B", deep_teal="#2E7D7A")
P = dict(butter="#F5D66E", teal="#45B5AA", lilac="#B7A3E6", navy="#2F3E63", pink="#F6A6C1", mint="#A8E0C0", coral="#EE6F5E", sky="#8FC9F0", white="#FAFAF7", wood="#B98A5E", deep_teal="#2C7A78", charcoal="#3A3F4A")
SH = {"me": ("hoodie", P["butter"], "#FFFFFF"), "diddy": ("tee_stripe", P["teal"], "#FAFAF7"), "mom": ("blouse", P["lilac"], "#FFFFFF"),
      "dad": ("collar", P["navy"], "#FFFFFF"), "may": ("tee_heart", P["pink"], "#EE6F5E"), "mayor": ("suit", P["charcoal"], "#D94848"),
      "teacher": ("cardigan", P["mint"], "#FAFAF7")}
CROWD = [P["coral"], P["sky"], P["mint"], P["pink"], P["white"], P["wood"], P["deep_teal"], "#E88FB0", "#8FC1E8", "#F2B66B"]
CSTY = ["tee", "hoodie", "collar", "tee_stripe"]
for i, col in enumerate(CROWD): SH["c%d" % (i + 1)] = (CSTY[i % 4], col, "#FAFAF7")
PA = {"me": ("#3D4A6B", "#F4F4F0"), "diddy": ("#2E3138", "#F4F4F0"), "mom": ("#5A4A7A", "#FAFAF7"), "dad": ("#2B2B33", "#1A1A1E"),
      "may": ("#8FB3E0", "#EE6F5E"), "mayor": ("#3A3F4A", "#1A1A1E"), "teacher": ("#6B5B4A", "#4A3020")}
for i, col in enumerate(["#3D4A6B", "#2E3138", "#6B5B4A", "#5A4A7A", "#4A5A4A"]): PA["p%d" % (i + 1)] = (col, "#F4F4F0")
for i, (k, v) in enumerate(SH.items()): fabric(shirt(v[1], v[0], v[2]), seed=i + 1).save(f"shirt_{k}.png")
for i, (k, v) in enumerate(PA.items()): fabric(pants(*v), seed=100 + i, strength=0.8).save(f"pants_{k}.png")
json.dump({"shirts": SH, "pants": PA}, open("looks.json", "w"), indent=1)
# preview sheet
prev = Image.new("RGBA", (W * 4, H * 2), (60, 60, 60, 255))
for n, k in enumerate(["me", "dad", "mayor", "may"]):
    prev.alpha_composite(Image.open(f"shirt_{k}.png"), (W * n, 0)); prev.alpha_composite(Image.open(f"pants_{k}.png"), (W * n, H))
prev.convert("RGB").resize((W * 2, H)).save("preview.jpg")
