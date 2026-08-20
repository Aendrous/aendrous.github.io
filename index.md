---
layout: default
title: Главная
---

# Айтишник о книгах

Публикации о расследованиях, элитах, книгах и скрытых смыслах. Плюс свои романы, новеллы для игры и живой Android-проект.

## WriterManager

Личный менеджер развития писателя (подход ClubOfSisters: prompt + корпус + каталог + CLI).

- **[Как работает роль](/projects/writer-manager/)**
- [Витрина `/WriterManager/`](/WriterManager/)
- [«Бутон сакуры» — роман ↔ ClubOfSisters ↔ ЛитМир](/2026/08/20/buton-sakury-roman-dlya-litmir-i-igry/)

## Проект: ClubOfSisters

Русскоязычная визуальная новелла для Android и **Хранитель историй** (продолжение канона с ИИ на телефоне).

- **[Веха проекта — что сделано и что дальше](/projects/clubofsisters/)**
- [Скачать APK](https://github.com/Aendrous/ClubOfSisters-releases/releases/latest)
- [CDN каталога новелл](/ClubOfSisters/)
- [Ранний анонс Хранителя](/2026/07/25/clubofsisters-story-keeper/)

## Статьи из переписки

Черновик собирается из экспорта чата (API не читает историю web-чата). Ключ только в `.env`, не в git.

- [Как положить чат и получить пост](/projects/deepseek-articles/)
- [Почему главная отдавала 404](/2026/08/20/stati-iz-perepiski-deepseek/)

## Последние статьи

{% for post in site.posts limit:8 %}
- [{{ post.title }}]({{ post.url }}) — {{ post.date | date: "%d.%m.%Y" }}
{% endfor %}
