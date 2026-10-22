# VENI Real Estate · Венера Хасанова

Сайт: https://venerahome.github.io

Дизайн — прототип из ChatGPT, наполнен настоящими объектами Венеры в Греции.

- `index.html` — страница и тексты
- `assets/styles.css` — оформление
- `assets/app.js` — каталог, фильтры, избранное, страница объекта, WhatsApp
- `data/listings.json` — объекты (источник); `python3 update_listings.py` пересобирает `assets/listings.js`
- `assets/hero.jpg` — фото главного экрана (Unsplash, см. PHOTO-SOURCES.txt); `assets/venera.jpg` — портрет
- Фото объектов берутся напрямую с imotipremier.com
- Собственные объекты Венеры: `"source": "veni"`, фото и видео в `assets/media/` (пути от корня: `/assets/media/...`), поле `video`. Ежедневная задача трогает только объекты без поля `source`.
- Языковые страницы `/bg/ /ru/ /en/ /de/ /es/` собирает `build_pages.py` (вызывается из `update_listings.py`).
