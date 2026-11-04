"""Тексты для объектов партнёра (ROMAN) на 5 языках. Используется partner_sync.py."""
import json, re
L = ["bg", "ru", "en", "de", "es"]
def D(*a): return dict(zip(L, a))
PLACES_NEW = {"kosharitsa": D("Кошарица", "Кошарица", "Kosharitsa", "Kosharitsa", "Kosharitsa"),
              "byala": D("Бяла (Варна)", "Бяла (Варна)", "Byala (Varna)", "Byala (Warna)", "Byala (Varna)")}

KIND = {
 "st": D("Студио", "Студия", "Studio", "Studio", "Estudio"),
 "b1": D("Апартамент с 1 спалня", "Квартира с 1 спальней", "One-bedroom flat", "2-Zimmer-Wohnung", "Piso de 1 dormitorio"),
 "b2": D("Апартамент с 2 спални", "Квартира с 2 спальнями", "Two-bedroom flat", "3-Zimmer-Wohnung", "Piso de 2 dormitorios"),
 "big": D("Многостаен апартамент", "Многокомнатные апартаменты", "Multi-room apartment", "Mehrzimmerwohnung", "Apartamento de varias habitaciones"),
}
IN = D("в комплекс", "в комплексе", "in", "in der Anlage", "en el complejo")
FLOOR = {
 "0": D("на партерен етаж", "на первом этаже", "on the ground floor", "im Erdgeschoss", "en planta baja"),
 "top": D("на последния етаж", "на последнем этаже", "on the top floor", "im obersten Stock", "en la última planta"),
}
def floor_txt(f, l):
    if f in FLOOR: return FLOOR[f][l]
    return {"bg": "на " + {"1":"1-ви","2":"2-ри","3":"3-ти","4":"4-ти","5":"5-и","6":"6-и"}.get(f, f) + " етаж", "ru": f"на {f}-м этаже", "en": f"on floor {f}", "de": f"im {f}. Stock", "es": f"en la {f}.ª planta"}[l]
FLAG = {  # (особенность в фичах, фраза в описании)
 "reduced": (D("Намалена цена", "Цена снижена", "Price reduced", "Preis gesenkt", "Precio rebajado"), None),
 "allnew": (D("Всичко ново", "Всё новое", "Everything new", "Alles neu", "Todo nuevo"), D("Всичко в апартамента е ново.", "В квартире всё новое.", "Everything in the flat is new.", "In der Wohnung ist alles neu.", "Todo en el piso es nuevo.")),
 "split": (D("Може да се раздели", "Можно разделить", "Can be divided", "Teilbar", "Se puede dividir"), D("Площта позволява да се обособи отделна спалня.", "Площадь позволяет выделить отдельную спальню.", "The space allows a separate bedroom to be created.", "Die Fläche erlaubt ein separates Schlafzimmer.", "El espacio permite crear un dormitorio aparte.")),
 "to1b": (D("Може да стане двустаен", "Можно сделать двушку", "Can become a one-bedroom", "Umbau zur 2-Zimmer-Wohnung möglich", "Convertible en 1 dormitorio"), D("Голямата площ позволява да се превърне в апартамент с отделна спалня.", "Большая площадь позволяет сделать из студии квартиру с отдельной спальней.", "Its size allows it to be turned into a one-bedroom flat.", "Die Größe erlaubt den Umbau zur 2-Zimmer-Wohnung.", "Su tamaño permite convertirlo en un piso de un dormitorio.")),
 "nego": (D("Цена по договаряне", "Возможен торг", "Price negotiable", "Preis verhandelbar", "Precio negociable"), None),
 "seaview": (D("Гледка към морето", "Вид на море", "Sea view", "Meerblick", "Vistas al mar"), D("От апартамента се вижда морето.", "Из квартиры видно море.", "The flat has a view of the sea.", "Die Wohnung bietet Meerblick.", "El piso tiene vistas al mar.")),
 "superseaview": (D("Панорамна гледка към морето", "Панорамный вид на море", "Panoramic sea view", "Panorama-Meerblick", "Vistas panorámicas al mar"), D("Великолепна панорамна гледка към морето.", "Великолепный панорамный вид на море.", "A superb panoramic view of the sea.", "Ein herrlicher Panoramablick aufs Meer.", "Unas vistas panorámicas al mar magníficas.")),
 "spacious": (D("Просторен", "Просторная", "Spacious", "Geräumig", "Amplio"), None),
 "urgent": (D("Спешна продажба", "Срочная продажа", "Urgent sale", "Eilverkauf", "Venta urgente"), None),
 "newbuild": (D("Нова сграда", "Новый дом", "New building", "Neubau", "Edificio nuevo"), D("Сградата е нова.", "Дом новый.", "The building is new.", "Das Gebäude ist neu.", "El edificio es nuevo.")),
 "furnished": (D("Обзаведен", "С мебелью", "Furnished", "Möbliert", "Amueblado"), None),
 "floorheat": (D("Подово отопление", "Тёплые полы", "Underfloor heating", "Fußbodenheizung", "Suelo radiante"), D("Има подово отопление.", "Есть тёплые полы.", "It has underfloor heating.", "Mit Fußbodenheizung.", "Tiene suelo radiante.")),
 "poolview": (D("Гледка към басейна", "Вид на бассейн", "Pool view", "Poolblick", "Vistas a la piscina"), D("Прозорците гледат към басейна.", "Окна выходят на бассейн.", "The windows overlook the pool.", "Die Fenster gehen zum Pool.", "Las ventanas dan a la piscina.")),
 "renovated": (D("Нов ремонт", "Свежий ремонт", "Newly renovated", "Frisch renoviert", "Recién reformado"), D("Апартаментът е след нов ремонт.", "В квартире свежий ремонт.", "The flat has been newly renovated.", "Die Wohnung ist frisch renoviert.", "El piso está recién reformado.")),
 "firstline": (D("Първа линия", "Первая линия", "Beachfront", "Erste Meereslinie", "Primera línea"), None),
 "bath2": (D("2 бани", "2 санузла", "2 bathrooms", "2 Bäder", "2 baños"), None),
 "bath3": (D("3 бани", "3 санузла", "3 bathrooms", "3 Bäder", "3 baños"), None),
 "storage": (D("Със склад", "С кладовкой", "Storage room", "Mit Abstellraum", "Con trastero"), None),
 "seamountain": (D("Гледка към морето и планината", "Вид на море и горы", "Sea and mountain views", "Meer- und Bergblick", "Vistas al mar y la montaña"), D("От терасата се виждат морето и планината.", "С террасы видно море и горы.", "The terrace looks out over the sea and the mountains.", "Von der Terrasse sieht man Meer und Berge.", "Desde la terraza se ven el mar y la montaña.")),
 "pool": (D("Басейн", "Бассейн", "Pool", "Pool", "Piscina"), None),
 "newfurn": (D("Нови мебели и техника", "Новая мебель и техника", "New furniture and appliances", "Neue Möbel und Geräte", "Muebles y electrodomésticos nuevos"), D("Мебелите и техниката са нови.", "Мебель и техника новые.", "The furniture and appliances are new.", "Möbel und Geräte sind neu.", "Los muebles y electrodomésticos son nuevos.")),
 "appliances": (D("С техника", "С техникой", "With appliances", "Mit Geräten", "Con electrodomésticos"), None),
 "garages2": (D("2 гаража в цената", "2 гаража в цене", "2 garages included", "2 Garagen inklusive", "2 garajes incluidos"), D("Два гаража са включени в цената.", "Два гаража входят в цену.", "Two garages are included in the price.", "Zwei Garagen sind im Preis enthalten.", "Dos garajes incluidos en el precio.")),
 "plot2002": (D("Двор 2002 м²", "Участок 2002 м²", "2,002 m² plot", "2.002 m² Grundstück", "Parcela de 2.002 m²"), None),
}
def num(n, l):
    if isinstance(n, float) and n.is_integer(): n = int(n)
    if isinstance(n, int): return f"{n:,}".replace(",", {"en": ",", "de": ".", "es": "."}.get(l, " "))
    s = f"{n:.2f}".rstrip("0").rstrip(".")
    return s if l == "en" else s.replace(".", ",")
