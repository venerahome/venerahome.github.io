#!/usr/bin/env python3
"""Подтягивает фото для объектов с полем "drive" (публичная папка Google Drive):
берёт список файлов папки и записывает ссылки на картинки в photos.
Запускается GitHub Action'ом (drive-photos.yml). Повторный запуск обновляет только объекты без фото,
или все — с аргументом --all."""
import json, re, sys, time, urllib.request
PATH = "data/listings.json"
MAX = 15

def folder_files(fid, depth=0):
    req = urllib.request.Request(f"https://drive.google.com/embeddedfolderview?id={fid}", headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
    out = []
    for kind, i, name in re.findall(r'<a href="https://drive\.google\.com/(file/d|drive/folders)/([^/?"]+)[^"]*"[^>]*>[\s\S]*?class="flip-entry-title">([^<]*)<', html):
        if kind == "file/d": out.append((name, i))
        elif depth < 2: out += folder_files(i, depth + 1)
    return out

def natkey(s): return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]

def main():
    every = "--all" in sys.argv
    d = json.load(open(PATH, encoding="utf-8"))
    changed = 0
    for p in d["listings"]:
        if not p.get("drive") or (p.get("photos") and not every): continue
        try:
            files = folder_files(p["drive"])
        except Exception as e:
            print(p["code"], "ошибка:", e); continue
        imgs = sorted([f for f in files if re.search(r"\.(jpe?g|png|webp)$", f[0], re.I)], key=lambda f: natkey(f[0]))[:MAX]
        photos = [f"https://lh3.googleusercontent.com/d/{i}=w1600" for _, i in imgs]
        if photos and photos != p.get("photos"):
            p["photos"] = photos; changed += 1
        print(p["code"], len(photos), "фото")
        time.sleep(0.5)
    if changed:
        json.dump(d, open(PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("обновлено объектов:", changed)

if __name__ == "__main__":
    main()
