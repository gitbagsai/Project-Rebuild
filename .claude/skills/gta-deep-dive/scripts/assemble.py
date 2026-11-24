"""Render an edit decision list (EDL) to an MP4 with FFmpeg.

Usage:
  python assemble.py edit.json out.mp4 [--check] [--preview] [--threads 4]

--check    validate the EDL and print a coverage report, render nothing
--preview  half resolution, fast encode (for checking timing)

EDL (paths relative to edit.json):
{
  "width": 1920, "height": 1080, "fps": 30,
  "voice": {"source": "audio/vo.wav", "start": 0.0, "gain_db": 0},
  "duration": 812.4,                         # optional, default: end of the last shot
  "game_audio_db": -26,                      # default level for clip audio under narration
  "shots": [                                 # contiguous: each start = previous end, first start = 0
    {"start": 0.0, "end": 2.4, "source": "sources/gta5_store.mp4", "in": 31.2,
     "credit": "Creator", "game_db": -10, "speed": 1.0, "zoom": 1.0, "focus": [0.5, 0.5],
     "blur": 0, "dim": 0, "freeze": false, "push": 1.0, "note": "why this shot"},
    {"start": 2.4, "end": 5.0, "source": "sources/cover.jpg", "push": 1.05}      # stills: push 1.0-1.15
  ],
  "overlays": [                              # full-frame PNGs from cards.py, global times
    {"image": "cards/dazed_1.png", "start": 23.5, "end": 26.0, "fade_in": 0.12, "fade_out": 0.12}
  ],
  "music": [{"source": "music/bed1.mp3", "start": 0, "end": 240, "in": 0, "gain_db": -20,
             "fade_in": 1.0, "fade_out": 2.0}],
  "music_drops": [{"start": 1457.4, "end": 1464.8}],   # music fully out, short ramps
  "sfx": [{"source": "sfx/hit.wav", "start": 23.45, "gain_db": -6}]
}

Overlays and credit pills are composited inside each shot's single encode (an overlay that spans a cut is
split at the cut, fades stay on global time), so the picture is encoded once and joined without re-encoding.
Credit pills use the theme from cards/cards.json next to edit/ (or "cards_spec": "path/to/cards.json").

Levels: voice and every music cue are loudness-matched to -16 LUFS first, so music gain_db is relative
to the voice (-18 to -22 sits like the reference style). Clip audio uses game_db as a plain gain.
Shots render once into OUT_work/ and are reused while their settings and source are unchanged.
"""
import argparse
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
SHOT_KEYS = {"start", "end", "source", "in", "credit", "game_db", "speed", "zoom", "focus", "blur", "dim",
             "freeze", "push", "note", "label"}
TOP_KEYS = {"width", "height", "fps", "voice", "duration", "game_audio_db", "shots", "overlays", "music",
            "music_drops", "sfx", "notes", "cards_spec"}


class EDLError(Exception):
    pass


def run(cmd, timeout=3600):
    p = subprocess.run(cmd, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding="utf8",
                       errors="replace", timeout=timeout)
    if p.returncode != 0:
        raise RuntimeError("Command failed:\n" + " ".join(map(str, cmd))[:1500] + "\n" + p.stderr[-2500:])
    return p.stdout


def probe(path):
    out = run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type",
               "-of", "json", str(path)], timeout=60)
    d = json.loads(out)
    types = {s.get("codec_type") for s in d.get("streams", [])}
    dur = float(d.get("format", {}).get("duration") or 0)
    return dur, "video" in types, "audio" in types


def load(edl_path):
    edl_path = Path(edl_path).resolve()
    e = json.loads(edl_path.read_text(encoding="utf-8-sig"))
    unknown = set(e) - TOP_KEYS
    if unknown:
        raise EDLError(f"Unknown top-level keys: {sorted(unknown)}")
    base = edl_path.parent

    def P(rel):
        p = Path(rel)
        return p if p.is_absolute() else (base / p)
    return e, base, P


