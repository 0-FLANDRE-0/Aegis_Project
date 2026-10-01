# AEGIS v48 WIP14B4 — 상태형 로프팅 구현·검증 보고

## 판정과 기준

**구현·범위별 회귀 통과 / B4 전체 CLOSED 보류.** 최대 요격거리나 모든 조건에서의 명중을 인증한 빌드가 아니다.

- 기준: `Aegis_SIM_v48_WIP14B3.html`
- B3 SHA-256: `c6a75f9f2c03e925ec298d0cb5885fa9b043c066aeb62117cf4674ec0c313123`
- 결과: `Aegis_SIM_v48_WIP14B4.html` · 7,319,028 bytes
- B4 SHA-256: `03de975ddac38c192eae1572b2588bba49defcb148a2fd9ae7b6921f4e7355e2`
- decoded C55 main SHA-256: `62aa1f6e8a4ff9445f3fde2f4d86e581e6457616daada424bf3c8a4164ba186b`
- 사용자 요청 목표: MR 160km대, ER/SM-6 240km 이상. 이 값은 이번 게임의 설계·검증 목표이며 실제 무장 제원을 검증한 수치가 아니다.

## 구현

### 1. 무장별 단계 상태

`SAM_LOFT_B4_PROFILES`의 네 프로필과 미사일 소유 `_loftB4` 상태를 추가했다. 장거리 경로는 CLIMB → CRUISE → DIVE 순서이며 필요하면 CLIMB에서 DIVE로 바로 전환할 수 있다. 한 번 DIVE로 진입하면 먼 표적 갱신을 받아도 다시 CLIMB/CRUISE로 되돌리지 않는다. 단거리의 DIRECT는 새 B4 에너지 선반을 넣지 않고 기존 단거리 경로를 유지한다는 의미이지, 완전히 직선인 물리 궤적을 보장한다는 뜻이 아니다.

MR/ER/SM-6는 각각 독립된 상승·유지·하강 프로필이다. ESSM은 완만한 별도 프로필이며 가까운 교전에는 Standard급 선반을 강제하지 않는다. RAM은 B2의 각도 기반 RF/IR 직접 유도와 해면 회피를 그대로 유지했다. RAM에 새 고고도 로프팅을 추가하지 않았다. 표적 고도가 해당 프로필의 최대 회랑 이상이면 `HIGH_TARGET` 직접 유도 분기로 기존 상승 유도를 보존한다. 높은 표적을 낮은 선반으로 끌어내리지 않으며 MR 20km 표적과 ESSM 고고도 비교도 기존 결과와 일치한다.

초기 거리와 관측 표적고도로 회랑을 정하고, 남은 거리·자체 항법 속도·연소 단계·종말 인계를 통해 전환한다. Mach/동압/에너지 높이/항법 및 표적 불확실성도 상태 진단에 남긴다. 현재는 거리·속도 중심의 **SIM_TUNED 단계형 게임 프로필**이며 완전한 에너지 최적제어기 또는 실제 미사일 유도 소프트웨어가 아니다.

### 2. 실제 제어 경로 연결

기존 코드는 적응형 고도 계산 뒤 Kappa 중기유도가 최종 명령을 다시 생성하므로, 앞단 loftDemand만 수정하면 적용되지 않을 수 있었다. B4는 기존 유도·자동조종 함수에 전달하는 게임 경로 참조를 단계 상태에 맞게 연결했다. 실제 위치·속도·추력·탄두 피해를 강제로 덮어쓰지 않는다.

유지 구간의 국부 경로 참조와 실제 표적 PIP를 구분했다. `controlHorizonS`는 해당 경로 참조용 시간이고 기존 `tgo`는 표적 인계·지원 판단용으로 남는다. 짧은 국부 참조 때문에 조기에 종말 인계되거나 DL 지원시간이 바뀌는 것을 피하기 위한 분리다. DIVE에서는 B4 경로 참조를 해제하고 기존 표적 추정·시커·종말 유도가 계속 작동한다.

새 단계는 자체 항법 추정치를 소비한다. 원시 표적 객체·전역 track을 새로 검색하거나 항법 오차 장부로 실제 좌표를 복원하지 않는다. 기존 legacy 30초 TGO 계산은 과거/단거리 경로에 남지만 새 B4 단계의 거리·회랑 권위로 쓰지 않는다.

### 3. 관제 범위와 표시

