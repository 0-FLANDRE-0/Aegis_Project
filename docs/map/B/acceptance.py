from pathlib import Path
import json,hashlib,re,base64,gzip
H=Path(__file__).resolve().parent;R=H.parents[2];E=H/'evidence';load=lambda p:json.loads((H/p).read_text());raw=(R/'Aegis_SIM_v48_WIP_MAP_B.html').read_bytes();sig=hashlib.sha256(raw).hexdigest()
m=load('evidence/map-b/map-b.json');u=load('evidence/ui88-delivery/ui.json');w=load('evidence/warnings/warnings.json');x=load('evidence/extra/extra.json');n=load('evidence/network-only.json');d=load('evidence/domain-final/execution.json');pair=load('evidence/paired-delivery/baseline-comparison.json');stat=load('evidence/static.json');term=load('evidence/release300-comparison.json');web=load('evidence/webgl8-comparison.json');world=load('evidence/delivery-world120.json')
# 378 original domain assertions plus the unchanged 42 paired assertions.
checks={};count=0
for folder in ['helicopter-flight','aps153','isar-native','isar-classes','isar-clock','isar-ui','emcon-native','emcon-ui','harpoon-f1','harpoon-clock','sov-native','sov-casualty','sov-deployment','sov-visual']:
 qs=[]
 for f in(E/'domain-final'/folder).glob('*.json'):
  try:q=json.loads(f.read_text())
  except:continue
  if 'checks'in q and isinstance(q['checks'],dict)and'pass'in q:qs.append((f,q))
 assert len(qs)==1,(folder,[str(f)for f,q in qs]);q=qs[0][1];count+=len(q['checks']);checks['domain.'+folder]=q['pass']and all(q['checks'].values())
assert count==378
pairedChecks=[v for c in pair['cases']for v in c['checks'].values()];assert len(pairedChecks)==42
checks.update({'domain420':count+len(pairedChecks)==420 and all(pairedChecks)and d['pass'],'ui88':u['pass']and len(u['checks'])==88,'MAP_B91':m['pass']and len(m['checks'])==91,'warnings23':w['pass']and len(w['checks'])==23,'extra13':x['pass']and len(x['checks'])==13,'networkOnly':n['pass'],'native281ByteExact':stat['nativeFunctions']==281 and not stat['nativeFunctionFailures'],'envelopeByteExact':stat['envelopeBlockByteExact'],'termination300':term['shots']==300 and not term['newFailures']and not term['differences'],'webgl8':web['pass']and web['flights']==8 and web['actualWebGLFlights']==8,'world120IdleCombat':world['pass']})
for k,q in [('map-b',m),('ui88',u),('warnings',w),('extra',x),('network',n),('world',world)]:checks[k+'.finalHtmlHash']=q['htmlSha256']==sig
checks['paired.finalHtmlHash']=pair['candidateSha256']==sig
prior=json.loads((R/'docs/cleanup/B/approved-raid-baselines.json').read_text());now=load('approved-raid-baselines.json');checks['approvedExactExpectationsUnchanged']=prior['entries']==now['entries']
main=gzip.decompress(base64.b64decode(re.search(rb'data-c55-index="13">([^<]+)',raw)[1]));manifest=json.loads(re.search(rb'const records=(\[.*?\]);',raw,re.S)[1])[13];checks['compressedMainIntegrity']=len(main)==manifest['rawBytes']and hashlib.sha256(main).hexdigest()==manifest['sha256']
out={'pass':all(checks.values()),'checks':checks,'counts':{'domain':420,'ui':88,'mapB':91,'warning':23,'extra':13,'nativeSourceFunctions':281,'nativeTerminationShots':300,'naturalWebGLFlights':8,'naturalWebGLAssertions':29,'terminationSuccessBefore':term['successBefore'],'terminationSuccessAfter':term['successAfter'],'terminationNewFailures':0,'naturalHitCount':web['hitCount']},'htmlSha256':sig,'tableProfileHash':'fa87852960ef276597cd43653d3d112da07cd844448d5ee6ad703c4791043121','scope':'UI/input only. Long native regression results retain their actual intermediate HTML SHA. The final artifact preserves the same native flight source and constants; final UI/current-core paired and world hashes are separately verified.'};(E/'acceptance.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out));assert out['pass']
