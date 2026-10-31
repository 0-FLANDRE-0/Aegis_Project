"""Instrument the actual B1 source in memory; never write a modified product HTML."""
from pathlib import Path
import base64,gzip,hashlib,json,re,sys
H=Path(__file__).resolve().parent;B=H.parent;R=B.parents[2]
sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'))
from browser_tools import instrument
EXPECTED='c9ec99f0b04e24127cc494833b8b1de24492a7ef0c00c2ee1432dba131f83ccc'
def build(hooks=True,extra=''):
 raw=(R/'Aegis_SIM_v48_WIP_GUN_B1.html').read_bytes();assert hashlib.sha256(raw).hexdigest()==EXPECTED
 helper='\n'.join(p.read_text()for p in [R/'docs/map/E/test-helper.js',R/'docs/map/D/extension-fixture.js',R/'docs/gun/B1/test-fixture.js'])
 if not hooks:return instrument(raw,helper+'\n'+extra)
 h=raw.decode();m=re.search(r'data-c55-index="13">([^<]+)</script>',h);source=gzip.decompress(base64.b64decode(m[1])).decode()
 # Internal requestFire is a closure: replacing its exported property would
 # NOT exercise continuous AutoAA. One guarded test-only insertion is needed.
 anchor="    // The fixed-tick driver already refreshes this solution every second."
 # A separate NPC factory contains an older local function of the same name.
 # The own-ship copy uniquely owns the B1 solveAirTrack closure.
 air=source.index("  function solveAirTrack(trackId,ammoId='MFF_127_SIM'")
 begin=source.rindex('function createProfileGunModuleWip13B3(',0,air);at=source.index(anchor,begin)
 assert at<source.index('return {spec,installation:',begin)
 addition="""    // PHASE0_DIAGNOSTIC_ONLY: current observations + existing continuation solver.
    if(window.__G2D__?.active&&window.__G2D__.flags.fresh&&state.solution.airDomain){
      const at=performance.now(),fresh=solveAirTrack(id,ammoId,{seedSolution:state.solution});
      window.__G2D__.noteRefresh({step:simStepCounter,ok:fresh.ok,reason:fresh.reason??null,elapsedMs:performance.now()-at});
      if(!fresh.ok)return fresh;state.solution=fresh;
    }
"""
 source=source[:at]+addition+source[at:]
 anchor='    const mffEvent=p.mffB1?gunB1ShellEvent(p,prev,next,dt):null;'
 assert source.count(anchor)==1
 source=source.replace(anchor,anchor+"\n    if(window.__G2D__?.active)window.__G2D__.sweep(p,prev,next,dt,Math.min(1,...[targetT,terrainT,seaT,fuzeT,mffEvent?.t].filter(t=>t!=null)));",1)
 gz=gzip.compress(source.encode(),9,mtime=0);h=h[:m.start(1)]+base64.b64encode(gz).decode()+h[m.end(1):];m=re.search(r'const records=(\[.*?\]);',h,re.S);rs=json.loads(m[1]);rs[13].update(rawBytes=len(source.encode()),gzipBytes=len(gz),sha256=hashlib.sha256(source.encode()).hexdigest());h=h[:m.start(1)]+json.dumps(rs,separators=(',',':'))+h[m.end(1):]
 return instrument(h.encode(),helper+'\n'+(H/'hooks.js').read_text())
