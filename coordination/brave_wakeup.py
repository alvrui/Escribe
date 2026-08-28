#!/usr/bin/env python3
"""Signal one already-open ChatGPT tab through Brave's CDP endpoint."""

import base64
import hashlib
import json
import os
import shutil
import secrets
import socket
import subprocess
import sys
import urllib.request
from urllib.parse import urlparse

PORT = int(os.environ.get("BRAVE_CDP_PORT", "9222"))
MESSAGE = os.environ.get("WAKEUP_MESSAGE", "CODEX_RESULT_READY")
DRY_RUN = "--dry-run" in sys.argv
COPY_LAST = "--copy-last-response" in sys.argv
SEND_CLIPBOARD = "--send-clipboard" in sys.argv
DESKTOP_SEND = "--desktop-send" in sys.argv


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

LAST_RESPONSE = r"""(() => {
  const visible = el => { const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0 && getComputedStyle(el).visibility !== 'hidden';
  };
  const messages = [...document.querySelectorAll(
    '[data-message-author-role="assistant"], article[data-testid*="conversation-turn"]'
  )].filter(visible);
  const el = messages.reverse().find(x =>
    x.getAttribute('data-message-author-role') === 'assistant' ||
    /assistant|ChatGPT/i.test(x.getAttribute('data-testid') || '')
  );
  if (!el) return {ok: false, reason: 'no visible assistant response found'};
  const buttons = [...el.querySelectorAll('button, [role="button"]')].filter(visible);
  const copy = buttons.find(x => /copy|copiar/i.test(
    (x.getAttribute('aria-label') || '') + ' ' + (x.getAttribute('title') || '') + ' ' + (x.innerText || '')
  ));
  if (copy) copy.click();
  const text = el.innerText.trim();
  if (!text) return {ok: false, reason: 'last assistant response is empty'};
  return {ok: true, text, copyButtonFound: Boolean(copy)};
})()"""


def clipboard_command(mode: str):
    candidates = {
        "read": [("wl-paste", ["wl-paste", "--no-newline"]), ("xclip", ["xclip", "-selection", "clipboard", "-o"]),
                 ("xsel", ["xsel", "--clipboard", "--output"])],
        "write": [("wl-copy", ["wl-copy"]), ("xclip", ["xclip", "-selection", "clipboard"]),
                  ("xsel", ["xsel", "--clipboard", "--input"])],
    }
    for name, command in candidates[mode]:
        if shutil.which(name):
            return command
    raise RuntimeError("no clipboard utility found (install wl-clipboard, xclip, or xsel)")


def clipboard_read() -> str:
    command = clipboard_command("read")
    result = subprocess.run(command, text=True, capture_output=True, check=True)
    value = result.stdout.strip()
    if not value:
        raise RuntimeError("system clipboard is empty")
    return value


def clipboard_write(value: str) -> None:
    command = clipboard_command("write")
    subprocess.run(command, input=value, text=True, check=True)


def desktop_send() -> None:
    xdotool = shutil.which("xdotool")
    if not xdotool:
        raise RuntimeError("desktop send requires xdotool; clipboard was prepared but nothing was sent")
    windows = subprocess.run([xdotool, "search", "--onlyvisible", "--name", "ChatGPT"],
                             text=True, capture_output=True, check=False).stdout.split()
    if len(windows) != 1:
        raise RuntimeError(f"expected exactly one visible ChatGPT desktop window, found {len(windows)}")
    window = windows[0]
    subprocess.run([xdotool, "windowactivate", "--sync", window], check=True)
    subprocess.run([xdotool, "key", "--clearmodifiers", "ctrl+v"], check=True)
    subprocess.run([xdotool, "key", "--clearmodifiers", "Return"], check=True)


def select_tab():
    try:
        matches = [tab for tab in tabs() if is_chatgpt(tab)]
    except Exception as error:
        raise RuntimeError(f"Brave CDP unavailable on 127.0.0.1:{PORT}; start the dedicated CDP profile first ({error})") from error
    if not matches:
        raise RuntimeError("no open ChatGPT tab found")
    if len(matches) > 1:
        raise RuntimeError(f"found {len(matches)} ChatGPT tabs; close extras")
    return matches[0]


def send_text(text: str):
    tab = select_tab()
    cdp = WebSocket(tab["webSocketDebuggerUrl"])
    try:
        probe = cdp.command("Runtime.evaluate", {"expression": PROBE, "returnByValue": True})
        value = probe.get("result", {}).get("value", {})
        if not value.get("ok"):
            raise RuntimeError(value.get("reason", "composer probe failed"))
        cdp.command("Input.insertText", {"text": text})
        for event in ("keyDown", "keyUp"):
            cdp.command("Input.dispatchKeyEvent", {"type": event, "key": "Enter", "code": "Enter",
                                                     "windowsVirtualKeyCode": 13, "nativeVirtualKeyCode": 13})
        print(json.dumps({"sent": True, "message": text, "title": tab.get("title")}))
    finally:
        cdp.close()


def copy_last_response():
    tab = select_tab()
    cdp = WebSocket(tab["webSocketDebuggerUrl"])
    try:
        result = cdp.command("Runtime.evaluate", {"expression": LAST_RESPONSE, "returnByValue": True})
        value = result.get("result", {}).get("value", {})
        if not value.get("ok"):
            raise RuntimeError(value.get("reason", "response probe failed"))
        clipboard_write(value["text"])
        if DESKTOP_SEND:
            desktop_send()
        print(json.dumps({"copied": True, "desktopSent": DESKTOP_SEND,
                          "copyButtonFound": value.get("copyButtonFound", False),
                          "characters": len(value["text"]), "title": tab.get("title")}))
    finally:
        cdp.close()


def main():
    if COPY_LAST:
        copy_last_response()
        return
    if SEND_CLIPBOARD:
        send_text(clipboard_read())
        return
    tab = select_tab()
    cdp = WebSocket(tab["webSocketDebuggerUrl"])
    try:
        probe = cdp.command("Runtime.evaluate", {"expression": PROBE, "returnByValue": True})
        value = probe.get("result", {}).get("value", {})
        if not value.get("ok"):
            raise RuntimeError(value.get("reason", "composer probe failed"))
        if DRY_RUN:
            print(json.dumps({"dryRun": True, "title": tab.get("title"), "url": tab.get("url"), "composer": value}))
            return
    finally:
        cdp.close()
    send_text(MESSAGE)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"wakeup: {error}", file=sys.stderr)
        sys.exit(1)
