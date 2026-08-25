---
layout: post
title: "Почему aendrous.github.io отдавал 404 и как статьи рождаются из чатов DeepSeek"
date: 2026-08-20
author: "Андрей Фетисов"
categories: [meta, github-pages, deepseek]
tags: [github-pages, jekyll, deepseek, clubofsisters]
---

Две недели главная [aendrous.github.io](https://aendrous.github.io/) встречала 404, а каталог ClubOfSisters при этом открывался. Это не «пропал репозиторий» и не сломанный домен. Сломалась схема сборки.

## Что случилось

Сайт — user GitHub Pages: репозиторий `Aendrous/aendrous.github.io`, ветка `main`, корень. Блог задуман как Jekyll: `_posts/`, `index.md`, тема Hacker.

1 августа в корень положили пустой `.nojekyll`. Зачем: CDN визуальной новеллы (тогда `/ClubOfSisters/stories/stories_catalog.json`, Yarn, OGG, обложки) GitHub иначе прогоняет через Jekyll. Для игры это смерть: каталог ловил 404, пока папки не опубликовали «как файлы».

Побочный эффект: **Jekyll выключился целиком**. Pages без Jekyll ищет `index.html`. У блога был только `index.md`. Запрос на `/` → 404. `/ClubOfSisters/` жил, потому что там настоящий HTML.

Отдельно последняя официальная сборка Pages с 6 августа зависла в статусе `building` (коммит с фанфик-ридером). Живая копия CDN на тот момент оставалась от 2 августа.

## Что нельзя было сделать «по API DeepSeek»

Ключ API и переписка в веб-чате — разные двери. `https://api.deepseek.com/chat/completions` не отдаёт список диалогов с chat.deepseek.com. Зато по экспорту чата можно собрать эссе в голосе этого блога и сразу выложить его как страницу.

В CDN для телефона секретов нет — и не должно быть. Ключ DeepSeek создаётся на [platform.deepseek.com](https://platform.deepseek.com/api_keys) и живёт только в локальном `.env` (шаблон в корне репозитория). Запасной вариант — тот же GigaChat, что у Хранителя историй, тоже только локально.

## Как теперь устроен конвейер

1. Экспорт чата → `_inbox/` (JSON в git не попадает).
2. `python3 tools/deepseek_to_post.py _inbox/conversations.json --index 0`
3. Пост в `_posts/`; сайт снова собирает **Jekyll** на GitHub Pages (`.nojekyll` снят).
4. CDN новелл вынесен в отдельный репозиторий [ClubOfSisters-cdn](https://github.com/Aendrous/ClubOfSisters-cdn) → https://aendrous.github.io/ClubOfSisters-cdn/

Главная снова должна открываться через Jekyll. Если после пуша GitHub всё ещё крутит старый «building», в Settings → Pages достаточно сохранить источник `main / (root)` ещё раз — очередь сборок иногда залипает.
