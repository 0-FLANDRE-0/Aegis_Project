"""Create the PERF_C handoff/checksums from fresh final-original evidence."""
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def support(q):
 paths={line[66:]for line in (ROOT/'docs/performance/B/REPOSITORY_SUPPORT.sha256').read_text().splitlines()}
 moves={f:'archive/v48/WIP_PERF_B/'+f for f in ['Aegis_SIM_v48_WIP_PERF_B.html','AEGIS_PLAN_STATUS_v48_WIP_PERF_B.md','SHA256SUMS_v48_WIP_PERF_B.txt']};moves['.github/workflows/performance-b.yml']='archive/v48/WIP_PERF_B/performance-b.yml';paths={moves.get(f,f)for f in paths}
 paths.update(['docs/performance/B/REPOSITORY_SUPPORT.sha256','docs/performance/B/evidence/remote-publication.json','README.md','AEGIS_PROJECT_INSTRUCTIONS.md','archive/README.md',q['candidate'],'AEGIS_PLAN_STATUS_v48_WIP_PERF_C.md','SHA256SUMS_v48_WIP_PERF_C.txt','.github/workflows/performance-c.yml'])
 for f in HERE.rglob('*'):
  if not f.is_file()or any(x in ['node_modules','__pycache__']for x in f.parts)or f.name in ['REPOSITORY_SUPPORT.sha256','remote-publication.json']:continue
  paths.add(str(f.relative_to(ROOT)))
 for f in paths:assert (ROOT/f).is_file(),f
 (HERE/'REPOSITORY_SUPPORT.sha256').write_text('\n'.join(sha(ROOT/f)+'  '+f for f in sorted(paths))+'\n');return len(paths)
