"""Replay every TRACK-C egress-bearing battle with S1 after-action seeker diagnostics."""
from pathlib import Path
import gzip,hashlib,importlib.util,json,sys,time,traceback

P=Path(__file__).resolve().parent;R=P.parents[3];E=P/'evidence/egress';E.mkdir(parents=True,exist_ok=True)
ORIG=Path('/dev/shm/aegis-ciws-dmg-a');sys.path[:0]=[str(ORIG/'docs/pip/B'),str(ORIG/'docs/helicopter/H'),str(ORIG/'docs/multiship/G'),str(ORIG/'docs/bunkerhill/K'),str(ORIG/'docs/missile/fuze-zem/A')]
import browser_backend;browser_backend.install()
from browser_i import launch,load
from browser_tools import instrument
from playwright.sync_api import sync_playwright

def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def sha(data):return hashlib.sha256(data if isinstance(data,bytes) else Path(data).read_bytes()).hexdigest()
def save(path,data):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

def jobs():
 lineage=json.loads((R/'docs/contact/track/C/LINEAGE_RESULTS.json').read_text());source=json.loads((R/'docs/contact/track/B_statistics_r4/JOBS.json').read_text());cases={(q['scenario'],q['seed']):q['case'] for q in source if q['product']=='R4'};out=[]
 for row in lineage['rows']:
  if row['product']!='C' or not row['egress']:continue
  scenario,seed,_=row['id'].split('-');focus=[q['id'] for q in row['egress']];case={**cases[(scenario,int(seed))],'checkpointSeconds':[],'asmSeekerFocusIds':focus,'lineageOn':True}
  out.append({'id':row['id'],'scenario':scenario,'seed':int(seed),'focusIds':focus,'prior':row['egress'],'case':case})
 return out

def helper():
 s=(ORIG/'docs/contact/track/C/test_support/battle.js').read_text();needle="  window.__TRACK_C_AA_INTERNAL__?.begin({record:c.lineageOn!==false});";assert s.count(needle)==1;s=s.replace(needle,"  window.__ASM_SEEKER_A_DIAG__.beginBattle(c.asmSeekerFocusIds??[]);\n"+needle,1)
 needle="  const trackCLineage=window.__TRACK_C_AA_INTERNAL__?.finish()??null;";assert s.count(needle)==1;s=s.replace(needle,needle+"\n  const asmSeekerADiagnostic=window.__ASM_SEEKER_A_DIAG__.finishBattle();",1)
 needle='  return {trackCLineage,schema:';assert s.count(needle)==1;s=s.replace(needle,'  return {trackCLineage,asmSeekerADiagnostic,schema:',1)
 return (ORIG/'docs/contact/track/C/after_action.js').read_text()+'\n'+s

EXPR="""c=>{const r=__TRACK_STABLE_BATTLE__.run(c),focus=new Set(c.asmSeekerFocusIds);return {schema:'AEGIS_ASM_SEEKER_A_EGRESS_REPLAY_1',case:r.case,status:r.status,end:r.end,qualification:r.qualification,targets:r.targets.filter(q=>focus.has(q.id)),events:r.events.filter(q=>(q.kind==='AFTER_ACTION_ASM_STATE'&&focus.has(q.target?.id))||q.kind==='NATIVE_PHALANX_HIT'||q.kind==='NATIVE_INTERCEPT_RESULT'||q.kind==='NATIVE_SHIP_HIT_RECORD'),asm:r.asmSeekerADiagnostic,lineage:r.trackCLineage?{seeker:r.trackCLineage.seeker.filter(q=>focus.has(q.id)),faults:r.trackCLineage.faults,dropped:r.trackCLineage.dropped}:null,final:{globalRng:r.final.globalRng,core:r.final.core,runtimeFault:r.final.runtimeFault,presentationFault:r.final.presentationFault},faults:r.faults};}"""

def main():
 diag=R/'Aegis_SIM_v48_WIP_ASM_SEEKER_A_DIAG.html';build=json.loads((P/'DIAGNOSTIC_BUILD.json').read_text());assert sha(diag)==build['outputSha256']
 inst=module('asm_seeker_a_track_c_instrument',ORIG/'docs/contact/track/C/instrument.py');probed,probe=inst.physical_probe(diag.read_bytes());body=instrument(probed,helper());plan={'schema':'AEGIS_ASM_SEEKER_A_EGRESS_REPLAY_PLAN_1','inputHtml':diag.name,'inputSha256':sha(diag),'instrumentedSha256':sha(body),'physicalProbe':probe,'helperSha256':sha(helper().encode()),'jobs':jobs(),'productCodeChanged':False,'truthUse':'AFTER_ACTION_ONLY'};save(P/'EGRESS_REPLAY_PLAN.json',plan)
 completed={p.stem.replace('.json','') for p in E.glob('*.json.gz')};rows=[];started=time.monotonic()
 with sync_playwright() as pw:
  for index,job in enumerate(plan['jobs'],1):
   path=E/(job['id']+'.json.gz')
   if path.exists():
    data=json.loads(gzip.decompress(path.read_bytes()));rows.append({'id':job['id'],'status':'CACHED','sha256':sha(path),'targets':data['targets'],'end':data['end']});continue
   errors=[];at=time.monotonic();browser=launch(pw)
   try:
    page=load(browser,body,ship=job['case']['ship'],errors=errors);page.set_default_timeout(900000);data=page.evaluate(EXPR,job['case']);assert not errors and not data['faults'] and not data['asm']['faults'] and not data['lineage']['faults'],(errors,data['faults'],data['asm']['faults'],data['lineage']['faults']);assert data['final']['core']==[] and data['final']['runtimeFault'] is None
    blob=gzip.compress(json.dumps(data,ensure_ascii=False,separators=(',',':')).encode(),9,mtime=0);path.write_bytes(blob);row={'id':job['id'],'status':'VALID','sha256':hashlib.sha256(blob).hexdigest(),'wallS':time.monotonic()-at,'targets':data['targets'],'end':data['end']}
   except Exception as e:
    row={'id':job['id'],'status':'INCOMPLETE','wallS':time.monotonic()-at,'error':str(e),'traceback':traceback.format_exc()}
   finally:browser.close()
   rows.append(row);save(P/'EGRESS_REPLAY_PROGRESS.json',{'completed':len(rows),'planned':len(plan['jobs']),'elapsedS':time.monotonic()-started,'rows':rows});print(json.dumps({k:row.get(k) for k in ['id','status','wallS','error']}),flush=True)
   if row['status']!='VALID':break
 result={'schema':'AEGIS_ASM_SEEKER_A_EGRESS_REPLAY_RESULTS_1','status':'PASS' if len(rows)==len(plan['jobs']) and all(q['status'] in ['VALID','CACHED'] for q in rows) else 'INCOMPLETE','inputSha256':sha(diag),'instrumentedSha256':sha(body),'elapsedS':time.monotonic()-started,'rows':rows};save(P/'EGRESS_REPLAY_RESULTS.json',result);print(json.dumps({'status':result['status'],'runs':len(rows),'elapsedS':result['elapsedS']}));return result

if __name__=='__main__':main()
