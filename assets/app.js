/* VENI — каталог объектов. Данные объектов: assets/listings.js (обновляется автоматически). */
/* ===== КОНТАКТЫ — меняйте здесь ===== */
const CONTACTS = {
  phones: [
    // отдельный номер для каждого языка: {lang: 'Русский', number: '+359...'}
    {lang: 'Основной', number: '+359879590026'}
  ],
  whatsapp: '+359882593077',
  viber: '+359882593077',
  telegram: 'venera_kh_happy', // имя в Telegram без @
  email: 'hasanova@imotipremier.com'
};
const WHATSAPP = CONTACTS.whatsapp.replace(/\D/g, '');
const fmtPhone = n => n.replace(/^\+359(\d{3})(\d{3})(\d{3})$/, '+359 $1 $2 $3');
const TYPES = {apt: 'Квартира', house: 'Дом', villa: 'Вилла', plot: 'Участок', commercial: 'Коммерческая'};
const TYPES_PL = {apt: 'Квартиры', house: 'Дома', villa: 'Виллы', plot: 'Участки', commercial: 'Коммерческие'};
const D = window.LISTINGS_DATA || {listings: [], places: {}};

const items = D.listings.map(p => {
  const city = (D.places[p.place] || {}).ru || p.place;
  const district = p.district ? p.district.ru : '';
  const bits = [district, p.bedrooms ? `${p.bedrooms} ${p.bedrooms === 1 ? 'спальня' : 'спальни'}` : '', p.sea === 0 ? 'на берегу' : ''].filter(Boolean);
  return {id: p.code, title: p.title.ru, city, district, type: TYPES[p.type] || p.type, typeKey: p.type, price: p.price, area: p.area,
    desc: bits.join(' · '), text: p.desc.ru, feat: (p.feat && p.feat.ru) || [], img: p.photos[0], photos: p.photos,
    url: p.url, bedrooms: p.bedrooms, bathrooms: p.bathrooms, floor: p.floor, plot: p.plot, sea: p.sea, furnished: p.furnished, featured: p.featured};
});
const byId = id => items.find(p => p.id === id);
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));

let fav = new Set(JSON.parse(localStorage.getItem('veni-fav') || '[]')), type = '', onlyFav = false, opened = null;
const $ = id => document.getElementById(id), money = n => new Intl.NumberFormat('ru-RU').format(n) + ' €';
const plural = (n, a, b, c) => { const m = n % 10, h = n % 100; return m === 1 && h !== 11 ? a : m >= 2 && m <= 4 && (h < 10 || h >= 20) ? b : c; };

/* фильтры, которые зависят от данных */
[...new Set(items.map(p => p.city))].forEach(c => $('city').insertAdjacentHTML('beforeend', `<option>${esc(c)}</option>`));
$('chips').innerHTML = `<button class="active" data-type="">Все объекты</button>` +
  [...new Set(items.map(p => p.typeKey))].map(k => `<button data-type="${TYPES[k]}">${TYPES_PL[k] || TYPES[k]}</button>`).join('');
if (D.updated) $('updated').textContent = 'Объекты обновлены: ' + new Date(D.updated).toLocaleDateString('ru-RU') + ' · все объявления опубликованы в Imoti Premier.';

