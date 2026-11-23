const { T0, VD, TXT, SEG, TOTAL } = TL; const NS = 11;
const NUMS = { '1': 'un', '2': 'deux', '3': 'trois', '4': 'quatre', '5': 'cinq', '12': 'douze', '20': 'vingt', '40': 'quarante', '30': 'trente' };
const norm = t => { t = t.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]/g, ''); return NUMS[t] || t; };
const toks = t => t.split(/\s+/).map(norm).filter(Boolean);
function cue(i, w, lead = 0.1) {
  const p = TXT[i].indexOf(w); if (p < 0) throw new Error('cue ' + w);
  const k = toks(TXT[i].slice(0, p)).length, tk = toks(w), W = TL.W[i]; let best = -1, bd = 1e9;
  for (let j = 0; j < W.length; j++) { if (W[j][0] !== tk[0]) continue; let sc = 0; for (let q = 1; q < Math.min(3, tk.length); q++) if (W[j + q] && W[j + q][0] === tk[q]) sc++; const dd = Math.abs(j - k) - sc * 4; if (dd < bd) { bd = dd; best = j; } }
  if (best < 0) { best = Math.min(W.length - 1, k); console.log('CUE approx', i, w); }
  return Math.max(0, W[best][1] - lead);
}
const at = (i, w) => T0[i] + cue(i, w);
const tl = gsap.timeline({ paused: true }); const $ = s => document.querySelector(s); const scenes = $('#scenes');
const words = (t, st = '') => t.split(' ').map(w => `<span class="w"><i style="${st}">${w}</i></span>`).join(' ');
const ML = 96, CW = 414, G = 24; const cx4 = (i, span = 1) => [ML + i * (CW + G), span * CW + (span - 1) * G];
const CK = `<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"><path class="ckp" pathLength="1" stroke-dasharray="1" stroke-dashoffset="0" d="M5 12.5l4.6 4.6L19 7.5"/></svg>`;
const chk = (col, sz, id = '') => `<div class="chk" ${id ? `id="${id}"` : ''} style="width:${sz}px;height:${sz}px;background:${col}">${CK}</div>`;
const num = (n, col, sz, st = '') => `<div class="num" style="width:${sz}px;height:${sz}px;background:${col};font-size:${Math.round(sz * .55)}px;${st}">${n}</div>`;
function sec(i, html) { const s = document.createElement('section'); s.id = 's' + i; s.innerHTML = html; scenes.appendChild(s); return s; }
function show(i, plain) {
  const s = '#s' + i; tl.set(s, { visibility: 'visible' }, Math.max(0, T0[i] - 0.02));
  if (!plain) tl.fromTo(s, { opacity: 0, x: 60 }, { opacity: 1, x: 0, duration: .45, ease: 'power3.out' }, T0[i]);
  if (i < NS - 1) { tl.to(s, { opacity: 0, x: plain ? 0 : -60, duration: .28, ease: 'power2.in' }, T0[i + 1] - 0.3); tl.set(s, { visibility: 'hidden' }, T0[i + 1]); }
}
const pop = (sel, t, o = {}) => tl.from(sel, Object.assign({ opacity: 0, y: 46, scale: .9, duration: .6, ease: 'back.out(1.7)' }, o), t);
const rise = (sel, t, o = {}) => tl.from(sel, Object.assign({ yPercent: 115, duration: .6, ease: 'power4.out', stagger: .055 }, o), t);
const draw = (sel, t) => tl.from(sel, { strokeDashoffset: 1, duration: .45, ease: 'power2.out' }, t);
function caps(i, list) {
  const s = $('#s' + i); list.forEach(([t, txt], k) => {
    const d = document.createElement('div'); d.className = 'cap'; d.innerHTML = `<span>${txt}</span>`; s.appendChild(d); const sp = d.firstChild;
    tl.fromTo(sp, { opacity: 0, y: 34, scale: .94 }, { opacity: 1, y: 0, scale: 1, duration: .4, ease: 'back.out(1.8)' }, t);
    if (k < list.length - 1) tl.to(sp, { opacity: 0, y: -24, duration: .22, ease: 'power2.in' }, list[k + 1][0] - 0.24);
  });
}
const pill = (n, t) => `<div class="pill">${n ? `<em>${n}</em>` : ''}${t}</div>`;
const frameFns = [];

