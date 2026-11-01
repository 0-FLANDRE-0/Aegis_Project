# TRACK-B 안정화 회귀 계획

현재 상태: **고정 후보의 원래17job 실행 완료·기존 strict5건 미승인 유지**. 아래는 실행에 사용한 계획이며 실제 결과는 [최종 비교](evidence/regression/FINAL_COMPARISON.json)와 [원래 결과 집계](REGRESSION_RESULTS.json)를 따른다. ACTIVE `87da98bf…dede18` / SHADOW `75b845f5…747d4f`, 도구 `97ac3014…041d4`가17행 모두 일치했다. domain402 PASS/4 FAIL/14 INCOMPLETE, D1 A29/30·기존B30/30, UI213/213, 실제WebGL8발29/29단언이다. 새 strict 실패0이며 기존 strict5건 회복0·기대값 승인0이다.

`track-b-stabilization-a`, 기준 commit `1d92554026d15f417d987aec519007ea9657a6b6`의 자료를 읽었다. 모든 실행은 root의 후보 freeze/GO 이후 진행했다. 이번 controller는 제품·원래 fixture·단언·기대값·허용 오차를 변경하지 않는다. 전투pilot/계측은 별도 lane이며 이번 결과만으로 전체 전투·장래 제어 불변을 주장하지 않는다.

## 기준 자료와 세 버전 비교

| 버전 | SHA-256 | 역할 |
| --- | --- | --- |
| TRACK-A | `e2c1976a8a21eae6a494bf6caf0ec5b702663bd97721763ef7e92c6d6096d67a` | 원래 strict 회귀 및 D1 서명 기준 |
| 전달된 TRACK-B ACTIVE | `0b3e5ad90324f10057f2e500692f4f56b020ddc4f12db16423bf4d258a38e4c6` | 안정화 전 실제 동작·미승인 차이 비교 |
| 새 STABLE_A | root freeze 후 기록 | 한 번의 실제 새 제품 실행 |

기존 B의 native364, paired38/42, domain402 PASS/4 FAIL/14 INCOMPLETE, D1 signature29/30은 승인된 새 기대값이 아니다. 최종 checksum과 실제 source/HTML이 맞는 **이미 측정된 reference**로만 재사용한다. A 및 B의 게시 manifest, 선택한 B 원시12파일, 원래 시험/helper23파일을 준비 단계에서 확인했다. 이 결과를 새 안정화 시험 PASS나 과거 차이 승인으로 세지 않는다. A/B 디렉터리와 evidence를 덮어쓰지 않으며 신규 결과는 `B_stabilization/evidence/regression/`에만 쓴다.

새 `_SHADOW.html`의 의미는 **기존 B ACTIVE 소비를 유지하고 안정화 제안을 shadow로 관측하는 것**이다. 이전 `Aegis_SIM_v48_WIP_TRACK_B_SHADOW.html`처럼 TRACK-A 소비를 유지하는 제품이 아니다. 혼동하지 않도록 후보명·SHA·비교 축을 실행 manifest에 기록한다. 이 lane의 기본 광역 실행은 새 ACTIVE 한 번이며 SHADOW의 직접 정책/순수성 검사는 해당 담당자의 결과와 연결한다.

## 실행 순서와 기존5차이

1. 원본 `friendly/A/ciws.py d1`을 그대로 실행한다. DDG-119,90°,Kh-35U11km,MANUAL,함포 AutoAA OFF,419010~419039 **30시드 전부1회**다. 단일 새 raw 결과를 A와 기존 B에 각각 비교해 새 baseline 전투를 중복 실행하지 않는다.
2. 원본 `helicopter/F/verify_regression.py --baseline-only`로 A↔후보 **기존6case/42단언/raid32초**를 그대로 실행한다. 기존 B의 같은6case 원시 출력을 읽어 A/B/후보3열 및 모든 B→후보 leaf 차이를 추가한다. B↔후보 비교를 위해 후보 raid를 다시 쏘지 않는다.
3. 원래 native13 suite364단언을 변경 없이 실행한다.
4. 원래 UI213과 자연 탐지→LOCK→정식 VLS→전체 fixed tick→실제 WebGL8발/29단언을 실행한다.

paired의 `samePhysicalState`/`sameExistingObserverState` DDG·CG4건과 D1 seed419012 signature1건은 다음 두 축으로 보고한다.

- **원래 strict:** A 기준과 실제 비교한 통과/실패·변경 leaf를 유지한다. 회복됐으면 실제 회복으로 표시하고 실패했으면 기대값을 바꾸지 않는다.
- **품질·전투:** 기존 B 및 A와 표적별 사후 결과·HP·피격·생존·자원·종료시각·관측/제어 상태를 함께 비교한다. 일부 최종 값이 같다는 이유로 원래 strict 차이 또는 관측 차이를 승인하지 않는다. 전체 raw 필드·P·identity·freshness·global/private RNG 차이를 제거하지 않는다.

