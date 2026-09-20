# AEGIS v48 WIP12F 터미널 탄도 마감 구현

## 1. 결론

WIP12F는 WIP12E REV5의 장갑·신관·구획 폭발을 교체하지 않고, 실제 소비자 연결에서 남아 있던 경계 오류를 닫는다.

- 안전장치 해제와 충돌 신관 작동을 분리했다.
- 지연신관은 최소 자극보다 얇은 판을 지나도 즉시 불발 처리되지 않는다.
- `PARTIAL`은 찌그러짐·균열·후면 spall을 만들 수 있지만 물리 개구는 만들지 않는다.
- 탄체 plug/rear spall은 모듈과 승조원에 같은 event ID로 한 번씩 전달된다.
- 관통 후 표적 밖으로 나간 살아 있는 탄체와 신관은 명시적 handoff로 남는다.
- 외피의 파임·균열·관통은 위치 기반 장갑 patch로 reset 전까지 다음 충돌에 반영된다.
- 불발탄과 비폭발 관통도 시각 scar와 장갑 patch를 남긴다.
- Kh-32와 Kh-35U의 live 경로에 실제 신관 지연 범위, 운동 파편 및 장갑 patch 소비자를 연결했다.

모델의 RHAe 및 신관 수치는 계속 `SIM_TUNED_RHA_EQUIVALENT_NORMALIZATION_NOT_CERTIFIED_FUZE_DATA`다.

## 2. 감사에서 확인하고 수정한 결함

| 항목 | 기존 문제 | WIP12F 판정 |
|---|---|---|
| 안전장치와 충돌 작동 | `armed`가 두 의미를 동시에 가질 수 있음 | 비행 상태만 `safetyArmed`를 정하고, 판재 접촉은 `impactInitiated`만 정함 |
| 얇은 판과 지연신관 | 최소 자극 미달 접촉이 지연신관을 영구 불발로 만들 수 있음 | 일반 지연신관은 `NO_FUNCTION_CONTINUE`; 다음 경계를 다시 판정 |
| 대함 미사일 보조 채널 | 일반 지연신관 원칙과 superquick fallback 관계가 불명확 | `ANTI_SHIP_DELAY_8`만 독립 초고속 외부기폭 보조 채널을 가진다는 SIM 가정을 계약에 명시 |
| 직격식 신관과 탄체 파손 | 판 통과 뒤 `FRACTURED` 결과가 접촉 순간의 직격식 개시까지 취소 | 직격식 개시는 접촉 순간 판정; 완전 `SHATTERED`만 작동 실패 |
| 접촉식 요격탄 | `delayRemainingS: 0`이 충돌 전 타이머 시작으로 해석되어 공중기폭 | 시작 상태를 `timerStarted:false`로 명시하고 첫 경계에서 타이머 개시 |
| 부분 관입 | `PARTIAL`이 구멍처럼 해석될 가능성 | `holeAreaM2 = 0`; breach 생성 조건을 `PERFORATED && plate.perforated`로 고정 |
| 후면 spall | 두꺼운 장갑에서도 전달량이 충분히 감쇠되지 않음 | 관입비와 장갑두께/구경비의 지수 감쇠를 함께 사용 |
| 운동 파편 소비 | module/crew 연결이 blast와 분리되어 누락되거나 중복될 수 있음 | `kineticSpallSources`를 공유하고 module/crew가 각 도메인에서 한 번만 소비 |
| 영구 장갑 손상 | 임시 `diagnosticPatches` 명칭에 실제 권위가 섞임 | `armorDamagePatches` 권위 채널을 신설하고 legacy 진단 배열은 호환용으로만 유지 |
| 관통 후 표적 이탈 | 살아 있는 신관/폭약 상태가 trace 종료와 함께 사라짐 | `AEGIS_POST_EXIT_PROJECTILE_HANDOFF_V48_WIP12F` 생성 |
| live ASM | 공통 kernel 개선이 Kh-32/Kh-35U 실전 경로에 일부만 연결 | 외피·내부 barrier patch, 운동 spall, crew, module, 영구 patch를 실제 명중 경로에 연결 |

## 3. 신관 결정

### 3.1 상태 축

