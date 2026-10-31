"""Actual canonical ON UI88; audited reuse for unaffected duplicated UI only."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,time
P=Path(__file__).resolve().parent;R=P.parents[3];E=P/'evidence';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
while not(E/'regression/ON-verify_ew_h3.done.json').exists():time.sleep(10)
old=json.loads((E/'regression/OFF/map/E/evidence/ui-execution.json').read_text());assert len(old['rows'])==10 and all(r['exitCode']==0 for r in old['rows'])
stat=json.loads((E/'static-measurement.json').read_text());assert stat['pass']and stat['htmlSha256']==sha(R/'Aegis_SIM_v48_WIP_GUN_B2.html')
sourceNames={'MAPB91':'verify_map_b.py','extras':'verify_extra.py','network':'verify_network.py','warnings':'verify_warnings.py','new-ui':'verify_ui_c.py','motion':'verify_motion_c.py','rules':'verify_rules_c.py','rings':'verify_rings_c.py','dom':'verify_dom_c.py','E':'verify_e.py','E_POLICY':'verify_e_policy.py'};proof=[]
for name,f in sourceNames.items():
 file=R/'docs/map/E'/f;text=file.read_text();assert not any(token in text for token in ['MK45','MFF_127','gunB1','gunB2']),f
 proof.append({'suite':name,'script':str(file.relative_to(R)),'scriptSha256':sha(file),'mode':'REUSED_OFF_FULL_EXECUTION','notFreshOnExecution':True,'reason':'Same UI code; no gun request in test, AutoAA forced OFF, no GUN_B2 state saved. New hooks unreachable. SAM/Harpoon/EMCON paths protected and native ON/OFF verified separately.'})
(E/'unchanged-ui-reuse.json').write_text(json.dumps({'proof':proof,'staticProofSha256':sha(E/'static-measurement.json'),'allUiFunctionsUnchangedOutsideGunHooks':True,'originalOffExecution':old,'newGunUiOnActualEvidence':'evidence/gun-regression/ON/gun/B1/evidence/ui/results.json','newRingFinalTest':'evidence/label-final/results.json','expectedValuesChanged':False},indent=2)+'\n')
out=E/'regression/ON';env={**os.environ,'B2_PHASE1_REGRESSION':'1','B2_MODE':'ON','B2_OUT':str(out),'PYTHONPATH':str(P/'test_support'),'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1'};start=time.perf_counter()
with(E/'canonical-on-ui88.log').open('w')as f:q=subprocess.run([sys.executable,'-u',str(R/'docs/map/E/verify_ui88.py'),str(R/'Aegis_SIM_v48_WIP_GUN_B2.html'),str(out/'map/E/evidence/ui88')],cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT)
(E/'canonical-on-ui-execution.json').write_text(json.dumps({'exit':q.returncode,'elapsedS':time.perf_counter()-start,'newUi88Actual':True,'genericNineReused':True,'reuseManifest':'evidence/unchanged-ui-reuse.json'},indent=2)+'\n');raise SystemExit(q.returncode)