D1의419012는 이전 계측에서 두 파일이 이미 존재했고, 근접 NIS 보류가 mean/P·focused revisit·cached TTI 순서와 마지막 CMS cue를 바꿨다. duplicate 제거 또는 두 번째 파일 생성 방지를 입증한 것으로 쓰지 않는다. paired4건은 첫 matching 보류→발사528→540tick→708kg 임시 적재차→원래 hull phase 응답 경로가 확인된 차이다. 안정화 후 해당 경로와 품질이 어떻게 바뀌었는지 원문으로 판단한다.

기존32초 및 새로 측정된 B의120초에서는8Kh-32+추가13ASM가 모두 alive이고 요격/피격 사건0이었다. 이번 원래32초 비교를 최종 전투 성공·8발 격추라고 표현하지 않는다. 자연 전투 pilot은 `audit_ciws`의 별도 AUTO 설정이며, MANUAL D1과 조건이 다르므로 raw 결과를 재사용하지 않는다. 이 lane은 원래419025 피격 FAIL도 원래 조건에서 독립 보존한다.

## 수·비용·동시 실행

native364+paired42=406개의 실제 기존 domain 단언이며, 구형 EMCON UI14는 계속 INCOMPLETE로 표시하여420을 설명한다. D130·UI213·WebGL29와 신규 정책 검사를 domain420에 더하지 않는다. 기존 CG→friendly observer2 미승인 차이도 별도 이력으로 유지한다.

기존 B의 실제 광역2420.8초와 D1 ACTIVE461.3초를 합치면 한 lane 약48분이다. 호스트 조건에 따라50분 이상이 될 수 있으며 예측을 실제 측정처럼 쓰지 않는다. 기존 A/B 자연 D1·광역을 다시 전부 실행하지 않고 hash가 맞는 원시 기준을 재사용한다. 회귀 lane은 직렬1개, 자연 전투 pilot lane은1개로 기존 공유 flock 두 slot의 전역 상한2를 지킨다. root의 별도 조정 없이 이 lane을 병렬2로 늘리지 않는다.

## 준비·실행 명령

```sh
# 브라우저0회. hash/provenance와 계획만 신규 경로에 기록한다.
TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python docs/contact/track/B_stabilization/regression.py --prepare

# root가 새 후보 SHA와 GO를 전달한 뒤에만 실행한다.
TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python -u docs/contact/track/B_stabilization/regression.py --run --sha ROOT_FROZEN_SHA --shadow-sha ROOT_FROZEN_SHADOW_SHA
```

`--only d1 paired-track-a`처럼 먼저 원래5차이를 확인하고 종료한다. 그 다음 root의 cost 독점 창을 비운 뒤 남은 광역을 실행한다. 동일 SHA의 닫힌 결과는 `--resume`에서 그대로 보존한다. FAIL은 FAIL로 재사용하며 PASS로 바꾸지 않는다. root가 명시적으로 재시험을 지시할 때만 `--retry-closed`를 쓰고 먼저 원시 자료와 이전 execution을 attempts에 보존한다. 이 방식으로 첫 단계의 미승인 strict 차이를 이유 없이 다시 쏘지 않는다. cost 종료 후 root가 두 lane을 배정한 경우에만 `--parallel 2`를 사용한다. native lane과 UI/WebGL lane을 우선 병행하고 누적 controller wall과 겹치는 worker wall 합은 구별한다.

`evidence/regression/STOP_AFTER_CURRENT`가 있으면 진행 중 worker 종료 후 멈추며 다음 suite를 시작하지 않는다. 후보나 원래 test source/controller가 실행 중 바뀌면 중단한다. 후보 packed script13을 직접 풀어 BUILD main/module SHA, 수정 모듈 정확히1회 내장, ACTIVE token과 현 SCOPE 일치를 `PRODUCT_SOURCE_PROOF.json`·gzip source에 남긴다. 이는 실제 제품 byte 증명이고 진단용 대체 연관 모델은 없다. root 요청 없이 무거운 재시험·새seed·다른 설정을 추가하지 않는다.

기본17job 모두에서 후보 SHA를 기록한다. 원래 assert 실패는 FAIL, 환경/timeout·미완료는 INCOMPLETE로 남기고 독립 사례 수집은 계속한다. 결과는 actual strict 회복 / 여전히 다른 관측 경로 / 실제 품질·전투 악화 / 미계측을 구별한다. 승인되지 않은 차이를 자동 PASS·KNOWN_DELTA·새 기대값으로 바꾸지 않는다. main·기존 B 브랜치 병합, release/tag·PR 생성은 이 도구가 수행하지 않는다.