- `safetyArmed`: 비행 시간·거리 또는 명시적 pre-arm 상태만 결정한다.
- `impactQualified`: 접촉한 판재의 RHAe, 정상속도, 정상충격량, plate work, 경사각 및 신관 생존을 만족했는지 뜻한다.
- `impactInitiated`: 유효 접촉이 실제 신관 회로를 개시했는지 뜻한다.
- `timerStarted`: 지연 시간이 흐르기 시작했는지 뜻한다.
- `dudReason`: 안전장치 미해제와 충격 손상을 구분한다.

충돌이 안전장치를 대신 해제하지 않는다. 안전장치가 풀리지 않은 탄은 충분한 판재 자극을 받아도 `SAFETY_NOT_ARMED_AT_IMPACT` 불발이다.

### 3.2 접촉 결과

| 신관 | 자극 미달 | 자극 충족 | 탄체 파손 |
|---|---|---|---|
| 일반 지연식 `8/12/20 mm RHAe` | 계속 비행, 다음 경계 재판정 | delay clock 시작 | 후단 신관은 관통 및 충분한 관입 여유가 있을 때만 `FRACTURED` 생존 |
| `ANTI_SHIP_DELAY_8` | 명시적 독립 superquick 외부기폭 | delay clock 시작 | 대함 profile 판정 사용 |
| 직격식 | 최소 두께 없음, 정상 접촉량은 필요 | 접촉 순간 개시 | 접촉 뒤 `FRACTURED`는 허용, `SHATTERED`는 실패 |
| 신관 없음 | 기폭 없음 | 기폭 없음 | 운동 피해만 적용 |

`8/12/20 mm RHAe`는 관통 보장치가 아니라 신관을 작동시키는 최소 판재 자극 분류다.

## 4. 장갑과 개구부

| 결과 | 외피 변화 | 내부 전달 | 물리 개구 |
|---|---|---|---|
| `SCORCH` | 그을림 | 작은 구조 충격 | 없음 |
| `DENT` | 소성 변형 | 제한된 충격·피로 및 작은 rear spall | 없음 |
| `CRATER` / `PARTIAL` | 파임·균열·잔존두께 감소 | 더 큰 rear spall과 구획 피로 | 없음 |
| `PERFORATED` | 관통구·plug | 직접 관통, plug/rear spall | 있음 |
| `EXTERNAL_BLAST_BLOWOUT` | 외부 폭압 파열 | 새 개구를 통한 pressure/hot gas/fragment | 있음 |

외부 고폭은 탄체가 관통하지 못해도 얇은 외판의 pressure/impulse/plate-work 한계를 넘으면 `EXTERNAL_BLAST_BLOWOUT`을 만들 수 있다. 두꺼운 장갑이 버티면 표면 손상과 제한된 내부 충격만 남고 direct hot-gas path는 생기지 않는다.

`damagedAreaM2`와 `holeAreaM2`는 별도다. 넓게 찢어지고 좌굴된 범위가 모두 열린 구멍으로 취급되지 않으므로, 시각 파괴 범위와 침수 면적을 동시에 과장하지 않는다.

## 5. 운동 파편과 폭발 피해

탄체 관입이 판재에 한 일에서 plug와 rear spall 에너지를 분리한다.

- plug 에너지는 실제 관통에서만 생성된다.
- rear spall은 비관통에서도 가능하지만 관입비와 두께/구경비로 감쇠한다.
- module 피해는 진행 방향, 거리, 에너지 및 장비 취약도로 계산한다.
- crew 피해는 같은 source를 상세 구획에 투영하고 event-ID 기반 결정 난수만 사용한다.
- blast trace의 구조 파괴 spall과 탄체의 kinetic spall은 서로 다른 물리 원천으로 유지한다.

폭발은 WIP12E의 공통 `BlastChargeSpec → BlastTrace → BlastDamagePacket`을 그대로 사용한다. 미사일·로켓·포탄 이름은 solver 분기에 쓰지 않으며, 폭약량·TNT 등가·케이스 질량·기폭 위치·매질·기존 개구만 입력한다.

## 6. 영구 손상과 다음 피격

`WIP12F_ARMOR_PATCH_LEDGER`는 표적, 표면, 재료, 위치 및 반경으로 patch를 식별한다.

- 첫 피격의 잔존두께와 잔존강도가 같은 위치의 다음 solver 입력을 낮춘다.
- 같은 위치의 반복 손상은 곱셈식 잔존두께와 누적 균열로 합성한다.
- 관통 또는 blast blowout patch는 이후 경로에서 열린 표면으로 취급한다.
- patch는 simulation reset 때만 삭제한다.
- 렌더러는 snapshot을 읽기만 하고 물리나 난수에 피드백하지 않는다.

