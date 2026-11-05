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
SITE = "https://venihomes.eu"
WA = "359882593077"
TG = "home_greece"
LANGS = ["ru", "bg", "en", "de"]   # испанский убран 04.11.2026
LOCALE = {"ru": "ru_RU", "bg": "bg_BG", "en": "en_GB", "de": "de_DE", "es": "es_ES"}
COLORS = {"greece": "#1c4563", "bulgaria": "#263a36", "europe": "#4b3446"}
BLOGS = ["greece", "bulgaria"]
# Два отдельных блога. Статья попадает в блог по полю "blog" (greece|bulgaria), иначе по категории.
BX = {
"ru": {
  "greece": {"name": "Блог о Греции", "title": "Блог о недвижимости в Греции — Венера Хасанова",
    "desc": "Цены, законы, Golden Visa и жизнь у моря в Греции — простыми словами. Блог консультанта Венеры Хасановой.",
    "kicker": "Блог о Греции · свежие статьи", "h1": "Недвижимость и жизнь в Греции",
    "lead": "Цены, законы, Golden Visa и жизнь у греческого моря — простыми словами. Я сама купила здесь дом и знаю этот путь изнутри.",
    "trust": [["Северная Греция", "Кавала, Халкидики, острова"], ["Golden Visa", "ВНЖ через недвижимость"], ["Свой дом в Греции", "знаю путь изнутри"]]},
  "bulgaria": {"name": "Блог о Болгарии", "title": "Блог о недвижимости в Болгарии — Венера Хасанова",
    "desc": "Цены, налоги, ВНЖ и жизнь у моря в Болгарии — простыми словами. Блог консультанта Венеры Хасановой, офис в Бургасе.",
    "kicker": "Блог о Болгарии · свежие статьи", "h1": "Недвижимость и жизнь в Болгарии",
    "lead": "Цены, налоги, ВНЖ и жизнь на болгарском побережье — простыми словами. Живу в Болгарии с 2013 года, офис в Бургасе.",
    "trust": [["С 2013 года", "живу в Болгарии"], ["Офис в Бургасе", "более 200 сделок"], ["Всё побережье", "от Несебра до Созополя"]]},
  "landT": "Два моря — два блога", "landLead": "Я работаю в двух странах и пишу о каждой отдельно. Выберите, что вам интереснее.",
  "open": "Открыть блог", "posts": "статей", "other": {"greece": "Мой блог о Болгарии →", "bulgaria": "Мой блог о Греции →"}, "allBlogs": "Все блоги"},
"bg": {
  "greece": {"name": "Блог за Гърция", "title": "Блог за недвижими имоти в Гърция — Венера Хасанова",
    "desc": "Цени, закони, Golden Visa и живот край морето в Гърция — с прости думи. Блогът на консултанта Венера Хасанова.",
    "kicker": "Блог за Гърция · нови статии", "h1": "Имоти и живот в Гърция",
    "lead": "Цени, закони, Golden Visa и живот край гръцкото море — с прости думи. Самата аз купих къща тук и познавам пътя отвътре.",
    "trust": [["Северна Гърция", "Кавала, Халкидики, островите"], ["Golden Visa", "пребиваване чрез имот"], ["Моя къща в Гърция", "познавам пътя отвътре"]]},
  "bulgaria": {"name": "Блог за България", "title": "Блог за недвижими имоти в България — Венера Хасанова",
    "desc": "Цени, данъци, пребиваване и живот край морето в България — с прости думи. Блогът на консултанта Венера Хасанова, офис Бургас.",
    "kicker": "Блог за България · нови статии", "h1": "Имоти и живот в България",
    "lead": "Цени, данъци, пребиваване и живот по българското крайбрежие — с прости думи. Живея в България от 2013 г., офис в Бургас.",
    "trust": [["От 2013 г.", "живея в България"], ["Офис в Бургас", "над 200 сделки"], ["Цялото крайбрежие", "от Несебър до Созопол"]]},
  "landT": "Две морета — два блога", "landLead": "Работя в две държави и пиша за всяка поотделно. Изберете коя ви интересува.",
  "open": "Към блога", "posts": "статии", "other": {"greece": "Моят блог за България →", "bulgaria": "Моят блог за Гърция →"}, "allBlogs": "Всички блогове"},
"en": {
  "greece": {"name": "Greece blog", "title": "Real estate in Greece blog — Venera Khassanova",
    "desc": "Prices, laws, the Golden Visa and life by the sea in Greece — in plain words. The blog of consultant Venera Khassanova.",
    "kicker": "Greece blog · fresh articles", "h1": "Property and life in Greece",
    "lead": "Prices, laws, the Golden Visa and life by the Greek sea — in plain words. I bought a house here myself and know the path first-hand.",
    "trust": [["Northern Greece", "Kavala, Halkidiki, the islands"], ["Golden Visa", "residency through property"], ["My own house in Greece", "I know the path first-hand"]]},
  "bulgaria": {"name": "Bulgaria blog", "title": "Real estate in Bulgaria blog — Venera Khassanova",
    "desc": "Prices, taxes, residency and life by the sea in Bulgaria — in plain words. The blog of consultant Venera Khassanova, Burgas office.",
    "kicker": "Bulgaria blog · fresh articles", "h1": "Property and life in Bulgaria",
    "lead": "Prices, taxes, residency and life on the Bulgarian coast — in plain words. I have lived in Bulgaria since 2013, with an office in Burgas.",
    "trust": [["Since 2013", "living in Bulgaria"], ["Burgas office", "200+ deals"], ["The whole coast", "from Nessebar to Sozopol"]]},
  "landT": "Two seas — two blogs", "landLead": "I work in two countries and write about each one separately. Choose the one you are interested in.",
  "open": "Open the blog", "posts": "articles", "other": {"greece": "My Bulgaria blog →", "bulgaria": "My Greece blog →"}, "allBlogs": "All blogs"},
"de": {
  "greece": {"name": "Griechenland-Blog", "title": "Blog über Immobilien in Griechenland — Venera Khassanova",
    "desc": "Preise, Gesetze, Golden Visa und Leben am Meer in Griechenland — einfach erklärt. Der Blog der Beraterin Venera Khassanova.",
    "kicker": "Griechenland-Blog · neue Artikel", "h1": "Immobilien und Leben in Griechenland",
    "lead": "Preise, Gesetze, Golden Visa und Leben am griechischen Meer — einfach erklärt. Ich habe hier selbst ein Haus gekauft und kenne den Weg.",
    "trust": [["Nordgriechenland", "Kavala, Chalkidiki, Inseln"], ["Golden Visa", "Aufenthalt durch Immobilie"], ["Eigenes Haus in Griechenland", "ich kenne den Weg"]]},
  "bulgaria": {"name": "Bulgarien-Blog", "title": "Blog über Immobilien in Bulgarien — Venera Khassanova",
    "desc": "Preise, Steuern, Aufenthalt und Leben am Meer in Bulgarien — einfach erklärt. Der Blog der Beraterin Venera Khassanova, Büro Burgas.",
    "kicker": "Bulgarien-Blog · neue Artikel", "h1": "Immobilien und Leben in Bulgarien",
    "lead": "Preise, Steuern, Aufenthalt und Leben an der bulgarischen Küste — einfach erklärt. Ich lebe seit 2013 in Bulgarien, Büro in Burgas.",
    "trust": [["Seit 2013", "in Bulgarien"], ["Büro in Burgas", "über 200 Abschlüsse"], ["Die ganze Küste", "von Nessebar bis Sosopol"]]},
  "landT": "Zwei Meere — zwei Blogs", "landLead": "Ich arbeite in zwei Ländern und schreibe über jedes getrennt. Wählen Sie, was Sie interessiert.",
  "open": "Zum Blog", "posts": "Artikel", "other": {"greece": "Mein Bulgarien-Blog →", "bulgaria": "Mein Griechenland-Blog →"}, "allBlogs": "Alle Blogs"},
"es": {
  "greece": {"name": "Blog de Grecia", "title": "Blog de inmuebles en Grecia — Venera Khassanova",
    "desc": "Precios, leyes, Golden Visa y vida junto al mar en Grecia, explicado con sencillez. El blog de la asesora Venera Khassanova.",
    "kicker": "Blog de Grecia · artículos nuevos", "h1": "Inmuebles y vida en Grecia",
    "lead": "Precios, leyes, Golden Visa y vida junto al mar griego, explicado con sencillez. Compré aquí mi propia casa y conozco el camino.",
    "trust": [["Norte de Grecia", "Kavala, Calcídica, islas"], ["Golden Visa", "residencia por inversión"], ["Mi casa en Grecia", "conozco el camino"]]},
  "bulgaria": {"name": "Blog de Bulgaria", "title": "Blog de inmuebles en Bulgaria — Venera Khassanova",
    "desc": "Precios, impuestos, residencia y vida junto al mar en Bulgaria, explicado con sencillez. El blog de la asesora Venera Khassanova, oficina en Burgas.",
    "kicker": "Blog de Bulgaria · artículos nuevos", "h1": "Inmuebles y vida en Bulgaria",
    "lead": "Precios, impuestos, residencia y vida en la costa búlgara, explicado con sencillez. Vivo en Bulgaria desde 2013, con oficina en Burgas.",
    "trust": [["Desde 2013", "vivo en Bulgaria"], ["Oficina en Burgas", "más de 200 operaciones"], ["Toda la costa", "de Nesebar a Sozopol"]]},
  "landT": "Dos mares, dos blogs", "landLead": "Trabajo en dos países y escribo sobre cada uno por separado. Elija el que le interese.",
  "open": "Ir al blog", "posts": "artículos", "other": {"greece": "Mi blog de Bulgaria →", "bulgaria": "Mi blog de Grecia →"}, "allBlogs": "Todos los blogs"},
}
def nposts(n, lang):
    if lang == "ru": return "статья" if n % 10 == 1 and n % 100 != 11 else "статьи" if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14) else "статей"
    if lang == "bg": return "статия" if n == 1 else "статии"
    if lang == "en": return "article" if n == 1 else "articles"
    if lang == "es": return "artículo" if n == 1 else "artículos"
    return "Artikel"
