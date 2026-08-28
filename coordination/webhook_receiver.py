#!/usr/bin/env python3
"""Small, dependency-free GitHub webhook receiver for the Escribe protocol."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

MAX_BODY = 1024 * 1024
REPO = Path(os.environ.get("ESCRIBE_REPO", Path(__file__).resolve().parents[1])).resolve()
STATE_DIR = Path(os.environ.get("ESCRIBE_STATE_DIR", Path.home() / ".local/state/escribe-webhook"))
SECRET = os.environ.get("GITHUB_WEBHOOK_SECRET", "")
WORKER = REPO / "coordination" / "worker.py"
lock = threading.Lock()
running = False


def valid_signature(body: bytes, supplied: str) -> bool:
    if not SECRET or not supplied.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(SECRET.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, supplied)


def task_changed(payload: dict) -> bool:
    target = "coordination/CURRENT_TASK.md"
    return any(target in commit.get("added", []) + commit.get("modified", [])
               for commit in payload.get("commits", []))


def launch_worker(after: str) -> bool:
    global running
    with lock:
        if running:
            return False
        running = True

    def run() -> None:
        global running
        try:
            STATE_DIR.mkdir(parents=True, exist_ok=True)
            log = (STATE_DIR / "worker.log").open("ab")
            env = os.environ.copy()
            env["ESCRIBE_WEBHOOK_AFTER"] = after
            subprocess.Popen([str(WORKER)], cwd=REPO, env=env, stdout=log,
                             stderr=subprocess.STDOUT, start_new_session=True)
            log.close()
        finally:
            # The worker owns the durable lock; this only permits webhook delivery
            # after the child has been spawned. The worker itself serializes runs.
            running = False

    threading.Thread(target=run, daemon=True).start()
    return True


class Handler(BaseHTTPRequestHandler):
    server_version = "EscribeWebhook/1.0"

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/github/webhook":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "-1"))
        except ValueError:
            length = -1
        if length < 0 or length > MAX_BODY:
            self.send_error(413)
            return
        body = self.rfile.read(length)
        if not valid_signature(body, self.headers.get("X-Hub-Signature-256", "")):
            self.send_error(401)
            return
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            self.send_error(400)
            return
        event = self.headers.get("X-GitHub-Event", "")
        if event == "ping":
            self.reply(200, {"accepted": True, "reason": "ping"})
        elif event != "push":
            self.reply(202, {"accepted": False, "reason": "event ignored"})
        elif payload.get("ref") != "refs/heads/main":
            self.reply(202, {"accepted": False, "reason": "branch ignored"})
        elif not task_changed(payload):
            self.reply(202, {"accepted": False, "reason": "task unchanged"})
        else:
            started = launch_worker(str(payload.get("after", "")))
            self.reply(202, {"accepted": started, "reason": "worker started" if started else "worker busy"})

    def reply(self, status: int, value: dict) -> None:
        data = json.dumps(value).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt: str, *args: object) -> None:
        print(fmt % args, flush=True)


if __name__ == "__main__":
    port = int(os.environ.get("ESCRIBE_WEBHOOK_PORT", "8787"))
    if not SECRET:
        raise SystemExit("GITHUB_WEBHOOK_SECRET is required")
    ThreadingHTTPServer((os.environ.get("ESCRIBE_WEBHOOK_HOST", "127.0.0.1"), port), Handler).serve_forever()

