# Inbox для экспорта чатов DeepSeek

API DeepSeek **не читает** историю с [chat.deepseek.com](https://chat.deepseek.com).
Он только генерирует новые ответы. Чтобы сделать статью из уже состоявшейся
переписки:

1. В веб-чате DeepSeek: профиль → Settings → Data / Privacy → **Export data**
   (или скопируйте диалог в markdown).
2. Положите файл сюда: `conversations.json`, `.md` или `.txt`.
3. JSON и zip **не коммитятся** (см. `.gitignore`) — в чатах бывают личные данные.
4. Дальше:

```bash
cp .env.example .env   # вписать DEEPSEEK_API_KEY с https://platform.deepseek.com/api_keys

python3 _writer/publish_from_chat.py --list _inbox/conversations.json
python3 _writer/publish_from_chat.py _inbox/conversations.json --index 0 --prefer gigachat
# без ключа — только расшифровка:
python3 tools/deepseek_to_post.py _inbox/example-chat.md --format-only --title "Черновик"
```

Готовый пост попадёт в `_posts/`, скрипт сразу пересоберёт `index.html`. Это локальный конвейер, не страница сайта.

Запасной ключ — GigaChat (как в ClubOfSisters / Хранителе): `GIGACHAT_AUTHORIZATION_KEY` в `.env`.