def blog_of(p): return p.get("blog") or ("bulgaria" if p.get("category") == "bulgaria" else "greece")

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
def bbase(lang, b): return base(lang) + b + "/"
def post_url(lang, slug): return SITE + post_path(lang, slug)
def home(lang): return f"/{lang}/"
def gv(lang): return "/golden-visa/ru/" if lang == "ru" else "/golden-visa/en/"
def rel(lang): return "/relocation/" if lang == "ru" else f"/relocation/{lang}/"

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
    d.text((x, H - 70), "venihomes.eu/blog", font=sans(22), fill=gold)
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
<link rel="stylesheet" href="/blog/blog.css?v=11">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-73W576V144"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','G-73W576V144');</script>
</head>
<body>"""

def topbar(lang, alts, b=None):
    t = TX[lang]; blink = bbase(lang, b) if b else base(lang)
    cur = ' aria-current="true"'
    langs = "".join(f'<a href="{alts[l]}"{cur if l == lang else ""}>{l.upper()}</a>' for l in LANGS)
    return f"""<header class="bar">
  <a href="{home(lang)}" class="logo">VENI<span>REAL ESTATE</span></a>
  <nav class="links"><a href="{blink}" class="on">{esc(BX[lang][b]["name"]) if b else t['blog']}</a><a href="{home(lang)}#catalog">{t['catalog']}</a><a href="{rel(lang)}">{esc(RX[lang]["menu"])}</a><a href="{home(lang)}#about">{ {"ru":"Обо мне","bg":"За мен","en":"About me","de":"Über mich","es":"Sobre mí"}[lang] }</a></nav>
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


