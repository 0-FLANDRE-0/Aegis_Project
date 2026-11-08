# SEEKER_UNIFY_U4 실행 계획

## 기준

- 기준 merge commit: `f17d3777a625699ab26f6a40de80a383f675ae85`
- 기준 제품: `Aegis_SIM_v48_WIP_ESM_A.html`
- 기준 제품 SHA-256: `5dcc6201d6acf32f56d570b01bbb33b673d835505ff877e70796e60a4bd3dad7`
- 작업 브랜치: `seeker-unify-u4`
- main 직접 변경, 자동 병합, release/tag 발행: 금지

## 커밋 A — SARH 쌍정 어댑터

1. 송신기·수신기 두 상태, 두 LOS, 송·수신 빔, 조사 상태와 쌍정 path range/rate를 명시적 익명 DTO로 변환한다.
2. 기존 물리 프런트엔드와 SARH 독립 RNG 호출 횟수·순서는 유지한다.
3. SHADOW에서 기존 echo/cell/measurement/covariance/state/guidance를 비교한 뒤 같은 빌드 규칙으로 ACTIVE를 만든다.
4. SPG OFF, 각 LOS 차단, 각 beam 이탈, clutter/chaff, TRACK/COAST/REACQUIRE/LOST, SM-2/ESSM/SM-6 교차 경로를 제한 시험한다.

## 커밋 B — RAM 수동 RF/IR 어댑터

1. player와 owner/NPC의 후보 열거·RNG 소유자를 callback으로 주입하는 공통 수동 RF/IR 측정 계약을 만든다.
2. RF/IR은 `PASSIVE_RF_2D` / `PASSIVE_IR_2D` 익명 측정으로만 공통 계층에 전달한다.
3. 확인된 `ramEmitterStrength` 소유권 결함은 기존 기본 추적 품질이 암시한 송신기 명목 세기를 보존해 좁게 분리하며 감도·gate·RNG는 바꾸지 않는다.
4. RF-first, IR takeover/dropout, EMCON·손상·전원, flare, 복수 RAM, player/NPC 격리를 SHADOW와 ACTIVE에서 확인한다.

## 커밋 C — 공통 연관·상태기계

1. 공통 엔진은 익명 측정, cue, 프로필과 무장별 gate/transition 훅만 소비한다.
2. 기존 수치·정책은 프로필/훅으로 그대로 옮기고 RAM authority, ASM HOJ, SARH↔ARH arbiter, Harpoon route/INS는 상위 훅으로 유지한다.
3. 각 미사일 local state, timer, hit counter와 RNG는 독립 상태 객체에 남긴다.
4. 대표 분기별 최대 30건의 SHADOW 동등성 이후 ACTIVE로 고정한다.

## 검증 규율

- 중간 커밋: 변경 함수 밖 보호 해시, 단계 전용 결정적 시험, RNG advance, truth 누출, 수명주기 및 오류 0만 확인한다.
- 최종 C ACTIVE 후보를 동결한 뒤 `MAX_THREAT` 광역 회귀는 정확히 1회만 실행한다.
- 설명되지 않은 차이, RNG 변화, truth 누출, 권한 변화 또는 기존 실패가 있으면 패키징·PR 생성을 중단한다.
- 통과한 경우만 제품/문서/체크섬/HTML ZIP/보고서 ZIP/Actions/원격 readback을 완료하고 PR을 생성한다. 병합은 사용자 결정이다.