관제의 `effectiveRangeKmGameplay`는 MR 160km, ER/SM-6 260km로 갱신했다. 이것은 무기 검토 범위이며 그 거리에서 발사를 무조건 허용하거나 명중을 보장하는 상수가 아니다. 기존 FCQ·권한·센서 시선·SPG 예약·재고·NEZ 조건은 유지했다.

DEBUG에 B4 프로필/단계/자체 추정 고도/회랑/잔여거리 표시를 추가했다. 읽기와 화면 갱신은 항법·패킷·단계 시간을 진행시키지 않는다. B3 HTML의 bootstrap 배지에 남아 있던 B2 표기를 B4로 맞췄다.

## 사거리 시험의 의미

아래는 **명시적으로 관측 트랙을 공급하는 독립 시험 fixture**다. 동일한 해역 seed 142000에서 고정 틱으로 표적을 갱신하고, 기존 실제 발사 게이트·SPG 예약/서보·비행·시커·신관·피해를 실행했다. 초기 센서 탐색부터 시작하는 전체 전투 캠페인이 아니며, 기만체·재밍·회피 기동을 포함하지 않는다. 고정 표적은 항법/경로 검증용 합성 표적이다.

표의 거리값은 **발사 당시 수평 분리거리**다. 접근 표적은 비행 도중 가까워지므로 발사 거리와 요격 지점의 함정 거리는 다르다. `closestM`은 고정 틱에 샘플한 최소거리이며 연속 신관 계산의 정확한 CPA와 다를 수 있다.

주요 확인:

- MR: 고도 2km와 10km의 160km 고정 표적 모두 요격. 10km 표적 사례는 약 212.57초, 요격 위치의 함정 수평거리 약 159.996km다.
- ER: 고도 10km의 240km 및 260km 고정 표적 요격. 260km 사례는 약 234.92초, 요격 위치 약 259.987km다.
- SM-6: 고도 10km의 240km 고정 표적은 seed 142000에서 미스, 142001/142002에서 요격. **3개 seed 중 2개 성공은 통계적 Pk나 안정적인 최대사거리의 증명이 아니다.**
- SM-6: 고도 10km, 초기 260km에서 250m/s로 접근하는 표적은 요격했으나 실제 요격 위치는 함에서 약 215.230km다. 이를 “함에서 260km 지점 요격”으로 표기하지 않는다.
- SM-6의 seed 142000, 고도 10km/260km 고정 표적은 약 259m를 빗나갔다. 도달 가능성과 확실한 종말 요격은 별개이며 이 실패를 신관/피해 수치 수정으로 없애지 않았다.
- ER의 고도 2km/240km 사례는 SPG 지원 사전검사 `NO_CHANNEL`로 발사 거부. 센서/조명 제약을 제거하지 않았다. 같은 거리 SM-6는 비행했지만 해당 저고도 고정 표적에 도달하지 못했다.
- ESSM은 단거리 회귀를 유지했다. 별도 25km/2km 고정 표적 비교에서 B3는 에너지 부족으로 미도달, B4는 요격했다. 그러나 40~50km의 여러 시험 조건에서는 여전히 에너지 부족으로 실패한다. ESSM 전 범위 성능 개선 완료라고 주장하지 않는다.

## B3와 동일 fixture 비교

동일한 개선된 시험 harness를 B3/B4 양쪽에 적용했다. 오래된 `_wip75StepFocused` 단독 호출에는 SPG 물리 서보 진행이 빠져 있으므로, 양쪽 모두 실제 서보 scheduler를 명시적으로 진행했다. 이 보완은 시험 fixture에만 있으며 production SPG 코드를 수정한 것이 아니다. 트랙은 시험임을 명시한 이상적 관측치로 갱신했다.

B3의 MR 160km/10km 고정 표적은 LOW_SPEED로 약 8.23km 앞에서 끝났고 B4는 요격했다. ER 260km/10km는 B3가 낮은 궤적으로 미도달, B4는 요격했다. B3의 SM-6 240km/10km 역시 미도달이었다. 단거리 SM-6 40km/10km 고정 표적의 미스와 ESSM 10km/50m 접근 표적의 요격은 B3/B4 결과가 같다.

## 실행한 검사