// ---------------------------------------------------------------- 0 · accroche
{
  const cC = at(0, 'Et si'), cD = at(0, 'Restez'), c12 = at(0, 'douze'), cF = at(0, 'face à');
  sec(0, `<div id="hA"><div style="position:absolute;left:0;right:0;top:96px;display:flex;justify-content:center"><div class="D" id="h0" style="background:var(--flag);color:#fff;font-size:150px;line-height:1;padding:26px 60px 30px;border-radius:26px;transform:rotate(-2deg);box-shadow:0 24px 60px rgba(229,30,32,.5)">EXPRESSION ORALE</div></div>
   <div class="hk D" id="h1" style="top:330px;font-size:104px;color:var(--yel)">${words('TCF CANADA & TCF QUÉBEC')}</div>
   <div id="chrw" style="position:absolute;left:0;right:0;top:500px;display:flex;justify-content:center"><div id="chrp" style="background:var(--flag);color:#fff;border-radius:60px;height:104px;padding:0 44px;display:flex;align-items:center;gap:22px;font-family:ID;font-weight:900;font-size:66px;box-shadow:0 16px 40px rgba(229,30,32,.45)"><u id="dot" style="width:26px;height:26px;border-radius:50%;background:#fff;display:block"></u><span id="chr">12:00</span></div></div>
   <div class="hk D" id="h2" style="top:640px;font-size:100px">${words('12 minutes, seul,')}</div><div class="hk D" id="h3" style="top:760px;font-size:100px">${words('face à un examinateur.')}</div></div>
  <div id="hB"><div class="hk D" id="h4" style="top:330px;font-size:96px">${words('Et si vous viviez cet examen')}</div>
   <div class="hk D" id="h5" style="top:470px;font-size:176px;color:var(--yel)">AVANT le jour J ?</div>
   <svg id="h5u" style="position:absolute;left:470px;top:690px" width="980" height="50" viewBox="0 0 980 50" fill="none"><path pathLength="1" stroke-dasharray="1" d="M10 34 C 250 6, 620 6, 970 26" stroke="#fff" stroke-width="12" stroke-linecap="round"/></svg></div>
  <div id="hC"><div style="position:absolute;left:0;right:0;top:170px;display:flex;justify-content:center"><div id="h6" style="background:var(--flag);color:#fff;font-weight:700;font-size:34px;height:70px;line-height:70px;padding:0 40px;border-radius:35px">EXAMEN BLANC D'EXPRESSION ORALE</div></div>
   <div class="hk D" id="h7" style="top:280px;font-size:104px">${words('Dans cette vidéo')}</div>
   ${[["Comment réserver", "L'offre, le créneau, le paiement"], ["Comment se passe la séance", "2 examens blancs, étape par étape"], ["Ce que vous recevez", "Un feedback personnalisé"]].map((c, k) => `<div class="glass hg" id="hg${k}" style="left:${ML + k * 584}px;top:490px;width:560px;height:310px"><div style="display:flex;justify-content:center;margin-top:36px">${num(k + 1, 'rgba(255,255,255,.28)', 84, 'color:#141b4d')}</div><div class="D" style="font-size:36px;margin-top:30px">${c[0]}</div><div style="font-size:26px;margin-top:14px;color:#cddaff">${c[1]}</div></div>`).join('')}
   <div class="hk D" id="h8" style="top:880px;font-size:50px;color:var(--yel);font-weight:800">Restez jusqu'à la fin ↓</div></div>`);
  show(0, true);
  tl.fromTo('#hookc', { scale: 1.12 }, { scale: 1.0, duration: 3.4, ease: 'none', transformOrigin: '50% 40%' }, 0);
  tl.to(['#hookc', '#hookv'], { opacity: 0, duration: .45 }, 2.9);
  tl.fromTo('#h0', { opacity: 0, scale: 2.6, rotation: -10 }, { opacity: 1, scale: 1, rotation: -2, duration: .5, ease: 'expo.out' }, 0.08);
  tl.to('#h0', { scale: 1.04, duration: .5, yoyo: true, repeat: 9, ease: 'sine.inOut' }, 0.7);
  tl.from('#h1 .w>i', { yPercent: 120, rotation: 6, duration: .5, ease: 'back.out(1.6)', stagger: .07 }, at(0, 'du TCF Canada') - .1);
  pop('#chrp', T0[0] + c12 - T0[0] + 0, { scale: .3, y: 0, ease: 'back.out(2.4)', duration: .5 });
  rise('#h2 .w>i', c12 + .15); rise('#h3 .w>i', cF);
  tl.to('#hA', { opacity: 0, y: -70, scale: .96, duration: .3, ease: 'power2.in' }, cC - .3);
  rise('#h4 .w>i', cC); tl.from('#h5', { opacity: 0, scale: 2.4, duration: .55, ease: 'expo.out' }, cC + .95); tl.from('#h5u path', { strokeDashoffset: 1, duration: .5, ease: 'power2.out' }, cC + 1.4);
  tl.to('#hB', { opacity: 0, y: -70, scale: .96, duration: .3, ease: 'power2.in' }, cD - .3);
  pop('#h6', cD, { y: -40 }); rise('#h7 .w>i', cD + .1); pop('.hg', cD + .3, { stagger: .12, y: 80 }); tl.from('#h8', { opacity: 0, y: 30, duration: .5 }, cD + .9);
  tl.to('#h8', { y: 10, duration: .5, yoyo: true, repeat: 7, ease: 'sine.inOut' }, cD + 1.4);
  ['comment réserver', 'comment se passe', 'ce que vous'].forEach((w, k) => { const t = at(0, w);
    tl.to(`#hg${k}`, { backgroundColor: 'rgba(255,255,255,.22)', scale: 1.06, duration: .25, ease: 'power2.out' }, t); tl.to(`#hg${k}`, { scale: 1, duration: .35, ease: 'back.out(2)' }, t + .25);
    tl.to(`#hg${k} .num`, { backgroundColor: '#ffd640', scale: 1.25, duration: .25 }, t); tl.to(`#hg${k} .num`, { scale: 1, duration: .3, ease: 'back.out(2.5)' }, t + .25); });
  frameFns.push(t => { if (t > cC) return; const s = Math.max(0, 720 - Math.max(0, t - c12) * 1); $('#chr').textContent = `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`; $('#dot').style.opacity = .55 + .45 * Math.sin(t * 8); });
}
// ---------------------------------------------------------------- 1 · c'est quoi
{
  const tiles = [['≈ <span class="cnt" data-v="40">40</span>', 'minutes', 'séance individuelle', 'séance individuelle'], ['Zoom', 'en visio', 'depuis chez vous', 'en visio'], ['<span class="cnt" data-v="2">2</span>', 'examens blancs', 'complets', 'deux simulations'], ['<span class="cnt" data-v="3">3</span>', 'tâches', 'par examen', 'trois tâches']];
  const [x0, w2] = cx4(0, 2), [x2] = cx4(2, 2);
  sec(1, pill(0, "C'est quoi ?") + tiles.map((c, k) => `<div class="card t1" id="t1${k}" style="left:${cx4(k)[0]}px;top:180px;width:${CW}px;height:230px;border-color:var(--royal);padding:22px 34px"><div class="D" style="font-size:96px;color:var(--royal);line-height:1.05">${c[0]}</div><div class="D" style="font-size:34px;margin-top:2px">${c[1]}</div><div style="font-size:24px;color:var(--slate)">${c[2]}</div></div>`).join('') +
    `<div class="card" id="exc" style="left:${x0}px;top:440px;width:${w2}px;height:510px"><div style="position:absolute;left:40px;top:34px;font-weight:700;font-size:24px;color:var(--royal);letter-spacing:.04em">VOS EXAMINATEURS</div>
      ${[['AHLEM', 'Examinatrice habilitée', 'fa.jpg'], ['EMMANUEL', 'Examinateur habilité', 'fe.jpg']].map((p, k) => `<div class="exp" id="exp${k}" style="position:absolute;left:${k * 426}px;top:92px;width:426px;text-align:center"><img src="${p[2]}" style="width:216px;height:216px;border-radius:50%;border:5px solid var(--royal);box-shadow:0 14px 30px rgba(24,56,255,.25)"><div class="D" style="font-size:40px;margin-top:14px">${p[0]}</div><div style="font-size:24px;color:var(--slate)">${p[1]}</div></div>`).join('')}
      <div id="exchip" style="position:absolute;left:40px;right:40px;top:430px;height:54px;border-radius:27px;background:var(--tint);color:var(--royal);font-weight:600;font-size:24px;line-height:54px;text-align:center">Vous choisissez votre examinateur au moment de réserver</div></div>
    <div class="card" id="ret" style="left:${x2}px;top:440px;width:${w2}px;height:170px;border-color:var(--green);display:flex;align-items:center;gap:28px;padding:0 40px">${chk('var(--green)', 80)}<div><div class="D" style="font-size:38px">Un retour personnalisé</div><div style="font-size:26px;color:var(--slate)">Après chacune des deux simulations</div></div></div>
    <div class="card" id="amb" style="left:${x2}px;top:634px;width:${w2}px;height:316px;border-color:#fad778;background:#fffae8;padding:36px 40px"><div class="D" id="amb1" style="font-size:46px;color:#b45309;line-height:1.2">${words("Ce n'est pas un cours.")}<br>${words("C'est une simulation.")}</div><div id="amb2" style="font-weight:600;font-size:28px;margin-top:34px;line-height:1.45">L'examinateur se comporte exactement<br>comme le jour de l'examen.</div></div>`);
  show(1, true); tl.from('#s1 .pill', { x: 300, opacity: 0, duration: .5, ease: 'back.out(1.5)' }, T0[1] + .35);
  tiles.forEach((c, k) => { const t = at(1, c[3]); pop(`#t1${k}`, t); const e = $(`#t1${k} .cnt`); if (e) tl.from(e, { textContent: 0, snap: { textContent: 1 }, duration: .7, ease: 'power2.out' }, t + .1); });
  pop('#exc', at(1, 'avec un examinateur'), { y: 70 }); pop('#exp0', at(1, 'Ahlem'), { scale: .4, ease: 'back.out(2.2)' }); pop('#exp1', at(1, 'Emmanuel'), { scale: .4, ease: 'back.out(2.2)' }); tl.from('#exchip', { opacity: 0, scaleX: .6, duration: .4 }, at(1, 'Emmanuel') + .5);
  pop('#ret', at(1, 'avec un retour'), { x: 80, y: 0 }); draw('#ret .ckp', at(1, 'avec un retour') + .3);
  pop('#amb', at(1, 'Attention'), { x: 80, y: 0 }); rise('#amb1 .w>i', at(1, 'Attention') + .25); tl.from('#amb2', { opacity: 0, y: 20, duration: .5 }, at(1, "L'examinateur se"));
}
// ---------------------------------------------------------------- 2 · pour qui
{
  const it = [["Vous passez le TCF Canada ou le TCF Québec bientôt", "Dans les prochaines semaines : c'est le moment de vous tester.", 'si vous passez'], ["Vous n'avez jamais parlé face à un examinateur", "Vous vivez le stress du jour J avant, sans l'enjeu.", "si vous n'avez"], ["Vous voulez savoir ce qui vous coûte des points à l'oral", "Un avis humain, précis, sur votre performance.", 'ou si vous']];
  sec(2, pill(0, 'Pour qui ?') + `<div class="D" id="pq" style="position:absolute;left:${ML}px;top:178px;font-size:64px">${words('Cette séance est idéale si…')}</div>` + it.map((c, k) => `<div class="card pqr" id="pq${k}" style="left:${ML}px;top:${290 + k * 229}px;width:1728px;height:202px;border-color:var(--green);display:flex;align-items:center;gap:40px;padding:0 50px">${chk('var(--green)', 84)}<div><div class="D" style="font-size:46px">${c[0]}</div><div style="font-size:29px;color:var(--slate);margin-top:8px">${c[1]}</div></div></div>`).join(''));
  show(2); tl.from('#s2 .pill', { x: 300, opacity: 0, duration: .5, ease: 'back.out(1.5)' }, T0[2] + .2); rise('#pq .w>i', T0[2] + .1);
  it.forEach((c, k) => { const t = at(2, c[2]); tl.from(`#pq${k}`, { x: -220, opacity: 0, duration: .6, ease: 'back.out(1.3)' }, t); tl.from(`#pq${k} .chk`, { scale: 0, duration: .45, ease: 'back.out(3)' }, t + .25); draw(`#pq${k} .ckp`, t + .45); });
}
// ---------------------------------------------------------------- navigateur
const CUR = `<svg viewBox="0 0 24 24"><path d="M4 2l15 9.5-6.6 1.4L16 20l-3 1.4-3.5-7L5 19z" fill="#fff" stroke="#141b4d" stroke-width="1.6" stroke-linejoin="round"/></svg>`;
function browser(i, url, imgs, hpage) {
  const html = `<div class="br" id="br${i}"><div class="bar"><u style="background:#ff5f56"></u><u style="background:#ffbd2e"></u><u style="background:#27c93f"></u><p>${url}</p></div><div class="vp"><div class="page" id="pg${i}">${imgs.map((f, k) => `<img id="im${i}_${k}" src="cap/${f}.jpg" style="${k ? 'opacity:0' : ''}">`).join('')}<div class="rip" id="rip${i}"></div><div class="cur" id="cur${i}">${CUR}</div></div></div></div>`;
  const cam = { s: 1.0775, cx: 800, cy: 349 };
  frameFns.push(() => { const s = cam.s, tx = Math.min(0, Math.max(1724 - 1600 * s, 862 - cam.cx * s)), ty = Math.min(0, Math.max(752 - hpage * s, 376 - cam.cy * s)); $('#pg' + i).style.transform = `translate(${tx}px,${ty}px) scale(${s})`; });
  const api = { html, cam,
    to(t, s, cx, cy, d = 1.1) { tl.to(cam, { s, cx, cy, duration: d, ease: 'power3.inOut' }, t - .25); },
    hl(r, t0, t1, pad = 7) { t0 = Math.min(t0, t1 - 1.0); const e = document.createElement('div'); e.className = 'hl'; Object.assign(e.style, { left: r[0] - pad + 'px', top: r[1] - pad + 'px', width: r[2] + 2 * pad + 'px', height: r[3] + 2 * pad + 'px' }); $('#pg' + i).insertBefore(e, $('#rip' + i));
      tl.fromTo(e, { opacity: 0, scale: 1.35 }, { opacity: 1, scale: 1, duration: .45, ease: 'back.out(2.2)' }, t0); tl.to(e, { scale: 1.035, duration: .5, yoyo: true, repeat: Math.max(1, 2 * Math.floor((t1 - t0 - .6) / 1) - 1), ease: 'sine.inOut' }, t0 + .5); tl.to(e, { opacity: 0, duration: .2 }, t1 - .2); },
    cur(t, x, y, d = .9) { tl.to('#cur' + i, { left: x, top: y, duration: d, ease: 'power3.inOut' }, t); },
    click(t, x, y) { tl.to('#cur' + i, { scale: .78, duration: .09, yoyo: true, repeat: 1, transformOrigin: '0 0' }, t); tl.set('#rip' + i, { left: x, top: y }, t); tl.fromTo('#rip' + i, { opacity: .95, scale: .2 }, { opacity: 0, scale: 1.7, duration: .55, ease: 'power2.out' }, t); },
    img(k, t) { tl.set(`#im${i}_${k}`, { opacity: 1 }, t); } };
  return api;
}
function stepIntro(i, n, title, dur) {
  const s = $('#s' + i); const d = document.createElement('div'); d.id = 'si' + i; d.style.cssText = 'position:absolute;inset:0;display:flex;align-items:center;justify-content:center;gap:50px;z-index:9';
  d.innerHTML = `<div id="siv${i}" style="position:absolute;inset:0;background:rgba(244,247,255,.94)"></div><div class="num" id="sin${i}" style="position:relative;width:240px;height:240px;background:var(--royal);font-size:150px;box-shadow:0 30px 60px rgba(24,56,255,.35)">${n}</div><div style="position:relative"><div style="font-weight:700;font-size:34px;color:var(--royal);letter-spacing:.14em">ÉTAPE ${n} SUR 3</div><div class="D" id="sit${i}" style="font-size:110px;line-height:1.1">${words(title)}</div></div>`; s.appendChild(d);
  const t = T0[i]; tl.from('#sin' + i, { scale: 0, rotation: -120, duration: .6, ease: 'back.out(1.8)' }, t + .1); rise(`#sit${i} .w>i`, t + .3);
  tl.to(d, { opacity: 0, scale: .5, x: 640, y: -460, duration: .5, ease: 'power3.in' }, t + dur - .5); tl.set(d, { visibility: 'hidden' }, t + dur);
  tl.from(`#s${i} .pill`, { scale: 0, opacity: 0, duration: .45, ease: 'back.out(2.2)', transformOrigin: '100% 50%' }, t + dur - .08);
}
// ---------------------------------------------------------------- 3 · étape 1
{
  const b = browser(3, 'formation-tcfcanada.com/tarification', ['tarifs'], R.t_h); sec(3, pill(1, "Choisir l'offre") + b.html); show(3);
  const c0 = at(3, 'Sur le site'), c1 = at(3, 'Dans la rubrique'), c2 = at(3, 'vous trouvez'), c3 = at(3, 'Le prix'), c4 = at(3, 'Cliquez sur le bouton'), E = T0[4] - .3;
  stepIntro(3, 1, "Choisir l'offre", c0 - T0[3] + .1);
  const mid = r => [r[0] + r[2] / 2, r[1] + r[3] / 2]; const tr = R.t_tarifs, tb = R.t_btn, title = [652, 383, 296, 46], pills = [320, 849, 565, 28];
  tl.set('#cur3', { left: 1250, top: 520 }, 0); b.cur(c0 + .2, ...mid(tr), 1.0); b.hl(tr, c0 + 1.1, c1 - .1, 6); b.click(c0 + 1.3, ...mid(tr));
  b.to(c1, 1.25, 800, 560); b.hl(title, c1 + .7, c2 - .1, 10); b.cur(c1 + .3, 990, 470, .9);
  b.to(c2, 1.38, 800, 722); b.hl(R.t_card, c2 + .9, c3 - .1, 8); b.cur(c2 + .3, 1100, 640, 1.0);
  b.to(c3, 1.6, 800, 850); b.hl(pills, c3 + .9, c3 + 2.6, 8); b.hl(R.t_price, c3 + 2.6, c4 - .1, 8); b.cur(c3 + .4, 610, 900, 1.0);
  b.to(c4, 1.62, 800, 870); b.cur(c4 + .5, ...mid(tb), 1.0); b.hl(tb, c4 + 1.3, E, 7); b.click(c4 + 1.9, ...mid(tb));
  caps(3, [[c0, 'Sur formation-tcfcanada.com, ouvrez la page « Tarifs »'], [c1 + .3, 'Rubrique « Nos nouveautés »'], [c2 + .3, "Examen blanc d'expression orale · avec Emmanuel ou Ahlem"], [c3 + .3, '$20.00 USD la séance : 2 examens blancs · 3 tâches par examen · ≈ 40 min'], [c4 + .3, 'Cliquez sur « Réserver mon examen oral — $20.00 USD »']]);
}
// ---------------------------------------------------------------- 4 · étape 2
{
  const b = browser(4, 'formation-tcfcanada.com/examen-oral/reserver', ['res0', 'res1', 'res2'], 1200); sec(4, pill(2, 'Choisir votre créneau') + b.html); show(4);
  const [c0, c1, c2, c3, c4, c5, c6, c7] = ['choisir votre créneau', "Les heures s'affichent", 'Dans le calendrier', 'Cliquez sur un jour', 'les heures libres', "Choisissez l'heure", 'vérifiez', 'puis cliquez'].map(w => at(4, w)); const E = T0[5] - .3;
  const s0 = at(4, "Les heures s'affichent") - .1; stepIntro(4, 2, 'Choisir votre créneau', s0 - T0[4]);
  const mid = r => [r[0] + r[2] / 2, r[1] + r[3] / 2]; const sl = R.r_slots, S = sl[R.r_si].r; const slAll = [sl[0].r[0], sl[0].r[1], sl[0].r[2], sl[sl.length - 1].r[1] + sl[sl.length - 1].r[3] - sl[0].r[1]];
  b.cam.s = 1.0775; b.cam.cx = 800; b.cam.cy = 500; tl.set('#cur4', { left: 1250, top: 620 }, 0);
  b.to(c1, 1.7, 800, 545); b.hl(R.r_tz, c1 + .8, c2 - .1, 6);
  b.to(c2, 1.8, 660, 776); b.hl(R.r_cal, c2 + .9, c3 - .1, 8); b.cur(c2 + .5, 760, 700, 1.0);
  b.cur(c3 - .5, ...mid(R.r_day), .8); b.click(c3 + .45, ...mid(R.r_day)); b.img(1, c3 + .55); b.hl(R.r_day, c3 + .6, c4 + 1.1, 5);
  b.to(c4 + .5, 1.6, 880, 690); b.hl(slAll, c4 + 1.5, c5 - .1, 9); b.cur(c4 + .9, 1010, 500, .9);
  b.cur(c5 + .2, ...mid(S), .9); b.click(c5 + 1.2, ...mid(S)); b.img(2, c5 + 1.3); b.hl(S, c5 + 1.35, c6 - .1, 5);
  b.to(c6, 1.75, 800, 960); b.hl(R.r_recap, c6 + .9, c7 - .1, 9); b.cur(c6 + .4, 760, 1040, 1.0);
  b.cur(c7 - .1, ...mid(R.r_cont), .7); b.hl(R.r_cont, c7 + .6, E, 6); b.click(c7 + .9, ...mid(R.r_cont));
  caps(4, [[s0 + .1, 'Les heures s\'affichent dans votre fuseau horaire (téléphone ou ordinateur)'], [c2 + .3, 'Chaque jour indique le nombre de créneaux disponibles'], [c3 + .2, 'Cliquez sur le jour qui vous convient'], [c4 + .4, "Les heures libres apparaissent avec le nom de l'examinateur · 40 min par séance"], [c5 + .2, "Choisissez l'heure et l'examinateur qui vous conviennent"], [c6 + .3, 'Vérifiez le récapitulatif : date, heure, examinateur, prix'], [c7 + .1, 'Cliquez sur « Continuer — $20.00 USD »']]);
}
// ---------------------------------------------------------------- grille 2×2
function grid2(i, items, mark) {
  const xs = [ML, ML + 876], ys = [180, 577];
  return items.map((c, k) => `<div class="card g2" id="g${i}_${k}" style="left:${xs[k % 2]}px;top:${ys[k >> 1]}px;width:852px;height:373px;border-color:${c[4]};padding:44px 48px">${mark === 'num' ? num(k + 1, c[4], 100) : chk(c[4], 100)}<div class="D" style="font-size:47px;margin-top:38px">${c[0]}</div><div style="font-size:29px;color:var(--slate);margin-top:10px;line-height:1.42">${c[1]}${c[2] ? '<br>' + c[2] : ''}</div></div>`).join('');
}
function grid2anim(i, items, mark) { items.forEach((c, k) => { const t = at(i, c[3]); pop(`#g${i}_${k}`, t, { y: 90, rotation: k % 2 ? 3 : -3 }); tl.from(`#g${i}_${k} .${mark === 'num' ? 'num' : 'chk'}`, { scale: 0, rotation: -90, duration: .5, ease: 'back.out(2.6)' }, t + .2); if (mark !== 'num') draw(`#g${i}_${k} .ckp`, t + .45);
  tl.to(`#g${i}_${k}`, { boxShadow: '0 0 0 8px rgba(24,56,255,.14),0 24px 48px rgba(20,40,120,.16)', duration: .3, yoyo: true, repeat: 1 }, t + .6); }); }
