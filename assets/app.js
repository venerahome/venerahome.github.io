/* VENI — каталог объектов на 5 языках. Данные объектов: assets/listings.js, тексты: assets/i18n.js */
/* ===== КОНТАКТЫ — меняйте здесь ===== */
const CONTACTS = {
  phones: [
    // отдельный номер для каждого языка: {lang: 'RU', number: '+359...'}
    {lang: 'BG · RU · EN', number: '+359882593077'}
  ],
  whatsapp: '+359882593077',
  viber: '+359882593077',
  telegram: 'venera_kh_happy', // имя в Telegram без @
  email: 'hasanova@imotipremier.com'
};
/* ===== GOOGLE ANALYTICS — вставьте ID вида 'G-XXXXXXXXXX' ===== */
const GA_ID = 'G-73W576V144';
if (GA_ID) {
  const g = document.createElement('script'); g.async = true; g.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_ID; document.head.appendChild(g);
  window.dataLayer = window.dataLayer || []; window.gtag = function () { dataLayer.push(arguments); }; gtag('js', new Date()); gtag('config', GA_ID);
}
const track = (name, params) => { try { if (window.gtag) gtag('event', name, params || {}); } catch (e) {} };
const LANGS = ['bg', 'ru', 'en', 'de', 'es'];
const WHATSAPP = CONTACTS.whatsapp.replace(/\D/g, '');
const fmtPhone = n => n.replace(/^\+359(\d{3})(\d{3})(\d{3})$/, '+359 $1 $2 $3');
const D = window.LISTINGS_DATA || {listings: [], places: {}};
const $ = id => document.getElementById(id);
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
const store = {get(k, d) { try { return JSON.parse(localStorage.getItem(k)) ?? d; } catch (e) { return d; } }, set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }};

/* ===== Язык ===== */
let lang = (() => {
  const q = new URLSearchParams(location.search).get('lang');
  if (LANGS.includes(q)) { store.set('veni-lang', q); return q; }
  const s = store.get('veni-lang', null); if (LANGS.includes(s)) return s;
  const n = (navigator.language || '').slice(0, 2); return LANGS.includes(n) ? n : 'ru';
})();
let T = I18N[lang];
const pick = o => (o && (o[lang] || o.ru || o.en || Object.values(o)[0])) || '';
const money = n => new Intl.NumberFormat(T.locale).format(n) + ' €';

let items = [];
function buildItems() {
  items = D.listings.map(p => {
    const city = pick(D.places[p.place]) || p.place, district = pick(p.district);
    const bits = [district, p.bedrooms ? T.bedrooms(p.bedrooms) : '', p.sea === 0 ? T.seafrontShort : ''].filter(Boolean);
    return {id: p.code, title: pick(p.title), city, place: p.place, district, type: T.types[p.type] || p.type, typeKey: p.type, price: p.price, area: p.area,
      desc: bits.join(' · '), text: pick(p.desc), feat: pick(p.feat) || [], img: p.photos[0], photos: p.photos,
      url: p.source === 'katoiko' ? '' : p.url, bedrooms: p.bedrooms, bathrooms: p.bathrooms, floor: p.floor, plot: p.plot, sea: p.sea, furnished: p.furnished, featured: p.featured,
      hay: [p.code, ...Object.values(p.title || {}), ...Object.values(D.places[p.place] || {}), ...Object.values(p.district || {})].join(' ').toLowerCase()};
  });
}
const byId = id => items.find(p => p.id === id);

let fav = new Set(store.get('veni-fav', [])), type = '', onlyFav = false, opened = null;