def validate(e, P):
    fps = e.get("fps", 30)
    shots = e.get("shots") or []
    if not shots:
        raise EDLError("No shots.")
    errors, cache = [], {}
    prev_end = 0.0
    for i, s in enumerate(shots):
        tag = f"shot {i + 1} ({s.get('start')}-{s.get('end')})"
        missing = [k for k in ("start", "end", "source") if k not in s]
        if missing:
            errors.append(f"{tag}: missing {missing}")
            continue
        bad = set(s) - SHOT_KEYS
        if bad:
            errors.append(f"{tag}: unknown keys {sorted(bad)}")
        if abs(s["start"] - prev_end) > 1.0 / fps:
            errors.append(f"{tag}: starts at {s['start']} but previous shot ends at {prev_end} (gap/overlap)")
        if s["end"] - s["start"] < 1.0 / fps:
            errors.append(f"{tag}: shorter than one frame")
        prev_end = s["end"]
        src = P(s["source"])
        if not src.exists():
            errors.append(f"{tag}: missing source {src}")
            continue
        if src.suffix.lower() in IMAGE_EXT:
            continue
        if src not in cache:
            cache[src] = probe(src)
        dur, has_v, _ = cache[src]
        if not has_v:
            errors.append(f"{tag}: {src.name} has no video stream")
        need = s.get("in", 0) + (0 if s.get("freeze") else (s["end"] - s["start"]) * s.get("speed", 1.0))
        if need > dur + 0.05:
            errors.append(f"{tag}: needs {src.name} up to {need:.2f}s but it is {dur:.2f}s long")
        if not 0.25 <= s.get("speed", 1.0) <= 4:
            errors.append(f"{tag}: speed must be 0.25-4")
        if not 1.0 <= s.get("zoom", 1.0) <= 3:
            errors.append(f"{tag}: zoom must be 1-3")
    total = e.get("duration", prev_end)
    if prev_end + 1.0 / fps < total:
        errors.append(f"shots end at {prev_end:.2f}s but duration is {total:.2f}s")
    for o in e.get("overlays", []):
        if not {"image", "start", "end"} <= set(o):
            errors.append(f"overlay {o}: needs image, start and end")
            continue
        if not P(o["image"]).exists():
            errors.append(f"overlay missing: {o['image']}")
        if not 0 <= o["start"] < o["end"] <= total + 0.05:
            errors.append(f"overlay {o['image']} {o['start']}-{o['end']} outside the film")
    for kind in ("music", "sfx"):
        for c in e.get(kind, []):
            if "source" not in c or not P(c["source"]).exists():
                errors.append(f"{kind} missing: {c.get('source')}")
            elif kind == "music" and not c.get("end", 0) > c.get("start", 0):
                errors.append(f"music {c['source']}: end must be after start")
    v = e.get("voice")
    if v and not P(v["source"]).exists():
        errors.append(f"voice missing: {v['source']}")
    if errors:
        raise EDLError("EDL problems:\n  " + "\n  ".join(errors))
    return total


def report(e, P, total):
    shots = e["shots"]
    by_src, still, blurred = {}, 0.0, 0.0
    for s in shots:
        d = s["end"] - s["start"]
        by_src.setdefault(s["source"], []).append(d)
        if Path(s["source"]).suffix.lower() in IMAGE_EXT or s.get("freeze"):
            still += d
        if s.get("blur"):
            blurred += d
    durs = sorted(s["end"] - s["start"] for s in shots)
    ov = sum(o["end"] - o["start"] for o in e.get("overlays", []))
    print(f"Duration {total:.1f}s | {len(shots)} shots | median shot {durs[len(durs) // 2]:.2f}s | "
          f"average {total / len(shots):.2f}s | longest {durs[-1]:.1f}s")
    print(f"Moving footage {total - still:.1f}s | stills/freezes {still:.1f}s | blurred card backdrops {blurred:.1f}s | "
          f"overlay time {ov:.1f}s")
    no_credit = [s for s in shots if not s.get("credit") and Path(s["source"]).suffix.lower() not in IMAGE_EXT]
    if no_credit:
        print(f"Note: {len(no_credit)} clip shots have no credit (fine only for your own recordings).")
    seen = {}
    for s in shots:
        key = (s["source"], round(s.get("in", 0), 1))
        seen.setdefault(key, []).append(s["start"])
    reps = {k: v for k, v in seen.items() if len(v) > 1}
    for (src, tin), starts in reps.items():
        print(f"Repeated shot {src}@{tin}s at {', '.join(f'{x:.1f}' for x in starts)} (OK only as a callback)")


