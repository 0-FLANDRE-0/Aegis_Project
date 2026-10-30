# SM6 240km 자연 RF 원인 분리 진단

## 현재 결론

현재 자료만으로 관측 오차와 기동 변화 중 무엇이 먼저였는지는 확정할 수 없다. 기존 `probe_release_regression.py`는 미사일의 실제 위치/속도, RF 모드, 선택된 source, 제어 입력과 G를 기록하지만, 유도기가 실제로 소비한 표적 추정 위치/속도는 기록하지 않았다.

따라서 이전의 “추적 악화가 기동 손실을 일으켰다”는 설명은 가설이다. 반대 방향의 영향과 상호 증폭도 남아 있다.

확인된 경계 시점:

| 후보 | ARH를 유도원으로 채택 | 첫 COAST | 해당 구간의 미사일 측방 좌표 |
|---|---:|---:|---:|
| DZT | 146.550초 | 148.700초 | 0.52m → 120.92m |
| HANDOFF | 147.950초 | 149.133초 | 0.58m → 53.02m |

두 후보 모두 공식적인 COAST 전부터 측방 기동이 나타났다. 이것만으로 기동이 관측 오차보다 먼저였다고 단정할 수는 없다. TRACK 상태에서도 추정값은 부정확할 수 있으며, 두 후보의 구간 길이도 다르다.

HANDOFF는 이후 재획득 구간이 길어지고 종말 속도가 약588m/s로 줄었지만, 이 역시 원인 순서를 증명하지 않는다. 같은 조건의 다른 네 시드가 약695~709m/s로 명중한 결과와 분리해서 읽어야 한다.

## 기준

- repo: `0-FLANDRE-0/Aegis_Project`
- branch/head: `launch-handoff-a@99c2ef33e5256acbfb3aa557a01065669404de89`
- DZT HTML SHA-256: `edc159fa347d721d61d80228e2512665f22da0adb4f02fdf4e2dbe82789e0c9c`
- HANDOFF HTML SHA-256: `e42a2e05b8ff2096dfb334e7b9427cd2cd6da46d567083f06620ffdf35729ed7`
- 기존 `docs/missile/termination/A/cases/normal.json`의 152번 입력 그대로.
- AIR/Su-35, 240km, 5km, 접근250m/s, seed12001, 종료기OFF.
- 기존 결과: DZT 성공/CPA5.478m, HANDOFF 실패/CPA51.308m.
- 종료기 ON/OFF는 이미 같은 결과가 확인됐으므로 먼저 OFF 조건을 고정해 조사한다.

## 실행

이 폴더를 원래 Codex 작업 환경에 풀고, 기존 저장소 루트에서 실행한다. 실행 HTML과 지원 파일을 읽을 뿐 제품 파일을 수정하지 않는다. 기존 Codex의 Playwright/Chromium 환경과 `browser_tools.py`를 재사용한다.

```sh
python /path/to/SM6_240KM_RF_DIAG/probe_sm6_240km_rf.py \
  --repo "$PWD" \
  --output /tmp/aegis-sm6-240km-rf-causal
```

먼저 관찰기 동등성만 확인하려면 `--native-only`를 붙인다. 출력 폴더가 비어 있지 않으면 덮어쓰지 않는다. 입력 HTML SHA가 다르면 중단하므로, 새 제품을 시험하려면 원래 기준과의 차이를 확인한 뒤 진단 입력 계약을 갱신한다.

## 세 가지 진단 모드

| 모드 | 바뀌는 경계 | 해석 |
|---|---|---|
| NATIVE | 관찰만 수행 | 원래 전체 반환값과 완전 일치해야 한다. 불일치 시 관찰기 결과를 폐기한다. |
| IDEAL_ARH_VALUES_REAL_VALIDITY | ARH adapter의 유효한 추정 위치/속도만 이상값으로 교체 | 실제 RF 유효성/신뢰도/획득 상태를 유지하며 값의 오차 영향을 분리한다. |
| WITHHOLD_ARH_AUTHORITY | ARH adapter의 acquire/hold 권한만 차단 | 실제 RF 코어는 계속 실행하고, 기존 중재기가 SARH/DL/MEM을 선택하게 한다. |

