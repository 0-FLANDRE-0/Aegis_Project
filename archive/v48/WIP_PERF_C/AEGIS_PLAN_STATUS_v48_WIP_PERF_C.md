# AEGIS PLAN STATUS v48_WIP_PERF_C

## 현재 기준

- 최적화3단계 완료. PERF_B final `d26e94194d52f0040f4d3d388b9bbce49460b440` 위 `performance-c`.
- HTML `Aegis_SIM_v48_WIP_PERF_C.html`, 15,707,171bytes, SHA-256 `5f8fb9ed69a960c4eef4c15ab22271c82c9b59a095a9ec8a959689ecba9acffd`. decoded main `015c4cf9f83c9f6bd595ce61583e214bbd12c8248fad15bacdc87fa10f0c7358`.
- records0~12/모델 assets·stablev48 보존, records13만 변경. 직전 PERF_B HTML/status/SHA/workflow 네 원본은 `archive/v48/WIP_PERF_B/`에 같은 bytes/blob으로 보존한다.

## 적용 내용

SPY 공통 대공 NIS 연관에서 트랙별 prediction/Jacobian/공분산 투영과 동일 오차 역행렬을 재사용한다. 상태6·공분산36·센서 위치/속도6·오차4를 exact 비교한다. 제자리 배열 변경/같은 tick 변화도 즉시 반영하며 측정 innovation은 매번 다시 계산한다. native 행렬/NIS 연산 순서는 유지한다.

캐시는 파생값·트랙 객체별 last1·WeakMap·snapshot 비저장이다. truth 접근이나 권한 캐시가 없다. canonical EKF prediction/correction·수상 연관·plot 생성/난수·focused/global 배정/게이트·실제 release guards와 fixed60/120/20Hz·physics/damage/EW/AI·Harpoon INS/ARH/DL0·CG/DDG 장비/조작·PERF_A/B 최적화를 유지한다.

## 검증

- 최종 원본 직접 1603/1603PASS,31suites/15captures, 과거·draft 결과 합산0, page/core/runtime/presentation 오류0.
- full packing/rebuild/syntax/scope·원본 native 갱신/배정/기존 cache/release source 보존·NIS231차등 사례/입력·게이트 경계·CG/DDG core.
- strict CG/DDG6조건과 직렬 CPU16쌍 상태/RNG/entity exact, 기존 함대·방어·피해·저장·UI/3D·세 owner1/8/16/64 회귀.
- 집계·입력·script/report/capture SHA는 `docs/performance/C/evidence/verification-summary.json`, CPU 조건/증가·감소/한계는 `docs/performance/C/PERFORMANCE.md`가 기준이다.

## 업로드·후속

§7.1 사용자 원본 직접 업로드/readback 승인을 유지한다. `docs/performance/C/evidence/remote-publication.json`은 code/support commit을 pin하고 자기 checksum에서 제외한다. proof-only commit 뒤 final-head도 따로 읽어 확인한다. Actions 계정 제한으로 manual workflow만 준비하며 dispatch/CI PASS 주장은 없다. main/선행PR 병합·새PR 생성은 이 단계에 포함하지 않는다.

다음은 피격 envelope의 convex/sort 지연 최적화, 실제 가시3D/효과·최종 재측정이다. 그 뒤 헬기/초수평선 탐지 → RGM-109E Block Va를 유지한다. 대표 조건 밖 모든 오격 방지·요격률·자연 장거리 획득·실제 doctrine·휴대폰 FPS 인증을 완료로 주장하지 않는다.
