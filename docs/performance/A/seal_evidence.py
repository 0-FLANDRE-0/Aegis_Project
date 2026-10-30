"""Seal fresh direct reports/captures and separate serial benchmark, pin every byte."""
import argparse,gzip,hashlib,json,shutil
from pathlib import Path
from suite_catalog import SUITES,ROOT
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('run',type=Path);p.add_argument('benchmark',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);html=a.html.read_bytes();hs=sha(html);rows=[];captures=[]
 suites={'static':('docs/performance/A/verify_static.py','static.json'),**SUITES}
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
  if f.name not in ['benchmark.json','benchmark-before-timing-normalization.json.gz']and not f.name.startswith('state-'):continue
  shutil.copyfile(f,a.out/f.name);benchmarkFiles.append({'path':f.name,'sha256':sha(f.read_bytes()),'bytes':f.stat().st_size})
 manifest=a.html.with_suffix('.manifest.json');build=json.loads(manifest.read_text());assert build['htmlSha256']==hs
 shutil.copyfile(manifest,a.out/'build-manifest.json')
 resource=json.loads((a.run/'resources/resources.json').read_text());baseline=json.loads((a.run/'baseline/baseline-comparison.json').read_text());assert all(c['checks']['samePhysicalState']and c['checks']['sameCombatRng']for c in baseline['cases'])
 summary={'schema':'AEGIS_PERFORMANCE_A_VERIFICATION_SUMMARY_1','candidate':'Aegis_SIM_v48_WIP_PERF_A.html','candidateBytes':len(html),'candidateSha256':hs,'mainSha256':build['mainSha256'],'baselineCommit':'b97925cb5fb27d4dad26d62db78520641ee70857','baselineHtmlSha256':build['baselineSha256'],'directChecks':sum(r['checks']for r in rows),'directPass':sum(r['checks']for r in rows),'supersededOrHistoricalChecksIncluded':0,'suites':rows,'captures':captures,'benchmark':{'conditions':benchmark['conditions'],'pairedCases':len(benchmark['pairs']),'allStateAndRngExact':benchmark['checks']['allPairedStateExact'],'summary':benchmark['summary'],'files':benchmarkFiles},'resourceSummary':{'nativeModels':64,'uniqueTextures':resource['pair']['candidate']['uniqueTextures'],'sourcePixelBytes':resource['pair']['candidate']['sourcePixelBytes'],'pixelAndGeometryParity':True,'lifecyclePass':True},'errors':{'page':0,'core':0,'runtime':0,'presentation':0},'conditions':{'seed':1831565813,'browser':'Chromium 151.0.7922.173 Debian13 / Python Playwright; CPU and native RAF/WebGL SwiftShader','priorFeatures':'All26 H4A browser suites rerun directly on PERF_A bytes; three-owner1/8/16/64x, actual native defense/Harpoon/EW, damage and import/reset, UI/camera/network/team','strictOwnshipBaseline':'CG/DDG idle/damaged/8Kh32AUTO state including EW/network/tactical/maneuver/attack/team and combatRNG exact; exclude only profiler performance metadata','semantics':'72 isolated EW dependency cases; supported outputs/call counts retained, unsupported pod calls0; isolated cache selftests in both real ship-profile browsers','resources':'baseline2 vs candidate64 models; native pixels and geometry exact; partial/last/repeated disposal, live+MAINwreck+catalog, import/reset epoch and recreation; closed catalog intentionally retains current model','timings':'benchmark serial after all other jobs,2repeats alternatingAB/BA, reverse second pass; not phone/GPU FPS','testHarnessNote':'Initial baseline command referred to pre-archive path and failed before comparison. Same baseline bytes rerun at archive path; only successful final reports counted.'},'actions':'not dispatched; user cannot use Actions; local final-original gate','pass':True}
 (a.out/'verification-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pass':True,'checks':summary['directChecks'],'suites':len(rows),'captures':len(captures),'pairedBenchmarkCases':len(benchmark['pairs']),'sha256':hs}))
if __name__=='__main__':main()
