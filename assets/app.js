/* VENI Real Estate — каталог, фильтры, избранное, страница объекта с FLIP-анимацией фото. */
(() => {
"use strict";

/* ===== Настройки ===== */
const CONTACT = {
  phone: "+359879590026", phoneShow: "+359 879 590 026",
  whatsapp: "359882593077", whatsappShow: "+359 882 593 077",
  viber: "+359882593077", viberShow: "+359 882 593 077",
  email: "hasanova@imotipremier.com"
};
const GA_ID = ""; // Google Analytics 4: вставьте "G-XXXXXXXXXX"
const LANGS = ["bg", "ru", "en", "de", "es"];
const PAGE = 9;
const SEA_NEAR = {ru:"Близко к морю (до 1 км)", bg:"Близо до морето (до 1 км)", en:"Near the sea (up to 1 km)", de:"Meeresnähe (bis 1 km)", es:"Cerca del mar (hasta 1 km)"};

const DATA = window.SITE_DATA || {listings: [], places: {}};
const LIST = DATA.listings;
const PLACES = DATA.places;
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;
const isDesktop = () => matchMedia("(min-width:1024px)").matches;
const store = {
  get(k, d) { try { const v = localStorage.getItem(k); return v == null ? d : JSON.parse(v); } catch (e) { return d; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
};
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));

/* ===== Analytics ===== */
if (GA_ID) {
  const s = document.createElement("script"); s.async = true; s.src = "https://www.googletagmanager.com/gtag/js?id=" + GA_ID; document.head.appendChild(s);
  window.dataLayer = window.dataLayer || []; window.gtag = function(){ dataLayer.push(arguments); }; gtag("js", new Date()); gtag("config", GA_ID);
}
const track = (n, p) => { try { window.gtag && gtag("event", n, p); } catch (e) {} };

/* ===== Язык ===== */
const qs0 = new URLSearchParams(location.search);
let lang = (() => {
  const q = qs0.get("lang"); if (LANGS.includes(q)) { store.set("veni-lang", q); return q; }
  const s = store.get("veni-lang", null); if (LANGS.includes(s)) return s;
  const n = (navigator.language || "").slice(0, 2); return LANGS.includes(n) ? n : "ru";
})();
let t = I18N[lang];

/* ===== Избранное ===== */
let favs = new Set(store.get("veni-favs", []).filter(s => LIST.some(p => p.slug === s)));
const saveFavs = () => store.set("veni-favs", [...favs]);

/* ===== Фильтры ===== */
const DEF = {q:"", type:"", deal:"", city:"", district:"", pmin:"", pmax:"", amin:"", amax:"", beds:"", sea:"", sort:"featured"};
const KEYS = Object.keys(DEF);
let F = {...DEF};
KEYS.forEach(k => { const v = qs0.get(k); if (v != null) F[k] = v; });
let shown = PAGE;

/* ===== Помощники ===== */
const money = n => new Intl.NumberFormat(t.locale).format(n) + " €";
const num = n => new Intl.NumberFormat(t.locale).format(n);
const placeName = p => PLACES[p.place]?.[lang] || p.place;
const districtName = p => p.district?.[lang] || "";
const loc = p => [placeName(p), districtName(p)].filter(Boolean).join(", ");
const propPath = p => `/properties/${p.slug}/`;
const bySlug = s => LIST.find(p => p.slug === s);
const seaText = p => p.sea == null ? "" : p.sea === 0 ? t.seafront : p.sea >= 1000 ? `${num(p.sea / 1000)} ${t.km}` : `${p.sea} ${t.m}`;
const norm = s => String(s).toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
const HAY = new Map(LIST.map(p => [p.slug, norm([p.code, ...Object.values(p.title), ...Object.values(PLACES[p.place] || {}), ...Object.values(p.district || {})].join(" "))]));
const heartSvg = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 20.5s-7.5-4.6-9.3-9.1C1.5 8.3 3.4 4.8 6.9 4.6c2-.1 3.6 1 5.1 2.9 1.5-1.9 3.1-3 5.1-2.9 3.5.2 5.4 3.7 4.2 6.8-1.8 4.5-9.3 9.1-9.3 9.1z"/></svg>';
const waLink = text => `https://wa.me/${CONTACT.whatsapp}?text=${encodeURIComponent(text)}`;

function applyFilters() {
  const q = norm(F.q.trim());
  const r = LIST.filter(p =>
    (!F.type || p.type === F.type) &&
    (!F.deal || p.deal === F.deal) &&
    (!F.city || p.place === F.city) &&
    (!F.district || (p.district && p.district.en === F.district)) &&
    (!F.pmin || p.price >= +F.pmin) && (!F.pmax || p.price <= +F.pmax) &&
    (!F.amin || p.area >= +F.amin) && (!F.amax || p.area <= +F.amax) &&
    (!F.beds || (p.bedrooms || 0) >= +F.beds) &&
    (!F.sea || (p.sea != null && p.sea <= 1000)) &&
    (!q || q.split(/\s+/).every(w => HAY.get(p.slug).includes(w)))
  );
  const S = {
    featured: (a, b) => (b.featured - a.featured) || (b.code - a.code),
    newest: (a, b) => b.code - a.code,
    "price-asc": (a, b) => a.price - b.price, "price-desc": (a, b) => b.price - a.price,
    "area-asc": (a, b) => a.area - b.area, "area-desc": (a, b) => b.area - a.area
  };
  return r.sort(S[F.sort] || S.featured);
}
const activeCount = () => KEYS.filter(k => !["q", "sort", "type"].includes(k) && F[k]).length;

function syncUrl() {
  if (view !== "home") return;
  const p = new URLSearchParams();
  KEYS.forEach(k => { if (F[k] && F[k] !== DEF[k]) p.set(k, F[k]); });
  if (qs0.get("lang")) p.set("lang", lang);
  const s = p.toString();
  history.replaceState(history.state, "", "/" + (s ? "?" + s : "") + location.hash);
}

/* ===== Тексты интерфейса ===== */
function applyTexts() {
  document.documentElement.lang = lang;
  $$("[data-i]").forEach(el => { const v = t[el.dataset.i]; if (typeof v === "string") el.textContent = v; });
  $$("[data-i-aria]").forEach(el => el.setAttribute("aria-label", t[el.dataset.iAria]));
  $$("[data-ph]").forEach(el => el.placeholder = t[el.dataset.ph]);
  $$("[data-alt]").forEach(el => el.alt = t[el.dataset.alt]);
  $("#lang").innerHTML = LANGS.map(l => `<button type="button" data-lang="${l}" aria-pressed="${l === lang}">${l.toUpperCase()}</button>`).join("");
  $("#steps").innerHTML = t.steps.map(s => `<li><h3>${esc(s[0])}</h3><p>${esc(s[1])}</p></li>`).join("");
  $("#aboutList").innerHTML = t.aboutList.map(s => `<li>${esc(s)}</li>`).join("");
  $("#contactList").innerHTML = [
    [t.cPhone, `tel:${CONTACT.phone}`, CONTACT.phoneShow],
    [t.cWa, `https://wa.me/${CONTACT.whatsapp}`, CONTACT.whatsappShow],
    [t.cViber, `viber://chat?number=${encodeURIComponent(CONTACT.viber)}`, CONTACT.viberShow],
    [t.cEmail, `mailto:${CONTACT.email}`, CONTACT.email]
  ].filter(r => r[2]).map(([k, h, v]) => `<li><span class="k">${esc(k)}</span><a href="${h}"${h.startsWith("http") ? ' target="_blank" rel="noopener"' : ""}>${esc(v)}</a></li>`).join("");
  $("#updated").textContent = DATA.updated ? `${t.updated}: ${new Date(DATA.updated).toLocaleDateString(t.locale)}` : "";
  renderQuiz();
  renderFilters();
  updateFavCounts();
}

/* ===== Фильтры: разметка ===== */
function opts(list, cur) { return list.map(([v, l]) => `<option value="${esc(v)}"${String(cur) === String(v) ? " selected" : ""}>${esc(l)}</option>`).join(""); }
function renderFilters() {
  const types = ["apt", "house", "villa", "plot", "commercial"].filter(k => LIST.some(p => p.type === k));
  $("#typeChips").setAttribute("aria-label", t.filters);
  $("#typeChips").innerHTML = [["", t.typesAll], ...types.map(k => [k, t.types[k]])]
    .map(([k, l]) => `<button type="button" class="chip" data-type="${k}" aria-pressed="${F.type === k}">${esc(l)}</button>`).join("");
  const sortOpts = Object.entries(t.sort);
  $("#sort").innerHTML = opts(sortOpts, F.sort);
  $("#q").value = F.q;

  const cities = [...new Set(LIST.map(p => p.place))];
  const districts = [...new Map(LIST.filter(p => p.district && (!F.city || p.place === F.city)).map(p => [p.district.en, p.district[lang]])).entries()];
  const adv = (id) => `
    <div class="adv-grid">
      <div class="field"><span>${esc(t.deal)}</span><div class="seg" role="group">
        ${[["", t.dealAll], ["sale", t.dealSale], ["rent", t.dealRent]].map(([v, l]) => `<button type="button" data-deal="${v}" aria-pressed="${F.deal === v}">${esc(l)}</button>`).join("")}
      </div></div>
      <label class="field"><span>${esc(t.city)}</span><select data-f="city">${opts([["", t.cityAll], ...cities.map(c => [c, PLACES[c]?.[lang] || c])], F.city)}</select></label>
      ${districts.length ? `<label class="field"><span>${esc(t.district)}</span><select data-f="district">${opts([["", t.districtAll], ...districts], F.district)}</select></label>` : ""}
      <div class="field wide"><span>${esc(t.price)}</span><div class="pair">
        <input inputmode="numeric" data-f="pmin" id="${id}-pmin" placeholder="${esc(t.from)}" aria-label="${esc(t.price + " " + t.from)}" value="${esc(F.pmin)}">
        <input inputmode="numeric" data-f="pmax" id="${id}-pmax" placeholder="${esc(t.to)}" aria-label="${esc(t.price + " " + t.to)}" value="${esc(F.pmax)}"></div></div>
      <div class="field wide"><span>${esc(t.area)}</span><div class="pair">
        <input inputmode="numeric" data-f="amin" id="${id}-amin" placeholder="${esc(t.from)}" aria-label="${esc(t.area + " " + t.from)}" value="${esc(F.amin)}">
        <input inputmode="numeric" data-f="amax" id="${id}-amax" placeholder="${esc(t.to)}" aria-label="${esc(t.area + " " + t.to)}" value="${esc(F.amax)}"></div></div>
      <label class="field"><span>${esc(t.beds)}</span><select data-f="beds">${opts([["", t.any], ["1", "1+"], ["2", "2+"], ["3", "3+"], ["4", "4+"]], F.beds)}</select></label>
      <div class="field"><span>&nbsp;</span><span class="seg"><button type="button" data-sea aria-pressed="${!!F.sea}">${esc(SEA_NEAR[lang])}</button></span></div>
      ${id === "m" ? `<label class="field"><span>${esc(t.sortLabel)}</span><select data-f="sort">${opts(sortOpts, F.sort)}</select></label>` : ""}
    </div>`;
  $("#advDesktop").innerHTML = adv("d");
  $("#advMobile").innerHTML = adv("m");
  const n = activeCount();
  $("#filterBadge").hidden = !n; $("#filterBadge").textContent = n;
}

/* ===== Каталог ===== */
const io = "IntersectionObserver" in window ? new IntersectionObserver(es => es.forEach(e => {
  if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
}), {rootMargin: "0px 0px -6% 0px"}) : null;

function cardHtml(p, reveal) {
  const fav = favs.has(p.slug);
  const st = p.status !== "sale" ? `<span class="card-status ${p.status === "sold" || p.status === "rented" ? "sold" : ""}">${esc(t.status[p.status])}</span>` : "";
  const area = p.area ? `${num(p.area)} м²` : "";
  return `<article class="card${reveal && io && !reduceMotion ? " reveal" : ""}" data-slug="${p.slug}">
    <a class="card-media" href="${propPath(p)}" data-open="${p.slug}" tabindex="-1" aria-hidden="true">
      <img src="${esc(p.photos[0] || "")}" alt="" loading="lazy" decoding="async" width="1200" height="800">
      <span class="card-type">${esc(t.type1[p.type])}</span>${st}
    </a>
    <button class="heart" type="button" data-fav="${p.slug}" aria-pressed="${fav}" aria-label="${esc(fav ? t.removeFav : t.addFav)}">${heartSvg}</button>
    <div class="card-body">
      <h3 class="card-title"><a href="${propPath(p)}" data-open="${p.slug}">${esc(p.title[lang])}</a></h3>
      <div class="card-meta"><span>${esc(loc(p))}</span><span>${area}</span></div>
      <div class="card-foot"><span class="price">${money(p.price)}</span><a class="more" href="${propPath(p)}" data-open="${p.slug}" tabindex="-1">${esc(t.more)}</a></div>
    </div>
  </article>`;
}
function observeCards(root) { if (io && !reduceMotion) $$(".card.reveal:not(.in)", root).forEach(c => io.observe(c)); }

function renderCatalog(reveal = true) {
  const r = applyFilters();
  const page = r.slice(0, shown);
  $("#grid").innerHTML = page.map(p => cardHtml(p, reveal)).join("");
  observeCards($("#grid"));
  $("#resultCount").textContent = t.found(r.length);
  $("#empty").hidden = r.length > 0;
  $("#moreBtn").hidden = r.length <= shown;
  $("#resetBtn").hidden = KEYS.every(k => k === "sort" || !F[k]);
  $("#sheetApply").textContent = t.apply(r.length);
  const n = activeCount(); $("#filterBadge").hidden = !n; $("#filterBadge").textContent = n;
  syncUrl();
}
function setFilter(k, v, rerenderFilters) {
  F[k] = v; shown = PAGE;
  if (k === "city") F.district = "";
  if (rerenderFilters) renderFilters();
  renderCatalog(false);
}
function resetFilters() { F = {...DEF}; shown = PAGE; renderFilters(); renderCatalog(false); }

let qTimer;
$("#q").addEventListener("input", e => { clearTimeout(qTimer); qTimer = setTimeout(() => setFilter("q", e.target.value), 220); });
$("#sort").addEventListener("change", e => setFilter("sort", e.target.value, true));
$("#moreBtn").addEventListener("click", () => { shown += PAGE; renderCatalog(true); });
$("#resetBtn").addEventListener("click", resetFilters);
$("#emptyReset").addEventListener("click", resetFilters);
document.addEventListener("change", e => {
  const f = e.target.closest("[data-f]");
  if (f && f.tagName === "SELECT" && (f.closest("#advDesktop") || f.closest("#advMobile"))) setFilter(f.dataset.f, f.value, true);
});
document.addEventListener("input", e => {
  const f = e.target.closest("input[data-f]");
  if (!f) return;
  clearTimeout(qTimer); qTimer = setTimeout(() => setFilter(f.dataset.f, f.value.replace(/[^\d]/g, "")), 350);
});

/* мобильная панель фильтров */
const sheet = $("#filterSheet");
$("#openFilters").addEventListener("click", () => { renderFilters(); renderCatalog(false); sheet.showModal(); });
$("#sheetApply").addEventListener("click", () => { sheet.close(); $("#catalog").scrollIntoView({behavior: reduceMotion ? "auto" : "smooth"}); });
$("#sheetReset").addEventListener("click", resetFilters);
sheet.addEventListener("click", e => { if (e.target === sheet) sheet.close(); });

/* ===== Подбор за 3 вопроса ===== */
function renderQuiz() {
  const g = (name, title, o) => `<fieldset class="q"><legend>${esc(title)}</legend><div class="q-opts">${Object.entries(o).map(([v, l], i) =>
    `<label><input type="radio" name="${name}" value="${v}"${i === 0 ? " required" : ""}><span>${esc(l)}</span></label>`).join("")}</div></fieldset>`;
  $("#quizForm").innerHTML = g("q1", t.q1, t.q1o) + g("q2", t.q2, t.q2o) + g("q3", t.q3, t.q3o) + `<button class="btn btn-dark" type="submit">${esc(t.quizGo)}</button>`;
}
$("#quizForm").addEventListener("submit", e => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const a = {q1: fd.get("q1"), q2: fd.get("q2"), q3: fd.get("q3")};
  const next = {...DEF};
  if (a.q1 === "invest") next.type = "apt";
  if (a.q2 === "b1") next.pmax = "100000";
  if (a.q2 === "b2") { next.pmin = "100000"; next.pmax = "200000"; }
  if (a.q2 === "b3") next.pmin = "200000";
  if (a.q3 === "sea") next.sea = "1";
  if (a.q3 === "city") next.city = "kavala";
  if (a.q3 === "quiet" && !next.type) next.type = "house";
  F = next;
  if (!applyFilters().length) { F.type = ""; F.city = ""; }
  if (!applyFilters().length) { F.sea = ""; }
  if (!applyFilters().length) { F.pmin = ""; F.pmax = ""; }
  shown = PAGE; renderFilters(); renderCatalog(true);
  track("quiz", a);
  $("#catalog").scrollIntoView({behavior: reduceMotion ? "auto" : "smooth"});
});

/* ===== Избранное ===== */
function updateFavCounts() {
  $$("[data-fav-count]").forEach(el => el.textContent = favs.size || "");
}
function toggleFav(slug) {
  favs.has(slug) ? favs.delete(slug) : favs.add(slug);
  saveFavs(); updateFavCounts();
  const on = favs.has(slug);
  $$(`[data-fav="${slug}"]`).forEach(b => { b.setAttribute("aria-pressed", on); b.setAttribute("aria-label", on ? t.removeFav : t.addFav); });
  if (view === "fav") renderFav();
  track(on ? "fav_add" : "fav_remove", {slug});
}
function renderFav() {
  const items = LIST.filter(p => favs.has(p.slug));
  $("#favGrid").innerHTML = items.map(p => cardHtml(p, false)).join("");
  $("#favEmpty").hidden = items.length > 0;
  $("#favCountLine").textContent = t.favCount(items.length);
}

/* ===== Страница объекта ===== */
function renderProp(p) {
  const v = $("#view-prop");
  if (!p) {
    v.innerHTML = `<div class="notfound"><div><h1>${esc(t.nfTitle)}</h1><p>${esc(t.nfText)}</p><a class="btn btn-dark" href="/#catalog" data-link="catalog">${esc(t.toCatalog)}</a></div></div>`;
    document.title = t.nfTitle + " · VENI";
    return;
  }
  const fav = favs.has(p.slug);
  const msg = `${t.waProp}\n${p.title[lang]} (${t.code} ${p.code})\n${location.origin}${propPath(p)}`;
  const specs = [
    [t.sp.type, t.type1[p.type]],
    [t.sp.deal, p.deal === "rent" ? t.dealRent : t.dealSale],
    [t.sp.status, t.status[p.status]],
    [t.sp.area, p.area ? `${num(p.area)} м²` : ""],
    [t.sp.plot, p.plot ? `${num(p.plot)} м²` : ""],
    [t.sp.beds, p.bedrooms || ""],
    [t.sp.baths, p.bathrooms || ""],
    [t.sp.floor, p.floor || ""],
    [t.sp.furn, p.furnished == null ? "" : p.furnished ? t.furnYes : t.furnNo],
    [t.sp.lift, p.lift ? t.yes : ""],
    [t.sp.sea, seaText(p)],
    [t.sp.ppm, p.area ? money(Math.round(p.price / p.area)) : ""]
  ].filter(r => r[1] !== "" && r[1] != null);
  const similar = LIST.filter(x => x.slug !== p.slug)
    .sort((a, b) => ((b.type === p.type) + (b.place === p.place)) - ((a.type === p.type) + (a.place === p.place)) || Math.abs(a.price - p.price) - Math.abs(b.price - p.price))
    .slice(0, 3);
  const desc = String(p.desc[lang] || "").split(/\n{2,}/).map(par => `<p>${esc(par).replace(/\n/g, "<br>")}</p>`).join("");
  v.innerHTML = `
    <div class="prop-hero" id="propHero" style="${heroStyle()}">
      <img id="propHeroImg" src="${esc(p.photos[0] || "")}" alt="${esc(p.title[lang])}" width="1200" height="800">
      <div class="prop-top">
        <a class="pill" href="/#catalog" data-back>${esc(t.back)}</a>
        <button class="heart" type="button" data-fav="${p.slug}" aria-pressed="${fav}" aria-label="${esc(fav ? t.removeFav : t.addFav)}">${heartSvg}</button>
      </div>
      ${p.photos.length ? `<button class="pill prop-gal-btn" type="button" data-gal="0">${esc(t.allPhotos(p.photos.length))}</button>` : ""}
    </div>
    <div class="prop-content" id="propContent">
      <div class="prop-body">
        <div class="prop-main">
          <div class="prop-head">
            <p class="eyebrow">${esc(t.type1[p.type])} · ${esc(t.code)} ${p.code} · ${esc(t.status[p.status])}</p>
            <h1>${esc(p.title[lang])}</h1>
            <div class="prop-loc">${esc(loc(p))}</div>
            <div class="prop-price">${money(p.price)}${p.area ? `<small>${money(Math.round(p.price / p.area))} / м²</small>` : ""}</div>
          </div>
          <dl class="specs" style="margin-top:26px">${specs.map(([k, val]) => `<div><dt>${esc(k)}</dt><dd>${esc(val)}</dd></div>`).join("")}</dl>
          <section style="margin-top:40px"><h2 class="prop-h2">${esc(t.descH)}</h2><div class="prop-desc">${desc}</div>
            ${(p.feat?.[lang] || []).length ? `<ul class="feat">${p.feat[lang].map(f => `<li>${esc(f)}</li>`).join("")}</ul>` : ""}</section>
          ${p.photos.length > 1 ? `<section style="margin-top:40px"><h2 class="prop-h2">${esc(t.galH)}</h2><div class="thumbs">${p.photos.map((ph, i) =>
            `<button type="button" data-gal="${i}" aria-label="${esc(t.galH)} ${i + 1}"><img src="${esc(ph)}" alt="" loading="lazy" width="1200" height="800"></button>`).join("")}</div></section>` : ""}
        </div>
        <aside class="prop-aside">
          <div class="prop-contact">
            <h3 style="font-size:1.6rem">${esc(t.askTitle)}</h3>
            <p>${esc(t.askText)}</p>
            <a class="btn btn-dark" href="${waLink(msg)}" target="_blank" rel="noopener" data-book="${p.code}">${esc(t.book)}</a>
            <a class="btn btn-outline" href="tel:${CONTACT.phone}">${esc(CONTACT.phoneShow)}</a>
          </div>
          ${p.url ? `<a class="src-link" href="${esc(p.url)}" target="_blank" rel="noopener">${esc(t.source)}</a>` : ""}
        </aside>
      </div>
      ${similar.length ? `<section class="similar"><h2 class="prop-h2">${esc(t.similarH)}</h2><div class="grid">${similar.map(x => cardHtml(x, false)).join("")}</div></section>` : ""}
      <div class="prop-spacer"></div>
    </div>
    <div class="prop-bar"><span class="price">${money(p.price)}</span><a class="btn btn-dark" href="${waLink(msg)}" target="_blank" rel="noopener" data-book="${p.code}">${esc(t.book)}</a></div>`;
  document.title = `${p.title[lang]} · ${money(p.price)} · VENI`;
}
function heroTop() { return isDesktop() ? ($("#topbar").offsetHeight || 64) : 0; }
function heroHeight() { return Math.round(isDesktop() ? innerHeight * 0.74 : Math.max(340, innerHeight * 0.64)); }
function heroStyle() { return `margin-top:${heroTop()}px;height:${heroHeight()}px`; }

/* ===== Вид / маршрут ===== */
let view = "home";
let homeReadyFromApp = false; // true, если объект открыт из каталога этого сайта (тогда «назад» = история браузера)
let returnTo = {view: "home", scroll: 0};
let currentSlug = null;
let animating = false;
let homeReady = false;

function setView(name) {
  view = name;
  $("#view-home").hidden = name !== "home";
  $("#view-prop").hidden = name !== "prop";
  $("#view-fav").hidden = name !== "fav";
  document.body.dataset.view = name;
  updateChrome();
}
function updateChrome() {
  const top = $("#topbar"), bn = $("#bottomnav");
  const pastHero = scrollY > ($("#hero").offsetHeight - 80);
  top.classList.toggle("solid", view !== "home" || pastHero);
  top.style.transform = (view === "prop" && !isDesktop()) ? "translateY(-110%)" : "";
  bn.classList.toggle("away", view === "prop");
  $$("[data-nav]").forEach(a => a.removeAttribute("aria-current"));
  $$(".topnav a").forEach(a => a.removeAttribute("aria-current"));
  const cur = view === "fav" ? "favorites" : (view === "home" ? (nearContact ? "contact" : "catalog") : "");
  if (cur) { $$(`[data-nav="${cur}"],.topnav [data-link="${cur}"]`).forEach(a => a.setAttribute("aria-current", "page")); }
}
function scrollToY(y) { window.scrollTo({top: y, left: 0, behavior: "instant"}); }
function homeTitle() { document.title = `${t.aboutTitle.replace(/\.$/, "")} · VENI Real Estate`; }

function ensureHome() { if (!homeReady) { renderCatalog(true); homeReady = true; } }

function parse(pathname) {
  const m = pathname.match(/^\/properties\/([^/]+)\/?$/);
  if (m) return {view: "prop", slug: decodeURIComponent(m[1])};
  if (/^\/favorites\/?$/.test(pathname)) return {view: "fav"};
  return {view: "home"};
}

/* открыть объект с анимацией фото из карточки */
function openProp(slug, srcImg, push = true) {
  if (animating) return;
  const p = bySlug(slug);
  if (view !== "prop") returnTo = {view, scroll: scrollY, slug};
  if (push) homeReadyFromApp = true;
  currentSlug = slug;
  if (push) history.pushState({v: "prop", slug, from: view}, "", propPath(p || {slug}));
  renderProp(p);
  track("view_property", {slug});
  const content = $("#propContent");
  const from = srcImg && srcImg.complete && srcImg.naturalWidth ? srcImg.getBoundingClientRect() : null;
  if (!p || !from || reduceMotion || from.bottom < 0 || from.top > innerHeight) {
    setView("prop"); scrollToY(0);
    requestAnimationFrame(() => content && content.classList.add("in"));
    return;
  }
  animating = true;
  const fly = srcImg.cloneNode();
  fly.className = "fly"; fly.removeAttribute("loading");
  Object.assign(fly.style, {top: from.top + "px", left: from.left + "px", width: from.width + "px", height: from.height + "px", borderRadius: "6px"});
  document.body.appendChild(fly);
  const leaving = view === "fav" ? $("#view-fav") : $("#view-home");
  leaving.classList.add("fading");
  const to = {top: heroTop(), left: 0, width: document.documentElement.clientWidth, height: heroHeight()};
  const anim = fly.animate([
    {top: from.top + "px", left: from.left + "px", width: from.width + "px", height: from.height + "px", borderRadius: "6px"},
    {top: to.top + "px", left: to.left + "px", width: to.width + "px", height: to.height + "px", borderRadius: "0px"}
  ], {duration: 650, easing: "cubic-bezier(0.2,0.75,0.2,1)", fill: "forwards"});
  const hero = $("#propHeroImg");
  setTimeout(() => {
    hero.style.opacity = "0";
    leaving.classList.remove("fading");
    setView("prop"); scrollToY(0);
  }, 330);
  const done = () => {
    if (!fly.isConnected) return;
    hero.style.opacity = "";
    fly.remove(); animating = false;
    requestAnimationFrame(() => content.classList.add("in"));
  };
  anim.onfinish = done; anim.oncancel = done;
  setTimeout(done, 1200); // страховка: убрать клон в любом случае
}

/* вернуться в каталог / избранное с обратной анимацией */
function closeProp() {
  if (animating) return;
  const target = returnTo.view === "fav" ? "fav" : "home";
  const slug = currentSlug;
  const heroImg = $("#propHeroImg");
  const hr = heroImg ? heroImg.getBoundingClientRect() : null;
  const heroVisible = hr && hr.bottom > 60 && heroImg.complete && heroImg.naturalWidth;
  if (target === "fav") renderFav(); else ensureHome();
  setView(target);
  scrollToY(returnTo.scroll || 0);
  homeTitle();
  const card = $(`${target === "fav" ? "#favGrid" : "#grid"} .card[data-slug="${CSS.escape(slug || "")}"] .card-media img`);
  const cr = card ? card.getBoundingClientRect() : null;
  if (reduceMotion || !heroVisible || !cr || cr.bottom < 0 || cr.top > innerHeight) return;
  animating = true;
  const fly = heroImg.cloneNode();
  fly.className = "fly"; fly.removeAttribute("id");
  document.body.appendChild(fly);
  card.style.opacity = "0";
  const anim = fly.animate([
    {top: hr.top + "px", left: hr.left + "px", width: hr.width + "px", height: hr.height + "px", borderRadius: "0px"},
    {top: cr.top + "px", left: cr.left + "px", width: cr.width + "px", height: cr.height + "px", borderRadius: "6px"}
  ], {duration: 560, easing: "cubic-bezier(0.2,0.75,0.2,1)", fill: "forwards"});
  const done = () => { if (!fly.isConnected) return; card.style.opacity = ""; fly.remove(); animating = false; };
  anim.onfinish = done; anim.oncancel = done; setTimeout(done, 1100);
}

function goHome(hash, push = true) {
  if (view === "prop" && history.state && history.state.v === "prop" && push && !hash) { history.back(); return; }
  ensureHome();
  if (push) history.pushState({v: "home"}, "", "/" + (hash || ""));
  setView("home"); homeTitle();
  if (hash) { const el = $(hash); if (el) requestAnimationFrame(() => el.scrollIntoView({behavior: reduceMotion ? "auto" : "smooth"})); }
  else scrollToY(0);
}
function goFav(push = true) {
  renderFav();
  if (push) history.pushState({v: "fav"}, "", "/favorites/");
  setView("fav"); scrollToY(0);
  document.title = `${t.favTitle} · VENI`;
}

window.addEventListener("popstate", () => {
  const r = parse(location.pathname);
  if (r.view === "prop") { if (view !== "prop" || currentSlug !== r.slug) openProp(r.slug, null, false); return; }
  if (view === "prop") {
    if (r.view === "fav") returnTo.view = "fav"; else if (returnTo.view === "fav") returnTo = {view: "home", scroll: 0};
    closeProp(); return;
  }
  if (r.view === "fav") goFav(false); else goHome(location.hash, false);
});

/* ===== Клики ===== */
document.addEventListener("click", e => {
  const lb = e.target.closest("#lang button");
  if (lb) {
    lang = lb.dataset.lang; t = I18N[lang]; store.set("veni-lang", lang);
    applyTexts(); renderCatalog(false);
    if (view === "prop") { renderProp(bySlug(currentSlug)); $("#propContent")?.classList.add("in"); }
    if (view === "fav") renderFav();
    if (view === "home") homeTitle();
    track("language", {lang}); return;
  }
  const fb = e.target.closest("[data-fav]");
  if (fb) { e.preventDefault(); e.stopPropagation(); toggleFav(fb.dataset.fav); return; }
  const chip = e.target.closest("[data-type]");
  if (chip) { setFilter("type", chip.dataset.type, true); return; }
  const deal = e.target.closest("[data-deal]");
  if (deal) { setFilter("deal", deal.dataset.deal, true); return; }
  if (e.target.closest("[data-sea]")) { setFilter("sea", F.sea ? "" : "1", true); return; }
  const gal = e.target.closest("[data-gal]");
  if (gal) { openLightbox(+gal.dataset.gal, gal); return; }
  if (e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return; // новая вкладка — как обычно
  const op = e.target.closest("[data-open]");
  if (op) {
    e.preventDefault();
    const card = op.closest(".card");
    const img = card ? $(".card-media img", card) : null;
    if (view === "prop") { // похожий объект на странице объекта
      history.pushState({v: "prop", slug: op.dataset.open, from: "prop"}, "", propPath(bySlug(op.dataset.open) || {slug: op.dataset.open}));
      currentSlug = op.dataset.open; renderProp(bySlug(currentSlug)); scrollToY(0);
      requestAnimationFrame(() => $("#propContent")?.classList.add("in")); return;
    }
    openProp(op.dataset.open, img); return;
  }
  if (e.target.closest("[data-back]")) {
    e.preventDefault();
    if (history.state && history.state.v === "prop" && history.length > 1 && homeReadyFromApp) history.back();
    else { returnTo = {view: "home", scroll: 0}; history.pushState({v: "home"}, "", "/#catalog"); ensureHome(); setView("home"); homeTitle(); requestAnimationFrame(() => $("#catalog").scrollIntoView()); }
    return;
  }
  const link = e.target.closest("[data-link]");
  if (link) {
    const k = link.dataset.link;
    e.preventDefault();
    if (k === "favorites") { goFav(); return; }
    if (k === "home") { goHome(""); return; }
    if (view === "prop") { returnTo = {view: "home", scroll: 0}; history.pushState({v: "home"}, "", "/#" + k); ensureHome(); setView("home"); homeTitle(); requestAnimationFrame(() => $("#" + k)?.scrollIntoView()); return; }
    goHome("#" + k); return;
  }
  const book = e.target.closest("[data-book]");
  if (book) track("book_viewing", {code: book.dataset.book});
});

/* ===== Главный экран: приближение фото ===== */
const heroImg = $("#heroImg");
let ctaZoom = false, ticking = false, nearContact = false;
function onScroll() {
  ticking = false;
  if (view !== "home") return;
  updateChrome();
  if (reduceMotion || ctaZoom) return;
  const h = $("#hero").offsetHeight;
  const pr = Math.min(1, Math.max(0, scrollY / h));
  heroImg.style.transform = `scale(${1 + pr * 0.18})`;
}
addEventListener("scroll", () => { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, {passive: true});
addEventListener("resize", () => { updateChrome(); if (view === "prop") { const h = $("#propHero"); if (h) h.setAttribute("style", heroStyle()); } });
$("#heroCta").addEventListener("click", e => {
  e.preventDefault();
  const cat = $("#catalog");
  if (reduceMotion) { cat.scrollIntoView(); return; }
  ctaZoom = true;
  const cur = parseFloat((heroImg.style.transform.match(/scale\(([\d.]+)/) || [0, 1])[1]);
  heroImg.animate([{transform: `scale(${cur})`}, {transform: "scale(1.22)"}], {duration: 900, easing: "cubic-bezier(0.65,0,0.35,1)", fill: "forwards"})
    .onfinish = function () { this.cancel(); ctaZoom = false; onScroll(); };
  setTimeout(() => cat.scrollIntoView({behavior: "smooth"}), 120);
  track("hero_cta", {});
});
if ("IntersectionObserver" in window) {
  new IntersectionObserver(es => { nearContact = es[0].isIntersecting; updateChrome(); }, {threshold: .35}).observe($("#contact"));
}

/* ===== Форма → WhatsApp ===== */
$("#contactForm").addEventListener("submit", e => {
  e.preventDefault();
  const name = $("#cf-name").value.trim(), contact = $("#cf-contact").value.trim(), msg = $("#cf-msg").value.trim();
  const err = $("#formError");
  if (!name || !contact) { err.textContent = t.fErr; err.hidden = false; (!name ? $("#cf-name") : $("#cf-contact")).focus(); return; }
  err.hidden = true;
  const text = `${t.waHello}\n${t.waName}: ${name}\n${t.waContact}: ${contact}${msg ? "\n" + msg : ""}`;
  track("lead_whatsapp", {});
  window.open(waLink(text), "_blank", "noopener");
});

/* ===== Галерея ===== */
const lb = $("#lightbox"); let lbIdx = 0;
function lbShow() {
  const p = bySlug(currentSlug); if (!p) return;
  const n = p.photos.length; lbIdx = (lbIdx + n) % n;
  $("#lbImg").src = p.photos[lbIdx]; $("#lbImg").alt = `${p.title[lang]} — ${lbIdx + 1}`;
  $("#lbCount").textContent = `${lbIdx + 1} / ${n}`;
  $("#lbPrev").hidden = $("#lbNext").hidden = n < 2;
}
function openLightbox(i) { lbIdx = i; lbShow(); lb.showModal(); }
$("#lbPrev").addEventListener("click", () => { lbIdx--; lbShow(); });
$("#lbNext").addEventListener("click", () => { lbIdx++; lbShow(); });
$("#lbClose").addEventListener("click", () => lb.close());
lb.addEventListener("keydown", e => { if (e.key === "ArrowLeft") { lbIdx--; lbShow(); } if (e.key === "ArrowRight") { lbIdx++; lbShow(); } });
let sx = null, sy = null;
$("#lbStage").addEventListener("pointerdown", e => { sx = e.clientX; sy = e.clientY; });
$("#lbStage").addEventListener("pointerup", e => {
  if (sx == null) return;
  const dx = e.clientX - sx, dy = e.clientY - sy; sx = null;
  if (Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy)) { lbIdx += dx < 0 ? 1 : -1; lbShow(); }
});

/* битые фото — спокойный фон вместо значка ошибки */
document.addEventListener("error", e => { if (e.target.tagName === "IMG") e.target.style.visibility = "hidden"; }, true);

/* ===== Старт ===== */
applyTexts();
const start = parse(location.pathname);
if (start.view === "prop") {
  renderProp(bySlug(start.slug)); currentSlug = start.slug;
  history.replaceState({v: "prop-direct", slug: start.slug}, "", location.pathname + location.search);
  setView("prop"); requestAnimationFrame(() => $("#propContent")?.classList.add("in"));
} else if (start.view === "fav") {
  history.replaceState({v: "fav"}, "", location.pathname + location.search);
  goFav(false);
} else {
  ensureHome(); history.replaceState({v: "home"}, "", location.pathname + location.search + location.hash);
  setView("home"); homeTitle(); onScroll();
}
})();
