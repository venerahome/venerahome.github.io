#!/usr/bin/env python3
"""Создаёт языковые страницы /bg/, /ru/, /en/, /de/, /es/ из index.html.
У каждой свой заголовок и описание, чтобы превью ссылки в Viber, WhatsApp
и Facebook показывалось на нужном языке. Запускается из update_listings.py."""
import os, re
R = os.path.dirname(os.path.abspath(__file__))
SITE = "https://venerahome.github.io"
META = {
  "bg": ("VENI — вашият личен консултант по недвижими имоти", "Апартаменти, къщи и вили в Гърция. Личен подход от Венера Хасанова — от избора до ключовете.", "bg_BG"),
  "ru": ("VENI — ваш личный консультант по недвижимости", "Квартиры, дома и виллы в Греции. Личный подход Венеры Хасановой — от выбора до ключей.", "ru_RU"),
  "en": ("VENI — your personal real estate consultant", "Apartments, houses and villas in Greece. Venera Hasanova's personal approach, from choice to keys.", "en_GB"),
  "de": ("VENI — Ihre persönliche Immobilienberaterin", "Wohnungen, Häuser und Villen in Griechenland. Persönliche Begleitung von Venera Hasanova, von der Auswahl bis zum Schlüssel.", "de_DE"),
  "es": ("VENI — su asesora inmobiliaria personal", "Pisos, casas y villas en Grecia. El trato personal de Venera Hasanova, de la elección a las llaves.", "es_ES"),
}
src = open(os.path.join(R, "index.html"), encoding="utf-8").read()
for l, (title, desc, loc) in META.items():
    h = src
    h = re.sub(r'<html lang="[^"]*">', f'<html lang="{l}">', h, count=1)
    h = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", h, count=1)
    h = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{desc}">', h, count=1)
    h = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{title}">', h, count=1)
    h = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{desc}">\n<meta property="og:locale" content="{loc}">', h, count=1)
    h = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{SITE}/{l}/">\n<link rel="canonical" href="{SITE}/{l}/">', h, count=1)
    h = h.replace('href="./assets/', 'href="../assets/').replace('src="./assets/', 'src="../assets/')
    h = h.replace('<script src="../assets/listings.js', f'<script>window.PAGE_LANG="{l}"</script>\n<script src="../assets/listings.js', 1)
    os.makedirs(os.path.join(R, l), exist_ok=True)
    open(os.path.join(R, l, "index.html"), "w", encoding="utf-8").write(h)
print("pages:", ", ".join(META))