function applyTexts() {
  document.documentElement.lang = lang;
  document.title = opened ? (byId(opened)?.title || '') + ' · VENI' : T.title;
  document.querySelectorAll('[data-i]').forEach(el => { const v = T[el.dataset.i]; if (typeof v === 'string') el.textContent = v; });
  document.querySelectorAll('[data-i-html]').forEach(el => { const v = T[el.dataset.iHtml]; if (typeof v === 'string') el.innerHTML = v; });
  document.querySelectorAll('[data-i-ph]').forEach(el => el.placeholder = T[el.dataset.iPh]);
  document.querySelectorAll('[data-i-aria]').forEach(el => el.setAttribute('aria-label', T[el.dataset.iAria]));
  document.querySelectorAll('[data-i-alt]').forEach(el => el.alt = T[el.dataset.iAlt]);
  $('lang').innerHTML = LANGS.map(l => `<button type="button" data-lang="${l}" aria-pressed="${l === lang}" title="${I18N[l].name}">${l.toUpperCase()}</button>`).join('');
  $('steps').innerHTML = T.steps.map(s => `<li><strong>${esc(s[0])}</strong><p class="muted">${esc(s[1])}</p></li>`).join('');
  $('aboutList').innerHTML = T.aboutList.map(s => `<li>${esc(s)}</li>`).join('');
  document.querySelectorAll('#budget option').forEach(o => { if (+o.value < 9999999) o.textContent = T.budgetUpTo(money(+o.value)); });
  const cityVal = $('city').value;
  $('city').innerHTML = `<option value="">${esc(T.cityAll)}</option>` + [...new Map(items.map(p => [p.place, p.city])).entries()].map(([k, c]) => `<option value="${esc(k)}">${esc(c)}</option>`).join('');
  $('city').value = cityVal;
  $('chips').innerHTML = `<button class="${type ? '' : 'active'}" data-type="">${esc(T.allObjects)}</button>` +
    [...new Set(items.map(p => p.typeKey))].map(k => `<button class="${type === k ? 'active' : ''}" data-type="${k}">${esc(T.typesPl[k] || k)}</button>`).join('');
  const sc = $('s-country').selectedIndex, st = $('s-type').selectedIndex;
  $('s-country').innerHTML = T.sCountries.map(c => `<option>${esc(c)}</option>`).join(''); $('s-country').selectedIndex = Math.max(0, sc);
  $('s-type').innerHTML = T.sTypes.map(c => `<option>${esc(c)}</option>`).join(''); $('s-type').selectedIndex = Math.max(0, st);
}
function setLang(l) {
  lang = l; T = I18N[l]; store.set('veni-lang', l); track('language', {language: l});
  const u = new URL(location.href); if (u.searchParams.has('lang')) { u.searchParams.set('lang', l); history.replaceState(history.state, '', u); }
  buildItems(); applyTexts(); render();
  if (opened) openItem(opened, null, false);
}

function render() {
  const q = $('search').value.toLowerCase().trim();
  let data = items.filter(p => (!type || p.typeKey === type) && (!onlyFav || fav.has(p.id)) && (!$('city').value || p.place === $('city').value) &&
    p.price <= +$('budget').value && (!q || (p.hay + ' ' + p.desc.toLowerCase()).includes(q)));
  if ($('sort').value !== 'default') data.sort((a, b) => ($('sort').value === 'asc' ? 1 : -1) * (a.price - b.price));
  else data.sort((a, b) => (b.featured - a.featured) || (b.id - a.id));
  $('count').textContent = (onlyFav ? T.favPrefix : '') + T.count(data.length);
  $('favBtn').textContent = fav.size ? T.navFavN(fav.size) : T.navFav;
  $('grid').innerHTML = data.map(p => `<article class="card"><div class="picture" role="button" tabindex="0" aria-label="${esc(T.open)}: ${esc(p.title)}" onclick="openItem(${p.id},this)" onkeydown="if(event.key==='Enter')openItem(${p.id},this)"><img loading="lazy" src="${esc(p.img)}" alt="${esc(p.title)}"><span class="tag">${esc(p.type.toUpperCase())}</span><button class="heart ${fav.has(p.id) ? 'on' : ''}" aria-label="${esc(fav.has(p.id) ? T.removeFav : T.addFav)}" aria-pressed="${fav.has(p.id)}" onclick="event.stopPropagation();toggleFav(${p.id})">${fav.has(p.id) ? '♥' : '♡'}</button></div><h3>${esc(p.title)}</h3><div class="row"><span>${esc(p.city)}${p.desc ? ' · ' + esc(p.desc) : ''}</span><span>${p.area ? p.area + ' ' + T.m + '²' : ''}</span></div><div class="price">${money(p.price)}</div><button class="more" onclick="openItem(${p.id},this.closest('.card').querySelector('.picture'))">${esc(T.more)}</button></article>`).join('')
    || `<p class="muted">${esc(onlyFav ? T.favEmpty : T.noneFound)}</p>`;
}
function toggleFav(id) { track(fav.has(id) ? 'favorite_remove' : 'favorite_add', {object_id: id}); fav.has(id) ? fav.delete(id) : fav.add(id); store.set('veni-fav', [...fav]); render(); }
function explore() { onlyFav = false; render(); document.querySelector('.hero').classList.add('zoom'); $('catalog').scrollIntoView({behavior: 'smooth'}); }
function showFav() { onlyFav = !onlyFav; render(); $('catalog').scrollIntoView({behavior: 'smooth'}); }

