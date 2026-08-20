#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Сборка статического HTML для GitHub Pages без Jekyll.

На aendrous.github.io лежит `.nojekyll`, иначе Jekyll ломает CDN ClubOfSisters
(JSON/OGG/Yarn) и корень сайта отдаёт 404: нет index.html, только index.md.

Запуск из корня репозитория:

    python3 tools/build_site.py
"""
from __future__ import annotations

import datetime as dt
import html
import re
import sys
from pathlib import Path

try:
    import markdown
except ImportError:
    sys.stderr.write("Нужен пакет markdown: python3 -m pip install markdown\n")
    raise

ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "_posts"
PROJECTS_DIR = ROOT / "projects"
INCLUDES = ROOT / "_includes"
CONFIG = ROOT / "_config.yml"

MD = markdown.Markdown(
    extensions=["tables", "fenced_code", "sane_lists", "nl2br", "smarty"],
    output_format="html5",
)

SITE_TITLE = "Айтишник хочет пофилосовствовать"
SITE_TAGLINE = "Исследования о книгах, тайных обществах и скрытых смыслах"
SITE_AUTHOR = "Андрей Фетисов"


def load_config() -> dict[str, str]:
    data: dict[str, str] = {}
    if not CONFIG.exists():
        return data
    for line in CONFIG.read_text(encoding="utf-8").splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        key, val = line.split(":", 1)
        data[key.strip()] = val.strip().strip('"').strip("'")
    return data


def parse_front_matter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    meta: dict[str, str] = {}
    for raw in parts[1].splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, val = line.split(":", 1)
        meta[key.strip()] = val.strip().strip('"').strip("'")
    return meta, parts[2].lstrip("\n")


def parse_date(raw: str | None, fallback_name: str) -> dt.date:
    if raw:
        raw = raw.strip()
        for fmt in ("%Y-%m-%d %H:%M:%S %z", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                parsed = dt.datetime.strptime(raw.replace("+0300", "+03:00"), fmt)
                return parsed.date()
            except ValueError:
                continue
        m = re.match(r"(\d{4}-\d{2}-\d{2})", raw)
        if m:
            return dt.date.fromisoformat(m.group(1))
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", fallback_name)
    if m:
        return dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return dt.date.today()


def slug_from_filename(name: str) -> str:
    return re.sub(r"^\d{4}-\d{2}-\d{2}-", "", name).rsplit(".", 1)[0]


def permalink_for(meta: dict[str, str], date: dt.date, slug: str) -> str:
    explicit = meta.get("permalink", "").strip()
    if explicit and ":year" not in explicit and ":title" not in explicit:
        path = explicit
        if not path.endswith("/"):
            if path.endswith(".html"):
                return path if path.startswith("/") else "/" + path
            path += "/"
        return path if path.startswith("/") else "/" + path
    suffix_html = explicit.endswith(".html") if explicit else False
    if suffix_html:
        return f"/{date:%Y}/{date:%m}/{date:%d}/{slug}.html"
    return f"/{date:%Y}/{date:%m}/{date:%d}/{slug}/"


def dest_for_permalink(permalink: str) -> Path:
    rel = permalink.lstrip("/")
    if rel.endswith(".html"):
        return ROOT / rel
    return ROOT / rel / "index.html"


def md_to_html(source: str) -> str:
    MD.reset()
    body = MD.convert(source)
    # Таблицы на узком экране
    body = body.replace("<table>", '<div class="table-wrap"><table>').replace(
        "</table>", "</table></div>"
    )
    return body


def comments_html() -> str:
    path = INCLUDES / "comments.html"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def page_shell(title: str, inner: str, description: str | None = None) -> str:
    cfg = load_config()
    site_title = cfg.get("title", SITE_TITLE)
    tagline = cfg.get("description", SITE_TAGLINE)
    desc = description or tagline
    full_title = title if title == site_title else f"{title} · {site_title}"
    comments = ""  # comments only on posts
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(full_title)}</title>
  <meta name="description" content="{html.escape(desc)}" />
  <meta name="author" content="{html.escape(SITE_AUTHOR)}" />
  <link rel="stylesheet" href="/assets/css/site.css" />
</head>
<body>
  <header class="site-header">
    <div class="container">
      <h1><a href="/" id="a-title">{html.escape(site_title)}</a></h1>
      <p class="tagline">{html.escape(tagline)}</p>
      <nav class="site-nav">
        <a href="/">Статьи</a>
        <a href="/projects/clubofsisters/">ClubOfSisters</a>
        <a href="/projects/deepseek-articles/">Статьи из DeepSeek</a>
        <a href="/ClubOfSisters/">CDN новелл</a>
        <a href="https://github.com/Aendrous/aendrous.github.io">GitHub</a>
      </nav>
    </div>
  </header>
  <div class="container" id="main_content">
{inner}
  </div>
  <footer class="site-footer">
    <div class="container">{html.escape(SITE_AUTHOR)} · GitHub Pages · без Jekyll, чтобы жил CDN ClubOfSisters</div>
  </footer>
{comments}
</body>
</html>
"""


def post_shell(title: str, inner: str, description: str | None = None) -> str:
    html_page = page_shell(title, inner, description)
    comments = comments_html()
    if comments:
        html_page = html_page.replace(
            "  </div>\n  <footer class=\"site-footer\">",
            f'    <div class="post-comments">\n{comments}\n    </div>\n  </div>\n  <footer class="site-footer">',
        )
    return html_page


