# TRACK-C 지시서: 트랙 수명·재획득 계보와 식별(IFF/FRIEND/own-fire) 근거

## 0. 현재 상태 (이 문서가 최신 기준)

- 첨부 인계서 `AEGIS_NEXT_PHASES_HANDOFF_2026-11-02.md`는 **TRACK-B 착수 전에 작성됐다.** 1~2장의 SHA·상태, 4장(TRACK-B)은 이미 지난 내용이다. 이 지시서와 내용이 다르면 **이 지시서를 따른다.**
- **TRACK-B 완료**:
  - R4 ACTIVE가 60쌍 통계 전투로 승인됐고 PR #63으로 main에 병합됐다.
  - main `d328c941` (cg-turret-a, ciws-dmg-a, friendly-contact-a, track-a, track-b 체인 포함)
  - 제품 `Aegis_SIM_v48_WIP_TRACK_B_STABLE_D.html`, SHA-256 `48b023c580db02b08f165fa7ac68f973734d82e8fb4daa5981dcc90b7e04e4ab`
  - 최신 상태 문서는 `docs/contact/track/CURRENT.json`, `docs/contact/track/B_statistics_r4/REPORT.md`
- **TRACK-B에서 넘어온 범위**: C55(자함·NPC) 및 SPQ AIR의 실제 연관은 아직 SHADOW-only다. 이번 C 범위에 포함한다(§3).
- **상속 이슈** (C의 식별/보호 범위와 겹치므로 이번에 결론을 낸다, §4):
  - CIWS 시드 `419025` 피격 1건(friendly-contact-a의 own-fire 보호 오염 수정 이후)
  - CG observer 정확 상태 차이 2건
  - 구형 EMCON UI 14건(현재 UI에서 제거된 `#lockBtn` 전제)

## 1. 기준과 산출물

- **기준**: main `d328c941`. 시작 시 HEAD·HTML SHA를 대조하고, 다르면 실제 값을 기록한 뒤 최신 main을 기준으로 한다.
- **작업 브랜치**: `track-c-lifecycle-a`
- **커밋 작성자**: `110261808+0-FLANDRE-0@users.noreply.github.com`
- **산출물**: `Aegis_SIM_v48_WIP_TRACK_C.html`(필요 시 `_SHADOW`), `docs/contact/track/C/`
  - `PLAN.md`, `REPORT.md`, `VALIDATION.json`, `changes.diff`, `BUILD.json`, `SCOPE.json`
  - 고정 시드 원시 결과, 실행 명령·환경·SHA
  - 보고서 맨 위에 `IMPLEMENTED / TESTED / APPROVED / UNRESOLVED / RELEASE` 다섯 상태를 따로 표시한다.
- **실행 시간 상한**: 전체 벽시계 **4시간**. 넘으면 그때까지의 결과를 저장하고 진행 상황을 보고한 뒤 멈춘다.

## 2. C-1 트랙 수명·독립 hit·재획득 계보

- 각 owner TrackStore의 `TENTATIVE/FIRM`, 관측 나이, coast/memory/drop/reacquire 조건과 호출 순서를 감사한다.
  - 새 tracking engine을 추가하지 않는다. 기존 상태의 의미를 **읽기 전용 view**로 설명한다.
- 센서별 `measuredAtS`/`receivedAtS`, 마지막 독립 fix, hit cadence, 3D 실측 증거와 2D 수상 prior의 유효 계약(16초)을 시각별로 기록한다.
- 다음 넷을 별개 사건으로 분류한다: 정상 관측 공백 후 재획득, 중복 트랙, 오병합(false merge), ID 교환. 표적 truth는 검증용 사후 label로만 쓴다.
- 새 트랙 alias가 생길 때 이전 파일의 분류·식별·권한·FCS 예약·BDA와의 관계를 정리한다. 좌표가 가깝다는 이유만으로 전부 복사하지 않는다.
- TRACK-B R4의 "물리 ID 교환·오병합·중복 지표 UNKNOWN" 공백을 이 계보 기록으로 채운다. RF 반사체 → 측정 → 연관 → KF epoch를 사후 lineage로 연결한다.

## 3. C-2 식별·보호 근거 수명, C55·SPQ AIR 실연관

**식별·보호 근거**
- 다음 필드의 출처·확인 시각·만료·재검증·승계 정책을 서로 분리해서 정리한다: `classification`, `identity`, `_operatorIdentity`, `threatStatus`, `engagementAuthority`, IFF 인증, `ownFireEvidence`, `protectedIdentity`.
- **자함 발사탄 보호**: 실제 발사 사실과 측정 경계로 보호하되, 비자함탄 관측이 보호 파일로 오염되는 경로는 0이어야 한다. 유효한 아군 보호를 없애는 수정도 금지한다.
- **수동 설정과 자동 인증의 만료**: 운용자 수동 FRIEND 지속성과 헬기 AIR IFF 만료 규칙이 서로 다르면 현행을 기록만 하고 바꾸지 않는다. 바꿔야 할 근거가 있으면 제안으로 올린다.
- **자동 승격 금지**: IFF 무응답 → HOSTILE 자동 승격 금지. 불확실한 alias → 자동 교전권한 승계 금지.