function contact(id) {
  const p = id ? byId(id) : null;
  const link = p ? location.origin + location.pathname + '#object-' + p.id : '';
  const msg = p ? `${T.waProp}\n${p.title} (№ ${p.id})\n${link}` : T.waGeneral;
  $('contactFor').hidden = !p;
  if (p) $('contactFor').textContent = T.objLine(p.id, p.title, money(p.price));
  const rows = [];
  CONTACTS.phones.filter(x => x.number).forEach(x => rows.push([`${T.cPhone} · ${x.lang}`, `tel:${x.number}`, fmtPhone(x.number)]));
  if (CONTACTS.whatsapp) rows.push(['WhatsApp', `https://wa.me/${WHATSAPP}?text=${encodeURIComponent(msg)}`, fmtPhone(CONTACTS.whatsapp)]);
  if (CONTACTS.viber) rows.push(['Viber', `viber://chat?number=${encodeURIComponent(CONTACTS.viber)}`, fmtPhone(CONTACTS.viber)]);
  if (CONTACTS.telegram) rows.push(['Telegram', `https://t.me/${CONTACTS.telegram}`, '@' + CONTACTS.telegram]);
  if (CONTACTS.email) rows.push(['Email', `mailto:${CONTACTS.email}?subject=${encodeURIComponent(p ? T.mailObj(p.id) : T.mailGen)}&body=${encodeURIComponent(msg)}`, CONTACTS.email]);
  $('contactList').innerHTML = rows.map(([k, h, v]) => `<li><span>${esc(k)}</span><a href="${esc(h)}"${h.startsWith('http') ? ' target="_blank" rel="noopener"' : ''}>${esc(v)}</a></li>`).join('');
  track('contact_open', {object_id: p ? p.id : 'general'});
  leadFor = p; $('leadOk').hidden = true; $('leadErr').hidden = true; $('leadForm').hidden = false;
  if (!$('contactDialog').open) $('contactDialog').showModal();
}

/* ===== Галерея на весь экран ===== */
let gIdx = 0, gx = null, gy = null;
function gShow() {
  const p = byId(opened); if (!p) return;
  const n = p.photos.length; gIdx = (gIdx + n) % n;
  $('gImg').src = p.photos[gIdx]; $('gImg').alt = `${p.title} — ${T.photoN(gIdx + 1)}`;
  $('gCount').textContent = `${gIdx + 1} / ${n}`;
  $('gPrev').hidden = $('gNext').hidden = n < 2;
  document.querySelectorAll('#gStrip button').forEach((b, k) => { b.classList.toggle('on', k === gIdx); if (k === gIdx) b.scrollIntoView({block: 'nearest', inline: 'center'}); });
}
function openGallery(i) {
  const p = byId(opened); if (!p || !p.photos.length) return;
  gIdx = i;
  $('gStrip').innerHTML = p.photos.length > 1 ? p.photos.map((ph, k) => `<button type="button" onclick="gIdx=${k};gShow()" aria-label="${esc(T.photoN(k + 1))}"><img src="${esc(ph)}" alt="" loading="lazy"></button>`).join('') : '';
  $('gallery').showModal(); gShow();
}
function closeGallery() { $('gallery').close(); }
function stepGallery(d) { gIdx += d; gShow(); }
$('gallery').addEventListener('keydown', e => { if (e.key === 'ArrowLeft') stepGallery(-1); if (e.key === 'ArrowRight') stepGallery(1); });
$('gStage').addEventListener('pointerdown', e => { gx = e.clientX; gy = e.clientY; });
$('gStage').addEventListener('pointerup', e => {
  if (gx == null) return; const dx = e.clientX - gx, dy = e.clientY - gy; gx = null;
  if (Math.abs(dx) > 40 && Math.abs(dx) > Math.abs(dy)) stepGallery(dx < 0 ? 1 : -1);
  else if (Math.abs(dy) > 90 && dy > 0) closeGallery();
});
$('gStage').addEventListener('click', e => { if (e.target.id === 'gStage') closeGallery(); });

