#!/usr/bin/env python3
"""Собирает блог из blog/posts/*.json:
  /blog/ (RU)  и /blog/en/ (EN) — списки статей
  /blog/<slug>/ и /blog/en/<slug>/ — страницы статей
  /blog/rss.xml и /blog/en/rss.xml — ленты (для автопостинга в Telegram и Facebook)
Формат статьи — см. blog/README.md. Запуск: python3 blog/build_blog.py"""
import os, json, re, html, glob, shutil
from datetime import datetime, timezone

R = os.path.dirname(os.path.abspath(__file__))
SITE = "https://venerahome.github.io"
WA = "359882593077"

TX = {
  "ru": {
    "blog": "Блог", "title": "Блог VENI — недвижимость в Греции, Болгарии и Европе",
    "desc": "Новости рынка недвижимости, законы, цены и жизнь в Греции и Болгарии. Каждый день — от Венеры Хасановой.",
    "eyebrow": "Блог · Каждый день", "h1": "Недвижимость в Греции,<br><em>Болгарии и Европе</em>",
    "lead": "Новости рынка, законы, цены и жизнь у моря — простыми словами. Новая статья каждый день.",
    "all": "Все", "cats": {"greece": "Греция", "bulgaria": "Болгария", "europe": "Европа"},
    "read": "Читать →", "sources": "Источники", "back": "← Все статьи", "catalog": "Каталог объектов",
    "months": ["января","февраля","марта","апреля","мая","июня","июля","августа","сентября","октября","ноября","декабря"],
    "ctaGvT": "Хотите ВНЖ в Евросоюзе через недвижимость?", "ctaGv": "Проверьте за минуту, подходите ли вы под Golden Visa в Греции, — пришлю закрытую подборку объектов.", "ctaGvB": "Пройти анкету ↗",
    "ctaCT": "Ищете недвижимость в Греции или Болгарии?", "ctaC": "Напишите мне — подберу варианты под ваш бюджет и отвечу на вопросы лично.", "ctaCB": "Написать в WhatsApp ↗",
    "waHello": "Здравствуйте, Венера! Я прочитал(а) статью в вашем блоге: ",
    "author": "Венера Хасанова · консультант по недвижимости",
    "empty": "Скоро здесь появятся статьи.",
  },
  "en": {
    "blog": "Blog", "title": "VENI Blog — real estate in Greece, Bulgaria and Europe",
    "desc": "Property market news, laws, prices and life in Greece and Bulgaria. Every day, by Venera Khassanova.",
    "eyebrow": "Blog · Every day", "h1": "Real estate in Greece,<br><em>Bulgaria and Europe</em>",
    "lead": "Market news, laws, prices and life by the sea, in plain words. A new article every day.",
    "all": "All", "cats": {"greece": "Greece", "bulgaria": "Bulgaria", "europe": "Europe"},
    "read": "Read →", "sources": "Sources", "back": "← All articles", "catalog": "Property catalogue",
    "months": ["January","February","March","April","May","June","July","August","September","October","November","December"],
    "ctaGvT": "Want EU residency through real estate?", "ctaGv": "Check in a minute whether you qualify for the Greek Golden Visa, and I will send you a private selection of properties.", "ctaGvB": "Take the questionnaire ↗",
    "ctaCT": "Looking for property in Greece or Bulgaria?", "ctaC": "Message me and I will find options for your budget and answer your questions personally.", "ctaCB": "Message me on WhatsApp ↗",
    "waHello": "Hello Venera! I read an article on your blog: ",
    "author": "Venera Khassanova · real estate consultant",
    "empty": "Articles are coming soon.",
  },
}

esc = lambda s: html.escape(str(s), quote=True)

def inline(s):
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+|/[^)\s]*)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', s)
    return s

def md(text):
    """Мини-разметка: ## заголовок, ### подзаголовок, - список, 1. список, > цитата, **жирный**, [ссылка](url)."""
    out, lst = [], None
    def close():
        nonlocal lst
        if lst: out.append(f"</{lst}>"); lst = None
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = block.strip().split("\n")
        for ln in lines:
            ln = ln.rstrip()
            if re.match(r"^- ", ln):
                if lst != "ul": close(); out.append("<ul>"); lst = "ul"
                out.append(f"<li>{inline(ln[2:])}</li>"); continue
            if re.match(r"^\d+\. ", ln):
                if lst != "ol": close(); out.append("<ol>"); lst = "ol"
                out.append(f"<li>{inline(re.sub(r'^\d+\. ', '', ln))}</li>"); continue
            close()
            if ln.startswith("### "): out.append(f"<h3>{inline(ln[4:])}</h3>")
            elif ln.startswith("## "): out.append(f"<h2>{inline(ln[3:])}</h2>")
            elif ln.startswith("> "): out.append(f"<blockquote>{inline(ln[2:])}</blockquote>")
            elif ln: out.append(f"<p>{inline(ln)}</p>")
        close()
    return "\n".join(out)

