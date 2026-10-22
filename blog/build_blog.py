#!/usr/bin/env python3
"""Собирает блог Венеры из blog/posts/*.json на 5 языках (ru, bg, en, de, es):
  /blog/ (RU), /blog/bg/, /blog/en/, /blog/de/, /blog/es/        — главные страницы блога
  /blog/<slug>/, /blog/<lang>/<slug>/                             — статьи
  /blog/rss.xml, /blog/<lang>/rss.xml                              — ленты
  /blog/og/<slug>-<lang>.jpg                                       — фирменные картинки для Telegram/Facebook
  /blog/sitemap.xml                                                — карта для Google
Формат статьи — blog/README.md. Запуск: python3 blog/build_blog.py  (--og заново перерисует все картинки)"""
import os, re, sys, json, html, glob, shutil
from datetime import datetime, timezone
from urllib.parse import quote

R = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(R)
SITE = "https://venerahome.github.io"
WA = "359882593077"
TG = "home_greece"
LANGS = ["ru", "bg", "en", "de", "es"]
LOCALE = {"ru": "ru_RU", "bg": "bg_BG", "en": "en_GB", "de": "de_DE", "es": "es_ES"}
COLORS = {"greece": "#1c4563", "bulgaria": "#263a36", "europe": "#4b3446"}

