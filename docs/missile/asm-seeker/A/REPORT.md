# ASM_SEEKER_A — 대함미사일 시커 감사와 최소 수정

IMPLEMENTED: **예** — 공용 Kh-35U/Kh-32 시커의 최초 EKF 연관 한 곳을 수정했다.

TESTED: **예** — S0/S1/S2, TRACK-C 60전투, native13 364건, UI 213건, WebGL 29건을 완료했다.

APPROVED: **지시서의 Confirmed 결함 자동 S2/S3 조건 적용**.

UNRESOLVED: **45 km 소형 수상표적 검출은 기존 SNR/evidence 계수 한계로 남김**. 저장된 TRACK-C run과 fresh replay의 최종 방어 분기는 달랐지만, 진단 observer ON/OFF는 byte exact였다.

RELEASE: **main 병합 승인 — PR·원격 readback 진행 전**. release/tag는 만들지 않는다.

## 결론

TRACK-C에서 qualified egress로 남은 최신 C 표본은 지시서의 39발이 아니라 실제 raw 기준 37발이었다. 37/37 모두 최초 accepted association과 최초 confirmed TRACK이 목표 함정이 아닌 인접 salvo의 `RF_OBJECT`였다. 첫 TRACK 전 피해는 0/37, 기만체 최초 연관은 0/37이었다.

기존 `asmSeekerAssociateMeasurements`의 EKF 미초기화 분기는 발사 cue의 거리·방위·고각 차이를 점수 감점으로만 썼다. 약 10.7 km의 지정 함정 echo가 같은 tick에 있어도 약 92.8 m, SNR 17,786의 인접 ASM 합성 echo가 점수를 이겨 잘못된 EKF를 만들 수 있었다.

수정은 기존 점수 정규화 척도인 거리 `max(1200 m, cueRange*0.12)`, 방위 `5°`, 고각 `4°`를 최초 획득 basket gate로도 사용한다. 실제 물체 ID·소속·truth는 읽지 않는다. 새 튜닝 상수는 없으며 RF/Pd·잡음·RCS·빔·gimbal·유도·추진·피해 코드는 바뀌지 않았다. 수정 main을 역치환하면 기준 main과 byte exact다.

## S0 — 실제 live 시커

| 무장 | 구현 | 결과 |
|---|---|---|
| Kh-35U | 공용 WIP22 monopulse seeker core | 수정 대상 |
| Kh-32 | 같은 공용 WIP22 core | 공용 수정 보존 검증 |
| RGM-84D Harpoon | 별도 `harpoonSeekerA` | 변경 없음, 독립 물리 검증 |

추가 live/debug-only 대함 시커는 찾지 못했다. 상태와 호출 그래프는 `ASM_SEEKER_STATE_AUDIT.md`, 등록값과 공개정보 경계는 `ASM_SEEKER_INVENTORY.md`에 있다.

## S1/S2 고정 행렬

| 조건 | 기준 | 수정본 |
|---|---:|---:|
| Kh-35U 20 km, 0/5/10/20° | 40/40 TRACK | 40/40 TRACK |
| 10/20° 최초 후보가 자함인 경우 | 20/20 | 0/20; 지정 수상표적 20/20 |
| 20 km, 40° 바깥 대조군 | 10/10 TRACK | 0/10 TRACK |
| 45 km 전 조건 | 0/50 | 0/50; 계수 변경 금지로 보존 |
| Kh-35U/Kh-32 무표적 | — | 오획득 0/20 |
| Kh-32 단일/복수 반사체 | — | 정상 TRACK 20/20 |
| Harpoon 독립 물리 경로 | — | 정상 TRACK 20/20 |
| ACQUIRE 후보 lateral steering | 0 | 0 |

진단 observer의 기준/ON 비교는 comparable final JSON과 global RNG가 같은 SHA `201bff4c…f043`으로 byte exact였다.

## S3 — 전투와 회귀

TRACK-C와 같은 60개 전투를 끝까지 다시 실행했다. 제품 오류나 강제 종료 없이 60/60이 `QUALIFYING_COMPLETED_BATTLE`이었다.

| 판정 | TRACK-C 기준 | 수정본 | 변화 |
|---|---:|---:|---:|
| 격추 | 264 | 294 | +30 |
| 실제 유출 | 15 | 21 | +6 |
| 시커 이탈 | 37 | 0 | -37 |
| 기타 종결 | 4 | 5 | +1 |
| 합계 | 320 | 320 | 0 |

37발의 부당한 이탈이 36발의 격추·실제 유출 증가와 1발의 기타 종결로 정확히 보존됐다. 이 결과는 시커가 방어 통계를 인위적으로 좋게 만들던 현상을 제거했다. HP는 지시대로 승인 판정에 쓰지 않았다. 상세 조건별 비교는 `S3_BATTLE_RESULTS.json`에 있다.

광범위 회귀 결과는 native13 364/364, UI 213/213, WebGL 29/29였다. 신규 실패는 0건이다. 헬기 비행·APS-153·ISAR·EMCON·하푼·소브레멘니·배속/시간축·저장/복원·정식 VLS 실사격을 동일 제품 SHA로 실행했다. 기존 구형 EMCON UI 14건은 이미 폐기된 부채로 분리하며 신규 실패로 세지 않는다. 기계 판정과 각 원본 결과 SHA는 `VALIDATION.json`, `REGRESSION_RESULTS.json`, `evidence/regression/`에 기록했다.

## 범위와 남은 일

- 45 km 검출 실패는 RF 감도·evidence 계수 영역이라 수정하지 않았다.
- 정상 피격 저하, 기만, 가림, 해면 클러터, SNR 부족, 기동 한계 실패는 그대로다.
- TRACK-D, OODA, 방어 무장 성능, 피해 물리, 저장 스키마는 건드리지 않았다.
- 상세 원인 행은 `EGRESS_CAUSAL_ANALYSIS.json`, 최소 변경은 `changes.diff`, build/scope 증명은 `BUILD.json`과 `SCOPE.json`에 있다.