// ---------------------------------------------------------------- 5 · étape 3
{
  const it = [["Connectez-vous à votre compte", "Il faut être connecté pour finaliser", "votre réservation.", 'Connectez-vous', 'var(--royal)'], ["Réglez en ligne : $20.00 USD", "Paiement sécurisé, directement sur le site.", "", 'puis réglez', 'var(--royal)'], ["Votre créneau vous est réservé", "Retenu pendant le paiement,", "réservé dès que le paiement est validé.", 'Votre créneau', 'var(--green)'], ["Le jour J : rejoignez Zoom", "Connectez-vous à la visioconférence", "à l'heure prévue.", 'Le jour de la séance', 'var(--flag)']];
  sec(5, pill(3, 'Payer et rejoindre la séance') + grid2(5, it, 'num')); show(5); stepIntro(5, 3, 'Le paiement', at(5, 'Connectez-vous') - T0[5]); grid2anim(5, it, 'num');
}
// ---------------------------------------------------------------- 6 · déroulement
{
  const cs = ["D'abord", 'Ensuite', 'Puis un deuxième', 'Et enfin'].map(w => at(6, w)); const E = T0[7];
  const st = [["Examen blanc n° 1", "≈ 12 minutes", '#1838ff'], ["Feedback", "personnalisé", '#16a34a'], ["Examen blanc n° 2", "≈ 12 minutes", '#1838ff'], ["Feedback final", "progrès et axes de travail", '#16a34a']];
  const det = [["Premier examen blanc", ["Simulation complète des 3 tâches", "L'examinateur pose les questions et tient son rôle", "Il chronomètre, sans vous aider"]], ["Feedback personnalisé", ["Vos points forts", "Vos erreurs principales", "Des conseils à appliquer immédiatement"]], ["Deuxième examen blanc", ["Une nouvelle simulation complète", "Avec de nouveaux sujets", "Vous appliquez les conseils reçus"]], ["Feedback final", ["Retour sur cette deuxième performance", "Vos principaux progrès", "Vos axes de travail"]]];
  const lab = ['EXAMEN BLANC N° 1', 'FEEDBACK', 'EXAMEN BLANC N° 2', 'FEEDBACK FINAL']; const [x0, w2] = cx4(0, 2), [x2] = cx4(2, 2);
  sec(6, pill(0, 'Le déroulement · ≈ 40 minutes') + st.map((c, k) => `<div class="card st" id="st${k}" style="left:${cx4(k)[0]}px;top:180px;width:${CW}px;height:140px;border-color:${c[2]};display:flex;align-items:center;gap:20px;padding:0 24px">${num(k + 1, c[2], 70)}<div><div class="D stt" style="font-size:31px">${c[0]}</div><div class="sts" style="font-size:22px;color:var(--slate)">${c[1]}</div></div></div>`).join('') +
    `<div style="position:absolute;left:${ML}px;top:338px;width:1728px;height:8px;border-radius:4px;background:var(--line)"><div id="stp" style="height:8px;border-radius:4px;background:var(--royal);width:0"></div></div>
    <div class="card" id="clc" style="left:${x0}px;top:366px;width:${w2}px;height:584px;overflow:hidden"><canvas id="clv" width="846" height="476" style="display:block"></canvas>
      ${lab.map((l, k) => `<div class="cll" id="cll${k}" style="position:absolute;left:24px;top:24px;height:50px;line-height:50px;border-radius:25px;background:var(--flag);color:#fff;font-weight:700;font-size:24px;padding:0 22px;opacity:0">${l}</div>`).join('')}
      <div class="D" id="clw" style="position:absolute;left:40px;top:496px;font-size:30px">Séance individuelle en visio (Zoom)</div><div style="position:absolute;left:40px;top:538px;font-size:21px;color:var(--slate)">Illustration générée par IA · déroulement d'une séance</div></div>
    <div class="card" id="dtc" style="left:${x2}px;top:366px;width:${w2}px;height:584px"><div id="dt0" style="position:absolute;left:44px;top:60px"><div class="D" style="font-size:50px">Votre séance en 4 temps</div><div style="font-size:30px;color:var(--slate);margin-top:14px">Vous testez, vous écoutez, vous recommencez.</div></div>
      ${det.map((d, k) => `<div class="dt" id="dt${k + 1}" style="position:absolute;left:44px;top:44px;right:40px;visibility:hidden"><div style="display:flex;align-items:center;gap:24px">${num(k + 1, st[k][2], 84)}<div class="D" style="font-size:46px">${d[0]}</div></div>${d[1].map(b => `<div class="dtb" style="display:flex;align-items:center;gap:24px;margin-top:54px">${chk(st[k][2], 56)}<div style="font-weight:600;font-size:32px">${b}</div></div>`).join('')}</div>`).join('')}</div>`);
  show(6); tl.from('#s6 .pill', { x: 300, opacity: 0, duration: .5, ease: 'back.out(1.5)' }, T0[6] + .2); pop('.st', T0[6] + .25, { stagger: .12, y: -60 }); pop('#clc', T0[6] + .5, { x: -80, y: 0 }); pop('#dtc', T0[6] + .6, { x: 80, y: 0 });
  cs.forEach((t, k) => { const end = k < 3 ? cs[k + 1] : E;
    tl.to('#stp', { width: (k + 1) * 25 + '%', duration: .7, ease: 'power2.inOut' }, t);
    tl.to(`#st${k}`, { backgroundColor: st[k][2], scale: 1.03, duration: .3, ease: 'back.out(2)' }, t); tl.to(`#st${k} .stt, #st${k} .sts`, { color: '#fff', duration: .2 }, t); tl.to(`#st${k} .num`, { backgroundColor: '#fff', color: st[k][2], duration: .2 }, t);
    if (k < 3) { tl.to(`#st${k}`, { backgroundColor: '#fff', scale: 1, duration: .3 }, end - .05); tl.to(`#st${k} .stt`, { color: '#141b4d', duration: .2 }, end - .05); tl.to(`#st${k} .sts`, { color: '#5c6a92', duration: .2 }, end - .05); tl.to(`#st${k} .num`, { backgroundColor: st[k][2], color: '#fff', duration: .2 }, end - .05); }
    tl.to(k ? `#dt${k}` : '#dt0', { opacity: 0, x: -40, duration: .22 }, t - .22); tl.set(`#dt${k + 1}`, { visibility: 'visible' }, t); tl.from(`#dt${k + 1}`, { opacity: 0, x: 50, duration: .4, ease: 'power3.out' }, t);
    tl.from(`#dt${k + 1} .dtb`, { opacity: 0, x: 60, duration: .45, ease: 'back.out(1.6)', stagger: .7 }, t + .5); tl.from(`#dt${k + 1} .dtb .chk`, { scale: 0, duration: .4, ease: 'back.out(3)', stagger: .7 }, t + .6);
    if (k) tl.to(`#cll${k - 1}`, { opacity: 0, duration: .15 }, t - .15); tl.fromTo(`#cll${k}`, { opacity: 0, x: -30 }, { opacity: 1, x: 0, duration: .35, ease: 'back.out(2)' }, t);
    tl.set('#clw', { textContent: k % 2 ? 'Avec Emmanuel, examinateur habilité' : 'Avec Ahlem, examinatrice habilitée' }, t); });
  const ctx = $('#clv').getContext('2d'); const base = [0, 0, 150, 140];
  frameFns.push(t => { if (t < T0[6] - .5 || t > E + .1) return; let k = -1; cs.forEach((c, j) => { if (t >= c) k = j; }); const F = (k < 0 || k % 2 === 0) ? window.FA : window.FE; const idx = k < 0 ? 0 : Math.min(F.length - 1, base[k] + Math.floor((t - cs[k]) * 30 * .75)); ctx.drawImage(F[idx], 0, 0, 846, 476); });
}
// ---------------------------------------------------------------- 7 · les 3 tâches
{
  const tk = [["TÂCHE 1", "Entretien dirigé", "≈ 2 min", "Sans préparation", "Se présenter et parler de soi<br>de manière naturelle.", 'Tâche un'], ["TÂCHE 2", "Interaction", "≈ 3 min 30", "≈ 2 min de préparation", "Poser des questions pour obtenir<br>des informations.", 'Tâche deux'], ["TÂCHE 3", "Point de vue", "≈ 4 min 30", "Sans préparation", "Exprimer et défendre une opinion<br>de manière structurée.", 'Tâche trois']];
  sec(7, pill(0, 'Les 3 tâches · format officiel') + tk.map((c, k) => `<div class="card tk" id="tk${k}" style="left:${ML + k * 584}px;top:180px;width:560px;height:770px;border-color:var(--sky);padding:48px 44px"><div class="tke" style="display:inline-block;background:var(--flag);color:#fff;font-weight:700;font-size:28px;height:58px;line-height:58px;border-radius:29px;padding:0 30px">${c[0]}</div><div class="D tke" style="font-size:60px;margin-top:58px">${c[1]}</div><div class="tkl" style="height:4px;background:var(--line);margin-top:26px;transform-origin:0 50%"></div><div class="D tke" style="font-size:84px;color:var(--royal);margin-top:44px;line-height:1;white-space:nowrap">${c[2]}</div><div class="tke" style="display:inline-block;background:var(--tint);color:var(--royal);font-weight:600;font-size:28px;height:60px;line-height:60px;border-radius:30px;padding:0 26px;margin-top:40px">${c[3]}</div><div class="tke" style="font-size:27px;color:var(--slate);margin-top:86px;line-height:1.45;white-space:nowrap">${c[4]}</div></div>`).join(''));
  show(7); tl.from('#s7 .pill', { x: 300, opacity: 0, duration: .5, ease: 'back.out(1.5)' }, T0[7] + .2);
  tk.forEach((c, k) => { const t = at(7, c[5]); pop(`#tk${k}`, t, { y: 140, rotation: (k - 1) * 4, duration: .7 }); tl.from(`#tk${k} .tke`, { opacity: 0, y: 30, duration: .45, ease: 'back.out(1.8)', stagger: .22 }, t + .3); tl.from(`#tk${k} .tkl`, { scaleX: 0, duration: .5 }, t + .5); });
}
// ---------------------------------------------------------------- 8 · feedback
{
  const it = [["Vos points forts", "Ce que vous faites déjà bien", 'var(--green)', 'vos points forts'], ["Vos erreurs principales", "Ce qui vous coûte des points", 'var(--flag)', 'vos erreurs'], ["Des conseils concrets", "À appliquer immédiatement", 'var(--royal)', 'et les conseils']]; const [x0, w2] = cx4(0, 2), [x2] = cx4(2, 2);
  const secs = [['POINTS FORTS', '#16a34a', [560, 640, 500]], ['ERREURS PRINCIPALES', '#e51e20', [520, 600, 660]], ['CONSEILS À APPLIQUER', '#1838ff', [600, 540, 630]]];
  sec(8, pill(0, 'Ce que vous recevez') + it.map((c, k) => `<div class="card" id="fb${k}" style="left:${x0}px;top:${180 + k * 196}px;width:${w2}px;height:172px;border-color:${c[2]};display:flex;align-items:center;gap:30px;padding:0 44px">${chk(c[2], 84)}<div><div class="D" style="font-size:42px">${c[0]}</div><div style="font-size:27px;color:var(--slate)">${c[1]}</div></div></div>`).join('') +
    `<div id="fbk" style="position:absolute;left:${x0}px;top:768px;width:${w2}px;height:182px;border-radius:26px;background:var(--ink);padding:38px 44px;box-shadow:0 24px 48px rgba(20,27,77,.3)"><div class="D" style="font-size:41px;color:#fff;line-height:1.3">${words('Vous savez exactement quoi corriger')}<br><span style="color:var(--yel)">${words('avant le jour J.')}</span></div></div>
    <div class="card" id="fic" style="left:${x2}px;top:180px;width:${w2}px;height:770px;overflow:hidden"><div style="background:var(--royal);height:124px;padding:22px 44px"><div class="D" style="font-size:42px;color:#fff">Fiche de retour</div><div style="font-size:24px;color:#dce6ff">Examen blanc d'expression orale</div></div>
     ${secs.map((s, k) => `<div style="position:absolute;left:44px;top:${156 + k * 186}px"><div style="font-weight:700;font-size:26px;color:${s[1]};letter-spacing:.03em">${s[0]}</div>${s[2].map(w => `<div style="display:flex;align-items:center;gap:20px;margin-top:22px"><u style="width:16px;height:16px;border-radius:50%;background:${s[1]};display:block"></u><div class="fln" style="width:${w}px;height:20px;border-radius:10px;background:#3c466e;filter:blur(5px);transform-origin:0 50%"></div></div>`).join('')}</div>`).join('')}
     <div style="position:absolute;left:44px;top:706px;height:46px;line-height:46px;border-radius:23px;background:#eef3fc;color:var(--slate);font-weight:600;font-size:20px;padding:0 24px">Exemple · contenu flouté</div></div>`);
  show(8); tl.from('#s8 .pill', { x: 300, opacity: 0, duration: .5, ease: 'back.out(1.5)' }, T0[8] + .2);
  pop('#fic', T0[8] + .3, { x: 200, y: 0, rotation: 5, duration: .8 }); tl.from('#fic .fln', { scaleX: 0, duration: .5, ease: 'power2.out', stagger: .28 }, T0[8] + 1.0);
  it.forEach((c, k) => { const t = at(8, c[3]); tl.from(`#fb${k}`, { x: -200, opacity: 0, duration: .6, ease: 'back.out(1.4)' }, t); tl.from(`#fb${k} .chk`, { scale: 0, duration: .45, ease: 'back.out(3)' }, t + .25); draw(`#fb${k} .ckp`, t + .45); });
  pop('#fbk', at(8, 'Vous savez'), { y: 80 }); rise('#fbk .w>i', at(8, 'Vous savez') + .2, { stagger: .07 });
}
// ---------------------------------------------------------------- 9 · checklist
{
  const it = [["Une bonne connexion Internet", "Testez votre réseau avant la séance.", "", 'une bonne connexion', 'var(--green)'], ["Un casque ou des écouteurs", "Pour bien entendre et être bien entendu.", "", 'un casque', 'var(--green)'], ["Une pièce calme", "Sans bruit ni interruption.", "", 'une pièce', 'var(--green)'], ["5 minutes d'avance", "Connectez-vous avant l'heure prévue.", "", 'et connectez-vous', 'var(--green)']];
  sec(9, pill(0, 'Avant votre séance : 4 réflexes') + grid2(9, it, 'chk')); show(9); tl.from('#s9 .pill', { x: 300, opacity: 0, duration: .5, ease: 'back.out(1.5)' }, T0[9] + .2); grid2anim(9, it, 'chk');
}
// ---------------------------------------------------------------- 10 · appel à l'action
{
  const c1 = at(10, 'sur formation'), c2 = at(10, 'Et le jour');
  sec(10, `<div style="position:absolute;left:0;right:0;top:44px;display:flex;justify-content:center"><div id="clg" style="background:#fff;border-radius:40px;padding:12px 36px;box-shadow:0 18px 40px rgba(4,8,40,.35)"><img src="logo.png" style="height:124px;display:block"></div></div>
   <div class="hk D" id="ct1" style="top:262px;font-size:94px">${words('Réservez votre examen blanc')}</div><div class="hk D" id="ct2" style="top:372px;font-size:94px;color:var(--yel)">${words("d'expression orale")}</div>
   <div style="position:absolute;left:0;right:0;top:536px;display:flex;justify-content:center"><div id="curl" style="position:relative;overflow:hidden;background:#fff;color:var(--royal);font-weight:700;font-size:58px;height:128px;line-height:128px;border-radius:64px;padding:0 64px;box-shadow:0 22px 50px rgba(4,8,40,.4)">formation-tcfcanada.com<i id="shine" style="position:absolute;top:0;left:-30%;width:22%;height:100%;background:linear-gradient(90deg,transparent,rgba(24,56,255,.22),transparent);transform:skewX(-20deg)"></i></div></div>
   <div id="ct3" style="position:absolute;left:0;right:0;top:708px;text-align:center;font-weight:600;font-size:33px;color:#d7e2ff">$20.00 USD · 2 examens blancs · feedback personnalisé · ≈ 40 min en visio</div>
   <div style="position:absolute;left:0;right:0;top:782px;display:flex;justify-content:center"><div id="ct4" style="background:var(--green);color:#fff;font-weight:700;font-size:33px;height:70px;line-height:70px;border-radius:35px;padding:0 38px">WhatsApp officiel : +1 506 253 60 67</div></div>
   <div class="hk D" id="ct5" style="top:896px;font-size:50px;color:var(--yel);font-weight:800">${words("Le jour J, vous aurez déjà vécu l'examen.")}</div>
   <div id="ct6" style="position:absolute;left:0;right:0;top:1016px;text-align:center;font-size:21px;color:#bfccf5">Simulation d'entraînement proposée par la plateforme : ce n'est pas une épreuve officielle.</div>`);
  show(10, true); const t = T0[10];
  pop('#clg', t + .1, { y: -120, ease: 'back.out(1.6)' }); rise('#ct1 .w>i', t + .15); rise('#ct2 .w>i', t + .55);
  pop('#curl', c1, { scale: .4, y: 0, ease: 'back.out(2)' }); tl.to('#shine', { left: '120%', duration: .9, ease: 'power2.inOut' }, c1 + .5); tl.to('#curl', { scale: 1.04, duration: .6, yoyo: true, repeat: 9, ease: 'sine.inOut' }, c1 + .7);
  tl.from('#ct3', { opacity: 0, y: 24, duration: .45 }, c1 + .5); pop('#ct4', c1 + .8, { y: 30 }); rise('#ct5 .w>i', c2, { stagger: .06 }); tl.from('#ct6', { opacity: 0, duration: .5 }, c1 + 1.2);
}
// ---------------------------------------------------------------- global
tl.set('#hdr', { opacity: 0 }, 0); tl.fromTo('#hdr', { opacity: 0, x: -80 }, { opacity: 1, x: 0, duration: .5, ease: 'power3.out' }, T0[1] + .3); tl.to('#hdr', { opacity: 0, duration: .2 }, T0[10] - .12);
function sweep(t, cb) { ['#sw1', '#sw2'].forEach((s, k) => tl.fromTo(s, { left: '-150%' }, { left: '110%', duration: .85, ease: 'power2.inOut' }, t - .42 + k * .07)); cb(t + .03); }
sweep(T0[1], t => tl.set('#bgN', { opacity: 0 }, t)); sweep(T0[10], t => tl.set('#bgN', { opacity: 1 }, t));
const fade = document.createElement('div'); fade.style.cssText = 'position:absolute;inset:0;background:#0a1460;opacity:0'; $('#stage').appendChild(fade); tl.to(fade, { opacity: 1, duration: .5 }, TOTAL - .5);
tl.set({}, {}, TOTAL);
const hctx = $('#hookc').getContext('2d');
window.seek = t => { tl.time(t, false);
  if (t < 3.3) hctx.drawImage(window.FA[Math.min(window.FA.length - 1, Math.floor(t * 30))], 0, 0, 1920, 1080);
  frameFns.forEach(f => f(t));
  const k = t / 9; $('#b1').style.transform = `translate(${Math.sin(k) * 90}px,${Math.cos(k * .8) * 60}px)`; $('#b2').style.transform = `translate(${Math.cos(k * .7) * 110}px,${Math.sin(k * .9) * 70}px)`; $('#b3').style.transform = `translate(${Math.sin(k * 1.3) * 140}px,${Math.cos(k) * 50}px)`;
  const pg = $('#prog'); pg.style.width = (1920 * t / TOTAL) + 'px'; pg.style.background = (t < T0[1] || t >= T0[10]) ? '#ffd640' : '#1838ff'; };
const load = (dir, n) => Promise.all(Array.from({ length: n }, (_, i) => new Promise(r => { const im = new Image(); im.onload = () => r(im); im.onerror = () => r(im); im.src = `${dir}/${String(i + 1).padStart(3, '0')}.jpg`; })));
Promise.all([load('fa', 301), load('fe', 301), document.fonts.ready, ...[...document.images].map(im => im.decode().catch(() => 0))]).then(([a, e]) => { window.FA = a; window.FE = e; window.seek(0); window.READY = true; });
