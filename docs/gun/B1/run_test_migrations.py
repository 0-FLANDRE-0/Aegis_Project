"""Two exact obsolete assertions, updated only for explicitly requested GUN features.
Run with GUN_B1_REGRESSION=OFF and the test_support PYTHONPATH.
Original reports are retained separately; product and original tests unchanged.
"""
from pathlib import Path
import sys,json,hashlib
H=Path(__file__).resolve().parent;R=H.parents[2];kind=sys.argv[1];assert kind in ['ui','edges'];p=R/f'docs/map/E/verify_d_{kind}.py';s=p.read_text()
if kind=='ui':
 old="q['model']['reason']=='NOT_SURFACE_TRACK'and not q['model']['allowed']";new="q['model']['reason']=='VELOCITY_UNCERTAINTY'and not q['model']['allowed']";reason='New AIR capability supersedes blanket surface-only rejection; legacy AIR fixture initializes the native default 80m/s velocity sigma and must still be blocked by the unchanged 30m/s GUN_B1 quality limit. The probe records this actual cause. Valid observed AIR cases are tested separately.'
else:
 old="('22000'if own.startswith('CG')else'24000')";new="'24000'";reason='Requested CG Mod4 fire-control maximum is 24km, replacing Mod2 22km; minimum remains exactly 800m.'
assert s.count(old)==1;s=s.replace(old,new)
fixtureChange=None
if kind=='ui':
 helper="\nwindow.__GB_LEGACY_AIR_INIT__=id=>{const tr=tracks.get(id),missing={...tr};delete missing._kfX;delete missing._kfP;const missingReason=gunB1AirReady(missing).reason;trackEkfInit(tr);return {missingReason,defaultVelocitySigmaMps:trackCovarianceMetrics(tr).velSigmaMps};};\n"
 mark='with sync_playwright()as pw:';assert s.count(mark)==1;s=s.replace(mark,'fixture+='+repr(helper)+'\n'+mark)
 needle="air=p.evaluate('__MB_TEST__.add({rangeKm:10,bearingDeg:30})');q=target"
 replacement="air=p.evaluate('__MB_TEST__.add({rangeKm:10,bearingDeg:30})');airInit=p.evaluate('id=>__GB_LEGACY_AIR_INIT__(id)',air);assert airInit=={'missingReason':'AIR_TRACK_3D_STATE_REQUIRED','defaultVelocitySigmaMps':80};records[tag+'.airFixtureB1']=airInit;q=target"
 assert s.count(needle)==1;s=s.replace(needle,replacement);fixtureChange={'before':needle,'after':replacement,'reason':'Legacy diagnostic track has no EKF until a native lazy initializer runs. Explicit native trackEkfInit fixes the fixture precondition at native sigma=80 without changing product coefficients or making it fireable. Also asserts missing-EKF branch separately.'}
out={'kind':kind,'source':p.relative_to(R).as_posix(),'sourceSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'oldAssertion':old,'newAssertion':new,'reason':reason,'productChanged':False,'originalTestFileChanged':False,'fixtureInitialization':fixtureChange};d=H/'evidence/test-migrations';d.mkdir(parents=True,exist_ok=True);(d/(kind+'.json')).write_text(json.dumps(out,indent=2)+'\n');exec(compile(s,str(p),'exec'),{'__name__':'__main__','__file__':str(p)})
