from pathlib import Path
import gzip,hashlib,json,math
H=Path(__file__).resolve().parent;m=json.loads((H/'results/measurement.json').read_text());checks={};calls=0
provenance=json.loads((H/'provenance.json').read_text());fixture=json.loads((H/'path-fixture.json').read_text());table=json.loads((H/'ENVELOPE_TABLE_D.json').read_text());canonical={r['cellId']:r for r in table['rows']}
checks['frozenNativeSource']=hashlib.sha256((H/'native-engine.js').read_bytes()).hexdigest()==provenance['nativeSha256']
checks['frozenPrivateBoundary']=hashlib.sha256((H/'private.js').read_bytes()).hexdigest()==provenance['privateSha256']
checks['frozenMeasuredInputs']=fixture['input']==json.loads((H/'inputs.json').read_text())
checks['embedded120']=len(canonical)==120
checks['cells126']=len(m['rows'])==126;checks['main120']=sum(not r.get('auxiliary')for r in m['rows'])==120
for row in m['rows']:
 raw=gzip.decompress((H/'results/cells'/(row['cellId']+'.json.gz')).read_bytes());j=json.loads(raw);d={x['rangeKm']:x for x in j['distances']};c={}
 c['logicalHash']=hashlib.sha256(raw).hexdigest()==next(x['sha256']for x in m['logicalHashes']if x['cellId']==row['cellId'])
 c['allFartherKmFail']=all(r in d and not d[r]['anyEffect']for r in range(max(5,row['maxRangeKm']+1),501))
 c['outerEffect']=not row['maxRangeKm']or d[row['maxRangeKm']]['effectCount']>=1
 c['innerContinuous']=all(r in d and d[r]['lethalCount']>=3 for r in range(5,row['effectiveRangeKm']+1,5))
 c['innerBreak']=row['effectiveRangeKm']==500 or d[row['effectiveRangeKm']+5]['lethalCount']<3
 c['fiveSeeds']=all([{k:s[k]for k in ['rngSeed','navigationSeed']}for s in q['shots']]==m['seeds']for q in d.values())
 c['finiteAndComplete']=all(s.get('reason')and s.get('outcome')and all(math.isfinite(s['terminal'][k])for k in ['timeS','xM','yM','altitudeM','speedMps'])for q in d.values()for s in q['shots'])
 c['counts']=row['calls']==len(d)*5;calls+=row['calls'];checks.update({row['cellId']+'.'+k:v for k,v in c.items()})
 if not row.get('auxiliary'):
  t=canonical[row['cellId']];checks[row['cellId']+'.embeddedRanges']=all(t[k]==row[k]for k in ['maxRangeKm','effectiveRangeKm'])
  for name,key,flag in [('outer','maxBoundary','success'),('inner','effectiveBoundary','lethal')]:
   q=row[key];v=[s['interceptPointKm']for s in q['shots']if s[flag]]if q else[];p=t['maxInterceptPoint'if name=='outer'else'effectiveInterceptPoint']
   checks[row['cellId']+'.'+name+'NativePoints']=(p is None)if not v else p is not None and p['minKm']==min(v)and p['maxKm']==max(v)and abs(p['meanKm']-sum(v)/len(v))<1e-10
checks['shotsTotal']=calls==m['calls']
for name,file in [('path','evidence/path.json'),('determinism','evidence/determinism.json'),('delivery','evidence/delivery.json')]:checks[name]=json.loads((H/file).read_text())['pass']
out={'pass':all(checks.values()),'checks':checks,'shots':calls,'fullSweeps':1};(H/'evidence/verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'pass':out['pass'],'shots':calls,'checks':len(checks),'failed':[k for k,v in checks.items()if not v]}));raise SystemExit(0 if out['pass']else 1)
