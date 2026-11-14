"""Put the lead character's design options in one labelled picture for the user to pick from.
    python tools/options.py <slug> <sheet_A> <sheet_B> [<sheet_C> <sheet_D>]
Writes videos/<slug>/character_options.jpg (the sheets stacked, each under a big A/B/C/D badge)
and prints its path."""
import os, sys
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if len(sys.argv) < 3:
    sys.exit(__doc__)
slug, files = sys.argv[1], sys.argv[2:6]
W, BAR, GAP = 1280, 84, 18

tiles = []
for f in files:
    im = Image.open(f).convert("RGB")
    tiles.append(im.resize((W, round(im.height * W / im.width)), Image.LANCZOS))

sheet = Image.new("RGB", (W, sum(BAR + t.height + GAP for t in tiles) - GAP), (20, 20, 24))
dr = ImageDraw.Draw(sheet)
big, small = kit.font("ariblk.ttf", 58), kit.font("arialbd.ttf", 30)
y = 0
for k, t in enumerate(tiles):
    letter = "ABCD"[k]
    dr.rounded_rectangle((16, y + 10, 100, y + BAR - 6), 14, fill=(255, 205, 40))
    dr.text((58, y + BAR // 2 + 2), letter, fill=(20, 20, 24), font=big, anchor="mm")
    dr.text((120, y + BAR // 2 + 2), f"Option {letter}", fill=(240, 240, 240), font=small, anchor="lm")
    sheet.paste(t, (0, y + BAR))
    y += BAR + t.height + GAP

out_dir = os.path.join(ROOT, "videos", slug)
os.makedirs(out_dir, exist_ok=True)
out = os.path.join(out_dir, "character_options.jpg")
sheet.save(out, quality=90)
print(out)