legacy ASM 경로도 초기 외피와 이후 barrier를 patch-aware 사본으로 만들어 기존 WIP100 관통 solver에 전달한다. solver 자체를 무기별로 갈라놓지 않는다.

## 7. 단일 피해 권위

공통 packet 적용 순서는 다음과 같다.

1. 탄도 trace가 경계, 운동 파편, 기폭 및 개구를 계산한다.
2. blast가 있으면 WIP12E가 immutable trace와 damage packet을 계산한다.
3. `impactEventId`가 피해/침수 소비자에서 수락된 경우에만 상태를 변경한다.
4. direct penetration, kinetic spall 및 authoritative blast parts를 target별로 병합한다.
5. 모듈, 구획, 승조원, 화재, 종강도, 침수 및 VLS가 자기 채널을 한 번씩 소비한다.
6. 수락 뒤에만 장갑 patch와 표시 event를 기록한다.
7. WIP12B terminal event와 WIP12D residual presentation은 이미 적용된 primary blast를 재생하지 않는다.

불발탄은 blast trace를 만들지 않는다. 대신 운동 관입·spall·승조원 피해, 외피 scar 및 장갑 patch만 남긴다.

## 8. 표적 이탈 handoff

`terminalExit` 경계를 관통한 탄체가 아직 살아 있으면 다음 상태를 보존한다.

- 위치와 진행 방향
- 탄체 축, 속도, 총질량 및 coherent mass
- integrity와 누적 시간
- 신관 안전·개시·잔여 지연 상태
- 남은 폭약량

trace의 호환 종료 사유는 계속 `TARGET_EXIT`이고, 상세 상태는 `postExitHandoff`에 둔다. 현재 렌더러는 이를 읽기만 하며 재충돌 물리는 후속 exterior/re-entry 소비자가 맡는다.

## 9. 실제 회귀 결과

| 검사 | 결과 |
|---|---:|
| inline JavaScript parse | PASS |
| WIP12F static contract | `17/17 PASS` |
| WIP12F hardening diagnostics | `11/11 PASS` |
| WIP12A/B/C/D/E inherited diagnostics | 모두 PASS |
| core selftest | `0 failures` |
| WIP12F Playwright | `4/4 PASS` |
| console/page error | `0/0` |

실제 live 경로:

| 항목 | Kh-32 | Kh-35U |
|---|---:|---:|
| seed / range | `481232 / 100 km` | `481235 / 100 km` |
| 명중 시각 | `92.78333333333333 s` | `345.81666666666666 s` |
| 결과 | `NORMAL_HIT` | `NORMAL_HIT` |
| module damage rows | `41` | `25` |
| compartment damage rows | `15` | `17` |
| ignition candidates | `5` | `2` |
| kinetic spall source | `1` | `1` |
| crew spall energy | `353074.9969 J` | `220278.8149 J` |
| armor patch committed | `1` | `1` |
| consumer issues | `0` | `0` |

추가 회귀:

- 불발탄: blast trace `0`, scar `+1`, armor patch `+1`, crew kinetic-spall source `1`
- 함교 500 kg TNT-equivalent 3회: 두 번째에 전방 SPY F1/F2 정지, 세 번째에 네 면 모두 정지
- solved 2D scar: `111`, top/side 모두 `111`, 130 simulation seconds 뒤 유지
- 3D render-state adapter: `V48_WIP12F_TERMINAL_HARDENING`, armor patch snapshot 전달 확인

## 10. 의도적으로 남긴 한계

- full CFD, 수중 bubble pulse, whipping 및 장시간 구조 좌굴은 계산하지 않는다.
- 함정용 강재의 RHAe와 8/12/20 mm 신관 profile은 공개 인증값이 아닌 simulation tuning이다.
- kinetic spall은 방향·거리·에너지 기반 bounded model이며 개별 파편 수천 개의 ray trace가 아니다.
- 국부 patch는 위치와 반경 기반이며 mesh 자체를 유한요소로 재해석하지 않는다.
- 전함·중순양함급 homogeneous/face-hardened 장갑은 지원하지만 복합장갑·반응장갑·지상전차용 모델은 범위 밖이다.
- 실제 함포의 외부탄도, 포신, 사격통제, 탄종 선택은 다음 WIP에서 이 공통 terminal API 앞에 연결해야 한다.
