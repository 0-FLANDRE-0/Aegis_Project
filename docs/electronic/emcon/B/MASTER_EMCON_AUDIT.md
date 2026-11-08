# EMCON_B Commit A — master 상태 감사

기준은 병합된 `main@3dbe3b84bde7a5b23e9713b26a7c8a9ba3823941`, 제품
`Aegis_SIM_v48_WIP_EMITTER_A.html` 22,146,163 bytes / SHA-256
`3a5886b4fe0826c834dd237574dd38c21bdd67600553f64c7ce532a7bce1c2be`다.

## 권위와 소비자

| 위치 | 분류 | 현재 의미 | EMCON_B 보존/연결 원칙 |
|---|---|---|---|
| `emconActive` | MASTER_OWNER | 자함 전체 레이더 침묵 | 신규 상태에 복제하지 않는다 |
| `observerC(r).emcon` | MASTER_OWNER | NPC/아군함 전체 레이더 침묵 | 함정별 기존 권위 유지 |
| `applyEmconDesignationF2` | MASTER_OWNER | 자함 master 쓰기, PD 종료/복귀 | 방사 없는 지정 계약 유지 |
| `toggleEmcon` | MASTER_OWNER | operator toggle, network 공동모드 이탈 | 기존 호출 호환 유지 |
| `electronicCommandF` | MASTER_OWNER | owner-addressed master/EW 명령 | 세부정책 command의 공통 진입점으로 확장 |
| `observerCommandC` | MASTER_OWNER | 비자함 진단 master/sensor 명령 | 기존 필드와 의미 보존 |
| `networkSetRadarG`, `networkGroupStepG` | MASTER_OWNER | 공동 EMCON 임시 overlay | 세부정책을 파괴하지 않는 lease로 분리 |
| `electronicSettingsF`, `networkExportElectronicG` | COMPATIBILITY_READER | 저장·네트워크 호환 view | master와 세부정책을 구분해 export |
| `electronicShipPhysicalEmittersDeclaredA` | PHYSICAL_EMISSION_GATE | 등록 장비의 실제 방출 | 장비별 effective query를 소비 |
| 자함 legacy SPY/SPQ/NAV + `observerStepC` | SENSOR_UPDATE_GATE | 실제 신규 measurement | 물리 방출과 같은 effective query 소비 |
| SPG/SAM/자동방사 경로 | WEAPON_DOCTRINE_GATE | 기존 master 기반 교전 제한 | FIRE_CONTROL 미등록 한계와 기존 차단 유지 |
| `fleetEmconG`, `networkEmconG`, MAP_E 요소 | UI_ONLY | routing/presentation | profile 기반, 명령 API만 mutation 허용 |
| snapshot/diagnostic API | DIAGNOSTIC_ONLY | read-only 관측 | RNG·truth·상태 mutation 금지 |

전체 기계 판정과 함수별 SHA는 [BASELINE_AUDIT.json](BASELINE_AUDIT.json)에 고정한다.

## 기준 상태 결론

- 자함 master와 NPC master는 서로 다른 저장 위치를 쓰지만 의미는 동일하다.
- 네트워크 `groupBase`는 개별 master를 잠시 보존하고 `groupLease`가 follower에 임시 모드를 전달한다.
- ECM 요청/allocator는 radar master와 별도다.
- 현재 물리 emitter resolver만 끄는 것으로는 충분하지 않다. 자함 legacy sensor scheduler와 NPC observer 측정 경로도 같은 판정을 소비해야 한다.
- `FIRE_CONTROL` 활성 장비는 EMITTER_A registry에 0개다. SPG-62의 기존 master 차단만 유지한다.
- 통신 링크는 radar EMCON과 분리한다.

Commit A는 제품 HTML을 변경하지 않는다.