# ---------- страница «Переезд и ВНЖ» (/relocation/) ----------
# Способы взяты из статей блога «ВНЖ в Греции: все варианты» и «ВНЖ в Болгарии: все основания».
# Когда по способу выйдет подробная статья — добавьте её slug в поле "post" и ссылка появится сама.
RX = {
"ru": {"menu": "Переезд и ВНЖ", "title": "Переезд и ВНЖ в Греции и Болгарии — Венера Хасанова",
  "desc": "Все законные способы переехать в Грецию и Болгарию простыми словами: пенсия, работа, бизнес, учёба, семья, цифровые кочевники, инвестиции и Golden Visa.",
  "kicker": "Переезд и ВНЖ", "h1": "Переезд в Грецию и Болгарию — <em>все способы</em>",
  "lead": "Я сама переехала на Балканы в 2013 году и живу между Болгарией и Грецией. Здесь собраны все законные пути получить ВНЖ — от пенсии и удалённой работы до инвестиций. По каждому пути готовлю подробный разбор простыми словами.",
  "gr": "Греция", "bg": "Болгария", "soon": "Подробный разбор скоро", "read": "Читать статью →", "test": "Проверить, подходите ли вы →",
  "step": "Сначала — национальная виза D в консульстве, потом ВНЖ в Болгарии, обычно на год с продлением.",
  "helpT": "Не знаете, какой путь ваш?", "help": "Напишите мне — расскажу, какие варианты подходят вашей семье, и что нужно подготовить.", "helpB": "Написать в WhatsApp ↗",
  "wa": "Здравствуйте, Венера! Хочу узнать, как переехать в Грецию или Болгарию.",
  "routes": {
   "gr": [["Golden Visa через недвижимость", "ВНЖ на 5 лет при покупке недвижимости — от 250 000 до 800 000 € в зависимости от района.", "gv"],
          ["Golden Visa без недвижимости", "Инвестиционные варианты без покупки жилья.", None],
          ["Финансово независимые люди", "Переезд с пассивным доходом — без работы в Греции.", None],
          ["Цифровые кочевники", "Для тех, кто работает удалённо на компанию или клиентов за пределами Греции.", None],
          ["Работа, учёба и семья", "Классические основания; после 5 лет можно получить статус долгосрочного резидента.", None]],
   "bg": [["Пенсионеры", "ВНЖ для получателей пенсии.", None],
          ["Цифровые кочевники", "Для тех, кто работает удалённо.", None],
          ["Инвестиция в недвижимость", "Обычная покупка квартиры ВНЖ не даёт — только инвестиция от 600 000 левов (около 306 775 €).", None],
          ["Бизнес, работа, учёба и семья", "Свой бизнес, трудовой договор, учёба или воссоединение семьи.", None]]}},
"bg": {"menu": "Преместване и пребиваване", "title": "Преместване и пребиваване в Гърция и България — Венера Хасанова",
  "desc": "Всички законни начини да се преместите в Гърция и България с прости думи: пенсия, работа, бизнес, учене, семейство, дигитални номади, инвестиции и Golden Visa.",
  "kicker": "Преместване и пребиваване", "h1": "Преместване в Гърция и България — <em>всички начини</em>",
  "lead": "Самата аз се преместих на Балканите през 2013 г. и живея между България и Гърция. Тук са събрани всички законни пътища за пребиваване — от пенсия и дистанционна работа до инвестиции. За всеки път подготвям подробен разбор с прости думи.",
  "gr": "Гърция", "bg": "България", "soon": "Подробен разбор скоро", "read": "Прочетете статията →", "test": "Проверете дали отговаряте →",
  "step": "Първо — национална виза D в консулството, после разрешение за пребиваване в България, обикновено за година с удължаване.",
  "helpT": "Не знаете кой път е вашият?", "help": "Пишете ми — ще ви кажа кои варианти подхождат на семейството ви и какво трябва да подготвите.", "helpB": "Пишете в WhatsApp ↗",
  "wa": "Здравейте, Венера! Искам да разбера как да се преместя в Гърция или България.",
  "routes": {
   "gr": [["Golden Visa чрез имот", "Пребиваване за 5 години при покупка на имот — от 250 000 до 800 000 € според района.", "gv"],
          ["Golden Visa без имот", "Инвестиционни варианти без покупка на жилище.", None],
          ["Финансово независими лица", "Преместване с пасивен доход — без работа в Гърция.", None],
          ["Дигитални номади", "За хора, които работят дистанционно за фирма или клиенти извън Гърция.", None],
          ["Работа, учене и семейство", "Класически основания; след 5 години може да се получи статут на дългосрочно пребиваващ.", None]],
   "bg": [["Пенсионери", "Пребиваване за получатели на пенсия.", None],
          ["Дигитални номади", "За хора, които работят дистанционно.", None],
          ["Инвестиция в имот", "Обикновената покупка на жилище не дава пребиваване — само инвестиция от 600 000 лв. (около 306 775 €).", None],
          ["Бизнес, работа, учене и семейство", "Собствен бизнес, трудов договор, учене или събиране на семейството.", None]]}},
"en": {"menu": "Relocation & residency", "title": "Relocation and residency in Greece and Bulgaria — Venera Khassanova",
  "desc": "Every legal way to move to Greece and Bulgaria in plain words: retirement, work, business, study, family, digital nomads, investment and the Golden Visa.",
  "kicker": "Relocation & residency", "h1": "Moving to Greece and Bulgaria — <em>every route</em>",
  "lead": "I moved to the Balkans myself in 2013 and live between Bulgaria and Greece. Here are all the legal routes to residency — from retirement and remote work to investment. I am preparing a detailed plain-language guide for each route.",
  "gr": "Greece", "bg": "Bulgaria", "soon": "Detailed guide coming soon", "read": "Read the article →", "test": "Check if you qualify →",
  "step": "First a national D visa at the consulate, then a residence permit in Bulgaria, usually for a year with renewal.",
  "helpT": "Not sure which route is yours?", "help": "Message me — I will tell you which options suit your family and what you need to prepare.", "helpB": "Message me on WhatsApp ↗",
  "wa": "Hello Venera! I would like to know how to move to Greece or Bulgaria.",
  "routes": {
   "gr": [["Golden Visa through property", "A 5-year residence permit when you buy property — from €250,000 to €800,000 depending on the area.", "gv"],
          ["Golden Visa without property", "Investment options that do not require buying a home.", None],
          ["Financially independent persons", "Moving with passive income — without working in Greece.", None],
          ["Digital nomads", "For people working remotely for a company or clients outside Greece.", None],
          ["Work, study and family", "The classic routes; after 5 years you can apply for long-term resident status.", None]],
   "bg": [["Retirees", "Residency for people receiving a pension.", None],
          ["Digital nomads", "For people who work remotely.", None],
          ["Investment in property", "Simply buying a flat does not give residency — only an investment from 600,000 leva (about €306,775).", None],
          ["Business, work, study and family", "Your own business, an employment contract, study or family reunification.", None]]}},
"de": {"menu": "Umzug & Aufenthalt", "title": "Umzug und Aufenthalt in Griechenland und Bulgarien — Venera Khassanova",
  "desc": "Alle legalen Wege nach Griechenland und Bulgarien einfach erklärt: Rente, Arbeit, Unternehmen, Studium, Familie, digitale Nomaden, Investitionen und Golden Visa.",
  "kicker": "Umzug & Aufenthalt", "h1": "Umzug nach Griechenland und Bulgarien — <em>alle Wege</em>",
  "lead": "Ich bin 2013 selbst auf den Balkan gezogen und lebe zwischen Bulgarien und Griechenland. Hier finden Sie alle legalen Wege zur Aufenthaltserlaubnis — von Rente und Remote-Arbeit bis zur Investition. Zu jedem Weg bereite ich einen ausführlichen, einfachen Leitfaden vor.",
  "gr": "Griechenland", "bg": "Bulgarien", "soon": "Ausführlicher Leitfaden folgt", "read": "Artikel lesen →", "test": "Prüfen, ob Sie infrage kommen →",
  "step": "Zuerst ein nationales Visum D im Konsulat, dann die Aufenthaltserlaubnis in Bulgarien, meist für ein Jahr mit Verlängerung.",
  "helpT": "Nicht sicher, welcher Weg passt?", "help": "Schreiben Sie mir — ich sage Ihnen, welche Möglichkeiten zu Ihrer Familie passen und was vorzubereiten ist.", "helpB": "Per WhatsApp schreiben ↗",
  "wa": "Hallo Venera! Ich möchte wissen, wie ich nach Griechenland oder Bulgarien umziehen kann.",
  "routes": {
   "gr": [["Golden Visa durch Immobilienkauf", "Aufenthaltserlaubnis für 5 Jahre beim Immobilienkauf — von 250.000 bis 800.000 € je nach Region.", "gv"],
          ["Golden Visa ohne Immobilie", "Investitionsmöglichkeiten ohne Wohnungskauf.", None],
          ["Finanziell unabhängige Personen", "Umzug mit passivem Einkommen — ohne Arbeit in Griechenland.", None],
          ["Digitale Nomaden", "Für alle, die remote für Firmen oder Kunden außerhalb Griechenlands arbeiten.", None],
          ["Arbeit, Studium und Familie", "Die klassischen Wege; nach 5 Jahren ist der Status als langfristig Aufenthaltsberechtigter möglich.", None]],
   "bg": [["Rentner", "Aufenthalt für Rentenbezieher.", None],
          ["Digitale Nomaden", "Für alle, die remote arbeiten.", None],
          ["Investition in Immobilien", "Ein normaler Wohnungskauf gibt keinen Aufenthalt — nur eine Investition ab 600.000 Lewa (ca. 306.775 €).", None],
          ["Unternehmen, Arbeit, Studium und Familie", "Eigenes Unternehmen, Arbeitsvertrag, Studium oder Familiennachzug.", None]]}},
"es": {"menu": "Mudanza y residencia", "title": "Mudanza y residencia en Grecia y Bulgaria — Venera Khassanova",
  "desc": "Todas las vías legales para mudarse a Grecia y Bulgaria, explicadas con sencillez: jubilación, trabajo, negocio, estudios, familia, nómadas digitales, inversión y Golden Visa.",
  "kicker": "Mudanza y residencia", "h1": "Mudarse a Grecia y Bulgaria — <em>todas las vías</em>",
  "lead": "Yo misma me mudé a los Balcanes en 2013 y vivo entre Bulgaria y Grecia. Aquí están todas las vías legales para obtener la residencia, desde la jubilación y el trabajo remoto hasta la inversión. Preparo una guía detallada y sencilla para cada una.",
  "gr": "Grecia", "bg": "Bulgaria", "soon": "Guía detallada próximamente", "read": "Leer el artículo →", "test": "Compruebe si cumple →",
  "step": "Primero, un visado nacional D en el consulado; después, el permiso de residencia en Bulgaria, normalmente por un año renovable.",
  "helpT": "¿No sabe qué vía es la suya?", "help": "Escríbame: le diré qué opciones encajan con su familia y qué debe preparar.", "helpB": "Escribir por WhatsApp ↗",
  "wa": "¡Hola, Venera! Quiero saber cómo mudarme a Grecia o Bulgaria.",
  "routes": {
   "gr": [["Golden Visa con inmueble", "Residencia de 5 años al comprar un inmueble: de 250.000 a 800.000 € según la zona.", "gv"],
          ["Golden Visa sin inmueble", "Opciones de inversión sin comprar vivienda.", None],
          ["Personas económicamente independientes", "Mudarse con ingresos pasivos, sin trabajar en Grecia.", None],
          ["Nómadas digitales", "Para quien trabaja en remoto para empresas o clientes fuera de Grecia.", None],
          ["Trabajo, estudios y familia", "Las vías clásicas; tras 5 años se puede obtener la residencia de larga duración.", None]],
   "bg": [["Jubilados", "Residencia para quienes cobran una pensión.", None],
          ["Nómadas digitales", "Para quien trabaja en remoto.", None],
          ["Inversión inmobiliaria", "Comprar un piso no da la residencia: solo una inversión desde 600.000 levas (unos 306.775 €).", None],
          ["Negocio, trabajo, estudios y familia", "Negocio propio, contrato de trabajo, estudios o reagrupación familiar.", None]]}},
}
GR_POST = "greece-residence-permit-all-options-2026"     # статья «ВНЖ в Греции: все варианты»
BG_POST = "bulgaria-residence-permit-grounds-2026"       # статья «ВНЖ в Болгарии: все основания» (появится, когда опубликуете)

