---
layout: default
title: "Статьи из переписки DeepSeek"
permalink: /projects/deepseek-articles/
---

На GitHub Pages нет сервера, который мог бы сам ходить в ваш аккаунт DeepSeek. История с [chat.deepseek.com](https://chat.deepseek.com) через API **не скачивается**. API только пишет новые ответы.

Цепочка такая:

1. Экспорт чата (Settings → Data / Export) или копипаст в markdown.
2. Файл в `_inbox/` (JSON в git не попадает).
3. Ключ в локальном `.env` — шаблон `.env.example`. Ключ: [platform.deepseek.com/api_keys](https://platform.deepseek.com/api_keys).
4. Команда:

```bash
python3 -m pip install markdown
python3 tools/deepseek_to_post.py _inbox/conversations.json --index 0
```

Без ключа можно сохранить сырую расшифровку:

```bash
python3 tools/deepseek_to_post.py _inbox/example-chat.md --format-only
```

В репозитории **нет** рабочих секретов: в публичной папке `ClubOfSisters/` их тоже не оказалось (и не должно быть — это CDN для Android). Старый GigaChat из Хранителя историй можно подставить локально как запасной вариант: `GIGACHAT_AUTHORIZATION_KEY` и флаг `--prefer gigachat`.

После генерации пост появляется в `_posts/`, а `tools/build_site.py` пишет HTML. Это нужно, потому что на сайте включён `.nojekyll`: так живёт CDN новелл, но Jekyll больше не превращает `index.md` в главную страницу.
