# TRACK-B 안정화 R3 — 원래 회귀 새 실행 계획

현재 상태: **정적 준비 PASS, R3 제품 회귀 미실행, 브라우저0**. root의 최종 제품 freeze 및 실행 GO를 받기 전에는 시작하지 않는다. 자연 pilot과 실제 task/track 소유권 가설의 계측 결과가 먼저 필요하므로 중간 제품에 광역42분 실행을 시작하지 않는다.

## 고정 비교 자료

| 자료 | SHA-256 | 의미 |
|---|---|---|
| TRACK-A HTML | `e2c1976a8a21eae6a494bf6caf0ec5b702663bd97721763ef7e92c6d6096d67a` | 원래 strict 단언·D1 서명 기준 |
| 전달 B ACTIVE HTML | `0b3e5ad90324f10057f2e500692f4f56b020ddc4f12db16423bf4d258a38e4c6` | 이전 동작·원시 차이 비교 |
| R1 STABLE_A HTML | `87da98bf8f6d8bd68ef87a3d2ac75ce9c355db9e95bd192ab060d01e5bdede18` | 완료된 원래17job의 역사적 비교 |
| R2 STABLE_B HTML | `c8a9266fe12d6543cf09a1e851af5a0c717e73117945291c5bb5babc9670d584` | 완료된 guarded 자연13 및 graph 자료만 비교 |
| R3 STABLE_C / SHADOW | 최종 root freeze 후 기록 | 모든 원래17job 새 실행 대상 |

**R2의 원래17job은 실행하지 않았다.** 준비된 R2 runner나 자연13 자료를 native/domain/UI/D1/WebGL 통과로 쓰지 않는다. [R2_HISTORICAL_PINS.json](R2_HISTORICAL_PINS.json)은 실제 존재하는 R2 구현·guarded 자연13·graph16파일만 고정한다. R1의 실제 회귀23파일은 [R1_REGRESSION_PINS.json](R1_REGRESSION_PINS.json), A/B는 기존 게시 manifest로 확인한다. 읽기 전용 자료이며 이전 source/evidence에 쓰지 않는다.

원래 시험/helper23개는 TRACK-A git 기준과 byte 동일해야 한다. 단언·기대값·허용오차·조건·시드·종료시각은 변경하지 않는다. source 원인 설명은 실패 승인 또는 기대값 변경 권한이 아니다.

## 새 실행17job과 추가 대조

1. 원본 `friendly/A/ciws.py d1`30시드419010~419039를 동일 DDG-119·90°·Kh-35U11km·MANUAL·함포 AutoAA OFF 조건에서 한 번 새 실행한다. 같은 fresh 결과를 A/B/R1 세 기준에 모두 대조하며 모든 raw leaf 차이를 남긴다. R2 D1 자료는 없다고 표시한다.
2. 원본 `helicopter/F/verify_regression.py --baseline-only`의6case·42단언·raid32초 그대로 A↔R3를 실행한다. 기존 B 및 R1의 같은 시나리오 원시 자료를 읽어 A/B/R1/R3 네 버전을 비교한다. 비교를 위해 이전 제품을 다시 쏘지 않는다.
3. 원래 native13 suite364단언을 최신 고정 R3 HTML에서 새로 실행한다.
4. 원래 UI213단언, 자연 탐지→LOCK→정식 VLS→full fixed tick→실제 WebGL8발29단언을 새로 실행한다. 8발 실행 또는29단언 통과를8개 표적 격추로 바꾸지 않는다.

native364+paired42는 원래406개 실행 가능한 domain 단언이다. legacy EMCON UI14는 계속 INCOMPLETE로 남겨420을 설명한다. 새로운 수학·관찰·graph 검사와 D130·UI213·WebGL29는 domain420에 더하지 않는다.

D1/paired뿐 아니라 native/UI/WebGL의 R1→R3 원시 JSON 전체 leaf 차이를 별도 gzip으로 저장한다. host profiler·elapsed·heap도 삭제하지 않는다. 추가 raw 대조는 원래 검사 결과를 대체하지 않는다. 각 worker 전후 실제 제품·controller SHA와23개 원본 source/helper를 확인한다. 다른 SHA의 결과를 재사용하지 않는다.

## 엄격 실패와 전투 품질의 분리

