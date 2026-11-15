"""Generate crisp signage, poster, and UI textures for engine/rbx/library.py rooms."""
import os
import sys
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "tex")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kit  # noqa: E402


def f(name, size):
    return kit.font(name, size)


def nurse_chart():
    im = Image.new("RGB", (600, 800), (248, 252, 250))
    d = ImageDraw.Draw(im)
    d.rectangle([16, 16, 584, 784], outline=(43, 158, 179), width=12)
    d.text((300, 75), "VISION CHECK", font=f("ariblk.ttf", 52), fill=(30, 80, 100), anchor="mm")
    rows = [("E", 130, 185), ("F  P", 86, 315), ("T  O  Z", 62, 420), ("L  P  E  D", 44, 510), ("P E C F D", 32, 585)]
    for txt, sz, y in rows:
        d.text((300, y), txt, font=f("ariblk.ttf", sz), fill=(25, 25, 30), anchor="mm")
    d.line([(60, 645), (540, 645)], fill=(210, 60, 65), width=8)
    d.text((300, 710), "NO SNEEZING!", font=f("ariblk.ttf", 46), fill=(210, 45, 55), anchor="mm")
    im.save(os.path.join(OUT, "nurse_chart.png"))


def court_seal():
    im = Image.new("RGB", (800, 800), (74, 46, 22))
    d = ImageDraw.Draw(im)
    d.ellipse([36, 36, 764, 764], fill=(42, 62, 104), outline=(224, 184, 76), width=22)
    d.ellipse([74, 74, 726, 726], outline=(224, 184, 76), width=6)
    # Justice scales icon
    d.rectangle([388, 220, 412, 540], fill=(235, 200, 95))
    d.rectangle([290, 520, 510, 555], fill=(235, 200, 95))
    d.rectangle([200, 265, 600, 285], fill=(235, 200, 95))
    for px in (225, 575):
        d.line([(px, 285), (px - 65, 420)], fill=(235, 200, 95), width=7)
        d.line([(px, 285), (px + 65, 420)], fill=(235, 200, 95), width=7)
        d.chord([px - 75, 390, px + 75, 460], 0, 180, fill=(235, 200, 95))
    d.text((400, 150), "BLOX COURT", font=f("ariblk.ttf", 58), fill=(250, 228, 145), anchor="mm")
    d.text((400, 640), "JUSTICE DEPT", font=f("ariblk.ttf", 52), fill=(250, 228, 145), anchor="mm")
    im.save(os.path.join(OUT, "court_seal.png"))


def diner_menu():
    im = Image.new("RGB", (1400, 520), (24, 24, 34))
    d = ImageDraw.Draw(im)
    d.rectangle([14, 14, 1386, 506], outline=(255, 77, 109), width=14)
    d.text((700, 95), "BLOX BURGER", font=f("ariblk.ttf", 118), fill=(255, 110, 140), anchor="mm")
    items = [("CLASSIC BURGER", "$4"), ("CHEESE FRIES", "$2"), ("VANILLA SHAKE", "$3")]
    for i, (nm, pr) in enumerate(items):
        y = 235 + i * 85
        d.text((130, y), nm, font=f("ariblk.ttf", 52), fill=(248, 240, 210), anchor="lm")
        d.text((1260, y), pr, font=f("ariblk.ttf", 54), fill=(95, 230, 140), anchor="rm")
    im.save(os.path.join(OUT, "diner_menu.png"))


def grocery_sign():
    im = Image.new("RGB", (1400, 420), (37, 99, 235))
    d = ImageDraw.Draw(im)
    d.rectangle([16, 16, 1384, 404], outline=(250, 204, 21), width=14)
    d.text((700, 140), "FRESH MARKET", font=f("ariblk.ttf", 112), fill=(255, 255, 255), anchor="mm")
    d.rectangle([280, 245, 1120, 355], fill=(250, 204, 21))
    d.text((700, 300), "AISLE 3: SNACKS & DRINKS", font=f("ariblk.ttf", 52), fill=(30, 41, 59), anchor="mm")
    im.save(os.path.join(OUT, "grocery_sign.png"))


