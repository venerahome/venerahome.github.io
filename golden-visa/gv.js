/* Страница «ВНЖ в Греции через недвижимость» (Golden Visa) — тексты RU/EN, анкета-фильтр, отправка заявки на почту */
const LEADS_EMAIL = 'khassanovav@gmail.com';   // куда приходят заявки
const WHATSAPP = '359882593077';
const GA_ID = 'G-73W576V144';
if (GA_ID) {
  const g = document.createElement('script'); g.async = true; g.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_ID; document.head.appendChild(g);
  window.dataLayer = window.dataLayer || []; window.gtag = function () { dataLayer.push(arguments); }; gtag('js', new Date()); gtag('config', GA_ID);
}
const track = (n, p) => { try { if (window.gtag) gtag('event', n, p || {}); } catch (e) {} };

const TX = {
ru: {
  eyebrow: 'Golden Visa · Северная Греция',
  h1: 'ВНЖ в Евросоюзе для всей семьи —<br><em>через дом у моря в Греции</em>',
  sub: 'Подберу объект под Golden Visa и проведу вас до получения ВНЖ: подбор, проверка, юрист, нотариус, подача документов.',
  cta: 'Проверить, подходите ли вы ↗',
  f1n: '5 лет', f1: 'ВНЖ с продлением', f2n: 'Шенген', f2: 'свободные поездки', f3n: '0 дней', f3: 'жить в Греции не обязательно',
  k1: '01 / Что вы получаете', benefitsTitle: 'Что даёт Golden Visa',
  benefits: [
    ['ВНЖ на 5 лет', 'с правом продления, пока недвижимость остаётся вашей'],
    ['Свободные поездки по Шенгену', 'без виз и очередей в консульства'],
    ['Вся семья по одной покупке', 'супруг(а), дети до 21 года, родители обоих супругов'],
    ['Без обязательного проживания', 'не нужно жить в Греции, чтобы сохранить ВНЖ'],
  ],
  k2: '02 / Условия', termsTitle: 'Сколько нужно вложить',
  terms: [
    ['от 250 000 €', 'Самый доступный путь к ВНЖ: здание, переведённое в жилое, или отреставрированный памятник архитектуры', '✓ Перевод или реставрация уже завершены — объект готов к подаче'],
    ['от 400 000 €', 'Северная Греция, Кавала и большая часть страны', 'Один объект, от 120 м²'],
    ['от 800 000 €', 'Афины, Салоники, Миконос, Санторини, острова с населением более 3 100 человек', 'Один объект, от 120 м²'],
  ],
  termsFine: 'Объект под Golden Visa нельзя сдавать посуточно, но можно сдавать надолго. Подходит ли конкретный объект, всегда подтверждает адвокат до сделки.',
  k3: '03 / Почему здесь', whyTitle: 'Почему Северная Греция',
  why: [
    ['ВНЖ от 250 000 €', 'объект после перевода в жилое или реставрации — перевод уже завершён, можно подавать'],
    ['Порог 400 000 €, а не 800 000 €', 'за ту же сумму — дом у моря, а не квартира в Афинах'],
    ['Море, горы и спокойная жизнь', 'Кавала — живой город с набережной, старым городом и пляжами'],
    ['Удобно добираться', 'аэропорты Кавалы и Салоник рядом'],
  ],
  k4: '04 / Подборка', closedTitle: 'Закрытая подборка объектов под Golden Visa',
  closedLead: 'Многие объекты от 250 000 € агентства не рекламируют открыто. Я пришлю подборку под ваш бюджет после короткой анкеты.',
  t1: 'Дом 250 м² · вид на море · Кавала', t2: 'Дом 257 м² · сад · Кавала', t3: '🔒 Ещё объекты — только по запросу',
  k5: '05 / Как это проходит', stepsTitle: 'От анкеты до ВНЖ',
  steps: [
    ['Анкета', '1 минута — я понимаю вашу ситуацию и бюджет'],
    ['Созвон', 'обсуждаем цель, семью и сроки, отвечаю на вопросы'],
    ['Подборка и просмотр', 'онлайн по видео или на месте — вас встретят в Греции'],
    ['Покупка', 'адвокат проверяет объект, сделка у нотариуса'],
    ['Подача на ВНЖ', 'документы на вас и семью подаются после покупки'],
  ],
  k6: 'Ваш консультант', aboutTitle: 'Венера Хасанова',
  about: [
    'Консультант по недвижимости Imoti Premier',
    'Живу на Балканах с 2013 года, между Болгарией и Грецией',
    'Несколько лет работаю с крупными агентствами Северной Греции',
    'Сама купила и восстанавливаю дом в Греции — знаю этот путь изнутри',
    'Консультирую на русском, английском и болгарском',
  ],
  k7: '06 / Анкета', formTitle: 'Проверьте, подходите ли вы',
  formLead: '6 вопросов, около минуты. Я лично отвечу и пришлю закрытую подборку.',
  qName: 'Ваше имя', qCit: 'Гражданство (страна паспорта)',
  qEu: 'Есть ли у вас паспорт страны Евросоюза?', eu: [['no', 'Нет'], ['yes', 'Да']],
  qBudget: 'Бюджет на покупку', budget: [['250-400', '250 000 – 400 000 €'], ['lt250', 'до 250 000 €'], ['400-800', '400 000 – 800 000 €'], ['800+', 'от 800 000 €']],
  qWhen: 'Когда планируете покупку?', when: [['3m', 'в ближайшие 3 месяца'], ['6m', 'в течение полугода'], ['later', 'пока изучаю']],
  qGoal: 'Главная цель', goal: [['visa', 'ВНЖ для семьи'], ['live', 'жить в Греции'], ['invest', 'вложение']],
  qContact: 'WhatsApp или email для ответа',
  send: 'Отправить и получить подборку ↗', sending: 'Отправляю…',
  privacy: 'Данные видит только Венера. Без рассылок и спама.',
  errFill: 'Пожалуйста, ответьте на все вопросы.', errSend: 'Не получилось отправить. Напишите мне в WhatsApp:',
  rHotT: 'Спасибо! Вы подходите под Golden Visa.', rHot: 'Я напишу вам в течение 24 часов и пришлю закрытую подборку. Хотите быстрее — напишите мне в WhatsApp прямо сейчас.',
  rMidT: 'Спасибо! Вы подходите под Golden Visa от 250 000 €.', rMid: 'Это самый доступный путь к ВНЖ: объект после перевода в жилое или реставрации, уже готовый к подаче. Я напишу вам в течение 24 часов и пришлю подборку. Хотите быстрее — напишите мне в WhatsApp прямо сейчас.',
  rLowT: 'Спасибо, заявка получена!', rLow: 'Для Golden Visa нужен бюджет от 250 000 €. Но я с удовольствием подберу вам дом в Греции под ваш бюджет — я напишу вам. А пока посмотрите каталог.',
  rEuT: 'Спасибо, заявка получена!', rEu: 'С паспортом Евросоюза Golden Visa вам не нужен — вы можете жить в Греции и так. Я с удовольствием подберу вам дом и напишу вам.',
  waBtn: 'Написать в WhatsApp ↗', catBtn: 'Смотреть каталог ↗',
  waHello: 'Здравствуйте, Венера! Я заполнил(а) анкету Golden Visa на сайте.',
  k8: '07 / Вопросы', faqTitle: 'Частые вопросы',
  faq: [
    ['Нужно ли жить в Греции?', 'Нет. Минимального срока проживания нет — ВНЖ сохраняется и продлевается, пока недвижимость остаётся вашей.'],
    ['Кто из семьи получает ВНЖ?', 'Супруг(а), неженатые дети до 21 года, а также родители обоих супругов (их случай рассматривается отдельно).'],
    ['Можно ли сдавать жильё?', 'Надолго — да. Посуточно (через Airbnb и похожие сервисы) — нельзя, это запрещено для объектов под Golden Visa.'],
    ['Можно ли купить несколько квартир на эту сумму?', 'Нет. Сумма должна быть вложена в один объект площадью от 120 м².'],
    ['Сколько стоит сверх цены объекта?', 'Налог на передачу собственности около 3%, нотариус, адвокат, госпошлина за ВНЖ, медицинская страховка, переводы документов. Точный расчёт пришлю под конкретный объект.'],
    ['Сколько длится оформление?', 'Зависит от объекта и готовности документов. Обычно несколько месяцев — точный срок назовёт адвокат.'],
  ],
  foot: '© 2026 Венера Хасанова · VENI · Imoti Premier',
  contactTitle: 'Или напишите мне напрямую', catalog: '← Все объекты в каталоге',
},
en: {
  eyebrow: 'Golden Visa · Northern Greece',
  h1: 'EU residency for your whole family —<br><em>through a seaside home in Greece</em>',
  sub: 'I will find a Golden Visa property for you and guide you all the way to your residence permit: selection, checks, lawyer, notary and application.',
  cta: 'Check if you qualify ↗',
  f1n: '5 years', f1: 'renewable permit', f2n: 'Schengen', f2: 'free travel', f3n: '0 days', f3: 'no need to live in Greece',
  k1: '01 / What you get', benefitsTitle: 'What the Golden Visa gives you',
  benefits: [
    ['A 5-year residence permit', 'renewable for as long as you own the property'],
    ['Free travel across Schengen', 'no visas, no consulate queues'],
    ['The whole family with one purchase', 'spouse, children under 21, and the parents of both spouses'],
    ['No minimum stay', 'you do not have to live in Greece to keep the permit'],
  ],
  k2: '02 / Requirements', termsTitle: 'How much you need to invest',
  terms: [
    ['from €250,000', 'The most affordable route to residency: a building converted to residential use, or a restored listed building', '✓ Conversion or restoration already completed — the property is ready for your application'],
    ['from €400,000', 'Northern Greece, Kavala and most of the country', 'One property, at least 120 m²'],
    ['from €800,000', 'Athens, Thessaloniki, Mykonos, Santorini, islands with more than 3,100 residents', 'One property, at least 120 m²'],
  ],
  termsFine: 'A Golden Visa property cannot be let short-term, but long-term letting is allowed. A lawyer always confirms that a specific property qualifies before the purchase.',
  k3: '03 / Why here', whyTitle: 'Why Northern Greece',
  why: [
    ['Residency from €250,000', 'a property after conversion to residential use or restoration, already completed and ready for your application'],
    ['€400,000 threshold, not €800,000', 'the same budget buys a house by the sea instead of a flat in Athens'],
    ['Sea, mountains and a calm life', 'Kavala is a lively city with a seafront, an old town and beaches'],
    ['Easy to reach', 'Kavala and Thessaloniki airports are close by'],
  ],
  k4: '04 / Selection', closedTitle: 'A private selection of Golden Visa properties',
  closedLead: 'Many properties from €250,000 are not advertised openly. I will send you a selection that fits your budget after a short questionnaire.',
  t1: '250 m² house · sea view · Kavala', t2: '257 m² house · garden · Kavala', t3: '🔒 More properties — on request only',
  k5: '05 / How it works', stepsTitle: 'From questionnaire to residence permit',
  steps: [
    ['Questionnaire', '1 minute, so I understand your situation and budget'],
    ['Call', 'we discuss your goal, family and timing, and I answer your questions'],
    ['Selection and viewing', 'online by video or in person — you will be met in Greece'],
    ['Purchase', 'a lawyer checks the property; the deal is signed at a notary'],
    ['Residence application', 'documents for you and your family are filed after the purchase'],
  ],
  k6: 'Your consultant', aboutTitle: 'Venera Khassanova',
  about: [
    'Real estate consultant at Imoti Premier',
    'Living in the Balkans since 2013, between Bulgaria and Greece',
    'Working for several years with leading agencies in Northern Greece',
    'Bought and restoring my own house in Greece — I know this path first-hand',
    'Consultations in English, Russian and Bulgarian',
  ],
  k7: '06 / Questionnaire', formTitle: 'Check if you qualify',
  formLead: '6 questions, about a minute. I will reply personally and send you the private selection.',
  qName: 'Your name', qCit: 'Citizenship (passport country)',
  qEu: 'Do you hold a passport of an EU country?', eu: [['no', 'No'], ['yes', 'Yes']],
  qBudget: 'Purchase budget', budget: [['250-400', '€250,000 – 400,000'], ['lt250', 'up to €250,000'], ['400-800', '€400,000 – 800,000'], ['800+', 'from €800,000']],
  qWhen: 'When do you plan to buy?', when: [['3m', 'within 3 months'], ['6m', 'within 6 months'], ['later', 'just exploring']],
  qGoal: 'Main goal', goal: [['visa', 'residency for my family'], ['live', 'living in Greece'], ['invest', 'investment']],
  qContact: 'WhatsApp or email for my reply',
  send: 'Send and get the selection ↗', sending: 'Sending…',
  privacy: 'Only Venera sees your details. No newsletters, no spam.',
  errFill: 'Please answer all the questions.', errSend: 'Something went wrong. Please message me on WhatsApp:',
  rHotT: 'Thank you! You qualify for the Golden Visa.', rHot: 'I will contact you within 24 hours and send you the private selection. Want it faster? Message me on WhatsApp right now.',
  rMidT: 'Thank you! You qualify for the Golden Visa from €250,000.', rMid: 'This is the most affordable route to residency: a property after conversion to residential use or restoration, ready for your application. I will contact you within 24 hours and send you a selection. Want it faster? Message me on WhatsApp right now.',
  rLowT: 'Thank you, your request is in!', rLow: 'The Golden Visa requires a budget from €250,000. I will gladly find you a home in Greece within your budget — I will contact you. Meanwhile, have a look at the catalogue.',
  rEuT: 'Thank you, your request is in!', rEu: 'With an EU passport you do not need a Golden Visa — you can already live in Greece. I will gladly find you a home and get in touch.',
  waBtn: 'Message me on WhatsApp ↗', catBtn: 'View the catalogue ↗',
  waHello: 'Hello Venera! I have filled in the Golden Visa questionnaire on your website.',
  k8: '07 / Questions', faqTitle: 'Frequently asked questions',
  faq: [
    ['Do I have to live in Greece?', 'No. There is no minimum stay — the permit is kept and renewed for as long as you own the property.'],
    ['Which family members are included?', 'Your spouse, unmarried children under 21, and the parents of both spouses (reviewed case by case).'],
    ['Can I rent the property out?', 'Long-term — yes. Short-term (Airbnb and similar) — no, this is not allowed for Golden Visa properties.'],
    ['Can I buy several flats with this amount?', 'No. The amount must be invested in one property of at least 120 m².'],
    ['What does it cost on top of the price?', 'Property transfer tax of about 3%, notary, lawyer, the permit fee, health insurance and document translations. I will send an exact estimate for a specific property.'],
    ['How long does it take?', 'It depends on the property and how ready your documents are. Usually a few months — the lawyer will give you the exact timing.'],
  ],
  foot: '© 2026 Venera Khassanova · VENI · Imoti Premier',
  contactTitle: 'Or message me directly', catalog: '← All properties in the catalogue',
},
};

