"""Path-only adapters for unchanged native ingress/owners and R4 D1 reference."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,shutil,sys,time
P=Path(__file__).resolve().parent;R=P.parents[3]
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 ap=argparse.ArgumentParser();ap.add_argument('task',choices=['ingress','allocation','r4-d1','r4-natural','r4-auto-iff','r4-idle']);a=ap.parse_args()
 build=json.loads((P/'BUILD.json').read_text());b=module('slots_extra_c',P.with_name('B')/'regression_runner.py');rt=module('native_a_extra_c',P.with_name('A')/'verify_runtime.py')
 rt.CANDIDATE=R/build['html'];temp=rt.P/'evidence'/('track-c-extra-'+a.task);assert not temp.exists(),'Never overwrite an execution';temp.mkdir(parents=True);rt.E=temp
 receipt={'task':a.task,'candidateSha256':build['htmlSha256'],'originalFixtureSha256':hashlib.sha256((rt.P/'verify_runtime.py').read_bytes()).hexdigest(),'fixtureAssertionsChanged':False};at=time.monotonic()
 try:
  with b.heavy_browser_slot():
   if a.task.startswith('r4-'):
    rt.CANDIDATE=R/'Aegis_SIM_v48_WIP_TRACK_B_STABLE_D.html';receipt['executedHtmlSha256']=hashlib.sha256(rt.CANDIDATE.read_bytes()).hexdigest();assert receipt['executedHtmlSha256']==build['baselineHtmlSha256'];rt.worker({'r4-d1':'d1','r4-natural':'repro-original','r4-auto-iff':'auto-iff','r4-idle':'idle'}[a.task])
   else:
    rt.BASE=R/'Aegis_SIM_v48_WIP_TRACK_B_STABLE_D.html';rt.BASE_SHA=build['baselineHtmlSha256'];getattr(rt,{'ingress':'native_ingress','allocation':'allocation_and_owners'}[a.task])()
  receipt['status']='PASS'
 except SystemExit as ex:
  receipt.update(status='PASS'if ex.code in [None,0]else'INCOMPLETE',nativeScriptExitCode=ex.code)
  if ex.code not in [None,0]:raise
 except Exception as ex:
  receipt.update(status='INCOMPLETE',error=repr(ex));raise
 finally:
  receipt['wallS']=time.monotonic()-at;(temp/'EXECUTION.json').write_text(json.dumps(receipt,indent=2)+'\n');dest=P/'evidence'/('extra-'+a.task);assert not dest.exists();shutil.move(temp,dest);print(json.dumps(receipt),flush=True)
if __name__=='__main__':main()
