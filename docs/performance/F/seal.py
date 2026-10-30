"""Seal only final-F original reports and isolated native timings."""
import argparse,gzip,hashlib,json,shutil
from pathlib import Path
from suite_catalog import SUITES,ROOT
HERE=Path(__file__).resolve().parent
BASE='bd8962011a16cfeb4158670d3e562a92e0a52ff4'
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('scratch',type=Path);p.add_argument('--checksums-only',action='store_true');a=p.parse_args();out=HERE/'evidence';out.mkdir(exist_ok=True);html=ROOT/'Aegis_SIM_v48_WIP_PERF_F.html';hs=sha(html.read_bytes())
 if not a.checksums_only:
  rows=[];captures=[]
  for name,(script,filename)in {'static':('docs/performance/F/verify_static.py','static.json'),**SUITES}.items():
   f=a.scratch/'final'/name/filename;raw=f.read_bytes();q=json.loads(raw);assert q['pass']and not q.get('errors'),name;tested=q.get('sha256',q.get('candidateSha256',q.get('htmlSha256')));assert tested==hs,(name,tested)
   groups=[q['checks']]if 'checks'in q else[c['checks']for c in q['cases']];assert all(v is True for g in groups for v in g.values()),name
   target=name+'.json'+('.gz'if len(raw)>30000 else '');data=gzip.compress(raw,9,mtime=0)if target.endswith('.gz')else raw;(out/target).write_bytes(data);rows.append({'suite':name,'checks':sum(len(g)for g in groups),'pass':True,'testedHtmlSha256':hs,'script':script,'scriptSha256':sha((ROOT/script).read_bytes()),'report':target,'reportSha256':sha(data)})
   for f in sorted(f.parent.glob('*.png')):
    target=name+'-'+f.name;shutil.copyfile(f,out/target);captures.append({'path':target,'sha256':sha(f.read_bytes())})
   if name=='endurance':
    for f in f.parent.glob('*.json.gz'):shutil.copyfile(f,out/f.name)
  raw=(a.scratch/'native-queue/native-queue.json').read_bytes();t=json.loads(raw);assert t['pass']and not t['errors']and t['sha256']==hs;data=gzip.compress(raw,9,mtime=0);(out/'native-queue.json.gz').write_bytes(data)
  for f in(a.scratch/'native-queue').glob('*.png'):shutil.copyfile(f,out/f.name)
  shutil.copyfile(a.scratch/'reproduction.json',out/'reproduction-e.json')
  shutil.copyfile(a.scratch/'retirement-e.json',out/'retirement-e.json')
  (out/'excluded-partial-verification.json').write_text(json.dumps({'additionalExcludedCandidate':'f037dd6e298ac5bcc2339aac37bec0cd56af760171158d10bd92f8de4f98dbae','additionalReason':'Functional ownership guard exposed DDG shared factory maps; replaced generic disposal with explicit CG per-presenter ownership. All preliminary checks excluded.','sha256':'791990594e4cb46e330754e056bc1edced0ccf014412d2c39fcd3ba3084d41e1','reason':'Queue-only preliminary original partial runner stopped after reproduced CG chain texture retirement omission; every final suite rerun on final ownership-scoped original. Preliminary checks/timings not included.'},indent=2)+'\n')
  manifest=json.loads((a.scratch/'perf-f.manifest.json').read_text());n=sum(r['checks']for r in rows);summary={'schema':'AEGIS_PERFORMANCE_F_FINAL_ORIGINAL','candidateSha256':hs,'candidateBytes':html.stat().st_size,'mainSha256':manifest['mainSha256'],'baselineCommit':BASE,'directChecks':n,'suites':rows,'captures':captures,'nativeTiming':{'report':'native-queue.json.gz','sha256':sha(data),'summary':t['summary']},'pass':True,'errors':0,'limits':t['limits']+' Endurance is120 simulated seconds per profile, not real-hour soak. No CI dispatch/main merge/PR.'};(out/'verification-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
  table='\n'.join(f"| {r['ship']} | {r['meanBeforeMs']/1000:.3f} | {r['meanAfterMs']/1000:.3f} | {r['observedReductionPercent']:.1f}% |"for r in t['summary'])
  (HERE/'PERFORMANCE.md').write_text(f'''# PERF_F 최종 검증 결과

최종 HTML SHA `{hs}`. 원본 {n}/{n} PASS, {len(rows)} suites, 오류0. CG 체인 텍스처의 owner retirement 누락도 보완했다. E에서 unique texture1/dispose0을 재현했고 F는 per-presenter ownedTextures Set으로 한 번 해제하며 DDG 공유 factory textures는 유지한다.

## 두 번째 피격 표시

E/F 원본 native RAF/THREE/SwiftShader LOW640×480에서 x12/z4 첫 구멍의 실제 anchor 제출 직후 x25/z4 두 번째 detached 피격을 추가했다. 두 함종 각2회, 반대 AB/BA, 총4쌍/8pages, 전체 회귀/카메라 종료 후 직렬이다. job drainage/fake clock 없음. 현재6ms render allowance와 fixed simulation은 그대로다. 실제 cut keys·GL0·physical snapshot/RNG 고정을 확인했다.

| 자함 | E 두 번째 cut 제출 평균 초 | F 평균 초 | 관측 지연 감소 |
|---|---:|---:|---:|
{table}

이 값은 host CPU submission 시간이다. hardware GPU 완료나 phone FPS가 아니다. 첫 actual anchor 다음 새 피격을 넣는 제어 조건이므로 모든 피격 위치·자연 다발 피격 성능을 일반화하지 않는다. 완료 후 최종 geometry는 별도 original THREE fixture에서 exact다.

## 부하와 자원

두 함종 각각24×300 =7200fixed ticks(120 simulated seconds), 세 함정, CG64/DDG16native Kh32 diagnostic workload에서 E/F 각24개 전체 authoritative snapshot, RNG/entity counts를 비교한다. host performance/profiler/lastBuildMs/lastAssessmentMs만 제외하고 raw states를 보존한다. post-GC JS heap은 계측 범위에서 급증하지 않는지 확인한다. 실제 수시간 플레이·VRAM 측정은 아니다. 기능 검사의 소요 시간은 성능 수치로 사용하지 않는다.

Native import/reset 8회×2함종에서1200smoke와4Kh32의 실제 GPU geometry/texture 회수, pool/maps 청소, warm-up 이후 GPU resource count를 확인한다. pending quick-cut 외부 함정의 실제 runtime replacement 후 presenter/root/originals/live geometry가 dispose되는지 확인한다. combat sinking 자체 시험은 아니다.

## 누적 최적화 수치의 기준

현재 F는 표시용 queue 선점과 CG 전용 텍스처 회수만 바꿨고 physics CPU·연기shader/model은 E와 같다. [E의 직접 H4A→E 누적 측정](../E/PERFORMANCE.md)은 당시 최종 E 원본의 기록으로 유지한다. F를 다시 누적 측정했다고 주장하지 않는다. 그 기록의64발 host CPU 감소는 자함34.8%, 세 함정42.7%였으며 일부 idle 조건은 증가했다. 단계별 개선율은 더하지 않는다.

계획한 마지막 최적화 검증 범위는 완료했다. 실제 장치 FPS/수시간 soak는 미실행이다. 다음 기능은 헬기/초수평선 탐지, 이후 RGM-109E Block Va다. Actions dispatch/CI PASS 주장은 없다.
''')
  status=f'''# v48 WIP PERF_F

PERF_E final `{BASE}` 위 performance-f. HTML **{html.stat().st_size:,}bytes**, SHA256 `{hs}`, main `{manifest['mainSha256']}`.

완료: 연속 피격에서 완성된 anchor 공개 뒤의 주변 quick 작업을 선점하여 최신 구멍을 먼저 처리한다. 미공개 anchor job은 선점하지 않아 starvation을 막는다. 현재 budget/완료 후 cut/fold/scorch/edges/detail과 live/original ownership을 보존한다. 외부CG presenter가 소유한 chain texture 한 장도 retirement에서 해제한다. packed13 표시용 scheduler와 texture disposal만 변경; 모델/physics/피해/센서/AI/RNG/60/120/20Hz와 actual release 유지.

최종 원본 {n}/{n} PASS/{len(rows)} suites, 오류0. 전체 교전·EW/network·세owner1/8/16/64·양함종·strict state/RNG·native WebGL·UI/카메라·save/preflight/import/reset, 연속3회 형상/큐,120초simulation 부하,8회GPU recovery와 pending-cut foreign owner replacement 포함. 별도 직렬 native4쌍의 실제 두 번째cut 제출 시간은 [성능](docs/performance/F/PERFORMANCE.md); 전체 증거 [검증](docs/performance/F/evidence/verification-summary.json).

제어된 detached scar/seeded track fixture이며 자연 다발 피격·실제 수시간 soak/hardware·phone FPS를 인증하지 않는다. E의 누적CPU 기록은 당시E검증으로 유지한다.

E 네 파일은 archive/v48/WIP_PERF_E에 samebytes/blob 보존. stablev48/이전 증거 유지. §7.1 full original 직접 upload·독립 readback. Actions dispatch/main·선행 branch merge/새PR 없음.

계획한 최적화 최종 검증 범위 완료. 다음은 헬기/초수평선 탐지 → RGM-109E Block Va다.
''';(ROOT/'AEGIS_PLAN_STATUS_v48_WIP_PERF_F.md').write_text(status)
  for file,oldheading,newheading in [('README.md','## 최신 개발 기준 — 최적화 WIP PERF_E','## 직전 개발 기준 — 최적화 WIP PERF_E (당시 기록)'),('AEGIS_PROJECT_INSTRUCTIONS.md','### 최신 개발 기준 PERF_E — 최적화5단계','### 직전 개발 기준 PERF_E — 최적화5단계 (당시 기록)')]:
   path=ROOT/file;text=path.read_text().replace(oldheading,newheading,1)
   for f in ['Aegis_SIM_v48_WIP_PERF_E.html','AEGIS_PLAN_STATUS_v48_WIP_PERF_E.md','SHA256SUMS_v48_WIP_PERF_E.txt']:text=text.replace(']('+f+')','](archive/v48/WIP_PERF_E/'+f+')')
   heading='## 최신 개발 기준 — 최적화 WIP PERF_F'if file=='README.md'else'### 최신 개발 기준 PERF_F — 최종 최적화 검증'
   block=f'''{heading}

- 현재 [HTML](Aegis_SIM_v48_WIP_PERF_F.html), {html.stat().st_size:,}bytes, SHA `{hs}`, main `{manifest['mainSha256']}`. PERF_E final `{BASE}` 위 performance-f. 현재 support/workflow/checksum은 F, 이전 문장은 당시 기록이다.
- complete anchor 공개 이후에만 remaining quick work를 최신 피격으로 선점한다. unpublished opening은 보호하고 live/original buffers를 유지한다. 안정된 입력의 최종 형상·현재6ms budget·physics/피해/sensors/AI/RNG/fixed60/120/20Hz/actual release와 이전 캐시/모델/연기 결과는 보존한다. packed13 표시용 scheduler와 texture disposal만 수정한다.
- 최종 원본 {n}/{n}PASS/{len(rows)}suites, 오류0. [상태](AEGIS_PLAN_STATUS_v48_WIP_PERF_F.md), [SHA](SHA256SUMS_v48_WIP_PERF_F.txt), [계약](docs/performance/F/README.md), [성능/한계](docs/performance/F/PERFORMANCE.md), [검증](docs/performance/F/evidence/verification-summary.json).
- 기존 전체 회귀와 연속3회 cut/queue, 양함종 각각120simulated seconds/7200ticks의 세 함정 overload exact state/RNG,8회nativeGPU smoke/Kh32 epoch와pending-cut 외부 함정owner replacement/disposal 검증. 전체 회귀/카메라 종료 후 native second-hit submit4쌍 직렬 AB/BA. 제어된 detached scar/diagnostic tracks이며 자연 다발 피격·실제 수시간 soak·hardware/phone FPS는 미실행이다. 누적CPU는 E 당시기록을 참조하며 새 F측정으로 표현하지 않는다.
- E 네 파일 samebytes/blob archive, stable와 이전 증거 유지. §7.1 full original 직접 upload/독립 remote readback. Actions dispatch/main·선행 branch merge/새 PR 없음.
- 계획한 최종 최적화 검증 범위 완료. 다음은 헬기/초수평선 탐지 → RGM-109E Block Va다.

''';path.write_text(text.replace(newheading,block+newheading,1))
  archive=ROOT/'archive/README.md';archive.write_text(archive.read_text()+'\n## WIP PERF_E 보존\n\n직전 E HTML/status/SHA/manual workflow 네 파일은 WIP_PERF_E에 samebytes/blob 보존. 현재root/support/workflow는 PERF_F다.\n')
 q=json.loads((out/'verification-summary.json').read_text());assert q['candidateSha256']==hs;status=ROOT/'AEGIS_PLAN_STATUS_v48_WIP_PERF_F.md';(ROOT/'SHA256SUMS_v48_WIP_PERF_F.txt').write_text(f'{hs}  {html.name}\n{sha(status.read_bytes())}  {status.name}\n')
 paths={line[66:]for line in(ROOT/'docs/performance/E/REPOSITORY_SUPPORT.sha256').read_text().splitlines()};moves={f:'archive/v48/WIP_PERF_E/'+f for f in ['Aegis_SIM_v48_WIP_PERF_E.html','AEGIS_PLAN_STATUS_v48_WIP_PERF_E.md','SHA256SUMS_v48_WIP_PERF_E.txt']};moves['.github/workflows/performance-e.yml']='archive/v48/WIP_PERF_E/performance-e.yml';paths={moves.get(f,f)for f in paths};paths.update(['docs/performance/E/REPOSITORY_SUPPORT.sha256','docs/performance/E/evidence/remote-publication.json',html.name,status.name,'SHA256SUMS_v48_WIP_PERF_F.txt','.github/workflows/performance-f.yml','README.md','AEGIS_PROJECT_INSTRUCTIONS.md','archive/README.md']);paths.update(str(f.relative_to(ROOT))for f in HERE.rglob('*')if f.is_file()and 'node_modules'not in f.parts and '__pycache__'not in f.parts and f.name not in ['REPOSITORY_SUPPORT.sha256','remote-publication.json']);(HERE/'REPOSITORY_SUPPORT.sha256').write_text(''.join(f'{sha((ROOT/f).read_bytes())}  {f}\n'for f in sorted(paths)));print(json.dumps({'pass':True,'checks':q['directChecks'],'suites':len(q['suites']),'supportFiles':len(paths),'sha256':hs}))
if __name__=='__main__':main()
