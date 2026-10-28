import sys, wave, numpy as np
SR=44100
w=wave.open(sys.argv[1]); x=np.frombuffer(w.readframes(w.getnframes()),'<i2').astype(float)/32768; x=x.reshape(-1,w.getnchannels()).mean(1); r=w.getframerate()
for ms in (1.2,1.0,1.4,0.9,1.6):
    win=int(0.02*r); e=np.sqrt(np.convolve(x**2,np.ones(win)/win,'same')); idx=np.nonzero(e>0.008)[0]
    out=[]; s=idx[0]; p=idx[0]
    for j in idx[1:]:
        if j-p>ms*r: out.append((s,p)); s=j
        p=j
    out.append((s,p))
    if len(out)==6: break
print(len(out), [(round(a/r-0.03,2), round((b-a)/r+0.05,2)) for a,b in out])
