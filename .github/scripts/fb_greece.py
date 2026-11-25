#!/usr/bin/env python3
"""Автопостинг на страницу Facebook «Veni Homes - Имоти в Гърция» (только на болгарском).

Расписание (время Софии):
  Пн, Ср, Пт  09:00 — статья из блога (Греция / сравнение)      19:00 — объект
  Вт, Чт      09:00 — объект                                      19:00 — объект
  Сб, Вс      —                                                   19:00 — объект

Объект: все фото одним постом + полный текст на болгарском + в конце ссылка на сайт и телефон.
Объекты не повторяются, пока не выйдут все; новые объекты идут вне очереди.
Когда выйдут все — начинается новый круг с пометкой «Все още е наличен».

Ключ страницы — секрет FB_GR_PAGE_TOKEN, ID страницы — FB_GR_PAGE_ID.
Что уже вышло — data/fb_greece_state.json.

Запуск:  fb_greece.py            — проверить время и опубликовать, если пора
         fb_greece.py --force listing|blog   — опубликовать сейчас (ручной запуск)
         fb_greece.py --dry ...  — только показать текст, ничего не публиковать
"""
import os, re, sys, json, glob, time, urllib.request, urllib.parse, urllib.error
from datetime import datetime
from zoneinfo import ZoneInfo

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = "https://venihomes.eu"
STATE = os.path.join(R, "data", "fb_greece_state.json")
PHONE = "+359 882 593 077"
GRAPH = "https://graph.facebook.com/v21.0"
MAX_PHOTOS = 30
TYPES = {"apt": "Апартамент", "house": "Къща", "villa": "Вила"}
EMOJI = {"apt": "🏢", "house": "🏡", "villa": "🏖"}

# день недели (0 = понедельник) → что выходит утром и вечером
PLAN = {0: ("blog", "listing"), 1: ("listing", "listing"), 2: ("blog", "listing"),
        3: ("listing", "listing"), 4: ("blog", "listing"), 5: (None, "listing"), 6: (None, "listing")}
MORNING, EVENING = 9, 19          # публикуем при первом запуске после этого часа
LATE = {MORNING: 13, EVENING: 23}  # позже этого часа слот пропускаем (чтобы не постить ночью)

DRY = "--dry" in sys.argv


def load_state():
    try:
        s = json.load(open(STATE, encoding="utf-8"))
    except Exception:
        s = {}
    s.setdefault("listings_posted", []); s.setdefault("listings_known", None)
    s.setdefault("round", 1); s.setdefault("blog_posted", []); s.setdefault("slots_done", [])
    return s


