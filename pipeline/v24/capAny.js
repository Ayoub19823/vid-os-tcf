const { chromium } = require('playwright');
const fs = require('fs');
const ease = t => t<.5 ? 4*t*t*t : 1-Math.pow(-2*t+2,3)/2;
(async () => {
  const b = await chromium.launch({ proxy: { server: process.env.HTTPS_PROXY } });
  const p = await b.newPage({ viewport: { width: 1600, height: 900 }, deviceScaleFactor: 2, ignoreHTTPSErrors: true });
  const PT = process.env.PARTIE || '14'; const OUT = process.env.CAPDIR || 'cap'; fs.mkdirSync(OUT,{recursive:true}); const J = {};
  const box = async (l) => { const r = await l.boundingBox(); return r && [r.x, r.y, r.x+r.width, r.y+r.height]; };
  const shot = async (n) => p.screenshot({ path: `${OUT}/${n}.png` });
  await p.goto('https://www.formation-tcfcanada.com/epreuve/expression-orale/sujets-actualites/'+(process.env.MSLUG||'novembre-2026'), { waitUntil: 'networkidle', timeout: 60000 });
  await p.waitForTimeout(1500); await p.keyboard.press('Escape');
  await p.getByRole('button',{name:'Tout refuser'}).click().catch(()=>{});
  await p.addStyleTag({content:'html{scroll-behavior:auto!important}'});
  await p.mouse.move(1590,890);
  const chip = p.getByRole('button',{name:new RegExp('^Partie '+PT+'\\b')}).first();
  await chip.scrollIntoViewIfNeeded(); await p.evaluate(()=>window.scrollTo(0,0)); await p.waitForTimeout(600);
  J.chip = await box(chip); await shot('A0');
  await p.mouse.move((J.chip[0]+J.chip[2])/2,(J.chip[1]+J.chip[3])/2); await p.waitForTimeout(300); await shot('A1');
  // find Partie 14 header
  const hdr = p.getByRole('button',{name:/^Partie 14\s*10 sujets/}).last();
  const hdrs = p.locator('text=Partie 14');
  const H = p.getByText('Partie '+PT,{exact:true}).last();
  const target = await H.evaluate(e=>e.closest('button').getBoundingClientRect().top+window.scrollY);
  const maxY = await p.evaluate(()=>document.documentElement.scrollHeight-window.innerHeight);
  J.Y1 = Math.round(Math.min(target - 300, maxY)); console.log('Y1', J.Y1);
  await p.mouse.move(1590,890);
  const N=48; for (let i=0;i<=N;i++){ await p.evaluate(y=>window.scrollTo(0,y), Math.round(ease(i/N)*J.Y1)); await p.waitForTimeout(30); await shot('B'+String(i).padStart(3,'0')); }
  const hb = await H.evaluate(e=>{const r=e.closest('button').getBoundingClientRect(); return [r.left,r.top,r.right,r.bottom];});
  J.hdr = hb; console.log('hdr', hb);
  await p.mouse.move((hb[0]+hb[2])/2,(hb[1]+hb[3])/2); await p.waitForTimeout(300); await shot('C0');
  await p.mouse.click((hb[0]+hb[2])/2,(hb[1]+hb[3])/2); await p.waitForTimeout(1500);
  await shot('C1');
  const t2 = p.getByText('Tâche '+(process.env.TACHE||'3'),{exact:true}).first().locator('xpath=ancestor::button[1]');
  J.t2 = await box(t2); console.log('t2', J.t2);
  await p.mouse.move((J.t2[0]+J.t2[2])/2,(J.t2[1]+J.t2[3])/2); await p.waitForTimeout(300); await shot('C2');
  await t2.click(); await p.waitForTimeout(1500); await shot('C3');
  const btn = p.getByText('Commencer la simulation').filter({visible:true}).first();
  const y0 = await p.evaluate(()=>window.scrollY);
  const bb = await btn.boundingBox(); const Y2 = Math.round(y0 + bb.y - 640); J.Y2=[y0,Y2];
  await p.mouse.move(1590,890);
  const M=36; for (let i=0;i<=M;i++){ await p.evaluate(y=>window.scrollTo(0,y), Math.round(y0+ease(i/M)*(Y2-y0))); await p.waitForTimeout(30); await shot('D'+String(i).padStart(3,'0')); }
  J.btn = await box(btn);
  J.cor = await box(p.getByText('Voir la correction').filter({visible:true}).first());
  J.card = await p.evaluate(()=>{ const b=[...document.querySelectorAll('button,a')].find(e=>e.textContent.includes('Commencer la simulation') && e.getBoundingClientRect().height>0); let e=b; while(e && !(e.getBoundingClientRect().height>200)) e=e.parentElement; const r=e.getBoundingClientRect(); return [r.left,r.top,r.right,r.bottom]; });
  J.text = await p.evaluate(()=>{ let ps=[...document.querySelectorAll('p')].filter(e=>e.getBoundingClientRect().height>0 && e.textContent.trim().length>40 && /[?.»)]\s*$/.test(e.textContent.trim())); if(!ps.length) ps=[...document.querySelectorAll('p,div,span')].filter(e=>e.getBoundingClientRect().height>0 && e.children.length==0 && e.textContent.trim().length>40 && /[?.»)]\s*$/.test(e.textContent.trim())); const e=ps[0]; const r=e.getBoundingClientRect(); return {t:e.textContent, r:[r.left,r.top,r.right,r.bottom]}; });
  J.badge = await box(p.getByText(/Avec simulation/).filter({visible:true}).first()).catch(()=>null);
  await shot('E0');
  await p.mouse.move((J.btn[0]+J.btn[2])/2,(J.btn[1]+J.btn[3])/2); await p.waitForTimeout(300); await shot('E1');
  await p.mouse.move((J.cor[0]+J.cor[2])/2,(J.cor[1]+J.cor[3])/2); await p.waitForTimeout(300); await shot('E2');
  await p.mouse.move(1590,890);
  fs.writeFileSync(`${OUT}/J.json`, JSON.stringify(J,null,1));
  
  await b.close();
})();
