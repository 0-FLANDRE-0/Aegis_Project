"""Separate CDP samples of the unchanged PERF_B workload; no runtime overrides."""
import argparse,gzip,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'docs/performance/A'))
from benchmark import SETUP,MEASURE,CG
from browser_i import launch,load
def summary(p):
 nodes={n['id']:n for n in p['nodes']};parents={c:n['id'] for n in p['nodes'] for c in n.get('children',[])};own={};inc={}
 for sid,dt in zip(p.get('samples',[]),p.get('timeDeltas',[])):
  own[sid]=own.get(sid,0)+dt;i=sid
  while i:inc[i]=inc.get(i,0)+dt;i=parents.get(i)
 def rows(v):
  return [dict(nodes[i]['callFrame'],ms=us/1000) for i,us in sorted(v.items(),key=lambda q:-q[1])[:70]]
 return {'sampledMs':sum(p.get('timeDeltas',[]))/1000,'self':rows(own),'inclusive':rows(inc)}
def main():
 a=argparse.ArgumentParser();a.add_argument('html',type=Path);a.add_argument('out',type=Path);o=a.parse_args();o.out.mkdir(parents=True,exist_ok=True);errors=[];rows=[]
 with sync_playwright() as pw:
  b=launch(pw)
  for fleet in [1,3]:
   p=load(b,o.html.read_bytes(),ship=CG,errors=errors);setup=p.evaluate(SETUP,dict(fleet=fleet,count=64));cdp=p.context.new_cdp_session(p);cdp.send('Profiler.enable');cdp.send('Profiler.setSamplingInterval',{'interval':1000});cdp.send('Profiler.start');r=p.evaluate(MEASURE,240);profile=cdp.send('Profiler.stop')['profile'];p.close()
   (o.out/f'fleet{fleet}.json.gz').write_bytes(gzip.compress(json.dumps(profile,separators=(',',':')).encode(),9,mtime=0));s=summary(profile);rows.append(dict(fleet=fleet,setup=setup,result=r,summary=s));print(json.dumps({'fleet':fleet,'self':s['self'][:12],'inclusive':s['inclusive'][:20]}),flush=True)
  b.close()
 q={'sha256':hashlib.sha256(o.html.read_bytes()).hexdigest(),'rows':rows,'errors':errors};(o.out/'profile.json').write_text(json.dumps(q,indent=2)+'\n')
if __name__=='__main__':main()
