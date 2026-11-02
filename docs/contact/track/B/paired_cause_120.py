"""Four NEW 120 s raid checks; original fixture changes only its tick horizon.

Not an old regression or approval. A/ACTIVE original setup, one continuous loop,
1 Hz scalars plus native launches/hits and 3.0-3.8 s precomputed B NIS edges.
"""
from pathlib import Path
import argparse,gzip,importlib.util,json,os,sys,time

P=Path(__file__).resolve().parent;R=P.parents[3]
spec=importlib.util.spec_from_file_location('paired_cause_original_support',P/'paired_cause.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
HELPER=P/'paired_cause_120.js';base.HELPER=HELPER

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',action='store_true');p.add_argument('--candidate-sha',required=True);p.add_argument('--out',type=Path,default=P/'evidence/paired-cause-120');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
 candidate=R/'Aegis_SIM_v48_WIP_TRACK_B.html';products=[('baseline',base.A,base.A_SHA),('active',candidate,a.candidate_sha)];original,expr=base.original_raid_expression();assert expr.count('raid:1920')==1;expr120=expr.replace('raid:1920','raid:7200',1)
 plan={'schema':'AEGIS_TRACK_B_NEW_120_RAID_PLAN_1','execution':'RUN'if a.run else'DRY_RUN','originalHorizonS':32,'newHorizonS':120,'ticks':7200,'continuousRun':True,'runs':4,'onlyFixtureCommandChange':'raid tick horizon 1920 -> 7200','originalExpressionSha256':base.sha(expr.encode()),'extendedExpressionSha256':base.sha(expr120.encode()),'helperSha256':base.sha(HELPER.read_bytes()),'runnerSha256':base.sha(Path(__file__).read_bytes()),'seed':0x6d2b79f5,'fps':60,'scale':8,'newTestNotOldRegression':True,'releaseApproved':False};(a.out/'PLAN.json').write_text(json.dumps(plan,indent=2)+'\n')
 if not a.run:print(json.dumps(plan));return 0
 assert os.environ.get('B2_PHASE1_REGRESSION')=='1'
 for label,file,pinned in products:assert base.sha(file.read_bytes())==pinned
 sys.path.insert(0,str(R/'docs/bunkerhill/K'));from browser_i import launch,load
 from playwright.sync_api import sync_playwright
 slots=base.module('paired120_shared_slots',P/'regression_runner.py');errors=[];records=[];results={};started=time.perf_counter();print(json.dumps({'pid':os.getpid(),'runs':4,'newHorizonS':120,'oneSharedBrowserLane':True}),flush=True)
 for label,file,pinned in products:
  body,proof_expected=base.instrument(file.read_bytes())
  for ship in base.SHIPS:
   with slots.heavy_browser_slot()as lease:
    with sync_playwright()as pw:
     browser=launch(pw);page=load(browser,body,ship=ship,errors=errors);page.set_default_timeout(1200000)
     # Existing B recorder is ON only to keep preexisting trace/native legacy
     # comparison available. No behavior switch is exposed or changed.
     if label=='active':page.evaluate('__TRACK_B__.configure({enabled:true,capacity:4096});__TRACK_B__.clear()')
     ready=page.evaluate('__TRACK_B_PAIRED_CAUSE_120__.start()');proof=page.evaluate('__TRACK_B_PAIRED_CAUSE_120__.proof()');proof_hash={k:base.sha(v.encode())if v else None for k,v in proof.items()};assert proof_hash['pipelineSource']==proof_expected['nativePipelineWrapperSha256'];assert proof_hash['baseSource']==proof_expected['nativeFixedTickSha256']
     original_result=page.evaluate(expr120,'raid');captured=json.loads(page.evaluate('JSON.stringify(__TRACK_B_PAIRED_CAUSE_120__.stop())'))
     assert not captured['faults'],captured['faults'];assert captured['step']==7200;assert original_result['run']['steps']==7200
     raw=json.dumps(captured,separators=(',',':')).encode();assert len(raw)<=10*1024*1024,('Passive record budget exceeded',len(raw));tag=label+'-'+ship
     (a.out/(tag+'.json.gz')).write_bytes(gzip.compress(raw,6,mtime=0));(a.out/(tag+'-result.json')).write_text(json.dumps(original_result,indent=2)+'\n')
     old=json.loads(gzip.decompress((P/'evidence/paired-cause'/(tag+'.json.gz')).read_bytes()))['rows'][-1];checkpoint=next(r for r in captured['rows']if r['step']==1920)
     checkpoint_checks={'ownCachedScalarsExact':checkpoint['own']==old['own'],'inventoryCountsExact':checkpoint['inventory']==old['inventory'],'originalRngFieldsExact':all(checkpoint['rng'][k]==old['rng'][k]for k in old['rng']),'samCountExact':checkpoint['samCount']==old['missiles']['samCount'],'ramCountExact':checkpoint['ramCount']==old['missiles']['ramCount'],'hostileCountExact':checkpoint['hostileCount']==old['missiles']['hostileCount']}
     final=captured['rows'][-1];flood=original_result['state']['damage']['flooding'];final_summary={'hp':original_result['state']['shipHP'],'waterM3':sum(x['waterM3']for x in flood['cells']),'waterByCell':[{'id':x['id'],'waterM3':x['waterM3']}for x in flood['cells']],'moduleDamage':original_result['state']['damage']['moduleDamage'],'survival':final['own']['survival'],'inventory':original_result['state']['inventory'],'targets':captured['targets'],'nativeAfterAction':original_result.get('afterActionTruth'),'rng':original_result['rng'],'launches':[e for e in captured['events']if e['kind']=='LAUNCH'],'shipHits':[e for e in captured['events']if e['kind']=='SHIP_HIT_NATIVE'],'nativeSystemHits':[e for e in captured['events']if e['kind']=='NATIVE_SYSTEM_HIT']}
     row={'label':label,'ship':ship,'productSha256':pinned,'sourceProofHashes':proof_hash,'instrumentation':proof_expected,'ready':ready,'run':original_result['run'],'uncompressedRecordBytes':len(raw),'checkpoint32Checks':checkpoint_checks,'all32ChecksExact':all(checkpoint_checks.values()),'final120':final_summary,'edgeWatchCount':len(captured['edges']),'lease':lease,'errors':list(errors)};records.append(row);results[(label,ship)]=row;(a.out/(tag+'-SUMMARY.json')).write_text(json.dumps(row,indent=2)+'\n');page.context.close();browser.close();print(json.dumps({'label':label,'ship':ship,'checkpoint32':checkpoint_checks,'finalHp':final_summary['hp'],'waterM3':final_summary['waterM3'],'nativeTargetOutcomes':[(t['id'],t['nativeOutcome'])for t in captured['targets']],'edges':len(captured['edges']),'wallS':time.perf_counter()-started}),flush=True)
   assert base.sha(file.read_bytes())==pinned
 comparisons=[]
 for ship in base.SHIPS:
  before=results[('baseline',ship)]['final120'];after=results[('active',ship)]['final120'];comparisons.append({'ship':ship,'before':before,'after':after,'fieldDeltas':list(base.diffs(before,after)),'strictFinalStateExact':before==after,'classification':'OUTCOME_COMPARISON_FOR_REVIEW_NOT_EXPECTATION_APPROVAL'})
 report={'schema':'AEGIS_TRACK_B_NEW_120_RAID_RESULT_1','status':'OBSERVED_FOR_REVIEW'if not errors else'INCOMPLETE','runs':records,'comparisons':comparisons,'errors':errors,'wallS':time.perf_counter()-started,'expectedValuesChanged':False,'releaseApproved':False};(a.out/'SUMMARY.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'wallS':report['wallS'],'releaseApproved':False}));return 0 if not errors else 1

if __name__=='__main__':raise SystemExit(main())
