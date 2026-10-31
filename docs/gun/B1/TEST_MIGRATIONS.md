# GUN_B1 시험 이관과 유지한 실패

제품의 비행·사통 조건이나 시험 허용치를 완화하지 않았다. 원래 MAP_E 시험 파일도 수정하지 않았다. 실제 source SHA와 실행 HTML SHA는 원시 JSON에 보존한다.

## 요청된 새 기능과 충돌하는 두 단언

`run_test_migrations.py`는 원래 시험 본문을 메모리에서 읽고 아래 기대 한 줄씩을 교체한다. AIR fixture의 native EKF 초기화도 아래에 명시한 대로 추가한다. 원래 실행은 `evidence/regression/`, 이관 실행은 `evidence/regression-migrated/`, source hash·정확한 치환문은 `evidence/test-migrations/`에 따로 둔다.

1. `verify_d_ui.py`: AIR를 항상 `NOT_SURFACE_TRACK`으로 거부하던 기대를 `VELOCITY_UNCERTAINTY`로 변경한다. 원래 fixture는 native 기본 속도 σ=80m/s로 초기화되어 새 대공 품질 상한 30m/s를 넘으므로 **여전히 발사 불가**여야 한다. `legacy-air-probe.json`은 실제 원인을 확인한 기록이다. 실제 3D 관측을 가진 AIR의 허용·경고·거부는 GUN_B1 신규 UI/native 시험에서 검증한다.
2. `verify_d_edges.py`: CG의 옛 Mod2 최대 22,000m 기대를 요청된 Mod4 24,000m로 변경한다. DDG 24,000m와 최소 800m는 그대로다.

## CG exact-state 3건: 변경하지 않은 기대값

CG idle/raid/damaged의 `samePhysicalState`가 다르다. 두 문의 moduleId와 HE/MFF 구성이 달라지고, 동일 위치의 탄약 질량 노드가 둘로 나뉘어 IEEE-754 합산 순서가 변한다. 총 질량은 같으나 cg.x가 약 8.88e-16m 달라지며 이후 정수역학 값에도 작은 차이가 전파된다. `verify_mass_split.py`는 복사한 노드 목록에서만 이 원인을 재현한다. 실제 게임의 질량 계산기나 부동소수 허용치는 바꾸지 않았다.

HP·침수·모듈 손상·VLS·CIWS·함포 발사 수·기존 관측·전투 RNG는 기준과 같다. 세 원래 exact-state 단언은 실패로 남긴다. `docs/map/E/approved-raid-baselines.json`의 승인 entries는 갱신하지 않았다. `raid-reference-test-guard.json`은 새 코드에서 동결 기대값을 실행하기 위한 core hash guard만 별도로 기록하며, 기대값 entries는 MAP_E와 동일하다. 이번 산출물 검토 후 사용자가 승인하면 다음 단계에서 기준값을 갱신할 수 있다.

## 시간 기반 UI 검사

다수의 full-fixed-tick 작업을 동시에 실행하는 중 애니메이션 샘플 수/그림 동기화 단언이 실패한 기록은 `evidence/regression/`에 그대로 보존한다. `run_idle_ui.py`는 반복 효과 시험·다른 브라우저 작업이 끝난 뒤 같은 원본 단언을 다시 실행하고, 누락된 후속 UI suite도 실행한다. 결과는 `evidence/regression-idle/`에 격리한다. 샘플 수·시간·좌표 허용치를 변경하지 않는다. 실행 비용 측정은 이 호스트의 관측값이며 실제 휴대폰 FPS 측정이 아니다.

## 수동 인계 시험의 로그 이름

초기 `verify_ui_handoff.py`는 로그의 action을 `GUN_COMMAND`로 예상했지만, 기존 note 함수가 추가 데이터의 `action:'FIRE'`를 병합한다. 실제 단발은 1회 정상 수행됐고 `metrics.gunRequests`도 1이었다. 단언을 **FIRE takeover 이벤트 1개 + gunRequests 정확히 1**로 수정하고 실제 클릭·사격을 재실행했다. 제품 코드는 이 시험 정정 때문에 바꾸지 않았다. 원인은 `evidence/ui-handoff/assertion-correction.json`에 남겼다.

## EW 저장 왕복 원시 비교

EW 동작 단언 94개는 모두 통과했고 H3 195개는 전체 원시 결과까지 동일하다. EW의 원래 전체 export 비교는 DDG/CG 두 건에서 false다. 차이는 저장의 CG Mod4 ID와 HE180/MFF180 배분뿐(각24/28 scalar 경로)이다. 원래 raw same=false와 기대값은 그대로 둔다. `verify_ew_inventory_delta.py`는 정확한 inventory 경로와 요청된 전후 값만 허용하고, 복사본에서 이 차이만 되돌렸을 때 나머지 전체 JSON이 byte 의미상 동일한지 검사한다. 사후 원인 분해이며 EW 검사나 승인 기대값 갱신이 아니다.

## AIR 진단 fixture 초기화 순서

첫 이관 실행은 210/213이었다. PIP 세 조건은 첫 preview 시 EKF가 없어서 `AIR_TRACK_3D_STATE_REQUIRED`를 반환했고, 다음 native lazy 초기화 후에는 기본 속도 σ=80m/s 때문에 `VELOCITY_UNCERTAINTY`를 표시했다. 양쪽 모두 실제 발사는 차단됐으며 첫 실행 JSON/로그는 `evidence/test-migrations/first-ui-run`과 `first-ui.log`에 보존한다.

재실행 fixture는 `trackEkfInit(tr)`을 명시한다. 새 수치나 유리한 공분산을 넣지 않고 native 기본 σ=80을 그대로 사용한다. 각 조건에서 (1) EKF를 제거한 복사 관측은 정확히 `AIR_TRACK_3D_STATE_REQUIRED`, (2) native 초기화 후 속도 σ는 정확히80임을 추가로 assert한다. 그 상태의 기존 AIR 단언은 정확히 `VELOCITY_UNCERTAINTY`이며 발사 불가를 확인한다. 제품·검사 허용치 변경 없이 213/213으로 재확인했다. 실제 측정 품질의 AIR 허용/경고/거부는 신규 UI76/native36이 따로 검증한다.
