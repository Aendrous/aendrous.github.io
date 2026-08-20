#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Собрать черновик статьи для GitHub Pages из переписки DeepSeek.

API DeepSeek НЕ отдаёт историю с chat.deepseek.com. Нужен экспорт чата
(JSON из настроек DeepSeek или скопированный markdown) в `_inbox/`.

Примеры:

    python3 tools/deepseek_to_post.py --list _inbox/conversations.json
    python3 tools/deepseek_to_post.py _inbox/conversations.json --index 0
    python3 tools/deepseek_to_post.py _inbox/example-chat.md --format-only
    python3 tools/deepseek_to_post.py _inbox/example-chat.md --title "Заголовок"

После успешной записи поста запускается tools/build_site.py.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from llm_client import complete, load_env  # noqa: E402

INBOX = ROOT / "_inbox"
POSTS = ROOT / "_posts"

SYSTEM_PROMPT = """Ты редактор блога «Айтишник хочет пофилосовствовать» (aendrous.github.io).
Автор — Андрей Фетисов. Темы: книги, мистика, элиты, игры, визуальные новеллы, скрытые смыслы.
Пиши по-русски, живым первым лицом или уверенным эссе. Не канцелярит. Можно таблица-сравнение.
Не выдумывай факты, которых нет в переписке. Если в чате спор — сохрани тезис и контраргумент.
Верни ТОЛЬКО markdown статьи в таком виде:

---
title: "Заголовок без точки в конце"
date: {today}
author: "Андрей Фетисов"
categories: [тема1, тема2]
tags: [тег1, тег2]
---

# Заголовок

Текст статьи.

Не добавляй HTML, не оборачивай в fence markdown всего файла.
"""

RU_TRANS = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
    "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sch", "ъ": "",
    "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
}


def slugify(text: str) -> str:
    out = []
    for ch in text.lower().strip():
        if ch in RU_TRANS:
            out.append(RU_TRANS[ch])
        elif ch.isalnum():
            out.append(ch)
        elif ch in " -_—–":
            out.append("-")
    slug = re.sub(r"-{2,}", "-", "".join(out)).strip("-")
    return slug[:70] or "zametka"


def _message_text(node: object) -> str:
    if node is None:
        return ""
    if isinstance(node, str):
        return node.strip()
    if isinstance(node, list):
        return "\n".join(t for t in (_message_text(x) for x in node) if t)
    if not isinstance(node, dict):
        return str(node).strip()
    for key in ("content", "text", "parts", "value"):
        if key in node:
            return _message_text(node[key])
    return ""


def _role_of(node: dict) -> str:
    author = node.get("author") or node.get("role") or node.get("sender") or ""
    if isinstance(author, dict):
        author = author.get("role") or author.get("name") or ""
    role = str(author).lower()
    if role in ("user", "human", "prompter"):
        return "user"
    if role in ("assistant", "model", "ai", "deepseek", "bot", "system"):
        return "assistant" if role != "system" else "system"
    return role or "unknown"


def _walk_mapping(mapping: dict) -> list[dict[str, str]]:
    """ChatGPT / DeepSeek export: mapping id → node with parent/children."""
    current = None
    for node in mapping.values():
        if not isinstance(node, dict):
            continue
        if node.get("parent") in (None, "client-created-root", ""):
            current = node
            break
    if current is None and mapping:
        current = next(iter(mapping.values()))
    ordered: list[dict[str, str]] = []
    seen: set[str] = set()
    while isinstance(current, dict):
        nid = str(current.get("id", id(current)))
        if nid in seen:
            break
        seen.add(nid)
        msg = current.get("message") or current
        if isinstance(msg, dict):
            text = _message_text(msg)
            if text:
                ordered.append({"role": _role_of(msg), "content": text})
        children = current.get("children") or []
        if not children:
            break
        nxt = mapping.get(children[-1]) if isinstance(children[-1], str) else None
        current = nxt if isinstance(nxt, dict) else None
    return ordered