function render() {
  const q = $('search').value.toLowerCase().trim();
  let data = items.filter(p => (!type || p.type === type) && (!onlyFav || fav.has(p.id)) && (!$('city').value || p.city === $('city').value) &&
    p.price <= +$('budget').value && (p.title + ' ' + p.city + ' ' + p.desc + ' ' + p.id).toLowerCase().includes(q));
  if ($('sort').value !== 'default') data.sort((a, b) => ($('sort').value === 'asc' ? 1 : -1) * (a.price - b.price));
  else data.sort((a, b) => (b.featured - a.featured) || (b.id - a.id));
  $('count').textContent = (onlyFav ? 'Избранное · ' : '') + data.length + ' ' + plural(data.length, 'объект', 'объекта', 'объектов');
  $('favBtn').textContent = fav.size ? `♥ Избранное · ${fav.size}` : '♡ Избранное';
  $('grid').innerHTML = data.map(p => `<article class="card"><div class="picture" role="button" tabindex="0" aria-label="Открыть: ${esc(p.title)}" onclick="openItem(${p.id},this)" onkeydown="if(event.key==='Enter')openItem(${p.id},this)"><img loading="lazy" src="${esc(p.img)}" alt="${esc(p.title)}"><span class="tag">${esc(p.type.toUpperCase())}</span><button class="heart ${fav.has(p.id) ? 'on' : ''}" aria-label="${fav.has(p.id) ? 'Убрать из избранного' : 'Добавить в избранное'}" aria-pressed="${fav.has(p.id)}" onclick="event.stopPropagation();toggleFav(${p.id})">${fav.has(p.id) ? '♥' : '♡'}</button></div><h3>${esc(p.title)}</h3><div class="row"><span>${esc(p.city)}${p.desc ? ' · ' + esc(p.desc) : ''}</span><span>${p.area} м²</span></div><div class="price">${money(p.price)}</div><button class="more" onclick="openItem(${p.id},this.closest('.card').querySelector('.picture'))">Подробнее ↗</button></article>`).join('')
    || `<p class="muted">${onlyFav ? 'В избранном пока пусто. Нажмите ♡ на понравившемся объекте.' : 'Объекты не найдены. Измените фильтры.'}</p>`;
}
function toggleFav(id) { fav.has(id) ? fav.delete(id) : fav.add(id); localStorage.setItem('veni-fav', JSON.stringify([...fav])); render(); }
function explore() { onlyFav = false; render(); document.querySelector('.hero').classList.add('zoom'); $('catalog').scrollIntoView({behavior: 'smooth'}); }
function showFav() { onlyFav = !onlyFav; render(); $('catalog').scrollIntoView({behavior: 'smooth'}); }
function contact(id) {
  const p = id ? byId(id) : null;
  const link = p ? location.origin + location.pathname + '#object-' + p.id : '';
  const msg = p ? `Здравствуйте! Меня интересует этот объект. Хочу узнать подробности и записаться на просмотр.\n${p.title} (№ ${p.id})\n${link}` : 'Здравствуйте, Венера! Хочу обсудить поиск недвижимости в Греции.';
  $('contactFor').hidden = !p;
  if (p) $('contactFor').textContent = `Объект № ${p.id} · ${p.title} · ${money(p.price)}`;
  const rows = [];
  CONTACTS.phones.filter(x => x.number).forEach(x => rows.push([`Телефон · ${x.lang}`, `tel:${x.number}`, fmtPhone(x.number)]));
  if (CONTACTS.whatsapp) rows.push(['WhatsApp', `https://wa.me/${WHATSAPP}?text=${encodeURIComponent(msg)}`, fmtPhone(CONTACTS.whatsapp)]);
  if (CONTACTS.viber) rows.push(['Viber', `viber://chat?number=${encodeURIComponent(CONTACTS.viber)}`, fmtPhone(CONTACTS.viber)]);
  if (CONTACTS.telegram) rows.push(['Telegram', `https://t.me/${CONTACTS.telegram}`, '@' + CONTACTS.telegram]);
  if (CONTACTS.email) rows.push(['Email', `mailto:${CONTACTS.email}?subject=${encodeURIComponent(p ? 'Объект № ' + p.id : 'Недвижимость в Греции')}&body=${encodeURIComponent(msg)}`, CONTACTS.email]);
  $('contactList').innerHTML = rows.map(([k, h, v]) => `<li><span>${esc(k)}</span><a href="${esc(h)}"${h.startsWith('http') ? ' target="_blank" rel="noopener"' : ''}>${esc(v)}</a></li>`).join('');
  $('contactDialog').showModal();
}
function setPhoto(i) { const p = byId(opened); if (!p) return; $('detailImg').src = p.photos[i]; document.querySelectorAll('.thumbs button').forEach((b, k) => b.classList.toggle('on', k === i)); $('detail').scrollTo({top: 0, behavior: 'smooth'}); }