| 묶음 | 결과 |
|---|---|
| stageUnit | 33/33 PASS |
| b4Runtime | 8/8 PASS |
| b3Transport | 49/49 PASS |
| b3Runtime | 25/25 PASS |
| package | 52/52 PASS |
| b2NavUnit | 38/38 PASS |
| vlsTiming | 12/12 PASS |
| releasePolicy | 22/22 PASS |
| uiHandlers | 2/2 PASS |

시험 묶음은 일부 같은 하위 검사를 공유하므로 숫자를 합산해 고유 시험 개수로 주장하지 않는다.

- MR 160km 고정, ER 260km 고정, SM-6 초기 260km 접근 표적의 **전체 단계 비행**을 1×/8×/16×/64× 틱 배치로 반복해 항법·비행/단계 이력이 일치했다. 이는 실기기 프레임률 측정이 아니다.
- B3의 GPS·양방향 DL·지연/손실/순번·독립 채널 중단·지원 종료 불변식·종말 권위 검사를 다시 실행했다.
- B2 ASM/RAM 항법 fixture와 RAM 분리 비행, ASM 분리 비행 결과를 B3 원본과 비교해 동일함을 확인했다.
- A13 공력·추진·질량 등의 동결 hash와 WIP156 셀 이탈 계약을 유지했다.
- C55 14개 레코드의 gzip/길이/SHA/JS 구문을 검사했다. 압축 자산 0~12는 B3와 동일하다.
- 지원 도구로 B3에서 재생성한 B4 HTML이 이번 결과와 바이트 단위로 일치했다.

## 검사 갱신

A14 기존 range-fit 검사는 “180km ER 계획 한계 뒤 SM-6 우선”을 전제로 190km를 시험했다. ER 계획 한계를 260km로 갱신했으므로 해당 분기 시험을 270km로 옮겼으며, 실제 무기 선택 코드는 기존 프로필 기반 로직을 유지했다.

B1 로프팅 진단의 “B4가 아직 미구현이어야 한다”는 boolean은 새 엔진 존재 검사로 바꿨다. 과거 30초 제한 계산의 진단 수치는 보존하고 과거식 진단임을 명시했다. 실제 B4 동작은 별도 33개 단계 검사와 전체 비행 시험으로 검증했다.

## 남은 사항

1. 기존 core 자기검사 `V48 WIP13A surface target submergedBreachFloods` 1건은 B3와 B4 모두 동일하게 실패한다. 침수 물리를 변경하거나 검사를 삭제하지 않았다.
2. Chromium native file URL은 관리자 정책으로 차단됐으며 HTML 전체를 `set_content`로 로드했다. 빈 페이지에서도 WebGL/WebGL2 생성 실패가 재현됐다. 2D/3D FIRE 조작은 통과했지만 실제 3D 함체·연기·카메라 및 모바일 GPU/FPS는 미검증이다. WebGL renderer의 콘솔 오류는 남아 있다.
3. SM-6 고정 장거리 표적의 seed별 미스, ESSM의 중장거리 에너지 부족, 저고도 원거리의 센서/조명 한계를 계속 구분해 검증해야 한다. 미시험 회피/횡단/도주 표적까지 최대사거리를 일반화하지 않는다.

**결론:** B4 단계형 게임 로프팅은 구현돼 실제 경로에 연결됐고, 요청한 거리대의 일부 조건에서 요격이 확인됐다. 그러나 안정적인 최대 요격거리·전 조건 명중·전체 프로젝트 CLOSED까지 선언한 것은 아니다.

## 전체 36-case 결과

`SM2`는 MR, `SM2ER`는 ER이다. 속도 양수는 함 쪽으로 접근한다. FAILED/LOW_SPEED/NO_CHANNEL도 삭제 없이 포함한다.