def shot_hash(s, src, ovs, W, H, fps, preview):
    st = src.stat()
    ov_ids = [[o, Path(o["path"]).stat().st_size, Path(o["path"]).stat().st_mtime_ns] for o in ovs]
    blob = json.dumps([s, str(src), st.st_size, st.st_mtime_ns, ov_ids, W, H, fps, preview, 6], sort_keys=True)
    return hashlib.sha1(blob.encode()).hexdigest()[:16]


def shot_overlays(s, overlays, fps):
    """Overlays (global times) that are visible during this shot, as shot-local pieces."""
    a, b = s["start"], s["end"]
    out = []
    for o in overlays:
        st, en = float(o["start"]), float(o["end"])
        lo, hi = max(st, a), min(en, b)
        if hi - lo < 0.5 / fps:
            continue
        out.append({"path": o["path"], "on": round(lo - a, 4), "off": round(hi - a, 4), "g_start": st, "g_end": en,
                    "fade_in": float(o.get("fade_in", 0.12)), "fade_out": float(o.get("fade_out", 0.12)),
                    "shot_start": a})
    return out


def render_shot(s, src, out_v, out_a, W, H, fps, game_db, threads, preview, ovs=()):
    dur = s["end"] - s["start"]
    frames = max(1, round(s["end"] * fps) - round(s["start"] * fps))
    is_img = src.suffix.lower() in IMAGE_EXT
    speed = float(s.get("speed", 1.0))
    zoom = float(s.get("zoom", 1.0))
    fx, fy = s.get("focus", [0.5, 0.5])
    push = float(s.get("push", 1.0))
    vf = []
    if is_img or s.get("freeze"):
        inp = (["-loop", "1", "-framerate", str(fps), "-i", str(src)] if is_img
               else ["-ss", f"{s.get('in', 0):.3f}", "-i", str(src)])
        vf.append("trim=end_frame=1,setpts=PTS-STARTPTS" if not is_img else "trim=end_frame=1")
        # Fill canvas (2x for smooth push), then zoompan push with focus point.
        vf.append(f"scale={2 * W}:{2 * H}:force_original_aspect_ratio=increase,crop={2 * W}:{2 * H}")
        z0, z1 = zoom, zoom * push
        vf.append(f"zoompan=z='{z0}+({z1}-{z0})*on/{max(1, frames - 1)}':"
                  f"x='({fx})*iw-iw/zoom*({fx})':y='({fy})*ih-ih/zoom*({fy})':d={frames}:s={W}x{H}:fps={fps}")
    else:
        inp = ["-ss", f"{s.get('in', 0):.3f}", "-i", str(src)]
        vf.append(f"setpts=(PTS-STARTPTS)/{speed}")
        vf.append(f"fps={fps}")
        zw, zh = math.ceil(W * zoom / 2) * 2, math.ceil(H * zoom / 2) * 2
        vf.append(f"scale={zw}:{zh}:force_original_aspect_ratio=increase")
        vf.append(f"crop={W}:{H}:x='min(max(0,iw*{fx}-{W}/2),iw-{W})':y='min(max(0,ih*{fy}-{H}/2),ih-{H})'")
    if s.get("blur"):
        vf.append(f"gblur=sigma={float(s['blur']) * (0.5 if preview else 1)}")
    if s.get("dim"):
        vf.append(f"drawbox=x=0:y=0:w=iw:h=ih:t=fill:color=black@{min(0.9, float(s['dim']))}")
    vf.append(f"tpad=stop_mode=clone:stop={frames},trim=end_frame={frames},setsar=1")
    # Overlays: one still per input, repeated inside the graph; fades run on the film's global clock so an
    # overlay split across a cut fades exactly as one continuous overlay would.
    graph, last, ov_inputs = [f"[0:v]{','.join(vf)}[b0]"], "[b0]", []
    for j, o in enumerate(ovs, 1):
        ov_inputs += ["-i", o["path"]]
        f = [f"[{j}:v]format=rgba,scale={W}:{H},loop=loop={frames}:size=1:start=0,trim=end_frame={frames},"
             f"settb=1/{fps * 1000},setpts=(N/{fps}+{o['shot_start']:.4f})/TB"]
        if o["fade_in"] > 0:
            f.append(f"fade=t=in:st={o['g_start']:.4f}:d={o['fade_in']:.4f}:alpha=1")
        if o["fade_out"] > 0:
            f.append(f"fade=t=out:st={max(o['g_start'], o['g_end'] - o['fade_out']):.4f}:d={o['fade_out']:.4f}:alpha=1")
        f.append(f"setpts=N/{fps}/TB")
        graph.append(",".join(f) + f"[o{j}]")
        graph.append(f"{last}[o{j}]overlay=0:0:eof_action=pass:enable='gte(t,{o['on'] - 0.5 / fps:.4f})*"
                     f"lt(t,{o['off'] - 0.5 / fps:.4f})'[b{j}]")
        last = f"[b{j}]"
    # Every shot must share one pixel format and colour range, or the joined picture changes format
    # mid-stream (JPEG stills are full range) and later filters reset.
    graph.append(f"{last}scale=out_range=tv:out_color_matrix=bt709,format=yuv420p[vout]")
    enc = ["-color_range", "tv", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-c:v", "libx264", "-preset", "ultrafast" if preview else "medium", "-crf", "26" if preview else "17",
           "-g", str(fps * 2), "-r", str(fps), "-threads", str(threads)]
    run(["ffmpeg", "-v", "error", "-y", "-nostdin", *inp, *ov_inputs, "-filter_complex", ";".join(graph),
         "-map", "[vout]", "-an", "-frames:v", str(frames), *enc, str(out_v)])
    # Clip audio (silence for stills, freezes or silent sources).
    has_audio = False
    if not is_img and not s.get("freeze"):
        has_audio = probe(src)[2]
    if has_audio:
        tempo = []
        sp = speed
        while sp > 2.0:
            tempo.append("atempo=2.0"); sp /= 2.0
        while sp < 0.5:
            tempo.append("atempo=0.5"); sp /= 0.5
        tempo.append(f"atempo={sp:.5f}")
        af = ",".join(["asetpts=PTS-STARTPTS", *tempo, "aresample=48000", "aformat=channel_layouts=stereo",
                       f"volume={game_db}dB", f"apad=whole_dur={frames / fps:.4f}", f"atrim=end={frames / fps:.4f}",
                       "afade=t=in:d=0.012", f"afade=t=out:st={max(0, frames / fps - 0.02):.4f}:d=0.02"])
        run(["ffmpeg", "-v", "error", "-y", "-nostdin", "-ss", f"{s.get('in', 0):.3f}",
             "-t", f"{dur * speed + 0.5:.3f}", "-i", str(src), "-vn", "-af", af, "-c:a", "pcm_s16le", str(out_a)])
    else:
        run(["ffmpeg", "-v", "error", "-y", "-nostdin", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
             "-t", f"{frames / fps:.4f}", "-c:a", "pcm_s16le", str(out_a)])