function openItem(id, el, push = true) {
  const p = byId(id); if (!p) return;
  opened = id;
  $('detailImg').src = p.img; $('detailImg').alt = p.title;
  const specs = [
    [p.area + ' м²', 'Площадь'], [p.type, 'Тип объекта'],
    p.bedrooms ? [p.bedrooms, 'Спальни'] : null, p.bathrooms ? [p.bathrooms, 'Санузлы'] : null,
    p.floor ? [p.floor, 'Этаж'] : null, p.plot ? [p.plot + ' м²', 'Участок'] : null,
    p.sea === 0 ? ['На берегу', 'Море'] : p.sea ? [(p.sea >= 1000 ? p.sea / 1000 + ' км' : p.sea + ' м'), 'До моря'] : null,
    p.furnished != null ? [p.furnished ? 'Есть' : 'Нет', 'Мебель'] : null
  ].filter(Boolean);
  $('detailBody').innerHTML = `<div class="detail-head"><div><span class="small" style="color:var(--gold)">SELECTED BY VENI · № ${p.id}</span><h2>${esc(p.title)}</h2><p class="muted">${esc([p.city, p.district].filter(Boolean).join(', '))}</p></div>
    <aside class="price-box"><span class="small">Цена</span><strong>${money(p.price)}</strong>${p.area ? `<span class="ppm">${money(Math.round(p.price / p.area))} за м²</span>` : ''}<button class="primary" type="button" onclick="contact(${p.id})">Хочу посмотреть ↗</button></aside></div>
    <div class="specs">${specs.map(s => `<div><strong>${esc(s[0])}</strong><span>${esc(s[1])}</span></div>`).join('')}</div>
    <h3 style="font:25px Georgia">Об этом объекте</h3><p class="muted">${esc(p.text)}</p>
    ${p.feat.length ? `<ul class="feat">${p.feat.map(f => `<li>${esc(f)}</li>`).join('')}</ul>` : ''}
    ${p.photos.length > 1 ? `<h3 style="font:25px Georgia;margin-top:34px">Фотографии · ${p.photos.length}</h3><div class="thumbs">${p.photos.map((ph, i) => `<button class="${i ? '' : 'on'}" onclick="setPhoto(${i})" aria-label="Фото ${i + 1}"><img loading="lazy" src="${esc(ph)}" alt=""></button>`).join('')}</div>` : ''}
    ${p.url ? `<p style="margin-top:28px"><a class="src" href="${esc(p.url)}" target="_blank" rel="noopener">Объявление в Imoti Premier ↗</a></p>` : ''}`;
  $('detailPrice').textContent = money(p.price);
  $('detail').classList.add('open'); $('detail').scrollTop = 0; document.body.style.overflow = 'hidden';
  document.title = p.title + ' · VENI';
  if (push) history.pushState({id}, '', '#object-' + id);
  if (el && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const r = el.getBoundingClientRect(), clone = document.createElement('img');
    clone.src = p.img; clone.className = 'fly';
    Object.assign(clone.style, {left: r.left + 'px', top: r.top + 'px', width: r.width + 'px', height: r.height + 'px', borderRadius: '5px'});
    document.body.append(clone);
    requestAnimationFrame(() => requestAnimationFrame(() => {
      const t = $('detailImg').getBoundingClientRect();
      Object.assign(clone.style, {left: t.left + 'px', top: t.top + 'px', width: t.width + 'px', height: t.height + 'px', borderRadius: '0'});
      setTimeout(() => clone.remove(), 700);
    }));
  }
}
window.addEventListener('popstate', () => {
  if (location.hash.startsWith('#object-')) openItem(+location.hash.slice(8), null, false);
  else { $('detail').classList.remove('open'); document.body.style.overflow = ''; opened = null; document.title = 'VENI — Пространство вашей жизни'; }
});
['search', 'city', 'budget', 'sort'].forEach(id => $(id).addEventListener('input', render));
document.querySelectorAll('.chips button').forEach(b => b.onclick = () => { type = b.dataset.type; document.querySelectorAll('.chips button').forEach(x => x.classList.toggle('active', x === b)); render(); });
document.addEventListener('error', e => { if (e.target.tagName === 'IMG') e.target.style.visibility = 'hidden'; }, true);
render();
if (location.hash.startsWith('#object-') && byId(+location.hash.slice(8))) {
  const initialId = +location.hash.slice(8);
  history.replaceState(null, '', location.pathname);
  openItem(initialId, null);
}
