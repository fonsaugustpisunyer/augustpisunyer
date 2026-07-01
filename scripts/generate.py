#!/usr/bin/env python3
"""
Regenerate the site's per-publication reader pages and sitemap.xml
from the single source of truth in data/papers.js.

Usage:
    python3 scripts/generate.py

Add or edit a paper by editing data/papers.js, then re-run this script.
Nothing here is hand-maintained per-paper, so links can never drift.
"""
import json
import re
import html
import datetime
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "papers.js"
DOMAIN = "https://www.augustpisunyer.com"


def load_papers():
    txt = DATA.read_text(encoding="utf-8")
    m = re.search(r"window\.PAPERS\s*=\s*(\[.*?\]);", txt, re.S)
    if not m:
        raise SystemExit("Could not find window.PAPERS array in data/papers.js")
    return json.loads(m.group(1))


def esc(s):
    return html.escape(s or "", quote=True)


def clean_venue(v):
    v = (v or "").strip()
    v = re.sub(r"^\(([^)]*)\)\.?\s*", "", v)   # drop leading "(Nota ...)."
    v = re.sub(r"\.\s*$", "", v)               # drop trailing period
    return v.strip()


HEADER = """  <header class="site-header">
    <div class="bar">
      <a class="brand" href="index.html"><span class="mark">August Pi-Sunyer</span><span class="dates">1879–1965</span></a>
      <nav class="site-nav" aria-label="Navegació principal">
        <a href="index.html">Inici</a>
        <a href="biography.html">Biografia</a>
        <a href="bibliography.html" aria-current="page">Bibliografia</a>
      </nav>
    </div>
  </header>"""

FOOTER = """  <footer class="site-footer">
    <div class="bar">
      <div>© <span data-year>2025</span> · Arxiu digital August Pi-Sunyer</div>
      <nav>
        <a href="index.html">Inici</a>
        <a href="biography.html">Biografia</a>
        <a href="bibliography.html">Bibliografia</a>
      </nav>
    </div>
  </footer>"""


def viewer(p):
    if p["available"]:
        return f'    <div class="pdf-frame">\n      <embed src="pdf/{esc(p["pdf"])}" type="application/pdf">\n    </div>'
    return (
        '    <div class="pdf-missing">\n'
        '      <strong>PDF no disponible</strong>\n'
        '      <span>Aquesta publicació encara no té el document digitalitzat.</span>\n'
        '    </div>'
    )


def actions(p):
    if not p["available"]:
        return ""
    pdf = esc(p["pdf"])
    return (
        f'<a class="btn btn-accent" href="pdf/{pdf}" target="_blank" rel="noopener">Obre el PDF ↗</a>'
        f'<a class="btn btn-ghost" href="pdf/{pdf}" download>Descarrega</a>'
    )


def nav_link(p, cls, label):
    if not p:
        return f'<a class="{cls} disabled" aria-hidden="true" tabindex="-1"></a>'
    return (
        f'<a class="{cls}" href="{esc(p["slug"])}.html">'
        f'<span class="dir">{label}</span>'
        f'<span>{esc(p["title"])}</span></a>'
    )


def render_paper(p, prev, nxt):
    authors = esc(p["authors"])
    venue = esc(clean_venue(p["venue"]))
    sep = ' · ' if authors and venue else ''
    cite = f'<span class="authors">{authors}</span>{sep}<span class="venue">{venue}</span>'
    return f"""<!DOCTYPE html>
<html lang="{esc(p.get('lang') or 'ca')}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(p['title'])} ({p['year']}) · August Pi-Sunyer</title>
  <meta name="description" content="{esc(p['citation'])}">
  <meta property="og:title" content="{esc(p['title'])} ({p['year']})">
  <meta property="og:description" content="{esc(p['citation'])}">
  <meta property="og:type" content="article">
  <link rel="icon" href="images/back2.png" type="image/png">
  <link rel="stylesheet" href="css/style.css">
</head>
<body>
  <a class="skip-link" href="#doc">Salta al document</a>
{HEADER}
  <main class="wrap reader" id="doc">
    <a class="backlink" href="bibliography.html">← Torna a la bibliografia</a>
    <div class="citation-block">
      <div class="yr">{p['year']}</div>
      <h1>{esc(p['title'])}</h1>
      <p class="cite">{cite}</p>
      <div class="doc-actions">{actions(p)}</div>
    </div>
{viewer(p)}
    <nav class="paper-nav" aria-label="Navegació entre publicacions">
      {nav_link(prev, 'prev', '← Anterior')}
      {nav_link(nxt, 'next', 'Següent →')}
    </nav>
  </main>
{FOOTER}
  <script src="js/site.js"></script>
</body>
</html>
"""


def write_sitemap(papers):
    today = datetime.date.today().isoformat()
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]

    def url(loc, pr):
        return (f'  <url>\n    <loc>{loc}</loc>\n'
                f'    <lastmod>{today}</lastmod>\n    <priority>{pr}</priority>\n  </url>')

    lines.append(url(f"{DOMAIN}/", "1.00"))
    lines.append(url(f"{DOMAIN}/biography.html", "0.80"))
    lines.append(url(f"{DOMAIN}/bibliography.html", "0.80"))
    for p in papers:
        lines.append(url(f"{DOMAIN}/{p['slug']}.html", "0.64"))
    lines.append('</urlset>\n')
    (ROOT / "sitemap.xml").write_text("\n".join(lines), encoding="utf-8")


def main():
    papers = load_papers()
    papers.sort(key=lambda p: (p["year"], p["title"]))
    for i, p in enumerate(papers):
        prev = papers[i - 1] if i > 0 else None
        nxt = papers[i + 1] if i < len(papers) - 1 else None
        (ROOT / f"{p['slug']}.html").write_text(render_paper(p, prev, nxt), encoding="utf-8")
    write_sitemap(papers)
    print(f"Generated {len(papers)} paper pages + sitemap.xml")


if __name__ == "__main__":
    main()
