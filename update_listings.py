#!/usr/bin/env python3
"""Пересобирает assets/listings.js из data/listings.json (сайт читает объекты из listings.js)."""
import json, os
R = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(R, "data", "listings.json"), encoding="utf-8"))
with open(os.path.join(R, "assets", "listings.js"), "w", encoding="utf-8") as f:
    f.write("/* Сгенерировано из data/listings.json — не редактировать вручную */\nwindow.LISTINGS_DATA = ")
    f.write(json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"))
    f.write(";\n")
print(len(data["listings"]), "listings")
