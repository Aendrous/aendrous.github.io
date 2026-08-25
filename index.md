---
layout: default
title: Главная
---

# Айтишник о книгах

Публикации о расследованиях, элитах, книгах и скрытых смыслах. Плюс свои романы, новеллы для игры и живой Android-проект.

## Прочитанное

Эссе и разборы чужих книг и историй.

{% assign reading = site.categories.прочитанное %}
{% if reading and reading.size > 0 %}
<ul>
{% for post in reading %}
  <li><a href="{{ post.url }}">{{ post.title }}</a> — {{ post.date | date: "%d.%m.%Y" }}</li>
{% endfor %}
</ul>
{% else %}
<p>Пока нет постов с категорией <code>прочитанное</code>.</p>
{% endif %}

## Романы и новеллы

- **[«Бутон сакуры» — роман ↔ ClubOfSisters ↔ ЛитМир](/2026/08/20/buton-sakury-roman-dlya-litmir-i-igry/)**
- [Главы новеллы в ClubOfSisters](https://aendrous.github.io/ClubOfSisters-cdn/content/buton_sakury/manifest.json)

## Проект: ClubOfSisters

Русскоязычная визуальная новелла для Android и **Хранитель историй** (продолжение канона с ИИ на телефоне).

- **[Веха проекта — что сделано и что дальше](/projects/clubofsisters/)**
- [Скачать APK](https://github.com/Aendrous/ClubOfSisters-releases/releases/latest)
- [CDN каталога новелл](https://aendrous.github.io/ClubOfSisters-cdn/)
- [Ранний анонс Хранителя](/2026/07/25/clubofsisters-story-keeper/)

## Остальное

{% for post in site.posts %}
{% unless post.categories contains "прочитанное" %}
- [{{ post.title }}]({{ post.url }}) — {{ post.date | date: "%d.%m.%Y" }}
{% endunless %}
{% endfor %}
