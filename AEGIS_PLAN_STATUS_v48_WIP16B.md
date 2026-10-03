# AEGIS v48 WIP16B — Plan / Status

갱신: 2026-10-03 (KST)

**C5 렌더러 연결·로컬 package·Chromium·전체 CI 통과 / HTML 사용자 업로드 대기 / main·v48.1 승격 보류.**

## 기준 파일

- branch: `WIP16`; base: `main@d2b840bae95267ffc53bfda847442b2211c1ab03`
- 수정 기준: 사용자 업로드 `Aegis_SIM_v48_WIP16A.html`, SHA-256 `6fba8ad6225e83fc86c7f07d275ab58feb4b8027d83a29aabeba3f6fa2382f24`.
- 새 후보: `Aegis_SIM_v48_WIP16B.html`, **7,357,036 bytes**.
- SHA-256: `7b63a62bb1cad123b7d7eb17c1fbe26452194c3ff2c637c09b4c48a2a6c8d76d`.
- Git blob: `d47126f8296f3bde6b81af0ce1a2668a3c79f9cf`.
- decoded main SHA-256: `824dffddd510ddd9d0a18b64b00b7e4e1941a7d6df972b17e1d78438e1d110a2`.
- 재현 가능한 소형 빌더·패치·검사: [docs/wip16/B/](docs/wip16/B/README.md).

## 수정 내용과 실제 원인

진입·이탈 구멍의 표면 검색은 기존에도 `HULL_3:SIM_antifoul`에 성공했다. 내부 화면의 SwiftShader GPU 제출이 느려 cooperative cut job의 진행과 메시 공개가 늦어졌고, 기존 audit는 공개되지 않은 구멍을 `meshMatched:false`로 표시했다. 재현에서 65.7초 뒤에도 commit 0·geometry revision 0이었다.

WIP16B는 필수 구멍 생성 작업 중에 직전 canvas를 유지하고, geometry commit 뒤 WebGL 제출을 재개한다. 기존 cut/fold 알고리즘·구멍 면적·프레임 작업 예산과 시뮬레이션 틱은 그대로 유지한다.

BridgeMaster 검사는 실제 `NAV_SCANNER`, 중첩 마스트 좌표를 ship-local SI로 환산한 장착점, parent chain, scanner mesh 2개, 마스트 draw 17개, 실제 기능 rotor 1개를 확인한다. 옛 우현 야드암·14개 draw 계약은 현재 C5 모델에 적용하지 않는다. imported root의 기존 보호 스키마 binding도 연결했다.

전체 renderer contract는 현재 source envelope, C5 model, 등록된 96개 VLS 셀과 실제 hinge/panel의 일대일 연결, 함포 joint, profile, radar controls와 내부·승조원 계약을 검사한다. VLS 피격 체적 중심을 개별 셀 등록점으로 오인하지 않는다. C5에 등록되지 않은 옛 구명뗏목 6개 검사에는 `applicable:false`를 명시하며 PASS로 기록하지 않는다. legacy debug model의 기존 검사 경로는 유지한다.

## 보존 범위

- C55 records 0–12 compressed bytes 동일.
- main script의 3D 렌더러 시작 전 전체 source 동일.
- 무기·센서·nav/DL/loft·전투 난수·피해 solver·구획·승조원·모델 geometry 변경 없음.
- 사용자 업로드 WIP16A HTML과 원본 closeout/evidence는 그대로 보존.
- 큰 HTML을 커넥터로 업로드하지 않는다. 사용자가 이 새 파일을 `WIP16`에 올린 뒤 원격 크기·Git blob·SHA-256을 대조한다.

## 검증

- 로컬 package: **34/34 PASS**. 모든 record hash, executable script 15개, asset/source 보존과 exact rebuild 포함.
- 실제 geometry 초기 실행: 실제 구멍 2개, 중심 ray 통과, 상태 불변, 내부/crew, geometry restore PASS. 당시 실패한 mast draw 수·VLS 등록 검사 기준은 현재 semantic binding으로 수정했다.
- 최종 tested code head: `75a29792f9d83c8e348c7ce4d89c1dbb54d75150`.
- WIP16B Chromium: [37094473097](https://github.com/0-FLANDRE-0/Aegis_Project/actions/runs/37094473097), **1/1 job PASS**. 패키지 **34/34**, renderer/recovery/negative checks **13/13**, 기존 Phalanx runtime **13/13 PASS**. core/page errors `0`; CI 생성 HTML과 로컬 SHA-256 exact 일치.
- WIP16A preservation: [37094473090](https://github.com/0-FLANDRE-0/Aegis_Project/actions/runs/37094473090), **4/4 job PASS**. 사용자 업로드 원본의 exact package 및 Chromium 검사 유지.
- 일반 smoke: [37094473114](https://github.com/0-FLANDRE-0/Aegis_Project/actions/runs/37094473114), **30/30 job PASS**. 실패하던 `aegis-3d-render`가 재구성 WIP16B에서 전체 contract, 두 실제 구멍·attachment·면적 보존·상태 불변, 내부/crew와 BridgeMaster 검사 모두 PASS.
- 일반 smoke의 3D job은 빌더로 생성한 WIP16B를 열고 `rendered-source.txt`에 기록한다. 다른 일반 job에는 역사 payload와 자동 선택 검사가 혼재하므로 전체를 WIP16B 전용 회귀로 주장하지 않는다.
- 실제 Chromium에서 잘못된 센서 장착 위치와 잘못된 VLS 셀 binding은 FAIL, ship-root 이동/회전 뒤 정상 ship-local 장착 검사는 PASS, 원본 메시 복구도 PASS.
- 캡처는 초기 HIGH preset 구멍 검사 뒤 LOW preset에서 양현 시점으로 수집했다. 원격 artifact 출처와 전체 행은 `docs/wip16/B/evidence/chromium.json`, 일반 3D 결과는 `evidence/general_3d.json`에 보존한다.
- 로컬 Chromium은 설치된 실행 파일이 없어 미실행. 실제 브라우저 검증은 Actions Chromium/SwiftShader에서 수행한다.

## 인계와 다음 작업

PR [#41](https://github.com/0-FLANDRE-0/Aegis_Project/pull/41)을 계속 사용한다. 새 브랜치는 만들지 않았다. 안정 기준은 v48이며 main 병합·v48.1 승격·release/tag는 실행하지 않았다.

새 HTML의 사용자 업로드와 원격 exact 확인을 마치면 현재 PR의 최종 통합 판정을 갱신한다. 이후 범위는 출항 전 함선 선택·생성·초기화 공통화 → 기존 DDG-119 동작 보존 → 벙커힐 프로필/모델 연결이다. 하푼·토마호크와 새 함선의 기능 구현은 이번 수정 범위에 포함하지 않는다.
