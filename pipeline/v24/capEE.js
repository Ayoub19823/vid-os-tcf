// Capture de la navigation « expression écrite » : MSLUG (ex. novembre-2026), COMBI (n° de combinaison), TACHE (1|2|3), CAPDIR
const { chromium } = require('playwright');
const fs = require('fs');
const ease = t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
(async () => {
  const b = await chromium.launch({ proxy: process.env.HTTPS_PROXY ? { server: process.env.HTTPS_PROXY } : undefined });
  const p = await b.newPage({ viewport: { width: 1600, height: 900 }, deviceScaleFactor: 2, ignoreHTTPSErrors: true });
  const CB = process.env.COMBI || '1', TK = +(process.env.TACHE || '1'), OUT = process.env.CAPDIR || 'capEE';
  fs.mkdirSync(OUT, { recursive: true }); fs.mkdirSync(OUT + '/s' + TK, { recursive: true }); const J = {};
  const box = async l => { const r = await l.boundingBox(); return r && [r.x, r.y, r.x + r.width, r.y + r.height]; };
  const shot = n => p.screenshot({ path: `${OUT}/${n}.png` });
  await p.goto('https://www.formation-tcfcanada.com/epreuve/expression-ecrite/sujets-actualites/' + (process.env.MSLUG || 'novembre-2026'), { waitUntil: 'networkidle', timeout: 60000 });
  await p.waitForTimeout(1500); await p.keyboard.press('Escape');
  await p.getByRole('button', { name: 'Tout refuser' }).click().catch(() => {});
  await p.addStyleTag({ content: 'html{scroll-behavior:auto!important}' });
  await p.evaluate(() => window.scrollTo(0, 0)); await p.mouse.move(1590, 890); await p.waitForTimeout(600);
  // pastille de la combinaison (barre de sélection en haut)
  const chip = p.locator('button').filter({ hasText: new RegExp('^\\s*Combinaison ' + CB + '\\s*3 tâches') }).first();
  J.chip = await box(chip); await shot('A0');
  await p.mouse.move((J.chip[0] + J.chip[2]) / 2, (J.chip[1] + J.chip[3]) / 2); await p.waitForTimeout(300); await shot('A1');
  // en-tête de la combinaison dans la liste
  const H = p.getByText('Combinaison ' + CB, { exact: true }).filter({ visible: true }).last();
  const target = await H.evaluate(e => (e.closest('button') || e).getBoundingClientRect().top + window.scrollY);
  const maxY = await p.evaluate(() => document.documentElement.scrollHeight - window.innerHeight);
  J.Y1 = Math.round(Math.min(target - 300, maxY));
  await p.mouse.move(1590, 890);
  const N = 48; for (let i = 0; i <= N; i++) { await p.evaluate(y => window.scrollTo(0, y), Math.round(ease(i / N) * J.Y1)); await p.waitForTimeout(30); await shot('B' + String(i).padStart(3, '0')); }
  J.hdr = await H.evaluate(e => { const r = (e.closest('button') || e).getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom]; });
  await p.mouse.move((J.hdr[0] + J.hdr[2]) / 2, (J.hdr[1] + J.hdr[3]) / 2); await p.waitForTimeout(300); await shot('C0');
  await H.click(); await p.waitForTimeout(2600); await shot('C1');
  // carte de la tâche
  const cor = p.getByText('Voir la correction').filter({ visible: true }).nth(TK - 1);
  const y0 = await p.evaluate(() => window.scrollY);
  J.t2 = await cor.evaluate(b => { const n = x => [...x.querySelectorAll('button,a')].filter(y => y.textContent.includes('Voir la correction')).length; let e = b; while (e.parentElement && n(e.parentElement) == 1) e = e.parentElement; const t = [...e.querySelectorAll('*')].find(x => x.children.length == 0 && /^Tâche \d$/.test(x.textContent.trim())); const r = (t || e).getBoundingClientRect(); return [r.left - 50, r.top - 6, r.right + 140, r.bottom + 26]; });
  await p.mouse.move((J.t2[0] + J.t2[2]) / 2, (J.t2[1] + J.t2[3]) / 2); await p.waitForTimeout(300); await shot('C2'); await shot('C3');
  const bb = await cor.boundingBox(); const Y2 = Math.round(y0 + bb.y - 640); J.Y2 = [y0, Y2];
  await p.mouse.move(1590, 890);
  const M = 36; for (let i = 0; i <= M; i++) { await p.evaluate(y => window.scrollTo(0, y), Math.round(y0 + ease(i / M) * (Y2 - y0))); await p.waitForTimeout(30); await p.screenshot({ path: `${OUT}/s${TK}/D${String(i).padStart(3, '0')}.png` }); }
  const S = {};
  S.btn = await box(cor); S.cor = S.btn;
  S.card = await cor.evaluate(b => { const n = x => [...x.querySelectorAll('button,a')].filter(y => y.textContent.includes('Voir la correction')).length; let e = b; while (e.parentElement && n(e.parentElement) == 1) e = e.parentElement; const r = e.getBoundingClientRect(); return [r.left, r.top, r.right, r.bottom]; });
  S.text = await cor.evaluate(b => { const n = x => [...x.querySelectorAll('button,a')].filter(y => y.textContent.includes('Voir la correction')).length; let e = b; while (e.parentElement && n(e.parentElement) == 1) e = e.parentElement; const q = [...e.querySelectorAll('p,div,span')].filter(x => x.children.length == 0 && x.textContent.trim().length > 40).sort((a, c) => c.textContent.length - a.textContent.length)[0]; const r = q.getBoundingClientRect(); return { t: q.textContent.trim(), r: [r.left, r.top, r.right, r.bottom] }; });
  S.Y2 = J.Y2;
  await p.screenshot({ path: `${OUT}/s${TK}/E0.png` });
  await p.mouse.move((S.btn[0] + S.btn[2]) / 2, (S.btn[1] + S.btn[3]) / 2); await p.waitForTimeout(300);
  await p.screenshot({ path: `${OUT}/s${TK}/E1.png` }); await p.screenshot({ path: `${OUT}/s${TK}/E2.png` });
  fs.writeFileSync(`${OUT}/J.json`, JSON.stringify({ ...J, ...S }, null, 1));
  fs.writeFileSync(`${OUT}/s${TK}/J.json`, JSON.stringify(S, null, 1));
  console.log(JSON.stringify(S.text.t).slice(0, 200), S.card.map(Math.round));
  await b.close();
})();