- 전달 B/R1의 paired4(DDG·CG samePhysicalState/sameExistingObserverState)와 D1 seed419012 서명1은 미승인 strict 차이다. 새 R3에서 실제 회복했는지 재판정하며 계속 다르면 그대로 FAIL이다.
- 소스상 인과 경로만 설명했다고 (a) 정상 변화로 승인하지 않는다. 종료까지 본 동일 조건의 paired 전투 결과·위협별 최종 결과·자함/아군 피해·생존·종료 사유가 실제로 뒷받침하지 않으면 미승인으로 유지한다. 원래32초 비교는 이 완결된 전투 증거가 아니다.
- 32초 truth-seeded fixture 또는 기존120초의 살아 있는8+13ASM를 completed battle/격추로 표현하지 않는다. 실제 native 종료가 없는 실행은 시간 경계와 미해결 수를 명시한다.
- 419025 피격 FAIL, 원래 CG→friendly observer2 차이, legacy14 미완료도 별도 상속 이력으로 남긴다. 일부 자원·표본·관측 차이가 작아졌다는 이유로 승인하지 않는다.
- R1/R2 자연13의 material 악화는 별도 guarded battle lane의 새 R3 결과로 판단한다. 이 원래 MANUAL D1이나 일반 AUTO 사례와 섞어 승인하지 않는다. 실제 EW/decoy/시커 이력 없이 단순 RNG 차이로 결론내리지 않는다.

## 제품 실행 증명과 자원 계획

`PRODUCT_SOURCE_PROOF.json`은 최신 BUILD/SCOPE/제품 SHA를 맞추고 실제 packed script13의 main SHA·association 모듈 정확히1회 내장·mode token·역변환 byte동일을 확인한다. 진단 복사본 또는 다른 stage 함수로 게임을 대체하지 않는다. SHADOW는 전달 B ACTIVE를 실제 소비하고 R3 proposal을 관측하는 별도 제품이며 실제 배정 결과 불변 검사는 계약/battle 담당 자료와 연결한다.

과거 R1 원17job의 worker wall 합48.18분, root 승인 phase 누적 controller wall42.32분은 참고 실측이다. 현재 lane을1개만 배정받으면 약48분 이상의 예산을 예상하되 호스트/다른 작업 조건에 따라 달라진다. 실행 후 실제 완료된 job의 측정으로 갱신한다. 전역 공유 flock 상한2를 지키며, 자연 battle이 다른 slot을 쓰는 동안 이 runner는 **parallel1**만 사용한다. root 허가 없이 lane을 늘리거나 cost 독점 창을 침범하지 않는다.

기본17job은 최종 freeze 뒤 모두 fresh다. 동일 R3 SHA에서 닫힌 PASS/FAIL은 resume으로 그대로 유지하고 중복 실행하지 않는다. 다른 R3 build 또는 R1/R2 결과를 resume하지 않는다. 명시적인 재시험 지시가 있을 때만 `--retry-closed`로 원시 자료를 먼저 attempts에 보존한다. STOP_AFTER_CURRENT 파일은 안전한 worker 경계에서 다음 실행을 막는다.

```sh
# 준비만. 이 단계의 source/reference PASS는 제품 회귀 PASS가 아니다.
TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python docs/contact/track/B_stabilization_r3/regression.py --prepare

# 최종 자연pilot/계약검사 후 root freeze와 GO가 온 다음에만 실행.
TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python -u docs/contact/track/B_stabilization_r3/regression.py --run --sha ROOT_FINAL_R3_ACTIVE_SHA --shadow-sha ROOT_FINAL_R3_SHADOW_SHA --parallel 1

# 같은 최종SHA·controller에 한해 닫힌 결과를 보존하고 남은 job만 실행.
TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python -u docs/contact/track/B_stabilization_r3/regression.py --run --resume --sha ROOT_FINAL_R3_ACTIVE_SHA --shadow-sha ROOT_FINAL_R3_SHADOW_SHA --parallel 1
```

원래 단언 실패는 FAIL, 환경/timeout/미완료는 INCOMPLETE다. 기대값 갱신·허용오차 완화·실패 제외·자동 승인·main 병합·PR/release/tag 생성은 이 도구가 하지 않는다.
