const { chromium } = require('playwright');
const fs = require('fs');
const ease = t => t<.5 ? 4*t*t*t : 1-Math.pow(-2*t+2,3)/2;
(async () => {
  const b = await chromium.launch({ proxy: { server: process.env.HTTPS_PROXY } });
  const p = await b.newPage({ viewport: { width: 1600, height: 900 }, deviceScaleFactor: 2, ignoreHTTPSErrors: true });
  const box = async (l) => { const r = await l.boundingBox(); return r && [r.x, r.y, r.x+r.width, r.y+r.height]; };
  await p.goto('https://www.formation-tcfcanada.com/epreuve/expression-orale/sujets-actualites/'+(process.env.MSLUG||'novembre-2026'), { waitUntil: 'networkidle', timeout: 60000 });
  await p.waitForTimeout(1500); await p.keyboard.press('Escape');
  await p.getByRole('button',{name:'Tout refuser'}).click().catch(()=>{});
  await p.addStyleTag({content:'html{scroll-behavior:auto!important}'});
  const PT = process.env.PARTIE || '14'; const OUT = process.env.CAPDIR || 'cap'; const H = p.getByText('Partie '+PT,{exact:true}).last();
  await H.scrollIntoViewIfNeeded(); await H.click(); await p.waitForTimeout(1500);
  const t2 = p.getByText('Tâche '+(process.env.TACHE||'3'),{exact:true}).first().locator('xpath=ancestor::button[1]');
  await t2.click(); await p.waitForTimeout(1500);
  const btns = p.getByText('Commencer la simulation').filter({visible:true});
  console.log('nbtns', await btns.count());
  
  const P0 = await H.evaluate(e=>e.closest('button').getBoundingClientRect().top+window.scrollY); for (const k of (process.env.KS||'1,2,3,4,5').split(',').map(Number)) {
    const dir = `${OUT}/s${k}`; fs.mkdirSync(dir,{recursive:true});
    const y0 = JSON.parse(fs.readFileSync(`${OUT}/J.json`)).Y2[0]; await p.evaluate(y=>window.scrollTo(0,y), y0); await p.mouse.move(1590,890); await p.waitForTimeout(400);
    const btn = btns.nth(k-1);
    const bb = await btn.boundingBox(); const Y2 = Math.round(y0 + bb.y - 640);
    const M=40; for (let i=0;i<=M;i++){ await p.evaluate(y=>window.scrollTo(0,y), Math.round(y0+ease(i/M)*(Y2-y0))); await p.waitForTimeout(30); await p.screenshot({path:`${dir}/D${String(i).padStart(3,'0')}.png`}); }
    const J = {Y2:[y0,Y2]};
    J.btn = await box(btn);
    const card = btn.locator('xpath=ancestor::*[.//p][1]');
    J.card = await btn.evaluate(b=>{ const n=x=>[...x.querySelectorAll('button,a')].filter(y=>y.textContent.includes('Commencer la simulation')).length; let e=b; while(e.parentElement && n(e.parentElement)==1) e=e.parentElement; const r=e.getBoundingClientRect(); return [r.left,r.top,r.right,r.bottom]; });
    J.text = await btn.evaluate(b=>{ const n=x=>[...x.querySelectorAll('button,a')].filter(y=>y.textContent.includes('Commencer la simulation')).length; let e=b; while(e.parentElement && n(e.parentElement)==1) e=e.parentElement; const q=[...e.querySelectorAll('p,div,span')].find(x=>x.children.length==0 && x.textContent.trim().length>40 && /[?.»)]\s*$/.test(x.textContent.trim())) || e.querySelector('p'); const r=q.getBoundingClientRect(); return {t:q.textContent, r:[r.left,r.top,r.right,r.bottom]}; });
    J.cor = await btn.evaluate(b=>{ const n=x=>[...x.querySelectorAll('button,a')].filter(y=>y.textContent.includes('Commencer la simulation')).length; let e=b; while(e.parentElement && n(e.parentElement)==1) e=e.parentElement; const c=[...e.querySelectorAll('button,a')].find(x=>x.textContent.includes('Voir la correction')); const r=c.getBoundingClientRect(); return [r.left,r.top,r.right,r.bottom]; });
    await p.screenshot({path:`${dir}/E0.png`});
    await p.mouse.move((J.btn[0]+J.btn[2])/2,(J.btn[1]+J.btn[3])/2); await p.waitForTimeout(300); await p.screenshot({path:`${dir}/E1.png`});
    await p.mouse.move((J.cor[0]+J.cor[2])/2,(J.cor[1]+J.cor[3])/2); await p.waitForTimeout(300); await p.screenshot({path:`${dir}/E2.png`});
    fs.writeFileSync(`${dir}/J.json`, JSON.stringify(J,null,1));
    console.log(k, JSON.stringify(J.text.t), J.card.map(Math.round));
  }
  await b.close();
})();