class Post:
    def __init__(self, path: Path, meta: dict[str, str], body: str):
        self.path = path
        self.meta = meta
        self.body = body
        self.date = parse_date(meta.get("date"), path.name)
        self.slug = slug_from_filename(path.name)
        self.title = meta.get("title") or self.slug.replace("-", " ")
        self.permalink = permalink_for(meta, self.date, self.slug)
        self.categories = meta.get("categories", "")

    @property
    def excerpt(self) -> str:
        text = re.sub(r"[#>*`\\[]", "", self.body)
        text = re.sub(r"\]\([^)]+\)", "", text)
        text = " ".join(text.split())
        return text[:180] + ("…" if len(text) > 180 else "")


def load_posts() -> list[Post]:
    posts: list[Post] = []
    for path in sorted(POSTS_DIR.glob("*.md")):
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        posts.append(Post(path, meta, body))
    posts.sort(key=lambda p: (p.date, p.path.name), reverse=True)
    return posts


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def render_post(post: Post) -> None:
    body = md_to_html(post.body)
    date_s = post.date.strftime("%d.%m.%Y")
    inner = (
        f'<article class="post">\n'
        f"  <h1>{html.escape(post.title)}</h1>\n"
        f'  <p class="post-meta">{date_s}'
        f' · <a href="/">на главную</a></p>\n'
        f'  <div class="post-content">\n{body}\n  </div>\n'
        f"</article>\n"
    )
    write(dest_for_permalink(post.permalink), post_shell(post.title, inner, post.excerpt))


def render_index(posts: list[Post]) -> None:
    items = []
    for post in posts:
        items.append(
            f'<li><a href="{html.escape(post.permalink)}">{html.escape(post.title)}</a>'
            f' <span class="date">— {post.date.strftime("%d.%m.%Y")}</span></li>'
        )
    inner = f"""
<h1>Айтишник о книгах</h1>
<p>Публикации о расследованиях, элитах, книгах и скрытых смыслах. Плюс живой проект визуальной новеллы.</p>

<div class="project-box">
  <h2>Проект: ClubOfSisters</h2>
  <p>Русскоязычная визуальная новелла для Android и <strong>Хранитель историй</strong> (продолжение канона с ИИ на телефоне).</p>
  <ul>
    <li><a href="/projects/clubofsisters/"><strong>Веха проекта — что сделано и что дальше</strong></a></li>
    <li><a href="https://github.com/Aendrous/ClubOfSisters-releases/releases/latest">Скачать APK</a></li>
    <li><a href="/ClubOfSisters/">CDN каталога новелл</a></li>
  </ul>
</div>

<div class="project-box">
  <h2>Статьи из переписки DeepSeek</h2>
  <p>Черновик статьи собирается из экспорта чата. Ключ API не лежит в репозитории — только в <code>.env</code> или в секретах GitHub Actions.</p>
  <ul>
    <li><a href="/projects/deepseek-articles/">Как положить чат и получить пост</a></li>
    <li><a href="/2026/08/20/stati-iz-perepiski-deepseek/">Заметка о пайплайне и починке 404</a></li>
  </ul>
</div>

<h2>Последние статьи</h2>
<ul class="post-list">
{chr(10).join(items)}
</ul>
"""
    write(ROOT / "index.html", page_shell(SITE_TITLE, inner))


def render_project_page(md_path: Path) -> None:
    meta, body = parse_front_matter(md_path.read_text(encoding="utf-8"))
    title = meta.get("title") or md_path.stem
    permalink = meta.get("permalink") or f"/projects/{md_path.stem}/"
    if not permalink.endswith("/") and not permalink.endswith(".html"):
        permalink += "/"
    inner = f"<article>\n  <h1>{html.escape(title)}</h1>\n{md_to_html(body)}\n</article>\n"
    write(dest_for_permalink(permalink), page_shell(title, inner))


def render_404() -> None:
    inner = """
<h1>404 — страницы нет</h1>
<p>Корень сайта раньше отдавал 404, потому что GitHub Pages с <code>.nojekyll</code> ищет <code>index.html</code>, а Jekyll был выключен ради CDN ClubOfSisters.</p>
<ul>
  <li><a href="/">Главная со статьями</a></li>
  <li><a href="/projects/clubofsisters/">ClubOfSisters</a></li>
  <li><a href="/ClubOfSisters/">CDN новелл (JSON / Yarn)</a></li>
</ul>
"""
    write(ROOT / "404.html", page_shell("404", inner))


def main() -> int:
    if not POSTS_DIR.is_dir():
        sys.stderr.write("_posts/ не найден — запустите из корня репозитория\n")
        return 1
    posts = load_posts()
    written: set[Path] = set()
    for post in posts:
        dest = dest_for_permalink(post.permalink)
        render_post(post)
        written.add(dest.resolve())
    for md_path in sorted(PROJECTS_DIR.glob("*.md")):
        meta, _body = parse_front_matter(md_path.read_text(encoding="utf-8"))
        permalink = meta.get("permalink") or f"/projects/{md_path.stem}/"
        if not permalink.endswith("/") and not permalink.endswith(".html"):
            permalink += "/"
        dest = dest_for_permalink(permalink).resolve()
        if dest in written:
            print(f"skip {md_path.relative_to(ROOT)} (permalink already from _posts)")
            continue
        render_project_page(md_path)
    render_index(posts)
    render_404()
    print(f"ok: {len(posts)} posts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
