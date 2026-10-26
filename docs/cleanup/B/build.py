"""CLEAN_B: change only diagnostic ENV_D data/accessor, preserve the whole game."""
from pathlib import Path
import base64,gzip,hashlib,json,re,subprocess
H=Path(__file__).resolve().parent;R=H.parents[2];A=R/'docs/cleanup/A'
sha=lambda b:hashlib.sha256(b).hexdigest()
raw=(R/'Aegis_SIM_v48_WIP_CLEAN_A.html').read_bytes();assert sha(raw)=='ceffbda64f3ffbefce4330b825e36408ea42bcc86abeddc27182843bd0b8ea45'
m=json.loads((H/'results/measurement.json').read_text());assert len(m['rows'])==120
old=json.loads((A/'ENVELOPE_TABLE_D.json').read_text());by={r['cellId']:r for r in old['rows']};rows=[]
for r in m['rows']:
 p=by[r['cellId']]
 rows.append({**{k:r[k]for k in ['cellId','weapon','altM','motion','targetLabel','targetSpeedMps','crossSpeedMps','maxRangeKm','effectiveMinKm','effectiveMaxKm','otherRuns','deadZones','boundaryFailures','refinedDistancesKm']},'intervalStatus':'MEASURED','maxInterceptPoint':p['maxInterceptPoint'],'effectiveMinInterceptPoint':r['effectiveMinBoundary']['lethalInterceptPoint'],'effectiveMaxInterceptPoint':r['effectiveMaxBoundary']['lethalInterceptPoint'],'outerBoundary':p['outerBoundary'],'effectiveMinBoundary':r['effectiveMinBoundary'],'effectiveMaxBoundary':r['effectiveMaxBoundary'],'sampleGrid':r['gridChecks'],'previous':p})
discard={'effectiveDefinition','effectiveMinSearchKm','effectiveMinResolutionKm','nextPointRule','noIntervalRule'}
conditions={**{k:v for k,v in old['conditions'].items()if k not in discard},'effectiveDefinition':'FARTHEST_ENDING_CONTIGUOUS_GRID_RUN','effectiveGrid':{'nearFromKm':1,'nearToKm':30,'nearStepKm':1,'farFromKm':35,'farStepKm':5,'cap':'maxRangeKm'},'passCriterion':'At least 3 of 5 KILL or STRUCT_FAIL','minimumRefinement':'If chosen first point >30km, fill integer points between its preceding failed point and first pass; re-form runs and choose the farthest-ending run','otherRunsPolicy':'Preserve all other sampled contiguous pass runs; do not use for ring','deadZonesPolicy':'Consecutive failing sampled points between pass runs; record leading/trailing failures separately'}
fp=json.loads((A/'fingerprint.json').read_text());fp['conditions']=conditions
profileHash=subprocess.check_output(['node','-e','const c=require("crypto"),f=require("fs"),x=JSON.parse(f.readFileSync(0,"utf8"));process.stdout.write(c.createHash("sha256").update(JSON.stringify(x)).digest("hex"));'],input=json.dumps(fp).encode()).decode()
table={**{k:v for k,v in old.items()if k not in ['rows','previousDefinition']},'schema':'AEGIS_ENVELOPE_TABLE_D_3','measurementRevision':'CLEAN_B','profileHash':profileHash,'conditions':conditions,'effectiveIntervalsComplete':True,'pendingEffectiveCells':0,'measurementStatus':'COMPLETE','rows':rows,'previousDefinition':{'schema':old['schema'],'profileHash':old['profileHash'],'revision':'CLEAN_A','policy':old['conditions']['effectiveDefinition'],'storage':'Exact preceding row in previous; earlier D2 history remains nested'},'newShots':m['newShotsTotal'],'measurementCalls':old['measurementCalls']+m['newShotsTotal'],'reusedBaseCommit':'60a83ccfbde89ec26d927b2993f0a4a9585c98af'}
(H/'ENVELOPE_TABLE_D.json').write_text(json.dumps(table,ensure_ascii=False,indent=2)+'\n');(H/'fingerprint.json').write_text(json.dumps(fp,indent=2)+'\n')
html=raw.decode();p=re.search(r'data-c55-index="13">([^<]+)</script>',html);main=gzip.decompress(base64.b64decode(p[1])).decode();pattern=r'// ENV_D_DATA_BEGIN[\s\S]*?// ENV_D_DATA_END';blocks=re.findall(pattern,main);assert len(blocks)==1
block=blocks[0];split=block.index('\nwindow.__ENV_D__=');newBlock='// ENV_D_DATA_BEGIN — DIAGNOSTIC_ONLY, no gameplay consumer or startup work.\nconst ENVELOPE_TABLE_D='+json.dumps(table,ensure_ascii=False,separators=(',',':'))+';'+block[split:]
new=re.sub(pattern,lambda _:newBlock,main);assert re.sub(pattern,'',new)==re.sub(pattern,'',main)
gz=gzip.compress(new.encode(),9,mtime=0);html=html[:p.start(1)]+base64.b64encode(gz).decode()+html[p.end(1):];p=re.search(r'const records=(\[.*?\]);',html,re.S);rs=json.loads(p[1]);rs[13].update(rawBytes=len(new.encode()),gzipBytes=len(gz),sha256=sha(new.encode()));html=html[:p.start(1)]+json.dumps(rs,separators=(',',':'))+html[p.end(1):]
out=R/'Aegis_SIM_v48_WIP_CLEAN_B.html';out.write_text(html)
receipt={'output':out.name,'sha256':sha(out.read_bytes()),'bytes':out.stat().st_size,'baseCommit':'60a83ccfbde89ec26d927b2993f0a4a9585c98af','baseHtmlSha256':sha(raw),'gameCodeChanged':False,'gameOutsideEnvelopeBlockByteExact':True,'gameCoreWithoutEnvelopeSha256':sha(re.sub(pattern,'',new).encode()),'profileHash':profileHash,'rows':120,'schema':table['schema'],'effectiveIntervalsComplete':True,'pendingCells':0}
(H/'build.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
