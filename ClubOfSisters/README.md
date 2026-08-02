# ClubOfSisters — CDN на GitHub Pages

Контент публикуется в репозиторий **user site** [`Aendrous/aendrous.github.io`](https://github.com/Aendrous/aendrous.github.io) в папку `ClubOfSisters/` (не через Pages самого игрового репо).

**Каталог:** https://aendrous.github.io/ClubOfSisters/stories/stories_catalog.json  
**Контент:** https://aendrous.github.io/ClubOfSisters/content/{novelId}/manifest.json  
**Индекс:** https://aendrous.github.io/ClubOfSisters/

Локальный источник в игровом репо: `docs/ClubOfSisters/` → копировать/публиковать в `aendrous.github.io/ClubOfSisters/`.

Полный контракт: [docs/REMOTE_CONTENT.md](../../REMOTE_CONTENT.md).

## Почему был 404

Сайт `aendrous.github.io` — отдельный репозиторий. Папки `/ClubOfSisters/` там не было, а в `main` игрового репо не было опубликованного `docs/` для project Pages.

## Обновление CDN

```bash
python tools/publish_content_pack.py --novel veter --update-catalog
# затем скопировать docs/ClubOfSisters → aendrous.github.io/ClubOfSisters и push
```

В `aendrous.github.io` лежит `.nojekyll`, чтобы JSON/OGG/PNG отдавались без Jekyll.