TX = {
"ru": {
  "name": "Венера Хасанова", "blog": "Блог", "catalog": "Объекты", "gv": "ВНЖ в Греции",
  "title": "Блог Венеры Хасановой — недвижимость в Греции и Болгарии",
  "desc": "Каждый день простыми словами: цены, законы, ВНЖ и жизнь у моря в Греции и Болгарии. Блог консультанта по недвижимости Венеры Хасановой.",
  "heroKicker": "Блог · новая статья каждое утро",
  "heroH1": "Недвижимость в Греции и Болгарии — <em>честно и по-человечески</em>",
  "heroLead": "Меня зовут Венера Хасанова. Я консультант по недвижимости и с 2013 года живу на Балканах — между Болгарией и Грецией. Здесь я каждый день простыми словами объясняю, что происходит с ценами, законами и жизнью у моря.",
  "trust": [["С 2013 года", "живу на Балканах"], ["Греция и Болгария", "сопровождаю покупки"], ["Свой дом в Греции", "знаю путь изнутри"]],
  "btnTg": "Подписаться в Telegram", "btnWa": "Задать вопрос в WhatsApp",
  "latest": "Свежая статья", "allPosts": "Все статьи", "all": "Все",
  "cats": {"greece": "Греция", "bulgaria": "Болгария", "europe": "Европа"},
  "min": "мин чтения", "tldr": "Коротко", "read": "Читать статью →", "sources": "Источники", "back": "← Все статьи",
  "role": "консультант по недвижимости · Греция и Болгария",
  "aboutT": "Об авторе",
  "aboutText": "Я консультант по недвижимости. С 2013 года живу на Балканах, между Болгарией и Грецией, сама купила дом в Греции и восстанавливаю его. Помогаю подобрать жильё, проверить его и спокойно пройти сделку — на русском, болгарском и английском.",
  "also": "Читайте также",
  "ctaGvT": "Хотите ВНЖ в Евросоюзе через недвижимость?", "ctaGv": "Проверьте за минуту, подходите ли вы под Golden Visa в Греции, — я пришлю закрытую подборку объектов.", "ctaGvB": "Пройти анкету ↗",
  "ctaCT": "Ищете недвижимость в Греции или Болгарии?", "ctaC": "Напишите мне — подберу варианты под ваш бюджет и отвечу на вопросы лично.", "ctaCB": "Написать в WhatsApp ↗",
  "subT": "Новая статья — каждое утро", "subText": "Подпишитесь на мой Telegram-канал, чтобы не пропускать важное о недвижимости в Греции и Болгарии.",
  "waHello": "Здравствуйте, Венера! Я прочитал(а) статью в вашем блоге: ", "waHi": "Здравствуйте, Венера! У меня вопрос о недвижимости.",
  "months": ["января","февраля","марта","апреля","мая","июня","июля","августа","сентября","октября","ноября","декабря"],
  "empty": "Скоро здесь появятся статьи.", "home": "Главная",
},
"bg": {
  "name": "Венера Хасанова", "blog": "Блог", "catalog": "Имоти", "gv": "Пребиваване в Гърция",
  "title": "Блогът на Венера Хасанова — недвижими имоти в Гърция и България",
  "desc": "Всеки ден с прости думи: цени, закони, пребиваване и живот край морето в Гърция и България. Блогът на консултанта по недвижими имоти Венера Хасанова.",
  "heroKicker": "Блог · нова статия всяка сутрин",
  "heroH1": "Недвижими имоти в Гърция и България — <em>честно и по човешки</em>",
  "heroLead": "Казвам се Венера Хасанова. Консултант съм по недвижими имоти и от 2013 г. живея на Балканите — между България и Гърция. Тук всеки ден обяснявам с прости думи какво се случва с цените, законите и живота край морето.",
  "trust": [["От 2013 г.", "живея на Балканите"], ["Гърция и България", "съпровождам покупки"], ["Моя къща в Гърция", "познавам пътя отвътре"]],
  "btnTg": "Абонирайте се в Telegram", "btnWa": "Задайте въпрос в WhatsApp",
  "latest": "Най-новата статия", "allPosts": "Всички статии", "all": "Всички",
  "cats": {"greece": "Гърция", "bulgaria": "България", "europe": "Европа"},
  "min": "мин четене", "tldr": "Накратко", "read": "Прочетете статията →", "sources": "Източници", "back": "← Всички статии",
  "role": "консултант по недвижими имоти · Гърция и България",
  "aboutT": "За автора",
  "aboutText": "Консултант съм по недвижими имоти. От 2013 г. живея на Балканите, между България и Гърция, сама купих къща в Гърция и я възстановявам. Помагам да изберете жилище, да го проверите и спокойно да минете през сделката — на български, руски и английски.",
  "also": "Прочетете също",
  "ctaGvT": "Искате пребиваване в ЕС чрез имот?", "ctaGv": "Проверете за минута дали отговаряте на условията за Golden Visa в Гърция — ще ви изпратя затворена селекция от имоти.", "ctaGvB": "Попълнете анкетата ↗",
  "ctaCT": "Търсите имот в Гърция или България?", "ctaC": "Пишете ми — ще подбера варианти според бюджета ви и лично ще отговоря на въпросите ви.", "ctaCB": "Пишете в WhatsApp ↗",
  "subT": "Нова статия — всяка сутрин", "subText": "Абонирайте се за моя Telegram канал, за да не пропускате важното за имотите в Гърция и България.",
  "waHello": "Здравейте, Венера! Прочетох статия във вашия блог: ", "waHi": "Здравейте, Венера! Имам въпрос за имот.",
  "months": ["януари","февруари","март","април","май","юни","юли","август","септември","октомври","ноември","декември"],
  "empty": "Скоро тук ще има статии.", "home": "Начало",
},
"en": {
  "name": "Venera Khassanova", "blog": "Blog", "catalog": "Properties", "gv": "Golden Visa",
  "title": "Venera Khassanova's blog — real estate in Greece and Bulgaria",
  "desc": "Every day, in plain words: prices, laws, residency and life by the sea in Greece and Bulgaria. The blog of real estate consultant Venera Khassanova.",
  "heroKicker": "Blog · a new article every morning",
  "heroH1": "Real estate in Greece and Bulgaria — <em>honest and human</em>",
  "heroLead": "My name is Venera Khassanova. I am a real estate consultant, and since 2013 I have lived in the Balkans, between Bulgaria and Greece. Here I explain every day, in plain words, what is happening with prices, laws and life by the sea.",
  "trust": [["Since 2013", "living in the Balkans"], ["Greece and Bulgaria", "guiding purchases"], ["My own house in Greece", "I know the path first-hand"]],
  "btnTg": "Follow on Telegram", "btnWa": "Ask me on WhatsApp",
  "latest": "Latest article", "allPosts": "All articles", "all": "All",
  "cats": {"greece": "Greece", "bulgaria": "Bulgaria", "europe": "Europe"},
  "min": "min read", "tldr": "In short", "read": "Read the article →", "sources": "Sources", "back": "← All articles",
  "role": "real estate consultant · Greece and Bulgaria",
  "aboutT": "About the author",
  "aboutText": "I am a real estate consultant. Since 2013 I have lived in the Balkans, between Bulgaria and Greece, and I bought a house in Greece myself and am restoring it. I help people choose a home, check it and go through the purchase calmly, in English, Russian and Bulgarian.",
  "also": "Read next",
  "ctaGvT": "Want EU residency through real estate?", "ctaGv": "Check in a minute whether you qualify for the Greek Golden Visa, and I will send you a private selection of properties.", "ctaGvB": "Take the questionnaire ↗",
  "ctaCT": "Looking for property in Greece or Bulgaria?", "ctaC": "Message me and I will find options for your budget and answer your questions personally.", "ctaCB": "Message me on WhatsApp ↗",
  "subT": "A new article every morning", "subText": "Follow my Telegram channel so you never miss what matters about property in Greece and Bulgaria.",
  "waHello": "Hello Venera! I read an article on your blog: ", "waHi": "Hello Venera! I have a question about property.",
  "months": ["January","February","March","April","May","June","July","August","September","October","November","December"],
  "empty": "Articles are coming soon.", "home": "Home",
},
"de": {
  "name": "Venera Khassanova", "blog": "Blog", "catalog": "Immobilien", "gv": "Golden Visa",
  "title": "Der Blog von Venera Khassanova — Immobilien in Griechenland und Bulgarien",
  "desc": "Jeden Tag in einfachen Worten: Preise, Gesetze, Aufenthalt und Leben am Meer in Griechenland und Bulgarien. Der Blog der Immobilienberaterin Venera Khassanova.",
  "heroKicker": "Blog · jeden Morgen ein neuer Artikel",
  "heroH1": "Immobilien in Griechenland und Bulgarien — <em>ehrlich und persönlich</em>",
  "heroLead": "Mein Name ist Venera Khassanova. Ich bin Immobilienberaterin und lebe seit 2013 auf dem Balkan, zwischen Bulgarien und Griechenland. Hier erkläre ich jeden Tag in einfachen Worten, was sich bei Preisen, Gesetzen und dem Leben am Meer tut.",
  "trust": [["Seit 2013", "auf dem Balkan zu Hause"], ["Griechenland und Bulgarien", "ich begleite Käufe"], ["Eigenes Haus in Griechenland", "ich kenne den Weg selbst"]],
  "btnTg": "Auf Telegram folgen", "btnWa": "Frage per WhatsApp",
  "latest": "Neuester Artikel", "allPosts": "Alle Artikel", "all": "Alle",
  "cats": {"greece": "Griechenland", "bulgaria": "Bulgarien", "europe": "Europa"},
  "min": "Min. Lesezeit", "tldr": "Kurz gesagt", "read": "Artikel lesen →", "sources": "Quellen", "back": "← Alle Artikel",
  "role": "Immobilienberaterin · Griechenland und Bulgarien",
  "aboutT": "Über die Autorin",
  "aboutText": "Ich bin Immobilienberaterin. Seit 2013 lebe ich auf dem Balkan, zwischen Bulgarien und Griechenland, und habe selbst ein Haus in Griechenland gekauft, das ich gerade restauriere. Ich helfe, eine Immobilie zu finden, sie zu prüfen und den Kauf in Ruhe abzuschließen – auf Englisch, Russisch und Bulgarisch.",
  "also": "Weiterlesen",
  "ctaGvT": "EU-Aufenthalt durch eine Immobilie?", "ctaGv": "Prüfen Sie in einer Minute, ob Sie für das griechische Golden Visa infrage kommen – ich schicke Ihnen eine exklusive Objektauswahl.", "ctaGvB": "Zum Fragebogen ↗",
  "ctaCT": "Suchen Sie eine Immobilie in Griechenland oder Bulgarien?", "ctaC": "Schreiben Sie mir – ich suche passende Angebote für Ihr Budget und beantworte Ihre Fragen persönlich.", "ctaCB": "Per WhatsApp schreiben ↗",
  "subT": "Jeden Morgen ein neuer Artikel", "subText": "Folgen Sie meinem Telegram-Kanal und verpassen Sie nichts Wichtiges über Immobilien in Griechenland und Bulgarien.",
  "waHello": "Hallo Venera! Ich habe einen Artikel in Ihrem Blog gelesen: ", "waHi": "Hallo Venera! Ich habe eine Frage zu einer Immobilie.",
  "months": ["Januar","Februar","März","April","Mai","Juni","Juli","August","September","Oktober","November","Dezember"],
  "empty": "Bald finden Sie hier Artikel.", "home": "Startseite",
},
"es": {
  "name": "Venera Khassanova", "blog": "Blog", "catalog": "Inmuebles", "gv": "Golden Visa",
  "title": "El blog de Venera Khassanova — inmuebles en Grecia y Bulgaria",
  "desc": "Cada día, con palabras sencillas: precios, leyes, residencia y vida junto al mar en Grecia y Bulgaria. El blog de la asesora inmobiliaria Venera Khassanova.",
  "heroKicker": "Blog · un artículo nuevo cada mañana",
  "heroH1": "Inmuebles en Grecia y Bulgaria — <em>con sinceridad y cercanía</em>",
  "heroLead": "Me llamo Venera Khassanova. Soy asesora inmobiliaria y desde 2013 vivo en los Balcanes, entre Bulgaria y Grecia. Aquí explico cada día, con palabras sencillas, qué pasa con los precios, las leyes y la vida junto al mar.",
  "trust": [["Desde 2013", "vivo en los Balcanes"], ["Grecia y Bulgaria", "acompaño compras"], ["Mi propia casa en Grecia", "conozco el camino"]],
  "btnTg": "Seguir en Telegram", "btnWa": "Pregúntame por WhatsApp",
  "latest": "Último artículo", "allPosts": "Todos los artículos", "all": "Todos",
  "cats": {"greece": "Grecia", "bulgaria": "Bulgaria", "europe": "Europa"},
  "min": "min de lectura", "tldr": "En resumen", "read": "Leer el artículo →", "sources": "Fuentes", "back": "← Todos los artículos",
  "role": "asesora inmobiliaria · Grecia y Bulgaria",
  "aboutT": "Sobre la autora",
  "aboutText": "Soy asesora inmobiliaria. Desde 2013 vivo en los Balcanes, entre Bulgaria y Grecia, y yo misma compré una casa en Grecia que estoy restaurando. Ayudo a elegir vivienda, a revisarla y a cerrar la compra con tranquilidad, en inglés, ruso y búlgaro.",
  "also": "Sigue leyendo",
  "ctaGvT": "¿Quieres la residencia en la UE a través de un inmueble?", "ctaGv": "Comprueba en un minuto si cumples los requisitos de la Golden Visa griega y te enviaré una selección privada de inmuebles.", "ctaGvB": "Rellenar el cuestionario ↗",
  "ctaCT": "¿Buscas un inmueble en Grecia o Bulgaria?", "ctaC": "Escríbeme: busco opciones para tu presupuesto y respondo a tus preguntas personalmente.", "ctaCB": "Escribir por WhatsApp ↗",
  "subT": "Un artículo nuevo cada mañana", "subText": "Sigue mi canal de Telegram para no perderte lo importante sobre inmuebles en Grecia y Bulgaria.",
  "waHello": "¡Hola, Venera! He leído un artículo en tu blog: ", "waHi": "¡Hola, Venera! Tengo una pregunta sobre un inmueble.",
  "months": ["enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre"],
  "empty": "Pronto habrá artículos aquí.", "home": "Inicio",
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
        for ln in block.strip().split("\n"):
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

# ---------- данные ----------
def L(p, lang):
    """Текст статьи на языке; если перевода нет — английский, затем русский."""
    return p.get(lang) or p.get("en") or p["ru"]

def stat(p, lang):
    s = p.get("stat")
    if not s: return None, None
    v = s.get("value"); lab = s.get("label", {})
    v = v.get(lang) or v.get("en") or v.get("ru") if isinstance(v, dict) else v
    lab = lab.get(lang) or lab.get("en") or lab.get("ru") if isinstance(lab, dict) else lab
    return v, lab

def minutes(p, lang): return max(2, round(len(L(p, lang)["body"].split()) / 200))

def fmt_date(d, lang):
    dt = datetime.strptime(d, "%Y-%m-%d"); m = TX[lang]["months"][dt.month - 1]
    if lang == "en": return f"{dt.day} {m} {dt.year}"
    if lang == "de": return f"{dt.day}. {m} {dt.year}"
    if lang == "es": return f"{dt.day} de {m} de {dt.year}"
    return f"{dt.day} {m} {dt.year}"

def base(lang): return "/blog/" if lang == "ru" else f"/blog/{lang}/"
def post_path(lang, slug): return base(lang) + slug + "/"
def post_url(lang, slug): return SITE + post_path(lang, slug)
def home(lang): return f"/{lang}/"
def gv(lang): return "/golden-visa/ru/" if lang == "ru" else "/golden-visa/en/"

def load_posts():
    posts = [json.load(open(f, encoding="utf-8")) for f in glob.glob(os.path.join(R, "posts", "*.json"))]
    posts = [p for p in posts if p.get("status", "published") == "published"]
    posts.sort(key=lambda p: (p["date"], p["slug"]), reverse=True)
    return posts

def write(path, s):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write(s)

# ---------- фирменные картинки для соцсетей ----------
def og_image(p, lang, force=False):
    rel = f"og/{p['slug']}-{lang}.jpg"; out = os.path.join(R, rel)
    if os.path.exists(out) and not force: return SITE + "/blog/" + rel
    try:
        from PIL import Image, ImageDraw, ImageFont, ImageOps
    except Exception:
        return SITE + "/assets/venera.jpg"
    F = os.path.join(R, "fonts")
    def lora(size, w=600):
        f = ImageFont.truetype(os.path.join(F, "Lora-Variable.ttf"), size)
        try: f.set_variation_by_axes([w])
        except Exception: pass
        return f
    sans = lambda size, bold=False: ImageFont.truetype(os.path.join(F, "Carlito-Bold.ttf" if bold else "Carlito-Regular.ttf"), size)
    W, H = 1200, 630
    bg = COLORS.get(p["category"], "#263a36")
    gold, cream, soft = (215, 185, 138), (246, 243, 237), (214, 222, 216)
    im = Image.new("RGB", (W, H), bg); d = ImageDraw.Draw(im)
    d.rectangle([24, 24, W - 25, H - 25], outline=gold + (0,), width=2)
    # портрет в круге
    por = Image.open(os.path.join(ROOT, "assets", "venera.jpg")).convert("RGB")
    pw, ph = por.size; side = min(pw, ph)
    por = por.crop((0, int(ph * 0.04), side, int(ph * 0.04) + side)).resize((280, 280), Image.LANCZOS)
    mask = Image.new("L", (280, 280), 0); ImageDraw.Draw(mask).ellipse([0, 0, 279, 279], fill=255)
    cx, cy = 860, 92
    d.ellipse([cx - 8, cy - 8, cx + 288, cy + 288], fill=gold)
    im.paste(por, (cx, cy), mask)
    t = TX[lang]
    def centered(y, text, font, fill):
        w = d.textlength(text, font=font); d.text((cx + 140 - w / 2, y), text, font=font, fill=fill)
    centered(400, t["name"], sans(32, True), cream)
    role = t["role"].split(" · ")
    centered(442, role[0], sans(22), gold)
    if len(role) > 1: centered(472, role[1], sans(22), gold)
    # левая колонка
    x, maxw = 76, 700
    kicker = p.get("kicker") or (t["cats"][p["category"]] + "  ·  " + fmt_date(p["date"], lang))
    d.text((x, 70), kicker.upper(), font=sans(24, True), fill=gold)
    y = 112
    v, lab = stat(p, lang)
    if v:
        fnum = lora(92, 700)
        while d.textlength(v.replace("→", "  "), font=fnum) > maxw and fnum.size > 50: fnum = lora(fnum.size - 6, 700)
        # стрелка «→» есть не во всех шрифтах — рисуем её отдельным шрифтом
        parts = v.split("→"); cx_ = x - 4
        farr = sans(int(fnum.size * 0.8), True)
        for i_, part in enumerate(parts):
            if i_:
                d.text((cx_ + 16, y + fnum.size * 0.12), "→", font=farr, fill=gold); cx_ += d.textlength("→", font=farr) + 32
            d.text((cx_, y), part.strip() if i_ else part.rstrip(), font=fnum, fill=gold)
            cx_ += d.textlength(part.strip() if i_ else part.rstrip(), font=fnum)
        y += fnum.size + 18
        if lab:
            fl = sans(26)
            words, line, lines = lab.split(), "", []
            for w_ in words:
                tst = (line + " " + w_).strip()
                if d.textlength(tst, font=fl) <= maxw: line = tst
                else: lines.append(line); line = w_
            lines.append(line)
            for ln in lines[:2]: d.text((x, y), ln, font=fl, fill=soft); y += 32
        y += 24
    ftitle = lora(40 if v else 54, 600)
    words, line, lines = L(p, lang)["title"].split(), "", []
    for w_ in words:
        tst = (line + " " + w_).strip()
        if d.textlength(tst, font=ftitle) <= maxw: line = tst
        else: lines.append(line); line = w_
    lines.append(line)
    room = max(1, int((H - 90 - y) // (ftitle.size * 1.25)))
    if len(lines) > room:
        lines = lines[:room]; lines[-1] = lines[-1].rstrip(",.:;—-") + "…"
    for ln in lines: d.text((x, y), ln, font=ftitle, fill=cream); y += int(ftitle.size * 1.25)
    d.text((x, H - 70), "venerahome.github.io/blog", font=sans(22), fill=gold)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    im.save(out, "JPEG", quality=86, optimize=True, progressive=True)
    return SITE + "/blog/" + rel

# ---------- куски страниц ----------
def head(lang, title, desc, url, image, alts, typ="website"):
    hl = "".join(f'<link rel="alternate" hreflang="{l}" href="{alts[l]}">' for l in LANGS)
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#f6f3ed">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="author" content="{esc(TX[lang]['name'])}">
<meta property="og:type" content="{typ}">
<meta property="og:site_name" content="VENI">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{esc(image)}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:url" content="{url}">
<meta property="og:locale" content="{LOCALE[lang]}">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="{url}">
{hl}<link rel="alternate" hreflang="x-default" href="{alts['en']}">
<link rel="alternate" type="application/rss+xml" title="VENI" href="{SITE}{base(lang)}rss.xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400..700;1,400..700&display=swap">
<link rel="stylesheet" href="/blog/blog.css?v=5">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-73W576V144"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','G-73W576V144');</script>
</head>
<body>"""

def topbar(lang, alts):
    t = TX[lang]
    cur = ' aria-current="true"'
    langs = "".join(f'<a href="{alts[l]}"{cur if l == lang else ""}>{l.upper()}</a>' for l in LANGS)
    return f"""<header class="bar">
  <a href="{home(lang)}" class="logo">VENI<span>REAL ESTATE</span></a>
  <nav class="links"><a href="{base(lang)}" class="on">{t['blog']}</a><a href="{home(lang)}#catalog">{t['catalog']}</a><a href="{gv(lang)}">{t['gv']}</a></nav>
  <span class="langs">{langs}</span>
</header>"""

def foot(lang):
    return f'<footer class="foot"><span>© 2026 {esc(TX[lang]["name"])} · VENI</span><span><a href="https://t.me/{TG}" target="_blank" rel="noopener">Telegram</a> · <a href="https://wa.me/{WA}" target="_blank" rel="noopener">WhatsApp</a></span></footer>'

def who(lang, cls="who"):
    t = TX[lang]
    return f'<span class="{cls}"><img src="/assets/venera.jpg" alt="" width="40" height="40"><span><b>{esc(t["name"])}</b><small>{esc(t["role"])}</small></span></span>'

def cover(p, lang, big=False):
    t = TX[lang]; v, lab = stat(p, lang)
    mid = (f'<span class="c-num">{esc(v)}</span><span class="c-label">{esc(lab or "")}</span>' if v
           else f'<span class="c-title">{esc(L(p, lang)["title"])}</span>')
    return f"""<div class="cover c-{p['category']}{' big' if big else ''}" aria-hidden="true">
  <span class="c-top"><span>{esc(t['cats'][p['category']])}</span><span class="c-mark">VENI</span></span>
  <span class="c-mid">{mid}</span>
  <span class="c-who"><img src="/assets/venera.jpg" alt="" loading="lazy" width="36" height="36">{esc(t['name'])}</span>
</div>"""

def meta_line(p, lang):
    t = TX[lang]
    return f'<span class="meta"><b>{esc(t["cats"][p["category"]])}</b> · {fmt_date(p["date"], lang)} · {minutes(p, lang)} {t["min"]}</span>'

def card(p, lang, featured=False):
    T = L(p, lang)
    return f"""<a class="card{' featured' if featured else ''}" href="{post_path(lang, p['slug'])}" data-cat="{p['category']}">
  {cover(p, lang, featured)}
  <span class="card-text">{meta_line(p, lang)}<h3>{esc(T['title'])}</h3><p>{esc(T['excerpt'])}</p><span class="more">{TX[lang]['read']}</span></span>
</a>"""

def cta(lang, p, url):
    t = TX[lang]
    if p.get("cta", "golden-visa") == "golden-visa":
        return f'<aside class="cta-box"><h3>{t["ctaGvT"]}</h3><p>{t["ctaGv"]}</p><a class="btn" href="{gv(lang)}#form">{t["ctaGvB"]}</a></aside>'
    msg = quote(t["waHello"] + L(p, lang)["title"] + "\n" + url)
    return f'<aside class="cta-box"><h3>{t["ctaCT"]}</h3><p>{t["ctaC"]}</p><a class="btn" href="https://wa.me/{WA}?text={msg}" target="_blank" rel="noopener">{t["ctaCB"]}</a></aside>'

def buttons(lang):
    t = TX[lang]
    return (f'<span class="btns"><a class="btn" href="https://t.me/{TG}" target="_blank" rel="noopener">{t["btnTg"]}</a>'
            f'<a class="btn ghost" href="https://wa.me/{WA}?text={quote(t["waHi"])}" target="_blank" rel="noopener">{t["btnWa"]}</a></span>')

def about(lang):
    t = TX[lang]
    return f"""<section class="about-card">
  <img src="/assets/venera.jpg" alt="{esc(t['name'])}" loading="lazy" width="800" height="1067">
  <div><span class="kicker">{t['aboutT']}</span><h3>{esc(t['name'])}</h3><p>{esc(t['aboutText'])}</p>{buttons(lang)}</div>
</section>"""

# ---------- сборка ----------
def build(force_og=False):
    posts = load_posts()
    # убрать старые страницы статей
    for l in LANGS:
        b = os.path.join(ROOT, base(l).strip("/"))
        if not os.path.isdir(b): continue
        for dname in os.listdir(b):
            full = os.path.join(b, dname)
            if os.path.isdir(full) and os.path.exists(os.path.join(full, ".generated")): shutil.rmtree(full)
    for lang in LANGS:
        t = TX[lang]; root = os.path.join(ROOT, base(lang).strip("/"))
        for i, p in enumerate(posts):
            T = L(p, lang); url = post_url(lang, p["slug"])
            alts = {l: post_url(l, p["slug"]) for l in LANGS}
            img = og_image(p, lang, force_og)
            src = "".join(f'<li><a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(s["title"])}</a></li>' for s in p.get("sources", []))
            tl = T.get("tldr") or []
            tldr = f'<aside class="tldr"><span class="kicker">{t["tldr"]}</span><ul>{"".join(f"<li>{esc(x)}</li>" for x in tl)}</ul></aside>' if tl else ""
            others = [q for q in posts if q["slug"] != p["slug"]][:2]
            also = f'<section class="also"><h2 class="sec">{t["also"]}</h2><div class="cards two">{"".join(card(q, lang) for q in others)}</div></section>' if others else ""
            ld = json.dumps({"@context": "https://schema.org", "@type": "Article", "headline": T["title"], "description": T["excerpt"],
                             "image": img, "datePublished": p["date"], "inLanguage": lang,
                             "author": {"@type": "Person", "name": t["name"], "jobTitle": t["role"], "image": SITE + "/assets/venera.jpg", "url": SITE + base(lang)},
                             "mainEntityOfPage": url}, ensure_ascii=False)
            page = f"""{head(lang, T['title'] + ' — ' + t['name'], T['excerpt'], url, img, alts, 'article')}
<script type="application/ld+json">{ld}</script>
{topbar(lang, alts)}
<main class="article">
  <a class="back" href="{base(lang)}">{t['back']}</a>
  {meta_line(p, lang)}
  <h1>{esc(T['title'])}</h1>
  <p class="excerpt">{esc(T['excerpt'])}</p>
  {who(lang)}
  {cover(p, lang, True)}
  {tldr}
  <div class="body">{md(T['body'])}</div>
  {cta(lang, p, url)}
  {about(lang)}
  {f'<section class="sources"><h3>{t["sources"]}</h3><ul>{src}</ul></section>' if src else ''}
</main>
<div class="wide">{also}</div>
{foot(lang)}
</body></html>"""
            dpath = os.path.join(root, p["slug"])
            write(os.path.join(dpath, "index.html"), page)
            open(os.path.join(dpath, ".generated"), "w").close()
        # главная блога
        alts = {l: SITE + base(l) for l in LANGS}
        trust = "".join(f"<li><b>{esc(a)}</b><span>{esc(b)}</span></li>" for a, b in t["trust"])
        chips = f'<button class="on" data-cat="">{t["all"]}</button>' + "".join(f'<button data-cat="{k}">{v}</button>' for k, v in t["cats"].items())
        feat = f'<section class="latest"><h2 class="sec">{t["latest"]}</h2>{card(posts[0], lang, True)}</section>' if posts else f'<p class="lead">{t["empty"]}</p>'
        rest = "".join(card(p, lang) for p in posts[1:])
        grid = f'<section class="list-all"><div class="list-head"><h2 class="sec">{t["allPosts"]}</h2><div class="chips" id="chips">{chips}</div></div><div class="cards" id="cards">{rest}</div></section>' if len(posts) > 1 else ""
        idx = f"""{head(lang, t['title'], t['desc'], SITE + base(lang), SITE + '/blog/og/blog-' + lang + '.jpg', alts)}
{topbar(lang, alts)}
<main class="list">
  <section class="intro">
    <img class="portrait" src="/assets/venera.jpg" alt="{esc(t['name'])}" width="800" height="1067">
    <div>
      <span class="kicker">{t['heroKicker']}</span>
      <h1>{t['heroH1']}</h1>
      <p class="lead">{esc(t['heroLead'])}</p>
      <ul class="trust">{trust}</ul>
      {buttons(lang)}
    </div>
  </section>
  {feat}
  {grid}
  <section class="sub"><div><h2>{t['subT']}</h2><p>{t['subText']}</p></div><a class="btn" href="https://t.me/{TG}" target="_blank" rel="noopener">{t['btnTg']} ↗</a></section>
</main>
{foot(lang)}
<script>(function(){{var c=document.getElementById('chips');if(!c)return;c.addEventListener('click',function(e){{var b=e.target.closest('button');if(!b)return;c.querySelectorAll('button').forEach(function(x){{x.classList.toggle('on',x===b)}});document.querySelectorAll('#cards .card').forEach(function(k){{k.hidden=!!b.dataset.cat&&k.dataset.cat!==b.dataset.cat}})}})}})()</script>
</body></html>"""
        write(os.path.join(root, "index.html"), idx)
        blog_og(lang, force_og)
        # RSS
        items = "".join(f"""<item><title>{esc(L(p, lang)['title'])}</title><link>{post_url(lang, p['slug'])}</link><guid isPermaLink="true">{post_url(lang, p['slug'])}</guid><pubDate>{datetime.strptime(p['date'], '%Y-%m-%d').replace(hour=9, tzinfo=timezone.utc).strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate><category>{t['cats'][p['category']]}</category><description>{esc(L(p, lang)['excerpt'])}</description><enclosure url="{SITE}/blog/og/{p['slug']}-{lang}.jpg" type="image/jpeg" length="0"/></item>""" for p in posts[:30])
        write(os.path.join(root, "rss.xml"), f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>{esc(t['title'])}</title><link>{SITE}{base(lang)}</link><description>{esc(t['desc'])}</description><language>{lang}</language>{items}</channel></rss>""")
    # карта сайта блога (+ Golden Visa)
    today = datetime.now().strftime("%Y-%m-%d")
    urls = [(SITE + base(l), today) for l in LANGS] + [(f"{SITE}/golden-visa/ru/", today), (f"{SITE}/golden-visa/en/", today)]
    for p in posts: urls += [(post_url(l, p["slug"]), p["date"]) for l in LANGS]
    write(os.path.join(R, "sitemap.xml"), '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in urls) + "</urlset>\n")
    print(f"blog: {len(posts)} posts × {len(LANGS)} languages")

def blog_og(lang, force=False):
    """Картинка для ссылки на сам блог."""
    out = os.path.join(R, "og", f"blog-{lang}.jpg")
    if os.path.exists(out) and not force: return
    fake = {"slug": "blog", "category": "greece", "date": datetime.now().strftime("%Y-%m-%d"),
            "kicker": "VENI · " + TX[lang]["blog"], lang: {"title": re.sub(r"<[^>]+>", "", TX[lang]["heroH1"]), "body": ""}}
    try:
        og_image_blog(fake, lang, out)
    except Exception as e:
        print("og blog:", e)

def og_image_blog(fake, lang, out):
    from PIL import Image, ImageDraw
    tmp_slug = fake["slug"]
    # используем ту же раскладку, но без даты/цифры
    p = dict(fake); p["stat"] = None
    path = og_image(p, lang, True)
    src = os.path.join(R, "og", f"{tmp_slug}-{lang}.jpg")
    if os.path.abspath(src) != os.path.abspath(out) and os.path.exists(src): os.replace(src, out)

if __name__ == "__main__":
    build(force_og="--og" in sys.argv)
