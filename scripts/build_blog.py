#!/usr/bin/env python3
"""Build the blog: convert notebooks/*.ipynb into styled HTML pages in blog/.

Notebook conventions (inherited from the old fastpages blog):
  - Filename: YYYY-MM-DD-slug.ipynb  (date of posting)
  - First markdown cell holds front matter:
        # Title
        > Description
        - categories: [a, b, c]
        - author: ...            (optional)
  - Cells whose source starts with "#hide" are dropped entirely.

Usage:  python scripts/build_blog.py   (run from the repo root, via build_blog.sh)
"""

import json
import re
import shutil
import unicodedata
from datetime import datetime
from pathlib import Path

import nbformat
from nbconvert import HTMLExporter

ROOT = Path(__file__).resolve().parent.parent
NOTEBOOKS = ROOT / "notebooks"
OUT = ROOT / "blog"
SITE_TITLE = "Ruben Esteche"
IMAGE_DIRS = ["posts_images", "fastcore_imgs", "ghtop_images", "my_icons"]

FILENAME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-(.+)\.ipynb$")


# ──────────────────────────────────────────────────────────────
# Front matter parsing
# ──────────────────────────────────────────────────────────────

def strip_quotes(text: str) -> str:
    text = text.strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        text = text[1:-1]
    return text.strip()


def parse_front_matter(cell_source: str) -> dict:
    """Parse the fastpages-style first markdown cell."""
    meta = {"title": None, "description": "", "categories": []}
    for line in cell_source.splitlines():
        line = line.strip()
        if line.startswith("# ") and meta["title"] is None:
            meta["title"] = strip_quotes(line[2:])
        elif line.startswith("> ") and not meta["description"]:
            meta["description"] = strip_quotes(line[2:])
        elif line.startswith("-"):
            m = re.match(r"-\s*categories\s*:\s*\[(.*)\]", line)
            if m:
                meta["categories"] = [c.strip() for c in m.group(1).split(",") if c.strip()]
    return meta


def slugify(name: str) -> str:
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    name = re.sub(r"[^a-zA-Z0-9]+", "-", name).strip("-").lower()
    return name


def reading_time(nb) -> int:
    words = 0
    for cell in nb.cells:
        words += len(cell.source.split())
    return max(1, round(words / 220))


# ──────────────────────────────────────────────────────────────
# HTML shells
# ──────────────────────────────────────────────────────────────

def page_shell(*, title, description, canonical_path, content, extra_head="") -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} — {SITE_TITLE}</title>
  <meta name="description" content="{description}">
  <link rel="canonical" href="https://resteche.github.io{canonical_path}">
  <link rel="icon" type="image/svg+xml" href="/assets/img/favicon.svg">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:ital,wght@0,400;0,500;0,700;1,400&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/assets/css/style.css">
  <link rel="stylesheet" href="/assets/css/blog.css">
{extra_head}</head>
<body class="blog-body">
  <header class="nav is-scrolled" id="nav">
    <div class="nav__inner">
      <a class="nav__logo" href="/" aria-label="Home">
        <span class="nav__logo-mark">RE</span>
        <span class="nav__logo-text">ruben<span class="accent">.</span>esteche</span>
      </a>
      <nav class="nav__links nav__links--static" aria-label="Primary">
        <a href="/#about">About</a>
        <a href="/#experience">Experience</a>
        <a href="/#projects">Projects</a>
        <a href="/blog/" class="is-active">Blog</a>
        <a href="/#contact" class="nav__cta">Contact</a>
      </nav>
    </div>
  </header>

  <main class="blog-main">
{content}
  </main>

  <footer class="footer">
    <div class="container footer__inner">
      <p class="footer__sig"><span class="prompt">$</span> echo "designed &amp; engineered by Ruben Esteche"</p>
      <ul class="footer__links">
        <li><a href="/">Home</a></li>
        <li><a href="/blog/">Blog</a></li>
        <li><a href="https://github.com/REsteche" target="_blank" rel="noopener">GitHub</a></li>
        <li><a href="https://www.linkedin.com/in/rubenesteche/" target="_blank" rel="noopener">LinkedIn</a></li>
      </ul>
    </div>
  </footer>
</body>
</html>
"""


MATHJAX_HEAD = """  <script>
    window.MathJax = {
      tex: {
        inlineMath: [["$", "$"], ["\\\\(", "\\\\)"]],
        displayMath: [["$$", "$$"], ["\\\\[", "\\\\]"]],
        processEscapes: true
      },
      options: { skipHtmlTags: ["script", "noscript", "style", "textarea", "pre"] }
    };
  </script>
  <script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>
