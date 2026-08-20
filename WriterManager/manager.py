#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CLI личного менеджера писателя (как chat.py в ClubOfSisters/demo ЛК).

  python3 WriterManager/manager.py "План анонса Бутона сакуры"
  python3 WriterManager/manager.py --repl
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "tools"))

from llm_client import complete, load_env  # noqa: E402

PROMPT_PATH = HERE / "prompt.md"
CORPUS_PATH = HERE / "knowledge" / "corpus.md"
CATALOG_PATH = HERE / "catalog.json"

ALWAYS = ("W-00", "W-01", "W-05")


def load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8").strip()


def split_sections(corpus: str) -> list[tuple[str, str]]:
    parts = re.split(r"\n---+\n", corpus)
    out: list[tuple[str, str]] = []
    for part in parts:
        text = part.strip()
        if not text:
            continue
        title = text.splitlines()[0].lstrip("# ").strip()[:80]
        out.append((title, text))
    return out


def retrieve(question: str, k: int = 4) -> str:
    corpus = CORPUS_PATH.read_text(encoding="utf-8") if CORPUS_PATH.exists() else ""
    sections = split_sections(corpus)
    if not sections:
        return corpus
    q = question.lower()
    tokens = set(re.findall(r"[а-яёa-z0-9]{3,}", q))
    scored: list[tuple[float, str]] = []
    for title, body in sections:
        blob = (title + "\n" + body).lower()
        score = sum(2.0 if t in title.lower() else 1.0 for t in tokens if t in blob)
        if any(tag.lower() in title.lower() for tag in ALWAYS):
            score += 0.8
        scored.append((score, body))
    scored.sort(key=lambda x: x[0], reverse=True)
    picked = [body for score, body in scored if score > 0][:k]
    if not picked:
        picked = [body for _, body in scored[:3]]
    catalog = ""
    if CATALOG_PATH.exists():
        catalog = "\n\n### catalog.json\n" + CATALOG_PATH.read_text(encoding="utf-8")[:4000]
    return "\n\n---\n\n".join(picked) + catalog


def system_prompt(question: str) -> str:
    return (
        load_prompt()
        + "\n\n# Контекст из корпуса\n\n"
        + retrieve(question)
    )


def ask(question: str, prefer: str = "gigachat", temperature: float = 0.35) -> str:
    load_env(ROOT / ".env")
    return complete(
        [
            {"role": "system", "content": system_prompt(question)},
            {"role": "user", "content": question},
        ],
        prefer=prefer,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="WriterManager — менеджер писателя Aendrous")
    parser.add_argument("question", nargs="?", help="Вопрос или задача")
    parser.add_argument("--repl", action="store_true")
    parser.add_argument("--prefer", choices=("gigachat", "deepseek", "auto"), default="gigachat")
    parser.add_argument("--temperature", type=float, default=0.35)
    args = parser.parse_args()
    load_env(ROOT / ".env")
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    if args.repl or not args.question:
        print("WriterManager (личный менеджер писателя). Пустая строка — выход.")
        while True:
            try:
                q = input("Aendrous> ").strip()
            except EOFError:
                break
            if not q:
                break
            print(ask(q, prefer=args.prefer, temperature=args.temperature))
            print()
        return 0

    print(ask(args.question, prefer=args.prefer, temperature=args.temperature))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