def build_relocation(posts):
    pub = {p["slug"] for p in posts}
    for lang in LANGS:
        t, X = TX[lang], RX[lang]
        url = SITE + rel(lang); alts = {l: SITE + rel(l) for l in LANGS}
        def col(c, post):
            items = ""
            for name, txt, link in X["routes"][c]:
                a = (f'<a href="{gv(lang)}">{X["test"]}</a>' if link == "gv" else
                     f'<a href="{post_path(lang, link)}">{X["read"]}</a>' if link in pub else f'<span class="soon">{X["soon"]}</span>')
                items += f'<li><h3>{esc(name)}</h3><p>{esc(txt)}</p>{a}</li>'
            more = f'<a class="btn" href="{post_path(lang, post)}">{X["read"]}</a>' if post in pub else ""
            step = f'<p class="r-step">{esc(X["step"])}</p>' if c == "bg" else ""
            return f'<section class="r-country c-{"greece" if c == "gr" else "bulgaria"}" id="{"greece" if c == "gr" else "bulgaria"}"><div class="r-photo"><h2>{esc(X[c])}</h2></div><ul class="routes">{items}</ul>{step}{more}</section>'
        page = f"""{head(lang, X['title'], X['desc'], url, SITE + '/assets/hero-sea.jpg', alts)}
{topbar(lang, alts)}
<main class="list land relocation">
  <section class="blog-banner c-reloc">
    <img class="mini" src="/assets/venera.jpg" alt="{esc(t['name'])}" width="160" height="160">
    <div><span class="kicker">{esc(X['kicker'])}</span><h1>{X['h1']}</h1><p class="lead">{esc(X['lead'])}</p></div>
    {buttons(lang)}
  </section>
  <div class="r-grid">{col('gr', GR_POST)}{col('bg', BG_POST)}</div>
  <aside class="cta-box"><h3>{esc(X['helpT'])}</h3><p>{esc(X['help'])}</p><a class="btn" href="https://wa.me/{WA}?text={quote(X['wa'])}" target="_blank" rel="noopener">{esc(X['helpB'])}</a></aside>
</main>
{foot(lang)}
</body></html>"""
        page = page.replace(f'class="on">{t["blog"]}<', f'>{t["blog"]}<', 1).replace(f'<a href="{rel(lang)}">', f'<a href="{rel(lang)}" class="on">', 1)
        write(os.path.join(ROOT, rel(lang).strip("/"), "index.html"), page)

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
            b = blog_of(p)
            others = [q for q in posts if q["slug"] != p["slug"] and blog_of(q) == b][:2]
            also = f'<section class="also"><h2 class="sec">{t["also"]}</h2><div class="cards two">{"".join(card(q, lang) for q in others)}</div></section>' if others else ""
            ld = json.dumps({"@context": "https://schema.org", "@type": "Article", "headline": T["title"], "description": T["excerpt"],
                             "image": img, "datePublished": p["date"], "inLanguage": lang,
                             "author": {"@type": "Person", "name": t["name"], "jobTitle": t["role"], "image": SITE + "/assets/venera.jpg", "url": SITE + base(lang)},
                             "mainEntityOfPage": url}, ensure_ascii=False)
            page = f"""{head(lang, T['title'] + ' — ' + t['name'], T['excerpt'], url, img, alts, 'article')}
<script type="application/ld+json">{ld}</script>
{topbar(lang, alts, b)}
<main class="article">
  <a class="back" href="{bbase(lang, b)}">← {esc(BX[lang][b]['name'])}</a>
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
        # главные страницы двух блогов
        X = BX[lang]
        for b in BLOGS:
            bp = [q for q in posts if blog_of(q) == b]; bx = X[b]; other = [o for o in BLOGS if o != b][0]
            alts = {l: SITE + bbase(l, b) for l in LANGS}
            trust = "".join(f"<li><b>{esc(a)}</b><span>{esc(c)}</span></li>" for a, c in bx["trust"])
            feat = f'<section class="latest"><h2 class="sec">{t["latest"]}</h2>{card(bp[0], lang, True)}</section>' if bp else f'<p class="lead">{t["empty"]}</p>'
            rest = "".join(card(q, lang) for q in bp[1:])
            grid = f'<section class="list-all"><div class="list-head"><h2 class="sec">{t["allPosts"]}</h2></div><div class="cards" id="cards">{rest}</div></section>' if len(bp) > 1 else ""
            idx = f"""{head(lang, bx['title'], bx['desc'], SITE + bbase(lang, b), SITE + '/blog/og/blog-' + lang + '.jpg', alts)}
{topbar(lang, alts, b)}
<main class="list land blog-{b}">
  <a class="back" href="{base(lang)}">← {esc(X['allBlogs'])}</a>
  <section class="blog-banner c-{b}">
    <img class="mini" src="/assets/venera.jpg" alt="{esc(t['name'])}" width="160" height="160">
    <div>
      <span class="kicker">{esc(bx['kicker'])}</span>
      <h1>{bx['h1']}</h1>
      <p class="lead">{esc(bx['lead'])}</p>
    </div>
    {buttons(lang)}
  </section>
  {feat}
  {grid}
  <p class="other-blog"><a href="{bbase(lang, other)}">{esc(X['other'][b])}</a></p>
  <section class="sub"><div><h2>{t['subT']}</h2><p>{t['subText']}</p></div><a class="btn" href="https://t.me/{TG}" target="_blank" rel="noopener">{t['btnTg']} ↗</a></section>
