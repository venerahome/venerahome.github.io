#!/usr/bin/env python3
"""Ежедневная сверка каталога с прайсом партнёра (Google-таблица, код ROMAN).
- новые строки → новые объекты (тексты на 5 языках, фото из папки Drive) + в очередь Telegram;
- изменилась цена → обновляем цену;
- «БЕЗ РЕКЛАМЫ» / «ПАУЗА» или строка исчезла → снимаем объект с сайта и из очереди.
Объект связан со строкой по папке Google Drive (поле drive). Комиссию никогда не переносим.
Итог пишет в data/partner_sync_log.json."""
import io, json, os, re, sys, datetime, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from partner_texts import *          # D, L, KIND, FLAG, IN, FLOOR, floor_txt, fee_txt, sea_txt, ACT16, CLOSE, CACAO, PLACES_NEW
import openpyxl

SHEET = "1WJp0Tmx1gz96ZwbqQl7Lht1EZUEE7MJY_g0Z1Y3xPrE"
LISTINGS, QUEUE, LOG = "data/listings.json", "data/announce_queue.json", "data/partner_sync_log.json"
CODE = {"bg": "Код: ROMAN", "ru": "Код: ROMAN", "en": "Code: ROMAN", "de": "Code: ROMAN", "es": "Código: ROMAN"}
# папки, которые у Венеры уже есть своими объявлениями — не дублируем
SKIP_FOLDERS = {"1Q_VRzpsMkoNBlYeizBo4lGqT34_GyAnP",  # Африкана (отель) = 379313
                "1HtwYWMxXUNGYdFLzzcZX5YlqJB7YDpdK",  # Афродита Палас 2 эт. 59 000 = 395047
                "1gruF7_hmPqnJ4v_AXVS6I_YzpS1SSW9d",  # Гренада = 800021
                "1jZzoBtSwKXG99k_ScZG6oiH_2O3hWPg1",  # Братя Миладинови 118 = 374960
                "1Qsn-tyABiBNZywyKGKvWBrNuvV9N_vPi"}  # Форт Нокс Ривиера A4-94 = 394995
PLACE = [("КАКАО", "sunny_beach", True), ("СЛ. БЕР", "sunny_beach", False), ("СЛЪНЧ", "sunny_beach", False), ("СОЛНЕЧ", "sunny_beach", False),
         ("ВЛАС", "sveti_vlas", False), ("РАВДА", "ravda", False), ("АХЕЛОЙ", "aheloy", False), ("КОШАРИЦ", "kosharitsa", False),
         ("БУРГАС", "burgas", False), ("НЕСЕБ", "nesebar", False), ("ПОМОРИ", "pomorie", False), ("БЯЛА", "byala", False)]
SECTION = [("СТУДИ", "st"), ("ДВУШ", "b1"), ("ТРЕШ", "b2"), ("ЧЕТЫРЕ", "big"), ("ДОМ", "house"), ("ОТЕЛ", "hotel")]
KEYS = [("СНИЖЕН", "reduced"), ("ВСЕ НОВОЕ", "allnew"), ("НА ДВУШКУ", "to1b"), ("МОЖНО РАЗДЕЛИТЬ", "split"), ("ТОРГ", "nego"),
        ("СУПЕР ВИД МОРЕ", "superseaview"), ("ВИД МОРЕ, ГОРЫ", "seamountain"), ("ВИД МОРЕ", "seaview"), ("ПРОСТОРН", "spacious"),
        ("СРОЧНО", "urgent"), ("НОВ ДОМ", "newbuild"), ("НОВОЕ ЗДАНИЕ", "newbuild"), ("НОВЫЙ АПТ", "newbuild"), ("ТЕПЛЫЕ ПОЛЫ", "floorheat"),
        ("ВИД БАССЕЙН", "poolview"), ("ВИД НА БАССЕЙН", "poolview"), ("НА БАССЕЙН", "poolview"), ("НОВЫЙ РЕМОНТ", "renovated"),
        ("СУПЕР РЕМОНТ", "renovated"), ("1 ЛИНИЯ", "firstline"), ("3ТУАЛ", "bath3"), ("3 ТУАЛ", "bath3"), ("2 ТУАЛ", "bath2"),
        ("КЛАДОВК", "storage"), ("НОВ МЕБЕЛЬ", "newfurn"), ("2 ГАРАЖА", "garages2")]
TR = dict(zip("АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ", ["A","B","V","G","D","E","E","Zh","Z","I","Y","K","L","M","N","O","P","R","S","T","U","F","H","Ts","Ch","Sh","Sht","A","Y","","E","Yu","Ya"]))

def translit(s): return "".join(TR.get(c.upper(), c) if c.upper() in TR else c for c in s).title()
def money(v):
    m = re.sub(r"[^\d]", "", str(v or "")); return int(m) if m else None
