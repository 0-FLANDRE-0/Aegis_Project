# REG_K + ENV_D 재현

기준: `kappa-pip-los-a` / `80b65143d10f0fc42072d068dacbbc69a2b78fc3`.
원본 KAPPA_PIP_LOS_A 실행 코드와 모든 게임 계수는 보존한다.
새 HTML에는 측정표 데이터와 명시적으로 호출하는 읽기 전용 `__ENV_D__.status()/table()/capture()`만 추가한다.
지도·발사 관문·AI의 소비자는 추가하지 않는다. 페이지 시작 시 사거리 진단을 실행하지 않는다.

이 수치는 SIM_TUNED 게임 모델의 결과이며 실제 무기 자료나 성능과 비교하지 않는다.

## 순서와 실행 비용

1. 원래 회귀를 양쪽 HTML에 실행한다: `python docs/envelope/D/run_reg_k.py`.
   기본 입력은 현재 KAPPA_PIP_LOS_A와 archive의 RANGE_RECOVERY_A다.
   이전 HTML을 archive한 뒤에는 스크립트의 current 경로를 같은 archive 파일로 지정한다.
2. 실제 WebGL 8발은 `run_observed_webgl.py HTML OUT`으로 실행한다.
   원래 29개 assertion은 변경하지 않고 OFF 대조군도 같은 3D 경로를 켠다.
3. `verify_world120.py`, `verify_combat_followup.py`로 해시 및 변경된 전투 사례를 확인한다.
4. `verify_path.py`는 실제 게임과 독립 native ASM 진단의 동일 경로 및 world/RNG/tick 불변을 확인한다.
5. `node docs/envelope/D/pilot.cjs` 뒤 `python docs/envelope/D/estimate.py`로 실행 전 비용을 기록한다.
   `COST_ESTIMATE.json`의 6시간 제한을 준수한다. full 측정은 자동 시작하지 않는다.
6. 승인된 이번 full 측정: `node docs/envelope/D/suite.cjs --execute-full`.
   4 workers, 120 기본 칸 + 다른 ASM 라벨6칸. 모든5개 시드에서 native 비행을 독립 실행한다.
7. full은 **한 번만** 실행한다. `node docs/envelope/D/finish_measurement.cjs`는
   모든 경계와 고정 무작위30궤적만 반복하며 전체 표를 다시 측정하지 않는다.
8. `compare_reg_k.py` → `build.py` → `verify_delivery.py` → `report.py`.

고정 시드5세트는 `engine.cjs`, 무작위 궤적 선택 seed는 `finish_measurement.cjs`에 있다.
`SIM_RNG_STATE`는 Pk/손상 난수, `SIM_SEED_BASE`는 native 항법/신관 파생 스트림으로 독립 공급한다.
BATTLESPACE_SEED만 바꿔 SAM 항법 시드가 바뀐 것으로 취급하지 않는다.

## 진단 격리와 판정

- source-copy 추출기와 dependencies.json은 실제 게임 함수 원문과 SHA-256을 기록한다.
- native `spawnEnemyMissile`로 ASM 엔티티를 만들고 native 피해 초기화를 사용한다.
- ASM 비행 AI를 적분하지 않고 위치·속도만 직선 등속으로 유지한다. 종말 tick의 native 피해/임무파괴 변화는 덮어쓰지 않는다.
- native WIP112 observer를 원래 fixed-tick 순서대로 부착한다. native ASM 함수의 비행 AI 이전 손상 prefix를 원문 추출해 같은 틱의 탄두/구조 파괴를 처리한다. 원 함수/추출 구간 SHA를 보존한다.
- native VLS release → native updateMissile → native 신관 → computeInterceptPk → applyInterceptResult와 Kh-32 임무파괴 계층을 그대로 실행한다.
- 이상 관측/지원/장비 조건만 `diagnostic/boundaries.json`에 명시적으로 격리한다.
- 최소5km, 상한500km. 바깥은 coarse/binary 뒤 더 먼 정수km 전수 확인이다.
  안쪽은5km부터 연속된5km grid에서 3/5 KILL/STRUCT_FAIL이 필요한 엄격한 정의다.
  5km에서 실패하면 안쪽은0km다. 이후 다시 명중하는 구간이 있어도 연결하지 않는다.
- 같은 비행에 Pk만5회 추첨하지 않는다. 항법 시드에 따라 궤적 자체가 달라진다.
- old ENV_C는 AIR point-target + PRE_KAPPA_PIP_LOS이다. 새 ASM 측정값으로 재표기하지 않는다.

## 결과 파일

- `ENVELOPE_TABLE_D.json` / `ENV_D_TABLE.csv`: 바깥·안쪽·요격점 평균/최소/최대, 경계의5발 결과.
- `REG_K_RESULTS.json`, `REG_K_ALL_CHANGES.csv`: 이전 기준과 모든 사격 결과·CPA·시간 차이.
- `results/cells/*.json.gz`: 모든 거리의5발 native 결과. 전역 스윕은 한 번이다.
- `results/followup.json.gz`: 경계 재검사·궤적·무작위30개 반복·ENV_C 경계 단일발 대조.
- `results/trajectories-10hz.csv.gz`, `results/phase-intervals.csv`, `plots/*`: 궤적과 단계.
- `results/SEA_IMPACT.csv.gz`: 해면 충돌 원시 목록. 출처와 반복 여부는 보고서를 따른다.
- `evidence/*`: 비용·동일 경로·결정성·최종 HTML 검증 및 원래 회귀의 로그/스크린샷.

gzip JSON/CSV는 표준 압축이며 확장자를 유지했다. 실행 HTML은 별도 ZIP에 한 개만 넣는다.
보고서 ZIP은 실행 HTML을 포함하지 않는다. 전체 측정 재현에는 저장소 checkout과 Node/Python/Chromium/Playwright가 필요하다.
무거운 검사는 CPU quota4에 맞춰 `taskset -c 0-3`를 사용한다.
헤드리스의 Canvas2D CPU backend 보정과 실제 SwiftShader WebGL을 구분한다.
시뮬레이션·조작·판정 함수나 assertion을 바꾸어 테스트를 통과시키지 않는다.

초기 계통손상 콜백 누락 v0 시도는1칸 완료 시 중단·무효화해 evidence/diagnostic-v0-incomplete-hooks에 별도 보존했다. 정식 전수/새 표/결정성 판정에서 제외한다. inputs.json의 profileFingerprintInput은 원래 AIR용 capture API가 함께 준 원시 출처이며 ENV_D 해시로 사용하지 않는다. 새 fingerprint.json이 ENV_D 기준이다.