const L = (window.PAGE_LANG === 'en' || window.PAGE_LANG === 'ru') ? window.PAGE_LANG
  : (/^ru|^uk|^be|^kk/i.test(navigator.language || '') ? 'ru' : 'en');
const T = TX[L];
const $ = id => document.getElementById(id);
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));

document.documentElement.lang = L;
document.querySelectorAll('.logo, .back').forEach(a => a.setAttribute('href', '/' + L + '/'));
document.querySelectorAll('[data-t]').forEach(el => { el.textContent = T[el.dataset.t]; });
document.querySelectorAll('[data-t-html]').forEach(el => { el.innerHTML = T[el.dataset.tHtml]; });
document.querySelectorAll('.langs a').forEach(a => a.setAttribute('aria-current', a.dataset.l === L ? 'true' : 'false'));
$('benefits').innerHTML = T.benefits.map(([a, b]) => `<li><b>${esc(a)}</b><span>${esc(b)}</span></li>`).join('');
$('why').innerHTML = T.why.map(([a, b]) => `<li><b>${esc(a)}</b><span>${esc(b)}</span></li>`).join('');
$('terms').innerHTML = T.terms.map(([a, b, c], i) => `<div class="term${i === 0 ? ' main' : ''}"><strong>${esc(a)}</strong><p>${esc(b)}</p><span>${esc(c)}</span></div>`).join('');
$('steps').innerHTML = T.steps.map(([a, b]) => `<li><b>${esc(a)}</b><span>${esc(b)}</span></li>`).join('');
$('aboutList').innerHTML = T.about.map(a => `<li>${esc(a)}</li>`).join('');
$('faq').innerHTML = T.faq.map(([q, a]) => `<details><summary>${esc(q)}</summary><p>${esc(a)}</p></details>`).join('');
['eu', 'budget', 'when', 'goal'].forEach(k => {
  $('o-' + k).innerHTML = T[k].map(([v, t]) => `<label class="opt"><input type="radio" name="${k}" value="${v}"><span>${esc(t)}</span></label>`).join('');
});
const labelOf = (k, v) => (T[k].find(x => x[0] === v) || [, v])[1];
const ruLabel = (k, v) => (TX.ru[k].find(x => x[0] === v) || [, v])[1];

