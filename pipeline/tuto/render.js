const { chromium } = require('playwright'); const { spawn } = require('child_process'); const fs = require('fs');
(async () => { const br = await chromium.launch({ args: ['--allow-file-access-from-files'] }); const p = await br.newPage({ viewport: { width: 1920, height: 1080 } });
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.goto('file://' + __dirname + '/index.html'); await p.waitForFunction('window.READY', null, { timeout: 90000 });
  const { T0, TOTAL } = await p.evaluate(() => ({ T0: TL.T0, TOTAL: TL.TOTAL })); const NF = Math.round(TOTAL * 30); const b = T0.map(v => Math.round(v * 30)); b[0] = 0; b[11] = NF;
  for (const k of process.argv[2].split(',').map(Number)) { const tmp = `sc/tmp_${k}.mp4`;
    const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-c:v', 'mjpeg', '-framerate', '30', '-i', '-', '-c:v', 'libx264', '-crf', '18', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-r', '30', tmp], { stdio: ['pipe', 'inherit', 'inherit'] });
    for (let f = b[k]; f < b[k + 1]; f++) { await p.evaluate(t => window.seek(t), f / 30); const buf = await p.screenshot({ type: 'jpeg', quality: 92 }); if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r)); }
    ff.stdin.end(); const code = await new Promise(r => ff.on('close', r)); if (code !== 0) throw new Error('ffmpeg ' + code); fs.renameSync(tmp, `sc/s${String(k).padStart(2, '0')}.mp4`); console.log('scene', k, b[k + 1] - b[k], 'frames'); }
  await br.close(); })().catch(e => { console.error('ERR', e.message); process.exit(1); });
