/* Отправка заявок с сайта на почту Венеры. Используется на главной и на странице Golden Visa.
   Сервис 1: Web3Forms — работает, когда ниже вписан ключ (бесплатно: web3forms.com → ввести email → ключ придёт на почту).
   Сервис 2: FormSubmit — запасной.
   Если сервис не ответил за 15 секунд — ошибка, и на странице появляется кнопка WhatsApp с заполненной заявкой. */
window.LEADS_EMAIL = 'khassanovav@gmail.com';
window.WEB3FORMS_KEY = ''; // ← сюда ключ Web3Forms

window.sendLead = async function (body) {
  const timeout = ms => { const ac = new AbortController(); setTimeout(() => ac.abort(), ms); return ac.signal; };
  const tries = [];
  if (window.WEB3FORMS_KEY) tries.push(async () => {
    const data = {access_key: window.WEB3FORMS_KEY, subject: body._subject || 'Заявка с сайта VENI', from_name: 'Сайт VENI'};
    Object.keys(body).forEach(k => { if (!k.startsWith('_')) data[k] = body[k]; });
    const r = await fetch('https://api.web3forms.com/submit', {method: 'POST', headers: {'Content-Type': 'application/json', Accept: 'application/json'}, body: JSON.stringify(data), signal: timeout(15000)});
    const j = await r.json().catch(() => ({}));
    if (!r.ok || j.success !== true) throw new Error(j.message || ('Web3Forms ' + r.status));
  });
  tries.push(async () => {
    const r = await fetch('https://formsubmit.co/ajax/' + window.LEADS_EMAIL, {method: 'POST', headers: {'Content-Type': 'application/json', Accept: 'application/json'}, body: JSON.stringify(body), signal: timeout(15000)});
    const j = await r.json().catch(() => ({}));
    if (!r.ok || String(j.success) !== 'true') throw new Error(j.message || ('FormSubmit ' + r.status));
  });
  let last;
  for (const t of tries) {
    try { await t(); return true; }
    catch (e) { last = e && e.name === 'AbortError' ? new Error('сервис отправки не ответил') : e; console.warn('sendLead:', last && last.message); }
  }
  throw last;
};
