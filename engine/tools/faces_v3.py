"""Draw the face atlas: 24 original expressions in a 6x4 grid (toon style, sharp ink lines).

Run:  python3 faces.py [out.png] [ink_hex]
Needs Pillow (pip install pillow). The PNG is transparent, so the head colour
shows through. Drawn 4x big then shrunk, so lines stay sharp, not soft.

Grid order (rbxkit.FACES must match):
  0 neutral   1 happy     2 sad      3 cry       4 angry     5 shocked
  6 scared    7 sleepy    8 talk     9 smirk    10 blink    11 creepy
 12 smile    13 laugh    14 nervous 15 dizzy    16 squeeze  17 wink
 18 oh       19 content  20 sparkle 21 sparkle_oh 22 nerd   23 stare

The whole set follows style-toon.md: big simple shapes, red open mouths, sweat drops,
swirl eyes, blush. Add new faces at the END (new row), never reorder: shot files
address faces by name, the atlas by position.
"""
import math
import sys
from PIL import Image, ImageDraw

NAMES = ["neutral", "happy", "sad", "cry", "angry", "shocked",
         "scared", "sleepy", "talk", "smirk", "blink", "creepy",
         "smile", "laugh", "nervous", "dizzy", "squeeze", "wink",
         "oh", "content", "sparkle", "sparkle_oh", "nerd", "stare"]
