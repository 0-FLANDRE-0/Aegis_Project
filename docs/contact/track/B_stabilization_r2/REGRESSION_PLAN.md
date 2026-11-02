# TRACK-B 안정화 R2 회귀 계획

현재 상태: **정적 준비 완료, R2 게임 회귀 미실행**. 새 제품 freeze와 root의 실행 GO를 받기 전 브라우저를 시작하지 않는다. R1의 통과 자료는 비교 기준일 뿐이며 R2의 통과로 재사용하지 않는다.

## 비교 축과 변경하지 않는 항목

| 버전 | 고정 SHA-256 | 사용 방식 |
|---|---|---|
| TRACK-A | `e2c1976a8a21eae6a494bf6caf0ec5b702663bd97721763ef7e92c6d6096d67a` | 원래 strict 단언·D1 서명 기준 |
| 전달된 B ACTIVE | `0b3e5ad90324f10057f2e500692f4f56b020ddc4f12db16423bf4d258a38e4c6` | 기존 실제 동작과 모든 원시 차이 비교 |
| 안정화 R1 STABLE_A | `87da98bf8f6d8bd68ef87a3d2ac75ce9c355db9e95bd192ab060d01e5bdede18` | 별도 역사적 비교. 17개 완료 job은 R2 실행이 아님 |
| 안정화 R2 STABLE_B | root freeze 후 기록 | 원래17job을 실제 새 HTML로 새로 실행 |

원래 시험/helper23개는 TRACK-A git 기준의 정확한 바이트와 비교한다. 단언, 기대값, 허용 오차, 조건, 시드, 시험 시간은 바꾸지 않는다. A와 B의 게시 manifest 및 선택 원시 자료도 이전과 같은 방식으로 검증한다. 추가 R1 회귀 자료23파일은 [R1_REGRESSION_PINS.json](R1_REGRESSION_PINS.json)에서 고정한다. 이 목록은 회귀 자료만 대상으로 하며 계속 작성 중인 R1 원인분석·ablation 자료를 동결한 것으로 취급하지 않는다.

새 결과는 `B_stabilization_r2/evidence/regression/`와 이 디렉터리의 `REGRESSION_RESULTS.json`에만 쓴다. A/B/R1 evidence는 읽기 전용이다. R1 source/build/HTML 보존 여부는 제품 builder의 별도 `R1_SOURCE_PINS.json`도 따른다.

R2의 SHADOW는 **전달된 B ACTIVE를 소비하며 R2 제안을 관측**한다. R1 ACTIVE를 소비하는 제품이나, TRACK-A를 소비하는 과거 B_SHADOW와 혼동하지 않는다. 이 회귀 lane의 기본 실제 실행은 R2 ACTIVE다. 정책의 ACTIVE/SHADOW·OFF/ON·수학/Node 검증은 별도 담당자의 결과와 연결하되 원래 domain420에 더하지 않는다.

## 새로 실행하는 원래17job

1. `friendly/A/ciws.py d1`: DDG-119·90°·Kh-35U11km·MANUAL·함포 AutoAA OFF·seed419010~419039 **30개 전부1회**. 새 원시 결과 하나를 A, 전달 B, R1 각각에 비교한다. seed419012의 strict 서명 차이와419025의 상속 피격 FAIL을 원래 조건으로 별도 표시한다.
2. 기존 `helicopter/F/verify_regression.py --baseline-only`: A↔R2 **6case/42단언/raid32초 그대로**. 같은 시나리오의 전달 B 및 R1 원시 실행과 대조하여 A/B/R1/R2 네 버전 자료를 남긴다. 새 비교를 위해 B/R1을 다시 실행하지 않는다.
3. 원래 native13 suite **364단언**을 R2에서 실행한다.
4. 원래 UI **213단언**, 자연 탐지→LOCK→정식 VLS→full fixed tick→실제 WebGL **8발/29단언**을 실행한다. 29개 검사 통과를8개 표적 격추로 표현하지 않는다.

한 R2 실행으로 얻은 D1은 세 reference에 대한 원래 서명 및 모든 leaf 차이를 남긴다. paired는 원래42단언을 유지하고 전달 B→R2, R1→R2의 **모든 원시 leaf**를 추가 보존한다. native/UI/WebGL도 원시 JSON의 R1→R2 전체 leaf 차이를 별도 gzip에 남긴다. 호스트 profiler·heap·elapsed 차이도 제거하지 않는다. 이 추가 대조는 원래 단언을 대체하거나 실패를 승인하는 기준이 아니다.

## 판정에서 보존할 미승인 사항

