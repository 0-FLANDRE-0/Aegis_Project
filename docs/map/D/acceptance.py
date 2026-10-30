from pathlib import Path
import json,hashlib,re,base64,gzip
H=Path(__file__).resolve().parent;R=H.parents[2];E=H/'evidence';load=lambda p:json.loads((H/p).read_text());sig=hashlib.sha256((R/'Aegis_SIM_v48_WIP_MAP_D.html').read_bytes()).hexdigest();checks={}
m=load('evidence/map-b/map-b.json');u=load('evidence/ui88/ui.json');w=load('evidence/warnings/warnings.json');x=load('evidence/extra/extra.json');n=load('evidence/network-only.json');d=load('evidence/domain-final/execution.json');pair=load('evidence/domain-final/paired-baseline/baseline-comparison.json');stat=load('evidence/static.json');world=load('evidence/delivery-world120.json');ui=load('evidence/new-ui/ui-c.json');motion=load('evidence/motion/motion.json');rules=load('evidence/rules/rules.json');rings=load('evidence/rings/rings.json');dom=load('evidence/dom-attachment.json')
count=0
for folder in ['helicopter-flight','aps153','isar-native','isar-classes','isar-clock','isar-ui','emcon-native','emcon-ui','harpoon-f1','harpoon-clock','sov-native','sov-casualty','sov-deployment','sov-visual']:
 qs=[]
 for f in(E/'domain-final'/folder).glob('*.json'):
  q=json.loads(f.read_text())
  if isinstance(q,dict)and isinstance(q.get('checks'),dict)and'pass'in q:qs.append(q)
 assert len(qs)==1,(folder,len(qs));q=qs[0];count+=len(q['checks']);checks['domain.'+folder]=q['pass']and all(q['checks'].values())
assert count==378;paired=[v for c in pair['cases']for v in c['checks'].values()];assert len(paired)==42
for k,q,expected in [('ui88',u,88),('mapB91',m,91),('warnings23',w,23),('extra13',x,13)]:checks[k]=q['pass']and len(q['checks'])==expected
checks.update(domain420=d['pass']and all(paired),networkOnly=n['pass'],native281Same=stat['checks']['native281Same'],envelopeByteSame=stat['checks']['tableByteSame'],world120=world['pass'],newUIC=ui['pass'],motionC=motion['pass'],rulesC=rules['pass'],ringsC=rings['pass'],domAttachment=dom['pass'])
# Compare every native result, including terminal state and samples.
b=json.loads(gzip.decompress((R/'docs/map/C/evidence/c2/MAP_C/release.json.gz').read_bytes()));t=json.loads(gzip.decompress((E/'c2/MAP_D/release.json.gz').read_bytes()));deltas=[a['id']for a,bb in zip(b['rows'],t['rows'])if a!=bb];term={'pass':len(b['rows'])==len(t['rows'])==300 and not deltas and not t['errors'],'shots':len(t['rows']),'differences':deltas,'successBefore':sum(r['result']['success']for r in b['rows']),'successAfter':sum(r['result']['success']for r in t['rows']),'htmlSha256':t['htmlSha256']};(E/'release300-comparison.json').write_text(json.dumps(term,indent=2)+'\n');checks['termination300']=term['pass']
b=json.loads((R/'docs/map/C/evidence/webgl8/observed-world.json').read_text());q=load('evidence/webgl8/observed-world.json');deltas=[]
for a,bb in zip(b['records'],q['records']):
 for key in ['weapon','enabled','launch','final','samples']:
  if a[key]!=bb[key]:deltas.append({'weapon':a['weapon'],'enabled':a['enabled'],'field':key})
web={'pass':q['pass']and len(q['records'])==8 and not deltas and all(r['framesAfterFlight'][1]>r['framesAfterFlight'][0]for r in q['records']),'flights':len(q['records']),'checks':len(q['checks']),'differences':deltas,'hitCount':sum(not r['final']['targetAlive']for r in q['records']),'htmlSha256':q['htmlSha256']};(E/'webgl8-comparison.json').write_text(json.dumps(web,indent=2)+'\n');checks['webgl8']=web['pass']
for key,q in [('map-b',m),('ui88',u),('warnings',w),('extra',x),('network',n),('domain',d),('world',world),('new-ui',ui),('motion',motion),('rules',rules),('rings',rings),('static',stat),('DOM',dom),('termination',term),('webgl',web)]:checks[key+'.finalHtmlSha256']=q['htmlSha256']==sig
checks['pair.finalHtmlSha256']=pair['candidateSha256']==sig
prior=json.loads((R/'docs/map/C/approved-raid-baselines.json').read_text());current=load('approved-raid-baselines.json');checks['sixApprovedEntriesUnchanged']=prior['entries']==current['entries'];checks['tableStatusMatch']=all(v['match']for k,v in ui['records'].items()if k.endswith('.status'))
source=(H/'map_d.js').read_text()+'\n'+(H/'preview.js').read_text();checks['noTargetTruthInNewPresentation']=not re.search(r'\b(?:enemyMissiles|targetPool|truthRef|RF_PHYSICS)\b',source)
raw=(R/'Aegis_SIM_v48_WIP_MAP_D.html').read_bytes();main=gzip.decompress(base64.b64decode(re.search(rb'data-c55-index="13">([^<]+)',raw)[1]));manifest=json.loads(re.search(rb'const records=(\[.*?\]);',raw,re.S)[1])[13];checks['compressedMainIntegrity']=hashlib.sha256(main).hexdigest()==manifest['sha256']and len(main)==manifest['rawBytes']
newD={}
for key,path in [('D_native','evidence/d-native/native.json'),('D_ui','evidence/d-ui/ui.json'),('D_edges','evidence/d-edges/edges.json')]:
 q=load(path);checks[key]=q['pass']and all(q['checks'].values());checks[key+'.finalHtmlSha256']=q['htmlSha256']==sig;newD[key]=len(q['checks'])
checks['all3780ExistingSymbolsSame']=stat['checks']['allExistingTopLevelSame']
checks['exactNativeHarpoonPreview']=stat['checks']['previewCopiesExact']
freeze=load('PRODUCT_FREEZE.json');checks['productFreeze']=freeze['htmlSha256']==sig and all(hashlib.sha256((R/p).read_bytes()).hexdigest()==v for p,v in freeze['sources'].items())
checks['creditsUnchanged']=hashlib.sha256((R/'CREDITS.md').read_bytes()).hexdigest()==freeze['creditsSha256']
for key,q,num in [('UIC135',ui,135),('motion73',motion,73),('rules45',rules,45),('rings33',rings,33),('DOM13',dom,13)]:checks[key+'.count']=len(q['checks'])==num
checks['testFixturesNotShipped']=all(q not in main.decode()for q in ['__MD_TEST__','__MB_TEST__','__MC_TEST__'])
out={'pass':all(checks.values()),'checks':checks,'counts':{'domain':420,'ui':88,'mapB':91,'warnings':23,'extra':13,'newUI':len(ui['checks']),'motion':len(motion['checks']),'rules':len(rules['checks']),'rings':len(rings['checks']),'dom':len(dom['checks']),**newD,'nativeFunctions':281,'nativeTerminationShots':300,'naturalWebglFlights':8,'naturalWebglAssertions':29,'terminationSuccess':term['successAfter'],'naturalHitCount':web['hitCount']},'htmlSha256':sig,'scope':'All final evidence above was executed on the delivered final HTML SHA. Initial development evidence is retained separately and is not counted.'};(E/'acceptance.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out));assert out['pass']