def concat(files, out, work, copy=True, extra=()):
    lst = work / (out.stem + "_list.txt")
    lst.write_text("".join(f"file '{f.resolve().as_posix()}'\n" for f in files), encoding="utf8")
    run(["ffmpeg", "-v", "error", "-y", "-nostdin", "-f", "concat", "-safe", "0", "-i", str(lst),
         *(["-c", "copy"] if copy else extra), str(out)])


def mix_audio(e, P, game_wav, out_wav, total):
    inputs, chains, labels = ["-i", str(game_wav)], [], ["[0:a]"]
    n = 1
    v = e.get("voice")
    if v:
        inputs += ["-i", str(P(v["source"]))]
        chains.append(f"[{n}:a]aresample=48000,aformat=channel_layouts=stereo,loudnorm=I=-16:TP=-1.5:LRA=11,"
                      f"aresample=48000,volume={v.get('gain_db', 0)}dB,adelay={round(v.get('start', 0) * 1000)}:all=1[voice]")
        labels.append("[voice]")
        n += 1
    mus = []
    for i, c in enumerate(e.get("music", [])):
        dur = c["end"] - c["start"]
        inputs += ["-i", str(P(c["source"]))]
        fi, fo = c.get("fade_in", 1.0), c.get("fade_out", 1.5)
        chains.append(f"[{n}:a]atrim=start={c.get('in', 0)}:duration={dur},asetpts=PTS-STARTPTS,aresample=48000,"
                      f"aformat=channel_layouts=stereo,loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,"
                      f"volume={c.get('gain_db', -20)}dB,afade=t=in:d={fi},afade=t=out:st={max(0, dur - fo)}:d={fo},"
                      f"adelay={round(c['start'] * 1000)}:all=1[m{i}]")
        mus.append(f"[m{i}]")
        n += 1
    if mus:
        bus = "".join(mus) + (f"amix=inputs={len(mus)}:normalize=0:dropout_transition=0" if len(mus) > 1 else "anull")
        for d in e.get("music_drops", []):
            a, b = float(d["start"]), float(d["end"])
            r = float(d.get("ramp", 0.08))
            bus += f",volume='if(between(t,{a - r},{b + r}),max(0,min(1,max(({a}-t)/{r},(t-{b})/{r}))),1)':eval=frame"
        chains.append(bus + "[music]")
        labels.append("[music]")
    for i, c in enumerate(e.get("sfx", [])):
        inputs += ["-i", str(P(c["source"]))]
        chains.append(f"[{n}:a]aresample=48000,aformat=channel_layouts=stereo,volume={c.get('gain_db', -6)}dB,"
                      f"adelay={round(c['start'] * 1000)}:all=1[s{i}]")
        labels.append(f"[s{i}]")
        n += 1
    chains.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0:dropout_transition=0,"
                  f"apad,atrim=end={total:.4f},alimiter=limit=0.89:level=false[out]")
    run(["ffmpeg", "-v", "error", "-y", "-nostdin", *inputs, "-filter_complex", ";".join(chains),
         "-map", "[out]", "-c:a", "pcm_s16le", "-ar", "48000", str(out_wav)])


