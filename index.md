---
layout: default
title: Главная
---

# Айтишник о книгах

Скоро здесь будут публикации о расследованиях, элитах и скрытых смыслах.

## ClubOfSisters

Мобильная визуальная новелла: [скачать APK](https://github.com/Aendrous/ClubOfSisters-releases/releases/latest) · [Хранитель историй](/2026/07/25/clubofsisters-story-keeper/)

## Последние статьи

{% for post in site.posts limit:5 %}
- [{{ post.title }}]({{ post.url }}) — {{ post.date | date: "%d.%m.%Y" }}
{% endfor %}
