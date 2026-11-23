const { chromium } = require('playwright'); const fs = require('fs');
const b64 = f => 'data:image/jpeg;base64,' + fs.readFileSync(f).toString('base64');
(async () => {
  const br = await chromium.launch(); const ctx = await br.newContext({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: 2, locale: 'fr-CA', timezoneId: 'America/Toronto' });
  const p = await ctx.newPage(); const R = {}; const FA = b64('fa.jpg'), FE = b64('fe.jpg');
  const cookies = async () => { try { await p.getByRole('button', { name: 'Tout refuser' }).click({ timeout: 4000 }); } catch (e) {} await p.waitForTimeout(500); };
  const faces = async () => p.evaluate(([FA, FE]) => {
    let n = 0;
    for (const el of document.querySelectorAll('div,span')) {
      const t = (el.textContent || '').trim(); if (t !== 'E' && t !== 'A') continue; if (el.children.length) continue;
      const r = el.getBoundingClientRect(); if (r.width < 20 || Math.abs(r.width - r.height) > 3) continue;
      el.style.backgroundImage = `url(${t === 'A' ? FA : FE})`; el.style.backgroundSize = 'cover'; el.style.color = 'transparent'; el.style.border = '2px solid rgba(255,255,255,.9)'; n++;
    } return n; }, [FA, FE]);
  const rect = async (loc) => { const b = await loc.boundingBox(); const s = await p.evaluate(() => [scrollX, scrollY]); return [b.x + s[0], b.y + s[1], b.width, b.height].map(v => Math.round(v * 10) / 10); };
  const shot = async (name, h) => { await p.evaluate(() => scrollTo(0, 0)); await p.waitForTimeout(300); await p.screenshot({ path: `cap/${name}.png`, clip: { x: 0, y: 0, width: 1600, height: h } }); };
  // ---- Tarifs
  await p.goto('https://www.formation-tcfcanada.com/tarification', { waitUntil: 'networkidle' }); await cookies(); console.log('faces', await faces());
  const btn = p.locator('a,button').filter({ hasText: 'Réserver mon examen oral' }).first();
  R.t_btn = await rect(btn); R.t_tarifs = await rect(p.locator('a').filter({ hasText: /^\s*TARIFS\s*$/i }).first());
  R.t_title = await rect(p.locator('h1,h2,h3').filter({ hasText: /NOUVEAUT/i }).first());
  const cardEl = (await btn.evaluateHandle(el => { let e = el; while (e && e.getBoundingClientRect().width < 900) e = e.parentElement; return e; })).asElement(); { const b = await cardEl.boundingBox(); R.t_card = [b.x, b.y + await p.evaluate(() => scrollY), b.width, b.height]; }
  R.t_price = await rect(p.locator('text=/séance individuelle/').first().locator('xpath=..'));
  R.t_pills = await rect(p.locator('text=2 examens blancs').first().locator('xpath=../..'));
  const H1 = Math.ceil(R.t_card[1] + R.t_card[3] + 260); await p.setViewportSize({ width: 1600, height: H1 }); await shot('tarifs', H1); R.t_h = H1;
  // ---- Réserver
  await p.setViewportSize({ width: 1600, height: 1000 });
  await p.goto('https://www.formation-tcfcanada.com/examen-oral/reserver', { waitUntil: 'networkidle' }); await cookies(); await p.waitForTimeout(800);
  R.r_tz = await rect(p.locator('text=/Heures affichées/').first().locator('xpath=ancestor::div[3]'));
  const days = p.locator('button').filter({ hasText: /dispo/ }); const nd = await days.count(); let u = null;
  for (let i = 0; i < nd; i++) { const b = await rect(days.nth(i)); u = u ? [Math.min(u[0], b[0]), Math.min(u[1], b[1]), Math.max(u[2], b[0] + b[2]), Math.max(u[3], b[1] + b[3])] : [b[0], b[1], b[0] + b[2], b[1] + b[3]]; }
  R.r_cal = [u[0], u[1], u[2] - u[0], u[3] - u[1]];
  let di = -1; for (let i = 2; i < nd; i++) { const t = await days.nth(i).innerText(); const m = t.match(/(\d+)\s*dispo/); if (m && +m[1] >= 6) { di = i; break; } } if (di < 0) di = Math.min(3, nd - 1);
  R.r_day = await rect(days.nth(di)); R.r_dayText = (await days.nth(di).innerText()).replace(/\s+/g, ' ');
  const pageH = async () => p.evaluate(() => document.documentElement.scrollHeight);
  let H2 = Math.min(1500, await pageH()); await p.setViewportSize({ width: 1600, height: H2 }); await shot('res0', H2);
  await days.nth(di).click(); await p.waitForTimeout(900); console.log('faces', await faces());
  const slots = p.locator('button').filter({ hasText: /\d\d\s*h\s*\d\d/ }); const ns = await slots.count(); R.r_slots = [];
  for (let i = 0; i < ns; i++) R.r_slots.push({ t: (await slots.nth(i).innerText()).replace(/\s+/g, ' '), r: await rect(slots.nth(i)) });
  R.r_slotHead = await rect(slots.first().locator('xpath=../..'));
  await shot('res1', H2);
  const si = Math.min(2, ns - 1); await slots.nth(si).click(); await p.waitForTimeout(900); console.log('faces', await faces()); R.r_si = si;
  const cont = p.locator('a,button').filter({ hasText: /^\s*Continuer/ }).first(); R.r_cont = await rect(cont);
  R.r_recap = await rect(p.locator('text=/VOTRE CRÉNEAU/i').first().locator('xpath=..')); R.r_recapCard = await rect(cont.locator('xpath=ancestor::div[2]'));
  R.r_recapText = (await p.locator('text=/VOTRE CRÉNEAU/i').first().locator('xpath=..').innerText()).replace(/\s+/g, ' ');
  H2 = Math.min(1600, await pageH()); await p.setViewportSize({ width: 1600, height: H2 }); await p.waitForTimeout(400); await shot('res2', H2); R.r_h = H2;
  // après « Continuer » : où arrive-t-on ?
  await p.setViewportSize({ width: 1600, height: 1000 }); await cont.click(); await p.waitForTimeout(3500); R.after_url = p.url(); await p.screenshot({ path: 'cap/after.png' });
  R.after_text = (await p.locator('body').innerText()).replace(/\s+/g, ' ').slice(0, 900);
  fs.writeFileSync('cap/R.json', JSON.stringify(R, null, 1)); console.log(JSON.stringify(R)); await br.close();
})().catch(e => { console.error('ERR', e.message); process.exit(1); });
