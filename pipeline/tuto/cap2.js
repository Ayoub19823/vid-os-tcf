const { chromium } = require('playwright'); const fs = require('fs');
const b64 = f => 'data:image/jpeg;base64,' + fs.readFileSync(f).toString('base64');
(async () => {
  const br = await chromium.launch(); const ctx = await br.newContext({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: 2, locale: 'fr-CA', timezoneId: 'America/Toronto' });
  const p = await ctx.newPage(); const R = JSON.parse(fs.readFileSync('cap/R.json')); const FA = b64('fa.jpg'), FE = b64('fe.jpg');
  await p.goto('https://www.formation-tcfcanada.com/tarification', { waitUntil: 'networkidle' }); await p.waitForTimeout(1500);
  await p.keyboard.press('Escape'); await p.waitForTimeout(600);
  const stillModal = await p.locator('text=devient illimitée').count();
  if (stillModal) { try { await p.locator('text=devient illimitée').locator('xpath=ancestor::div[3]').locator('button').first().click({ timeout: 3000 }); } catch (e) { console.log('modal', e.message.slice(0, 80)); } }
  await p.waitForTimeout(500);
  try { await p.getByRole('button', { name: 'Tout refuser' }).click({ timeout: 4000 }); } catch (e) { console.log('cookies', e.message.slice(0, 60)); } await p.waitForTimeout(600);
  console.log('modal left', await p.locator('text=devient illimitée').count(), 'cookies left', await p.locator('text=Nous utilisons des cookies').count());
  await p.evaluate(([FA, FE]) => { for (const el of document.querySelectorAll('div,span')) { const t = (el.textContent || '').trim(); if ((t !== 'E' && t !== 'A') || el.children.length) continue; const r = el.getBoundingClientRect(); if (r.width < 20 || Math.abs(r.width - r.height) > 3) continue; el.style.backgroundImage = `url(${t === 'A' ? FA : FE})`; el.style.backgroundSize = 'cover'; el.style.color = 'transparent'; } }, [FA, FE]);
  const rc = async (loc) => { const b = await loc.boundingBox(); const sy = await p.evaluate(() => scrollY); return [b.x, b.y + sy, b.width, b.height].map(v => Math.round(v * 10) / 10); };
  const btn = p.locator('a,button').filter({ hasText: 'Réserver mon examen oral' }).first();
  R.t_btn = await rc(btn); R.t_tarifs = await rc(p.locator('a').filter({ hasText: /^\s*TARIFS\s*$/i }).first());
  R.t_title = await rc(p.locator('text=/^\\s*NOS\\s*$/').first().locator('xpath=ancestor-or-self::*[self::h1 or self::h2 or self::h3][1]').first()).catch(async () => rc(p.getByText(/NOUVEAUT/).first()));
  const h = await btn.evaluateHandle(el => { let e = el; while (e && (e.getBoundingClientRect().height < 300)) e = e.parentElement; return e; });
  const cb = await h.asElement().boundingBox(); const sy = await p.evaluate(() => scrollY); R.t_card = [cb.x, cb.y + sy, cb.width, cb.height];
  R.t_price = await rc(p.getByText('séance individuelle').first().locator('xpath=..'));
  R.t_pills = await rc(p.getByText('2 examens blancs', { exact: true }).first().locator('xpath=../..'));
  R.t_exam = await rc(p.getByText('VOS EXAMINATEURS').first().locator('xpath=..'));
  const H1 = Math.ceil(R.t_card[1] + R.t_card[3] + 220); await p.setViewportSize({ width: 1600, height: H1 }); await p.evaluate(() => scrollTo(0, 0)); await p.waitForTimeout(600);
  await p.screenshot({ path: 'cap/tarifs.png', clip: { x: 0, y: 0, width: 1600, height: H1 } }); R.t_h = H1;
  fs.writeFileSync('cap/R.json', JSON.stringify(R, null, 1)); for (const k of Object.keys(R).filter(k => k.startsWith('t_'))) console.log(k, JSON.stringify(R[k])); await br.close();
})().catch(e => { console.error('ERR', e.message); process.exit(1); });
