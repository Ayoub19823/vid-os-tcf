const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ proxy: { server: process.env.HTTPS_PROXY } });
  const p = await b.newPage({ viewport: { width: 1600, height: 900 }, deviceScaleFactor: 1, ignoreHTTPSErrors: true });
  await p.goto('https://www.formation-tcfcanada.com/epreuve/expression-orale/sujets-actualites/octobre-2026', { waitUntil: 'networkidle', timeout: 60000 });
  await p.waitForTimeout(1500); await p.keyboard.press('Escape');
  await p.getByRole('button',{name:'Tout refuser'}).click().catch(()=>{});
  const all = p.getByText('Partie 14', {exact:true});
  console.log('n', await all.count());
  for (let i=0;i<await all.count();i++){ const e=all.nth(i); console.log(i, await e.evaluate(e=>e.tagName+' '+e.parentElement.tagName+' '+e.closest('button')?.className?.slice(0,60))); }
  const h = all.last(); await h.scrollIntoViewIfNeeded(); await h.click(); await p.waitForTimeout(1500);
  console.log('tabs', await p.getByText('Tâche 2',{exact:true}).count(), await p.locator('text=Interaction orale').count());
  await p.screenshot({path:'cap/dbg.png'});
  await b.close();
})();
