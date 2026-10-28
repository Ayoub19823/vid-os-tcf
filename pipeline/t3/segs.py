import sys, wave, numpy as np
SR=44100
def rd(p):
    w=wave.open(p); x=np.frombuffer(w.readframes(w.getnframes()),'<i2').astype(float)/32768; return x.reshape(-1,w.getnchannels()).mean(1)
def segs(x, thr=0.008, minsil=1.5):
    win=int(0.02*SR); e=np.sqrt(np.convolve(x**2,np.ones(win)/win,'same')); idx=np.nonzero(e>thr)[0]
    out=[]; s=idx[0]; p=idx[0]
    for j in idx[1:]:
        if j-p>minsil*SR: out.append((s,p)); s=j
        p=j
    out.append((s,p)); return out
def find(f, n):
    x=rd(f); res={}
    for ms in np.arange(0.6,3.01,0.1):
        sg=segs(x,minsil=ms); res[round(ms,1)]=len(sg)
        if len(sg)==n: return x, sg, ms, res
    return x, None, None, res
if __name__=='__main__':
    for f,n in [(a, int(b)) for a,b in zip(sys.argv[1::2], sys.argv[2::2])]:
        x,sg,ms,res=find(f,n)
        print(f, n, 'ms', ms, 'counts', res if sg is None else '', [round((b-a)/SR,1) for a,b in sg] if sg else '')

def robust(x, n):
    """segmentation tolérante : retire les blips < 0.4 s, puis coupe les segments fusionnés à leur plus long silence"""
    best = None
    for ms in np.arange(0.6, 2.01, 0.1):
        sg = [s for s in segs(x, minsil=ms) if (s[1] - s[0]) / SR > 0.4]
        if len(sg) == n: return sg
        if len(sg) < n and (best is None or len(sg) > len(best)): best = sg
    sg = list(best)
    win = int(0.02 * SR); e = np.sqrt(np.convolve(x ** 2, np.ones(win) / win, 'same'))
    while len(sg) < n:
        i = max(range(len(sg)), key=lambda k: sg[k][1] - sg[k][0]); a, b = sg[i]
        quiet = e[a:b] < 0.008; best_len, best_mid, run, st = 0, None, 0, 0
        for j, q in enumerate(quiet):
            if q:
                if run == 0: st = j
                run += 1
                if run > best_len: best_len, best_mid = run, st + run // 2
            else: run = 0
        if best_mid is None: break
        c = a + best_mid; sg[i:i + 1] = [(a, c - best_len // 2), (c + best_len // 2, b)]
    return sg
