# AEGIS v48 WIP15 — SRBOC Physical Launcher / Nulka Preparation Plan

작성: 2026-10-01 (KST)  
기준: `main` / `Aegis_SIM_v48_WIP14B4.html`

## 1. 목적

WIP15는 soft-kill 장비의 **물리 설치 위치와 runtime 상태를 하나의 canonical layout으로 통합**하는 단계에서 시작한다.

사용자가 확인한 현재 함정 3D 모델은 한쪽 현에 SRBOC 6-tube launcher 3기를 가지며, 반대 현까지 합쳐 **6 launchers / 36 tubes**를 의도한다.

반면 WIP14B4 runtime은 4-launcher / 24-round 상태를 사용하고, Mk 214의 생성 위치도 개별 launcher/tube muzzle과 직접 연결되어 있지 않다.

이 불일치를 닫기 전에는 Nulka를 추가하지 않는다.

## 2. WIP15A — SRBOC Canonical Layout

### 2.1 Source-of-truth 원칙

3D renderer 안에만 존재하는 launcher 좌표를 simulation에서 역으로 읽지 않는다.

구현 시 다음 순서를 사용한다.

```text
ShipProfile / canonical soft-kill hardpoints
        ↓
launcher runtime state
        ↓
tube inventory / selected tube
        ↓
ship-local muzzle transform
        ↓
world spawn position + ship kinematics
        ↓
Mk 214 flight / deployment
```

3D renderer는 같은 canonical hardpoint/tube layout을 읽어서 mesh를 만든다.

즉 3D가 physics source가 되는 것이 아니라 **profile geometry가 physics와 3D의 공통 source**가 된다.

### 2.2 Canonical launcher identities

구현 전 실제 B4 mesh transform을 audit한 뒤 명칭을 확정하되 기본 구조는 다음을 권장한다.

- `STBD_FWD`
- `STBD_MID`
- `STBD_AFT`
- `PORT_FWD`
- `PORT_MID`
- `PORT_AFT`

각 launcher는 다음을 선언한다.

- ship-local mount origin
- mount orientation / allowed launch sector
- 6개의 tube muzzle local offset/orientation
- tube loaded/empty state
- launcher health/availability
- side / station metadata

좌표 숫자는 renderer의 현재 모델과 사용자 확인 이미지를 대조한 뒤 정한다. 확인 전 추측 좌표를 하드코딩하지 않는다.

### 2.3 Runtime inventory

목표 canonical state:

```text
launcher count: 6
tubes per launcher: 6
total loaded Mk 214: 36
```

재고는 단순 총합 하나가 아니라 launcher/tube 상태에서 파생한다.

- launcher별 잔탄
- 전체 잔탄
- next available tube
- damaged/empty launcher
- soft-kill auto가 사용할 수 있는 launcher

가 동일 state를 사용해야 한다.

### 2.4 Physical launch origin

Mk 214 발사 시 다음을 지킨다.

1. launcher를 선택한다.
2. 해당 launcher의 loaded tube 하나를 선택한다.
3. tube muzzle의 ship-local transform을 현재 함 자세에 적용한다.
4. 그 world muzzle position에서 projectile을 생성한다.
5. 초기 projectile velocity에는 launcher ejection/launch velocity와 **현재 함의 병진 속도**를 합성한다.
6. 필요하면 함의 각속도에 따른 local-point velocity도 포함하되 실제 B4 ship dynamics API와 먼저 대조한다.
7. tube inventory는 실제 spawn 승인 시점에만 소모한다.

UI click이나 3D frame은 spawn 권위가 아니다.

### 2.5 Launcher selection

기존 위협 bearing 기반 선택 정책은 유지 가능한 부분을 보존하되, 4개의 추상 quadrant launcher ID를 6개 실제 station으로 바꾼다.

선택에는 최소 다음을 고려한다.

- threat bearing
- launcher side/station
- launch sector
- launcher/tube availability
- launcher damage
- cooldown/release policy

정확한 tactical doctrine는 WIP15A에서 불필요하게 새로 튜닝하지 않는다. 첫 목표는 **기존 동작을 6개 실제 launcher geometry에 안전하게 매핑**하는 것이다.

