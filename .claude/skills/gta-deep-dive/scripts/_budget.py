"""Shared per-project request budget for search.py and fetch.py.

State lives in PROJECT/sources/: budget.json (limits, edited only by the user),
ledger.jsonl (append-only record of every search and download attempt) and
.net.lock (one network job at a time).
"""
import json
import os
import re
import time
from pathlib import Path

DEFAULTS = {"max_searches": 12, "max_downloads": 20, "min_gap_seconds": 6, "max_height": 1080}
# Real rate-limit / bot-check signals only. A bare "HTTP Error 403" is usually an outdated yt-dlp failing on
# format URLs, so it is recorded as a failure (with its log), not as a block.
# "Sign in to confirm your age" is an age gate on that one video (a normal failure), not a block.
BLOCK_RE = re.compile(r"HTTP Error 429|Too Many Requests|captcha|sign in to confirm you.re not a bot|not a bot|"
                      r"bot check|confirm you.re not a robot", re.I)


class BudgetError(SystemExit):
    pass


def sources_dir(project):
    root = Path(project).resolve() / "sources"
    root.mkdir(parents=True, exist_ok=True)
    return root


def limits(root):
    path = root / "budget.json"
    if not path.exists():
        path.write_text(json.dumps(DEFAULTS, indent=2), encoding="utf8")
    data = dict(DEFAULTS)
    data.update(json.loads(path.read_text(encoding="utf8")))
    return data


def ledger(root):
    path = root / "ledger.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf8").splitlines() if line.strip()]


def append(root, entry):
    entry = dict(entry, time=time.time())
    with (root / "ledger.jsonl").open("a", encoding="utf8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())


class NetLock:
    """Exclusive lock so only one search/download runs per project."""

    def __init__(self, root):
        self.path = root / ".net.lock"

    def __enter__(self):
        try:
            fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            raise BudgetError(f"Another network job holds {self.path}. If no search/fetch is running, "
                              "delete that file and try again.")
        with os.fdopen(fd, "w") as f:
            json.dump({"pid": os.getpid(), "start": time.time()}, f)
        return self

    def __exit__(self, *exc):
        self.path.unlink(missing_ok=True)


def check(root, kind):
    """Raise BudgetError if a new request of this kind is not allowed now."""
    lim = limits(root)
    rows = ledger(root)
    # A block stays in force until the USER authorises a retry; that is recorded by appending
    # {"kind": "clear", "state": "cleared", "by": "user", "reason": ...}. Earlier rows are never removed.
    last_clear = max((i for i, r in enumerate(rows) if r.get("kind") == "clear" and r.get("by") == "user"), default=-1)
    if any(r.get("state") == "blocked" for r in rows[last_clear + 1:]):
        raise BudgetError("A previous request was blocked (429 / bot check). Network requests are stopped "
                          "for this project. Continue with downloaded footage and tell the user.")
    unfinished = [r for r in rows if r.get("state") == "started"]
    finished_ids = {r.get("attempt") for r in rows if r.get("state") != "started"}
    if any(r.get("attempt") not in finished_ids for r in unfinished):
        raise BudgetError("An earlier attempt has no end record (interrupted). Check no downloader is still "
                          "running, then append a line with state 'interrupted' for it to ledger.jsonl.")
    used = len([r for r in unfinished if r.get("kind") == kind])
    cap = lim["max_searches" if kind == "search" else "max_downloads"]
    if used >= cap:
        raise BudgetError(f"{kind} budget used ({used}/{cap}). Reuse what you have, or ask the user to raise "
                          f"the limit in {root / 'budget.json'}.")
    ends = [r["time"] for r in rows if r.get("state") != "started" and r.get("kind") != "clear"]
    if ends:
        wait = lim["min_gap_seconds"] - (time.time() - max(ends))
        if wait > 0:
            time.sleep(wait)
    return lim, used, cap


def is_blocked(text):
    return bool(BLOCK_RE.search(text or ""))
