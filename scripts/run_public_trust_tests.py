#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path.home() / "Projects/github/modu-inc-website"
WORKTREE = Path("/tmp/modu-public-trust-pages-test")
BRANCH = "agent/public-trust-pages"


def run(argv: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, cwd=cwd, text=True, capture_output=True, check=False)


def main() -> int:
    fetch = run(["git", "-C", str(REPO), "fetch", "-q", "origin", BRANCH])
    if fetch.returncode != 0:
        print(json.dumps({"ok": False, "stage": "fetch", "stderr": fetch.stderr[-1500:]}))
        return fetch.returncode
    if WORKTREE.exists():
        run(["git", "-C", str(REPO), "worktree", "remove", "--force", str(WORKTREE)])
        shutil.rmtree(WORKTREE, ignore_errors=True)
    add = run(["git", "-C", str(REPO), "worktree", "add", "--detach", str(WORKTREE), "FETCH_HEAD"])
    if add.returncode != 0:
        print(json.dumps({"ok": False, "stage": "worktree", "stderr": add.stderr[-1500:]}))
        return add.returncode
    result = run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        cwd=WORKTREE,
    )
    print(json.dumps({
        "ok": result.returncode == 0,
        "returncode": result.returncode,
        "stdout": result.stdout[-5000:],
        "stderr": result.stderr[-5000:],
    }, separators=(",", ":")))
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
