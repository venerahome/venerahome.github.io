#!/usr/bin/env python3
"""Создаёт языковые страницы /bg/, /ru/, /en/, /de/, /es/ из index.html
и витрины стран /{язык}/greece/ и /{язык}/bulgaria/.
У каждой свой заголовок и описание, чтобы превью ссылки в Viber, WhatsApp
и Facebook показывалось на нужном языке. Запускается из update_listings.py."""
import os, re
R = os.path.dirname(os.path.abspath(__file__))
SITE = "https://venihomes.eu"
LANGS = ["bg", "ru", "en", "de"]
META = {
  "bg": ("VENI — вашият личен консултант по недвижими имоти", "Апартаменти, къщи и вили в Гърция и България. Личен подход от Венера Хасанова — от избора до ключовете.", "bg_BG"),
  "ru": ("VENI — ваш личный консультант по недвижимости", "Квартиры, дома и виллы в Греции и Болгарии. Личный подход Венеры Хасановой — от выбора до ключей.", "ru_RU"),
  "en": ("VENI — your personal real estate consultant", "Apartments, houses and villas in Greece and Bulgaria. Venera Khassanova's personal approach, from choice to keys.", "en_GB"),
  "de": ("VENI — Ihre persönliche Immobilienberaterin", "Wohnungen, Häuser und Villen in Griechenland und Bulgarien. Persönliche Begleitung von Venera Khassanova, von der Auswahl bis zum Schlüssel.", "de_DE"),
}
COUNTRY = {  # витрины стран: (заголовок, описание)
  "greece": {
    "bg": ("Имоти в Гърция — VENI", "Къщи до морето, вили и апартаменти в Северна Гърция, Халкидики и островите. Имоти за Златна виза. Венера Хасанова."),
    "ru": ("Недвижимость в Греции — VENI", "Дома у моря, виллы и квартиры в Северной Греции, на Халкидиках и островах. Объекты под Золотую визу. Венера Хасанова."),
    "en": ("Property in Greece — VENI", "Seaside houses, villas and flats in Northern Greece, Halkidiki and the islands. Golden Visa options. Venera Khassanova."),
    "de": ("Immobilien in Griechenland — VENI", "Häuser am Meer, Villen und Wohnungen in Nordgriechenland, Chalkidiki und auf den Inseln. Golden Visa. Venera Khassanova."),
  },
  "bulgaria": {
    "bg": ("Имоти в България — VENI", "Апартаменти, къщи, парцели и търговски имоти в Бургас, Слънчев бряг, Несебър, Свети Влас и по морето. Венера Хасанова."),
    "ru": ("Недвижимость в Болгарии — VENI", "Квартиры, дома, участки и коммерция в Бургасе, Солнечном береге, Несебре, Святом Власе и у моря. Венера Хасанова."),
    "en": ("Property in Bulgaria — VENI", "Flats, houses, plots and commercial property in Burgas, Sunny Beach, Nessebar, Sveti Vlas and along the coast. Venera Khassanova."),
    "de": ("Immobilien in Bulgarien — VENI", "Wohnungen, Häuser, Grundstücke und Gewerbe in Burgas, Sonnenstrand, Nessebar, Sveti Vlas und an der Küste. Venera Khassanova."),
  },
}
CODE = {"greece": "gr", "bulgaria": "bg"}
src = open(os.path.join(R, "index.html"), encoding="utf-8").read()

def page(l, title, desc, loc, sub=""):
    h = src
    path = f"/{l}/" + (sub + "/" if sub else "")
    h = re.sub(r'<html lang="[^"]*">', f'<html lang="{l}">', h, count=1)
    h = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", h, count=1)
    h = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{desc}">', h, count=1)
    h = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{title}">', h, count=1)
    h = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{desc}">\n<meta property="og:locale" content="{loc}">', h, count=1)
    h = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{SITE}{path}">\n<link rel="canonical" href="{SITE}{path}">', h, count=1)
    if sub:  # альтернативные языки ведут на ту же витрину
        h = re.sub(r'(hreflang="(bg|ru|en|de|es)" href="https://venihomes\.eu/\2/)"', rf'\1{sub}/"', h)
        h = h.replace('hreflang="x-default" href="https://venihomes.eu/"', f'hreflang="x-default" href="https://venihomes.eu/ru/{sub}/"')
    up = "../../" if sub else "../"
    h = h.replace('href="./assets/', f'href="{up}assets/').replace('src="./assets/', f'src="{up}assets/')
    js = f'window.PAGE_LANG="{l}"' + (f';window.PAGE_COUNTRY="{CODE[sub]}"' if sub else "")
    h = h.replace(f'<script src="{up}assets/listings.js', f'<script>{js}</script>\n<script src="{up}assets/listings.js', 1)
    d = os.path.join(R, l, sub) if sub else os.path.join(R, l)
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(h)

for l, (title, desc, loc) in META.items():
    page(l, title, desc, loc)
    for sub, by in COUNTRY.items():
        t, d = by[l]
        page(l, t, d, loc, sub)
print("pages:", ", ".join(META), "+ greece/bulgaria")