def main():
 p=argparse.ArgumentParser();p.add_argument('--checksums-only',action='store_true');a=p.parse_args();q=json.loads((HERE/'evidence/verification-summary.json').read_text());assert q['pass']and sha(ROOT/q['candidate'])==q['candidateSha256']
 n=q['directChecks'];ns=len(q['suites']);captures=len(q['captures']);hs=q['candidateSha256'];size=q['candidateBytes'];ms=q['mainSha256']
 if not a.checksums_only:
  table='\n'.join(f"| {r['fleet']} | {r['count']} | {r['meanBefore']:.2f} | {r['meanAfter']:.2f} | {r['observedReductionPercent']:.1f}% |"for r in q['benchmark']['summary'])
  (HERE/'PERFORMANCE.md').write_text(f'''# PERF_C 성능·검증 조건

최종 원본 {size:,}bytes, SHA `{hs}`, decoded main `{ms}`. PERF_B와 PERF_C를 같은 호스트에서 직렬 비교했다. seed1831565813, Chromium151.0.7922.173/Playwright1.62.0, warm120+측정240 actual fixed ticks, 2반복이며 각 조건의 두 pass가 AB/BA 반대 순서다. 두 번째에는 조건 순서도 뒤집는다. 다른 회귀·profile 작업이 끝난 후 측정했다.

CG 자함, optional 아군CG+적DDG, 적 항공기/구표적함OFF, terrain bypass, native Kh-32 초기 수평거리16km·고도10000m·4방위다. helper 측정 트랙은 부하 fixture이며 자연 탐지 증거가 아니다. 16쌍 모두 관측/저장/무장/방어/EW 상태·entity 수·combatRNG를 exact 비교한다. performance/profiler 및 기존 performance.now() duration인 lastBuildMs/lastAssessmentMs만 명시 제외하고 full raw state도 보존한다. 실제 시뮬레이션 시각·연관·판단·발사·효과는 포함한다.

| 함정 수 | Kh-32 수 | PERF_B ms/tick 평균 | PERF_C ms/tick 평균 | 관측 CPU 시간 감소 |
|---:|---:|---:|---:|---:|
{table}

해당 호스트/대표 조건의 CPU 관측이며 휴대폰/하드웨어 GPU FPS 또는 보편적 개선율이 아니다. 이번8조건 평균은 모두 감소했다. 0~8발 조건의 작은 차이는 실행 변동일 수 있다. PERF_B의 32발 약2~2.5% 증가는 당시 A/B 비교값이고 이번 표는 새 B/C 비교다. 서로 다른 실행의 절대 시간을 누적 성능율로 합산하지 않는다. profiler sensors_tracks_ew phase는 tick당2회이므로 calls로 가중한다. 별도 CDP 1ms profile은 inclusive 호출이 겹쳐 전체 비율로 합산하지 않는다.

최종 원본 직접 {n}/{n}PASS,{ns}suites/{captures}captures, 과거·draft 결과 합산0, page/core/runtime/presentation 오류0. native NIS231사례에서 number exact·filter state exact를 확인했다. 상태6개/공분산36개 제자리 변경, 센서 위치·속도6개, 측정 오차4개, signed zero·invalid/fallback·canonical 갱신/거부 후 재연관, 36/64/96/180 게이트 양측과 실제 두 함종 core를 확인했다. 이 VM 의존성 제어는 자연 탐지나 요격률 인증이 아니다. 반복32관측의 native matrix multiply64→2는 동일 입력 제어 사례의 작업 감소이며 전체 게임 개선율이 아니다.

CG/DDG idle/8Kh32AUTO/손상6조건의 EW/network/tactical/maneuver/attack/team 포함 상태/RNG exact, 세 owner1/8/16/64배속, 실제 VLS/RAM/Phalanx·채프/눌카/Harpoon·actual release guards·native RAF/WebGL 피격·UI/camera·저장/reset·AI/공유를 새 원본에 직접 실행했다. 기존 PERF_A texture/canvas/lifecycle와 PERF_B planner/frame 계약도 재검사했다. 각 native/natural fixture의 조건·한계는 해당 raw report를 따른다. Actions dispatch는 없다.
''')
  (ROOT/'AEGIS_PLAN_STATUS_v48_WIP_PERF_C.md').write_text(f'''# AEGIS PLAN STATUS v48_WIP_PERF_C

## 현재 기준

- 최적화3단계 완료. PERF_B final `d26e94194d52f0040f4d3d388b9bbce49460b440` 위 `performance-c`.
- HTML `{q['candidate']}`, {size:,}bytes, SHA-256 `{hs}`. decoded main `{ms}`.
- records0~12/모델 assets·stablev48 보존, records13만 변경. 직전 PERF_B HTML/status/SHA/workflow 네 원본은 `archive/v48/WIP_PERF_B/`에 같은 bytes/blob으로 보존한다.

## 적용 내용

SPY 공통 대공 NIS 연관에서 트랙별 prediction/Jacobian/공분산 투영과 동일 오차 역행렬을 재사용한다. 상태6·공분산36·센서 위치/속도6·오차4를 exact 비교한다. 제자리 배열 변경/같은 tick 변화도 즉시 반영하며 측정 innovation은 매번 다시 계산한다. native 행렬/NIS 연산 순서는 유지한다.

캐시는 파생값·트랙 객체별 last1·WeakMap·snapshot 비저장이다. truth 접근이나 권한 캐시가 없다. canonical EKF prediction/correction·수상 연관·plot 생성/난수·focused/global 배정/게이트·실제 release guards와 fixed60/120/20Hz·physics/damage/EW/AI·Harpoon INS/ARH/DL0·CG/DDG 장비/조작·PERF_A/B 최적화를 유지한다.

## 검증

- 최종 원본 직접 {n}/{n}PASS,{ns}suites/{captures}captures, 과거·draft 결과 합산0, page/core/runtime/presentation 오류0.
- full packing/rebuild/syntax/scope·원본 native 갱신/배정/기존 cache/release source 보존·NIS231차등 사례/입력·게이트 경계·CG/DDG core.
- strict CG/DDG6조건과 직렬 CPU16쌍 상태/RNG/entity exact, 기존 함대·방어·피해·저장·UI/3D·세 owner1/8/16/64 회귀.
- 집계·입력·script/report/capture SHA는 `docs/performance/C/evidence/verification-summary.json`, CPU 조건/증가·감소/한계는 `docs/performance/C/PERFORMANCE.md`가 기준이다.

## 업로드·후속

§7.1 사용자 원본 직접 업로드/readback 승인을 유지한다. `docs/performance/C/evidence/remote-publication.json`은 code/support commit을 pin하고 자기 checksum에서 제외한다. proof-only commit 뒤 final-head도 따로 읽어 확인한다. Actions 계정 제한으로 manual workflow만 준비하며 dispatch/CI PASS 주장은 없다. main/선행PR 병합·새PR 생성은 이 단계에 포함하지 않는다.

다음은 피격 envelope의 convex/sort 지연 최적화, 실제 가시3D/효과·최종 재측정이다. 그 뒤 헬기/초수평선 탐지 → RGM-109E Block Va를 유지한다. 대표 조건 밖 모든 오격 방지·요격률·자연 장거리 획득·실제 doctrine·휴대폰 FPS 인증을 완료로 주장하지 않는다.
''')
  readme=ROOT/'README.md';text=readme.read_text();assert '## 최신 개발 기준 — 최적화 WIP PERF_C'not in text;text=text.replace('## 최신 개발 기준 — 최적화 WIP PERF_B','## 직전 개발 기준 — 최적화 WIP PERF_B (당시 기록)',1)
  for f in ['Aegis_SIM_v48_WIP_PERF_B.html','AEGIS_PLAN_STATUS_v48_WIP_PERF_B.md','SHA256SUMS_v48_WIP_PERF_B.txt']:text=text.replace(']('+f+')','](archive/v48/WIP_PERF_B/'+f+')')
  block=f'''## 최신 개발 기준 — 최적화 WIP PERF_C

- [HTML]({q['candidate']}), **{size:,}bytes**, SHA `{hs}`.
- SPY NIS 연관의 exact 트랙 상태/공분산/센서 원점 계산 재사용. 측정 innovation·native EKF 갱신·배정/게이트·발사권한·RNG/물리/피해는 유지한다.
- 최종 원본 **{n}/{n}PASS /{ns}suites**, 오류0. NIS231사례·CG/DDG6조건과 직렬16쌍 상태/RNG exact. [성능·조건](docs/performance/C/PERFORMANCE.md), [상태](AEGIS_PLAN_STATUS_v48_WIP_PERF_C.md), [SHA](SHA256SUMS_v48_WIP_PERF_C.txt), [계약](docs/performance/C/README.md), [직접 검증](docs/performance/C/evidence/verification-summary.json).
- PERF_B final 위 `performance-c`, full original 직접 upload·독립 readback. Actions dispatch/main·선행PR 병합·새PR 생성 없음. 다음은 피격 envelope → 실제 render·최종 재측정 → 헬기/초수평선 → RGM-109E Block Va다.

''';readme.write_text(text.replace('## 직전 개발 기준 — 최적화 WIP PERF_B',block+'## 직전 개발 기준 — 최적화 WIP PERF_B',1))
  inst=ROOT/'AEGIS_PROJECT_INSTRUCTIONS.md';text=inst.read_text();assert '### 최신 개발 기준 PERF_C'not in text;text=text.replace('### 최신 개발 기준 PERF_B — 최적화2단계','### 직전 개발 기준 PERF_B — 최적화2단계 (당시 기록)',1)
  block=f'''### 최신 개발 기준 PERF_C — 최적화3단계

- 현재 세트 v48_WIP_PERF_C, HTML {size:,}bytes SHA `{hs}`, main `{ms}`. PERF_B final `d26e94194d52f0040f4d3d388b9bbce49460b440` 위 performance-c. 현행 support/workflow/checksum은 PERF_C, 아래 PERF_B 이하는 당시 기록이다.
- SPY 공통 대공 NIS의 prediction/Jacobian/공분산 투영·동일 오차 역행렬만 캐시한다. 트랙 객체별 WeakMap last1, 상태6·공분산36·센서 위치/속도6·오차4 exact 비교로 in-place/same-tick 변경도 즉시 반영한다. 측정 innovation은 매번 현재값, native 산술·행렬/NIS 합산 순서를 유지한다.
- 캐시는 파생값·snapshot 비저장이며 truth/권한/시간 기반 cache가 아니다. native EKF 예측/갱신·수상 연관·plot 생성/난수·focused/global 배정/게이트·actual release source와 fixed60/120/20Hz·물리/피해/EW/AI/Harpoon DL0·PERF_A/B 최적화를 유지한다.
- 최종 원본 직접 {n}/{n}PASS/{ns}suites/{captures}captures, 오류0. NIS231차등/전체 입력 제자리 변화·오차·signed zero/invalid·갱신/거부·게이트 경계, 두 함종 core, strict CG/DDG6조건/직렬16쌍 상태/RNG/entity exact와 기존 native/browser/세 owner1/8/16/64를 확인했다. 집계/SHA/조건/한계는 PERF_C evidence를 따른다.
- PERF_B 네 원본 samebytes/blob·stablev48/assets0~12 보존. §7.1 승인에 따라 full original 직접 upload/readback, Actions dispatch/CI PASS/main·선행PR 병합/새PR 생성 없음. 다음은 피격 envelope → 실제 render·최종 재측정이며 이후 헬기/초수평선 → RGM-109E Block Va다. host CPU를 휴대폰/실제GPU FPS로 표현하지 않는다.

''';inst.write_text(text.replace('### 직전 개발 기준 PERF_B',block+'### 직전 개발 기준 PERF_B',1))
  archive=ROOT/'archive/README.md';text=archive.read_text();text=text.replace('PERF_B의 직전 PERF_A','당시 PERF_B의 직전 PERF_A',1).replace('현재 검증/workflow는 `docs/performance/B/`다.','당시 검증/workflow는 `docs/performance/B/`였다.',1)
  block='\nPERF_C의 직전 PERF_B HTML/status/SHA/workflow는 `v48/WIP_PERF_B/`에 원래 bytes/blob으로 보존한다. PERF_B support/evidence는 `docs/performance/B/`에 유지하고 현재 검증/workflow는 `docs/performance/C/`다.\n'
  archive.write_text(text.replace('\n당시 PERF_B',block+'\n당시 PERF_B',1))
 (ROOT/'SHA256SUMS_v48_WIP_PERF_C.txt').write_text('\n'.join(sha(ROOT/f)+'  '+f for f in [q['candidate'],'AEGIS_PLAN_STATUS_v48_WIP_PERF_C.md'])+'\n')
 print(json.dumps({'checks':n,'htmlSha256':hs,'supportFiles':support(q),'statusSha256':sha(ROOT/'AEGIS_PLAN_STATUS_v48_WIP_PERF_C.md')}))
if __name__=='__main__':main()
