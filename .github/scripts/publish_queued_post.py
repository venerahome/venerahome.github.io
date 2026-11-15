#!/usr/bin/env python3
"""Публикует ОДНУ статью из очереди blog/queue/ (по порядку имён файлов) — раз в день.
Ставит сегодняшнюю дату (по Софии), переносит файл в blog/posts/ГГГГ-ММ-ДД-slug.json и пишет путь в GITHUB_OUTPUT (file=...).
Если сегодня статья из очереди уже выходила (blog/queue/state.json) или очередь пуста — ничего не делает."""
import os, json, glob
from datetime import datetime
from zoneinfo import ZoneInfo

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
Q = os.path.join(R, "blog", "queue")
STATE = os.path.join(Q, "state.json")
today = datetime.now(ZoneInfo("Europe/Sofia")).strftime("%Y-%m-%d")
state = json.load(open(STATE)) if os.path.exists(STATE) else {}
out = os.environ.get("GITHUB_OUTPUT")
def emit(k, v):
    print(f"{k}={v}")
    if out: open(out, "a").write(f"{k}={v}\n")

files = sorted(f for f in glob.glob(os.path.join(Q, "*.json")) if not f.endswith("state.json"))
if state.get("last_day") == today and not os.environ.get("FORCE"):
    print("Сегодня статья уже вышла"); emit("file", ""); raise SystemExit(0)
if not files:
    print("Очередь пуста"); emit("file", ""); raise SystemExit(0)
src = files[0]
p = json.load(open(src, encoding="utf-8"))
p["date"] = today
p["status"] = "published"
dst = os.path.join(R, "blog", "posts", f"{today}-{p['slug']}.json")
json.dump(p, open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
os.remove(src)
state["last_day"] = today
state.setdefault("published", []).append({"day": today, "slug": p["slug"]})
json.dump(state, open(STATE, "w"), ensure_ascii=False, indent=1)
print("Публикую:", p["slug"], "| осталось в очереди:", len(files) - 1)
emit("file", os.path.relpath(dst, R))
