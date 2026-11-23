const { chromium } = require('playwright');
(async () => { const br = await chromium.launch({ args: ['--allow-file-access-from-files'] }); const p = await br.newPage({ viewport: { width: 1920, height: 1080 } });
  p.on('pageerror', e => console.log('PAGEERR', e.message)); p.on('console', m => { if (m.type() === 'error') console.log('CONS', m.text()); });
  await p.goto('file://' + __dirname + '/index.html'); await p.waitForFunction('window.READY', null, { timeout: 60000 });
  console.log(await p.evaluate(() => JSON.stringify(TL.T0.map(v => +v.toFixed(1)))));
  for (const t of process.argv[2].split(',')) { await p.evaluate(t => window.seek(t), +t); await p.screenshot({ path: `pv/t${t}.jpg`, type: 'jpeg', quality: 85 }); }
  await br.close(); })().catch(e => { console.error('ERR', e.message); process.exit(1); });