let started = false;
$('gvForm').addEventListener('input', () => { if (!started) { started = true; track('gv_form_start', {lang: L}); } });
document.querySelectorAll('a[href="#form"]').forEach(a => a.addEventListener('click', () => track('gv_cta_click', {lang: L})));

$('gvForm').addEventListener('submit', async e => {
  e.preventDefault();
  const name = $('f-name').value.trim(), cit = $('f-cit').value.trim(), contact = $('f-contact').value.trim();
  const pick = k => (document.querySelector(`input[name="${k}"]:checked`) || {}).value;
  const eu = pick('eu'), budget = pick('budget'), when = pick('when'), goal = pick('goal');
  if (!name || !cit || !contact || !eu || !budget || !when || !goal) { $('err').textContent = T.errFill; $('err').hidden = false; return; }
  $('err').hidden = true;

  // Сортировка заявки: горячая 400k+ / горячая 250k (перевод или реставрация) / без Golden Visa / гражданин ЕС
  const tier = eu === 'yes' ? 'eu' : budget === 'lt250' ? 'low' : budget === '250-400' ? 'mid' : 'hot';
  const tag = {hot: '🔥 ГОРЯЧАЯ', mid: '🔥 ГОРЯЧАЯ · 250k (перевод/реставрация)', low: 'Бюджет до 250k', eu: 'Гражданин ЕС'}[tier];
  const body = {
    _subject: `${tag} · Golden Visa · ${name} · ${cit} · ${ruLabel('budget', budget)}`,
    _template: 'table', _captcha: 'false',
    'Категория': tag, 'Имя': name, 'Гражданство': cit, 'Паспорт ЕС': ruLabel('eu', eu),
    'Бюджет': ruLabel('budget', budget), 'Сроки': ruLabel('when', when), 'Цель': ruLabel('goal', goal),
    'Контакт': contact, 'Язык страницы': L.toUpperCase(),
  };
  const btn = $('send'); btn.disabled = true; btn.textContent = T.sending;
  const waText = [T.waHello, `${T.qName}: ${name}`, `${T.qCit}: ${cit}`, `${T.qBudget}: ${labelOf('budget', budget)}`, `${T.qWhen}: ${labelOf('when', when)}`].join('\n');
  const waLink = `https://wa.me/${WHATSAPP}?text=${encodeURIComponent(waText)}`;
  try {
    const r = await fetch('https://formsubmit.co/ajax/' + LEADS_EMAIL, {method: 'POST', headers: {'Content-Type': 'application/json', Accept: 'application/json'}, body: JSON.stringify(body)});
    const j = await r.json().catch(() => ({}));
    if (!r.ok || String(j.success) !== 'true') throw new Error(j.message || r.status);
    track('gv_lead', {tier, budget, lang: L});
    const t = {hot: [T.rHotT, T.rHot], mid: [T.rMidT, T.rMid], low: [T.rLowT, T.rLow], eu: [T.rEuT, T.rEu]}[tier];
    const second = (tier === 'low' || tier === 'eu') ? `<a class="ghost-btn" href="/${L}/#catalog">${esc(T.catBtn)}</a>` : '';
    $('result').innerHTML = `<h3>${esc(t[0])}</h3><p>${esc(t[1])}</p><a class="cta" href="${esc(waLink)}" target="_blank" rel="noopener" id="waAfter">${esc(T.waBtn)}</a>${second}`;
    $('result').hidden = false; $('gvForm').hidden = true;
    $('waAfter').addEventListener('click', () => track('gv_whatsapp', {tier}));
    $('result').scrollIntoView({behavior: 'smooth', block: 'center'});
  } catch (err) {
    console.warn('FormSubmit:', err && err.message);
    $('err').innerHTML = `${esc(T.errSend)} <a href="${esc(waLink)}" target="_blank" rel="noopener">WhatsApp ↗</a>`; $('err').hidden = false;
  } finally { btn.disabled = false; btn.textContent = T.send; }
});
