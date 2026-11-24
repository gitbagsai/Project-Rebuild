"""Download one source video (or one section of it) or one image into the project, within the budget.

Usage:
  python fetch.py PROJECT ID URL --credit "Creator name" [--section 1:20-2:05] [--basis "why you may use it"]
  python fetch.py PROJECT ID IMAGE_URL --image --credit "Outlet"

ID is a short name you choose (letters, digits, - and _), e.g. gta5_wanted_escape.
Video goes to PROJECT/sources/ID.mp4, images to PROJECT/sources/ID.<ext>.
Every attempt (including failures) counts against max_downloads in budget.json.
A 429 / bot check stops all network requests for the project.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import uuid
from pathlib import Path

import _budget

TIME = r"(?:\d+:)?\d+(?::\d+)?(?:\.\d+)?"


def manifest_add(root, row):
    with (root / "manifest.jsonl").open("a", encoding="utf8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def kill_tree(proc):
    if proc.poll() is not None:
        return
    if sys.platform == "win32":
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], capture_output=True, timeout=20)
    else:
        proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("project")
    p.add_argument("id")
    p.add_argument("url")
    p.add_argument("--credit", required=True, help="name shown in the on-screen credit pill")
    p.add_argument("--basis", default="commentary excerpt, credited", help="why this use is allowed")
    p.add_argument("--section", help="only download START-END, e.g. 1:20-2:05")
    p.add_argument("--image", action="store_true", help="URL is a direct image link")
    a = p.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,60}", a.id):
        p.error("ID: letters, digits, - and _ only.")
    if not re.match(r"https?://", a.url):
        p.error("URL must start with http:// or https://")
    if a.section and not re.fullmatch(fr"{TIME}-{TIME}", a.section):
        p.error("--section looks like 1:20-2:05")
    root = _budget.sources_dir(a.project)
    if list(root.glob(a.id + ".*")):
        p.error(f"{a.id} already exists in {root}. Pick a new ID or reuse that file.")
    rows = _budget.ledger(root)
    if any(r.get("url") == a.url and r.get("section") == a.section and r.get("state") == "saved" for r in rows):
        p.error("This URL/section was already downloaded. Check manifest.jsonl.")
    ytdlp = shutil.which("yt-dlp")
    if not a.image and not ytdlp:
        p.error("yt-dlp is not installed. Run check_tools.py.")

    with _budget.NetLock(root):
        lim, used, cap = _budget.check(root, "download")
        attempt = uuid.uuid4().hex[:10]
        base = {"kind": "download", "attempt": attempt, "id": a.id, "url": a.url, "section": a.section}
        _budget.append(root, dict(base, state="started"))
        state, detail = "failed", ""
        try:
            with tempfile.TemporaryDirectory(dir=root) as td:
                work = Path(td)
                if a.image:
                    req = urllib.request.Request(a.url, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=30) as r:
                        ctype = r.headers.get("Content-Type", "")
                        data = r.read(25 * 1024 * 1024 + 1)
                    if len(data) > 25 * 1024 * 1024 or not ctype.startswith("image/"):
                        detail = f"not an image or too large ({ctype})"
                    else:
                        ext = {"image/png": ".png", "image/webp": ".webp", "image/gif": ".gif"}.get(ctype.split(";")[0], ".jpg")
                        (root / (a.id + ext)).write_bytes(data)
                        state = "saved"
                else:
                    h = int(lim["max_height"])
                    cmd = [ytdlp, "--ignore-config", "--no-playlist", "--no-overwrites", "--no-progress",
                           "--retries", "0", "--fragment-retries", "1", "--extractor-retries", "0",
                           "--socket-timeout", "20", "--concurrent-fragments", "1", "--limit-rate", "6M",
                           "--write-info-json", "--merge-output-format", "mp4",
                           "-f", f"bv*[height<={h}][ext=mp4]+ba[ext=m4a]/bv*[height<={h}]+ba/b[height<={h}]",
                           "-o", str(work / (a.id + ".%(ext)s"))]
                    if a.section:
                        cmd += ["--download-sections", "*" + a.section]
                    cmd += ["--", a.url]
                    with tempfile.TemporaryFile() as log:
                        proc = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT)
                        try:
                            proc.wait(timeout=1800)
                        except BaseException:
                            kill_tree(proc)
                            raise
                        log.seek(0)
                        detail = log.read().decode("utf8", "replace")
                    logdir = root / "logs"
                    logdir.mkdir(exist_ok=True)
                    (logdir / f"{attempt}_{a.id}.log").write_text(" ".join(cmd) + "\n\n" + detail, encoding="utf8")
                    vids = [f for f in work.iterdir() if f.suffix.lower() in (".mp4", ".mkv", ".webm", ".mov")]
                    if _budget.is_blocked(detail):
                        state = "blocked"
                    elif proc.returncode == 0 and vids:
                        for f in work.iterdir():
                            if f.is_file():
                                f.replace(root / f.name)
                        state = "saved"
        except KeyboardInterrupt:
            state = "interrupted"
            raise
        except Exception as e:  # network errors etc.
            detail = str(e)
            state = "blocked" if _budget.is_blocked(detail) else "failed"
        finally:
            _budget.append(root, dict(base, state=state, detail=detail[-600:]))

    if state == "saved":
        info = {}
        info_file = root / (a.id + ".info.json")
        if info_file.exists():
            meta = json.loads(info_file.read_text(encoding="utf8"))
            info = {"title": meta.get("title"), "channel": meta.get("channel") or meta.get("uploader"),
                    "upload_date": meta.get("upload_date"), "duration": meta.get("duration")}
        files = [f.name for f in root.glob(a.id + ".*") if not f.name.endswith(".json")]
        manifest_add(root, dict(id=a.id, url=a.url, file=files[0] if files else None, credit=a.credit,
                                basis=a.basis, section=a.section, **info))
        print(f"Saved {files[0] if files else a.id} | download {used + 1}/{cap} used.")
    elif state == "blocked":
        raise SystemExit("Blocked (429 / bot check / sign-in). Network requests are now stopped for this project. "
                         f"Full output: sources/logs/{attempt}_{a.id}.log. Last lines:\n{detail[-600:]}\n"
                         "Do not retry; continue with downloaded footage and tell the user.")
    else:
        raise SystemExit(f"Download failed ({used + 1}/{cap} used). Last output:\n{detail[-800:]}")


if __name__ == "__main__":
    main()
