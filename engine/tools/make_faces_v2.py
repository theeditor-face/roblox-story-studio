# Bold "Roblox story" face set: thick ink outlines, big white eyes, expressive brows and mouths, tears/sweat/blush.
# 24 faces, 1024x1024 RGBA each (drawn at 4x, downscaled), plus an atlas preview.
from PIL import Image, ImageDraw
import math, os
S = 4; N = 1024 * S
INK = (22, 18, 24, 255); WHITE = (255, 255, 255, 255); MOUTH = (92, 22, 34, 255); TONGUE = (238, 110, 128, 255)
TEAR = (150, 214, 255, 255); TEAR_D = (40, 92, 160, 255); BLUSH = (255, 120, 140, 120); RED = (226, 64, 70, 255)
LW = 17  # base line width (1024 space)
def P(x, y): return (x * S, y * S)
def new(): return Image.new("RGBA", (N, N), (0, 0, 0, 0))
def line(d, pts, w=LW, col=INK):
    pts = [P(*p) for p in pts]; ww = int(w * S)
    d.line(pts, fill=col, width=ww, joint="curve")
    for p in (pts[0], pts[-1]): d.ellipse([p[0] - ww / 2, p[1] - ww / 2, p[0] + ww / 2, p[1] + ww / 2], fill=col)
def bez(p0, p1, p2, n=40):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in [i / n for i in range(n + 1)]]
def ell(d, cx, cy, rx, ry, fill, outline=INK, w=LW):
    d.ellipse([P(cx - rx, cy - ry), P(cx + rx, cy + ry)], fill=fill, outline=outline, width=int(w * S) if outline else 0)
def poly(d, pts, fill, outline=INK, w=LW):
    d.polygon([P(*p) for p in pts], fill=fill)
    if outline: line(d, pts + [pts[0]], w, outline)
def eye(d, cx, cy, rx=78, ry=92, look=(0, 0), pr=0.5, lid=0.0, lid_tilt=0, glint=True, pupil_col=INK):
    # lid: fraction of the eye covered from the top (0..0.8); lid_tilt: + inner side lower (sad), - outer lower
    m = Image.new("L", (N, N), 0); md = ImageDraw.Draw(m)
    md.ellipse([P(cx - rx, cy - ry), P(cx + rx, cy + ry)], fill=255)
    if lid > 0:
        top = cy - ry + 2 * ry * lid
        md.polygon([P(cx - rx - 5, cy - ry - 5), P(cx + rx + 5, cy - ry - 5), P(cx + rx + 5, top - lid_tilt), P(cx - rx - 5, top + lid_tilt)], fill=0)
    layer = new(); ld = ImageDraw.Draw(layer)
    ld.ellipse([P(cx - rx, cy - ry), P(cx + rx, cy + ry)], fill=WHITE)
    px, py = cx + look[0] * rx * 0.45, cy + look[1] * ry * 0.4 + (ry * lid * 0.6 if lid else 0)
    r = rx * pr
    ld.ellipse([P(px - r, py - r * 1.12), P(px + r, py + r * 1.12)], fill=pupil_col)
    if glint: ld.ellipse([P(px - r * 0.55, py - r * 0.75), P(px - r * 0.05, py - r * 0.25)], fill=WHITE)
    clip = Image.new("RGBA", (N, N), (0, 0, 0, 0)); clip.paste(layer, (0, 0), m)
    d._image.alpha_composite(clip)
    # outline along the visible shape
    o = new(); od = ImageDraw.Draw(o)
    od.ellipse([P(cx - rx, cy - ry), P(cx + rx, cy + ry)], outline=INK, width=int(LW * S))
    mo = Image.new("L", (N, N), 0); ImageDraw.Draw(mo).ellipse([P(cx - rx - 20, cy - ry - 20), P(cx + rx + 20, cy + ry + 20)], fill=255)
    if lid > 0:
        top = cy - ry + 2 * ry * lid
        ImageDraw.Draw(mo).polygon([P(cx - rx - 25, cy - ry - 25), P(cx + rx + 25, cy - ry - 25), P(cx + rx + 25, top - lid_tilt - 2), P(cx - rx - 25, top + lid_tilt - 2)], fill=0)
    c2 = Image.new("RGBA", (N, N), (0, 0, 0, 0)); c2.paste(o, (0, 0), mo); d._image.alpha_composite(c2)
    if lid > 0:
        top = cy - ry + 2 * ry * lid
        # lid line across the eye
        hw = rx * math.sqrt(max(0, 1 - ((top - cy) / ry) ** 2)) + 4
        line(d, [(cx - hw, top + lid_tilt * (hw / (rx + 5))), (cx + hw, top - lid_tilt * (hw / (rx + 5)))], LW * 1.1)