def fnum(s):
    m = re.search(r"(\d+(?:[.,]\d+)?)", s or ""); return float(m.group(1).replace(",", ".")) if m else None

def fetch_rows():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET}/export?format=xlsx"
    data = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read()
    if not data.startswith(b"PK"): raise SystemExit("Таблица недоступна без входа — нужен доступ «всем, у кого есть ссылка»")
    ws = openpyxl.load_workbook(io.BytesIO(data)).worksheets[0]
    rows, section = [], None
    for r in ws.iter_rows():
        v = [str(c.value).strip() if c.value is not None else "" for c in r[:9]] + [""] * 9
        if v[0] and not v[1]:
            for k, s in SECTION:
                if k in v[0].upper(): section = s
            continue
        if not money(v[1]) or not section: continue
        link = r[8].hyperlink.target if len(r) > 8 and r[8].hyperlink else ""
        m = re.search(r"folders/([\w-]+)", link or "")
        rows.append(dict(row=r[0].row, name=v[0], price=money(v[1]), place=v[3], area=v[4], feesea=v[5], act=v[6], note=v[7],
                         label=v[8], folder=m.group(1) if m else None, section=section))
    return rows

def parse(r):
    name, rest = (r["name"].split("/", 1) + [""])[:2]
    name = re.sub(r"\s+", " ", name).strip(); rest = rest.upper()
    fl = "0" if "ПАРТЕР" in rest else "top" if "ПОСЛ" in rest else (re.search(r"(\d+)", rest).group(1) if re.search(r"\d+", rest) else None)
    up = r["place"].upper(); place, cacao = None, False
    for k, p, c in PLACE:
        if k in up: place, cacao = p, c; break
    fs = r["feesea"]
    if "/" in fs:
        a, b = fs.split("/", 1); fee = 0.0 if "БЕЗ" in a.upper() else fnum(a); sea = fnum(b)
        sea = int(sea * 1000) if sea is not None and "КМ" in b.upper() else (int(sea) if sea is not None else None)
    else:
        fee = None; s = fnum(fs); sea = int(s * 1000) if s and "КМ" in fs.upper() else (int(s) if s else None)
    note = r["note"].upper()
    flags = []
    for k, f in KEYS:
        if k in note and f not in flags and not (f == "seaview" and ("superseaview" in flags or "seamountain" in flags)): flags.append(f)
    if r["section"] in ("st", "b1", "b2") and "МЕБЕЛЬ" in note and "БЕЗ МЕБЕЛ" not in note and "newfurn" not in flags: flags.append("furnished")
    return dict(cyr=name.title(), lat=translit(name), fl=fl, area=int(fnum(r["area"]) or 0) or None, fee=fee, sea=sea, place=place, cacao=cacao, flags=flags)

