---
layout: default
title: Главная
---

# Айтишник о книгах

Скоро здесь будут публикации о расследованиях, элитах и скрытых смыслах.

## Проект: ClubOfSisters

Русскоязычная визуальная новелла для Android и **Хранитель историй** (продолжение канона с GigaChat на телефоне).

- **[Веха проекта — что сделано и что дальше](/projects/clubofsisters/)**
- [Скачать APK](https://github.com/Aendrous/ClubOfSisters-releases/releases/latest)
- [Ранний анонс Хранителя](/2026/07/25/clubofsisters-story-keeper/)

## Последние статьи

{% for post in site.posts limit:8 %}
- [{{ post.title }}]({{ post.url }}) — {{ post.date | date: "%d.%m.%Y" }}
{% endfor %}
