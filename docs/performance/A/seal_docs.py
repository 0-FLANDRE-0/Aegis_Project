"""Publishable handoff docs/checksums from already passed final-original evidence."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 q=json.loads((HERE/'evidence/verification-summary.json').read_text());assert q['pass'];html=ROOT/q['candidate'];assert sha(html)==q['candidateSha256'];n=q['directChecks'];hs=q['candidateSha256'];size=q['candidateBytes'];mainSha=q['mainSha256']
 table='\n'.join(f"| {r['fleet']} | {r['count']} | {r['meanBefore']:.2f} | {r['meanAfter']:.2f} | {r['observedReductionPercent']:.1f}% |"for r in q['benchmark']['summary'])
 (HERE/'PERFORMANCE.md').write_text(f"""# PERF_A 최종 성능·검증 조건

원본 {size:,}bytes, SHA `{hs}`, main `{mainSha}`. H4A 원본과 PERF_A 원본을 같은 호스트에서 직렬 비교했다. seed1831565813, Chromium151.0.7922.173/Playwright1.62.0, warm120+측정240 actual fixed ticks, 각각2반복/AB·BA 교대/두 번째 조건 역순이다. 다른 회귀 작업이 끝난 후 측정했다.

CG 자함, optional 아군CG+적DDG, 적 항공기/구표적함OFF, terrain bypass, native Kh-32 초기 수평거리16km·고도10000m·4방위다. helper가 넣는 측정 트랙은 부하 fixture이며 자연 탐지 증거가 아니다. 모든16쌍에서 저장/관측/무장/방어/EW 상태, entity 수와 combatRNG를 exact 비교했다. 기존 performance/profiler 및 `performance.now()`가 기록하는 방어 진단의 lastBuildMs/lastAssessmentMs만 비교에서 제외한다. 시뮬레이션 시각·판단·발사·효과 값은 유지한다. 원래 처리시간 필드를 포함한 raw 상태도 모두 보존하고 이 명시적 정규화로 재검증했다. 자세한 각 반복과 압축 상태 원본은 evidence/benchmark.json 및 state-*.json.gz다.

| 함정 수 | Kh-32 수 | H4A ms/tick 평균 | PERF_A ms/tick 평균 | 관측 CPU 시간 감소 |
|---:|---:|---:|---:|---:|
{table}

이 값은 해당 호스트/대표 조건의 CPU 관측이며 사용자 휴대폰 FPS 또는 보편적 개선율이 아니다. 단독 자함의 `getShipSystemDamage`는 기존 경로를 유지하므로 전체 함정 수에 따라 효과가 달라진다. 적은 부하에서 작은 차이는 측정 변동일 수 있다. 64발 조건의 비용이 남아 있어 다음 단계의 planner/SPG·SPY·접촉 geometry 감사를 계속해야 한다. `sensors_tracks_ew` phase는 tick당2회이므로 phase 평균을 단순 합산하지 않고 calls로 가중한다.

실제 native64모델에 고유 Kh-32 도색 texture/canvas1개·2048×2048 RGBA8 source pixel16,777,216bytes를 확인했다. 이전2모델은 동일 픽셀의 texture/canvas2개를 만들었다. 같은 도색64개를 만들 경우의 중복 source pixel budget1,073,741,824bytes(1GiB)가16,777,216bytes(16MiB)로 줄어드는 구조다. 실제 VRAM/heap 측정값이나 FPS가 아니며 mipmap/GPU·renderer별 upload 비용은 별도다. geometry/재질은 개별 소유이며 이 단계에서 draw 수를 줄이지 않는다.

기존 도색 픽셀 SHA와 geometry/재질 SHA가 정확히 같다. 부분 제거 뒤 texture disposal0/실제 WebGL 렌더, 마지막 제거1/반복 제거1, 새 생성·MAIN잔해·닫힌 도감 참조·도감 전환·import/reset epoch를 확인했다. 기존 도감은 닫아도 현재 모델을 보관한다.

새 원본 직접 {n}/{n}PASS,29suites/15captures. 과거 H4A 결과를 합산하지 않았다. CG/DDG6 ownship 조건은 performance 계측 외 EW/network/tactical/maneuver/attack/team을 포함한 상태와 RNG가 exact다. 세 owner1/8/16/64 배속, 실제 nativeVLS/RAM/Phalanx·채프/눌카/Harpoon·피격 후 nativeRAF/WebGL·UI/camera·저장/reset 및 기존 함대 AI/공유를 직접 재검사했다. 자연 Harpoon과 close-in의 fixture 조건/late guards는 해당 report를 따른다. core/page/runtime/presentation 오류0, Actions 미실행이다.
""")
 status=f"""# AEGIS PLAN STATUS v48_WIP_PERF_A

## 현재 기준