def make(code, r, x, P):
    kind = r["section"]
    district = CACAO if x["cacao"] else D(x["cyr"], x["cyr"], x["lat"], x["lat"], x["lat"])
    pl = lambda l: P[x["place"]][l]
    cx = lambda l: x["cyr"] if l in ("bg", "ru") else x["lat"]
    title, desc, feat = {}, {}, {}
    for l in L:
        if kind == "house":
            k = D("Къща", "Дом", "House", "Haus", "Casa")[l]
            title[l] = f"{k} {x['area']} м², {pl(l)}" if l in ("bg", "ru") else f"{k}, {x['area']} m², {pl(l)}"
            s1 = D(f"Къща от {x['area']} м² в {pl('bg')}.", f"Дом площадью {x['area']} м², {pl('ru')}.", f"A {x['area']} m² house in {pl('en')}.",
                   f"Ein Haus mit {x['area']} m² in {pl('de')}.", f"Casa de {x['area']} m² en {pl('es')}.")[l]
        else:
            k = KIND.get(kind, KIND["b1"])[l]
            title[l] = f"{k} {x['area']} м², {cx(l)}, {pl(l)}" if l in ("bg", "ru") else f"{k}, {x['area']} m², {cx(l)}, {pl(l)}"
            where = D(f"Какао Бийч, {pl('bg')}", f"Какао Бич, {pl('ru')}", f"Cacao Beach, {pl('en')}", f"Cacao Beach, {pl('de')}", f"Cacao Beach, {pl('es')}")[l] if x["cacao"] else pl(l)
            ft = floor_txt(x["fl"], l) if x["fl"] else ""
            s1 = {"bg": f"{k} от {x['area']} м² {ft} {IN[l]} {cx(l)}, {where}.", "ru": f"{k} площадью {x['area']} м² {ft} {IN[l]} «{cx(l)}», {where}.",
                  "en": f"A {x['area']} m² {k.lower()} {ft} {IN[l]} {cx(l)}, {where}.", "de": f"{k} mit {x['area']} m² {ft} {IN[l]} {cx(l)}, {where}.",
                  "es": f"{k} de {x['area']} m² {ft} {IN[l]} {cx(l)}, {where}."}[l].replace("  ", " ")
        extra = " ".join(FLAG[f][1][l] for f in x["flags"] if FLAG[f][1])
        facts = ". ".join(t for t in [sea_txt(x["sea"], l), fee_txt(x["fee"], x["area"], l)] if t)
        act = ACT16[l] if "16" in r["act"] else ""
        desc[l] = " ".join(t for t in [s1, extra, (facts + ".") if facts else "", act, CLOSE.get(kind, CLOSE["b1"])[l], CODE[l]] if t)
        a16 = ("Акт 16" if l in ("bg", "ru") else {"en": "Act 16", "de": "Akt 16", "es": "Acta 16"}[l]) if act else None
        feat[l] = ([FLAG[f][0][l] for f in x["flags"]][:3] + [t for t in [sea_txt(x["sea"], l), a16] if t])[:4]
    return {"code": code, "slug": f"{x['place'].replace('_', '-')}-{'house' if kind == 'house' else 'apt'}-{code}", "country": "bg", "source": "partner",
            "type": "house" if kind == "house" else "apt", "deal": "sale", "status": "sale", "featured": False, "place": x["place"],
            "district": None if kind == "house" else district, "price": r["price"], "area": x["area"], "plot": None,
            "bedrooms": {"st": 0, "b1": 1, "b2": 2, "big": 4}.get(kind), "bathrooms": 3 if "bath3" in x["flags"] else 2 if "bath2" in x["flags"] else None,
            "floor": x["fl"] if x["fl"] not in (None, "top") else None, "sea": x["sea"], "furnished": True if {"furnished", "newfurn"} & set(x["flags"]) else None,
            "lift": None, "url": None, "drive": r["folder"], "photos": [], "title": title, "desc": desc, "feat": feat}

def main():
    rows = fetch_rows()
    d = json.load(open(LISTINGS, encoding="utf-8")); P = d["places"]
    for k, v in PLACES_NEW.items(): P.setdefault(k, v)
    q = json.load(open(QUEUE, encoding="utf-8")) if os.path.exists(QUEUE) else {"queue": [], "last_slot": ""}
    mine = {l["drive"]: l for l in d["listings"] if l.get("source") == "partner" and l.get("drive")}
    log = {"date": datetime.date.today().isoformat(), "added": [], "removed": [], "price": [], "skipped": []}
    seen = set()
    nxt = max([l["code"] for l in d["listings"] if l.get("source") == "partner"] + [810999]) + 1
    nxt = max(nxt, 811000)
    for r in rows:
        f = r["folder"]
        if not f or f in SKIP_FOLDERS or r["section"] == "hotel": continue
        blocked = re.search(r"БЕЗ РЕКЛАМ|ПАУЗ", r["note"].upper())
        if f in mine:
            l = mine[f]
            if blocked: continue                       # снимем ниже (не попадёт в seen)
            seen.add(f)
            if l["price"] != r["price"]:
                log["price"].append([l["code"], l["title"]["ru"], l["price"], r["price"]]); l["price"] = r["price"]
            continue
        if blocked: continue
        x = parse(r)
        if not x["place"] or not x["area"]:
            log["skipped"].append([r["row"], r["name"], "неизвестный район или площадь"]); continue
        o = make(nxt, r, x, P); nxt += 1
        d["listings"].append(o); seen.add(f); q["queue"].append(o["code"])
        log["added"].append([o["code"], o["title"]["ru"], o["price"]])
    gone = [l for dr, l in mine.items() if dr not in seen]
    for l in gone: log["removed"].append([l["code"], l["title"]["ru"]])
    gone_codes = {l["code"] for l in gone}
    d["listings"] = [l for l in d["listings"] if l["code"] not in gone_codes]
    q["queue"] = [c for c in q["queue"] if c not in gone_codes]
    if len(gone) > 25:                                # защита: таблица пустая/сломалась — ничего не трогаем
        raise SystemExit(f"Подозрительно много снятых объектов ({len(gone)}) — изменения не сохраняю")
    if os.environ.get("DRY") == "1":
        print("ПРОБНЫЙ ЗАПУСК, ничего не сохраняю"); print(json.dumps(log, ensure_ascii=False, indent=1)); return
    if log["added"] or log["removed"] or log["price"]:
        d["updated"] = log["date"]
        json.dump(d, open(LISTINGS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        json.dump(q, open(QUEUE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    hist = json.load(open(LOG, encoding="utf-8")) if os.path.exists(LOG) else []
    hist = ([log] + hist)[:60]
    json.dump(hist, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(log, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main()