def brow(d, cx, cy, ln=120, ang=0, w=22, bend=0):
    a = math.radians(ang); dx, dy = math.cos(a) * ln / 2, math.sin(a) * ln / 2
    p0, p2 = (cx - dx, cy - dy), (cx + dx, cy + dy)
    line(d, bez(p0, (cx, cy - bend), p2), w)
def closed_eye(d, cx, cy, w=130, up=True, h=40):
    line(d, bez((cx - w / 2, cy), (cx, cy + (-h if up else h) * 2), (cx + w / 2, cy)), LW * 1.3)
def mouth_open(d, cx, cy, w, h, teeth=True, tongue=True, shape="d"):
    if shape == "d":   # flat top, round bottom (laugh)
        pts = [(cx - w / 2 + (w / 2) * (1 - math.cos(t)) * 0 + w / 2 * -math.cos(t), cy + h * math.sin(t)) for t in [i * math.pi / 40 for i in range(41)]]
    else:              # ellipse
        pts = [(cx + w / 2 * math.cos(t), cy + h / 2 * math.sin(t)) for t in [i * 2 * math.pi / 60 for i in range(60)]]
    m = Image.new("L", (N, N), 0); ImageDraw.Draw(m).polygon([P(*p) for p in pts], fill=255)
    layer = new(); ld = ImageDraw.Draw(layer)
    ld.polygon([P(*p) for p in pts], fill=MOUTH)
    ys = [p[1] for p in pts]; top, bot = min(ys), max(ys)
    if teeth: ld.rectangle([P(cx - w, top - 5), P(cx + w, top + (bot - top) * 0.26)], fill=WHITE)
    if tongue: ld.ellipse([P(cx - w * 0.32, bot - (bot - top) * 0.42), P(cx + w * 0.32, bot + (bot - top) * 0.3)], fill=TONGUE)
    c = Image.new("RGBA", (N, N), (0, 0, 0, 0)); c.paste(layer, (0, 0), m); d._image.alpha_composite(c)
    line(d, pts + [pts[0]], LW)
def tear_stream(d, x, y0, y1=980, w=46):
    pts = [(x - w / 2, y0), (x + w / 2, y0), (x + w / 2 + 10, y1), (x - w / 2 - 10, y1)]
    poly(d, pts, TEAR, TEAR_D, 9)
def drop(d, x, y, s=1.0, _k=2.0, col=TEAR, oc=TEAR_D):
    s = s * _k
    r = 26 * s
    pts = [(x, y - 2.3 * r)] + [(x + r * math.cos(math.radians(a)), y + r * math.sin(math.radians(a))) for a in range(-55, 236, 10)]
    poly(d, pts, col, oc, 9)
    ell(d, x - 9 * s, y - 4 * s, 6 * s, 9 * s, (255, 255, 255, 230), None)
def blush(d, y=600, x=200, rx=78, ry=34):
    for sx in (512 - x - 40, 512 + x + 40): ell(d, sx, y, rx, ry, BLUSH, None)
def spiral(d, cx, cy, r=80):
    pts = [(cx + (r * t / (6 * math.pi)) * math.cos(t), cy + (r * t / (6 * math.pi)) * math.sin(t)) for t in [i * 0.1 for i in range(int(6 * math.pi / 0.1))]]
    line(d, pts, LW * 1.1)