### 2.6 Mass ledger

현재 Mk 214 mass를 함 중심의 단일 점으로 처리하는 경로가 있다면 launcher/tube inventory 기반으로 분산한다.

- 각 launcher에 남은 round mass
- mount 자체 질량이 이미 다른 geometry/mass source에 존재하는지 audit
- 같은 질량을 renderer와 runtime에 중복 계상하지 않음

효과가 작더라도 canonical ownership을 맞춘다.

### 2.7 Operational snapshot / reset

4-launcher 배열을 6-launcher로 바꾸므로 기존 snapshot contract를 반드시 audit한다.

옵션:

- schema/revision migration을 명시적으로 제공하거나
- 구형 4-launcher snapshot을 호환 불가로 명시적으로 거부

silent padding/truncation은 금지한다.

reset 후에는 6 launchers × 6 loaded tubes = 36발이 정확히 복원되어야 한다.

## 3. 3D 정합

현재 보이는 6개의 launcher mesh가 실제로 어떤 local transform에서 생성되는지 source를 먼저 확인한다.

구현 뒤에는 renderer 내부의 독립 숫자 배열을 없애거나 compatibility wrapper로 낮추고 canonical hardpoint data를 소비한다.

필수 확인:

- PORT/STBD 각각 3기
- launcher mesh center와 canonical mount origin 일치
- 각 6 tube muzzle 방향과 physical spawn line 일치
- 함 선회/roll/pitch/translation 중에도 spawn이 mesh에서 분리되지 않음
- renderer는 presentation-only 유지

## 4. WIP15A 필수 회귀

1. launcher state 정확히 6개.
2. 각 launcher tube 정확히 6개.
3. reset 직후 총 36 rounds.
4. 각 launcher를 강제 선택하여 6개 muzzle 모두에서 spawn origin 검증.
5. 36회 정상 발사 뒤 전체 empty.
6. 한 launcher의 6발 소진은 다른 launcher inventory를 변경하지 않음.
7. damaged/empty launcher는 선택에서 제외.
8. 위협 방위별 선택 결과가 허용 launch sector 안에 있음.
9. 함 이동 중 spawn이 함 중심이 아니라 해당 muzzle을 따라감.
10. 초기 projectile velocity가 필요한 ship motion을 상속.
11. 1×/8×/16× fixed-step 동일 seed의 launcher/tube consumption history 일치.
12. 2D/3D 전환이 inventory/spawn 결과를 바꾸지 않음.
13. UI 총잔탄이 runtime tube 합과 일치.
14. mass ledger의 Mk 214 mass가 tube inventory 합과 일치.
15. snapshot round-trip 또는 명시적 migration/rejection fixture PASS.
16. 기존 chaff cloud/RF effect 결과에 의도하지 않은 변경 없음.
17. WIP14 B2/B3/B4 nav/DL/loft/VLS 핵심 회귀 보존.

## 5. WIP15B — Nulka는 이후

Nulka 구현은 WIP15A 완료 후 별도 gate로 진행한다.

준비 단계의 설계 원칙만 고정한다.

- Mk 214 chaff와 별도의 active expendable decoy entity
- 별도 inventory/canister/launcher capability
- active RF source를 기존 ASM seeker return competition에 연결
- truth identity로 미사일의 기만 대상을 강제하지 않음
- flight/hover/deception 수치는 공개 근거와 SIM_TUNED를 구분
- soft-kill threat manager와 연동하되 Nulka 발사 조건/자원/쿨다운은 chaff와 별도

**WIP15A 코드가 닫히기 전 Nulka runtime 구현을 시작하지 않는다.**

## 6. 준비 단계 종료 조건

이번 preparation-only commit은 다음만 만족하면 끝난다.

- WIP15 branch가 WIP14B4가 들어간 최신 main에서 분기됨
- WIP15 branch/status 문서 존재
- WIP15A/WIP15B 범위와 순서 문서화
- baseline HTML은 byte 변경 없음
- runtime/test/workflow 구현 변경 없음
- PR/merge 없음