</main>
{foot(lang)}
</body></html>"""
            write(os.path.join(root, b, "index.html"), idx)
            open(os.path.join(root, b, ".generated"), "w").close()
        # лендинг /blog/: два блога рядом
        alts = {l: SITE + base(l) for l in LANGS}
        def bcard(b):
            bp = [q for q in posts if blog_of(q) == b]; last = bp[0] if bp else None
            lt = f'<span class="b-last">{esc(t["latest"])}: <b>{esc(L(last, lang)["title"])}</b></span>' if last else ""
            return (f'<a class="blog-pick c-{b}" href="{bbase(lang, b)}"><span class="kicker">{esc(t["cats"][b])} · {len(bp)} {esc(nposts(len(bp), lang))}</span>'
                    f'<strong>{esc(X[b]["name"])}</strong><span class="b-desc">{esc(X[b]["desc"])}</span>{lt}<span class="btn">{esc(X["open"])} →</span></a>')
        idx = f"""{head(lang, t['title'], t['desc'], SITE + base(lang), SITE + '/blog/og/blog-' + lang + '.jpg', alts)}
{topbar(lang, alts)}
<main class="list land">
  <section class="land-head">
    <img class="mini" src="/assets/venera.jpg" alt="{esc(t['name'])}" width="160" height="160">
    <div>
      <span class="kicker">{t['heroKicker']}</span>
      <h1>{esc(X['landT'])}</h1>
      <p class="lead">{esc(X['landLead'])}</p>
    </div>
    {buttons(lang)}
  </section>
  <section class="blog-picks">{bcard('greece')}{bcard('bulgaria')}</section>
  <section class="sub"><div><h2>{t['subT']}</h2><p>{t['subText']}</p></div><a class="btn" href="https://t.me/{TG}" target="_blank" rel="noopener">{t['btnTg']} ↗</a></section>