COLS, ROWS, CELL, SS = 6, 4, 512, 4
ZOOM = 1.18
S = CELL * SS


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def draw_face(name, ink):
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    W = int(S * 0.04)                      # line width
    white = (255, 255, 255, 255)
    red = (232, 71, 76, 255)               # open mouth
    tongue = (255, 138, 150, 255)
    tear = (120, 190, 255, 255)
    blush = (255, 120, 130, 150)
    ex, ey, er = (S * 0.31, S * 0.69), S * 0.42, S * 0.07   # eye x's, eye y, eye radius
    my = S * 0.70                          # mouth y

    def dot(x, y, r=er, tall=1.3, shine=False):
        d.ellipse([x - r, y - r * tall, x + r, y + r * tall], fill=ink)
        if shine:
            s = r * 0.42
            d.ellipse([x - r * 0.45 - s / 2, y - r * 0.7 - s / 2, x - r * 0.45 + s / 2, y - r * 0.7 + s / 2], fill=white)

    def ring(x, y, r=er * 1.55, pupil=0.3, look=(0, 0)):
        d.ellipse([x - r, y - r, x + r, y + r], fill=white, outline=ink, width=int(W * 0.7))
        p = r * pupil
        px, py = x + look[0] * r * 0.4, y + look[1] * r * 0.4
        d.ellipse([px - p, py - p, px + p, py + p], fill=ink)

    def arc_eye(x, y, up=True, r=er * 1.15):
        box = [x - r, y - r * 0.9, x + r, y + r * 0.9]
        d.arc(box, 195 if up else 15, 345 if up else 165, fill=ink, width=W)

    def line_eye(x, y, r=er * 1.1):
        d.line([x - r, y, x + r, y], fill=ink, width=W)

    def brow(x, y, tilt, L=er * 1.5):      # tilt>0: inner end down (angry)
        inner = 1 if x < S / 2 else -1
        d.line([x - L, y + (tilt if inner < 0 else -tilt), x + L, y + (-tilt if inner < 0 else tilt)],
               fill=ink, width=W)

    def flat_mouth(w=0.07, y=my):
        d.line([S * (0.5 - w), y, S * (0.5 + w), y], fill=ink, width=W)

    def smile(w=0.11, h=0.06, y=my, up=True):
        box = [S * (0.5 - w), y - S * h, S * (0.5 + w), y + S * h]
        d.arc(box, 15 if up else 195, 165 if up else 345, fill=ink, width=W)

    def open_smile(w=0.13, h=0.11, y=my - S * 0.03):
        box = [S * (0.5 - w), y - S * h, S * (0.5 + w), y + S * h]
        d.chord(box, 0, 180, fill=red, outline=ink, width=W)
        d.line([S * (0.5 - w), y, S * (0.5 + w), y], fill=ink, width=W)

    def o_mouth(r=0.06, y=my + S * 0.02, fill=red, squash=1.15):
        d.ellipse([S * (0.5 - r), y - S * r * squash, S * (0.5 + r), y + S * r * squash], fill=fill, outline=ink,
                  width=max(6, min(W, int(S * r * 0.4))))

    def sweat(x=S * 0.84, y=S * 0.40, r=S * 0.032):
        d.polygon([(x, y - r * 2.4), (x + r * 1.05, y), (x - r * 1.05, y)], fill=ink)
        d.ellipse([x - r * 1.15, y - r * 1.15, x + r * 1.15, y + r * 1.15], fill=ink)
        d.polygon([(x, y - r * 1.8), (x + r * 0.7, y), (x - r * 0.7, y)], fill=tear)
        d.ellipse([x - r * 0.8, y - r * 0.8, x + r * 0.8, y + r * 0.8], fill=tear)

    def cheeks(dy=2.2, r=1.15):
        for x in ex:
            d.ellipse([x - er * r, ey + er * dy, x + er * r, ey + er * (dy + 0.9)], fill=blush)

    def zigzag(w=0.12, y=my, n=6, amp=0.022):
        pts = [(S * (0.5 - w + 2 * w * i / n), y + (S * amp if i % 2 else -S * amp)) for i in range(n + 1)]
        d.line(pts, fill=ink, width=W, joint="curve")

    def spiral(x, y, r=er * 1.5, turns=2.3):
        pts = []
        for i in range(60):
            a = i / 59 * turns * 2 * math.pi
            rr = r * i / 59
            pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
        d.line(pts, fill=ink, width=int(W * 0.8), joint="curve")

    def sparkle_eye(x, y, r=er * 1.75):
        d.ellipse([x - r, y - r * 1.15, x + r, y + r * 1.15], fill=ink)
        d.ellipse([x - r * 0.62, y - r * 0.2, x + r * 0.62, y + r * 0.95], fill=(88, 62, 110, 255))
        d.ellipse([x - r * 0.7, y - r * 0.85, x - r * 0.05, y - r * 0.2], fill=white)
        d.ellipse([x + r * 0.2, y + r * 0.25, x + r * 0.55, y + r * 0.6], fill=white)
        for k in (-1, 0, 1):               # lashes
            d.line([x + k * r * 0.7, y - r * 1.05, x + k * r * 0.95, y - r * 1.45], fill=ink, width=int(W * 0.7))

    if name == "neutral":
        for x in ex: dot(x, ey)
        flat_mouth()
    elif name == "happy":
        for x in ex: arc_eye(x, ey, up=True)
        open_smile()
        cheeks()
    elif name == "sad":
        for x in ex: dot(x, ey + er * 0.3, er * 0.9)
        for x in ex: brow(x, ey - er * 2.1, -er * 0.55)
        smile(0.08, 0.05, my + S * 0.05, up=False)
    elif name == "cry":
        for x in ex: arc_eye(x, ey, up=False)
        for x in ex: brow(x, ey - er * 2.0, -er * 0.55)
        for x in ex:
            d.polygon([(x - er * 0.5, ey + er * 0.7), (x + er * 0.5, ey + er * 0.7),
                       (x + er * 0.75, S * 0.93), (x - er * 0.75, S * 0.93)], fill=tear)
        o_mouth(0.06, my + S * 0.03, fill=red, squash=0.85)
    elif name == "angry":
        for x in ex: ring(x, ey + er * 0.2, er * 1.45, pupil=0.36)
        for x in ex: brow(x, ey - er * 1.75, er * 0.85, L=er * 1.7)
        o_mouth(0.065, my + S * 0.03, fill=red, squash=0.95)
    elif name == "shocked":
        for x in ex: ring(x, ey, er * 1.6, pupil=0.24)
        o_mouth(0.085, my + S * 0.03)
        sweat()
    elif name == "scared":                 # panic: wide rings + clenched teeth
        for x in ex: ring(x, ey, er * 1.55, pupil=0.22)
        for x in ex: brow(x, ey - er * 2.4, -er * 0.6)
        box = [S * 0.33, my - S * 0.07, S * 0.67, my + S * 0.09]
        d.rounded_rectangle(box, radius=S * 0.05, fill=white, outline=ink, width=W)
        d.line([S * 0.33, my + S * 0.01, S * 0.67, my + S * 0.01], fill=ink, width=int(W * 0.6))
        for i in range(1, 5):
            x = S * (0.33 + i * 0.068)
            d.line([x, my - S * 0.07, x, my + S * 0.09], fill=ink, width=int(W * 0.6))
        sweat()
    elif name == "sleepy":                 # half-lidded, unimpressed
        for x in ex:
            d.chord([x - er * 1.15, ey - er * 1.2, x + er * 1.15, ey + er * 1.2], 0, 180, fill=ink)
            d.line([x - er * 1.45, ey, x + er * 1.45, ey], fill=ink, width=W)
        flat_mouth(0.06)
    elif name == "talk":
        for x in ex: dot(x, ey)
        d.ellipse([S * 0.42, my - S * 0.05, S * 0.58, my + S * 0.08], fill=red, outline=ink, width=W)
        d.ellipse([S * 0.455, my + S * 0.015, S * 0.545, my + S * 0.07], fill=tongue)
    elif name == "smirk":
        for x in ex: dot(x, ey, er * 0.95)
        brow(ex[0], ey - er * 1.8, er * 0.5)
        brow(ex[1], ey - er * 2.3, -er * 0.35)
        d.arc([S * 0.40, my - S * 0.10, S * 0.64, my + S * 0.04], 15, 125, fill=ink, width=W)
    elif name == "blink":
        for x in ex: line_eye(x, ey)
        flat_mouth()
    elif name == "creepy":
        for x in ex:
            d.ellipse([x - er * 1.3, ey - er * 1.3, x + er * 1.3, ey + er * 1.3], fill=ink)
            d.ellipse([x - er * 0.2, ey - er * 0.2, x + er * 0.2, ey + er * 0.2], fill=white)
        d.arc([S * 0.25, my - S * 0.16, S * 0.75, my + S * 0.10], 15, 165, fill=ink, width=W)
        for i in range(1, 8):
            x = S * (0.27 + i * 0.058)
            d.line([x, my + S * 0.03, x, my + S * 0.085], fill=ink, width=int(W * 0.6))
    elif name == "smile":
        for x in ex: dot(x, ey)
        smile(0.12, 0.07, my - S * 0.02)
    elif name == "laugh":
        for x in ex: arc_eye(x, ey, up=True, r=er * 1.3)
        box = [S * 0.34, my - S * 0.16, S * 0.66, my + S * 0.14]
        d.chord(box, 0, 180, fill=red, outline=ink, width=W)
        d.line([S * 0.34, my - S * 0.01, S * 0.66, my - S * 0.01], fill=ink, width=W)
        d.chord([S * 0.41, my + S * 0.04, S * 0.59, my + S * 0.16], 180, 360, fill=tongue)
    elif name == "nervous":
        for x in ex: dot(x, ey, er * 0.95)
        zigzag(0.09, my, n=4, amp=0.02)
        sweat()
    elif name == "dizzy":
        for x in ex: spiral(x, ey)
        o_mouth(0.075, my + S * 0.03, fill=red)
        d.ellipse([S * 0.455, my + S * 0.03, S * 0.545, my + S * 0.10], fill=tongue)
    elif name == "squeeze":                # >_< bracing
        for x, sgn in zip(ex, (1, -1)):
            r = er * 1.25
            d.line([x - sgn * r, ey - r, x + sgn * r * 0.6, ey, x - sgn * r, ey + r], fill=ink, width=W, joint="curve")
        zigzag(0.10, my, n=6, amp=0.02)
    elif name == "wink":
        dot(ex[0], ey)
        arc_eye(ex[1], ey, up=True)
        open_smile(0.11, 0.09)
        cheeks()
    elif name == "oh":
        for x in ex: dot(x, ey)
        o_mouth(0.045, my + S * 0.01, fill=tongue, squash=1.0)
    elif name == "content":                # relieved, eyes closed
        for x in ex: arc_eye(x, ey - er * 0.3, up=False, r=er * 1.25)
        smile(0.13, 0.08, my - S * 0.03)
    elif name == "sparkle":
        for x in ex: sparkle_eye(x, ey)
        smile(0.07, 0.045, my + S * 0.02)
        cheeks(dy=2.6, r=1.3)
    elif name == "sparkle_oh":
        for x in ex: sparkle_eye(x, ey)
        o_mouth(0.04, my + S * 0.04, fill=tongue, squash=1.0)
        cheeks(dy=2.6, r=1.3)
    elif name == "nerd":                   # round glasses, eyes up
        r = er * 1.75
        for x in ex:
            d.ellipse([x - r, ey - r, x + r, ey + r], fill=white, outline=ink, width=W)
            p = r * 0.36
            d.ellipse([x - p, ey - r * 0.55 - p, x + p, ey - r * 0.55 + p], fill=ink)
        d.line([ex[0] + r, ey, ex[1] - r, ey], fill=ink, width=W)
        o_mouth(0.045, my + S * 0.04, fill=red, squash=1.1)
    elif name == "stare":                  # thousand-yard stare
        for x in ex: ring(x, ey, er * 1.5, pupil=0.2)
        flat_mouth(0.05)
    z = int(S * ZOOM)                      # features a bit bigger on the head (toon style)
    big = im.resize((z, z), Image.LANCZOS)
    o = (z - S) // 2
    return big.crop((o, o, o + S, o + S)).resize((CELL, CELL), Image.LANCZOS)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "face_atlas.png"
    ink = hexrgb(sys.argv[2]) if len(sys.argv) > 2 else (24, 20, 28, 255)
    atlas = Image.new("RGBA", (CELL * COLS, CELL * ROWS), (0, 0, 0, 0))
    for i, n in enumerate(NAMES):
        atlas.paste(draw_face(n, ink), ((i % COLS) * CELL, (i // COLS) * CELL))
    atlas.save(out)
    print("saved", out)


if __name__ == "__main__":
    main()
