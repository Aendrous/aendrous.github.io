---
layout: default
title: "WriterManager — менеджер писателя"
permalink: /projects/writer-manager/
---

На этом сайте рядом с CDN **ClubOfSisters** появилась папка проекта **WriterManager**.

Там же подход, что у Хранителя историй и демо на GigaChat: `prompt.md` + корпус знаний + каталог + CLI. Роль другая — **личный менеджер по развитию Андрея Фетисова как писателя**.

## Что в зоне ответственности

- эссе блога о прочитанных книгах и расследованиях;
- анонсы и связки **роман ↔ новелла ↔ ЛитМир**;
- очередь по ClubOfSisters и Story Keeper;
- сборка статей из экспорта чатов DeepSeek/GigaChat.

## Флагманский текст

**«Бутон сакуры: Тайцзи в ритме хастла»** — свой роман (около 20 глав), уже в игре как `buton_sakury`, линия публикации для ЛитМир.

## Команды

```bash
python3 WriterManager/manager.py "Собери план анонса Бутона сакуры"
python3 WriterManager/publish_from_chat.py _inbox/conversations.json --index 0 --prefer gigachat
python3 tools/build_site.py
```

Ключ GigaChat — тот же, что вшит в Story Keeper ClubOfSisters; лежит только в корневом `.env`, не в git и не в Pages.

Витрина: [/WriterManager/](/WriterManager/) · каталог: [/WriterManager/catalog.json](/WriterManager/catalog.json)
