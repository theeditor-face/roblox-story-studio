#!/usr/bin/env python3
"""words.json -> caps.ass in the bright-toon style (style-toon.md §6): phrase captions, 2-4 words, ALL CAPS,
small bold type at 70.7 % of the height, one coloured key word per phrase, 2-frame fade-in, gone in pauses.

usage: python3 make_caps_toon.py words.json caps.ass
         [--yellow "eighteen,saturday,becca"] [--red "cracked,wait"] [--blue "water,towel,silence"]
         [--max-words 4] [--max-chars 24] [--fs 56] [--y 1357] [--outline 6] [--font "Poppins ExtraBold"]
Colour rule (style-toon.md §6.2): red = the rule word / danger / pain, yellow = names, times, key objects,
blue = calm or neutral things. At most one coloured run per phrase; about half the phrases get one.
words.json: a list of {w|word|text, start, end}, or Whisper/Parakeet segments."""
import json, re, argparse
p = argparse.ArgumentParser()
p.add_argument("words"); p.add_argument("out")
p.add_argument("--yellow", default=""); p.add_argument("--red", default=""); p.add_argument("--blue", default="")
p.add_argument("--max-words", type=int, default=4); p.add_argument("--max-chars", type=int, default=24)
p.add_argument("--fs", type=int, default=56); p.add_argument("--y", type=int, default=1357)
p.add_argument("--outline", type=int, default=6); p.add_argument("--font", default="Poppins ExtraBold")
p.add_argument("--lead", type=float, default=1 / 30); p.add_argument("--gap", type=float, default=0.3)
a = p.parse_args()
d = json.load(open(a.words))
if isinstance(d, dict):
    d = d.get("words") or [w for s in d.get("segments", []) for w in s.get("words", [])]
W = [(float(w.get("start", w.get("s"))), float(w.get("end", w.get("e"))), (w.get("w") or w.get("word") or w.get("text") or "").strip()) for w in d]
W = [w for w in W if w[2]]
norm = lambda w: re.sub(r"'s$", "", re.sub(r"[^\w']", "", w).lower().replace("’", "'"))
show = lambda w: re.sub(r"[\"“”,.;:]+", "", w).upper()
COL = {"yellow": "EAD95B", "red": "DB5D5E", "blue": "75C8E2"}
key = {}
for name in COL:
    for x in getattr(a, name).split(","):
        if x.strip(): key[norm(x.strip())] = name
# group words into phrases: break after . , ? ! ; at a pause; at max words / chars
phr, cur = [], []
for i, w in enumerate(W):
    cur.append(w)
    nxt = W[i + 1] if i + 1 < len(W) else None
    chars = sum(len(show(x[2])) + 1 for x in cur)
    brk = nxt is None or re.search(r"[.,?!;:]\W*$", w[2]) or nxt[0] - w[1] > a.gap or len(cur) >= a.max_words \
        or chars + len(show(nxt[2])) > a.max_chars
    if brk: phr.append(cur); cur = []
for i in range(len(phr) - 1, 0, -1):          # no 1-word orphans (a, the, I ...) unless the line is 1 word
    if len(phr[i]) == 1 and len(phr[i][0][2]) <= 3 and not re.search(r"[.?!]\W*$", phr[i - 1][-1][2]) \
            and phr[i][0][0] - phr[i - 1][-1][1] <= a.gap and len(phr[i - 1]) < a.max_words + 1:
        phr[i - 1] += phr[i]; del phr[i]
def bgr(h): return f"&H00{h[4:6]}{h[2:4]}{h[0:2]}&"
def ts(t):
    t = max(0.0, t); return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"
hdr = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Cap,{a.font},{a.fs},&H00FFFFFF&,&H00FFFFFF&,&H00000000&,&H00000000&,0,0,0,0,100,100,-1,0,1,{a.outline},3,5,60,60,0,1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
ev, n_col = [], 0
for i, ph in enumerate(phr):
    start = max(0.0, ph[0][0] - a.lead)
    nxt = phr[i + 1][0][0] - a.lead if i + 1 < len(phr) else 1e9
    end = min(nxt, ph[-1][1] + 0.25)           # stays a beat after the last word, never into the next phrase
    parts, used = [], False
    for (_, _, w) in ph:
        c = key.get(norm(w))
        if c and not used: parts.append(f"{{\\1c{bgr(COL[c])}}}{show(w)}{{\\1c&H00FFFFFF&}}"); used = True
        else: parts.append(show(w))
    n_col += used
    txt = " ".join(parts)
    width = sum(len(show(w[2])) + 1 for w in ph) * 0.62 * a.fs
    sc = min(100, int(100 * 0.82 * 1080 / max(1, width)))
    ev.append(f"Dialogue: 0,{ts(start)},{ts(max(end, start + 0.2))},Cap,,0,0,0,,{{\\an5\\pos(540,{a.y})\\fad(66,0)\\blur0.6\\fscx{sc}\\fscy{sc}}}{txt}")
open(a.out, "w", encoding="utf-8").write(hdr + "\n".join(ev) + "\n")
nw = sum(len(x) for x in phr)
print(f"{len(ev)} captions, {nw / len(ev):.2f} words each, {len(ev) / max(1e-9, W[-1][1]) :.2f} per second; coloured key word in {100 * n_col / len(ev):.0f} % (target 40-60 %) -> {a.out}")
