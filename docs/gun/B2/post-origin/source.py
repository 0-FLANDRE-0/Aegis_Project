"""The original Phase0 instrumenter, pointed explicitly at merged AIR_ORIGIN_A.
No product or historical Phase0 tool is edited. Only the input-file/sha guard
inside a private in-memory copy of the builder is substituted.
"""
from pathlib import Path
import base64,gzip,hashlib,json,re,sys
P=Path(__file__).resolve().parent;B=P.parent;R=B.parents[2];D=B/'diagnostic'
MAIN='cce180255e0f76b804a2ae6a3b6078aec2f9dea8'
SOURCE=R/'Aegis_SIM_v48_WIP_AIR_ORIGIN_A.html'
SOURCE_SHA='4c5191753025406697520c63afcc97c116a83c4b6b924a4b605b49233c697eeb'
MAIN_SHA='bc4453fb740dcf9df0ff43f8353f1099ce7a72fc3f03bf0e3bef5d8d3cfa6a97'
sha=lambda b:hashlib.sha256(b).hexdigest()
sys.path[:0]=[str(D),str(R/'docs/missile/fuze-zem/A')]
from browser_tools import instrument
def main_source(raw):return gzip.decompress(base64.b64decode(re.search(rb'data-c55-index="13">([^<]+)',raw)[1]))
assert sha(SOURCE.read_bytes())==SOURCE_SHA and sha(main_source(SOURCE.read_bytes()))==MAIN_SHA
original=(D/'build_fixture.py').read_text()
needle=" raw=(R/'Aegis_SIM_v48_WIP_GUN_B1.html').read_bytes();assert hashlib.sha256(raw).hexdigest()==EXPECTED"
replacement=" raw=SOURCE.read_bytes();assert hashlib.sha256(raw).hexdigest()==SOURCE_SHA"
assert original.count(needle)==1
scope={'__file__':str(D/'build_fixture.py'),'__name__':'_post_origin_phase0_builder','SOURCE':SOURCE,'SOURCE_SHA':SOURCE_SHA}
exec(compile(original.replace(needle,replacement,1),str(D/'build_fixture.py')+'::POST_ORIGIN_INPUT_ONLY','exec'),scope)
NAMES=['shipboardRadarEchoFieldWip13B13','shipboardRadarEchoToAirPlotWip13B13','spq9bAnonymousPlotContractV34','trackRadarPrediction','trackEkfUpdateRadar','spawnMainGunProjectileWip13B3']
FINGERPRINT="""
window.__POST_ORIGIN_SOURCES__=()=>Object.fromEntries([
 ['shipboardRadarEchoFieldWip13B13',shipboardRadarEchoFieldWip13B13],
 ['shipboardRadarEchoToAirPlotWip13B13',shipboardRadarEchoToAirPlotWip13B13],
 ['spq9bAnonymousPlotContractV34',spq9bAnonymousPlotContractV34],
 ['trackRadarPrediction',trackRadarPrediction],['trackEkfUpdateRadar',trackEkfUpdateRadar],
 ['spawnMainGunProjectileWip13B3',typeof g2nativeSpawn==='function'?g2nativeSpawn:spawnMainGunProjectileWip13B3]
].map(([name,f])=>[name,f.toString()]));
"""
NATIVE=r'''
window.__POST_ORIGIN_NATIVE__=c=>{const result=__GB_TEST__.scenario(c);return {result,rng:SIM_RNG_STATE,step:simStepCounter,coreState:{shipHP,navigation:{...shipNav,trail:undefined},gun:gunB1OwnGuns().map(([id,g])=>({id,q:g.snapshot()})),targets:enemyMissiles.map(t=>({id:t.id,p:{x:worldToMeters(t.x),y:worldToMeters(t.y),z:Number(t.z)||0},v:{x:worldSpeedToMps(t.vx??0),y:worldSpeedToMps(t.vy??0),z:Number(t.vz)||0},alive:t.alive})),lock:selectedLockId}};};
'''
def build(hooks=True):
 raw=scope['build'](hooks,NATIVE if not hooks else'')
 return instrument(raw,FINGERPRINT)
def provenance():return {'mergedMain':MAIN,'product':SOURCE.name,'productHtmlSha256':SOURCE_SHA,'productMainSha256':MAIN_SHA,'originalBuilderSha256':sha((D/'build_fixture.py').read_bytes()),'originalHooksSha256':sha((D/'hooks.js').read_bytes()),'builderSubstitution':{'old':needle,'new':replacement},'testOnly':True,'phase1ProductChanges':False}
