"""Print the narration text of videos/<slug>/script.txt exactly as it goes to the voice (lines starting
with # are notes and are skipped), then the character count and the Flashloop credit estimate.
    python tools/script_text.py <slug>"""
import os, sys

STUDIO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if len(sys.argv) < 2:
    sys.exit(__doc__)
p = os.path.join(STUDIO, "videos", sys.argv[1], "script.txt")
lines = [l.strip() for l in open(p, encoding="utf-8") if l.strip() and not l.lstrip().startswith("#")]
text = "\n".join(lines)
print(text)
print(f"\n--- {len(text)} characters, {len(text.split())} words, ~{len(text) * 4} Flashloop credits for the voice",
      file=sys.stderr)
