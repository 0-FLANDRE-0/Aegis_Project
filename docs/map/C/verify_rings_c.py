from pathlib import Path
import sys,json,hashlib,math
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(H));from verify_map_helpers import *
E=H/'evidence/rings';E.mkdir(parents=True,exist_ok=True);checks={};records={};errors=[]
def ck(k,v):checks[k]=bool(v);print(k,bool(v),flush=True)
def geometry(q):return[c for c in q['calls']if not(c.get('set')=='font'or c.get('method')=='fillText')]
with sync_playwright()as pw:
 b=launch(pw)
 for w,h in [(1400,900),(832,384)]:
  versions={}
  for version in ['B','C']:
   raw=(R/f'Aegis_SIM_v48_WIP_MAP_{version}.html').read_bytes();p=load_fleet(b,instrument(raw,(H/'test-helper.js').read_text()+'\n'+(H/'motion-helper.js').read_text()),width=w,height=h,errors=errors);reset(p);select(p,'SM6');q=[]
   for targetCase in ['initial','target','deadzone']:
    if targetCase!='initial':
     reset(p);select(p,'SM6'if targetCase=='target'else'SM2');tid=p.evaluate('o=>__MB_TEST__.add(o)',{'rangeKm':10 if targetCase=='target'else 3,'altM':1000 if targetCase=='target'else 30,'speedMps':0 if targetCase=='target'else 680});o=p.evaluate('id=>__MAP_A__.objects().find(o=>o.key==="TRACK:"+id)',tid);p.evaluate('o=>__MAP_B__.pickObject(o,"MAIN")',o)
    p.evaluate('__MAP_B__.refresh(true)')
    for surface in ['MAIN','PIP']:
     # Identical logical rect across versions isolates ring draw geometry from changed bar height.
     view={'rect':{'x':0,'y':0,'w':w,'h':h-100,'shortSide':min(w,h-100)},'target':surface,'km':40 if targetCase=='initial'else 5,'center':{'x':0,'y':0}};probe=p.evaluate('v=>__MC_TEST__.ringProbe(v)',view);q.append({'case':targetCase,'surface':surface,'probe':probe});records[f'{w}.{version}.{targetCase}.{surface}']=probe
   versions[version]=q;p.close()
  for before,after in zip(versions['B'],versions['C']):
   tag=f"{w}.{after['surface']}.{after['case']}";ck(tag+'.sameGeometryColorDash',geometry(before['probe'])==geometry(after['probe']));fonts=[r['value']for r in after['probe']['calls']if r.get('set')=='font'];zoom=after['probe']['zoom'];ck(tag+'.font9',any(abs(float(f.split('px')[0])*zoom-9)<1e-8 for f in fonts));
   if after['case']!='initial':ck(tag+'.predictionFont11',any(abs(float(f.split('px')[0])*zoom-11)<1e-8 for f in fonts))
 b.close()
ck('pageErrors0',not errors);q={'pass':all(checks.values()),'checks':checks,'records':records,'errors':errors,'htmlSha256':hashlib.sha256((R/'Aegis_SIM_v48_WIP_MAP_C.html').read_bytes()).hexdigest()};(E/'rings.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':q['pass'],'count':len(checks),'failed':[k for k,v in checks.items()if not v]}));raise SystemExit(0 if q['pass']else 1)
