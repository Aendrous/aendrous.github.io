# ClubOfSisters — GitHub Pages

Каталог новелл и **content packs** для Android-приложения.

**Каталог:** https://aendrous.github.io/ClubOfSisters/stories/stories_catalog.json  
**Контент:** https://aendrous.github.io/ClubOfSisters/content/{novelId}/manifest.json  

Полный контракт: [docs/REMOTE_CONTENT.md](../../REMOTE_CONTENT.md).

## Включение

1. Репозиторий → Settings → Pages
2. Source: Deploy from branch `main`
3. Folder: `/docs`
4. Сохранить

Файлы:
- `docs/ClubOfSisters/stories/stories_catalog.json`
- `docs/ClubOfSisters/content/{novelId}/` — packs (sprites, backgrounds, audio, covers, yarn)
- `docs/ClubOfSisters/covers/` — обложки (legacy)

Приложение загружает каталог (`RemoteStoryCatalogLoader`, `_useRemoteCatalog = true`) и перед стартом новеллы скачивает pack (`RemoteContentCache`).
