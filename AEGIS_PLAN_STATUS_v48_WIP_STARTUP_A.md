# AEGIS v48 WIP_STARTUP_A — 출항 전 함선 선택·초기화

갱신: 2026-10-03 UTC

**요청 단계 구현·로컬 회귀와 사용자 HTML 업로드·원격 exact 확인 완료. 원격 CI 검사 진행 예정.**

- 결과: `Aegis_SIM_v48_WIP_STARTUP_A.html`, `7,361,673 bytes`
- SHA-256: `94f5e9321fe1f04c5b43c4d8dca5b0762014c1cffe358ad92a81b8ffe70e7c92`
- Git blob SHA: `52310e0c6a58d3240ae9c2333cc9f61351f5e597`
- 기준: 사용자 WIP16B `7b63a62bb1cad123b7d7eb17c1fbe26452194c3ff2c637c09b4c48a2a6c8d76d`
- branch: `ship-startup-ddg-regression`, parent `WIP16@145532316e1f87435f50a8de4a271497f0d2f1ab`
- 사용자 업로드 commit: `6e05d8c21ba83aca4f29a37cbaa6ce151b6be9db`. 그 parent는 위 기준 commit이며 HTML 한 파일만 추가됐다. 원격 tree의 크기·Git blob이 로컬 검증본과 일치한다.
- 안정 main: `d2b840bae95267ffc53bfda847442b2211c1ab03`; 기존 PR #41은 미병합 상태 그대로다.
- `WIP_STARTUP_A`는 번호 미확정 상태를 유지하는 기능명 토큰이다.

함선 선택 전에 runtime 생성을 멈추고, 선택된 불변 profile로 자함·월드를 한 번 생성한다. 기존 subsystem builder/compatibility 참조는 그 객체에 결속한다. 선택 → 초기화 → 편성 → 출항 상태와 출항 gate를 추가했다. DDG-119 entity ID·profile revision·작전 snapshot schema는 유지했다. VLS 초기 재고와 재시작 heading/close-in 탄수는 profile에서 읽는다.

## 검증

| 검사 | 결과 | 증거 |
|---|---|---|
| C55 integrity·15 JS syntax·자산/profile 보존·exact rebuild | 34/34 PASS | `docs/ship-startup/A/evidence/package.json` |
| 선택 대기·거부·한 번 생성·clock 정지·분리·출항·재시작·이전 저장 | 15/15 PASS | `docs/ship-startup/A/evidence/startup.json` |
| 기존 WIP16 DDG 회귀와 fresh-context same-seed 반복 | 14/14 PASS | `docs/ship-startup/A/evidence/runtime.json.gz` |
| 기존 B 결과 대조 | PASS | `docs/ship-startup/A/evidence/baseline-comparison.json` |
| 실제 3D cut·read-only·복구·VLS·crew·부정 검사 | 13/13 PASS | `docs/ship-startup/A/evidence/renderer.json.gz` |

boot seed `1831565813` (`0x6d2b79f5`), Phalanx seeds `23001/23002`, bearings `-20/0/20°`, spotting seeds `21001/21002`. 원본과 후보 모두 발사 `1,132`, 명중 `16`, hit rate `1.4134275618%`, 결과 `STRUCT_FAIL 2 / INTERCEPT_FAIL_NO_HULL_HIT 1 / KILL 3`, 자함 피격 `0`. aggregate는 exact 일치한다. 상세 JSON float 10개에는 최대 약 `3.9e-13` 차이가 있어 전체 JSON byte/exact 일치로 기록하지 않는다. 기존 threshold와 후보 seed 반복 exact 검사는 통과했다.

기존 침수 fixture의 1×/8×/16×/64× fixed-step 회귀는 통과했다. 정상/손상 CIWS 순서, 표적 flooding·damage도 기존 runtime 검사에 포함된다. 3D에서 authoritative 피해/침수/구조/구획/crew 상태는 바뀌지 않았고 geometry 복원과 잘못된 mount/VLS binding 거부가 확인됐다. 전 범위 실비행·성능 벤치마크는 이번 완료 증거에 포함하지 않는다. 원격 CI는 지원 반영 후 별도로 기록한다.

## 범위와 다음 단계

벙커힐을 아직 운용 registry에 등록하지 않았다. 하푼/토마호크와 다함 동시 운용도 후속 범위다. 다음 구현은 벙커힐 불변 profile·model registration·필요 builder를 이번 선택/생성 경계에 연결하고 두 함선의 초기화·reset·3D 결속을 각각 검증하는 것이다.

큰 HTML은 지침 7.1대로 사용자가 업로드했고 원격 exact 확인을 마쳤다. 지원 반영에서 이전 B 세트는 동일 Git blob으로 `archive/v48/WIP16B/`에 이동한다. 새 전용 CI는 업로드 HTML을 덮어쓰지 않고 재구성본과 `cmp`한 뒤 lifecycle·기존 B 저장 복원·원본/후보 전투·3D 복구를 검사한다. 일반 smoke의 실제 3D 입력도 새 업로드로 바꾸고 선택 버튼을 눌러 초기화 대기를 해제한다. 나머지 일반 job에는 기존 역사 payload가 포함된다. CI와 PR 결과는 후속 마감 기록에 추가한다. main/정식 v48 변경·승격·release/tag는 없다.

상태 문서와 HTML의 SHA-256은 `SHA256SUMS_v48_WIP_STARTUP_A.txt`를 따른다. 상세 구현·명령·한계는 `docs/ship-startup/A/README.md`에 있다.
