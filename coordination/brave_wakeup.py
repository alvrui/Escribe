#!/usr/bin/env python3
"""Signal one already-open ChatGPT tab through Brave's CDP endpoint."""

import base64
import hashlib
import json
import os
import secrets
import socket
import sys
import urllib.request
from urllib.parse import urlparse

PORT = int(os.environ.get("BRAVE_CDP_PORT", "9222"))
MESSAGE = os.environ.get("WAKEUP_MESSAGE", "CODEX_RESULT_READY")
DRY_RUN = "--dry-run" in sys.argv


def tabs():
    with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/list", timeout=5) as response:
        return json.load(response)


def is_chatgpt(tab):
    hostname = urlparse(tab.get("url", "")).hostname or ""
    return tab.get("type") == "page" and (
        hostname == "chatgpt.com" or hostname.endswith(".chatgpt.com") or
        hostname == "chat.openai.com" or hostname.endswith(".chat.openai.com")
    )


def read_exact(sock, size):
    data = bytearray()
    while len(data) < size:
        chunk = sock.recv(size - len(data))
        if not chunk:
            raise RuntimeError("CDP connection closed")
        data.extend(chunk)
    return bytes(data)


class WebSocket:
    def __init__(self, ws_url):
        parsed = urlparse(ws_url)
        self.sock = socket.create_connection((parsed.hostname, parsed.port), timeout=10)
        key = base64.b64encode(secrets.token_bytes(16)).decode()
        path = parsed.path or "/"
        self.sock.sendall((f"GET {path} HTTP/1.1\r\nHost: {parsed.netloc}\r\n"
                           f"Upgrade: websocket\r\nConnection: Upgrade\r\n"
                           f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n").encode())
        header = b""
        while b"\r\n\r\n" not in header:
            header += self.sock.recv(4096)
        if not header.startswith(b"HTTP/1.1 101"):
            raise RuntimeError("CDP tab did not accept WebSocket upgrade")
        self.ident = 0

    def send(self, value):
        payload = json.dumps(value, separators=(",", ":")).encode()
        mask = secrets.token_bytes(4)
        masked = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
        length = len(masked)
        if length < 126:
            prefix = bytes([0x81, 0x80 | length])
        elif length < 65536:
            prefix = bytes([0x81, 0xFE]) + length.to_bytes(2, "big")
        else:
            prefix = bytes([0x81, 0xFF]) + length.to_bytes(8, "big")
        self.sock.sendall(prefix + mask + masked)

    def command(self, method, params=None):
        self.ident += 1
        self.send({"id": self.ident, "method": method, "params": params or {}})
        while True:
            first, second = read_exact(self.sock, 2)
            length = second & 0x7F
            if length == 126:
                length = int.from_bytes(read_exact(self.sock, 2), "big")
            elif length == 127:
                length = int.from_bytes(read_exact(self.sock, 8), "big")
            if second & 0x80:
                mask = read_exact(self.sock, 4)
                payload = bytes(byte ^ mask[index % 4] for index, byte in enumerate(read_exact(self.sock, length)))
            else:
                payload = read_exact(self.sock, length)
            if first & 0x0F == 8:
                raise RuntimeError("CDP tab closed WebSocket")
            if first & 0x0F != 1:
                continue
            message = json.loads(payload)
            if message.get("id") != self.ident:
                continue
            if "error" in message:
                raise RuntimeError(message["error"].get("message", "CDP command failed"))
            return message.get("result", {})

    def close(self):
        self.sock.close()


PROBE = """(() => {
  const visible = el => { const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0 && getComputedStyle(el).visibility !== 'hidden'; };
  const candidates = [...document.querySelectorAll('textarea, [contenteditable="true"], [role="textbox"]')]
    .filter(visible).filter(el => !el.disabled && !el.getAttribute('aria-disabled'));
  const el = candidates.find(x => /message|prompt|ask|mensaje|pregunta/i.test(
    (x.getAttribute('placeholder') || '') + ' ' + (x.getAttribute('aria-label') || '')
  )) || candidates[0];
  if (!el) return {ok: false, reason: 'no visible ChatGPT composer found'};
  const value = el.matches('textarea, input') ? el.value : el.innerText;
  if (value.trim()) return {ok: false, reason: 'composer is not empty; refusing to disturb a draft'};
  el.focus(); return {ok: true, tag: el.tagName};
})()"""


def main():
    try:
        matches = [tab for tab in tabs() if is_chatgpt(tab)]
    except Exception as error:
        raise RuntimeError(f"Brave CDP unavailable on 127.0.0.1:{PORT}; start the dedicated CDP profile first ({error})") from error
    if not matches:
        raise RuntimeError("no open ChatGPT tab found")
    if len(matches) > 1:
        raise RuntimeError(f"found {len(matches)} ChatGPT tabs; close extras")
    tab = matches[0]
    cdp = WebSocket(tab["webSocketDebuggerUrl"])
    try:
        probe = cdp.command("Runtime.evaluate", {"expression": PROBE, "returnByValue": True})
        value = probe.get("result", {}).get("value", {})
        if not value.get("ok"):
            raise RuntimeError(value.get("reason", "composer probe failed"))
        if DRY_RUN:
            print(json.dumps({"dryRun": True, "title": tab.get("title"), "url": tab.get("url"), "composer": value}))
            return
        cdp.command("Input.insertText", {"text": MESSAGE})
        for event in ("keyDown", "keyUp"):
            cdp.command("Input.dispatchKeyEvent", {"type": event, "key": "Enter", "code": "Enter",
                                                     "windowsVirtualKeyCode": 13, "nativeVirtualKeyCode": 13})
        print(json.dumps({"sent": True, "message": MESSAGE, "title": tab.get("title")}))
    finally:
        cdp.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"wakeup: {error}", file=sys.stderr)
        sys.exit(1)