def star(d, cx, cy, r, col=WHITE):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5; rr = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon([P(*p) for p in pts], fill=col)
EL, ER, EY = 512 - 170, 512 + 170, 478
MY = 752
def face(name):
    im = new(); d = ImageDraw.Draw(im); d._image = im
    if name == "neutral":
        eye(d, EL, EY); eye(d, ER, EY); brow(d, EL, EY - 140, ang=-4); brow(d, ER, EY - 140, ang=4); line(d, [(452, MY), (572, MY)], LW * 1.2)
    elif name == "happy":
        closed_eye(d, EL, EY + 10); closed_eye(d, ER, EY + 10); brow(d, EL, EY - 130, ang=-8, bend=14); brow(d, ER, EY - 130, ang=8, bend=14)
        mouth_open(d, 512, MY - 50, 230, 150); blush(d)
    elif name == "smile":
        eye(d, EL, EY, look=(0, -0.1)); eye(d, ER, EY, look=(0, -0.1)); brow(d, EL, EY - 140, ang=-6, bend=12); brow(d, ER, EY - 140, ang=6, bend=12)
        line(d, bez((400, MY - 30), (512, MY + 70), (624, MY - 30)), LW * 1.3); blush(d)
    elif name == "laugh":
        line(d, [(EL - 70, EY - 20), (EL + 50, EY + 20), (EL - 70, EY + 60)], LW * 1.4); line(d, [(ER + 70, EY - 20), (ER - 50, EY + 20), (ER + 70, EY + 60)], LW * 1.4)
        mouth_open(d, 512, MY - 70, 300, 200); blush(d); drop(d, 870, 330, 0.9)
    elif name == "sad":
        eye(d, EL, EY + 10, look=(0, 0.4), lid=0.3, lid_tilt=28); eye(d, ER, EY + 10, look=(0, 0.4), lid=0.3, lid_tilt=-28)
        brow(d, EL, EY - 120, ang=-18, bend=-6); brow(d, ER, EY - 120, ang=18, bend=-6)
        line(d, bez((430, MY + 40), (512, MY - 30), (594, MY + 40)), LW * 1.3)
    elif name == "cry":
        closed_eye(d, EL, EY + 20, up=False); closed_eye(d, ER, EY + 20, up=False)
        brow(d, EL, EY - 100, ang=-20); brow(d, ER, EY - 100, ang=20)
        tear_stream(d, EL + 20, EY + 40); tear_stream(d, ER - 20, EY + 40)
        mouth_open(d, 512, MY + 20, 150, 120, teeth=False, shape="o"); line(d, bez((450, MY - 60), (512, MY - 80), (574, MY - 60)), 6, TEAR_D)
    elif name == "angry":
        eye(d, EL, EY + 10, look=(0.2, 0.1), pr=0.42, lid=0.32, lid_tilt=-34); eye(d, ER, EY + 10, look=(-0.2, 0.1), pr=0.42, lid=0.32, lid_tilt=34)
        brow(d, EL + 10, EY - 95, ln=150, ang=24, w=30); brow(d, ER - 10, EY - 95, ln=150, ang=-24, w=30)
        mouth_open(d, 512, MY + 10, 190, 80, tongue=False, shape="o")
        for a in (0, 90, 180, 270):  # vein mark
            r = math.radians(a + 45); line(d, bez((820 + 20 * math.cos(r), 220 + 20 * math.sin(r)), (820 + 50 * math.cos(r + 0.6), 220 + 50 * math.sin(r + 0.6)), (820 + 70 * math.cos(r), 220 + 70 * math.sin(r))), 14, RED)
    elif name == "shocked":
        eye(d, EL, EY, rx=92, ry=108, pr=0.26, glint=False); eye(d, ER, EY, rx=92, ry=108, pr=0.26, glint=False)
        brow(d, EL, EY - 175, ang=-10, bend=20); brow(d, ER, EY - 175, ang=10, bend=20)
        mouth_open(d, 512, MY + 30, 150, 190, teeth=False, shape="o")
    elif name == "scared":
        eye(d, EL, EY, rx=88, ry=100, pr=0.24, look=(0.3, 0), glint=False); eye(d, ER, EY, rx=88, ry=100, pr=0.24, look=(0.3, 0), glint=False)
        brow(d, EL, EY - 150, ang=-22, bend=-8); brow(d, ER, EY - 150, ang=22, bend=-8)
        pts = [(400 + i * 224 / 8, MY + (18 if i % 2 else -18)) for i in range(9)]; line(d, pts, LW * 1.1)
        drop(d, 860, 320, 1.0); drop(d, 170, 380, 0.7)
    elif name == "nervous":
        eye(d, EL, EY, look=(-0.6, 0)); eye(d, ER, EY, look=(-0.6, 0)); brow(d, EL, EY - 140, ang=-16); brow(d, ER, EY - 140, ang=16)
        mouth_open(d, 512, MY, 220, 70, tongue=False, shape="o"); d.rectangle([P(410, MY - 30), P(614, MY + 30)], fill=WHITE)
        for x in range(430, 614, 40): line(d, [(x, MY - 30), (x, MY + 30)], 8)
        line(d, [(402, MY - 34), (622, MY - 34), (622, MY + 34), (402, MY + 34), (402, MY - 34)], LW); drop(d, 870, 330)
    elif name == "sleepy":
        closed_eye(d, EL, EY + 20, up=False, h=20); closed_eye(d, ER, EY + 20, up=False, h=20); brow(d, EL, EY - 110, ang=-4); brow(d, ER, EY - 110, ang=4)
        ell(d, 540, MY, 34, 40, MOUTH); ell(d, 640, MY - 40, 56, 56, (200, 236, 255, 200), TEAR_D, 8)
    elif name == "talk":
        eye(d, EL, EY); eye(d, ER, EY); brow(d, EL, EY - 145, ang=-8, bend=10); brow(d, ER, EY - 145, ang=8, bend=10)
        mouth_open(d, 512, MY - 20, 170, 110, teeth=True, tongue=True, shape="d")
    elif name == "smirk":
        eye(d, EL, EY + 6, lid=0.35, look=(0.3, 0)); eye(d, ER, EY + 6, lid=0.35, look=(0.3, 0)); brow(d, EL, EY - 120, ang=-4); brow(d, ER, EY - 150, ang=-14, bend=10)
        line(d, bez((440, MY + 20), (560, MY + 30), (620, MY - 30)), LW * 1.3)
    elif name == "blink":
        closed_eye(d, EL, EY + 10, up=False, h=10); closed_eye(d, ER, EY + 10, up=False, h=10); brow(d, EL, EY - 140, ang=-4); brow(d, ER, EY - 140, ang=4)
        line(d, [(452, MY), (572, MY)], LW * 1.2)
    elif name == "creepy":
        eye(d, EL, EY, rx=72, ry=72, pr=0.18, glint=False); eye(d, ER, EY, rx=72, ry=72, pr=0.18, glint=False)
        brow(d, EL, EY - 110, ang=-20, w=26); brow(d, ER, EY - 110, ang=20, w=26)
        pts = bez((300, MY - 60), (512, MY + 120), (724, MY - 60))
        mouth = pts + bez((724, MY - 60), (512, MY + 20), (300, MY - 60))
        poly(d, mouth, MOUTH)
        for i in range(1, 9):
            p = pts[i * 5]; line(d, [(p[0], p[1] - 40), (p[0], p[1])], 10, WHITE)
        line(d, pts, LW * 1.2)
    elif name == "dizzy":
        spiral(d, EL, EY); spiral(d, ER, EY); pts = [(420 + i * 184 / 8, MY + (16 if i % 2 else -16)) for i in range(9)]; line(d, pts, LW)
        star(d, 180, 200, 48, (255, 214, 64, 255)); star(d, 860, 240, 36, (255, 214, 64, 255))
    elif name == "squeeze":
        line(d, [(EL - 70, EY - 30), (EL + 50, EY + 10), (EL - 70, EY + 50)], LW * 1.5); line(d, [(ER + 70, EY - 30), (ER - 50, EY + 10), (ER + 70, EY + 50)], LW * 1.5)
        pts = [(410 + i * 204 / 10, MY + (20 if i % 2 else -20)) for i in range(11)]; line(d, pts, LW * 1.2); drop(d, 870, 300)
    elif name == "wink":
        eye(d, EL, EY); closed_eye(d, ER, EY + 10); brow(d, EL, EY - 145, ang=-8, bend=10); brow(d, ER, EY - 120, ang=10, bend=10)
        line(d, bez((410, MY - 20), (520, MY + 70), (630, MY - 40)), LW * 1.3); blush(d)
    elif name == "oh":
        eye(d, EL, EY, rx=84, ry=96, pr=0.36); eye(d, ER, EY, rx=84, ry=96, pr=0.36); brow(d, EL, EY - 160, ang=-6, bend=14); brow(d, ER, EY - 160, ang=6, bend=14)
        mouth_open(d, 512, MY + 10, 80, 90, teeth=False, tongue=False, shape="o")
    elif name == "content":
        closed_eye(d, EL, EY + 10); closed_eye(d, ER, EY + 10); brow(d, EL, EY - 120, ang=-4); brow(d, ER, EY - 120, ang=4)
        line(d, bez((430, MY - 20), (512, MY + 50), (594, MY - 20)), LW * 1.3); blush(d)
    elif name in ("sparkle", "sparkle_oh"):
        for cx in (EL, ER):
            eye(d, cx, EY, rx=96, ry=110, pr=0.62, glint=False, pupil_col=(60, 40, 110, 255))
            star(d, cx - 22, EY - 30, 34); ell(d, cx + 28, EY + 34, 12, 12, WHITE, None)
        brow(d, EL, EY - 170, ang=-6, bend=12); brow(d, ER, EY - 170, ang=6, bend=12); blush(d, y=620)
        if name == "sparkle": mouth_open(d, 512, MY - 30, 200, 130)
        else: mouth_open(d, 512, MY + 10, 100, 110, teeth=False, shape="o")
    elif name == "nerd":
        for cx in (EL, ER): ell(d, cx, EY, 110, 110, (230, 245, 255, 90), INK, 20); eye(d, cx, EY, rx=60, ry=66, look=(0, -0.3))
        line(d, [(EL + 110, EY - 10), (ER - 110, EY - 10)], 20); mouth_open(d, 512, MY - 10, 160, 100)
        d.rectangle([P(470, MY - 40), P(554, MY + 10)], fill=WHITE); line(d, [(512, MY - 40), (512, MY + 8)], 6)
    elif name == "stare":
        eye(d, EL, EY, rx=84, ry=84, pr=0.14, glint=False); eye(d, ER, EY, rx=84, ry=84, pr=0.14, glint=False)
        line(d, [(EL - 80, EY - 120), (EL + 80, EY - 120)], 24); line(d, [(ER - 80, EY - 120), (ER + 80, EY - 120)], 24); line(d, [(470, MY + 10), (554, MY + 10)], LW)
    k = 1.18; cx, cy = 512 * S, 590 * S
    big = im.resize((int(N * k), int(N * k)), Image.LANCZOS)
    ox, oy = int(cx * k - cx), int(cy * k - cy)
    im = big.crop((ox, oy, ox + N, oy + N))
    return im.resize((1024, 1024), Image.LANCZOS)
NAMES = "neutral happy sad cry angry shocked scared sleepy talk smirk blink creepy smile laugh nervous dizzy squeeze wink oh content sparkle sparkle_oh nerd stare".split()
os.makedirs("out", exist_ok=True)
atlas = Image.new("RGBA", (6 * 340, 4 * 340), (232, 185, 143, 255))
for i, n in enumerate(NAMES):
    im = face(n); im.save(f"out/{n}.png")
    atlas.alpha_composite(im.resize((340, 340), Image.LANCZOS), ((i % 6) * 340, (i // 6) * 340))
atlas.convert("RGB").save("atlas2.jpg", quality=90)
print("ok")
