"""Search YouTube for candidate footage (metadata only, no download), within the project budget.

Usage:
  python search.py PROJECT "gta 5 wanted level escape no commentary" [--n 15]

Prints a numbered table and appends results to PROJECT/sources/candidates.jsonl.
Each run counts as one search against PROJECT/sources/budget.json.
"""
import argparse
import json
import shutil
import subprocess
import uuid

import _budget


def fmt_dur(s):
    if not s:
        return "?"
    s = int(s)
    return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}" if s >= 3600 else f"{s // 60}:{s % 60:02d}"


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("project")
    p.add_argument("query")
    p.add_argument("--n", type=int, default=15, help="results to list (max 30)")
    a = p.parse_args()
    ytdlp = shutil.which("yt-dlp")
    if not ytdlp:
        p.error("yt-dlp is not installed. Run check_tools.py.")
    root = _budget.sources_dir(a.project)
    n = max(1, min(30, a.n))
    with _budget.NetLock(root):
        lim, used, cap = _budget.check(root, "search")
        attempt = uuid.uuid4().hex[:10]
        _budget.append(root, {"kind": "search", "attempt": attempt, "state": "started", "query": a.query})
        end = {"kind": "search", "attempt": attempt, "state": "failed", "query": a.query}
        try:
            proc = subprocess.run([ytdlp, "--ignore-config", "--flat-playlist", "-J", "--no-warnings",
                                   "--extractor-retries", "0", "--socket-timeout", "20",
                                   f"ytsearch{n}:{a.query}"],
                                  capture_output=True, text=True, encoding="utf8", errors="replace", timeout=120)
            out = proc.stdout + proc.stderr
            if _budget.is_blocked(out):
                end["state"] = "blocked"
                raise SystemExit("YouTube refused the request (rate limit / bot check). Network requests are now "
                                 "stopped for this project.")
            if proc.returncode != 0:
                end["detail"] = proc.stderr[-600:]
                raise SystemExit("Search failed:\n" + proc.stderr[-800:])
            entries = json.loads(proc.stdout).get("entries") or []
            end.update(state="done", results=len(entries))
        except subprocess.TimeoutExpired:
            end["detail"] = "timeout"
            raise SystemExit("Search timed out (counted as a failed search).")
        except ValueError as e:
            end["detail"] = f"bad JSON: {e}"
            raise SystemExit("Search returned unreadable output (counted as a failed search).")
        finally:
            _budget.append(root, end)
    with (root / "candidates.jsonl").open("a", encoding="utf8") as f:
        for i, e in enumerate(entries, 1):
            row = {"query": a.query, "id": e.get("id"), "url": e.get("url") or f"https://www.youtube.com/watch?v={e.get('id')}",
                   "title": e.get("title"), "channel": e.get("channel") or e.get("uploader"),
                   "duration": e.get("duration"), "views": e.get("view_count")}
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            views = f"{row['views']:,}" if row["views"] else "?"
            print(f"{i:2d}. [{fmt_dur(row['duration'])}] {row['title']}  | {row['channel']} | {views} views\n    {row['url']}")
    print(f"\nSearch {used + 1}/{cap} used for this project.")


if __name__ == "__main__":
    main()
