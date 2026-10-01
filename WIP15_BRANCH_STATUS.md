# AEGIS v48 WIP15 — Branch / Preparation Status

작성: 2026-10-01 (KST)

## 현재 판정

**WIP15 BRANCH CREATED / PREPARATION ONLY. RUNTIME CODE NOT STARTED.**

- repository: `0-FLANDRE-0/Aegis_Project`
- branch: `WIP15`
- base: `main` commit `dc8f67b01dc515441d61f057caffc4e550c0bae8`
- runtime baseline: `Aegis_SIM_v48_WIP14B4.html`
- baseline SHA-256: `03de975ddac38c192eae1572b2588bba49defcb148a2fd9ae7b6921f4e7355e2`
- baseline Git blob SHA: `5e454823e4fd8c608d05ecd5e880a13cf5e5b2ce`
- WIP14 feature scope: CLOSED / merged via PR #38

이번 branch에서는 아직 HTML/runtime 코드를 수정하지 않는다. 새 simulator artifact, PR, merge, release/tag도 만들지 않는다.

## WIP15 목표

WIP15의 첫 구현 단계는 Nulka가 아니다.

먼저 현재 soft-kill launcher 표현의 불일치를 닫는다.

- 3D 모델 의도/표현: **PORT 3 + STARBOARD 3 = 총 6기**
- 각 SRBOC launcher: **6 tubes**
- 프로젝트 목표 inventory: **6 × 6 = 36 Mk 214 rounds**
- 현재 runtime: **4 launchers / 24 rounds**
- 현재 chaff spawn origin: 실제 개별 launcher/tube muzzle이 아닌 추상 발사점 사용

따라서 WIP15A는 다음을 canonical contract로 만든다.

1. 6개 launcher hardpoint
2. launcher당 6개 tube/muzzle
3. runtime inventory 36발
4. 발사기별 재고와 선택 권위
5. 실제 tube muzzle에서 Mk 214 생성
6. 함 자세/이동에 따른 muzzle world transform 및 초기 함 속도 상속
7. UI / mass ledger / snapshot / reset / soft-kill selector의 동일 layout 소비
8. 2D/3D는 동일 authoritative layout을 읽고 렌더링만 수행

## 단계

### WIP15A — SRBOC Canonical Layout & Physical Launch Origin

구현 전 audit → canonical hardpoint → runtime migration → physical spawn → regression 순으로 진행한다.

세부 계약:
`docs/wip15/WIP15_SRBOC_NULKA_PREP_PLAN.md`

### WIP15B — Nulka Active Decoy

WIP15A가 닫힌 뒤 착수한다.

Nulka는 기존 chaff entity의 단순 variant로 만들지 않고 별도 active expendable decoy 계층으로 설계한다. 단, 실제 구현 범위와 공개근거/SIM_TUNED 항목은 WIP15A 종료 뒤 다시 확정한다.

## 이번 준비 단계에서 하지 않은 것

- `Aegis_SIM_v48_WIP14B4.html` 수정
- SRBOC launcher count/inventory 수정
- 3D launcher geometry 이동
- Mk 214 spawn origin 수정
- snapshot schema/revision 수정
- Nulka entity/RF source/flight model 구현
- soft-kill doctrine tuning
- main 수정
- PR/merge/release/tag 생성

## 다음 작업 시작 조건

다음 구현 turn에서 가장 먼저 B4 source의 다음 항목을 실제 코드 기준으로 다시 audit한다.

- SRBOC runtime profile / launcher state / inventory
- Mk 214 spawn function과 초기 position/velocity
- soft-kill auto launcher selection
- 3D SRBOC six-launcher mesh 생성 위치/transform
- mass ledger의 Mk 214 위치/수량
- operational snapshot codec/revision
- reset/lifecycle
- UI ammo readout

그 audit 결과를 기준으로 WIP15A 구현 범위를 잠그고 코드 변경을 시작한다.
