"""Generate a consistent handoff and checksums from passed final-byte evidence."""
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def support(q):
 oldPaths=[line[66:]for line in (ROOT/'docs/performance/A/REPOSITORY_SUPPORT.sha256').read_text().splitlines()]
 files=['Aegis_SIM_v48_WIP_PERF_A.html','AEGIS_PLAN_STATUS_v48_WIP_PERF_A.md','SHA256SUMS_v48_WIP_PERF_A.txt'];moves={f:'archive/v48/WIP_PERF_A/'+f for f in files};moves['.github/workflows/performance-a.yml']='archive/v48/WIP_PERF_A/performance-a.yml'
 paths={moves.get(f,f)for f in oldPaths};paths.update(['README.md','AEGIS_PROJECT_INSTRUCTIONS.md','archive/README.md',q['candidate'],'AEGIS_PLAN_STATUS_v48_WIP_PERF_B.md','SHA256SUMS_v48_WIP_PERF_B.txt','.github/workflows/performance-b.yml'])
 for f in HERE.rglob('*'):
  if not f.is_file()or any(x in ['node_modules','__pycache__']for x in f.parts)or f.name in ['REPOSITORY_SUPPORT.sha256','remote-publication.json']:continue
  paths.add(str(f.relative_to(ROOT)))
 for f in paths:assert (ROOT/f).is_file(),f
 (HERE/'REPOSITORY_SUPPORT.sha256').write_text('\n'.join(sha(ROOT/f)+'  '+f for f in sorted(paths))+'\n');return len(paths)
