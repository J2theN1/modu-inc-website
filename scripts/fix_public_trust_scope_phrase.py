#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

REPO = Path.home() / "Projects/github/modu-inc-website"
WORKTREE = Path("/tmp/modu-public-trust-scope-fix")
BRANCH = "agent/public-trust-pages"
OLD = "It does not describe all MODU products, private development systems, client deployments or separately contracted services."
NEW = "It covers only this public website, not private development systems, client deployments or separately contracted services."


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
    path = WORKTREE / "scripts/apply_public_trust_pages.py"
    source = path.read_text(encoding="utf-8")
    if OLD not in source:
        print(json.dumps({"ok": False, "stage": "patch", "reason": "expected phrase missing"}))
        return 2
    path.write_text(source.replace(OLD, NEW, 1), encoding="utf-8")
    run(["git", "add", str(path.relative_to(WORKTREE))], cwd=WORKTREE)
    commit = run(["git", "commit", "-m", "fix: scope privacy notice to public website"], cwd=WORKTREE)
    if commit.returncode != 0:
        print(json.dumps({"ok": False, "stage": "commit", "stdout": commit.stdout[-1500:], "stderr": commit.stderr[-1500:]}))
        return commit.returncode
    push = run(["git", "push", "origin", f"HEAD:{BRANCH}"], cwd=WORKTREE)
    if push.returncode != 0:
        print(json.dumps({"ok": False, "stage": "push", "stdout": push.stdout[-1500:], "stderr": push.stderr[-1500:]}))
        return push.returncode
    print(json.dumps({"ok": True, "commit": run(["git", "rev-parse", "HEAD"], cwd=WORKTREE).stdout.strip()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
