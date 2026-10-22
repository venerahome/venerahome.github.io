#!/usr/bin/env python3
"""Собирает страницу Golden Visa: /golden-visa/ (язык по браузеру), /golden-visa/ru/, /golden-visa/en/ из gv-template.html.
Тексты страницы — в gv.js, оформление — в gv.css."""
import os
R = os.path.dirname(os.path.abspath(__file__))
SITE = "https://venihomes.eu/golden-visa/"
META = {
  "ru": ("ВНЖ в Греции через недвижимость — Golden Visa | VENI", "ВНЖ в Евросоюзе для всей семьи через дом у моря в Северной Греции. Подбор объекта от 250 000 € и сопровождение до получения ВНЖ."),
  "en": ("Greece Golden Visa through real estate | VENI", "EU residency for your whole family through a seaside home in Northern Greece. Properties from €250,000 and full support until you get your permit."),
}
tpl = open(os.path.join(R, "gv-template.html"), encoding="utf-8").read()
def page(lang, page_lang, url, out):
    t, d = META[lang]
    h = (tpl.replace("{{LANG}}", lang).replace("{{TITLE}}", t).replace("{{DESC}}", d)
            .replace("{{URL}}", url).replace("{{HOMELANG}}", lang))
    h = h.replace(f'window.PAGE_LANG = "{lang}"', f'window.PAGE_LANG = "{page_lang}"')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(h)
page("ru", "ru", SITE + "ru/", os.path.join(R, "ru", "index.html"))
page("en", "en", SITE + "en/", os.path.join(R, "en", "index.html"))
page("en", "auto", SITE, os.path.join(R, "index.html"))   # язык выбирается по браузеру
print("golden-visa pages: /golden-visa/, /ru/, /en/")
