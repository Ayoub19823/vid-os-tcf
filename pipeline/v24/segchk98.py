import sys,os,importlib,re,numpy as np
sys.argv=['x','k','a','b']
src=open('buildX.py').read(); pre=src[:src.index('E = [clean(t)')]
for mod,keys in (('script11',['amine','aissatou','christian','leila','serge']),('script12',['kenza','mamadou','anjali','oumar','bintou'])):
  for k in keys:
    os.environ['SCRIPT']=mod; g={}
    exec(pre.replace("key, ewav, cwav = sys.argv[1], sys.argv[2], sys.argv[3]", f"key, ewav, cwav = '{k}', '{k}/e1.wav', '{k}/c1.wav'"), g)
    S=g['S']; cl=g['clean']
    for nm,f in (('E',g['ewav']),('C',g['cwav'])):
      T=[cl(t) for t in S[nm]]; cs=g['clips'](f,len(T))
      rate=np.array([len(c)/44100/len(t) for c,t in zip(cs,T)])
      med=np.median(rate); bad=[(i,round(r/med,2)) for i,r in enumerate(rate) if r/med>1.7 or r/med<0.55]
      print(k,nm,'OK' if not bad else bad)