| 무장 | 초기 수평거리 km | 표적 고도 km | 접근속도 m/s | seed | 결과 | 샘플 최소거리 m |
|---|---:|---:|---:|---:|---|---:|
| SM2 | 40 | 10 | 0 | 142000 | PROX_DETONATION_KILL | 11.2 |
| SM2 | 80 | 10 | 0 | 142000 | PROX_DETONATION_KILL | 10.0 |
| SM2 | 120 | 10 | 0 | 142000 | PROX_DETONATION_KILL | 8.3 |
| SM2 | 160 | 10 | 0 | 142000 | PROX_DETONATION_KILL | 4.8 |
| SM2ER | 40 | 10 | 0 | 142000 | PROX_DETONATION_KILL | 10.5 |
| SM2ER | 120 | 10 | 0 | 142000 | PROX_DETONATION_KILL | 12.9 |
| SM2ER | 180 | 10 | 0 | 142000 | PROX_DETONATION_KILL | 14.5 |
| SM2ER | 240 | 10 | 0 | 142000 | PROX_DETONATION_KILL | 6.8 |
| SM2ER | 260 | 10 | 0 | 142000 | PROX_DETONATION_KILL | 13.7 |
| SM6 | 40 | 10 | 0 | 142000 | PROX_DETONATION_MISS | 70.9 |
| SM6 | 120 | 10 | 0 | 142000 | PROX_DETONATION_KILL | 7.4 |
| SM6 | 180 | 10 | 0 | 142000 | PROX_DETONATION_KILL | 12.8 |
| SM6 | 240 | 10 | 0 | 142000 | SEA_IMPACT | 88.5 |
| SM6 | 260 | 10 | 0 | 142000 | SEA_IMPACT | 259.1 |
| ESSM | 10 | 10 | 0 | 142000 | PROX_DETONATION_KILL | 8.7 |
| ESSM | 25 | 10 | 0 | 142000 | LOW_SPEED | 946.6 |
| ESSM | 40 | 10 | 0 | 142000 | LOW_SPEED | 13861.0 |
| ESSM | 50 | 10 | 0 | 142000 | LOW_SPEED | 20162.6 |
| SM2 | 40 | 2 | 0 | 142000 | PROX_DETONATION_KILL | 8.1 |
| SM2 | 160 | 2 | 0 | 142000 | PROX_DETONATION_KILL | 18.4 |
| SM2ER | 180 | 2 | 0 | 142000 | PROX_DETONATION_KILL | 8.3 |
| SM2ER | 240 | 2 | 0 | 142000 | RELEASE_REJECTED:NO_CHANNEL | — |
| SM6 | 180 | 2 | 0 | 142000 | PROX_DETONATION_KILL | 10.2 |
| SM6 | 240 | 2 | 0 | 142000 | LOW_SPEED | 1171.1 |
| ESSM | 15 | 2 | 0 | 142000 | PROX_DETONATION_KILL | 9.2 |
| ESSM | 40 | 2 | 0 | 142000 | LOW_SPEED | 13280.8 |
| SM2 | 40 | 0.05 | 250 | 142000 | PROX_DETONATION_KILL | 18.1 |
| SM2ER | 40 | 0.05 | 250 | 142000 | PROX_DETONATION_KILL | 11.9 |
| SM6 | 40 | 0.05 | 250 | 142000 | PROX_DETONATION_KILL | 19.4 |
| ESSM | 10 | 0.05 | 250 | 142000 | PROX_DETONATION_KILL | 24.1 |
| SM2 | 160 | 10 | 250 | 142000 | PROX_DETONATION_KILL | 16.7 |
| SM2ER | 260 | 10 | 250 | 142000 | PROX_DETONATION_KILL | 16.7 |
| SM6 | 260 | 10 | 250 | 142000 | PROX_DETONATION_KILL | 28.7 |
| ESSM | 40 | 10 | 250 | 142000 | LOW_SPEED | 8983.8 |
| SM6 | 240 | 10 | 0 | 142001 | PROX_DETONATION_KILL | 7.7 |
| SM6 | 240 | 10 | 0 | 142002 | PROX_DETONATION_KILL | 8.7 |

## 재생성과 실행

B3 원본을 별도로 보존한 상태에서:

```bash
python apply_b4.py Aegis_SIM_v48_WIP14B3.html Aegis_SIM_v48_WIP14B4.html
node tests/state.test.cjs
node tests/transport.test.cjs
python tests/package_b4.py Aegis_SIM_v48_WIP14B3.html Aegis_SIM_v48_WIP14B4.html
python tests/runtime_b4.py Aegis_SIM_v48_WIP14B4.html
python tests/runtime_b3.py Aegis_SIM_v48_WIP14B4.html
```

브라우저 검사에는 Python Playwright와 Chromium이 필요하다. `CHROMIUM_PATH`로 실행 파일을 지정할 수 있다. GUI 그림 검증이 막힌 환경에서는 통과로 기록하지 않는다. 재패키징 바이트 동일성은 이번 Python/zlib 환경에서 확인한 결과이며 다른 zlib 버전의 gzip 바이트 차이는 별도 확인해야 한다.