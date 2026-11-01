"""Read-only timeline of unchanged CG UI failure, with independent feature flags."""
from pathlib import Path
import json,os,subprocess,sys,time,hashlib
P=Path(__file__).resolve().parent;R=P.parents[3];E=P/'evidence/ui-single-cause';E.mkdir(parents=True,exist_ok=True)
if len(sys.argv)>1:
 f=R/'docs/gun/B1/verify_ui.py';source=f.read_text().replace("R/'Aegis_SIM_v48_WIP_GUN_B1.html'","R/'Aegis_SIM_v48_WIP_GUN_B2.html'").replace("[(1400,900),(832,384)]","[(1400,900)]",1).replace("['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']","['CG_52_LATE_TICONDEROGA']",1).replace("['MAIN','PIP']","['MAIN']",1)
 hook=r'''
window.__B2_UI_TRACE__=[];
{const old=__GB_TEST__.uiTick;__GB_TEST__.uiTick=function(n){let result;for(let i=0;i<n;i++){result=old.call(this,1);if(i>=200&&i<=245){const tr=[...tracks.values()][0];__B2_UI_TRACE__.push({step:simStepCounter,ready:tr?gunB1AirReady(tr):null,guns:result.map(x=>({id:x.id,q:x.q,pointing:gunB2Pointing(x.spec,x.q.solution,x.q.bodyAzRad,x.q.elevationRad)}))});}}return result;};}
'''
 if os.environ.get('B2_PRECHECK_UNION')=='1':
  hook+=r"""
{const before=gunB2PrepareRelease.toString(),old='if(!gunB2Pointing(spec,state.solution,state.bodyAzRad,state.elevationRad).ok)return null;',next='if(!gunB2Pointing(spec,state.solution,state.bodyAzRad,state.elevationRad).ok&&!wip13b6GunPointingAssessment(spec,state.solution,state.bodyAzRad,state.elevationRad).ok)return null;';if(!before.includes(old))throw Error('PRECHECK_SOURCE_NOT_FOUND');gunB2PrepareRelease=eval('('+before.replace(old,next)+')');window.__B2_PRECHECK_EXPERIMENT__={before,after:gunB2PrepareRelease.toString(),finalPointingGateUnchanged:true};}
"""
  source=source.replace("records[tag+'.shots']=q","records[tag+'.shots']=q;records[tag+'.precheck']=p.evaluate('__B2_PRECHECK_EXPERIMENT__')",1)
 source=source.replace("with sync_playwright()as pw:","fixture+="+repr(hook)+"\nwith sync_playwright()as pw:",1).replace("records[tag+'.shots']=q","records[tag+'.shots']=q;records[tag+'.timeline']=p.evaluate('__B2_UI_TRACE__')",1)
 # These are additional diagnostic repetitions, not replacements for failed originals.
 sys.argv=[str(f)];exec(compile(source,str(f)+'::ONE_CG_READ_ONLY_TIMELINE','exec'),{'__file__':str(f),'__name__':'__main__'});raise SystemExit()
base={k:False for k in ['alignment','dispersion','airWindow','fuze','fragments']};cases={'OFF':base,'ALIGNMENT':{**base,'alignment':True},'WINDOW':{**base,'airWindow':True},'ALL':{k:True for k in base}};rows=[]
for name,flags in cases.items():
 out=E/name;env={**os.environ,'B2_PHASE1_REGRESSION':'1','B2_MODE':'ON','B2_FLAGS':json.dumps(flags),'B2_ALLOW_AUTO':'1','B2_OUT':str(out),'PYTHONPATH':str(P/'test_support'),'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1'}
 with(E/(name+'.log')).open('w')as f:q=subprocess.run([sys.executable,'-u',__file__,name],cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT)
 rows.append({'flags':name,'exit':q.returncode});print(rows[-1],flush=True)
(E/'execution.json').write_text(json.dumps({'rows':rows,'originalTestChanged':False,'coefficientsChanged':False,'productSha256':hashlib.sha256((R/'Aegis_SIM_v48_WIP_GUN_B2.html').read_bytes()).hexdigest()},indent=2)+'\n')
