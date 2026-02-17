---
layout: default
title: Главная
---

# Айтишник о книгах

Скоро здесь будут публикации о расследованиях, элитах и скрытых смыслах.

## Последние статьи

{% for post in site.posts limit:5 %}
- [{{ post.title }}]({{ post.url }}) — {{ post.date | date: "%d.%m.%Y" }}
{% endfor %}
