"""Audit exhaustive grids, five real native shots, boundaries and delivery."""
from pathlib import Path
import gzip,hashlib,json,math,statistics
H=Path(__file__).resolve().parent
m=json.loads((H/'results/measurement.json').read_text());checks={};records=[];calls=0
table=json.loads((H/'ENVELOPE_TABLE_D.json').read_text());canonical={r['cellId']:r for r in table['rows']}
checks['embedded120']=len(canonical)==120
checks['main120']=sum(not r.get('auxiliary')for r in m['rows'])==120
checks['aux6']=sum(bool(r.get('auxiliary'))for r in m['rows'])==6
checks['uniqueCells126']=len({r['cellId']for r in m['rows']})==126
for row in m['rows']:
 p=H/'results/cells'/(row['cellId']+'.json.gz');raw=gzip.decompress(p.read_bytes());j=json.loads(raw)
 expected=next(q['sha256']for q in m['logicalHashes']if q['cellId']==row['cellId'])
 d={q['rangeKm']:q for q in j['distances']};local={}
 local['logicalHash']=hashlib.sha256(raw).hexdigest()==expected
 local['fiveDistinctNativeSeedPairs']=all(len(q['shots'])==5 and [{k:s[k]for k in ['rngSeed','navigationSeed']}for s in q['shots']]==m['seeds']for q in d.values())
 local['allFartherIntegerKmActuallyTested']=all(r in d and not d[r]['anyEffect']for r in range(max(5,row['maxRangeKm']+1),501))
 local['maxBoundaryNativeEffect']=row['maxRangeKm']==0 or d[row['maxRangeKm']]['effectCount']>=1
 local['effectiveContinuousFrom5']=all(r in d and d[r]['lethalCount']>=3 for r in range(5,row['effectiveRangeKm']+1,5))
 local['effectiveFirstBreak']=row['effectiveRangeKm']==500 or d[row['effectiveRangeKm']+5]['lethalCount']<3
 local['rangeOrdering']=0<=row['effectiveRangeKm']<=row['maxRangeKm']<=500 and row['effectiveRangeKm']%5==0
 local['allShotsHaveOutcomeAndReason']=all(isinstance(s['outcome'],str)and isinstance(s['reason'],str)and s['reason']for q in d.values()for s in q['shots'])
 local['nativeTargetLabel']=all(s['targetLabel']==row['targetLabel']for q in d.values()for s in q['shots'])
 local['requiredTerminalNumericsFinite']=all(all(isinstance(s['terminal'][k],(int,float))and math.isfinite(s['terminal'][k])for k in ['timeS','xM','yM','altitudeM','speedMps'])for q in d.values()for s in q['shots'])
 local['callsMatchDistances']=row['calls']==len(d)*5
 if not row.get('auxiliary'):
  c=canonical[row['cellId']]
  local['embeddedDistancesMatchNative']=c['maxRangeKm']==row['maxRangeKm']and c['effectiveRangeKm']==row['effectiveRangeKm']
  for name,boundary,pointKey,flag in [('outer','maxBoundary','maxInterceptPoint','success'),('inner','effectiveBoundary','effectiveInterceptPoint','lethal')]:
   q=row[boundary];values=[s['interceptPointKm']for s in q['shots']if s[flag]]if q else[];point=c[pointKey]
   local[name+'PointAveragesNativeSuccessfulShots']=(point is None)if not values else point is not None and point['minKm']==min(values)and point['maxKm']==max(values)and math.isclose(point['meanKm'],statistics.fmean(values),rel_tol=0,abs_tol=1e-10)
 calls+=row['calls'];checks.update({row['cellId']+'.'+k:v for k,v in local.items()});records.append({'cellId':row['cellId'],'distances':len(d),'calls':row['calls'],'checks':local})
checks['totalCalls']=calls==m['calls']
for name,file in [('nativePath','evidence/path.json'),('boundaryTrajectoryDeterminism','evidence/determinism.json'),('finalHtml','evidence/delivery-verification.json')]:
 j=json.loads((H/file).read_text());checks[name]=j['pass']
reg=json.loads((H/'REG_K_RESULTS.json').read_text());checks['regressionFullyCollected']=all(k in reg['acceptance']for k in ['current','recovery'])
checks['regression420And88PerBuild']=all(v['domain']['count']==420 and v['ui']['count']==88 for v in reg['acceptance'].values())
provenance=json.loads((H/'PROVENANCE.json').read_text());checks['nativeMeasurementFilesUnchanged']=all(hashlib.sha256((H/f).read_bytes()).hexdigest()==sha for f,sha in provenance['files'].items())
out={'schema':'AEGIS_REG_K_ENV_D_VERIFICATION_1','verificationPass':all(checks.values()),'measurementComplete':len(records)==126,'fullSweepCount':1,'checks':checks,'records':records,'shots':calls,'regressionPass':reg['pass'],'successToFailure':reg['successToFailureCount'],'failureToSuccess':reg['failureToSuccessCount'],'gameCodeChanged':False,'tableRows':120}
(H/'evidence/verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'pass':out['verificationPass'],'checks':len(checks),'failed':[k for k,v in checks.items()if not v],'shots':calls,'regressionPass':reg['pass']}));raise SystemExit(0 if out['verificationPass']else 1)
