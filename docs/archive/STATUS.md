# 현재 상태 (2026-11-06 기준)

## 레포

- `main` `2293c895` (PR #70 `cue-a-1` 병합). 바로 앞은 PR #69 `seeker-unify-c` 병합 `ac05c551`
- 최신 제품: `Aegis_SIM_v48_WIP_CUE_A_1.html`, SHA-256 `0449d3192cc4cafbda3686669e3738a36b7a7d8aeda205b5cbd3e614061b814a`
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
| **U3 하푼** | 설계 대화 중 (`DESIGN_NOTES.md`) | 다음 |

## CUE_A-1 결과 요약

- Kh-35U: TRACK/명중 60/59, EMCON OFF·ON 모두 C와 같음
- Kh-32: EMCON OFF에서 TRACK +5 (S대역 빔이 넓어진 효과), 명중 40으로 같음
- 오획득 증가 0, 이웃 ASM 최초 연관 0, 혼입(아군 시커·눌카·재머·항공기 레이더) 선택 0/50
- 60 전투(참고) 301/19/0/0
- 검토에서 나온 후속 과제는 `BACKLOG.md`에 있다.
