#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from deepseek_to_post import load_chats, parse_markdown_transcript, slugify  # noqa: E402


def test_markdown_example() -> None:
    path = ROOT / "_inbox" / "example-chat.md"
    chats = load_chats(path)
    assert len(chats) == 1
    title, msgs = chats[0]
    assert title
    roles = [m["role"] for m in msgs]
    assert roles.count("user") >= 2
    assert roles.count("assistant") >= 2
    assert any("nojekyll" in m["content"] for m in msgs)


def test_prefixed_transcript() -> None:
    msgs = parse_markdown_transcript("User: привет\nAssistant: ок\n")
    assert msgs == [
        {"role": "user", "content": "привет"},
        {"role": "assistant", "content": "ок"},
    ]


def test_mapping_export() -> None:
    payload = [
        {
            "title": "Про 404",
            "mapping": {
                "a": {
                    "id": "a",
                    "parent": None,
                    "children": ["b"],
                    "message": {"author": {"role": "user"}, "content": {"parts": ["вопрос"]}},
                },
                "b": {
                    "id": "b",
                    "parent": "a",
                    "children": [],
                    "message": {"author": {"role": "assistant"}, "content": {"parts": ["ответ"]}},
                },
            },
        }
    ]
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as fh:
        json.dump(payload, fh)
        tmp = Path(fh.name)
    try:
        chats = load_chats(tmp)
    finally:
        tmp.unlink(missing_ok=True)
    assert chats[0][0] == "Про 404"
    assert [m["role"] for m in chats[0][1]] == ["user", "assistant"]
    assert chats[0][1][0]["content"] == "вопрос"


def test_slugify() -> None:
    assert slugify("Статьи из DeepSeek") == "stati-iz-deepseek"


def main() -> int:
    test_markdown_example()
    test_prefixed_transcript()
    test_mapping_export()
    test_slugify()
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
