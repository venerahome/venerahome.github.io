#!/usr/bin/env python3
"""Собирает сайт из template.html + data/listings.json.

Создаёт:
  index.html                      — главная (каталог)
  favorites/index.html            — избранное
  properties/<slug>/index.html    — отдельная страница каждого объекта (свой адрес и превью для мессенджеров)
  404.html                        — несуществующий адрес
  sitemap.xml, robots.txt

Запуск:  python3 build.py
"""
import json, os, re, shutil, html, time

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = "https://venerahome.github.io"
LANG = "ru"

with open(os.path.join(ROOT, "template.html"), encoding="utf-8") as f:
    TPL = f.read()
with open(os.path.join(ROOT, "data", "listings.json"), encoding="utf-8") as f:
    DATA = json.load(f)

LIST = DATA["listings"]
VERSION = str(int(time.time()))
HERO = (next((p for p in LIST if p.get("featured")), LIST[0])["photos"][0]) if LIST else ""
DATA_JS = json.dumps(DATA, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
HOME_DESC = "Венера Хасанова — квартиры, дома и виллы в Греции. Личный подход от выбора до ключей. Консультации на болгарском, русском и английском."


def money(n):
    return f"{n:,}".replace(",", " ") + " €"


def page(path, title, desc, og_image, route, robots="", canonical=None):
    out = TPL
    rep = {
        "%%LANG%%": LANG,
        "%%TITLE%%": html.escape(title, quote=True),
        "%%DESC%%": html.escape(desc, quote=True),
        "%%CANONICAL%%": canonical or (SITE + path),
        "%%OG_IMAGE%%": og_image,
        "%%HERO_IMAGE%%": HERO,
        "%%ROBOTS%%": robots,
        "%%VERSION%%": VERSION,
        "%%DATA%%": DATA_JS,
        "%%ROUTE%%": json.dumps(route, ensure_ascii=False),
    }
    for k, v in rep.items():
        out = out.replace(k, v)
    target = os.path.join(ROOT, path.strip("/"), "index.html") if path.endswith("/") and path != "/" else os.path.join(ROOT, "index.html" if path == "/" else path.strip("/"))
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        f.write(out)


# чистим старые страницы объектов (проданные объекты исчезают)
props_dir = os.path.join(ROOT, "properties")
if os.path.isdir(props_dir):
    shutil.rmtree(props_dir)

page("/", "Венера Хасанова · VENI Real Estate — недвижимость в Греции", HOME_DESC, HERO, {"view": "home"})
page("/favorites/", "Избранное · VENI Real Estate", HOME_DESC, HERO, {"view": "fav"}, robots='<meta name="robots" content="noindex">')
page("/404.html", "Страница не найдена · VENI Real Estate", HOME_DESC, HERO, {"view": "auto"}, robots='<meta name="robots" content="noindex">', canonical=SITE + "/")

urls = [SITE + "/"]
for p in LIST:
    path = f"/properties/{p['slug']}/"
    title = f"{p['title'][LANG]} · {money(p['price'])} · VENI Real Estate"
    desc = re.sub(r"\s+", " ", p["desc"][LANG]).strip()
    if len(desc) > 160:
        desc = desc[:157].rsplit(" ", 1)[0] + "…"
    page(path, title, desc, p["photos"][0] if p["photos"] else HERO, {"view": "prop", "slug": p["slug"]})
    if p.get("status") in (None, "sale", "rent", "reserved"):
        urls.append(SITE + path)

with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    for u in urls:
        f.write(f"  <url><loc>{u}</loc><lastmod>{DATA.get('updated', '')}</lastmod></url>\n")
    f.write("</urlset>\n")
with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
    f.write(f"User-agent: *\nAllow: /\nDisallow: /favorites/\nSitemap: {SITE}/sitemap.xml\n")

print(f"built {len(LIST)} property pages")