/* ===== Страница объекта ===== */
function openItem(id, el, push = true) {
  const p = byId(id); if (!p) return;
  const reopen = opened === id && $('detail').classList.contains('open');
  opened = id;
  $('detailImg').src = p.img; $('detailImg').alt = p.title;
  $('galOpen').textContent = T.allPhotos(p.photos.length); $('galOpen').hidden = !p.photos.length;
  const S = T.sp;
  const specs = [
    p.area ? [p.area + ' ' + T.m + '²', S.area] : null, [p.type, S.type],
    p.bedrooms ? [p.bedrooms, S.beds] : null, p.bathrooms ? [p.bathrooms, S.baths] : null,
    p.floor ? [p.floor, S.floor] : null, p.plot ? [p.plot + ' ' + T.m + '²', S.plot] : null,
    p.sea === 0 ? [S.seafront, S.sea] : p.sea ? [(p.sea >= 1000 ? p.sea / 1000 + ' ' + T.km : p.sea + ' ' + T.m), S.toSea] : null,
    p.furnished != null ? [p.furnished ? S.yes : S.no, S.furn] : null
  ].filter(Boolean);
  $('detailBody').innerHTML = `<div class="detail-head"><div><span class="small" style="color:var(--gold)">SELECTED BY VENI · № ${p.id}</span><h2>${esc(p.title)}</h2><p class="muted">${esc([p.city, p.district].filter(Boolean).join(', '))}</p></div>
    <aside class="price-box"><span class="small">${esc(T.price)}</span><strong>${money(p.price)}</strong>${p.area ? `<span class="ppm">${money(Math.round(p.price / p.area))} ${esc(T.perM2)}</span>` : ''}<button class="primary" type="button" onclick="contact(${p.id})">${esc(T.wantView)}</button></aside></div>
    <div class="specs">${specs.map(s => `<div><strong>${esc(s[0])}</strong><span>${esc(s[1])}</span></div>`).join('')}</div>
    <h3 style="font:25px Georgia">${esc(T.aboutObj)}</h3><p class="muted">${esc(p.text)}</p>
    ${p.feat.length ? `<ul class="feat">${p.feat.map(f => `<li>${esc(f)}</li>`).join('')}</ul>` : ''}
    ${p.photos.length > 1 ? `<h3 style="font:25px Georgia;margin-top:34px">${esc(T.photosN(p.photos.length))}</h3><div class="thumbs">${p.photos.map((ph, i) => `<button class="${i ? '' : 'on'}" onclick="openGallery(${i})" aria-label="${esc(T.photoN(i + 1))}"><img loading="lazy" src="${esc(ph)}" alt=""></button>`).join('')}</div>` : ''}
    ${p.url ? `<p style="margin-top:28px"><a class="src" href="${esc(p.url)}" target="_blank" rel="noopener">${esc(T.source)}</a></p>` : ''}`;
  $('detailPrice').textContent = money(p.price);
  document.title = p.title + ' · VENI';
  if (reopen) return;
  track('view_property', {object_id: p.id, object_title: p.title, price: p.price});
  $('detail').classList.add('open'); $('detail').scrollTop = 0; document.body.style.overflow = 'hidden';
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
  else { $('detail').classList.remove('open'); document.body.style.overflow = ''; opened = null; document.title = T.title; }
});

/* ===== Заявка на продажу ===== */
function sellForm() { track('sell_form_open'); $('sellErr').hidden = true; $('sellOk').hidden = true; $('sellDialog').showModal(); }
const LEADS_EMAIL = 'khassanovapremier@gmail.com'; // куда приходят заявки
function sellLines() {
  const v = id => $(id).value.trim();
  if (!v('s-name') || !v('s-phone')) { $('sellErr').textContent = T.sErr; $('sellErr').hidden = false; (v('s-name') ? $('s-phone') : $('s-name')).focus(); return null; }
  $('sellErr').hidden = true;
  return [[T.sName, v('s-name')], [T.sPhone, v('s-phone')], [T.sCountry, v('s-country')], [T.sType, v('s-type')],
    [T.sCity, v('s-city')], [T.sArea, v('s-area')], [T.sPrice, v('s-price')], [T.sellCommentL, v('s-msg')]].filter(r => r[1]);
}
$('sellFormEl').addEventListener('submit', async e => {
  e.preventDefault();
  const rows = sellLines(); if (!rows) return;
  const btn = $('sellSend'); btn.disabled = true; btn.textContent = T.sSending; $('sellOk').hidden = true;
  const body = {_subject: `Заявка на продажу с сайта VENI — ${$('s-name').value.trim()}`, _template: 'table', _captcha: 'false', 'Язык сайта': lang.toUpperCase()};
  rows.forEach(([k, v]) => body[k] = v);
  try {
    const r = await fetch('https://formsubmit.co/ajax/' + LEADS_EMAIL, {method: 'POST', headers: {'Content-Type': 'application/json', Accept: 'application/json'}, body: JSON.stringify(body)});
    const j = await r.json().catch(() => ({}));
    if (!r.ok || String(j.success) !== 'true') throw new Error(j.message || r.status);
    track('sell_request_sent', {method: 'email'});
    $('sellOk').textContent = T.sOk; $('sellOk').hidden = false; $('sellFormEl').reset(); applyTexts();
  } catch (err) {
    console.warn('FormSubmit:', err && err.message);
    $('sellErr').textContent = /activat/i.test(String(err && err.message)) ? 'Форма ещё не активирована: откройте письмо от FormSubmit на почте khassanovapremier@gmail.com и нажмите «Activate Form».' : T.sFail;
    $('sellErr').hidden = false;
  } finally { btn.disabled = false; btn.textContent = T.sSend; }
});
$('sellWa').addEventListener('click', () => {
  const rows = sellLines(); if (!rows) return;
  track('sell_request_sent', {method: 'whatsapp'});
  window.open(`https://wa.me/${WHATSAPP}?text=` + encodeURIComponent([T.sellHello, ...rows.map(([k, v]) => `${k}: ${v}`)].join('\n')), '_blank', 'noopener');
});

