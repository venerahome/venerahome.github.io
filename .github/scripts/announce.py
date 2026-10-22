#!/usr/bin/env python3
"""Анонс новых статей блога в Telegram-группу и на страницу Facebook.
Запускается GitHub Action'ом после публикации. Берёт файлы статей, добавленные в этом push.
Ключи — в секретах репозитория (Settings → Secrets and variables → Actions):
  TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID   — бот и группа/канал
  FB_PAGE_ID, FB_PAGE_TOKEN              — страница Facebook
Если ключей нет — этот канал просто пропускается. Язык анонса: переменная POST_LANG (ru по умолчанию)."""
import os, sys, json, html, urllib.request, urllib.parse

SITE = "https://venerahome.github.io"
LANG = (os.environ.get("POST_LANG") or "ru").strip()
TAGS = {"ru": {"greece": "#Греция", "bulgaria": "#Болгария", "europe": "#Европа"},
        "en": {"greece": "#Greece", "bulgaria": "#Bulgaria", "europe": "#Europe"}}
MORE = {"ru": "Читать статью →", "en": "Read the article →"}

def url_for(p):
    return f"{SITE}/blog/{'' if LANG == 'ru' else 'en/'}{p['slug']}/"

def post(url, data):
    req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(), method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

def telegram(p):
    tok, chat = os.environ.get("TELEGRAM_BOT_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    if not tok or not chat: print("Telegram: ключи не заданы — пропускаю"); return True
    L = p[LANG]; link = url_for(p)
    text = (f"<b>{html.escape(L['title'])}</b>\n\n{html.escape(L['excerpt'])}\n\n"
            f"<a href=\"{link}\">{MORE[LANG]}</a>\n\n{TAGS[LANG].get(p['category'], '')}")
    r = post(f"https://api.telegram.org/bot{tok}/sendMessage", {
        "chat_id": chat, "text": text, "parse_mode": "HTML",
        "link_preview_options": json.dumps({"url": link, "prefer_large_media": True, "show_above_text": True})})
    print("Telegram:", "ok" if r.get("ok") else r); return bool(r.get("ok"))

def facebook(p):
    page, tok = os.environ.get("FB_PAGE_ID"), os.environ.get("FB_PAGE_TOKEN")
    if not page or not tok: print("Facebook: ключи не заданы — пропускаю"); return True
    L = p[LANG]
    msg = f"{L['title']}\n\n{L['excerpt']}\n\n{TAGS[LANG].get(p['category'], '')}"
    try:
        r = post(f"https://graph.facebook.com/v21.0/{page}/feed", {"message": msg, "link": url_for(p), "access_token": tok})
    except urllib.error.HTTPError as e:
        print("Facebook: ошибка", e.code, e.read().decode()[:300]); return False
    print("Facebook:", "ok" if r.get("id") else r); return bool(r.get("id"))

def main(files):
    ok = True
    for f in files:
        if not (f.startswith("blog/posts/") and f.endswith(".json")) or not os.path.exists(f): continue
        p = json.load(open(f, encoding="utf-8"))
        if p.get("status", "published") != "published": continue
        print("Статья:", p["slug"])
        ok = telegram(p) and ok
        ok = facebook(p) and ok
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main([x for x in sys.argv[1:] if x])