- 원래 domain은 native364+paired42=406개 실제 단언이다. retired EMCON UI14는 INCOMPLETE로 보존하여420을 설명한다.
- paired DDG·CG의 `samePhysicalState`/`sameExistingObserverState`4건과 D1 seed419012 서명1건은 전달 B/R1에서 남은 strict5건이다. R2에서 실제 회복했으면 회복, 계속 다르면 실패로 기록한다. 기대값은 갱신하지 않는다.
- 419025 피격 FAIL, 과거 CG→friendly observer2 차이, legacy14 미완료는 별도 상속 이력이다. 새 연관 알고리즘이 이 문제를 해결했다고 가정하지 않는다.
- R1 자연13 포화전에서 모듈 손상과 잔존 초기 위협1→3 악화가 관찰되었으며 미승인 상태다. 다른 ordinary AUTO 사례의 통과나 원래 MANUAL D1과 섞어 승인하지 않는다. 자연전투·ablation 담당자의 새 R2 시험을 별도 판단한다.
- 원래32초 paired는8Kh-32의 최종 격추·전투 완료를 검증하지 않는다. 120초 확장에서도8+13ASM가 생존했던 기존 기록을 completed battle로 바꾸지 않는다.

## 제품·소스 실행 증명

실행 전 `BUILD.json`, `SCOPE.json`, 제품 SHA를 교차 확인한다. 실제 packed script13을 해제하여 main SHA, association 모듈 정확히1회 내장, legacy ACTIVE와 R2 ACTIVE mode token, 역변환 byte 동일 proof를 `PRODUCT_SOURCE_PROOF.json`에 기록한다. 압축된 실제 모듈도 함께 보존한다. 이 정적 proof 자체는 게임 실행이 아니며 실제 동작은 원래 fixture가 해당 HTML을 실행한 결과로 증명한다.

각 job은 제품 SHA, controller SHA 및 원래23개 source/helper 바이트를 실행 전후 재확인한다. 실행 중 달라지면 해당 결과를 통과로 처리하지 않는다. diagnostic 대체 함수나 근사 모델로 시험하지 않는다. 무장·센서·KF·피해·RNG를 logger 또는 비교 코드가 다시 실행하지 않는다.

## 비용·동시 실행·재개

R1의 원래17job에서 worker wall 합은 약48.18분, 실제 여러 승인 phase의 누적 controller wall은42.32분이었다. 2개 lane을 이 회귀만 독점한다면 계산상 하한은 약24.1분이지만, 다른 자연전투/계약 시험과 공유하므로 이를 완료 약속으로 쓰지 않는다. 새 실행이 시작되면 실제 종료 job의 측정 시간으로 남은 비용을 갱신한다.

기존 `heavy_browser_slot`의 공유 flock 두 slot으로 **전역 브라우저 상한2**를 유지한다. 기본은1개 lane이다. root가 두 slot을 배정한 때만 `--parallel 2`를 쓴다. cost 독점 창은 완전히 비운다. 먼저 D1+paired로 원래5차이를 확인할 수 있지만 제품 freeze/GO 전에는 실행하지 않는다.

동일 R2 SHA의 닫힌 PASS와 FAIL은 `--resume`에서 그대로 유지하여 중복 사격을 피한다. R1 또는 다른 R2 SHA 결과를 resume으로 가져오는 것은 금지한다. 닫힌 실패 재시험은 명시적 지시를 받은 경우에만 `--retry-closed`로 원시 자료를 먼저 attempts에 보존하고 시행한다. `evidence/regression/STOP_AFTER_CURRENT`는 현재 worker 종료 뒤 다음 작업을 막는다.

```sh
# 정적 준비만. 브라우저0. 새 R2 제품이 없어도 실행 가능하다.
TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python docs/contact/track/B_stabilization_r2/regression.py --prepare

# root가 두 제품 SHA와 GO를 준 뒤, 최초 비교만 수행하는 예.
TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python -u docs/contact/track/B_stabilization_r2/regression.py --run --sha ROOT_R2_ACTIVE_SHA --shadow-sha ROOT_R2_SHADOW_SHA --only d1 paired-track-a --parallel 1

# 같은 SHA·같은 controller로 나머지를 새 실행한다. 닫힌2job 재실행0.
TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python -u docs/contact/track/B_stabilization_r2/regression.py --run --resume --sha ROOT_R2_ACTIVE_SHA --shadow-sha ROOT_R2_SHADOW_SHA --parallel 1
```

정상 원래 단언 실패는 FAIL, 환경 오류/timeout/미완료는 INCOMPLETE로 남긴다. 모든 차이는 raw 증거와 함께 회복/지속 strict 차이/실제 품질 악화/미계측으로 구분한다. 자동 기대값 승인, main·기존 B 병합, PR·release·tag 생성은 수행하지 않는다.