- 최적화1단계 완료. H4A final `b97925cb5fb27d4dad26d62db78520641ee70857` 위 `performance-a`.
- HTML `{q['candidate']}`, {size:,}bytes, SHA-256 `{hs}`.
- decoded main SHA-256 `{mainSha}`. records0~12/모델 assets 및 stablev48 유지, records13만 변경.
- 직전 H4A HTML/status/SHA/workflow는 `archive/v48/WIP_MULTI_SHIP_H4A/`에 같은 bytes/blob으로 보존한다.

## 적용 내용

1. 불변 hitbox의 system→고유 module name 색인. owner별 현재 손상값·자함 기존 경로·가변 geometry fallback을 유지한다.
2. EW 지원 대역 검사 선행으로 불필요한 pod 위치/손상/사각 계산 제거. 지원 대역의 결과와 기존 정책을 유지한다.
3. Kh-32 동일 도색 texture/canvas 공유. idempotent lease·마지막 참조 disposal·새 생성·import/reset·도감 수명 확인.

캐시는 snapshot에 저장하지 않는다. fixed60/120/20Hz·RNG, 센서/RF/CMS·AI·발사 권한·CG Phalanx-only·DDG장비, Harpoon INS/ARH/DL0, 충돌/관통/피해·EW·조작을 유지한다. 지원 계약은 docs/performance/A/README.md를 따른다.

## 최종 원본 직접 검증

- {n}/{n}PASS,29suites/15captures, 과거·실패한 draft 검사 합산0. page/core/runtime/presentation 오류0.
- static packing/rebuild/scope, 두 함종 새 selftest,72 EW 동등성 조건, native64모델 픽셀/geometry와 전체 texture lifecycle을 확인했다.
- CG/DDG6조건 strict 상태/RNG exact, 세 owner1/8/16/64 결정성, 기존26 H4A browser suites를 새 원본으로 직접 실행했다.
- 별도 직렬 CPU 비교16쌍의 관측/저장/무장/방어/EW·entity/RNG exact. 표와 반복·조건·한계는 docs/performance/A/PERFORMANCE.md 및 evidence/benchmark.json을 따른다.
- 최종 원본·script/report/capture SHA와 집계는 docs/performance/A/evidence/verification-summary.json이 권위다. 초기 baseline 경로 오류는 같은 bytes의 archive 경로로 재실행했고 성공한 최종 보고만 합산했다.

## 업로드와 남은 단계

사용자 직접 원본 upload/readback 승인에 따라 branch에 전체 원본과 support를 반영한다. 독립 readback은 docs/performance/A/evidence/remote-publication.json이 권위이며 자기 자신을 checksum에서 제외한다. Actions 사용 불가로 수동 workflow만 준비하며 CI PASS를 주장하지 않는다. main/H4A/선행PR 병합과 새PR 생성은 실행하지 않는다.

다음 최적화는 교전 planner/SPG-62 중복 계산, SPY 연관, 피격 envelope 지연, 실제 가시 탄체/효과의 render 비용 순으로 검토한다. 큰 기능 순서는 최적화 이후 헬기/초수평선 탐지 → 사용자 지정 RGM-109E Block Va를 유지한다. 보편적 요격률·모든 오격 방지·하드웨어 FPS 보장은 이 대표 조건 검증에 포함하지 않는다.
"""
 (ROOT/'AEGIS_PLAN_STATUS_v48_WIP_PERF_A.md').write_text(status)
 title='## 최신 개발 기준 — 최적화 WIP PERF_A'
 readme=ROOT/'README.md';text=readme.read_text();assert title not in text
 block=f"""{title}

- [HTML]({q['candidate']}), **{size:,} bytes**, SHA `{hs}`.
- 불변 부품 색인·EW 지원 대역 조기 검사·Kh-32 동일 도색 공유. **64모델에 canvas/texture1개**, 원래 도색 픽셀과 geometry를 보존하고 부분/최종 제거·도감·import/reset 수명을 검증했다.
- 기존 fixed60/120/20Hz·센서·AI·무장·피해·Harpoon DL0를 유지한다. strict6 ownship조건과 직렬CPU16쌍에서 상태/RNG exact. [성능 조건/관측](docs/performance/A/PERFORMANCE.md).
- 최종 원본 **{n}/{n}PASS /29suites**, 오류0. [상태](AEGIS_PLAN_STATUS_v48_WIP_PERF_A.md), [SHA](SHA256SUMS_v48_WIP_PERF_A.txt), [운용](docs/performance/A/README.md), [직접 검증](docs/performance/A/evidence/verification-summary.json).
- H4A final 위 `performance-a`, 원본 직접 업로드·독립 readback, Actions dispatch 없이 로컬 gate. 다음은 교전 planner/SPG 중복 계산 최적화이며 헬기/초수평선 → RGM-109E Block Va는 최적화 뒤다. main/선행PR 병합·새PR 생성은 실행하지 않는다.

