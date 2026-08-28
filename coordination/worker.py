#!/usr/bin/env python3
"""Idempotent worker: sync main, run Codex, publish RESULT.md."""

from __future__ import annotations

import fcntl
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(os.environ.get("ESCRIBE_REPO", Path(__file__).resolve().parents[1])).resolve()
STATE = Path(os.environ.get("ESCRIBE_STATE_DIR", Path.home() / ".local/state/escribe-webhook"))
LOCK = STATE / "worker.lock"
TASK = REPO / "coordination/CURRENT_TASK.md"
RESULT = REPO / "coordination/RESULT.md"
CODEX = os.environ.get("CODEX_BIN", str(Path.home() / ".local/bin/codex"))
if not Path(CODEX).exists():
    CODEX = shutil.which("codex") or "codex"


def run(*args: str, check: bool = True, **kwargs: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=REPO, text=True, check=check, **kwargs)


def main() -> int:
    STATE.mkdir(parents=True, exist_ok=True)
    with LOCK.open("w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return 0
        if run("git", "status", "--porcelain", check=False, capture_output=True).stdout:
            return publish("blocked", "Checkout is dirty; no pull or execution was attempted.")
        run("git", "fetch", "origin", "main")
        run("git", "merge", "--ff-only", "origin/main")
        prompt = """Read AGENTS.md if it exists, then read coordination/CURRENT_TASK.md. Execute that task in this repository. Do not modify production systems, credentials, webhook configuration, or coordination/RESULT.md. Run appropriate tests. At the end, report a concise summary, files changed, tests run, and any blocker."""
        codex = subprocess.run([CODEX, "exec", "--ephemeral", "--cd", str(REPO), "--sandbox", "workspace-write", "--", prompt],
                               cwd=REPO, text=True, capture_output=True, check=False)
        output = (codex.stdout + "\n" + codex.stderr).strip()
        status = "completed" if codex.returncode == 0 else "failed"
        return publish(status, output[-12000:])


def publish(status: str, details: str) -> int:
    now = datetime.now(timezone.utc).isoformat()
    RESULT.write_text(f"# Result\n\n- Status: **{status}**\n- Finished: `{now}`\n\n## Details\n\n{details}\n", encoding="utf-8")
    run("git", "add", "-A")
    if run("git", "diff", "--cached", "--quiet", check=False).returncode == 0:
        return 0
    run("git", "commit", "-m", f"coordination: publish {status}")
    push = run("git", "push", "origin", "HEAD:main", check=False, capture_output=True)
    return push.returncode


if __name__ == "__main__":
    raise SystemExit(main())
