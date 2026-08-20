# WriterManager — личный менеджер развития писателя

Папка проекта для сайта [`aendrous.github.io`](https://aendrous.github.io/).  
Роль ИИ: **личный менеджер по развитию Андрея Фетисова (Aendrous) как писателя**.

Подход взят из ClubOfSisters / Хранителя историй / демо ЛК:

| ClubOfSisters | WriterManager |
|---|---|
| Content packs + `stories_catalog.json` | `catalog.json` — книги, новеллы, проекты |
| Yarn → сцена на телефоне | Черновик → `_posts/` → GitHub Pages |
| GigaChat в APK | Тот же ключ локально в корневом `.env` (не в git) |
| `prompt.md` + корпус инструкций | `prompt.md` + `knowledge/corpus.md` |
| CLI / Story Keeper | `python WriterManager/manager.py` |

## Что ведёт менеджер

1. **Эссе и расследования** блога (книги, элиты, мистика).
2. **Проекты**: ClubOfSisters, Story Keeper, CDN новелл.
3. **Свои романы и новеллы** — в первую очередь «Бутон сакуры: Тайцзи в ритме хастла» (ЛитМир / игра).
4. **Прочитанное** → карточка в корпусе → заготовка статьи.
5. **Переписка DeepSeek/GigaChat** → пост через `tools/deepseek_to_post.py`.

## Быстрый старт

Ключ уже может лежать в корневом `.env` (из Story Keeper ClubOfSisters). Не коммитить.

```bash
# Диалог с менеджером
python3 WriterManager/manager.py --repl
python3 WriterManager/manager.py "Собери план анонса Бутона сакуры для блога"

# Статья из экспорта чата (роль писателя)
python3 WriterManager/publish_from_chat.py _inbox/example-chat.md --format-only
python3 WriterManager/publish_from_chat.py _inbox/conversations.json --index 0 --prefer gigachat

# Пересборка сайта
python3 tools/build_site.py
```

Публичная витрина: https://aendrous.github.io/WriterManager/
