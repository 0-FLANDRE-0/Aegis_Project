# AEGIS v48 WIP16 — Branch / Handoff Status

갱신: 2026-10-03 (KST)

**WIP16B 업로드·최종 CI 검증 완료 / 기술적 통합 PASS / main 명시 승인 대기·v48.1 승격 보류.**

- branch: `WIP16`; 안정 기준 `main@d2b840bae95267ffc53bfda847442b2211c1ab03`.
- tested code head: `75a29792f9d83c8e348c7ce4d89c1dbb54d75150`.
- 최종 tested support head: `05cd0ebcb7c0fb8a7bfcd2f65aa46184545585d4`. 업로드 guard·검사 초기 seed·geometry 대기를 보완했으며 HTML은 동일하다.
- 전달 후보: `Aegis_SIM_v48_WIP16B.html`, `7,357,036 bytes`.
- SHA-256: `7b63a62bb1cad123b7d7eb17c1fbe26452194c3ff2c637c09b4c48a2a6c8d76d`.
- Git blob: `d47126f8296f3bde6b81af0ce1a2668a3c79f9cf`.
- 사용자 업로드 commit `7562bb0925e2b85521d37fefd2c81898ed6de18a`의 원격 WIP16B 크기·Git blob이 검증본과 exact 일치한다. 업로드 commit은 B HTML만 추가하며 stable v48와 WIP16A 원본 blob은 동일하다.
- 상태/체크섬: `AEGIS_PLAN_STATUS_v48_WIP16B.md`, `SHA256SUMS_v48_WIP16B.txt`.
- 구현·소형 빌더·검사·증거: [docs/wip16/B/](docs/wip16/B/README.md).
- Codex 새 환경용 [개발 인계서](docs/wip16/B/AEGIS_CODEX_HANDOFF_WIP16B.md). 이 인계 추가는 문서 변경이며 HTML·검증 코드·main 상태는 동일하다.
- 로컬 package **34/34**, B Chromium renderer/recovery/negative **13/13**, 기존 runtime **13/13 PASS**.
- B workflow [37094473097](https://github.com/0-FLANDRE-0/Aegis_Project/actions/runs/37094473097) **1/1 job PASS**.
- 원본 보존 workflow [37094473090](https://github.com/0-FLANDRE-0/Aegis_Project/actions/runs/37094473090) **4/4 job PASS**.
- 일반 smoke [37094473114](https://github.com/0-FLANDRE-0/Aegis_Project/actions/runs/37094473114) **32/32 job PASS**. 3D job의 실제 입력은 재구성 B이며, 다른 일반 job에는 역사 payload가 섞여 있다.
- 최종 [B workflow](https://github.com/0-FLANDRE-0/Aegis_Project/actions/runs/37096259094) **1/1 PASS**: package 34/34, renderer 13/13, 기존 13조건+전체 결과 seed 반복 검사 14/14. [원본 A 보존](https://github.com/0-FLANDRE-0/Aegis_Project/actions/runs/37096259099) **4/4 PASS**, A runtime 14/14. A/B 전체 same-seed benchmark·spotting exact 일치. [최종 일반 smoke](https://github.com/0-FLANDRE-0/Aegis_Project/actions/runs/37096259111)는 3D 통합 포함 **32/32 PASS**다. 전체 목록을 조회해 첫 페이지 집계 오류를 바로잡았다.

원래 두 구멍은 선체 표면 검색에 성공했지만 GPU 렌더 제출 때문에 geometry queue가 지연됐다. B는 필수 aperture commit까지 직전 canvas를 유지한다. C5 root/schema, 실제 중첩 센서 mount와 마스트 17 draws, source envelope, 함포 joint, 96 셀/hinge/panel binding을 검증한다. 전투 source와 geometry asset은 보존한다.

[PR #41](https://github.com/0-FLANDRE-0/Aegis_Project/pull/41)의 B HTML 업로드·원격 exact 확인은 끝났다. 업로드 후 CI와 파일 대조 guard의 결과는 [마감 증거](docs/wip16/B/evidence/upload_closeout.json)를 따른다. 신규 branch·main 병합·v48.1 승격·release/tag는 실행하지 않았다.

최종 CI가 모두 통과해 기술적 통합 판정은 PASS다. 다음 진입점은 명시 승인 시 PR 통합이며, 병합 승인과 v48.1 승격/release 지시는 별개다. 이후 출항 전 함선 선택/초기화 공통화 → 벙커힐 연결이다. 하푼·토마호크와 다함 동시 운용은 후속 범위다.

## WIP16A 마감 당시 기록

아래는 B 수리 전의 역사 기록이다. 현재 판정은 위 B 상태를 따른다.

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
