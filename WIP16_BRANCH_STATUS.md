# AEGIS v48 WIP16 — Branch / Handoff Status

갱신: 2026-10-03 (KST)

## 판정

**WIP16A 명시 범위 package/Chromium PASS / 전체 PR은 3D 통합 검사 실패로 HOLD / main·v48.1 보류.**

- branch: `WIP16`
- base: `main@d2b840bae95267ffc53bfda847442b2211c1ab03`
- user upload commit: `3be1ba489a0f8b934b8d2000aec408b56ea863af`
- stable baseline: `Aegis_SIM_v48.html`
- candidate: `Aegis_SIM_v48_WIP16A.html`, `7,354,882 bytes`
- SHA-256: `6fba8ad6225e83fc86c7f07d275ab58feb4b8027d83a29aabeba3f6fa2382f24`
- remote/local Git blob exact: `d0d8b3de795716cb21ba2f7ba9673b8024dc2ceb`
- status/checksums: `AEGIS_PLAN_STATUS_v48_WIP16A.md`, `SHA256SUMS_v48_WIP16A.txt`
- current PR / Actions / remaining approval: `docs/wip16/A/CLOSEOUT.md`

사용자 HTML은 재작성하지 않았다. 지원 빌더의 gzip 헤더와 runtime 검사 격리를 수정하고 후보 전용 CI를 추가한다. main / tag / release / v48.1 승격은 아직 실행하지 않는다.

## 변경

- Mk244 고정 분산 `3.0 mil / 80% diameter`는 유지.
- 기존 수-degree gunfire gate 대신 사거리와 고정 탄착군 반경을 반영한 **metre-scale burst-centre gate** 사용.
- ballistic solution의 `predictedMissM`도 fire authorization에 사용.
- 기존 WIP112 exposed `fins` system box를 실제 CIWS projectile control-surface hit geometry로 연결.
- control-surface hit는 즉시 critical kill을 만들지 않고 작은 직접 구조피해 + 기존 WIP112/WIP113 fins/control-authority 경로 사용.
- WIP104 closed-loop spotting 상수는 수정하지 않음.
- WIP103 diagnostic fixture는 case reset 때 tracking ID / gun-local RNG / correlated aim-error를 비워 회귀 격리를 보강. production gameplay 변경 아님.

## 원본 지원 자료의 대표 검증

4 km / 280 m/s / 12 m / -20·0·+20° / seeds 23001·23002:

- v48 + diagnostic-reset-only: 3,472발 / 10 physical hits / 0.288%
- WIP16A acceptance: 1,098발 / 15 physical hits / 1.366%
- physical-hit rate 약 4.74×
- 발사탄 약 68.4% 감소
- firing residual 중앙값 0.0847° → 0.0338°
- WIP16A physical hit: BODY 7 / CONTROL_SURFACE 8
- 양쪽 모두 이 6조건의 함정 피격은 0이므로 Pk 배수 주장이 아님.

1.5 km / 350 m/s late-entry 4 seeds에서는 1건 ship penetration이 남아 보장요격으로 만들지 않았다.

## 원본 지원 자료의 검사

- package / C55 / source preservation / syntax: `64/64 PASS`
- runtime acceptance: `13/13 PASS`
- stable v48 → WIP16A exact rebuild: PASS
- core self-test failures: `0`
- page errors: `0`

상세 계획: `docs/wip16/WIP16_PHALANX_FIRE_CONTROL.md`


직접 재검사 결과는 package `64/64`, 추가 무결성·전체 JS·exact rebuild `21/21 PASS`다. 현재 Chromium은 `13/13 PASS`, 전용 workflow `4/4 job PASS`다. 일반 smoke는 `29/30 PASS`, 후보를 연 `aegis-3d-render`가 실패했다. 정확한 증거는 마감 기록을 따른다. 위 원본 runtime aggregate는 이전 audit 순서에서 나온 역사 기록이며 새 fresh-context 회귀값과 혼합하지 않는다.