def gym_banner():
    im = Image.new("RGB", (1400, 460), (30, 58, 138))
    d = ImageDraw.Draw(im)
    d.rectangle([16, 16, 1384, 444], outline=(249, 115, 22), width=16)
    d.text((700, 140), "BLOX TIGERS", font=f("ariblk.ttf", 120), fill=(255, 255, 255), anchor="mm")
    d.rectangle([220, 250, 1180, 385], fill=(15, 23, 42), outline=(249, 115, 22), width=8)
    d.text((430, 318), "HOME  84", font=f("ariblk.ttf", 62), fill=(74, 222, 128), anchor="mm")
    d.text((970, 318), "GUEST  78", font=f("ariblk.ttf", 62), fill=(248, 113, 113), anchor="mm")
    im.save(os.path.join(OUT, "gym_banner.png"))


def police_chart():
    im = Image.new("RGB", (900, 1200), (244, 247, 251))
    d = ImageDraw.Draw(im)
    d.rectangle([12, 12, 888, 1188], outline=(30, 58, 138), width=14)
    d.rectangle([12, 12, 888, 175], fill=(30, 58, 138))
    d.text((450, 94), "BLOX POLICE DEPT", font=f("ariblk.ttf", 66), fill=(255, 255, 255), anchor="mm")
    for idx, label in enumerate(("6 FT", "5 FT", "4 FT", "3 FT", "2 FT", "1 FT")):
        y = 250 + idx * 155
        d.line([(60, y), (840, y)], fill=(51, 65, 85), width=8)
        d.text((95, y - 36), label, font=f("ariblk.ttf", 42), fill=(30, 58, 138), anchor="lm")
    im.save(os.path.join(OUT, "police_chart.png"))


def park_sign():
    im = Image.new("RGB", (1000, 520), (120, 68, 32))
    d = ImageDraw.Draw(im)
    d.rectangle([24, 24, 976, 496], fill=(242, 232, 205), outline=(64, 128, 60), width=16)
    d.text((500, 155), "BLOXVILLE PARK", font=f("ariblk.ttf", 80), fill=(34, 84, 45), anchor="mm")
    d.text((500, 295), "PLAYGROUND ->", font=f("ariblk.ttf", 58), fill=(180, 70, 35), anchor="mm")
    d.text((500, 405), "OPEN SUNRISE - SUNSET", font=f("ariblk.ttf", 40), fill=(70, 60, 45), anchor="mm")
    im.save(os.path.join(OUT, "park_sign.png"))


def rooftop_billboard():
    im = Image.new("RGB", (1200, 520), (15, 23, 42))
    d = ImageDraw.Draw(im)
    d.rectangle([16, 16, 1184, 504], outline=(56, 189, 248), width=14)
    d.text((600, 175), "BLOX CITY 24/7", font=f("ariblk.ttf", 104), fill=(250, 204, 21), anchor="mm")
    d.rectangle([180, 300, 1020, 430], fill=(225, 29, 72))
    d.text((600, 365), "LIVE ROOFTOP NEWS", font=f("ariblk.ttf", 64), fill=(255, 255, 255), anchor="mm")
    im.save(os.path.join(OUT, "rooftop_billboard.png"))


