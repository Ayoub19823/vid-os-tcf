// Liste les sujets d'expression orale (Tâche 2 et 3) d'un ou plusieurs mois et indique s'ils ont déjà une vidéo.
// usage : MOIS="novembre-2026,octobre-2026" node pick.js > sujets.json
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ proxy: process.env.HTTPS_PROXY ? { server: process.env.HTTPS_PROXY } : undefined });
  const p = await b.newPage({ viewport: { width: 1600, height: 900 }, ignoreHTTPSErrors: true });
  const out = [];
  for (const m of (process.env.MOIS || 'novembre-2026').split(',')) {
    await p.goto('https://www.formation-tcfcanada.com/epreuve/expression-orale/sujets-actualites/' + m, { waitUntil: 'networkidle', timeout: 60000 });
    await p.waitForTimeout(1500); await p.keyboard.press('Escape');
    await p.getByRole('button', { name: 'Tout refuser' }).click().catch(() => {});
    const parts = await p.evaluate(() => [...new Set([...document.querySelectorAll('button *')].filter(e => e.children.length == 0).map(e => (e.textContent.trim().match(/^Partie (\d+)$/) || [])[1]).filter(Boolean))].map(Number).sort((a, b) => a - b));
    for (const pt of parts) {
      const H = p.getByText('Partie ' + pt, { exact: true }).last();
      await H.scrollIntoViewIfNeeded(); await H.click(); await p.waitForTimeout(1200);
      for (const t of [2, 3]) {
        const tab = p.getByText('Tâche ' + t, { exact: true }).first().locator('xpath=ancestor::button[1]');
        if (!(await tab.count())) continue;
        await tab.click(); await p.waitForTimeout(1000);
        const cards = await p.evaluate(() => {
          const n = x => [...x.querySelectorAll('button,a')].filter(y => y.textContent.includes('Commencer la simulation')).length;
          return [...document.querySelectorAll('button,a')].filter(e => e.textContent.includes('Commencer la simulation') && e.getBoundingClientRect().height > 0)
            .map(b => { let e = b; while (e.parentElement && n(e.parentElement) == 1) e = e.parentElement;
              const q = [...e.querySelectorAll('p,div,span')].find(x => x.children.length == 0 && x.textContent.trim().length > 40);
              return { texte: (q ? q.textContent : e.innerText).trim(), video: e.innerText.includes('Voir la simulation') }; });
        });
        cards.forEach((c, i) => out.push({ mois: m, partie: pt, tache: t, sujet: i + 1, ...c }));
      }
      await H.click().catch(() => {}); await p.waitForTimeout(500);   // referme la partie
    }
  }
  console.log(JSON.stringify(out, null, 1));
  await b.close();
})();