def fmt_date(d, lang):
    dt = datetime.strptime(d, "%Y-%m-%d")
    m = TX[lang]["months"][dt.month - 1]
    return f"{dt.day} {m} {dt.year}" if lang == "ru" else f"{dt.day} {m} {dt.year}"

def head(lang, title, desc, url, image, alt_ru, alt_en, typ="website"):
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#f6f3ed">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta property="og:type" content="{typ}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{esc(image)}">
<meta property="og:url" content="{url}">
<meta property="og:locale" content="{'ru_RU' if lang == 'ru' else 'en_GB'}">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="ru" href="{alt_ru}">
<link rel="alternate" hreflang="en" href="{alt_en}">
<link rel="alternate" type="application/rss+xml" title="VENI" href="{SITE}/blog/{'' if lang == 'ru' else 'en/'}rss.xml">
<link rel="stylesheet" href="/blog/blog.css?v=1">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-73W576V144"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','G-73W576V144');</script>
</head>
<body>"""

def topbar(lang, alt_ru, alt_en):
    t = TX[lang]
    home = "/ru/" if lang == "ru" else "/en/"
    return f"""<header class="bar">
  <a href="{home}" class="logo">VENI<span>REAL ESTATE</span></a>
  <nav class="links"><a href="/blog/{'' if lang == 'ru' else 'en/'}">{t['blog']}</a><a href="{home}#catalog">{t['catalog']}</a><a href="/golden-visa/{lang}/">Golden Visa</a>
  <span class="langs"><a href="{alt_ru}"{' aria-current="true"' if lang == 'ru' else ''}>RU</a><a href="{alt_en}"{' aria-current="true"' if lang == 'en' else ''}>EN</a></span></nav>
</header>"""

def foot(lang="ru"):
    name = "Венера Хасанова" if lang == "ru" else "Venera Khassanova"
    return f'<footer class="foot">© 2026 {name} · VENI</footer>'

def cta(lang, post, url):
    t = TX[lang]
    if post.get("cta", "golden-visa") == "golden-visa":
        return f"""<aside class="cta-box"><h3>{t['ctaGvT']}</h3><p>{t['ctaGv']}</p><a class="btn" href="/golden-visa/{lang}/#form">{t['ctaGvB']}</a></aside>"""
    from urllib.parse import quote
    msg = quote(t["waHello"] + post[lang]["title"] + "\n" + url)
    return f"""<aside class="cta-box"><h3>{t['ctaCT']}</h3><p>{t['ctaC']}</p><a class="btn" href="https://wa.me/{WA}?text={msg}" target="_blank" rel="noopener">{t['ctaCB']}</a></aside>"""

def load_posts():
    posts = []
    for f in glob.glob(os.path.join(R, "posts", "*.json")):
        p = json.load(open(f, encoding="utf-8"))
        if p.get("status", "published") != "published": continue
        posts.append(p)
    posts.sort(key=lambda p: (p["date"], p["slug"]), reverse=True)
    return posts

def post_url(lang, slug): return f"{SITE}/blog/{'' if lang == 'ru' else 'en/'}{slug}/"

def write(path, s):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(s)

def build():
    posts = load_posts()
    # убрать старые страницы статей (вдруг статью удалили)
    for base in [R, os.path.join(R, "en")]:
        if not os.path.isdir(base): continue
        for d in os.listdir(base):
            full = os.path.join(base, d)
            if os.path.isdir(full) and os.path.exists(os.path.join(full, ".generated")): shutil.rmtree(full)
    for lang in ["ru", "en"]:
        t = TX[lang]
        root = R if lang == "ru" else os.path.join(R, "en")
        # статьи
        for p in posts:
            L = p[lang]; url = post_url(lang, p["slug"])
            a_ru, a_en = post_url("ru", p["slug"]), post_url("en", p["slug"])
            src = "".join(f'<li><a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(s["title"])}</a></li>' for s in p.get("sources", []))
            body = f"""{head(lang, L['title'] + ' | VENI', L['excerpt'], url, p['image'], a_ru, a_en, 'article')}
{topbar(lang, a_ru, a_en)}
<main class="article">
  <a class="back" href="/blog/{'' if lang == 'ru' else 'en/'}">{t['back']}</a>
  <span class="cat">{t['cats'][p['category']]} · {fmt_date(p['date'], lang)}</span>
  <h1>{esc(L['title'])}</h1>
  <p class="excerpt">{esc(L['excerpt'])}</p>
  <img class="cover" src="{esc(p['image'])}" alt="" width="1200" height="800">
  <div class="body">{md(L['body'])}</div>
  {cta(lang, p, url)}
  {f'<section class="sources"><h3>{t["sources"]}</h3><ul>{src}</ul></section>' if src else ''}
  <p class="author">{t['author']}</p>
