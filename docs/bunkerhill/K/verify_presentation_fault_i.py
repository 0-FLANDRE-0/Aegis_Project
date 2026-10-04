"""Controlled render exception: native RAF, CIC fallback, recovery and reset."""
from pathlib import Path
import argparse,hashlib,json,time
from playwright.sync_api import sync_playwright
from browser_i import launch,load,served_bytes
p=argparse.ArgumentParser();p.add_argument('html');p.add_argument('out');p.add_argument('--main-override');p.add_argument('--baseline');a=p.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True);errors=[];checks={};details={}
inject='''()=>{const v=window.__WIP148_3D_VIEW__,d=window.__NAVAL_SIM_DIAG__,original=v.render;window.__I_THROWN__=null;window.__I_AFTER_DRAWS__=0;v.render=function(...args){if(!window.__I_THROWN__){window.__I_THROWN__={step:d.ciwsB1Closure.snapshot().simStepCounter};throw Error('I_CONTROLLED_RENDER_EXCEPTION')}window.__I_AFTER_DRAWS__++;return original.apply(this,args)};d.ciwsB1Closure.setPaused(false);}'''
observe='''()=>({step:window.__NAVAL_SIM_DIAG__.ciwsB1Closure.snapshot().simStepCounter,active:window.__WIP148_3D_VIEW__.active,draws:window.__I_AFTER_DRAWS__,thrown:window.__I_THROWN__,simFault:window.__WIP125_DIAG__.wip150RuntimeFault(),presentationFault:window.__WIP125_DIAG__.wip150PresentationFault?.()??null})'''
with sync_playwright()as pw:
 b=launch(pw,webgl=True)
 if a.baseline:
  page=load(b,served_bytes(a.baseline),webgl=True,errors=errors);page.evaluate(inject);page.wait_for_function('window.__I_THROWN__',timeout=30000);first=page.evaluate(observe);page.wait_for_timeout(1200);last=page.evaluate(observe);details['baseline']={'first':first,'last':last};checks['BaselineRAFStopped']=first['step']==last['step']and last['draws']==0;page.close()
 page=load(b,served_bytes(a.html,a.main_override),webgl=True,errors=errors);page.evaluate(inject);page.wait_for_function('window.__I_THROWN__',timeout=30000);first=page.evaluate(observe)
 page.wait_for_function('()=>!window.__WIP148_3D_VIEW__.active&&window.__NAVAL_SIM_DIAG__.ciwsB1Closure.snapshot().simStepCounter>window.__I_THROWN__.step+10',timeout=30000);last=page.evaluate(observe);page.evaluate('window.__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(true)');details['candidate']={'first':first,'last':last}
 checks['NativeSimulationContinues']=last['step']>last['thrown']['step']+10;checks['CICFallback']=last['active']is False;checks['SimFaultAbsent']=last['simFault']is None
 checks['StructuredErrorPreserved']=last['presentationFault']['stage']=='EXTERNAL_3D'and'I_CONTROLLED_RENDER_EXCEPTION'in last['presentationFault']['message']and last['presentationFault']['action']=='RETURN_TO_CIC'
 page.evaluate('window.__WIP148_3D_VIEW__.open()');page.wait_for_function('window.__I_AFTER_DRAWS__>0',timeout=90000);checks['Native3DReopens']=page.evaluate('window.__WIP148_3D_VIEW__.active')
 page.evaluate('window.__NAVAL_SIM_DIAG__.resetEntireSessionV48Wip11A();window.__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(true)');checks['ResetClearsPresentationFault']=page.evaluate('window.__WIP125_DIAG__.wip150PresentationFault()')is None;checks['CoreZero']=page.evaluate('window.__CORE_SELFTEST_FAILURES__')==[];page.close();b.close()
expected=[e for e in errors if'I_CONTROLLED_RENDER_EXCEPTION'in e];unexpected=[e for e in errors if'I_CONTROLLED_RENDER_EXCEPTION'not in e];checks['OnlyBaselineControlledException']=len(expected)==(1 if a.baseline else 0);checks['UnexpectedErrorsZero']=not unexpected
r={'schema':'AEGIS_PRESENTATION_FAULT_CONTAINMENT_I','html':Path(a.html).name,'sha256':hashlib.sha256(Path(a.html).read_bytes()).hexdigest(),'diagnosticOnlyMemoryOverride':bool(a.main_override),'faultInjection':'PRESENTATION_ONLY_ONCE_NO_PHYSICS_EXCEPTION','checks':checks,'details':details,'expectedBaselineErrors':expected,'errors':unexpected,'pass':all(checks.values())};(out/'result.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'checks':checks,'errors':unexpected,'pass':r['pass']},ensure_ascii=False),flush=True)
if not r['pass']:raise SystemExit(1)
