"""Seal only fresh final-original reports, serial timings and repository checksums."""
import argparse,gzip,hashlib,json,shutil
from pathlib import Path
from suite_catalog import SUITES,ROOT
HERE=Path(__file__).resolve().parent
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('run',type=Path);p.add_argument('benchmark',type=Path);p.add_argument('latency',type=Path);p.add_argument('--checksums-only',action='store_true');a=p.parse_args();out=HERE/'evidence';out.mkdir(exist_ok=True);hs=sha(a.html.read_bytes())
 if not a.checksums_only:
  suites={'static':('docs/performance/D/verify_static.py','static.json'),**SUITES};rows=[];captures=[]
  for name,(script,filename)in suites.items():
   f=a.run/name/filename;raw=f.read_bytes();q=json.loads(raw);assert q['pass']and not q.get('errors'),name;tested=q.get('sha256',q.get('candidateSha256',q.get('htmlSha256')));assert tested==hs,(name,tested)
   groups=[q['checks']]if 'checks'in q else[c['checks']for c in q['cases']];assert all(v is True for g in groups for v in g.values()),name
   target=name+'.json'+('.gz'if len(raw)>30000 else '');data=gzip.compress(raw,9,mtime=0)if target.endswith('.gz')else raw;(out/target).write_bytes(data);rows.append({'suite':name,'checks':sum(len(g)for g in groups),'pass':True,'testedHtmlSha256':hs,'script':script,'scriptSha256':sha((ROOT/script).read_bytes()),'report':target,'reportSha256':sha(data)})
   for f in sorted(f.parent.glob('*.png')):
    target=name+'-'+f.name;shutil.copyfile(f,out/target);captures.append({'path':target,'sha256':sha(f.read_bytes()),'testedHtmlSha256':hs})
  b=json.loads((a.benchmark/'benchmark.json').read_text());l=json.loads((a.latency/'native-latency.json').read_text());assert b['pass']and l['pass']and b['sha256']==l['sha256']==hs
  files=[]
  for folder,allowed in [(a.benchmark,lambda f:f.name=='benchmark.json'or f.name.startswith('state-')),(a.latency,lambda f:f.name=='native-latency.json'or f.suffix=='.png')]:
   for f in sorted(folder.iterdir()):
    if not allowed(f):continue
    shutil.copyfile(f,out/f.name);files.append({'path':f.name,'sha256':sha(f.read_bytes()),'bytes':f.stat().st_size})
  notes=[];incomplete=a.latency.parent/'not-counted-z4-timeout'
  if incomplete.exists():
   note=json.loads((incomplete/'note.json').read_text());assert note['candidateSha256']==hs
   for f in sorted(incomplete.iterdir()):
    target='not-counted-z4-'+f.name+('.gz'if f.suffix=='.py'else '');data=gzip.compress(f.read_bytes(),9,mtime=0)if f.suffix=='.py'else f.read_bytes();(out/target).write_bytes(data)
   notes.append(note)
  manifest=json.loads(a.html.with_suffix('.manifest.json').read_text());assert manifest['htmlSha256']==hs;(out/'build-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
  q={'schema':'AEGIS_PERFORMANCE_D_VERIFICATION_SUMMARY_1','candidate':'Aegis_SIM_v48_WIP_PERF_D.html','candidateBytes':a.html.stat().st_size,'candidateSha256':hs,'mainSha256':manifest['mainSha256'],'baselineCommit':'5ddd05ce9358e9a23c11d26030bff05c6f18fa1d','baselineHtmlSha256':manifest['baselineSha256'],'directChecks':sum(r['checks']for r in rows),'directPass':sum(r['checks']for r in rows),'supersededOrHistoricalChecksIncluded':0,'suites':rows,'captures':captures,'benchmark':{'conditions':b['conditions'],'pairedCases':len(b['pairs']),'allStateAndRngExact':b['checks']['allPairedStateExact'],'summary':b['summary']},'nativeLatency':{'conditions':l['conditions'],'pairedCases':len(l['pairs']),'summary':l['summary']},'timingFiles':files,'errors':{'page':0,'core':0,'runtime':0,'presentation':0},'conditions':{'geometry':'Controlled native THREE generator differential on both profiles; quick/detail/sealed attribute bytes/index/groups/bounds/bindings exact. Cancellation after early publication and reset lifetime verified; this controlled fixture is not native latency evidence.','envelope':'Actual registered 3,072 layout queries and 384 convex duplicate/degenerate/signed-zero cases exact. No source-model geometry changes.','regression':'All 26 H4A suites plus prior PERF_A/B/C regression helpers rerun on final original; ownship six idle/damaged/AUTO cases and three-owner 1/8/16/64x, current release guards, native RAF/WebGL, UI/camera/EW/network/team/import/reset.','performance':'Serial after all other jobs; same seed, opposite AB/BA within cases, reverse second traversal. Density host CPU and separate native first cut/fold render submissions. No mobile FPS or hardware GPU completion claim.'},'actions':'not dispatched; local final-original gate','pass':True};(out/'verification-summary.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
  q['incompleteTimingNotes']=notes;(out/'verification-summary.json').write_text(json.dumps(q,ensure_ascii=False,indent=2)+'\n')
  size=q['candidateBytes'];n=q['directChecks'];ns=len(rows);rootfile=ROOT/q['candidate'];shutil.copyfile(a.html,rootfile)
  table='\n'.join(f"| {r['fleet']} | {r['count']} | {r['meanBefore']:.3f} | {r['meanAfter']:.3f} | {r['observedReductionPercent']:+.1f}% |"for r in b['summary'])
  native='\n'.join(f"| {'CG-52'if r['ship'].startswith('CG')else 'DDG-119'} | {r['meanBeforeMs']/1000:.2f} | {r['meanAfterMs']/1000:.2f} | {r['observedReductionPercent']:+.1f}% |"for r in l['summary'])
  (HERE/'PERFORMANCE.md').write_text(f'''# PERF_D 측정

최종 HTML {size:,}bytes SHA `{hs}`, main `{q['mainSha256']}`. 최종 원본 {n}/{n}PASS/{ns}suites, page/core/runtime/presentation 오류0. 형상 fixture의 3단계 정점·법선·색상·UV·index/group/bounds/binding exact와 취소/초기화를 확인했다. 형상 fixture의 generator 강제 완료 시간은 아래 성능 수치로 사용하지 않는다.

native RAF/WebGL에서 첫 attached cut/fold를 THREE renderer에 제출하기까지의 시간이다. seed1831565813, Chromium151.0.7922.173/Playwright1.62.0, SwiftShader/LOW/480×360, 자함만·항공기/구표적OFF, 물리 일시정지, diagnostic native Kh-32 dud structural hit1회(x12/z1.5/STARBOARD). 두 pass에서 함종별 AB/BA를 반대로 하고 두 번째 함종 순서를 뒤집었다. 다른 검사/타이밍 작업이 끝난 뒤 직렬 실행했다. 원본 피해/저장 상태와 RNG가 네 쌍 모두 정확히 같다. 후속 장식 대기 중 실제 완성된 구멍을 제출하는 것을 확인했다.

| 자함 | 이전 평균 s | 현재 평균 s | 관측 지연 감소 |
|---|---:|---:|---:|
{native}

이 값은 호스트의 소프트웨어 WebGL/대표 일회 피격 조건이다. 실제 GPU 완료·휴대폰 FPS·동시 다수 피격·자연 폭발 교전 속도 인증이 아니다. native frame의 렌더 간격이 길어 절대 초 단위 수치를 일반 기기에 적용할 수 없다. 최종 그을음·윤곽선·상세 변형은 기존 cooperative 작업으로 이어서 완성한다.

초기 x12/z4(갑판 주변),640×480 baseline 시험은240초 안에 첫 유효 actualHole 제출이 관측되지 않았다. 그동안199 draw/42589damage steps가 진행됐다. job phase/면 일치 audit를 함께 수집하지 않아 원인은 미확정이다. candidate까지 진행하지 못한 미완료 비교이며 이 개선율이나 PASS 집계에 포함하지 않는다. 당시 script/note는 not-counted-z4-*로 보존한다. 갑판 주변은 다음3D 부하 단계에서 면 일치와 job phase를 함께 확인해야 한다.

별도 밀집 미사일 비교는 이전과 같은 CG 자함/optional allyCG+enemyDDG, native Kh-32 helper16km·10000m·4방위, warm120+측정240 fixed ticks이다. 측정 트랙은 diagnostic workload다. 두 pass opposite AB/BA, 역순 조건, 16쌍 상태/RNG/entity exact를 확인하며 performance/profiler/기존 performance.now duration인 lastBuildMs/lastAssessmentMs만 제외한다. 모든 raw state는 보존한다.

| 물리 함정 | Kh-32 | 이전 ms/tick | 현재 ms/tick | 관측 CPU 감소 |
|---:|---:|---:|---:|---:|
{table}

작은 차이는 실행 변동일 수 있고 일부 증가도 표에 그대로 포함한다. 센서·피해·RNG·고정 주기·무기 결과를 바꾸지 않는 최적화이므로 모든 조건의 보편적 성능 개선을 주장하지 않는다. 원시 paired timings와 상태는 evidence/benchmark.json, state-*.json.gz, native-latency.json 및 captures다. GitHub Actions는 dispatch하지 않았다.
''')
  (ROOT/'AEGIS_PLAN_STATUS_v48_WIP_PERF_D.md').write_text(f'''# v48 WIP PERF_D

PERF_C final `5ddd05ce9358e9a23c11d26030bff05c6f18fa1d` 위 performance-d. HTML **{size:,}bytes**, SHA256 `{hs}`, main `{q['mainSha256']}`.

완료: CG/DDG 등록 단면의 중복 제거 임시 배열, 변형 경계 임시 벡터를 줄였다. 자함 첫 구멍/변형은 기존6ms frame allowance의 남은 시간을 사용하고, 전체 quick shape가 완성되면 그을음·윤곽선보다 먼저 한 번에 표시한다. 후속 장식·detail의 최종 형상과 physical damage/authority/RNG/fixed60/120/20Hz는 보존한다. publish 이후 취소가 live geometry를 dispose하지 않도록 소유권을 이전한다.

최종 원본 직접 **{n}/{n}PASS / {ns}suites**, 오류0. 형상 quick/detail/sealed exact·취소/초기화, 등록 layout3,072질의/convex384사례, 기존 모든 회귀 및 strict CG/DDG6조건·density16쌍 상태/RNG exact. native first render submission은 별도4쌍으로 측정했고 피해 상태/RNG exact다. [성능/조건](docs/performance/D/PERFORMANCE.md), [최종 증거](docs/performance/D/evidence/verification-summary.json), [계약/재현](docs/performance/D/README.md).

원본 packed2/13만 변경하고 등록 모델/envelope 원본 bytes는 보존했다. 직전 PERF_C HTML/status/SHA/manual workflow는 archive/v48/WIP_PERF_C에 samebytes/blob으로 이동했다. stablev48은 그대로다. 기존 §7.1 승인으로 full original upload·독립 원격 readback을 수행한다. Actions dispatch/CI PASS/main·선행 branch 병합/새PR 생성 없음.

다음은 실제3D/효과 전체 부하 최적화와 최종 재측정, 이후 헬기/초수평선 탐지 → RGM-109E Block Va다. 호스트 CPU/native software-render submission을 휴대폰/실제GPU FPS로 표현하지 않는다.
''')
  readme=ROOT/'README.md';text=readme.read_text();text=text.replace('## 최신 개발 기준 — 최적화 WIP PERF_C','## 직전 개발 기준 — 최적화 WIP PERF_C (당시 기록)',1)
  inst=ROOT/'AEGIS_PROJECT_INSTRUCTIONS.md';itext=inst.read_text();itext=itext.replace('### 최신 개발 기준 PERF_C — 최적화3단계','### 직전 개발 기준 PERF_C — 최적화3단계 (당시 기록)',1)
  for f in ['Aegis_SIM_v48_WIP_PERF_C.html','AEGIS_PLAN_STATUS_v48_WIP_PERF_C.md','SHA256SUMS_v48_WIP_PERF_C.txt']:
   text=text.replace(']('+f+')','](archive/v48/WIP_PERF_C/'+f+')');itext=itext.replace(']('+f+')','](archive/v48/WIP_PERF_C/'+f+')')
  block=f'''## 최신 개발 기준 — 최적화 WIP PERF_D

- [HTML]({q['candidate']}), **{size:,}bytes**, SHA `{hs}`.
- 피격 메쉬의 완성된 구멍·변형을 먼저 표시하고, 기존 frame 작업 예산의 남은 부분을 사용한다. 두 함종의 단면·변형 경계 계산 할당 비용도 줄였다. 최종 메쉬/물리 피해·RNG·주기·release guard는 유지한다.
- 최종 원본 **{n}/{n}PASS/{ns}suites**, 오류0. [상태](AEGIS_PLAN_STATUS_v48_WIP_PERF_D.md), [SHA](SHA256SUMS_v48_WIP_PERF_D.txt), [계약](docs/performance/D/README.md), [조건/성능](docs/performance/D/PERFORMANCE.md), [검증](docs/performance/D/evidence/verification-summary.json).
- performance-d full original upload/readback. Actions dispatch/main·선행 branch 병합/새PR 생성 없음. 다음은 실제3D/효과 부하와 최종 재측정 → 헬기/초수평선 → RGM-109E Block Va다.

''';readme.write_text(text.replace('## 직전 개발 기준 — 최적화 WIP PERF_C',block+'## 직전 개발 기준 — 최적화 WIP PERF_C',1))
  iblock=f'''### 최신 개발 기준 PERF_D — 최적화4단계

- 현재 v48_WIP_PERF_D, HTML {size:,}bytes SHA `{hs}`, main `{q['mainSha256']}`. PERF_C final `5ddd05ce9358e9a23c11d26030bff05c6f18fa1d` 위 performance-d. 현행 support/workflow/checksum은 PERF_D, 아래 이전 단계는 당시 기록이다.
- source sectional envelope의 기존 rounded-key/last-value/order/sort/convex 결과를 유지하면서 임시 배열을 줄인다. 변형 radial edge는 동일 scalar 산술이다. packed2/13만 변경하고 등록 모델·삼각형·envelope source bytes를 유지한다.
- 완성된 quick opening/fold snapshot을 atomic publish한 후 동일 generator로 scorch/outline을 완성한다. detail은 기존 동작. live geometry ownership을 publish 시 이전하며 cancellation finally는 미공개 작업만 dispose한다. reset/import/owner retirement가 기존 수명주기로 live geometry를 회수한다. presenter-only _damageOpeningRevisionPerfD는 snapshot/authority에 저장하지 않는다.
- 자함 quick은 다른 owner 이후 기존6ms allowance의 unused share를 빌린다. total allowance/다른 owner shares/detail slice/fixed60/120/20Hz 및 physics/damage/RNG/release/PERF_A/B/C caches를 보존한다. 기존 cooperative step overshoot 가능성은 남아 있다.
- 최종 원본 {n}/{n}PASS/{ns}suites, 오류0. 두 함종 geometry quick/detail/sealed bytes/index/groups/bounds/bindings와 cancel/reset, layout3,072/convex384 사례 exact. 전체 기존 회귀·six strict ownship 조건·density16쌍·native latency4쌍 state/RNG exact. 증거의 fixture와 실제 native RAF latency를 구별하고 host CPU/SwiftShader submission을 phone/hardwareGPU FPS로 표현하지 않는다.
- 이전 PERF_C 네 파일 samebytes/blob archive, stablev48 보존. §7.1 승인으로 full original 직접 upload/readback. Actions dispatch/CI PASS/main·선행 branch 병합/새PR 생성 없음. 다음은 실제3D/효과 최적화·최종 재측정, 그 뒤 헬기/초수평선 → RGM-109E Block Va다.

''';inst.write_text(itext.replace('### 직전 개발 기준 PERF_C',iblock+'### 직전 개발 기준 PERF_C',1))
  archive=ROOT/'archive/README.md';archive.write_text(archive.read_text()+'\n## WIP PERF_C 보존\n\n직전 verified PERF_C HTML/status/SHA/manual workflow 네 파일은 WIP_PERF_C에 samebytes/blob으로 이동했다. 해당 historical scripts/records는 당시 경로와 조건을 보존하며 현재 root/support/workflow는 PERF_D다.\n')
 q=json.loads((out/'verification-summary.json').read_text());assert q['candidateSha256']==hs
 status=ROOT/'AEGIS_PLAN_STATUS_v48_WIP_PERF_D.md';(ROOT/'SHA256SUMS_v48_WIP_PERF_D.txt').write_text(f"{hs}  {q['candidate']}\n{sha(status.read_bytes())}  {status.name}\n")
 paths={line[66:]for line in (ROOT/'docs/performance/C/REPOSITORY_SUPPORT.sha256').read_text().splitlines()};moves={f:'archive/v48/WIP_PERF_C/'+f for f in ['Aegis_SIM_v48_WIP_PERF_C.html','AEGIS_PLAN_STATUS_v48_WIP_PERF_C.md','SHA256SUMS_v48_WIP_PERF_C.txt']};moves['.github/workflows/performance-c.yml']='archive/v48/WIP_PERF_C/performance-c.yml';paths={moves.get(f,f)for f in paths}
 paths.update(['docs/performance/C/REPOSITORY_SUPPORT.sha256','docs/performance/C/evidence/remote-publication.json',q['candidate'],status.name,'SHA256SUMS_v48_WIP_PERF_D.txt','.github/workflows/performance-d.yml','README.md','AEGIS_PROJECT_INSTRUCTIONS.md','archive/README.md'])
 paths.update(str(f.relative_to(ROOT))for f in HERE.rglob('*')if f.is_file()and 'node_modules'not in f.parts and '__pycache__'not in f.parts and f.name not in ['REPOSITORY_SUPPORT.sha256','remote-publication.json'])
 (HERE/'REPOSITORY_SUPPORT.sha256').write_text(''.join(f'{sha((ROOT/f).read_bytes())}  {f}\n'for f in sorted(paths)));print(json.dumps({'pass':True,'checks':q['directChecks'],'suites':len(q['suites']),'supportFiles':len(paths),'sha256':hs}))
if __name__=='__main__':main()
