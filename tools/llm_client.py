#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Клиенты LLM: DeepSeek (основной) и GigaChat (как в ClubOfSisters).

Ключи только из окружения / .env — никогда не пишем их в git или в Pages.
"""
from __future__ import annotations

import json
import os
import ssl
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def load_env(path: Path | None = None) -> None:
    env_path = path or (ROOT / ".env")
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        os.environ.setdefault(key.strip(), val.strip().strip("'").strip('"'))


def _http_json(
    url: str,
    payload: dict[str, Any] | None,
    headers: dict[str, str],
    *,
    insecure: bool = False,
    method: str = "POST",
    form: bytes | None = None,
) -> dict[str, Any]:
    data = form
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json", **headers}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    ctx = ssl._create_unverified_context() if insecure else ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=180) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} {url}: {body[:800]}") from exc
    return json.loads(raw) if raw else {}


def _content_from_message(message: dict[str, Any]) -> str:
    content = message.get("content")
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text") or item.get("content") or ""
                if text:
                    parts.append(str(text))
        return "\n".join(parts).strip()
    return str(content or "").strip()


class DeepSeekClient:
    def __init__(self) -> None:
        load_env()
        self.api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
        self.model = os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-flash").strip()
        self.base = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/")

    def available(self) -> bool:
        return bool(self.api_key)

    def chat(self, messages: list[dict[str, str]], *, temperature: float = 0.7) -> str:
        if not self.api_key:
            raise RuntimeError("Нет DEEPSEEK_API_KEY. Скопируйте .env.example → .env")
        url = f"{self.base}/chat/completions"
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": False,
        }
        # V4: thinking можно выключить для предсказуемого markdown.
        if self.model.startswith("deepseek-v4"):
            payload["thinking"] = {"type": "disabled"}
        data = _http_json(
            url,
            payload,
            {"Authorization": f"Bearer {self.api_key}"},
        )
        try:
            return _content_from_message(data["choices"][0]["message"])
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"Неожиданный ответ DeepSeek: {str(data)[:500]}") from exc


class GigaChatClient:
    """OAuth Basic → chat/completions, как в ClubOfSisters / lk-partner-assistant-demo."""

    OAUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    CHAT_URL = "https://api.giga.chat/v1/chat/completions"

    def __init__(self) -> None:
        load_env()
        self.auth_key = (
            os.environ.get("GIGACHAT_AUTHORIZATION_KEY")
            or os.environ.get("GIGACHAT_AUTH_KEY")
            or os.environ.get("GIGACHAT_API_KEY")
            or ""
        ).strip()
        self.scope = os.environ.get("GIGACHAT_SCOPE", "GIGACHAT_API_PERS").strip()
        self.model = os.environ.get("GIGACHAT_MODEL", "GigaChat-3-Ultra").strip()
        self._token: str | None = None

    def available(self) -> bool:
        return bool(self.auth_key)

    def _token_value(self) -> str:
        if self._token:
            return self._token
        data = _http_json(
            self.OAUTH_URL,
            None,
            {
                "Authorization": f"Basic {self.auth_key}",
                "RqUID": str(uuid.uuid4()),
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            },
            insecure=True,
            form=f"scope={self.scope}".encode("utf-8"),
        )
        token = data.get("access_token")
        if not token:
            raise RuntimeError(f"GigaChat OAuth не вернул token: {str(data)[:400]}")
        self._token = str(token)
        return self._token

    def chat(self, messages: list[dict[str, str]], *, temperature: float = 0.7) -> str:
        if not self.auth_key:
            raise RuntimeError("Нет GIGACHAT_AUTHORIZATION_KEY")
        data = _http_json(
            self.CHAT_URL,
            {"model": self.model, "messages": messages, "temperature": temperature},
            {"Authorization": f"Bearer {self._token_value()}", "Accept": "application/json"},
            insecure=True,
        )
        try:
            return _content_from_message(data["choices"][0]["message"])
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"Неожиданный ответ GigaChat: {str(data)[:500]}") from exc


def complete(messages: list[dict[str, str]], *, prefer: str = "deepseek") -> str:
    """prefer: deepseek | gigachat | auto."""
    load_env()
    ds = DeepSeekClient()
    gc = GigaChatClient()
    order = ["deepseek", "gigachat"] if prefer != "gigachat" else ["gigachat", "deepseek"]
    if prefer == "auto":
        order = ["deepseek", "gigachat"]
    errors: list[str] = []
    for name in order:
        client = ds if name == "deepseek" else gc
        if not client.available():
            continue
        try:
            return client.chat(messages)
        except Exception as exc:  # noqa: BLE001 — показать пользователю, попробовать запасной
            errors.append(f"{name}: {exc}")
    if not ds.available() and not gc.available():
        raise RuntimeError(
            "Нет ключа API. Создайте .env из .env.example "
            "(DEEPSEEK_API_KEY с platform.deepseek.com или GIGACHAT_AUTHORIZATION_KEY)."
        )
    raise RuntimeError("LLM не ответил. " + " | ".join(errors))
