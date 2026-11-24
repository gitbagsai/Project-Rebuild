"""Word-timed transcript of a voiceover (or a source clip), and a phrase finder for placing cuts.

Usage:
  python transcribe.py AUDIO_OR_VIDEO OUT.json [--model small.en] [--language en]
  python transcribe.py find OUT.json "they remember your shirt" [--all]

The first form writes OUT.json (segments with word times) and OUT.txt (one timestamped line per segment).
The find form prints start/end seconds of a phrase, e.g. to set a shot start or an overlay start.
Needs faster-whisper (pip install faster-whisper). Models download on first use unless --local-only.
Uses an NVIDIA GPU when available, otherwise CPU.
"""
import argparse
import json
import os
import re
import site
import sys
from pathlib import Path


def norm(w):
    return re.sub(r"[^\w']", "", w.lower())


def find(args):
    d = json.loads(Path(args.transcript).read_text(encoding="utf8"))
    words = [w for s in d["segments"] for w in s["words"]]
    target = [norm(x) for x in args.phrase.split() if norm(x)]
    nw = [norm(w[2]) for w in words]
    hits = []
    for i in range(len(nw) - len(target) + 1):
        if nw[i:i + len(target)] == target:
            hits.append((words[i][0], words[i + len(target) - 1][1]))
    if not hits:
        sys.exit("Not found. Check the wording in the .txt transcript (recognition may differ slightly).")
    for a, b in (hits if args.all else hits[:1]):
        print(f"{a:.2f} {b:.2f}")


def transcribe(args):
    for base in site.getsitepackages() + [site.getusersitepackages()]:
        for sub in ("cublas", "cudnn", "cuda_nvrtc", "cuda_runtime"):
            p = Path(base) / "nvidia" / sub / "bin"
            if p.is_dir() and hasattr(os, "add_dll_directory"):
                os.add_dll_directory(str(p))
                os.environ["PATH"] = str(p) + os.pathsep + os.environ.get("PATH", "")
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit("faster-whisper is not installed: pip install faster-whisper")
    out = Path(args.out)
    model = None
    for dev, ct in (("cuda", "float16"), ("cpu", "int8")):
        try:
            model = WhisperModel(args.model, device=dev, compute_type=ct, cpu_threads=4,
                                 local_files_only=args.local_only)
            segs, _ = model.transcribe(args.audio, language=args.language, word_timestamps=True)
            data = []
            for s in segs:
                data.append({"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip(),
                             "words": [[round(w.start, 2), round(w.end, 2), w.word.strip()] for w in s.words or []]})
            break
        except Exception as e:  # GPU libraries missing -> CPU
            if dev == "cpu":
                raise
            print(f"GPU unavailable ({str(e)[:120]}), using CPU.", flush=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"model": args.model, "segments": data}, ensure_ascii=False), encoding="utf8")
    with out.with_suffix(".txt").open("w", encoding="utf8") as f:
        for s in data:
            f.write(f"[{int(s['start'] // 60)}:{s['start'] % 60:05.2f}] {s['text']}\n")
    print(f"{len(data)} segments -> {out} and {out.with_suffix('.txt')}")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "find":
        ap = argparse.ArgumentParser()
        ap.add_argument("cmd")
        ap.add_argument("transcript")
        ap.add_argument("phrase")
        ap.add_argument("--all", action="store_true")
        return find(ap.parse_args())
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("audio")
    ap.add_argument("out")
    ap.add_argument("--model", default="small.en")
    ap.add_argument("--language", default="en")
    ap.add_argument("--local-only", action="store_true", help="never download a model")
    transcribe(ap.parse_args())


if __name__ == "__main__":
    main()
