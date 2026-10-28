const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ proxy: { server: process.env.HTTPS_PROXY } });
  const p = await b.newPage({ viewport: { width: 1600, height: 900 }, ignoreHTTPSErrors: true });
  await p.goto('https://www.formation-tcfcanada.com/epreuve/expression-orale/sujets-actualites/octobre-2026', { waitUntil: 'networkidle', timeout: 60000 });
  await p.waitForTimeout(1500); await p.keyboard.press('Escape');
  await p.getByRole('button',{name:'Tout refuser'}).click().catch(()=>{});
  for (const PT of ['13','12','11','10']) {
    const H = p.getByText('Partie '+PT,{exact:true}).last();
    await H.scrollIntoViewIfNeeded(); await H.click(); await p.waitForTimeout(1500);
    await p.getByText('Tâche 2',{exact:true}).first().locator('xpath=ancestor::button[1]').click(); await p.waitForTimeout(1500);
    const n = await p.getByText(/Avec simulation/).filter({visible:true}).first().textContent().catch(()=>'?');
    const v = await p.getByText('Voir la simulation').filter({visible:true}).count();
    console.log('P'+PT, n.trim(), 'boutons:', v);
    await H.click(); await p.waitForTimeout(800);
  }
  await b.close();
})();
