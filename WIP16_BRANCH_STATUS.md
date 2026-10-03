# AEGIS v48 WIP16 — Branch / Handoff Status

갱신: 2026-10-03 (KST)

## 판정

**WIP16A Phalanx fire-control stabilization 구현 및 명시 범위 검증 통과 / 사용자 gameplay 확인 대기 / 목표 안정판 v48.1.**

- branch: `WIP16`
- base: `main@d2b840bae95267ffc53bfda847442b2211c1ab03`
- stable baseline: `Aegis_SIM_v48.html`
- baseline SHA-256: `9e786ddb1331fcd496b6b9604cec87317667ebc501e99270cc33fd6ba1ab9e83`
- local candidate: `Aegis_SIM_v48_WIP16A.html`
- candidate bytes: `7,354,882`
- candidate SHA-256: `6fba8ad6225e83fc86c7f07d275ab58feb4b8027d83a29aabeba3f6fa2382f24`
- decoded main SHA-256: `8e5fb5f435c6f164879d4246feb5f548ceabef087701ac760c0132cb1dac0669`
- target after approval: **v48.1**

대형 HTML은 이 커밋에서 원격 업로드하지 않는다. 사용자 확인·업로드 전에는 main / PR / tag / release를 변경하지 않는다.

## 변경

- Mk244 고정 분산 `3.0 mil / 80% diameter`는 유지.
- 기존 수-degree gunfire gate 대신 사거리와 고정 탄착군 반경을 반영한 **metre-scale burst-centre gate** 사용.
- ballistic solution의 `predictedMissM`도 fire authorization에 사용.
- 기존 WIP112 exposed `fins` system box를 실제 CIWS projectile control-surface hit geometry로 연결.
- control-surface hit는 즉시 critical kill을 만들지 않고 작은 직접 구조피해 + 기존 WIP112/WIP113 fins/control-authority 경로 사용.
- WIP104 closed-loop spotting 상수는 수정하지 않음.
- WIP103 diagnostic fixture는 case reset 때 tracking ID / gun-local RNG / correlated aim-error를 비워 회귀 격리를 보강. production gameplay 변경 아님.

## 대표 검증

4 km / 280 m/s / 12 m / -20·0·+20° / seeds 23001·23002:

- v48 + diagnostic-reset-only: 3,472발 / 10 physical hits / 0.288%
- WIP16A acceptance: 1,098발 / 15 physical hits / 1.366%
- physical-hit rate 약 4.74×
- 발사탄 약 68.4% 감소
- firing residual 중앙값 0.0847° → 0.0338°
- WIP16A physical hit: BODY 7 / CONTROL_SURFACE 8
- 양쪽 모두 이 6조건의 함정 피격은 0이므로 Pk 배수 주장이 아님.

1.5 km / 350 m/s late-entry 4 seeds에서는 1건 ship penetration이 남아 보장요격으로 만들지 않았다.

## 최종 검사

- package / C55 / source preservation / syntax: `64/64 PASS`
- runtime acceptance: `13/13 PASS`
- stable v48 → WIP16A exact rebuild: PASS
- core self-test failures: `0`
- page errors: `0`

상세 계획: `docs/wip16/WIP16_PHALANX_FIRE_CONTROL.md`
