"""Generate a small starter set of original sound effects with FFmpeg (no downloads, no licences needed).

Usage:
  python make_sfx.py OUTDIR

Writes: hit.wav (low impact for cards/stamps), whoosh.wav (for chapter maps and card entries),
tick.wav (for checklist items and list beats), riser.wav (1.5 s build before a reveal).
Replace them with your own library any time; they only need to be short WAVs.
"""
import subprocess
import sys
from pathlib import Path

SFX = {
    "hit.wav": ("aevalsrc='0.9*sin(2*PI*(55+90*exp(-t*30))*t)*exp(-t*9)+0.25*(random(0)*2-1)*exp(-t*40)':"
                "s=48000:d=0.7", "lowpass=f=2500,afade=t=out:st=0.5:d=0.2"),
    "whoosh.wav": ("anoisesrc=d=0.6:c=pink:r=48000:a=0.6",
                   "bandpass=f=900:w=1.2,volume='sin(PI*t/0.6)':eval=frame,afade=t=in:d=0.05,afade=t=out:st=0.45:d=0.15"),
    "tick.wav": ("aevalsrc='0.7*sin(2*PI*1800*t)*exp(-t*60)':s=48000:d=0.12", "highpass=f=600"),
    "riser.wav": ("anoisesrc=d=1.5:c=white:r=48000:a=0.4",
                  "highpass=f=300,lowpass=f=6000,volume='pow(t/1.5,2)':eval=frame,afade=t=out:st=1.45:d=0.05"),
}


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    for name, (src, af) in SFX.items():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-nostdin", "-f", "lavfi", "-i", src, "-af",
                        af + ",aformat=channel_layouts=stereo", "-ar", "48000", str(out / name)], check=True)
        print(out / name)


if __name__ == "__main__":
    main()