def parse_conversation(obj: object) -> tuple[str, list[dict[str, str]]]:
    if isinstance(obj, list):
        # список сообщений или список бесед
        if obj and isinstance(obj[0], dict) and (
            "role" in obj[0] or "author" in obj[0] or "content" in obj[0]
        ):
            msgs = []
            for item in obj:
                if not isinstance(item, dict):
                    continue
                text = _message_text(item)
                if text:
                    msgs.append({"role": _role_of(item), "content": text})
            return "chat", msgs
        return "", []
    if not isinstance(obj, dict):
        return "", []
    title = str(obj.get("title") or obj.get("name") or obj.get("id") or "chat")
    if isinstance(obj.get("mapping"), dict):
        return title, _walk_mapping(obj["mapping"])
    for key in ("messages", "items", "conversation"):
        if isinstance(obj.get(key), list):
            _, msgs = parse_conversation(obj[key])
            return title, msgs
    return title, []


def load_chats(path: Path) -> list[tuple[str, list[dict[str, str]]]]:
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".md", ".txt"}:
        title = path.stem
        msgs = parse_markdown_transcript(raw)
        return [(title, msgs)]
    data = json.loads(raw)
    chats: list[tuple[str, list[dict[str, str]]]] = []
    if isinstance(data, list):
        for item in data:
            title, msgs = parse_conversation(item)
            if msgs:
                chats.append((title or f"chat-{len(chats)+1}", msgs))
        if not chats:
            title, msgs = parse_conversation(data)
            if msgs:
                chats.append((title, msgs))
        return chats
    if isinstance(data, dict):
        for key in ("conversations", "data", "chats", "items"):
            if isinstance(data.get(key), list):
                for item in data[key]:
                    title, msgs = parse_conversation(item)
                    if msgs:
                        chats.append((title or f"chat-{len(chats)+1}", msgs))
                if chats:
                    return chats
        title, msgs = parse_conversation(data)
        if msgs:
            return [(title, msgs)]
    raise ValueError(f"Не распознал формат экспорта: {path}")


def parse_markdown_transcript(text: str) -> list[dict[str, str]]:
    lines = text.replace("\r\n", "\n").split("\n")
    msgs: list[dict[str, str]] = []
    role = "user"
    buf: list[str] = []
    header = re.compile(
        r"^\s{0,3}#{1,3}\s*(user|assistant|you|human|deepseek|ai|бот|я)\s*[:：]?\s*$",
        re.I,
    )
    bold = re.compile(
        r"^\s*\*\*(user|assistant|you|human|deepseek|ai|бот|я)\*\*\s*[:：]?\s*$",
        re.I,
    )
    prefixed = re.compile(
        r"^\s*(user|assistant|you|human|deepseek|ai|бот|я)\s*[:：]\s*(.*)$",
        re.I,
    )

    def alias(name: str) -> str:
        n = name.lower()
        if n in {"user", "you", "human", "я"}:
            return "user"
        return "assistant"

    def flush() -> None:
        body = "\n".join(buf).strip()
        if body:
            msgs.append({"role": role, "content": body})
        buf.clear()

    for line in lines:
        m = header.match(line) or bold.match(line)
        if m:
            flush()
            role = alias(m.group(1))
            continue
        m = prefixed.match(line)
        if m:
            flush()
            role = alias(m.group(1))
            rest = m.group(2)
            if rest:
                buf.append(rest)
            continue
        buf.append(line)
    flush()
    return msgs


def transcript(msgs: list[dict[str, str]], limit: int = 24000) -> str:
    chunks = []
    for msg in msgs:
        role = "Автор" if msg["role"] == "user" else "DeepSeek"
        chunks.append(f"### {role}\n\n{msg['content'].strip()}\n")
    text = "\n".join(chunks).strip()
    if len(text) > limit:
        text = text[:limit] + "\n\n[...переписка обрезана...]\n"
    return text


def extract_front_matter_title(markdown_text: str) -> str | None:
    m = re.search(r'^title:\s*"?([^"\n]+)"?\s*$', markdown_text, re.M)
    return m.group(1).strip() if m else None


