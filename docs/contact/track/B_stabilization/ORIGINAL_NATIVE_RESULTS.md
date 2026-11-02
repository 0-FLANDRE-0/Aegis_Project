# 원 B native 전체 보존 검증

최종 후보에서 원본 B23개 native 그룹과 cohort14를 **8개 fresh context에서 전부 실행해 PASS**했다. 실행 시간은 133.18초다. 기존 대표19개 검증에 이어, 나머지 원본 그룹도 실제 최종 제품에서 실행했다.

| 최종 제품 | B 연관 진단 | 원본 native | 원본 cohort | 기존 B 전체 nativeResult delta / state hash delta |
|---|---|---:|---:|---:|
| SHADOW | OFF | 84/84 | 14/14 | 0 / 0 |
| SHADOW | ON | 90/90 | 14/14 | 0 / 0 |
| ACTIVE | OFF | 84/84 | 14/14 | 0 / 0 |
| ACTIVE | ON | 90/90 | 14/14 | 0 / 0 |

OFF/ON은 원래 B runner가 조작한 B 연관 진단의 상태다. 기존 A 관측 trace의 fixture 설정도 원본 그대로 유지했다. cohort helper는 내부에서 두 진단을 ON으로 강제하므로, cohort4개는 모두 `FORCED_ON_BY_ORIGINAL_HELPER`로 기록했다. cohort를 OFF 시험이라고 부르지 않는다.

각 제품·진단 설정마다 native와 cohort를 서로 다른 fresh context로 시작했다. 원래 cohort 기준자료와 같은 초기 조건을 사용해, 앞서 실행한 native23의 observer/RNG 누적 상태가 비교에 섞이지 않게 했다. 최대 동시 브라우저는1개였다.

원본 B run_native.py와 run_cohort_supplement.py, native_support/native_c55/native_integration/cohort_supplement helper 바이트 및 원래84/90/14 기준자료는 published B CHECKSUMS와 모두 일치했다. 새 controller는 원래 run_native.py를 수정 없이 import해 같은 NPC C55 accessor를 사용한다. 기존 main의 구형 SHADOW mode guard 대신 실제 `mode=ACTIVE`와 `stabilizationMode`를 검사하는 controller만 별도로 두었다. 원래 게임 assertion·fixture·허용 오차·기대값은 바꾸지 않았다.

새 raw 결과는 보조 조회 전에 저장했다. 기존 B의 `nativeResult` 전체를 schema/header/A diagnostic trace까지 포함해 leaf 단위로 비교했고, fixture별 전체 passive filter/P·physical·private/global RNG hash도 비교했다. **모든8개 결과에서 raw delta0, state hash delta0**다. 아무 differing field도 제외하거나 자동 승인하지 않았다. 각 delta 파일은 빈 결과까지 보존했다.

SHADOW와 ACTIVE 각각 B 진단 OFF/ON의 native gameplay records·모든 fixture state·마지막 private/world 상태가 정확히 같았다. 반복 snapshot, private state 조회, 실제 awaited ENV status, core self-test도 모두 통과했다. 실제 브라우저/fixture 오류는0이다.

최종 pins:

- ACTIVE: `87da98bf8f6d8bd68ef87a3d2ac75ce9c355db9e95bd192ab060d01e5bdede18`
- SHADOW: `75b845f5b353c576ea191a2508578edcb29b4110a69cbf97e532df6562747d4f`
- 원 B ACTIVE: `0b3e5ad90324f10057f2e500692f4f56b020ddc4f12db16423bf4d258a38e4c6`
- 새 controller: `d71ce36634c9fac65a2b276f1021822e988b78bd37fa5db7f1f963d6e7ad3ae1`
- 원 native helper 결합 SHA: `971f275dda92012c8af4ab8bf949db192c5d2aa51d6c9c1117eac7e4614cbd6b`
- 원 cohort helper 결합 SHA: `9dff42ff01ca392650b036b18d1da1697136c27d4d3b237b34e8eb472db9555a`

이 검증은 direct native anonymous-ingress 경로의 보존 증거다. 자연 RF/Pd·전투·전체 도메인420 회귀의 새 승인이나 사거리/무장 성능 검증을 뜻하지 않는다. 기존 solver47의 포화 정책 교체 strict 차이1건과 자연전투 회귀는 별도 결과이며 이번 native PASS로 덮지 않는다.

기존 scoped `NATIVE_RESULTS.md`/`NATIVE_SUMMARY.json`와 그 대표19·새23·metadata18 원시 자료는 바꾸지 않았다. 이번 추가 전체 검증의 기계 판독 자료는 `evidence/original-native-full/SUMMARY.json`, source/기준자료 pins는 `PROVENANCE.json`, 원시 결과와 모든 delta는 같은 디렉터리에 있다.

실행 controller 종료 후 브라우저 main0과 두 공유 lease 모두 반환을 확인했다. `LANE_CLOSE.json`에 남겼으며 추가 브라우저를 실행하지 않는다.
