#!/usr/bin/env python3
"""Публикует НОВЫЕ объекты (дома, квартиры, виллы) в Telegram-канал на русском.
Запускается GitHub Action'ом при изменении data/listings.json.
Сравнивает список объектов до и после push: новые коды = новые объекты.
Ключи — те же секреты, что и для блога: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID.
Использование: announce_listings.py <старый listings.json> <новый listings.json> [код ...]
Если переданы коды — публикуются только они (ручной повтор)."""
import os, sys, json, html, time, urllib.request, urllib.parse, urllib.error

SITE = "https://venihomes.eu"
TYPES = {"apt": "Квартира", "house": "Дом", "villa": "Вилла"}   # что публикуем
MAX_POSTS = 8          # защита от «флуда» при массовом импорте
EMOJI = {"apt": "🏢", "house": "🏡", "villa": "🏖"}

def load(path):
    try:
        return json.load(open(path, encoding="utf-8"))
    except Exception:
        return {"listings": [], "places": {}}

def money(n):
    return f"{int(n):,}".replace(",", " ") + " €"

def abs_url(u):
    return u if u.startswith("http") else SITE + (u if u.startswith("/") else "/" + u)

def caption(p, places):
    ru = lambda o: (o or {}).get("ru") or ""
    place = ru(places.get(p.get("place"))) or p.get("place", "")
    where = ", ".join(x for x in [place, ru(p.get("district"))] if x)
    facts = []
    if p.get("area"): facts.append(f"{p['area']} м²")
    if p.get("bedrooms"): facts.append(f"спален: {p['bedrooms']}")
    if p.get("plot"): facts.append(f"участок {p['plot']} м²")
    if p.get("sea") == 0: facts.append("первая линия")
    elif isinstance(p.get("sea"), (int, float)) and not isinstance(p.get("sea"), bool) and p.get("sea") > 0: facts.append(f"до моря {p['sea']} м")
    link = f"{SITE}/ru/#object-{p['code']}"
    desc = ru(p.get("desc"))
    feats = (p.get("feat") or {}).get("ru") or []
    head = (f"{EMOJI.get(p['type'], '🏠')} <b>{html.escape(ru(p.get('title')))}</b>\n\n"
            f"💶 <b>{money(p['price'])}</b>\n📍 {html.escape(where)}\n"
            + (f"📐 {html.escape(' · '.join(facts))}\n" if facts else "")
            + ("🎬 Есть видео\n" if (p.get("videos") or p.get("video")) else ""))
    tail = (("\n" + "\n".join("✔️ " + html.escape(f) for f in feats[:4]) + "\n" if feats else "")
            + f"\n👉 <a href=\"{link}\">Смотреть объект на сайте</a>\n"
            + "📩 Пишите — отвечу лично: @venera_kh_happy\n\n#Греция #недвижимость")
    room = 1024 - len(head) - len(tail) - 10          # лимит подписи к фото в Telegram
    if room > 80 and desc:
        d = desc if len(desc) <= room else desc[:room].rsplit(" ", 1)[0] + "…"
        head += "\n" + html.escape(d) + "\n"
    return head + tail

def api(method, data):
    tok = os.environ["TELEGRAM_BOT_TOKEN"]
    req = urllib.request.Request(f"https://api.telegram.org/bot{tok}/{method}",
                                 data=urllib.parse.urlencode(data).encode(), method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return {"ok": False, "error": e.read().decode()[:300]}

def publish(p, places):
    chat = os.environ["TELEGRAM_CHAT_ID"]
    cap = caption(p, places)
    photos = [abs_url(u) for u in (p.get("photos") or [])][:5]
    if len(photos) >= 2:
        media = [{"type": "photo", "media": u} for u in photos]
        media[0].update({"caption": cap, "parse_mode": "HTML"})
        r = api("sendMediaGroup", {"chat_id": chat, "media": json.dumps(media)})
        if r.get("ok"): return True
        print("  альбом не ушёл, пробую одно фото:", r.get("error") or r)
    if photos:
        r = api("sendPhoto", {"chat_id": chat, "photo": photos[0], "caption": cap, "parse_mode": "HTML"})
        if r.get("ok"): return True
        print("  фото не ушло, отправляю текстом:", r.get("error") or r)
    r = api("sendMessage", {"chat_id": chat, "text": cap, "parse_mode": "HTML"})
    print("  текст:", "ok" if r.get("ok") else r)
    return bool(r.get("ok"))

def main():
    if not os.environ.get("TELEGRAM_BOT_TOKEN") or not os.environ.get("TELEGRAM_CHAT_ID"):
        print("Telegram: ключи не заданы — пропускаю"); return 0
    old, new = load(sys.argv[1]), load(sys.argv[2])
    only = {int(x) for x in sys.argv[3:] if x.strip().isdigit()}
    old_codes = {l["code"] for l in old["listings"]}
    if only:
        fresh = [l for l in new["listings"] if l["code"] in only]
    else:
        fresh = [l for l in new["listings"] if l["code"] not in old_codes and l.get("type") in TYPES
                 and l.get("deal", "sale") == "sale"]
    print("Новых объектов для публикации:", len(fresh))
    if len(fresh) > MAX_POSTS:
        print(f"Слишком много сразу ({len(fresh)}) — публикую первые {MAX_POSTS}")
        fresh = fresh[:MAX_POSTS]
    ok = True
    for i, p in enumerate(fresh):
        print("Объект", p["code"], (p.get("title") or {}).get("ru", ""))
        ok = publish(p, new.get("places", {})) and ok
        if i < len(fresh) - 1: time.sleep(4)
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
