"""Minimal Telegram Bot API client using only the standard library."""

import json
import time
import urllib.error
import urllib.request

API_BASE = "https://api.telegram.org/bot{token}/{method}"
MAX_MESSAGE_LEN = 4096


class TelegramError(RuntimeError):
    pass


class TelegramClient:
    def __init__(self, token: str):
        if not token:
            raise ValueError("TELEGRAM_BOT_TOKEN is not set")
        self.token = token

    def call(self, method: str, http_timeout: float = 60, **params):
        url = API_BASE.format(token=self.token, method=method)
        data = json.dumps({k: v for k, v in params.items() if v is not None}).encode()
        req = urllib.request.Request(
            url, data=data, headers={"Content-Type": "application/json"}
        )
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=http_timeout) as resp:
                    body = json.load(resp)
                break
            except urllib.error.HTTPError as e:
                body = json.loads(e.read() or b"{}")
                break
            except (TimeoutError, urllib.error.URLError) as e:
                # GitHub 러너에서 텔레그램 API 응답이 가끔 늦어 몇 번 다시 시도합니다.
                if attempt == 2:
                    raise
                print(f"{method}: {e!r}, retrying", flush=True)
                time.sleep(5 * (attempt + 1))
        if not body.get("ok"):
            raise TelegramError(f"{method} failed: {body.get('description', body)}")
        return body["result"]

    def send_message(self, chat_id, text: str, parse_mode: str | None = "HTML"):
        """Send text, splitting it into chunks if it exceeds Telegram's limit."""
        for chunk in _split(text, MAX_MESSAGE_LEN):
            self.call(
                "sendMessage",
                chat_id=chat_id,
                text=chunk,
                parse_mode=parse_mode,
                disable_web_page_preview=True,
            )

    def get_updates(self, offset: int | None = None, timeout: int = 50):
        """Long-poll for new messages."""
        return self.call(
            "getUpdates",
            http_timeout=timeout + 30,
            offset=offset,
            timeout=timeout,
            allowed_updates=["message"],
        )

    def set_my_commands(self, commands: list[tuple[str, str]]):
        self.call(
            "setMyCommands",
            commands=[{"command": c, "description": d} for c, d in commands],
        )


def _split(text: str, size: int):
    if len(text) <= size:
        yield text
        return
    buf = ""
    for line in text.splitlines(keepends=True):
        while len(line) > size:
            if buf:
                yield buf
                buf = ""
            yield line[:size]
            line = line[size:]
        if len(buf) + len(line) > size:
            yield buf
            buf = ""
        buf += line
    if buf:
        yield buf
