from pathlib import Path
import gzip,json,time
H=Path(__file__).resolve().parent
def read(name):return json.loads(gzip.decompress((H/'product-rf-parts'/name).read_bytes()))
parts=[read(f'{v}-S{i}-primary.json.gz')for v in ['BASE','FINAL']for i in range(1,6)];repeat=read('FINAL-S1-repeat.json.gz');rows=[x['row']for x in parts];errors=[e for x in parts+[repeat]for e in x['errors']]
comparison=[]
for i in range(1,6):
 b=next(x for x in rows if x['variant']=='BASE'and x['seedIndex']==i);f=next(x for x in rows if x['variant']=='FINAL'and x['seedIndex']==i);comparison.append({'seedIndex':i,'base':b['summary'],'final':f['summary']})
first=next(x for x in rows if x['variant']=='FINAL'and x['seedIndex']==1)
checks={'pageErrors0':not errors,'allFinite':all(all(isinstance(v,(int,float))and v==v and abs(v)!=float('inf')for p in x['result'].get('pathTrace',[])for v in [p['preShapePipLosGammaDeg'],p['usedGammaDeg'],*p['vFinal'].values()])for x in rows),'finalDeterministic':first['result']==repeat['row']['result'],'nativeRfUsed':all(x['result'].get('firstTrackS')is not None for x in rows)}
summary={'schema':'AEGIS_NEAR_VERTICAL_PATH_FIX_A_PRODUCT_RF_1','scope':'Actual Chromium product VLS/fixed-tick/native RF-EKF flight; ship track and linear ASM motion are controlled by the test fixture.','comparison':comparison,'checks':checks,'errors':errors};summary['pass']=all(checks.values())
(H/'product-rf-results.json.gz').write_bytes(gzip.compress(json.dumps({'summary':summary,'rows':rows,'repeat':repeat['row']},separators=(',',':')).encode(),9,mtime=0));(H/'product-rf-summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({'pass':summary['pass'],'checks':checks,'outcomes':comparison},indent=2));raise SystemExit(0 if summary['pass']else 1)