/* ===== События ===== */
['search', 'city', 'budget', 'sort'].forEach(id => $(id).addEventListener('input', render));
$('chips').addEventListener('click', e => { const b = e.target.closest('button'); if (!b) return; type = b.dataset.type; document.querySelectorAll('#chips button').forEach(x => x.classList.toggle('active', x === b)); render(); });
$('lang').addEventListener('click', e => { const b = e.target.closest('[data-lang]'); if (b) setLang(b.dataset.lang); });
$('contactList').addEventListener('click', e => { const a = e.target.closest('a'); if (a) track('contact_click', {method: a.closest('li').firstChild.textContent, object_id: opened || 'general'}); });
document.addEventListener('error', e => { if (e.target.tagName === 'IMG') e.target.style.visibility = 'hidden'; }, true);

buildItems(); applyTexts(); render();
if (location.hash.startsWith('#object-') && byId(+location.hash.slice(8))) {
  const initialId = +location.hash.slice(8);
  history.replaceState(null, '', location.pathname + location.search);
  openItem(initialId, null);
}

/* ===== Заявка из окна контактов (просмотр / вопрос) → на почту ===== */
let leadFor = null;
$('leadForm').addEventListener('submit', async e => {
  e.preventDefault();
  const name = $('l-name').value.trim(), ph = $('l-phone').value.trim(), msg = $('l-msg').value.trim();
  if (!name || !ph) { $('leadErr').textContent = T.lErr; $('leadErr').hidden = false; (name ? $('l-phone') : $('l-name')).focus(); return; }
  $('leadErr').hidden = true;
  const btn = $('leadSend'); btn.disabled = true; btn.textContent = T.sSending;
  const p = leadFor;
  const body = {_subject: `${p ? 'Заявка на просмотр № ' + p.id : 'Заявка с сайта VENI'} — ${name}`, _template: 'table', _captcha: 'false',
    'Имя': name, 'Телефон / email': ph, 'Сообщение': msg || '—', 'Язык сайта': lang.toUpperCase()};
  if (p) { body['Объект'] = `№ ${p.id} · ${p.title} · ${money(p.price)}`; body['Ссылка'] = location.origin + location.pathname + '#object-' + p.id; }
  try {
    const r = await fetch('https://formsubmit.co/ajax/' + LEADS_EMAIL, {method: 'POST', headers: {'Content-Type': 'application/json', Accept: 'application/json'}, body: JSON.stringify(body)});
    const j = await r.json().catch(() => ({}));
    if (!r.ok || String(j.success) !== 'true') throw new Error(j.message || r.status);
    track('lead_sent', {object_id: p ? p.id : 'general'});
    $('leadForm').reset(); $('leadOk').textContent = T.lOk; $('leadOk').hidden = false;
  } catch (err) { console.warn('FormSubmit:', err && err.message); $('leadErr').textContent = /activat/i.test(String(err && err.message)) ? 'Форма ещё не активирована: откройте письмо от FormSubmit на почте khassanovapremier@gmail.com и нажмите «Activate Form».' : T.sFail; $('leadErr').hidden = false; }
  finally { btn.disabled = false; btn.textContent = T.lSend; }
});