def ensure_front_matter(markdown_text: str, title: str | None, today: str) -> str:
    text = markdown_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:markdown)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text).strip()
    if text.startswith("---"):
        if re.search(r"^date:\s*$", text, re.M) or "date:" not in text[:400]:
            text = re.sub(r"^---\s*", f"---\ndate: {today}\n", text, count=1)
        return text + ("\n" if not text.endswith("\n") else "")
    safe_title = (title or "Заметка из переписки DeepSeek").replace('"', "'")
    return (
        f"---\ntitle: \"{safe_title}\"\ndate: {today}\n"
        f'author: "Андрей Фетисов"\ncategories: [черновики, deepseek]\ntags: [deepseek]\n---\n\n'
        f"{text}\n"
    )


def write_post(markdown_text: str, title_hint: str | None) -> Path:
    today = dt.date.today().isoformat()
    text = ensure_front_matter(markdown_text, title_hint, today)
    title = extract_front_matter_title(text) or title_hint or "zametka"
    slug = slugify(title)
    path = POSTS / f"{today}-{slug}.md"
    n = 2
    while path.exists():
        path = POSTS / f"{today}-{slug}-{n}.md"
        n += 1
    path.write_text(text, encoding="utf-8")
    return path


def format_only_article(title: str, msgs: list[dict[str, str]]) -> str:
    today = dt.date.today().isoformat()
    body = transcript(msgs)
    return (
        f"---\ntitle: \"{title.replace(chr(34), chr(39))}\"\ndate: {today}\n"
        f'author: "Андрей Фетисов"\ncategories: [черновики, deepseek]\n'
        f"tags: [deepseek, расшифровка]\n---\n\n"
        f"# {title}\n\n"
        f"*Черновик из переписки, без редактуры моделью (`--format-only`).*\n\n"
        f"{body}\n"
    )


def build_article(title: str, msgs: list[dict[str, str]], prefer: str) -> str:
    today = dt.date.today().isoformat()
    user = (
        f"Заголовок-подсказка: {title}\n\n"
        f"Переписка:\n\n{transcript(msgs)}\n\n"
        f"Собери из этого законченную статью для блога."
    )
    prompt = SYSTEM_PROMPT.format(today=today)
    return complete(
        [{"role": "system", "content": prompt}, {"role": "user", "content": user}],
        prefer=prefer,
    )


def main(argv: list[str] | None = None) -> int:
    load_env()
    parser = argparse.ArgumentParser(description="Переписка DeepSeek → пост Jekyll/статический HTML")
    parser.add_argument("source", nargs="?", help="JSON или markdown в _inbox/")
    parser.add_argument("--list", dest="list_only", action="store_true", help="Показать беседы в файле")
    parser.add_argument("--index", type=int, default=0, help="Номер беседы (с нуля)")
    parser.add_argument("--title", default="", help="Подсказка заголовка")
    parser.add_argument("--format-only", action="store_true", help="Не звать API, сохранить расшифровку")
    parser.add_argument("--prefer", choices=("deepseek", "gigachat", "auto"), default="deepseek")
    parser.add_argument("--skip-build", action="store_true")
    args = parser.parse_args(argv)

    if not args.source:
        parser.print_help()
        print("\nПоложите экспорт в _inbox/ и укажите файл.")
        return 2

    path = Path(args.source)
    if not path.is_absolute():
        path = (ROOT / path).resolve()
    if not path.exists():
        sys.stderr.write(f"Нет файла: {path}\n")
        return 1

    chats = load_chats(path)
    if args.list_only:
        for i, (title, msgs) in enumerate(chats):
            print(f"{i:3d}  {title}  ({len(msgs)} сообщ.)")
        return 0
    if not chats:
        sys.stderr.write("В файле нет сообщений.\n")
        return 1
    if args.index < 0 or args.index >= len(chats):
        sys.stderr.write(f"--index {args.index} вне диапазона 0..{len(chats)-1}\n")
        return 1

    title, msgs = chats[args.index]
    title = args.title or title or path.stem
    if args.format_only:
        article = format_only_article(title, msgs)
    else:
        article = build_article(title, msgs, args.prefer)

    out = write_post(article, title)
    print(f"post {out.relative_to(ROOT)}")
    if not args.skip_build:
        from build_site import main as build_main

        return build_main()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