def main():
 p=argparse.ArgumentParser();p.add_argument('--checksums-only',action='store_true');a=p.parse_args();q=json.loads((HERE/'evidence/verification-summary.json').read_text());assert q['pass'];assert sha(ROOT/q['candidate'])==q['candidateSha256']
 n=q['directChecks'];ns=len(q['suites']);captures=len(q['captures']);hs=q['candidateSha256'];size=q['candidateBytes'];ms=q['mainSha256']
 if not a.checksums_only:
  table='\n'.join(f"| {r['fleet']} | {r['count']} | {r['meanBefore']:.2f} | {r['meanAfter']:.2f} | {r['observedReductionPercent']:.1f}% |"for r in q['benchmark']['summary'])
  (HERE/'PERFORMANCE.md').write_text(f'''# PERF_B 성능·검증 조건

최종 원본 {size:,}bytes, SHA `{hs}`, main `{ms}`. PERF_A와 PERF_B를 같은 호스트에서 직렬 비교했다. seed1831565813, Chromium151.0.7922.173/Playwright1.62.0, warm120+측정240 actual fixed ticks, 각2반복/AB·BA 교대/두 번째 조건 역순이다. 다른 회귀·profile 작업이 끝난 후 측정했다.

CG 자함, optional 아군CG+적DDG, 적 항공기/구표적함OFF, terrain bypass, native Kh-32 초기 수평거리16km·고도10000m·4방위다. helper 측정 트랙은 부하 fixture이며 자연 탐지 증거가 아니다. 16쌍 모두 저장/관측/무장/방어/EW 상태·entity 수·combatRNG를 exact 비교했다. performance/profiler 및 기존 방어 진단의 `performance.now()` duration인 lastBuildMs/lastAssessmentMs만 명시적으로 제외했다. 실제 시뮬레이션 시각·판단·발사·효과 값은 포함한다. 전체 raw 상태도 state-*.json.gz로 보존한다.

조건별 version order가 두 반복에서 같은 옛 runner 식을 original case index로 고쳤다. 정확한 첫 pass는 유지하고 두 번째는 각 조건에서 반대 순서로 다시 실행했다. 최종 표에는 반대순서 검사를 통과한 두 pass만 쓴다. 처음의 두 번째 pass·전체 report/source는 not-counted-original-order-*에 별도 보존한다. game HTML·fixture setup/measurement/state 함수는 이 보정에서 변경하지 않았다.

| 함정 수 | Kh-32 수 | PERF_A ms/tick 평균 | PERF_B ms/tick 평균 | 관측 CPU 시간 감소 |
|---:|---:|---:|---:|---:|
{table}

해당 호스트/대표 조건의 CPU 관측이며 사용자 휴대폰·하드웨어 GPU FPS 또는 보편적 개선율이 아니다. 64발에서 약10~11% 감소했으며 32발 평균은 약2~2.5% 증가했다. 32발 증가는 후속 SPY 최적화와 재측정에서 추적한다. 작은 차이는 측정 변동일 수 있다. 64발 비용과 SPY/피격/실제 가시 render의 비용이 남아 있다. profiler sensors_tracks_ew phase는 tick당2회이므로 calls로 가중한다. CDP 1ms sampling은 timing과 별도로 수행했다. 원본 샘플과 입력/SHA는 evidence/profile-a-* 및 profile-b-*를 따른다. inclusive 호출 시간은 겹치므로 더해서 전체 비율로 표현하지 않는다.

새 원본 직접 {n}/{n}PASS,{ns}suites/{captures}captures. 과거 결과 합산0, page/core/runtime/presentation 오류0. 독립 제어 사례96개에서 두 native planner의 계획·예약이 exact이고 새 ctx·current reservation·관측/pose/damage 변화와 기본 forecast 계약을 확인했다. frame의 모든 입력 변화·owner 분리·invalid throw·signed zero·canonical transform exact 및 실제 두 함종 core selftest를 확인했다.

CG/DDG idle/8Kh32AUTO/손상6조건의 EW/network/tactical/maneuver/attack/team 포함 상태/RNG exact, 세 owner1/8/16/64배속 결정성, 실제 VLS/RAM/Phalanx·채프/눌카/Harpoon·late actual-release guards·native RAF/WebGL 피격·UI/camera·저장/reset·기존 AI/공유를 새 원본에 직접 실행했다. 개별 native/natural fixture와 한계는 해당 report를 따른다. PERF_A 도색64모델 source texture1개·pixel/geometry parity와 수명도 유지했다. Actions는 dispatch하지 않았다.
''')
  (ROOT/'AEGIS_PLAN_STATUS_v48_WIP_PERF_B.md').write_text(f'''# AEGIS PLAN STATUS v48_WIP_PERF_B

## 현재 기준

- 최적화2단계 완료. PERF_A final `4b42aacd4271ce790b47b981b9a58dc960e5d5c5` 위 `performance-b`.
- HTML `{q['candidate']}`, {size:,}bytes, SHA-256 `{hs}`. decoded main `{ms}`.
- records0~12/모델 assets·stablev48 보존, records13만 변경. 직전 PERF_A4원본은 archive/v48/WIP_PERF_A/에 samebytes/blob 보존.

## 적용 내용

1. 동일 synchronous planner ctx 안에서 관측 threat/delay 예측과 SPG 기하 점수를 공유한다. NEZ에 필요 없는 track metadata 복사를 생략한다. 다음 build에는 새 ctx로 현재 관측/자세/피해/사통을 읽고, 예약 충돌은 매번 검사한다.
2. owner별 body frame을 모든 heading/heel/trim/draft/origin x/y/z가 Object.is exact일 때만 공유한다. 같은 tick의 자세 변경을 즉시 반영하며 canonical constructor/invalid 예외를 유지한다.

캐시는 derived only·snapshot 비저장이다. 실제 발사의 보호/권한/HOLD/EMCON/손상/capability·예비탄·FCS 재검사는 유지한다. fixed60/120/20Hz·sensor/CMS·AI/RNG·native flight/collision/damage·EW·CG Phalanx-only·DDG장비·Harpoon INS/ARH/DL0·조작과 PERF_A 최적화를 유지한다. 상세 계약은 docs/performance/B/README.md다.

## 검증

- 최종 원본 직접 {n}/{n}PASS,{ns}suites/{captures}captures, 과거·draft 결과 합산0, page/core/runtime/presentation 오류0.
- full packing/rebuild/scope, 두 native planner96제어사례·ctx 수명/예약/현재 관측/자세/피해·기본 반환 계약·frame exact inputs/core selftest.
- strict CG/DDG6조건 상태/RNG exact, 기존26 H4A browser suites와 PERF_A texture lifecycle 새 원본 직접 재검사, 세 owner1/8/16/64배속exact·native 방어/피해/저장/UI 회귀.
- 별도 직렬 CPU16쌍 상태·RNG·entity exact. 표/반복/조건/한계는 docs/performance/B/PERFORMANCE.md 및 evidence/benchmark.json, script/report/capture SHA/집계는 evidence/verification-summary.json이 권위다.

## 업로드·후속

사용자 full original 직접 업로드/readback 승인으로 새 branch에 원본/support를 반영한다. 독립 remote tree/blob/raw bytes 확인은 docs/performance/B/evidence/remote-publication.json이 code commit을 pin하고 자기 자신을 checksum에서 제외한다. 이후 final-head도 별도 확인한다. Actions 계정 제한으로 manual workflow만 준비하며 dispatch/CI PASS 주장은 없다. main/이전PR 병합·새PR 생성은 실행하지 않는다.

다음은 SPY 관측 연관 최적화, 피격 envelope 지연, 실제 가시3D/효과와 최종 재측정이다. 그 뒤 헬기/초수평선 탐지 → RGM-109E Block Va를 유지한다. 대표 조건 밖 보편적 요격률·모든 오격 방지·하드웨어 FPS 보장은 포함하지 않는다.
''')
  readme=ROOT/'README.md';text=readme.read_text();assert '## 최신 개발 기준 — 최적화 WIP PERF_B'not in text
  text=text.replace('## 최신 개발 기준 — 최적화 WIP PERF_A','## 직전 개발 기준 — 최적화 WIP PERF_A (당시 기록)',1)
  for f in ['Aegis_SIM_v48_WIP_PERF_A.html','AEGIS_PLAN_STATUS_v48_WIP_PERF_A.md','SHA256SUMS_v48_WIP_PERF_A.txt']:text=text.replace(']('+f+')','](archive/v48/WIP_PERF_A/'+f+')')
  block=f'''## 최신 개발 기준 — 최적화 WIP PERF_B

- [HTML]({q['candidate']}), **{size:,}bytes**, SHA `{hs}`.
- 교전 판단 내 관측 예측/SPG 기하 공유와 exact owner 자세의 body frame 재사용. 실제 예약·발사 재검사와 기존 물리/센서/AI/RNG/피해를 유지한다.
- 최종 원본 **{n}/{n}PASS /{ns}suites**, 오류0. strict CG/DDG6조건과 직렬16쌍 상태/RNG exact. [성능·조건](docs/performance/B/PERFORMANCE.md), [상태](AEGIS_PLAN_STATUS_v48_WIP_PERF_B.md), [SHA](SHA256SUMS_v48_WIP_PERF_B.txt), [계약](docs/performance/B/README.md), [직접 검증](docs/performance/B/evidence/verification-summary.json).
- PERF_A final 위 `performance-b`, full original 직접 upload·독립 readback. Actions dispatch/병합/새PR 생성 없음. 다음은 SPY 관측 연관 최적화, 이후 피격/3D·최종 재측정 → 헬기/초수평선 → RGM-109E Block Va다.

'''
  readme.write_text(text.replace('## 직전 개발 기준 — 최적화 WIP PERF_A',block+'## 직전 개발 기준 — 최적화 WIP PERF_A',1))
  inst=ROOT/'AEGIS_PROJECT_INSTRUCTIONS.md';text=inst.read_text();assert '### 최신 개발 기준 PERF_B'not in text;text=text.replace('### 최신 개발 기준 PERF_A — 최적화1단계','### 직전 개발 기준 PERF_A — 최적화1단계 (당시 기록)',1)
  block=f'''### 최신 개발 기준 PERF_B — 최적화2단계

- 현재 세트 v48_WIP_PERF_B, HTML {size:,}bytes SHA `{hs}`, main `{ms}`. PERF_A final `4b42aacd4271ce790b47b981b9a58dc960e5d5c5` 위 performance-b. 현행 support/workflow/checksum은 PERF_B, 아래 PERF_A 이하는 당시 기록이다.
- 두 native lexical planner의 build-local ctx에서 같은 threat/delay forecast와 SPG 기하 점수를 재사용하고 unused track metadata 복사를 생략한다. 다음 판단의 현재 sensor/pose/damage/firecontrol과 매회 current reservation 충돌 검사는 유지한다. 실제 발사에 이 cache를 넘기지 않으며 권한/FRIEND/NEUTRAL/HOLD/EMCON/damage/capability/FCS/예비탄 재검사를 유지한다.
- owner별 body frame은 heading/heel/trim/draft/origin xyz 전부 Object.is exact일 때만 재사용한다. current snapshot/항법 읽기·canonical constructor/invalid 예외를 유지하고 same-tick 변화도 즉시 반영한다. 캐시는 파생값·snapshot 비저장, fixed60/120/20Hz·RNG·무장·피해·EW·AI·Harpoon DL0와 PERF_A 최적화를 유지한다.
- 새 원본 직접 {n}/{n}PASS/{ns}suites/{captures}captures, 오류0. planner96제어사례, exact frame transitions/두 함종 core, CG/DDG6조건·직렬16쌍 상태/RNG·entity exact와 기존26 H4A browser suites/native 방어/피해/UI·세 owner1/8/16/64를 확인했다. counts/SHA/조건/한계는 PERF_B evidence를 따른다.
- PERF_A 네 원본 samebytes/blob과 stablev48/assets0~12 보존. §7.1 직접 원본 upload/readback 승인 유지, Actions dispatch/CI PASS/main·선행PR 병합/새PR 생성 없음. 다음은 SPY 관측 연관 → 피격 envelope → 실제 render·최종 재측정이며 이후 헬기/초수평선 → RGM-109E Block Va다. host CPU를 휴대폰/실제GPU FPS로 표현하지 않는다.

'''
  inst.write_text(text.replace('### 직전 개발 기준 PERF_A',block+'### 직전 개발 기준 PERF_A',1))
  archive=ROOT/'archive/README.md';text=archive.read_text();archive.write_text(text.replace('PERF_A의 직전 H4A','PERF_B의 직전 PERF_A HTML/status/SHA/workflow는 `v48/WIP_PERF_A/`에 원래 bytes/blob으로 보존한다. PERF_A support/evidence는 `docs/performance/A/`에 유지하고 현재 검증/workflow는 `docs/performance/B/`다.\n\n당시 PERF_A의 직전 H4A',1).replace('현재 검증·workflow 기준은 `docs/performance/A/`다.','당시 검증·workflow 기준은 `docs/performance/A/`였다.'))
 (ROOT/'SHA256SUMS_v48_WIP_PERF_B.txt').write_text('\n'.join(sha(ROOT/f)+'  '+f for f in [q['candidate'],'AEGIS_PLAN_STATUS_v48_WIP_PERF_B.md'])+'\n')
 print(json.dumps({'checks':n,'htmlSha256':hs,'supportFiles':support(q),'statusSha256':sha(ROOT/'AEGIS_PLAN_STATUS_v48_WIP_PERF_B.md')}))
if __name__=='__main__':main()
