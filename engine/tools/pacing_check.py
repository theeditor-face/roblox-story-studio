#!/usr/bin/env python3
"""usage: python3 pacing_check.py cuts.txt words.json duration_seconds"""
# pacing_check.py - pacing.md targets from cuts + word timestamps. Zero tokens.
# usage: python3 pacing_check.py cuts.txt words.json duration_seconds
#   cuts.txt   = one cut time in s per line, excluding 0 (NLE export, `ffmpeg scdet`, or plan_timing.py for a plan)
#   words.json = word timestamps (WhisperX / faster-whisper / studio timing.py, or plan_timing.py's words_planned.json)
# wpm is speech only (audio.md 1.2): gaps >=0.5 s (the designed pauses) are taken out; slow reads stay in.
import json, re, sys, statistics as st
if len(sys.argv) != 4 or sys.argv[1] in ("-h", "--help"): sys.exit(__doc__ or "usage: python3 pacing_check.py cuts.txt words.json duration_seconds")
cuts = sorted(float(x) for x in open(sys.argv[1]) if x.strip())
dur = float(sys.argv[3])
d = json.load(open(sys.argv[2]))
if isinstance(d, dict):
    d = d.get("words") or [w for s in d.get("segments", []) for w in s.get("words", [])]
W = [(w.get("word") or w.get("text") or "").strip() for w in d]
S = [float(w["start"]) for w in d]; E = [float(w["end"]) for w in d]
end_p = lambda w: re.sub(r"[\"'”’)\]]+$", "", w)[-1:] in (".", "?", "!")
starts = [S[0]] + [S[i] for i in range(1, len(W)) if end_p(W[i - 1])]
edges = [0.0] + cuts + [dur]
shots = [b - a for a, b in zip(edges, edges[1:])]
def near(t, pool, tol=0.15): return any(abs(t - p) <= tol for p in pool)
on_sent = sum(near(c, starts) for c in cuts)
sent_cut = sum(near(s, cuts) for s in starts[1:])
leads = [min((c - s for c in cuts if abs(c - s) <= .15), key=abs, default=None) for s in starts]
leads = [x for x in leads if x is not None]
gaps = [(E[i], S[i + 1] - E[i]) for i in range(len(W) - 1) if S[i + 1] - E[i] >= 0.5]
speech = E[-1] - S[0] - sum(g for _, g in gaps)
wpm = len(W) / speech * 60
lo = 160 if dur <= 80 else 200
end_sh = [b - a for a, b in zip(edges, edges[1:]) if a >= dur - 15]; body_sh = [b - a for a, b in zip(edges, edges[1:]) if a < dur - 15]
ratio = st.mean(end_sh) / st.mean(body_sh) if end_sh and body_sh else 1.0
rows = [
 ("cuts/min 20-48",            round(len(cuts) / dur * 60, 1), 20 <= len(cuts) / dur * 60 <= 48),
 ("mean shot 1.3-2.5 s",       round(st.mean(shots), 2), 1.3 <= st.mean(shots) <= 2.5),
 ("shots > 3.5 s (<=2 holds)", sum(s > 3.5 for s in shots), sum(s > 3.5 for s in shots) <= 2),
 ("longest shot <= 6 s",       round(max(shots), 2), max(shots) <= 6),
 ("words/shot 5-6.5",          round(len(W) / len(shots), 2), 5 <= len(W) / len(shots) <= 6.5),
 ("sentence starts w/ cut >=60%", round(100 * sent_cut / max(1, len(starts) - 1)), sent_cut / max(1, len(starts) - 1) >= .6),
 ("cuts on sentence starts >=55%", round(100 * on_sent / len(cuts)), on_sent / len(cuts) >= .55),
 ("mean lead ms (-66..0)",     round(1000 * st.mean(leads)) if leads else None, bool(leads) and -.066 <= st.mean(leads) <= 0.0),
 ("first cut <= 2.5 s",        round(cuts[0], 2), cuts[0] <= 2.5),
 ("cuts in first 10 s >= 4",   sum(c < 10 for c in cuts), sum(c < 10 for c in cuts) >= 4),
 ("first word <= 0.2 s",       round(S[0], 2), S[0] <= .2),
 ("words in 0-3 s: 9-13",       sum(x < 3.0 for x in S), 9 <= sum(x < 3.0 for x in S) <= 13),
 (f"wpm {lo}-240 (speech only)", round(wpm), lo <= wpm <= 240),
 ("last 15 s mean shot vs body: >=1.2x or <=0.88x", f"{ratio:.2f}x", ratio >= 1.2 or ratio <= 0.88),
 ("pauses >=0.5 s: 2-3, each 0.6-1.3 s", " ".join(f"{g:.2f}@{t:.1f}" for t, g in gaps) or "none",
  2 <= len(gaps) <= 3 and all(.595 <= g <= 1.305 for _, g in gaps)),
 ("pause B (last pause, <=15 words before the end) 0.6-1.0 s", f"{gaps[-1][1]:.2f}, {sum(s > gaps[-1][0] for s in S)} words after" if gaps else "none",
  bool(gaps) and .595 <= gaps[-1][1] <= 1.005 and sum(s > gaps[-1][0] for s in S) <= 15),
]
for n, v, ok in rows: print(f"{'PASS' if ok else 'FAIL':4}  {n:50} {v}")