"""


def build_post_html(meta, date, minutes, body) -> str:
    cats = "".join(f"<li>{c}</li>" for c in meta["categories"])
    tags_html = f'<ul class="tags post__tags">{cats}</ul>' if cats else ""
    content = f"""    <article class="post container">
      <header class="post__header">
        <a class="post__back" href="/blog/">← All posts</a>
        <h1 class="post__title">{meta["title"]}</h1>
        <p class="post__meta">
          <time datetime="{date.isoformat()}">{date.strftime("%b %-d, %Y")}</time>
          <span class="post__dot">·</span> {minutes} min read
        </p>
        {tags_html}
      </header>
      <div class="post__content">
{body}
      </div>
      <footer class="post__footer">
        <a class="btn btn--ghost" href="/blog/">← Back to all posts</a>
      </footer>
    </article>
"""
    return page_shell(
        title=meta["title"],
        description=meta["description"].replace('"', "&quot;"),
        canonical_path=f"/blog/{meta['slug']}.html",
        content=content,
        extra_head=MATHJAX_HEAD,
    )


def build_index_html(posts) -> str:
    cards = []
    for p in posts:
        cats = "".join(f"<li>{c}</li>" for c in p["categories"][:4])
        tags_html = f'<ul class="tags">{cats}</ul>' if cats else ""
        cards.append(f"""        <a class="post-card" href="/blog/{p["slug"]}.html">
          <time class="post-card__date" datetime="{p["date"].isoformat()}">{p["date"].strftime("%b %-d, %Y")}</time>
          <h2>{p["title"]}</h2>
          <p>{p["description"]}</p>
          {tags_html}
          <span class="post-card__more">Read post →</span>
        </a>""")
    cards_html = "\n".join(cards)
    content = f"""    <section class="container blog-index">
      <header class="blog-index__header">
        <p class="section__index">blog</p>
        <h1 class="section__title">Lab <span class="gradient-text">notebook</span></h1>
        <p class="section__lead">Physics, machine learning and programming — long-form posts written as executable Jupyter notebooks.</p>
      </header>
      <div class="blog-index__grid">
{cards_html}
      </div>
    </section>
"""
    return page_shell(
        title="Blog",
        description="Posts on physics, machine learning, and programming by Ruben Esteche.",
        canonical_path="/blog/",
        content=content,
    )


# ──────────────────────────────────────────────────────────────
# Conversion
# ──────────────────────────────────────────────────────────────

def clean_notebook(nb):
    """Drop the front-matter cell and any fastpages #hide cells."""
    cells = []
    for i, cell in enumerate(nb.cells):
        if i == 0 and cell.cell_type == "markdown":
            continue  # front matter
        first_line = cell.source.lstrip().splitlines()[0].strip() if cell.source.strip() else ""
        if first_line in ("#hide", "# hide"):
            continue
        cells.append(cell)
    nb.cells = cells
    return nb


def main():
    exporter = HTMLExporter(template_name="basic")
    exporter.exclude_anchor_links = True

    OUT.mkdir(exist_ok=True)

    posts = []
    for path in sorted(NOTEBOOKS.glob("*.ipynb")):
        m = FILENAME_RE.match(path.name)
        if not m:
            print(f"  !! skipping {path.name} (name must be YYYY-MM-DD-slug.ipynb)")
            continue
        date = datetime.strptime(m.group(1), "%Y-%m-%d").date()
        slug = slugify(m.group(2))

        nb = nbformat.read(path, as_version=4)
        meta = parse_front_matter(nb.cells[0].source) if nb.cells else {}
        if not meta.get("title"):
            meta["title"] = m.group(2).replace("_", " ").replace("-", " ")
        meta["slug"] = slug
        minutes = reading_time(nb)

        nb = clean_notebook(nb)
        body, _ = exporter.from_notebook_node(nb)

        (OUT / f"{slug}.html").write_text(
            build_post_html(meta, date, minutes, body), encoding="utf-8"
        )
        posts.append({**meta, "date": date, "minutes": minutes})
        print(f"  ✓ {date}  {meta['title']}  →  blog/{slug}.html")

    posts.sort(key=lambda p: p["date"], reverse=True)
    (OUT / "index.html").write_text(build_index_html(posts), encoding="utf-8")
    print(f"  ✓ index  →  blog/index.html  ({len(posts)} posts)")

    # Copy image folders referenced with relative paths inside notebooks.
    for d in IMAGE_DIRS:
        src = NOTEBOOKS / d
        if src.is_dir():
            shutil.copytree(src, OUT / d, dirs_exist_ok=True)
    print("  ✓ images copied")


if __name__ == "__main__":
    main()
