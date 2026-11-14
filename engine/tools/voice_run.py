# One command for the voice step: speed up 1.3x WITH pitch shift, cut silences + align words in one pass.
#   python tools/voice_run.py --video <slug> --voice videos/<slug>/audio/raw.mp3 [--speed 1.3] [--no-pitch]
import argparse, os, shutil, subprocess, sys
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
ap = argparse.ArgumentParser()
ap.add_argument('--video', required=True)
ap.add_argument('--voice', required=True)
ap.add_argument('--speed', type=float, default=1.3)
ap.add_argument('--no-pitch', action='store_true', help='Keep original pitch (atempo) instead of pitch-shifting with speed (asetrate)')
o = ap.parse_args()
adir = os.path.join(ROOT, 'videos', o.video, 'audio'); os.makedirs(adir, exist_ok=True)
fast = os.path.join(adir, 'raw_fast.wav')
os.environ.setdefault('WHISPER_MODEL', 'base.en')
voice_py = [sys.executable, os.path.join(ROOT, 'tools', 'voice.py'), '--video', o.video]
af = f'atempo={o.speed}' if o.no_pitch else f'aresample=48000,asetrate=48000*{o.speed},aresample=48000'
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', o.voice, '-af', af, '-ar', '48000', '-ac', '1', fast], check=True)
subprocess.run(voice_py + ['--voice', fast, '--force'], check=True)
print(f'voice ready: {os.path.join(adir, "voice.wav")} (x{o.speed} {"flat-pitch" if o.no_pitch else "pitch-shifted"}, silences cut, then timestamped)')
