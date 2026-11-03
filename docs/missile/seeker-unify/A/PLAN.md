# SEEKER_UNIFY_A 고정 계획

IMPLEMENTED: **진행 중 — Part 1 RCS 근거 고정 전**

TESTED: **아니오 — 기준 SHA와 공급 경로 감사만 완료**

APPROVED: **지시서의 근거 기반 RCS-only 변경 및 조건부 자동 병합**

UNRESOLVED: **공개 함급별 절대 RCS 측정값 부재, 장거리 ASM 종말 획득 원인, 시커 구현 분기**

RELEASE: **아니오**

## 기준

- Git: `a36c6bf032f5af8daaf0822d822fbc08ac00a00c`
- HTML: `Aegis_SIM_v48_WIP_ASM_SEEKER_A.html`
- SHA-256: `9a00c8c02bd88ef1322b1b47882a2299184e174230391f9a608347f2b4fb3e5f`
- 작업 브랜치: `seeker-unify-a`

## Part 1 순서

1. 모든 수상 RF 반사체와 센서 소비 경로를 목록화한다.
2. Skolnik 1974 경험식과 공개 배수량을 사용해 S/X/IJ 대역 beam 기준 총량을 계산한다.
3. 공개 정성 근거가 있는 DDG-51 계열만 15 dB 저감한다. 이 값은 `SIM_TUNED`이며 10–20 dB 설계 가정 범위의 중앙값이다. CG-52·소브레멘니·시험 헐크는 추가 저감 0 dB로 둔다.
4. 기존 함정 구역/방위 비율은 보존하고 총량만 정규화한다. 일반 진단 접촉은 실제 함급·배수량이 없으므로 변경하지 않는다.
5. 기준/수정본을 같은 seed로 재진단한다. 오획득이 하나라도 증가하면 제품 승격을 중단한다.
6. 주 판정 통과 시에만 전체 회귀·통계와 병합을 수행한다.

## Part 2 순서

- Part 1 결과와 무관하게 WIP22, Harpoon, SAM v1, RAM 시커의 물리·측정·연관·상태기계 경계를 감사한다.
- 공통 API와 프로필 이전표만 설계하며 제품 구현은 하지 않는다.

## 시간 상한

- Part 1: 4시간
- Part 2: 2시간
