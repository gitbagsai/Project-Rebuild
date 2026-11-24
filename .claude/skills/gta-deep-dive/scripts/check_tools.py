"""Check that everything this skill needs is installed, and create the project folders.

Usage:
  python check_tools.py [PROJECT]
"""
import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path

NEEDED = [
    ("ffmpeg", "https://ffmpeg.org/download.html (Windows: winget install Gyan.FFmpeg; macOS: brew install ffmpeg)"),
    ("ffprobe", "comes with ffmpeg"),
    ("yt-dlp", "pip install -U yt-dlp   (or winget install yt-dlp / brew install yt-dlp)"),
]
PY = [("PIL", "pip install pillow", True), ("faster_whisper", "pip install faster-whisper", True)]
FOLDERS = ["research", "script", "sources", "scans", "audio", "music", "sfx", "cards", "edit", "renders"]


def main():
    ok = True
    for tool, how in NEEDED:
        path = shutil.which(tool)
        if path:
            ver = subprocess.run([tool, "-version" if tool.startswith("ff") else "--version"], capture_output=True,
                                 text=True).stdout.splitlines()[:1]
            print(f"OK   {tool}: {ver[0] if ver else path}")
        else:
            ok = False
            print(f"MISSING {tool}: install with {how}")
    for mod, how, required in PY:
        if importlib.util.find_spec(mod):
            print(f"OK   python module {mod}")
        else:
            ok = ok and not required
            print(f"MISSING python module {mod}: {how}")
    if shutil.which("yt-dlp") and not any(shutil.which(js) for js in ("deno", "node", "bun", "qjs")):
        print("WARN no JavaScript runtime (deno recommended): recent yt-dlp needs one for many YouTube formats. "
              "Install deno (https://deno.com) if downloads fail with missing-format errors.")
    if shutil.which("ffmpeg"):
        filters = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True).stdout
        for f in ("zoompan", "gblur", "loudnorm", "alimiter"):
            if f" {f} " not in filters:
                ok = False
                print(f"MISSING ffmpeg filter {f}: install a full ffmpeg build")
    if len(sys.argv) > 1:
        root = Path(sys.argv[1])
        for f in FOLDERS:
            (root / f).mkdir(parents=True, exist_ok=True)
        print(f"Project folders ready in {root.resolve()}")
    print("All set." if ok else "Install the missing items, then run this again.")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