"""
 readme.write_text(text.replace('## 직전 개발 기준 — Multi Ship WIP H4A',block+'## 직전 개발 기준 — Multi Ship WIP H4A',1))
 inst=ROOT/'AEGIS_PROJECT_INSTRUCTIONS.md';text=inst.read_text();title='### 최신 개발 기준 PERF_A — 최적화1단계';assert title not in text
 block=f"""{title}

- 현재 세트 `v48_WIP_PERF_A`, HTML {size:,}bytes SHA `{hs}`, main `{mainSha}`. H4A final `b97925cb5fb27d4dad26d62db78520641ee70857` 위 `performance-a`. 현행 support/workflow/checksum은 PERF_A, 아래 H4A 이하 내용은 당시 기록이다.
- 불변 등록 hitbox system→고유 module name만 WeakMap으로 색인하고 현재 owner damage를 매번 읽는다. 자함 기존 함수/가변 geometry scan을 유지한다. EW IJ band 검사를 pod geometry 이전으로 이동하며 지원 band 계산·정책은 유지한다.
- Kh32 기존 도색 texture/canvas를 view/THREE/실제 paint 입력별로 공유한다. geometry/material/plume은 개별이고 body geometry lease는 idempotent, 마지막 참조에서만 texture.dispose 및 entry 제거다. live/MAIN wreck/도감·import/reset/native render를 검사했다. 닫힌 도감은 기존 current model1개를 보관한다. 두 캐시는 파생 데이터이며 snapshot/전투 상태를 소유하지 않는다.
- 새 원본 직접 {n}/{n}PASS/29suites/15captures, 오류0. H4A26 browser suites, 두 함종 selftests/72 EW조건,64모델 source texture1개·pixel/geometry parity,6ownship strict state/RNG와3owner1/8/16/64배속exact,별도직렬16쌍을 확인했다. counts/SHA/조건/범위는 PERF_A evidence를 따른다.
- H4A 네 원본 samebytes/blob과 stablev48/assets0~12를 보존한다. §7.1 full original upload/readback 승인 유지; Actions 미실행/CI PASS 주장 없음; main/선행PR 병합·새PR 생성 없음. 다음은 planner/SPG·SPY·피격 envelope·실제 render 최적화이며 이후 헬기/초수평선 → RGM-109E Block Va를 유지한다. CPU 관측을 휴대폰/실제GPU FPS로 표현하지 않는다.

"""
 inst.write_text(text.replace('### 직전 개발 기준 MULTI SHIP H4A',block+'### 직전 개발 기준 MULTI SHIP H4A',1))
 shaFile=ROOT/'SHA256SUMS_v48_WIP_PERF_A.txt';shaFile.write_text('\n'.join(sha(ROOT/f)+'  '+f for f in [q['candidate'],'AEGIS_PLAN_STATUS_v48_WIP_PERF_A.md'])+'\n')
 oldPaths=[line[66:]for line in (ROOT/'docs/multiship/H4A/REPOSITORY_SUPPORT.sha256').read_text().splitlines()]
 moves={f:'archive/v48/WIP_MULTI_SHIP_H4A/'+f for f in ['Aegis_SIM_v48_WIP_MULTI_SHIP_H4A.html','AEGIS_PLAN_STATUS_v48_WIP_MULTI_SHIP_H4A.md','SHA256SUMS_v48_WIP_MULTI_SHIP_H4A.txt']};moves['.github/workflows/multiship-h4a.yml']='archive/v48/WIP_MULTI_SHIP_H4A/multiship-h4a.yml'
 paths={moves.get(f,f)for f in oldPaths};paths.update(['README.md','AEGIS_PROJECT_INSTRUCTIONS.md','archive/README.md',q['candidate'],'AEGIS_PLAN_STATUS_v48_WIP_PERF_A.md','SHA256SUMS_v48_WIP_PERF_A.txt','.github/workflows/performance-a.yml'])
 for f in HERE.rglob('*'):
  if not f.is_file()or any(x in ['node_modules','__pycache__']for x in f.parts)or f.name in ['REPOSITORY_SUPPORT.sha256','remote-publication.json']:continue
  paths.add(str(f.relative_to(ROOT)))
 for f in paths:assert (ROOT/f).is_file(),f
 (HERE/'REPOSITORY_SUPPORT.sha256').write_text('\n'.join(sha(ROOT/f)+'  '+f for f in sorted(paths))+'\n');print(json.dumps({'checks':n,'htmlSha256':hs,'supportFiles':len(paths),'statusSha256':sha(ROOT/'AEGIS_PLAN_STATUS_v48_WIP_PERF_A.md')}))
if __name__=='__main__':main()