**C55·SPQ AIR 실연관 (TRACK-B에서 이관)**
- B의 SHADOW 비교 자료를 출발점으로 C55 자함/NPC와 SPQ AIR 연관을 ACTIVE로 적용할지 검토한다.
- TRACK-B 공용 solver와 HOLD 정책(δ=1, 기존 NIS)을 그대로 쓴다. 계수를 결과에 맞춰 바꾸지 않는다.
- C55는 CIWS 즉응 방어 경로라서, 연관 보류가 사격 지연으로 이어지는지 반드시 전투 시험으로 확인한다(§5).

## 4. 상속 이슈 처리

| 항목 | 처리 |
|---|---|
| CIWS `419025` | own-fire 보호 범위다. §5 통계 판정의 D1 30시드 비교에 포함해 결론을 낸다. 30회 합계가 나빠지지 않고 원인이 RNG/교전 분기로 설명되면 기대값을 갱신한다. |
| CG observer 2건 | 원인을 C-1 계보 기록으로 설명한다. 정확 상태 차이의 원인이 friendly-contact-a의 승인된 수정 범위면 기대값을 갱신하고, 아니면 보고한다. |
| 구형 EMCON UI 14건 | 제거된 `#lockBtn` 전제라서 **폐기한다(사용자 승인).** 같은 동작을 현재 UI로 검증하는 대체 시험이 UI213에 있는지 대조표를 남기고, 빠진 동작이 있으면 현재 UI 기준 시험을 추가한다. |

- 갱신·폐기는 모두 전후 값과 근거를 승인 기록 파일에 남긴다. 허용 오차는 바꾸지 않는다.

## 5. 검증과 판정

**기능·계약**
- 연관/만료/재획득, stale/shared/replay, 분리된 두 물체, 복수 owner, 수면 prior, IFF ON/OFF/유효기간, NEUTRAL·수동·HOLD 보호를 native fixture와 자연 RF로 검증한다.
- C55 자함 발사 보호와 후속 파일 수명: SAM/RAM/Phalanx 보호 오인 0
- 회귀: native13, paired42, D1 30, UI213, WebGL8, 헬기·하푼 자연 재현, AUTO/IFF, 배속 1/8/16/64, 저장/복원, owner·RNG·ENV

**전투 통계 판정 (TRACK-B와 같은 방식)**
- 기존 main(R4) vs C 후보, 같은 시드 쌍으로 비교한다.
  - B_statistics_r4의 시나리오 세트: 6발 포화 ×20, 13발 포화 ×10, 2발/3발/교차 ×10
  - D1(DDG 90° 단발) ×30
- 집계: 격추, 유출(명중), 피격 회차, 이탈. 시나리오는 미사일 전부 종말까지 실행한다. **HP는 판정에서 제외한다**(가중합 포화 문제, 별도 작업 예정).
- **통과 조건**: C의 합계 유출 수와 피격 회차가 기준보다 통계적으로 나쁘지 않음(B_statistics_r4와 같은 검정). 개별 시드 차이는 원인 로그만 첨부한다.
- **이탈 분류 추가**: 이탈한 미사일마다 원인을 기만체(Nulka/채프) 유인 / 시커 상실 / 기타로 분류만 해서 기록한다. 시커 코드는 고치지 않는다. 결과는 별도 ASM 시커 감사의 입력 자료다.

## 6. 병합 권한

- §5를 통과하면 사용자 확인 없이 다음을 수행한다:
  1. 기대값 갱신(§4 포함, 전후 값·원인 기록)
  2. `track-c-lifecycle-a` → main PR 생성과 병합(merge commit, squash 금지)
  3. 병합 후 main HTML SHA와 원격 readback 기록
- 통과하지 못하면 병합하지 말고, 원인을 보고하고 멈춘다.
- **계속 금지**: release·tag 생성, main에 직접 커밋.

## 7. 금지 사항 (인계서 9장 유지, 10번만 §6으로 대체)

- **truth 비누수**: 실제 물체 ID·소속·생존·위치는 센서 물리 합성과 사후 진단에만 쓴다.
- **계수로 결과 맞추기 금지**: RF Pd/잡음/RCS/클러터, EKF 이득·공분산, 탄도·유도·신관·Pk, 피해·침수·질량 계수를 트랙 문제를 감추는 데 쓰지 않는다.
- **관측 날조 금지**: 수상 8 m prior를 관측 고도로 쓰지 않는다. ESM 방위에서 거리를 만들지 않는다. ISAR 판독을 위치 hit로 쓰지 않는다.
- classification ≠ identity ≠ authority. 수동 우선권·ROE를 유지한다.
- TRACK-D, OODA, ASM 시커 수정, HP 지표 수정은 이번에 하지 않는다.

## 8. 진행 순서

1. 기준 대조, `PLAN.md` 작성(시험 시드·시나리오·판정 규칙을 첫 실행 전에 고정)
2. C-1 계보 감사 → C-2 식별·보호 정리 → C55·SPQ AIR ACTIVE 후보
3. 기능 검증과 회귀
4. §5 통계 전투(4시간 상한 안에서)
5. 판정 → 통과 시 §6 병합, 미통과 시 보고 후 멈춤
