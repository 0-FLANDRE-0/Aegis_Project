"""AIR_ORIGIN_A: preserve the receiver actually used by RF; no numerical retuning."""
from pathlib import Path
import base64,gzip,hashlib,json,re,difflib
B=Path(__file__).resolve().parent;R=B.parents[3]
BASE=R/'Aegis_SIM_v48_WIP_GUN_B1.html';OUT=R/'Aegis_SIM_v48_WIP_AIR_ORIGIN_A.html'
raw=BASE.read_bytes();assert hashlib.sha256(raw).hexdigest()=='c9ec99f0b04e24127cc494833b8b1de24492a7ef0c00c2ee1432dba131f83ccc'
h=raw.decode();m=re.search(r'data-c55-index="13">([^<]+)</script>',h);before=gzip.decompress(base64.b64decode(m[1])).decode();s=before
def replace(old,new):
 global s
 assert s.count(old)==1,(old[:100],s.count(old));s=s.replace(old,new,1)
# These normalized receiver values already participate in range/elevation/Doppler.
# Adding metadata does not change echo extraction, RNG, RF strength or noise.
replace('sensorXWorld:rxX,sensorYWorld:rxY,sensorVxMps:rxVx,sensorVyMps:rxVy});',
        'sensorXWorld:rxX,sensorYWorld:rxY,sensorZM:rxZ,sensorVxMps:rxVx,sensorVyMps:rxVy,sensorVzMps:rxVz});')
start=s.index('function shipboardRadarEchoToAirPlotWip13B13(');end=s.index('\n',start);old=s[start:end]
new=old.replace('source,domainEvidence:evidence','sensorXWorld:echo.sensorXWorld,sensorYWorld:echo.sensorYWorld,sensorZM:echo.sensorZM,sensorVxMps:echo.sensorVxMps,sensorVyMps:echo.sensorVyMps,sensorVzMps:echo.sensorVzMps,source,domainEvidence:evidence');assert new!=old;replace(old,new)
start=s.index('function spq9bAnonymousPlotContractV34(');end=s.index('\n  function ',start+1);old=s[start:end]
new=old.replace("'source','domainEvidence'","'sensorXWorld','sensorYWorld','sensorZM','sensorVxMps','sensorVyMps','sensorVzMps','source','domainEvidence'");assert new!=old;replace(old,new)
gz=gzip.compress(s.encode(),9,mtime=0);h=h[:m.start(1)]+base64.b64encode(gz).decode()+h[m.end(1):]
m=re.search(r'const records=(\[.*?\]);',h,re.S);records=json.loads(m[1]);records[13].update(rawBytes=len(s.encode()),gzipBytes=len(gz),sha256=hashlib.sha256(s.encode()).hexdigest());h=h[:m.start(1)]+json.dumps(records,separators=(',',':'))+h[m.end(1):];OUT.write_bytes(h.encode())
(B/'AIR_ORIGIN_A.diff').write_text(''.join(difflib.unified_diff(before.splitlines(True),s.splitlines(True),fromfile=BASE.name+'::main',tofile=OUT.name+'::main')))
(B/'build.json').write_text(json.dumps({'baseCommit':'9719f1e8b3e574f0969eb57c6b2055f7f8d3ee4c','baseline':BASE.name,'baselineSha256':hashlib.sha256(raw).hexdigest(),'output':OUT.name,'sha256':hashlib.sha256(OUT.read_bytes()).hexdigest(),'mainSha256':hashlib.sha256(s.encode()).hexdigest(),'changedFunctions':['shipboardRadarEchoFieldWip13B13','shipboardRadarEchoToAirPlotWip13B13','spq9bAnonymousPlotContractV34'],'expectedValuesUpdated':False,'phase':'AIR_ORIGIN_A_ONLY'},indent=2)+'\n');print((B/'build.json').read_text())