def fee_txt(f, area, l):
    if f is None: return None
    if f == 0: return D("Без такса поддръжка", "Без платы за обслуживание", "No maintenance fee", "Keine Hausgebühr", "Sin cuota de mantenimiento")[l]
    if f <= 25:
        v = num(f, l); return {"bg": f"Такса поддръжка {v} €/м² годишно", "ru": f"Обслуживание {v} €/м² в год", "en": f"Maintenance €{v}/m² a year", "de": f"Hausgebühr {v} €/m² pro Jahr", "es": f"Cuota {v} €/m² al año"}[l]
    v = num(int(f), l); return {"bg": f"Такса поддръжка {v} € годишно", "ru": f"Обслуживание {v} € в год", "en": f"Maintenance €{v} a year", "de": f"Hausgebühr {v} € pro Jahr", "es": f"Cuota {v} € al año"}[l]
def sea_txt(m, l):
    if m is None: return None
    if m >= 1000:
        k = num(m / 1000, l) if m % 1000 else str(m // 1000)
        return {"bg": f"{k} км до морето", "ru": f"{k} км до моря", "en": f"{k} km to the sea", "de": f"{k} km zum Meer", "es": f"A {k} km del mar"}[l]
    return {"bg": f"{m} м до морето", "ru": f"{m} м до моря", "en": f"{m} m to the sea", "de": f"{m} m zum Meer", "es": f"A {m} m del mar"}[l]
ACT16 = D("Акт 16 — сградата е въведена в експлоатация.", "Акт 16 — дом сдан в эксплуатацию.", "Act 16 — the building is officially completed.", "Akt 16 – das Gebäude ist abgenommen.", "Acta 16: el edificio está terminado y legalizado.")
CLOSE = {
 "st": D("Удобен вариант за почивка или за отдаване под наем през сезона.", "Удобный вариант для отдыха или сдачи в аренду в сезон.", "A handy choice for holidays or seasonal letting.", "Ideal für Urlaub oder Saisonvermietung.", "Una buena opción para vacaciones o alquiler de temporada."),
 "b1": D("Подходящ за живеене, почивка или отдаване под наем.", "Подойдёт для жизни, отдыха или сдачи в аренду.", "Suits living in, holidays or letting.", "Zum Wohnen, für Urlaub oder Vermietung.", "Para vivir, veranear o alquilar."),
 "b2": D("Достатъчно място за семейство — за живеене или почивка.", "Достаточно места для семьи — для жизни или отдыха.", "Room for a family — to live in or for holidays.", "Platz für eine Familie – zum Wohnen oder Urlauben.", "Espacio para una familia: para vivir o veranear."),
 "big": D("Рядко предложение за голямо семейство, близо до морето.", "Редкое предложение для большой семьи у самого моря.", "A rare offer for a large family right by the sea.", "Ein seltenes Angebot für eine große Familie direkt am Meer.", "Una oferta poco común para una familia grande junto al mar."),
}
CACAO = D("Какао Бийч", "Какао Бич", "Cacao Beach", "Cacao Beach", "Cacao Beach")

