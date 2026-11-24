"""Look inside a video before using it: detect cuts, find loud game-audio moments, make contact sheets.

Usage:
  python scan.py VIDEO OUTDIR [--from 0] [--to END] [--every 0] [--frames 12.5,40.2]

Default: one tile per detected shot (middle frame). --every N: one tile every N seconds instead.
--frames: also export full-size frames at those times for close inspection.
Writes OUTDIR/scan.json and OUTDIR/sheet_01.jpg, sheet_02.jpg ... (20 tiles each, timestamps burned in).
Open the sheets as images to choose in-points; then confirm with --frames around the chosen moment.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def run(cmd, timeout=1800, cwd=None):
    return subprocess.run(cmd, cwd=cwd, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding="utf8",
                          errors="replace", timeout=timeout)


def ts(t):
    return f"{int(t // 60)}:{t % 60:05.2f}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("outdir")
    ap.add_argument("--from", dest="t0", type=float, default=0.0)
    ap.add_argument("--to", dest="t1", type=float)
    ap.add_argument("--every", type=float, default=0.0)
    ap.add_argument("--threshold", type=float, default=0.3, help="scene-change sensitivity (lower = more cuts)")
    ap.add_argument("--frames", help="comma-separated times to export at full size")
    a = ap.parse_args()
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg not found.")
    src = Path(a.video).resolve()
    out = Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)
    pr = run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(src)])
    dur = float(pr.stdout.strip() or 0)
    t1 = min(a.t1 or dur, dur)
    span = ["-ss", str(a.t0), "-t", str(t1 - a.t0)]

    # Cuts and loudness (metadata files written inside a temp dir to avoid path escaping issues)
    with tempfile.TemporaryDirectory() as td:
        run(["ffmpeg", "-v", "error", "-nostdin", "-threads", "2", *span, "-i", str(src), "-an", "-vf",
             f"scale=320:-2,select='gt(scene,{a.threshold})',metadata=print:file=scenes.txt",
             "-fps_mode", "vfr", "-f", "null", "-"], cwd=td)
        run(["ffmpeg", "-v", "error", "-nostdin", *span, "-i", str(src), "-vn", "-ac", "1", "-ar", "8000", "-af",
             "asetnsamples=4000,astats=metadata=1:reset=1,"
             "ametadata=print:key=lavfi.astats.Overall.RMS_level:file=levels.txt", "-f", "null", "-"], cwd=td)
        sc, lv = Path(td) / "scenes.txt", Path(td) / "levels.txt"
        text = sc.read_text() if sc.exists() else ""
        ltext = lv.read_text() if lv.exists() else ""
    cuts = [a.t0 + float(x) for x in re.findall(r"pts_time:([\d.]+)", text)]

    # Loud moments (game-audio events: crashes, gunshots, shouts) from 0.5 s RMS windows.
    loud, levels = [], []
    for m in re.finditer(r"pts_time:([\d.]+)\s+lavfi\.astats\.Overall\.RMS_level=(\S+)", ltext):
        try:
            v = float(m.group(2))
        except ValueError:
            continue
        if v > -200:
            levels.append((a.t0 + float(m.group(1)), v))
    if levels:
        vals = sorted(v for _, v in levels)
        med = vals[len(vals) // 2]
        for t, v in levels:
            if v > med + 9 and (not loud or t - loud[-1]["t"] > 2.0):
                loud.append({"t": round(t, 2), "db_over_median": round(v - med, 1)})

    # Tiles
    if a.every > 0:
        times, t = [], a.t0
        while t < t1:
            times.append((t, a.every))
            t += a.every
    else:
        bounds = [a.t0] + [c for c in cuts if a.t0 < c < t1] + [t1]
        times = [(x, y - x) for x, y in zip(bounds, bounds[1:]) if y - x > 0.05]
    font = None
    for cand in ("arial.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf", "/Library/Fonts/Arial.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/TTF/DejaVuSans.ttf"):
        try:
            font = ImageFont.truetype(cand, 15)
            break
        except OSError:
            pass
    if font is None:
        try:
            font = ImageFont.load_default(size=15)
        except TypeError:  # Pillow < 10.1
            font = ImageFont.load_default()
    tiles = []
    with tempfile.TemporaryDirectory() as td:
        for i, (start, d) in enumerate(times):
            mid = start + d / 2 if a.every <= 0 else start
            f = Path(td) / f"{i}.jpg"
            run(["ffmpeg", "-v", "error", "-y", "-nostdin", "-ss", f"{mid:.3f}", "-i", str(src), "-frames:v", "1",
                 "-vf", "scale=384:-2", str(f)])
            if not f.exists():
                continue
            im = Image.open(f).convert("RGB")
            dr = ImageDraw.Draw(im)
            lab = f"{ts(start)}  ({d:.1f}s)" if a.every <= 0 else ts(start)
            dr.rectangle((0, 0, 8 + dr.textlength(lab, font=font), 20), fill=(0, 0, 0))
            dr.text((4, 2), lab, font=font, fill=(255, 230, 0))
            tiles.append(im)
    sheets = []
    for si in range(0, len(tiles), 20):
        group = tiles[si:si + 20]
        w, h = group[0].size
        cols = 5
        rows = (len(group) + cols - 1) // cols
        sheet = Image.new("RGB", (w * cols, h * rows))
        for j, im in enumerate(group):
            sheet.paste(im, ((j % cols) * w, (j // cols) * h))
        p = out / f"sheet_{si // 20 + 1:02d}.jpg"
        sheet.save(p, quality=82)
        sheets.append(p.name)
    frames = []
    if a.frames:
        for t in [float(x) for x in a.frames.split(",") if x.strip()]:
            p = out / f"frame_{t:.2f}.jpg".replace(":", "_")
            run(["ffmpeg", "-v", "error", "-y", "-nostdin", "-ss", f"{t:.3f}", "-i", str(src), "-frames:v", "1",
                 "-q:v", "2", str(p)])
            frames.append(p.name)
    info = {"video": str(src), "duration": dur, "window": [a.t0, t1], "cuts": [round(c, 2) for c in cuts],
            "loud_moments": loud, "sheets": sheets, "frames": frames}
    (out / "scan.json").write_text(json.dumps(info, indent=1), encoding="utf8")
    print(f"{len(cuts)} cuts, {len(loud)} loud moments, {len(sheets)} sheets -> {out}")
    if loud:
        print("Loud moments: " + ", ".join(f"{ts(x['t'])} (+{x['db_over_median']}dB)" for x in loud[:25]))


if __name__ == "__main__":
    main()
