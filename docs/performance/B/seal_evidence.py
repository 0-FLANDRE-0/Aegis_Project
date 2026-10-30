"""Seal fresh final-original reports/captures, serial benchmark and separate profiles."""
import argparse,gzip,hashlib,json,shutil
from pathlib import Path
from suite_catalog import SUITES,ROOT
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('run',type=Path);p.add_argument('benchmark',type=Path);p.add_argument('out',type=Path);p.add_argument('--profiles',nargs='*',type=Path,default=[]);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);html=a.html.read_bytes();hs=sha(html);rows=[];captures=[]
 suites={'static':('docs/performance/B/verify_static.py','static.json'),**SUITES}
 for name,(script,filename)in suites.items():
  f=a.run/name/filename;raw=f.read_bytes();q=json.loads(raw);assert q['pass']and not q.get('errors'),name
  tested=q.get('sha256',q.get('candidateSha256',q.get('htmlSha256')));assert tested==hs,(name,tested)
  groups=[q['checks']]if 'checks'in q else [c['checks']for c in q['cases']];assert all(v is True for g in groups for v in g.values()),name
  target=name+'.json'+('.gz'if len(raw)>30000 else '');data=gzip.compress(raw,9,mtime=0)if target.endswith('.gz')else raw;(a.out/target).write_bytes(data)
  rows.append({'suite':name,'checks':sum(len(g)for g in groups),'pass':True,'testedHtmlSha256':hs,'script':script,'scriptSha256':sha((ROOT/script).read_bytes()),'report':target,'reportSha256':sha(data),'uncompressedReportBytes':len(raw)})
  for image in sorted(f.parent.glob('*.png')):
   name2=name+'-'+image.name;shutil.copyfile(image,a.out/name2);captures.append({'path':name2,'sha256':sha(image.read_bytes()),'testedHtmlSha256':hs})
 benchmark=json.loads((a.benchmark/'benchmark.json').read_text());assert benchmark['pass']and benchmark['sha256']==hs
 benchmarkFiles=[]
 for f in sorted(a.benchmark.iterdir()):
  if f.name!='benchmark.json'and not f.name.startswith('state-'):continue
  shutil.copyfile(f,a.out/f.name);benchmarkFiles.append({'path':f.name,'sha256':sha(f.read_bytes()),'bytes':f.stat().st_size})
 previous=a.benchmark.parent/'benchmark-original-order';superseded=[]
 if previous.exists():
  assert sha((previous/'benchmark.json').read_bytes())==benchmark['conditions']['firstPassSource']['reportSha256']
  assert sha((previous/'benchmark-source.py').read_bytes())==benchmark['conditions']['firstPassSource']['scriptSha256']
  for f in sorted(previous.iterdir()):
   if f.name not in ['benchmark.json','benchmark-source.py']and not f.name.startswith('state-r1-'):continue
   target='not-counted-original-order-'+f.name+('.gz'if f.suffix in ['.json','.py']else '');data=gzip.compress(f.read_bytes(),9,mtime=0)if f.suffix in ['.json','.py']else f.read_bytes();(a.out/target).write_bytes(data);superseded.append({'path':target,'sha256':sha(data)})
 profileFiles=[]
 for folder in a.profiles:
  meta=json.loads((folder/'profile.json').read_text());assert not meta['errors'];name=folder.name
  assert all(r['result']['run']['steps']==240 and r['result']['core']==[]and all(v is None for v in r['result']['faults'])for r in meta['rows'])
  for f in sorted(folder.iterdir()):
   if f.name!='profile.json'and not f.name.endswith('.json.gz'):continue
   target=name+'-'+f.name;shutil.copyfile(f,a.out/target);profileFiles.append({'path':target,'sha256':sha(f.read_bytes()),'sampledHtmlSha256':meta['sha256'],'timingRun':False})
 manifest=a.html.with_suffix('.manifest.json');build=json.loads(manifest.read_text());assert build['htmlSha256']==hs;shutil.copyfile(manifest,a.out/'build-manifest.json')
 baseline=json.loads((a.run/'baseline/baseline-comparison.json').read_text());assert all(c['checks']['samePhysicalState']and c['checks']['sameCombatRng']for c in baseline['cases'])
 notes=[];failedCamera=a.run.parent/'failed-runs/camera-concurrent'
 if failedCamera.exists():
  evidence=[]
  for f in sorted(failedCamera.iterdir()):
   if f.suffix not in ['.log','.json']:continue
   target='not-counted-camera-concurrent-'+f.name;shutil.copyfile(f,a.out/target);evidence.append({'path':target,'sha256':sha(f.read_bytes())})
  notes.append({'suite':'camera','initialRun':'Desktop passed; mobile ally-focus wait timed out during parallel regression. No final report was generated.','resolution':'Same final HTML and unchanged G camera script rerun alone after other suites finished; both actual pointer/touch cases passed. Initial partial checks/capture are not included in counts.','files':evidence})
 summary={'schema':'AEGIS_PERFORMANCE_B_VERIFICATION_SUMMARY_1','candidate':'Aegis_SIM_v48_WIP_PERF_B.html','candidateBytes':len(html),'candidateSha256':hs,'mainSha256':build['mainSha256'],'baselineCommit':'4b42aacd4271ce790b47b981b9a58dc960e5d5c5','baselineHtmlSha256':build['baselineSha256'],'directChecks':sum(r['checks']for r in rows),'directPass':sum(r['checks']for r in rows),'supersededOrHistoricalChecksIncluded':0,'suites':rows,'captures':captures,'benchmark':{'conditions':benchmark['conditions'],'pairedCases':len(benchmark['pairs']),'allStateAndRngExact':benchmark['checks']['allPairedStateExact'],'summary':benchmark['summary'],'files':benchmarkFiles},'separateProfiles':profileFiles,'errors':{'page':0,'core':0,'runtime':0,'presentation':0},'conditions':{'seed':1831565813,'browser':'Chromium 151.0.7922.173 Debian13 / Playwright1.62.0; native RAF/WebGL SwiftShader','priorFeatures':'All26 H4A browser suites rerun directly on PERF_B bytes; three-owner1/8/16/64x, native defense/Harpoon/EW, damage/import/reset, UI/camera/network/team','strictOwnshipBaseline':'CG/DDG idle/damaged/8Kh32AUTO state including EW/network/tactical/maneuver/attack/team and combatRNG exact; exclude only profiler performance metadata','semantics':'Two native lexical planners,48 controlled cases each; full plan/reservations exact. Context lifetime/current reservation changes/new pose/damage/measurement and default forecast contracts. Pure exact-input frame transitions plus both real ship-profile core selftests. Dependency controls are not natural acquisition.','resources':'Prior shared paint retained; baseline2/candidate64 native models, pixels/geometry and partial/last/repeated disposal, live+MAINwreck+catalog and import/reset. Closed catalog retains model by existing design.','timings':'Serial after all other jobs,2repeats alternatingAB/BA, reverse second pass. Explicit host-duration normalization from outset; raw states preserved. CDP samples separate. Host CPU, not phone/GPU FPS.'},'actions':'not dispatched; local final-original gate','pass':True}
 summary['testExecutionNotes']=notes
 summary['supersededTimingEvidence']={'files':superseded,'note':'The old case traversal reversed in pass two but version ordering stayed the same within each case. PERF_B corrects this using original case index. Exact first pass retained; second pass rerun in opposite version order. Old second-pass timings are not counted.'}
 (a.out/'verification-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':True,'checks':summary['directChecks'],'suites':len(rows),'captures':len(captures),'pairedBenchmarkCases':len(benchmark['pairs']),'sha256':hs}))
if __name__=='__main__':main()
