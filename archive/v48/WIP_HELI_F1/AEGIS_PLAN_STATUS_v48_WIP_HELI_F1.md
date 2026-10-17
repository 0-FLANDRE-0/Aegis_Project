# AEGIS v48 WIP HELI_F1 — 수동 하푼 OTH 관문·식별 근거·교전 로그

구현·정적·런타임·브라우저 회귀 완료. 구현 소스 `e9e0d75d0c2b5f232286828cb46d9f46fff05f11`. HELI_E1 `69a5e38` 위 `helicopter-harpoon-f1`. [사용자 범위 결정](docs/helicopter/H/CONFLICTS.md), [운용·재현](docs/helicopter/H/README.md), [검증](docs/helicopter/H/evidence/verification-summary.json), [독립 원격 확인](docs/helicopter/H/remote-publication.json).

- 원본 **16,075,722bytes**, E1 대비 **1,500bytes 증가**.
- HTML SHA-256 `913d7d611c827ade8f62d5671d811404506c4f2923c9b9a37c3e7b3cf91724f2`.
- packed13 SHA-256 `9419107e887b5020a3cec626c0d49d21600288fcd712ab7430d342b6b4495676`.
- 그 외13 packed 자산, stable v48, 이전 A–G 소스·증거는 보존한다. 저장 schema/함정 장비 구성은 변경하지 않는다.

## 결과

순수 offboard도 기존 수동 식별·트랙 확정·최대 나이10초·2σ 예측 바스켓·사거리·손상·발사 자세 조건을 통과하면 하푼을 발사할 수 있다. active/foreign native gate, 자동 발사관 선택, FLEET/foreign 수동 wrapper를 함께 처리했다. 별도의 offboard 공분산 페널티는 없다. 원격 보고가 실제 현지 관측 시각을 갱신하지 않는다. AI capability/현지 관측/보호 corridor와 SAM/GUN 권한, 좌표/경로 발사는 유지한다.

순수 offboard 운용자 식별의 기존 허용 정책에 `OPERATOR_ONLY` 근거를 붙인다. 현지 관측이 있는 경우 `LOCAL_SENSOR`, `ISAR`는 후속 자리만 둔다. 같은 트랙에 새 관측이 왔다는 이유로 과거 발사 식별 근거를 고쳐 쓰지 않는다.

DEBUG → **교전 로그**: 함정별 최대64발, 발사 시각·트랙ID·LOCAL/OFFBOARD/MIXED·predictionSigmaM(기존2σ)·운용자 식별·식별 근거·사거리. 실제 종료 뒤 명중/자폭 사유/소실과 적성·아군·중립 상선·없음을 기록한다. 실제 충돌 대상 범주만 `AFTER_ACTION_TRUTH` 사후 경계에서 구한다. 전술/센서/AI/유도는 로그를 읽지 않는다. 실시간 전술 명중 보고와 DL은 추가하지 않으며 `updatesAfterRelease:false`를 유지한다. 기록은 transient이며 reset/import 때 비운다. 상선 범주 검증은 기존 무인 컨테이너 민간 선체를 사용했다.

APS_SPEC_F의 `shortTargetRangeM`, `longSmallTarget*`, `longMediumTarget*` 7개 reference는 `USER_DESIGN_TARGET`으로 바꿨다. 사용자 감각 목표이며 물리 근거가 아님을 APS_REFS_F에 명시했다. 숫자·레이더 계산은 같다.

## 검증

최종 동일 원본 **209/209 PASS /7 suites**, page errors0. static42 / isolated native policy31 / native46 / 실제 헬기·수신기 재생18 / 혼합 바스켓6 / UI·배속24 / 기존 전투42. 이전 E1 검사152개는 더하지 않는다.

- 실제 DDG 헬기 SHORT/PERI20km에서 각각13개, LONG100km에서6개의 확정 측정을 확보하고 Hawklink 전달을 확인했다. CG 수신기 진단 재생에서 SHORT/PERI는 발사 품질 통과, LONG은 `INS_PREDICTION_BASKET_INSUFFICIENT`였다. 이는 플레이 중 전단 공유 기능이 아니다.
- 링크 단절 후10초 초과 `SURFACE_TRACK_COAST_EXPIRED`; AUTO/SEMIAUTO·가짜 AI token·UNKNOWN/FRIEND/NEUTRAL·사거리·장비/발사대 손상 거부를 확인했다.
- 실제 OTH 수동 발사→중립 선체 충돌에서 OPERATOR_ONLY/NEUTRAL_MERCHANT/AFTER_ACTION_TRUTH를 기록했다. 실제 적함10km와 중립 선체8km가 같은4km 바스켓에 있는 경우에도 중립 피격을 의도한 적함 명중으로 잘못 기록하지 않았다.
- 발사 후 링크와 모함 트랙을 제거해도 미사일 최종 전체 상태가 같았다. FLEET의 타함 CG 수동 발사·로그 소유권,64건 제한·복제·중복 종료·lifecycle 초기화도 확인했다.
- 1/8/16/64×에서 같은640 fixed ticks의 미사일·로그·RNG가 같다. 테스트의 출항·pause를 원자적으로 실행해1틱 경쟁을 없앴고, 요청600틱이 프레임 단위로608/640이 되던 기존 도구의 반올림을 피해640틱으로 맞췄다. 시뮬 시간 주기를 변경한 것이 아니다.
- 데스크톱1000×760 / 모바일390×1000에서 실제 포인터로 로그 열기·전체 선택·닫기와 읽기 전용 상태를 확인했다. DDG/CG의 대기·8Kh32 AUTO·손상6조건에서 기존 물리·피해·배치·RNG·observer·offboard 상태가 E1과 같다.

## 남은 범위·전달

사용자는 **F1 완료 후 CG-52 헬기 운용은 다음 단계**로 선택했다. 현재 DDG는 헬기만, CG는 하푼만 지원한다. 원래 모함 전용 Hawklink와 순수 헬기 트랙 Link16 재공유 제외를 유지하므로, 완전한 라이브 헬기→모함 하푼 운용은 CG 항공 운용 후속 단계다.

이전 E1 네 파일은 archive/v48/WIP_HELI_E1에 동일 bytes/blob으로 보존한다. 전체 원본을 직접 작업 브랜치에 올리고 GitHub tree/decoded blob을 독립 readback한다. 수동 workflow만 제공하고 Actions dispatch/main·이전 브랜치 병합/새 PR 생성은 하지 않는다. 실제 휴대폰·hardware FPS는 측정하지 않았다. 실제 자폭 장치/헬기 피격·격추/ISAR/Link16 확대도 추가하지 않았다.
