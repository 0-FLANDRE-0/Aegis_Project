# WIP16A — Phalanx Fire-Control Stabilization

작성: 2026-10-03 (KST)

## 목적

v48의 Phalanx는 높은 local-track 품질에서도 실제 20 mm physical-hit 비율이 낮고 다량의 탄을 소비했다. WIP16A는 ammunition dispersion을 임의 축소하지 않고 다음 두 경로를 수정한다.

1. **언제 발사하는가** — 현재 사거리에서 탄착군 중심이 표적에 충분히 가까울 때만 사격.
2. **무엇을 실제로 맞출 수 있는가** — 몸통 capsule 외에 이미 존재하는 WIP112 exposed fins/control surfaces를 실제 projectile surface로 연결.

## Fire-control contract

`WIP16_PHALANX_FIRE_CONTROL_MODEL`은 다음을 사용한다.

- 현재 range
- 고정 Mk244 3.0 mil 80%-diameter group radius
- turret residual을 metres of burst-centre error로 환산한 값
- ballistic solver `predictedMissM`
- ENGAGE hysteresis

TRACK/ENGAGE 상태 이름과 local radar track source는 유지한다.

## Physical-hit contract

- body capsule intersection은 기존 권위 유지.
- body miss일 때만 WIP112 `fins` AABB를 missile-local frame에서 swept test.
- fin/control-surface hit는 body critical hit와 동일하게 취급하지 않음.
- 즉시 critical kill 확률 0, 작은 direct structure damage.
- WIP112 observer / WIP113 control-authority degradation은 기존 경로 그대로 사용.

단순히 전체 ASM hitbox를 부풀리는 변경은 하지 않는다.

## 보존

- Mk244 dispersion: 3.0 mil exact.
- muzzle velocity / drag / fire rate unchanged.
- Phalanx radar/sensor model unchanged.
- WIP104 spotting constants unchanged.
- SeaRAM logic unchanged.
- WIP15 Nulka/SRBOC, B3 DL/GPS, B4 loft, WIP15C surface engagement/flood repair unchanged.

## 검증 기준

- same-condition 4 km / 280 m/s physical-hit rate >= 1%.
- BODY와 CONTROL_SURFACE hit가 모두 실제 발생.
- firing-frame turret residual median < 0.05°.
- late-entry condition에서 방어 실패 가능성이 남아 있을 것.
- core self-test zero, page-error zero.
- package exact rebuild.
- 기존 CIWS maneuver estimator / damage ordering / WIP13A flooding time-scale 회귀 보존.

## 승격

사용자가 실제 gameplay 체감을 확인하고 승인하면 WIP16A를 정식 `v48.1` 후보로 승격한다. 승인 전 main/tag/release 변경 금지.