def subway_map():
    im = Image.new("RGB", (1200, 640), (248, 250, 252))
    d = ImageDraw.Draw(im)
    d.rectangle([14, 14, 1186, 626], outline=(30, 41, 59), width=14)
    d.rectangle([14, 14, 1186, 130], fill=(30, 58, 138))
    d.text((600, 72), "CENTRAL STATION  -  METRO MAP", font=f("ariblk.ttf", 52), fill=(255, 255, 255), anchor="mm")
    d.line([(120, 260), (1080, 260)], fill=(239, 68, 68), width=22)
    d.line([(140, 440), (1060, 330)], fill=(37, 99, 235), width=22)
    d.line([(450, 170), (760, 560)], fill=(34, 197, 94), width=22)
    for sx, sy in ((220, 260), (600, 260), (960, 260), (300, 420), (600, 370), (900, 345)):
        d.ellipse([sx - 24, sy - 24, sx + 24, sy + 24], fill=(255, 255, 255), outline=(15, 23, 42), width=8)
    d.text((600, 550), "PLATFORM 2  -  NEXT TRAIN 1 MIN", font=f("ariblk.ttf", 44), fill=(30, 41, 59), anchor="mm")
    im.save(os.path.join(OUT, "subway_map.png"))


def space_hud():
    im = Image.new("RGB", (1200, 600), (10, 22, 40))
    d = ImageDraw.Draw(im)
    d.rectangle([14, 14, 1186, 586], outline=(56, 189, 248), width=12)
    d.text((600, 78), "ORBITAL STATION  -  DECK 07", font=f("ariblk.ttf", 54), fill=(56, 189, 248), anchor="mm")
    d.ellipse([110, 165, 430, 485], outline=(34, 197, 94), width=8)
    d.ellipse([180, 235, 360, 415], outline=(34, 197, 94), width=5)
    d.line([(270, 325), (410, 225)], fill=(74, 222, 128), width=8)
    d.text((800, 220), "O2 LEVEL:  99%", font=f("ariblk.ttf", 58), fill=(74, 222, 128), anchor="mm")
    d.text((800, 325), "AIRLOCK:  SEALED", font=f("ariblk.ttf", 52), fill=(251, 146, 60), anchor="mm")
    d.text((800, 430), "GRAVITY:  1.0 G", font=f("ariblk.ttf", 52), fill=(224, 242, 254), anchor="mm")
    im.save(os.path.join(OUT, "space_hud.png"))


def haunted_portrait():
    im = Image.new("RGB", (700, 900), (36, 24, 48))
    d = ImageDraw.Draw(im)
    d.rectangle([20, 20, 680, 880], outline=(180, 147, 59), width=26)
    d.ellipse([210, 180, 490, 460], fill=(130, 138, 125))
    d.polygon([(140, 820), (560, 820), (460, 490), (240, 490)], fill=(20, 16, 28))
    for ex in (285, 415):
        d.ellipse([ex - 30, 285, ex + 30, 335], fill=(250, 204, 21))
        d.ellipse([ex - 10, 298, ex + 10, 322], fill=(15, 15, 20))
    d.arc([275, 365, 425, 425], 190, 350, fill=(25, 20, 30), width=10)
    im.save(os.path.join(OUT, "haunted_portrait.png"))


def beach_sign():
    im = Image.new("RGB", (1000, 520), (14, 165, 233))
    d = ImageDraw.Draw(im)
    d.rectangle([18, 18, 982, 502], fill=(254, 243, 199), outline=(249, 115, 22), width=16)
    d.text((500, 160), "SUNNY BAY BEACH", font=f("ariblk.ttf", 76), fill=(194, 65, 12), anchor="mm")
    d.text((500, 295), "SURF RENTALS & SHAVE ICE", font=f("ariblk.ttf", 46), fill=(15, 118, 110), anchor="mm")
    d.text((500, 405), "WAVES: HIGH", font=f("ariblk.ttf", 44), fill=(225, 29, 72), anchor="mm")
    im.save(os.path.join(OUT, "beach_sign.png"))


if __name__ == "__main__":
    for fn in (
        nurse_chart, court_seal, diner_menu, grocery_sign, gym_banner, police_chart,
        park_sign, rooftop_billboard, subway_map, space_hud, haunted_portrait, beach_sign,
    ):
        fn()
    print("Generated 12 library signage textures in", OUT)