def write_credits(e, P, base, out):
    rows, seen = [], set()
    man = {}
    for mf in (base / "sources" / "manifest.jsonl", base.parent / "sources" / "manifest.jsonl"):
        if not mf.exists():
            continue
        for line in mf.read_text(encoding="utf8").splitlines():
            if line.strip():
                r = json.loads(line)
                if r.get("file"):
                    man[r["file"]] = r
    for s in e["shots"]:
        name = Path(s["source"]).name
        if name in seen:
            continue
        seen.add(name)
        m = man.get(name, {})
        credit = s.get("credit") or m.get("credit")
        if credit or m:
            rows.append(f"{credit or '?'}: {m.get('title') or name} {m.get('url') or ''}".strip())
    for c in e.get("music", []):
        rows.append(f"Music: {Path(c['source']).name}")
    out.write_text("Footage and sources\n" + "\n".join(dict.fromkeys(rows)) + "\n", encoding="utf8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("edl")
    ap.add_argument("out")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--threads", type=int, default=4)
    a = ap.parse_args()
    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            sys.exit(f"{tool} not found on PATH. Run check_tools.py.")
    e, base, P = load(a.edl)
    try:
        total = validate(e, P)
    except EDLError as err:
        sys.exit(str(err))
    report(e, P, total)
    if a.check:
        print("EDL OK.")
        return
    out = Path(a.out).resolve()
    if out.exists():
        sys.exit(f"{out} exists. Choose a new output name (keep earlier versions).")
    W, H, fps = e.get("width", 1920), e.get("height", 1080), e.get("fps", 30)
    if a.preview:
        W, H = W // 2 // 2 * 2, H // 2 // 2 * 2
    work = out.parent / (out.stem + "_work")
    shots_dir = base / ".shot_cache"
    work.mkdir(parents=True, exist_ok=True)
    shots_dir.mkdir(exist_ok=True)
    gdb = e.get("game_audio_db", -26)

    import cards
    theme, spec = None, P(e["cards_spec"]) if e.get("cards_spec") else None
    for cand in ([spec] if spec else [base.parent / "cards" / "cards.json", base / "cards" / "cards.json"]):
        if cand.exists():
            theme = json.loads(cand.read_text(encoding="utf-8-sig")).get("theme")
            break
    kit = cards.Kit(W, H, theme, base)
    pill_dir = shots_dir / "pills"
    pill_dir.mkdir(exist_ok=True)
    overlays = [dict(o, path=str(P(o["image"]).resolve())) for o in e.get("overlays", [])]

    vids, auds = [], []
    n = len(e["shots"])
    print(f"Overlays: {len(overlays)} + credit pills, composited per shot.", flush=True)
    for i, s in enumerate(e["shots"], 1):
        src = P(s["source"])
        ovs = []
        if s.get("credit"):
            key = json.dumps([s["credit"], kit.t, W, H], sort_keys=True)
            pill = pill_dir / ("pill_" + hashlib.sha1(key.encode()).hexdigest()[:12] + ".png")
            if not pill.exists():
                cards.credit_pill(kit, s["credit"]).save(pill)
            ovs.append({"path": str(pill), "on": 0.0, "off": s["end"] - s["start"], "g_start": s["start"],
                        "g_end": s["end"], "fade_in": 0, "fade_out": 0, "shot_start": s["start"]})
        ovs += shot_overlays(s, overlays, fps)
        h = shot_hash(s, src, ovs, W, H, fps, a.preview)
        v, au = shots_dir / f"{h}.mp4", shots_dir / f"{h}.wav"
        if not (v.exists() and au.exists()):
            print(f"[{i}/{n}] {src.name} @ {s.get('in', 0)}s ({s['end'] - s['start']:.2f}s)", flush=True)
            tv, ta = v.with_suffix(".tmp.mp4"), au.with_suffix(".tmp.wav")
            render_shot(s, src, tv, ta, W, H, fps, s.get("game_db", gdb), a.threads, a.preview, ovs)
            tv.replace(v)
            ta.replace(au)
        vids.append(v)
        auds.append(au)
    print("Joining picture...", flush=True)
    base_v = work / "picture.mp4"
    concat(vids, base_v, work)
    game = work / "game_audio.wav"
    concat(auds, game, work)
    pic = base_v
    print("Mixing audio...", flush=True)
    mix = work / "mix.wav"
    mix_audio(e, P, game, mix, total)
    tmp = out.with_name(out.stem + ".partial.mp4")
    run(["ffmpeg", "-v", "error", "-y", "-nostdin", "-i", str(pic), "-i", str(mix), "-map", "0:v", "-map", "1:a",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{total:.3f}", "-movflags", "+faststart", str(tmp)])
    dur, has_v, has_a = probe(tmp)
    if not (has_v and has_a) or abs(dur - total) > 0.2:
        sys.exit(f"Output check failed: duration {dur:.2f}s vs {total:.2f}s, video={has_v}, audio={has_a}. "
                 f"Kept {tmp} for inspection.")
    tmp.rename(out)
    write_credits(e, P, base, out.with_name(out.stem + "_credits.txt"))
    print(f"Done: {out} ({dur:.1f}s). Credits: {out.stem}_credits.txt. Intermediate files: {work}")


if __name__ == "__main__":
    main()