</main>
{foot(lang)}
</body></html>"""
        write(os.path.join(root, "index.html"), idx)
        blog_og(lang, force_og)
        # RSS
        items = "".join(f"""<item><title>{esc(L(p, lang)['title'])}</title><link>{post_url(lang, p['slug'])}</link><guid isPermaLink="true">{post_url(lang, p['slug'])}</guid><pubDate>{datetime.strptime(p['date'], '%Y-%m-%d').replace(hour=9, tzinfo=timezone.utc).strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate><category>{t['cats'][p['category']]}</category><description>{esc(L(p, lang)['excerpt'])}</description><enclosure url="{SITE}/blog/og/{p['slug']}-{lang}.jpg" type="image/jpeg" length="0"/></item>""" for p in posts[:30])
        write(os.path.join(root, "rss.xml"), f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>{esc(t['title'])}</title><link>{SITE}{base(lang)}</link><description>{esc(t['desc'])}</description><language>{lang}</language>{items}</channel></rss>""")
    # карта сайта блога (+ Golden Visa)
    today = datetime.now().strftime("%Y-%m-%d")
    urls = [(SITE + base(l), today) for l in LANGS] + [(SITE + bbase(l, b), today) for l in LANGS for b in BLOGS] + [(f"{SITE}/golden-visa/ru/", today), (f"{SITE}/golden-visa/en/", today)] + [(SITE + rel(l), today) for l in LANGS]
    for p in posts: urls += [(post_url(l, p["slug"]), p["date"]) for l in LANGS]
    write(os.path.join(R, "sitemap.xml"), '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in urls) + "</urlset>\n")
    build_relocation(posts)
    print(f"blog: {len(posts)} posts × {len(LANGS)} languages + relocation")

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
