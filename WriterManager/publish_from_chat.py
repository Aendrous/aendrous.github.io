#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Обёртка tools/deepseek_to_post.py с ролью WriterManager.

  python3 WriterManager/publish_from_chat.py _inbox/example-chat.md --format-only
  python3 WriterManager/publish_from_chat.py _inbox/conversations.json --index 0 --prefer gigachat
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "tools"))

from deepseek_to_post import (  # noqa: E402
    build_article,
    format_only_article,
    load_chats,
    write_post,
)
from llm_client import complete, load_env  # noqa: E402

PROMPT = (HERE / "prompt.md").read_text(encoding="utf-8")
CORPUS_HEAD = (HERE / "knowledge" / "corpus.md").read_text(encoding="utf-8")[:6000]


def build_writer_article(title: str, msgs: list, prefer: str) -> str:
    today = dt.date.today().isoformat()
    from deepseek_to_post import transcript

    system = f"""{PROMPT}

Дополнительно: верни ТОЛЬКО markdown статьи для aendrous.github.io:

---
title: "Заголовок"
date: {today}
author: "Андрей Фетисов"
categories: [писательство, проекты]
tags: [aendrous, writer-manager]
---

# Заголовок

Текст.

Фрагмент корпуса:
{CORPUS_HEAD}
"""
    user = (
        f"Заголовок-подсказка: {title}\n\n"
        f"Переписка / сырьё:\n\n{transcript(msgs)}\n\n"
        f"Собери статью для блога писателя (проекты, книги, новеллы)."
    )
    return complete(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        prefer=prefer,
    )


def main() -> int:
    load_env(ROOT / ".env")
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("--index", type=int, default=0)
    parser.add_argument("--title", default="")
    parser.add_argument("--format-only", action="store_true")
    parser.add_argument("--prefer", choices=("gigachat", "deepseek", "auto"), default="gigachat")
    parser.add_argument("--skip-build", action="store_true")
    parser.add_argument("--list", dest="list_only", action="store_true")
    args = parser.parse_args()

    path = Path(args.source)
    if not path.is_absolute():
        path = (ROOT / path).resolve()
    chats = load_chats(path)
    if args.list_only:
        for i, (title, msgs) in enumerate(chats):
            print(f"{i:3d}  {title}  ({len(msgs)} сообщ.)")
        return 0
    title, msgs = chats[args.index]
    title = args.title or title
    if args.format_only:
        article = format_only_article(title, msgs)
    else:
        try:
            article = build_writer_article(title, msgs, args.prefer)
        except Exception:
            # запасной путь — общий пайплайн
            article = build_article(title, msgs, args.prefer)
    out = write_post(article, title)
    print(f"post {out.relative_to(ROOT)}")
    if not args.skip_build:
        from build_site import main as build_main

        return build_main()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