def save_state(s):
    s["slots_done"] = s["slots_done"][-30:]
    json.dump(s, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def money(n):
    return f"{int(n):,}".replace(",", " ") + " €"


def abs_url(u):
    return u if u.startswith("http") else SITE + (u if u.startswith("/") else "/" + u)


def clean_desc(t):
    # служебные коды в конце объявления («Код: ЕГ», «Код: ПИР», ROMAN) — только для Венеры
    t = re.sub(r"\s*Код:\s*\S+\s*$", "", t or "").strip()
    return re.sub(r"\s*\bROMAN\b\s*$", "", t).strip()


# ---------- Facebook ----------
def fb(path, data):
    page, tok = os.environ.get("FB_GR_PAGE_ID"), os.environ.get("FB_GR_PAGE_TOKEN")
    req = urllib.request.Request(f"{GRAPH}/{path.format(page=page)}",
                                 data=urllib.parse.urlencode(dict(data, access_token=tok)).encode(), method="POST")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": e.read().decode()[:400]}
    except Exception as e:
        return {"error": str(e)[:400]}


def post_with_photos(text, photos):
    if DRY:
        print(f"[проба] {len(photos)} фото\n{text}\n"); return True
    ids = []
    for u in photos[:MAX_PHOTOS]:
        r = fb("{page}/photos", {"url": u, "published": "false"})
        if r.get("id"): ids.append(r["id"])
        else: print("  фото не загрузилось:", u, r.get("error"))
    if not ids:
        r = fb("{page}/feed", {"message": text})
    else:
        data = {"message": text}
        for i, x in enumerate(ids):
            data[f"attached_media[{i}]"] = json.dumps({"media_fbid": x})
        r = fb("{page}/feed", data)
    print("  Facebook:", "ok " + r["id"] if r.get("id") else r)
    return bool(r.get("id"))


# ---------- объекты ----------
def listing_text(p, places, again):
    bg = lambda o: (o or {}).get("bg") or ""
    where = ", ".join(x for x in [bg(places.get(p.get("place"))) or p.get("place", ""), bg(p.get("district"))] if x)
    facts = []
    if p.get("area"): facts.append(f"{p['area']} м²")
    if p.get("bedrooms"): facts.append(f"спални: {p['bedrooms']}")
    if p.get("bathrooms"): facts.append(f"бани: {p['bathrooms']}")
    if p.get("floor"): facts.append(f"етаж: {p['floor']}")
    if p.get("plot"): facts.append(f"парцел {p['plot']} м²")
    sea = p.get("sea")
    if sea == 0: facts.append("първа линия")
    elif isinstance(sea, (int, float)) and not isinstance(sea, bool) and sea > 0: facts.append(f"до морето {sea} м")
    if p.get("furnished"): facts.append("обзаведен")
    feats = (p.get("feat") or {}).get("bg") or []
    lines = []
    if again: lines.append("🔔 Все още е наличен!\n")
    lines.append(f"{EMOJI.get(p['type'], '🏠')} {bg(p.get('title'))}\n")
    lines.append(f"💶 {money(p['price'])}")
    lines.append(f"📍 {where}, Гърция")
    if facts: lines.append("📐 " + " · ".join(facts))
    desc = clean_desc(bg(p.get("desc")))
    if desc: lines.append("\n" + desc)
    if feats: lines.append("\n" + "\n".join("✔️ " + f for f in feats))
    lines.append(f"\n👉 Повече снимки и информация: {SITE}/bg/greece/#object-{p['code']}")
    lines.append(f"📞 {PHONE} (Viber, WhatsApp)")
    lines.append("\n#Гърция #Кавала #имотивГърция #VeniHomes")
    return "\n".join(lines)


def pick_listing(s, data):
    pool = [l for l in data["listings"] if l.get("country") == "gr" and l.get("type") in TYPES
            and l.get("deal", "sale") == "sale" and l.get("status", "sale") == "sale" and l.get("photos")]
    codes = [l["code"] for l in pool]
    if s["listings_known"] is None:        # первый запуск: все текущие объекты считаем «известными»
        s["listings_known"] = codes
    known = set(s["listings_known"])
    posted = set(s["listings_posted"])
    fresh = [l for l in pool if l["code"] not in known and l["code"] not in posted]   # новые — вне очереди
    rest = [l for l in pool if l["code"] in known and l["code"] not in posted]
    rest.sort(key=lambda l: (l.get("source") != "veni", not l.get("featured")))       # сначала свои объекты
    if not fresh and not rest and pool:
        s["round"] += 1; s["listings_posted"] = []
        print("Все объекты уже выходили — начинаю новый круг", s["round"])
        return pick_listing(s, data)
    return (fresh + rest)[0] if (fresh or rest) else None


def do_listing(s):
    data = json.load(open(os.path.join(R, "data", "listings.json"), encoding="utf-8"))
    p = pick_listing(s, data)
    if not p: print("Нет объектов для публикации"); return True
    again = s["round"] > 1 and p["code"] in set(s["listings_known"])
    print("Объект", p["code"], (p.get("title") or {}).get("bg", ""))
    ok = post_with_photos(listing_text(p, data.get("places", {}), again), [abs_url(u) for u in p["photos"]])
    if ok and not DRY:
        s["listings_posted"].append(p["code"])
        if p["code"] not in s["listings_known"]: s["listings_known"].append(p["code"])
    return ok


# ---------- блог ----------
def is_greek(p):
    return p.get("category") in ("greece", "compare") or p.get("blog") in ("greece", "both")


def do_blog(s):
    posts = []
    for f in glob.glob(os.path.join(R, "blog", "posts", "*.json")):
        p = json.load(open(f, encoding="utf-8"))
        if p.get("status", "published") == "published" and is_greek(p) and p.get("bg", {}).get("title") \
                and p["slug"] not in s["blog_posted"]:
            posts.append(p)
    if not posts: print("Новых статей про Грецию нет — пропускаю"); return True
    p = max(posts, key=lambda x: x.get("date", ""))          # самая свежая из ещё не опубликованных
    L = p["bg"]; link = f"{SITE}/blog/bg/{p['slug']}/"
    tags = "#Гърция #България #имоти #VeniHomes" if p.get("category") == "compare" else "#Гърция #имотивГърция #VeniHomes"
    text = f"📰 {L['title']}\n\n{L.get('excerpt', '')}\n\n👉 Прочетете статията: {link}\n\n{tags}"
    print("Статья", p["slug"])
    if DRY:
        print(f"[проба]\n{text}\n"); return True
    r = fb("{page}/feed", {"message": text, "link": link})
    print("  Facebook:", "ok " + r["id"] if r.get("id") else r)
    if r.get("id"): s["blog_posted"].append(p["slug"])
    return bool(r.get("id"))


def main():
    if not DRY and not (os.environ.get("FB_GR_PAGE_ID") and os.environ.get("FB_GR_PAGE_TOKEN")):
        print("Нет ключей FB_GR_PAGE_ID / FB_GR_PAGE_TOKEN — ничего не публикую"); return 1
    s = load_state()
    if "--force" in sys.argv:
        kind = sys.argv[sys.argv.index("--force") + 1]
        ok = do_blog(s) if kind == "blog" else do_listing(s)
        if not DRY: save_state(s)
        return 0 if ok else 1
    now = datetime.now(ZoneInfo("Europe/Sofia"))
    day = now.strftime("%Y-%m-%d"); plan = PLAN[now.weekday()]
    todo = None
    for hour, kind in ((EVENING, plan[1]), (MORNING, plan[0])):
        slot = f"{day}-{hour}"
        if kind and hour <= now.hour < LATE[hour] and slot not in s["slots_done"]:
            todo = (slot, kind); break
    if not todo:
        print("Сейчас", now.strftime("%a %H:%M"), "— публиковать нечего"); return 0
    slot, kind = todo
    print("Слот", slot, "→", kind)
    ok = do_blog(s) if kind == "blog" else do_listing(s)
    if ok and not DRY: s["slots_done"].append(slot)
    if not DRY: save_state(s)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