</main>
{foot(lang)}
</body></html>"""
            d = os.path.join(root, p["slug"])
            write(os.path.join(d, "index.html"), body)
            open(os.path.join(d, ".generated"), "w").close()
        # список
        cards = "".join(f"""<a class="card" href="{post_url(lang, p['slug'])}" data-cat="{p['category']}">
  <img src="{esc(p['image'])}" alt="" loading="lazy" width="1200" height="800">
  <span class="cat">{t['cats'][p['category']]} · {fmt_date(p['date'], lang)}</span>
  <h2>{esc(p[lang]['title'])}</h2><p>{esc(p[lang]['excerpt'])}</p><span class="more">{t['read']}</span></a>""" for p in posts) or f'<p class="lead">{t["empty"]}</p>'
        chips = f'<button class="on" data-cat="">{t["all"]}</button>' + "".join(f'<button data-cat="{k}">{v}</button>' for k, v in t["cats"].items())
        idx_url = f"{SITE}/blog/{'' if lang == 'ru' else 'en/'}"
        idx = f"""{head(lang, t['title'], t['desc'], idx_url, posts[0]['image'] if posts else SITE + '/assets/hero.jpg', SITE + '/blog/', SITE + '/blog/en/')}
{topbar(lang, SITE + '/blog/', SITE + '/blog/en/')}
<main class="list">
  <span class="kicker">{t['eyebrow']}</span>
  <h1>{t['h1']}</h1>
  <p class="lead">{t['lead']}</p>
  <div class="chips" id="chips">{chips}</div>
  <div class="cards" id="cards">{cards}</div>
</main>
{foot(lang)}
<script>document.getElementById('chips').addEventListener('click',e=>{{const b=e.target.closest('button');if(!b)return;document.querySelectorAll('#chips button').forEach(x=>x.classList.toggle('on',x===b));document.querySelectorAll('#cards .card').forEach(c=>c.hidden=!!b.dataset.cat&&c.dataset.cat!==b.dataset.cat)}})</script>
</body></html>"""
        write(os.path.join(root, "index.html"), idx)
        # RSS
        items = "".join(f"""<item><title>{esc(p[lang]['title'])}</title><link>{post_url(lang, p['slug'])}</link><guid isPermaLink="true">{post_url(lang, p['slug'])}</guid><pubDate>{datetime.strptime(p['date'], '%Y-%m-%d').replace(hour=9, tzinfo=timezone.utc).strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate><category>{t['cats'][p['category']]}</category><description>{esc(p[lang]['excerpt'])}</description><enclosure url="{esc(p['image'])}" type="image/jpeg" length="0"/></item>""" for p in posts[:30])
        rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>{esc(t['title'])}</title><link>{idx_url}</link><description>{esc(t['desc'])}</description><language>{lang}</language>{items}</channel></rss>"""
        write(os.path.join(root, "rss.xml"), rss)
    # карта сайта блога (+ страница Golden Visa) для Google; основной sitemap.xml не трогаем
    today = datetime.now().strftime("%Y-%m-%d")
    urls = [(f"{SITE}/blog/", today), (f"{SITE}/blog/en/", today), (f"{SITE}/golden-visa/ru/", today), (f"{SITE}/golden-visa/en/", today)]
    for p in posts: urls += [(post_url("ru", p["slug"]), p["date"]), (post_url("en", p["slug"]), p["date"])]
    write(os.path.join(R, "sitemap.xml"), '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in urls) + "</urlset>\n")
    print(f"blog: {len(posts)} posts")

if __name__ == "__main__":
    build()
