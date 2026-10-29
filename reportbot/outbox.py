"""Send Markdown report files (outbox/*.md) to Telegram once.

Usage:
    python -m reportbot.outbox outbox/2026-09-29-foo.md [more.md ...]

Only a small Markdown subset is converted to Telegram HTML: headings,
**bold**, `code`, lists, checkboxes, blockquotes, rules and tables.
"""

import html
import os
import re
import sys
from pathlib import Path

from reportbot.config import allowed_chat_ids, load_env
from reportbot.telegram import TelegramClient

_TABLE_SEP = re.compile(r"^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?$")


def _inline(text: str) -> str:
    text = html.escape(text, quote=False)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    return text


def _cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def md_to_telegram(md: str) -> str:
    out: list[str] = []
    table_header = True
    for raw in md.splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if stripped.startswith("|"):
            if _TABLE_SEP.match(stripped):
                continue
            cells = [_inline(c) for c in _cells(stripped)]
            if table_header:
                out.append("▪️ <b>" + "</b> | <b>".join(cells) + "</b>")
                table_header = False
            else:
                out.append("• " + cells[0] + (" → " + " / ".join(cells[1:]) if len(cells) > 1 else ""))
            continue
        table_header = True  # the next table row starts a new table
        if re.fullmatch(r"-{3,}|\*{3,}", stripped):
            out.append("──────────")
        elif m := re.match(r"^(#{1,6})\s+(.*)", stripped):
            prefix = "📌 " if len(m.group(1)) <= 2 else ""
            out.append(f"<b>{prefix}{_inline(m.group(2))}</b>")
        elif m := re.match(r"^(\s*)[-*]\s+\[( |x|X)\]\s+(.*)", line):
            box = "☐" if m.group(2) == " " else "☑"
            out.append(f"{m.group(1)}{box} {_inline(m.group(3))}")
        elif m := re.match(r"^(\s*)[-*]\s+(.*)", line):
            out.append(f"{m.group(1)}• {_inline(m.group(2))}")
        elif stripped.startswith(">"):
            out.append("▎" + _inline(stripped.lstrip("> ")))
        else:
            out.append(_inline(line))
    # collapse runs of blank lines
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip()


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__, file=sys.stderr)
        return 1
    load_env()
    client = TelegramClient(os.environ.get("TELEGRAM_BOT_TOKEN", ""))
    chat_ids = allowed_chat_ids()
    if not chat_ids:
        print("TELEGRAM_ALLOWED_CHAT_IDS is empty: no one to send to", file=sys.stderr)
        return 1
    for path in argv:
        text = md_to_telegram(Path(path).read_text(encoding="utf-8"))
        for chat_id in chat_ids:
            client.send_message(chat_id, text)
        print(f"sent {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
