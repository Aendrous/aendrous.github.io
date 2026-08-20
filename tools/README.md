# Tools

## Почему не Jekyll на GitHub

В корне репозитория `.nojekyll`: иначе Pages пропускает JSON/Yarn/OGG ClubOfSisters через Jekyll и каталог новелл ловит 404. Без Jekyll корень ищет `index.html`, поэтому блог собирается скриптом.

```bash
python3 -m pip install markdown
python3 tools/build_site.py
```

## Статьи из чатов DeepSeek

См. `_inbox/README.md` и `/projects/deepseek-articles/`.

```bash
python3 tools/deepseek_to_post.py --list _inbox/conversations.json
python3 tools/deepseek_to_post.py _inbox/example-chat.md --format-only --title "Черновик"
python3 tools/test_chat_parse.py
```
