# 현재 상태 (2026-11-06 SEEKER_UNIFY_U3 기준)

## 레포

- `main` `be19f467` (PR #71 문서 아카이브 병합; 부모에 PR #70 `cue-a-1` 포함)
- 최신 PR: [#72](https://github.com/0-FLANDRE-0/Aegis_Project/pull/72) OPEN (`seeker-unify-u3`)
- 기준 제품: `Aegis_SIM_v48_WIP_CUE_A_1.html`, SHA-256 `0449d3192cc4cafbda3686669e3738a36b7a7d8aeda205b5cbd3e614061b814a`
- 후보 제품: `Aegis_SIM_v48_WIP_SEEKER_UNIFY_U3.html`, SHA-256 `3eecf254b9a586398fb2236068cca722912730d8dc492275f06157407ed6e2ea`
- 게임 소스는 HTML 안의 `data-c55-index="13"` gzip+base64 블록이다. 압축을 풀면 약 40 MB JS다.

  ```python
  m = re.search(rb'data-c55-index="13">([^<]+)', raw)
  js = gzip.decompress(base64.b64decode(m[1]))
  ```

- 고정 작업 규칙: 루트 `AEGIS_PROJECT_INSTRUCTIONS.md` (Truth 경계, 고정 dt, 격리 RNG, 3D는 표시 전용)

## 역할

- 사용자: 방향 결정, 지시서 검토·전달, 플레이 검수, **PR 병합**
- 리뷰 AI: 레포 검토, 결과 해석, 지시서 작성 (`REVIEWER_PLAYBOOK.md`)
- 작업 AI: 구현·시험·PR 생성

## 지금까지 흐름

| 작업 | 내용 | 상태 |
|---|---|---|
| TRACK-A/B/C | 트랙 신뢰성 | main |
| ASM_SEEKER_A (PR #65/66) | 이웃 ASM 오획득 수정. 시커 최초 연관을 hard basket으로 | main |
| ASM_SEEKER_B | 원거리 획득 실패 진단 (원인: 함정 RCS 과소) | 진단만 |
| SEEKER_UNIFY_A (PR #67) | 함정 RCS를 Skolnik 경험식으로 정비. 시커 통합 감사·설계 | main |
| SEEKER_UNIFY_B (PR #68) | U0 cue 바구니 시간 확장, U1 공통 DTO | main |
| SEEKER_UNIFY_C (PR #69) | U2 ACTIVE, 대함 시커 빔·LOS 왕복 보정, CUE_A(cue 필터·수동 RF·위협 가정 스위치) | main |
| CUE_A-1 (PR #70) | Singer cue 필터(τ=60 s, 정확 이산화), 바구니 상한, 수동 RF 함정 레이더 family·대역·회전 레이더, 0.5 km 거리 하한 원복 | main |
| **U3 하푼** | U2/CUE_A/HOJ 공통 계약 + 수동 RF 우도 선택 | PR #72 OPEN, 게이트 완료 |

## U3 결과 요약

- A–D 단계 게이트 PASS. 각 단계 SHADOW 확인 뒤 ACTIVE 전환.
- 일반 하푼 track cue의 고정 4 km 상한 제거; route prior 4 km 유지.
- 하푼 HOJ는 ASSUMED_THREAT, MAX_THREAT ON/CONFIRMED_ONLY OFF.
- 수동 RF 후보는 gate 뒤 `d² + ln(det(S))`; truth/RNG 사용 0.
- 최종 광역 1회: native364/364, UI213/213, WebGL29/29 PASS.
- paired raw38/42의 4건은 D ACTIVE raid 경로로 단계 분리. 기대값 갱신0, 물리·손상·VLS·최종 결과 동일.
- 상세와 잔여는 `docs/missile/seeker-unify/U3/FINAL_REPORT.md`, `BACKLOG.md`를 따른다.
