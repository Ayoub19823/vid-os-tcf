const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ proxy: { server: process.env.HTTPS_PROXY } });
  const p = await b.newPage({ viewport: { width: 1600, height: 900 }, ignoreHTTPSErrors: true });
  await p.goto('https://www.formation-tcfcanada.com/epreuve/expression-orale/sujets-actualites/octobre-2026', { waitUntil: 'networkidle', timeout: 60000 });
  await p.waitForTimeout(1500); await p.keyboard.press('Escape');
  await p.getByRole('button',{name:'Tout refuser'}).click().catch(()=>{});
  const parts = await p.evaluate(()=>[...document.querySelectorAll('button')].map(b=>b.textContent.trim()).filter(t=>/^Partie \d+/.test(t)));
  console.log('PARTS', parts.join(' | '));
  for (const PT of ['15','14']) {
    const H = p.getByText('Partie '+PT,{exact:true}).last();
    if (!(await H.count())) { console.log('no partie', PT); continue; }
    await H.scrollIntoViewIfNeeded(); await H.click(); await p.waitForTimeout(1500);
    const t2 = p.getByText('Tâche 2',{exact:true}).first().locator('xpath=ancestor::button[1]');
    await t2.click(); await p.waitForTimeout(1500);
    const info = await p.evaluate(()=>{
      const out=[];
      const btns=[...document.querySelectorAll('button,a')].filter(e=>e.textContent.includes('Commencer la simulation') && e.getBoundingClientRect().height>0);
      for (const b of btns){ let e=b; while(e && !(e.getBoundingClientRect().height>200)) e=e.parentElement;
        const txt=(e.querySelector('p')||e).textContent.trim().slice(0,70);
        const yt=[...e.querySelectorAll('a,button,[class*=youtube],[aria-label],svg')].filter(x=>/youtu/i.test(x.outerHTML)).map(x=>(x.getAttribute('href')||x.getAttribute('aria-label')||x.getAttribute('title')||x.tagName)).slice(0,3);
        out.push(txt+' => '+JSON.stringify(yt));}
      return out; });
    console.log('P'+PT, info.join('\n'));
    await p.screenshot({path:'/tmp/claude-0/-home-claude/7a22c9af-0a80-57d2-89a2-1a32e1824476/scratchpad/yt_'+PT+'.png'});
    await H.click(); await p.waitForTimeout(800);
  }
  await b.close();
})();
