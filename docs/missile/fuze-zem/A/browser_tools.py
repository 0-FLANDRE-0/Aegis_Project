from pathlib import Path
import base64,gzip,hashlib,json,re,sys
H=Path(__file__).resolve().parent;R=H.parents[3]
sys.path[:0]=[str(R/'docs/pip/B'),str(R/'docs/helicopter/H')]
import browser_backend
browser_backend.install()
from browser import launch,load_fleet

def instrument(raw,helper):
 h=raw.decode();m=re.search(r'data-c55-index="13">([^<]+)</script>',h);s=gzip.decompress(base64.b64decode(m[1])).decode();mark='\n  completeShipStartup();';assert s.count(mark)==1;s=s.replace(mark,mark+'\n'+helper,1);z=gzip.compress(s.encode(),9,mtime=0);h=h[:m.start(1)]+base64.b64encode(z).decode()+h[m.end(1):];m=re.search(r'const records=(\[.*?\]);',h,re.S);rows=json.loads(m[1]);rows[13].update(rawBytes=len(s.encode()),gzipBytes=len(z),sha256=hashlib.sha256(s.encode()).hexdigest());return(h[:m.start(1)]+json.dumps(rows,separators=(',',':'))+h[m.end(1):]).encode()

def fixture():
 s=(R/'docs/missile/termination/A/live-fixture.js').read_text()
 a="_wip75ResetCase(seed);nextTargetId=1;engagementControlMode='MANUAL';"
 b=a+"SIM_SEED_BASE=(c.navigationSeed??2047861954)>>>0;SIM_RNG_STATE=(c.rngSeed??seed)>>>0;BATTLESPACE_SEED=SIM_SEED_BASE;"
 assert a in s;s=s.replace(a,b,1)
 a="""const t=makeBaseTarget(ax+Math.cos(brg)*kmToWorld(c.rangeKm??30),ay+Math.sin(brg)*kmToWorld(c.rangeKm??30),brg+Math.PI,c.targetSpeedMps??250);
 t.z=c.altM??5000;t.vz=0;t.acType='Su-35';t._testFixture=true;targetPool.push(t);
 const tid=trackIdForTruthV27('AIR',t.id,true);"""
 b="""const h=brg+Math.PI,along=c.targetSpeedMps??250,cross=c.crossSpeedMps??0;
 spawnEnemyMissile({id:1,x:ax+Math.cos(brg)*kmToWorld(c.rangeKm??30),y:ay+Math.sin(brg)*kmToWorld(c.rangeKm??30),z:c.altM??5000,vx:mpsToWorldSpeed(Math.cos(h)*along-Math.sin(h)*cross),vy:mpsToWorldSpeed(Math.sin(h)*along+Math.cos(h)*cross),heading:h,asmType:c.targetLabel??'Kh-35U',lastKnownShipX:ax,lastKnownShipY:ay});
 const t=enemyMissiles.at(-1);Object.assign(t,{z:c.altM??5000,vz:0,vx:mpsToWorldSpeed(Math.cos(h)*along-Math.sin(h)*cross),vy:mpsToWorldSpeed(Math.sin(h)*along+Math.cos(h)*cross)});wip112EnsureTargetState(t);
 const tid=trackIdForTruthV27('ASM',t.id,true);"""
 assert a in s;s=s.replace(a,b,1)
 s=s.replace("trackTruthRefV27('AIR',t.id)","trackTruthRefV27('ASM',t.id)",1)
 s=s.replace("classification:'FIGHTER'","classification:'ASM',domain:'AIR',isASM:true",1)
 s=s.replace("const samples=[],events=[];let lastKey=", "diagCaseA={fuze:[],phases:[],passes:[],maxDemand:null,lastRange:null,lastSlope:0,lastPhase:''};\n const samples=[],events=[];let lastKey=",1)
 s=s.replace("updateMissile(m,SIM_FIXED_DT);if(t.alive)","wip112AttachObservers();updateMissile(m,SIM_FIXED_DT);if(t.alive)envNativeAsmDamagePrefixD(t,SIM_FIXED_DT);diagStepA(m,t);if(t.alive)",1)
 s=s.replace("return {weapon,seed,scenario:","const samResult=m._deathReason?.startsWith('PROX_DETONATION_')?m._deathReason.slice(16):null;const retired=t._wip11cRetirementQueued?.cause;const actualOutcome=!t.alive&&retired==='WARHEAD_AIRBURST'?'KILL':!t.alive&&retired==='DELAYED_STRUCTURAL_FAILURE'?'STRUCT_FAIL':samResult;\n return {diagnostic:diagCaseA,fuzeState:Object.fromEntries(Object.entries(m).filter(([k])=>k.startsWith('_fuze')&&k!=='_fuzeOpportunityRngA'&&k!=='_fuzeSignalChannelsA')),actualOutcome,weapon,seed,scenario:",1)
 # Keep the original lethal-only success and report any native effect separately.
 s=s.replace("success:!t.alive&&!removed&&!!m.proxDetonated,", "success:!t.alive&&!removed&&!!m.proxDetonated,anyEffect:['KILL','STRUCT_FAIL','DAMAGED'].includes(actualOutcome),",1)
 return (H/'hooks.js').read_text()+'\n'+(R/'docs/envelope/D/diagnostic/native-asm-prefix.js').read_text()+'\n'+s
