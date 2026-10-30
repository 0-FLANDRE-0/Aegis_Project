# MAP_D 검증 보고서

## 1. 변경 요약

- 기준 main `9f8e77f96a39cafe017728a0734bc8dd0102a4f6` (PR #56), MAP_C SHA-256 `84fa5df960772cdb9c9904310ca7af752e3cedae025fd864dc1b27a9de6f8d7b`.
- 산출물 `Aegis_SIM_v48_WIP_MAP_D.html` / 22,045,180 bytes / SHA-256 `5be55bdc1390d79f7b74bbfa5f128af916ffecdcf28693d0524578646955f40f`.
- `map-d`에서 작업했다. main 병합·release·tag 생성 없음. CREDITS.md와 워크플로 보존. 사용자 병합용 PR을 연다.
- 하단 RGM-84/5in을 기존 지도 선택 흐름에 추가했다. 단발/연속, 탄종, 하푼 발수와 경로 버튼은 기존 공개 API에만 연결한다.
- 함포 CUE/탄종 선택/명시적 중지는 운용자 클릭으로만 수행한다. 발사 요청은 별도 UI 큐에 넣고 기존 fixed tick 시작에서 디스패치한다. 표시·그리기에서 발사/CUE하지 않는다.
- 하푼은 관문·문 열림·쿨다운을 매 발 유지한다. 경로 프로그램은 살보당 한 번 고정하고 같은 프로그램을 모든 발에 전달한다.
- CG는 각 gunMount를 직접 호출하며 selectedGunId와 mainGun 포인터를 변경하지 않는다. 평상시 포 선택 컨트롤도 그대로다.
- 비행·INS·시커·탄도·사통 품질·발사 권한·사거리표·게임 저장 스키마와 계수는 변경하지 않았다.

구현 전 확인: [PRE_IMPLEMENTATION.md](PRE_IMPLEMENTATION.md). 변경 전체: [MAP_D.diff](MAP_D.diff). 입력 감사: [data-sources.json](data-sources.json).

## 2. 신규 D1–D6 검수

| 항목 | 결과 |
|---|---|
| D1 바 | PC 1400×900 / 폰 832×384 × MAIN/PIP × DDG/CG. 설치된 RGM-84/5in만 확장 선택, 다른 재고는 기존 동작. 장전 2발일 때 3/4발 비활성. 선택/판정 전후 다른 바 박스 최대 변화 0px. 다른 무장을 메뉴로 여는 동안 이전 선택 유지. |
| D2 하푼 | 18개 native 관문 조건, 미리보기 전후 상태 변화 0, native 결과와 일치. 실제 1/2/3/4발, 서로 다른 발사관 자동 선택. 문 지연 최소 0.183333s, 발 간격 최소 1.700000s. 중간 보호 식별 거부 후 추가 발사 0. |
| D3 경로 | MAIN/PIP 빈 바다 탭은 경유점 추가, 함 WP 증분 0. 2km/최대8점 native 거부 유지. 편집 띠·탐색 중심 표시. 2발의 고정 routeProgram/searchCenter 일치, native 초안 초기화. 보호 표적이면 경로 발사도 거부. 내부 좌표 연결점은 native 간격/개수 규칙을 사용. |
| D4 함포 | 명시적 탭→native CUE. READY 초록/DEGRADED 주황/불허 빨강. 단발 정렬 대기와 재클릭 취소, 실제 1발, 연속 시작/중지·추가 발사 0, 급탄 중 탄종 거부, 이후 SAP 전환. 표적/무장 해제는 지도 소유 연속사격/CUE 중지. AIR 표적 거부. |
| D5 CG 자동 | 함수만/2문/함미만은 평상시 방위 변경으로 확인. 사계 없음은 실제 25° 횡경사/270° 표적에서 native 내림각 한계로 확인. 제외된 포 발사 0, 선택 포 설정 변화 0. 아래 설명 참조. |
| D6 크기 | PC/폰 × MAIN/PIP. 메뉴·경로 띠·태그 화면 안, 발사 실제 터치 높이 ≥40px, 경로 버튼 ≥28px. 실제 WebGL 3D+PiP 캡처 포함. |

DDG에는 하푼이 설치되어 있지 않아 프로파일을 바꾸지 않았다. DDG는 RGM-84 칸 부재와 5in을 검수하고, 실제 하푼은 CG에서 검수했다.

평상시 CG 15° 간격 방위 스윕에서는 함수/함미 사계의 합집합이 360°를 덮었다. 따라서 평상시 방위만으로 존재하지 않는 공동 사각을 만들기 위해 사계 값을 바꾸지 않았다. 기존 물리 자세 API로 25° 횡경사를 설정했을 때 270° 표적의 요구 내림각이 native 한계를 벗어나는 것을 별도 재현했다. 실제 fixed tick에서는 파랑/복원력이 자세를 바꾸므로 이 공동 사각 조건은 초기 거부·버튼 비활성과 무발사를 검사했고, 평상시 단독 포/2문 조건은 실제 발사까지 검사했다.

### 하푼 관문 비교

| 조건 | 미리보기 상태 불변 | native 결과 일치 |
|---|---|
| READY | True | True |
| TRACK_SUPPORT_BLOCKED (관측 해면충돌 · 숨김) | True | True |
| PROTECTED_IDENTITY (보호 식별 · 숨김 · 경로) | True | True |
| TRACK_SUPPORT_BLOCKED (관측 해면충돌+BDA · 표시 유지) | True | True |
| TRACK_SUPPORT_BLOCKED (관측 위협 해제) | True | True |
| NO_TRACK | True | True |
| PROTECTED_IDENTITY | True | True |
| SURFACE_IDENTITY_NOT_AUTHORIZED | True | True |
| NOT_SURFACE_TRACK | True | True |
| SURFACE_TRACK_COAST_EXPIRED | True | True |
| SURFACE_TRACK_NOT_CONFIRMED | True | True |
| SURFACE_TARGET_OUTSIDE_WEAPON_ENVELOPE | True | True |
| INS_PREDICTION_BASKET_INSUFFICIENT | True | True |
| TUBE_EMPTY | True | True |
| MK141_LAUNCHER_DAMAGED | True | True |
| LAUNCHER_COOLDOWN | True | True |
| MANUAL_SURFACE_AUTHORITY_REQUIRED | True | True |
| MANUAL_SURFACE_AUTHORITY_REQUIRED | True | True |

사유 비교에는 관측 해면충돌+BDA/위협 해제/READY/트랙 없음/보호 식별/식별 미승인/AIR/10초 초과/미확정/최소거리 밖/INS 바스켓 초과/탄 없음/발사기 손상/쿨다운/AUTO/SEMIAUTO를 포함했다. 주황 단계를 하푼에 추가하지 않았다.

발사 저널의 releaseStep는 tick 끝의 counter 증가 전 값이다. 문 지연은 요청 tick 시작부터 실제 소비한 tick 수 `(releaseStep+1-requestStep)/60`으로 계산했다. 기존 저널·문 지연 계수는 변경하지 않았다.

### 링 공급원

| 무장 | 최소 / 최대 | 공급원 |
|---|---|
| RGM-84 | 4 / 140km | HARPOON_PROFILE_A.sim |
| DDG Mk45 | 0.8 / 24km | 해당 native fireControl |
| CG Mk45 | 0.8 / 22km | 해당 native fireControl |

ENVELOPE_TABLE_D는 SAM용 그대로이며 하푼/함포 측정표를 새로 계산하지 않았다. 링 라벨은 MAP_C의 9px 스타일을 사용한다. 작은 PiP에서 최소·최대 라벨이 서로 겹치지 않도록 12px 수직 간격을 둔다.

## 3. 기존 회귀 결과

| 검수 | 결과 |
|---|---|
| 도메인 | 420/420 (단독 378 + 승인된 paired 42) |
| 기존 UI / MAP_B | 88/88 / 91/91 |
| 경고 / 추가 | 23/23 / 13/13 |
| MAP_C UI / 추종 / 규칙 / 링 / DOM | 135 / 73 / 45 / 33 / 13, 전부 통과 |
| network-only | PASS |
| 종료기 | 300발 결과 byte 동일, 222→222 성공, 신규 실패 0 |
| 자연 관측→LOCK→정식 VLS→실제 WebGL | 8발 / 29검사, 원래 4/8 명중 유지, 발사/종말/궤적 표본 차이 0 |
| 하푼 기존 | harpoon-f1 / harpoon-clock 포함 도메인 검사 PASS |
| 함포 기존 | wip13b1RunDiagnostics / composite FCQ fixture PASS |
| 비행 지문 | 281개 byte 동일 |
| 원래 최상위 함수/상수 | 3,780개 byte 동일 |
| 내장 사거리표 | 120행 전체 블록 byte 동일, status match:true |
| MAP_D 추가 | native 84, UI 213, 경계 145, 전부 통과 |

120초 상태 해시:

- idle: `fb1fac63054a72db26cce4b4f4781288a7f07a28465ce5ac2aa5597760adffbc` (MAP_C와 동일)
- combat: `b7d28c54e141aff3cd3353b5ee6f02ee2fe633f825c5c5814f79b9c83779e8f1` (MAP_C와 동일)

DDG3+CG3 승인 회귀 기대값은 변경하지 않았다. UI 코어 해시에 묶인 검증 guard만 새 산출물에 다시 연결했다. 기존 VLS/ARM 입력·정밀추적·EMCON·H3 수동 경로 우선 규칙을 유지했다.

## 4. 상태와 데이터 경계

- 새 UI는 관측 whitelist/기존 displayable object와 자함 인벤토리·사격해·자함 자세만 읽는다. 표적 truth/entity/RF 배열 직접 참조 없음.
- 추가 감사에서 관측 해면충돌 표식과 KILL_ASSESSMENT가 함께 남은 표시 가능 트랙의 미리보기 OK/native TRACK_SUPPORT_BLOCKED 불일치를 재현했다. 새 private 관측 사본에 이 기존 관측 표식과 보호 식별을 private 관측 whitelist에 보존했다. 내부 관문에는 표시 숨김 정책을 중복 적용하지 않고, 화면에는 기존 표시 가능한 트랙/마지막 보고만 사용한다. 실제 발사 관문은 바꾸지 않았고 숨긴 보호 트랙의 경로 거부를 포함한 지원 차단 사례를 추가해 최종본으로 회귀를 다시 실행했다. 변경 전 증거: evidence/development/support-before.json.
- 하푼 미리보기는 원본 관문 3개와 readiness 본문을 byte 동일하게 추출해 private 관측 Map/발사기 사본에서 실행한다. 공유 own-frame 캐시 대신 같은 프레임 생성식의 private 결과를 사용한다. 추출 SHA는 native-preview-manifest.json.
- 함포는 공개 snapshot의 FCQ/해와 native clearance/releaseGate를 읽고, 최종 요청은 native API가 다시 판정한다. 탄도·FCQ를 UI에서 재구현하지 않았다.
- UI queue/선택/편집 띠는 저장하지 않는다. 원래 routeDraft 저장 규칙은 보존한다. 자함 전환/epoch/시간 되감기 시 임시 명령을 폐기한다.
- 하푼 발사 저널은 자함의 발사 확인 id/tube/releaseStep에만 사용한다. 비행 중 실제 미사일 위치를 표시하지 않는다.

## 5. 시험 준비와 실행 시간

테스트 fixture는 보고서에만 들어가며 제품에는 __MD_TEST__/__MB_TEST__/__MC_TEST__가 없다. 합성 관측 트랙 시험과 실제 자연 RF/WebGL 비행을 구분했다. 두 함정·두 지도·두 크기의 새 UI 시험은 실제 포/하푼 런타임과 fixed tick을 사용했다.

| 작업 | 실제 실행(s) |
|---|---:|
| MAP_D native | 35.687 |
| MAP_D UI | 897.303 |
| MAP_D 경계 | 338.854 |
| 도메인 | 1795.395 |
| 기존 UI 파이프라인 | 2612.725 |
| 종료기/world/WebGL 파이프라인 | 1474.447 |

위 시간은 일부 병렬 실행된 각 파이프라인의 wall time이므로 합계가 전체 소요시간은 아니다. 헤드리스 Chromium/SwiftShader 환경이며 실제 휴대폰 FPS를 측정한 결과는 아니다.

초기 시험 준비에서 독립 시나리오의 gun.clear()가 급탄 시간을 남기던 것을 fixture gun.reset()으로 교정했다. ENV status()는 async로 await하고, 경로 띠는 다음 rAF의 표시를 기다려 검사한다. 제품 기능/관문 임계값을 완화하지 않았다. 초기 로그는 evidence/development에 따로 보존하며 최종 통과 수에 넣지 않는다.

## 6. 제출과 범위 밖

- HTML ZIP과 REPORT ZIP을 분리하고 원격 readback SHA/ZIP CRC를 확인한다. 보고서 ZIP의 REPORT.html을 열면 캡처를 볼 수 있다.
- main 병합·release·tag·aegis-smoke.yml 변경 없음. 사용자 병합용 PR만 생성한다.
- CG Mk45 Mod2 포구속도 823→760 보정, SAM 사거리표 특이점, SOV_B/TMA, 소브레멘니 센서는 이번에 수정하지 않았다.
- 기존 자연 관측 일부 비명중 결과를 그대로 보존했다. 이번 작업은 성공률/기동/유도 계수 수정이 아니다.