후자의 두 모드는 진단용 반사실 실험이다. 제품 수정안이나 실제 시커 성능 증거가 아니다. 실제 RF 코어의 detected/TRACK 상태, 탐지 거리, Pd, 난수, PN/APN/Kappa 이득, 추진/공력/G 한계를 강제 변경하지 않는다. 제어 경로가 바뀌면 이후 궤적과 관측열도 달라지므로, 서로 다른 모드의 난수 소비 및 관측열이 동일하다고 주장하지 않는다.

이상값 모드의 truth 접근은 이 격리된 시험 경계에만 존재한다. 제품에 포함하지 않는다.

## 새로 남기는 값

- 유도기가 소비한 표적 위치/속도와 선택 source, 품질, 유효성.
- 온보드 상대 상태와 실제 상대 상태의 차이. INS 재기준화 오차를 표적 오차로 혼동하지 않는다.
- ARH/SARH EKF의 상태와 공분산 대각, 측정 선택/갱신 여부와 잔차 계측.
- source 중재와 Kappa/PN/APN/ZEM/bridge의 현재 tick 호출 여부와 마지막 호출 시각.
- 최종 기체 입력, 실제/전달 G, 공력·기동 항력, 구동기 상태.
- 마지막 선택값 및 NIS/SNR가 캐시인지 현재 갱신인지 구분하는 timestamp.
- 초기8초와135초 이후의 고정 tick 기록.

추정 오차 비교는 `before`의 PRE_DYNAMICS 경계에서 수행한다. 동역학이 진행된 뒤의 미사일 위치와 진행 전의 표적/추정치를 섞어 추적 오차를 만들지 않는다. `afterPhysical`는 실제 기체 응답 확인용이다.

## 판별 순서

1. NATIVE 두 후보가 기존 전체 반환값과 일치하는지 확인한다.
2. 147~163초 구간에서 ARH의 측정 잔차/추정 오차 증가, 유도원 전환, 명령 변화, 기동 항력 증가의 순서를 비교한다.
3. 같은 절대 시각뿐 아니라 같은 표적 거리와 같은 제어 단계에서도 비교한다.
4. 이상값 모드에서 실패가 해소되는지 확인한다. 해소돼도 물리 관측의 어느 부분이 잘못됐는지는 측정·EKF·중재 로그로 추가 분리한다.
5. ARH 권한 차단 모드에서 실패가 해소되는지 확인한다. 해소돼도 ARH를 상시 비활성화하는 제품 수정으로 연결하지 않는다.
6. 어느 모드에서도 해소되지 않으면 인계 후 초기조건, Kappa→종말 전환, 기동 응답/에너지 경로를 우선 재검토한다.

검증 목표는 seed12001 한 발만 명중시키는 것이 아니다. 원인을 확인한 최소 수정 후, 기존 다섯 시드와 주변 거리/고도 조건에서 실제 AIR/native RF 회귀를 실행한다.

## 검증 상태와 제한

이 패키지의 JS/Python 문법 검사와 제한된 stub 기반 관찰기 계약 검사는 PASS했다. stub 검사는 반환값 identity, 원래 함수 호출 수, detached 로그, 반사실 모드의 adapter 반환값 분리를 확인한다. 이 환경에서는 현재 제품의 실제 AIR/native RF 브라우저 재실행을 완료하지 못했다. 이 패키지는 추가 계측을 위한 준비물이다. 현재 정밀 원인을 확정하거나 제품 수정이 완료됐다고 해석하지 않는다.

원래 `probe_release_regression.py`의 압축 raw도 표적 추정 상태를 기록하지 않으므로, 압축 파일을 푸는 것만으로 빠진 시계열을 복구할 수 없다.

## 참고 자료

- [원래 계측 코드](https://github.com/0-FLANDRE-0/Aegis_Project/blob/99c2ef33e5256acbfb3aa557a01065669404de89/docs/missile/launch-handoff/A/probe_release_regression.py)
- [실패 요약](https://github.com/0-FLANDRE-0/Aegis_Project/blob/99c2ef33e5256acbfb3aa557a01065669404de89/docs/missile/launch-handoff/A/final-evidence/release-regression-analysis.json)
- [상세 보고서](https://github.com/0-FLANDRE-0/Aegis_Project/blob/99c2ef33e5256acbfb3aa557a01065669404de89/docs/missile/launch-handoff/A/REPORT.md)

