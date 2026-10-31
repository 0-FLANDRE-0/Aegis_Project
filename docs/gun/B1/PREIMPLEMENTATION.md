# GUN_B1 구현 전 설계 · 2026-10-31

기준 map-e `5542aa005479713a5a8959143157fdf4ba07447e`, PR #58 미병합. 별도 gun-b1. 기준 HTML SHA-256 `f825ccffbdf617f9f1154f131db484ac6682e91fceedcb9e33e2686f5255514b`.

## 기존 확정 사항과의 관계

1. 원래 selectAmmo는 발사 후 cycleRemainingS 동안 거부하지만, 비순환 상태에서 탄종 교체 자체는 즉시다. 새 임의 급탄 지연을 추가하지 않는다. 기존 3초 사격 사이클/전환 거부를 보존한다.
2. 헬기의 실제 피해/격추는 기존 합의대로 보류한다. 비행 헬기는 물리 근접 신관 반응에는 포함하되, 피해 처리는 DEFERRED_HELO_DAMAGE로 남긴다. 피아에 따른 신관 예외는 없다. 센서/자동 선정은 관측 트랙만 사용한다.
3. CG 개별 포 선택 UI와 EMCON 무방사 지정 GUI를 복원하지 않는다. 기존 MAP_D 자동 2문 규칙을 확장한다.

## CG 성능/외형

`MK45_MOD4_CG52_MK160_V1`: 기존 Mod4 객체를 spread하고 id, sourceBasis, CG 탄약고 출처만 덮어쓴다. 설치별 hardpointId/geometryMask/moduleName/neutralAzRad 유지. 원래 Mod2 정의는 수정하지 않는다. 설치의 포구 오프셋/노출 길이를 Mod4 외형 기준(.91,0,2.87 / 6.206m)으로 변경하며, 원래 하드포인트를 유지한다. 좌표 감사 보정: CG hardpoint는 포탑 바닥이고 DDG hardpoint는 이미 높은 축 기준이다. 따라서 Z 오프셋은 DDG 생성기의 trunnionZM(10.92)−baseDeckZM(8.05)=2.87m를 쓴다(MODEL_REGISTRATION). 0을 그대로 복사하면 포신이 갑판에 묻는다. CG 모듈 생성기는 설치에서 중립각과 사계 끝을 현재와 동일하게 합성한다.

DDG `WIP148_EXTERNAL_3D.buildMk45(parent,mats)`를 선택적 레이아웃 인자로 확장해 동일 생성기를 호출한다. CG 원본 포 조립체를 렌더에서 숨기고 새 포탑을 동일 hardpoint에 배치. 포구/트러니언은 모듈에서 산출하여 렌더 어댑터가 소비한다. 포구 끝 `.006m`의 bore 형상은 장식이며 물리 포구와 비교할 때 별도로 명시한다. 렌더→물리 피드백 없음.

## 탄약 분배

| 함 | 이전(포문당) | 새 분배(포문당) | 함 총탄수 |
|---|---|---|---|
| DDG | HE360/SAP240 | HE180/SAP240/MFF180 | 600 유지 |
| CG | HE360/SAP240 | HE180/SAP240/MFF180 ×2 | 1200 유지 |

SIM_TUNED, 기존 HE의 절반을 새 탄에 배분. 질량/탄도는 HE와 같아 초도 총질량 유지. 구 저장 CG는 모듈 id를 현재 설치 모듈로 이식하고, **남은 HE의 floor(HE/2)**만 MFF로 전환한다. HE+MFF 잔량, SAP, shotsFired 보존. 이미 MFF가 있는 저장은 재분할하지 않는다. DDG 함포 잔량은 기존 작전 저장 스키마에 없으므로 기존 초기화 정책 유지. 기존 검증기는 각 탄종 초기 배분을 상한으로 삼으므로 옛 HE 잔량을 분할한 후 검증한다. 저장 스키마/필드 추가 없음.

## 파편과 물리 객체 경계

SAM `_wip88FragmentationPk` 본문을 사본 함수로 가져와 첫 프로파일 선택만 5인치 전용 SIM_TUNED 파라미터로 바꾼다. 원래 함수/레지스트리/호출은 byte 동일. `_wip88GurneyFragmentSpeed`, `_wip99FragmentArrivalGeometry`는 순수 함수로 그대로 호출한다. 전용 함수는 기존 게임의 파편 통계 계산을 재사용하며 실제 Mk187/MK419 성능을 나타내지 않는다. ASM 결과는 기존 applyInterceptResult와 잔해/로그 경로, 그 밖의 객체는 해당 기존 사망/종료 경로에 연결한다. MFF가 없으면 새 난수 소비 없음. 클러터는 포탄별 독립 시드 스트림이고 기존 전투 RNG에 영향 없음. 파편 피해 난수는 기존 처리 경로 그대로.

물리 신관 후보: enemyMissiles(ASM), targetPool(항공기/드론), missiles(SAM), ramMissiles, harpoonWorldA(), NPC executionD의 sam/ram, 비행 상태 헬기. 같은 객체 중복 제외. onboard 헬기는 제외. 센서/사통/자동 표적 선정은 이 목록을 읽지 않는다. 미관측 객체도 신관에 반응하며 아군 요격탄도 예외 없음.

## SIM_TUNED 초안 전체

새 수치는 게임 전용이며 성공률 목표를 맞추지 않는다. 기존 상수를 그대로 사용하는 항목은 새 튜닝이 아니다.

| 키 | 초안 | 선택 근거 |
|---|---:|---|
| initialMffShareOfHe | 0.5 | 기존 HE 풀을 절반 분할, 총탄수/질량 보존 |
| armDistanceM | 430 | 지시서 공개 최소 교전거리 참조; 신관 실제 제원이 아님 |
| proxRadiusM | 25 | 게임 근접 판정 거리, 실제 신관 값 아님 |
| etMarginS | 0.2 | 관측 사격해 시한의 게임 보조 여유 |
| explosiveMassKg | 3.7 | HE 공개 참고량을 게임 탄두에 임시 사용; Mk187 실제 값 주장 안 함 |
| fragmentCount | 1200 | 기존 게임 파편 모델을 호출하기 위한 가상 재고 |
| caseMassKg/gurneyDrivenMassKg | 9 / 9 | 가상 파편 파라미터, 실제 구조 추정 안 함 |
| avgFragmentMassKg | 0.0075 | 위 가상 재고와 질량의 내부 정합 |
| gurneyMps | 2200 | 기존 게임 계산기의 가상 에너지 입력 |
| effectiveFragmentFraction | 1 | 명시 재고 분기를 사용하며 별도 효율 감쇠 없음 |
| annularBandHalfAngleDeg | 55 | 게임 파편 분포, 실제 탄두 분포 아님 |
| fragmentQueryRadiusM | 120 | 물리 피해 후보의 계산 비용 제한 |
| clutterAltitudeScaleM | 12 | 수면 가까이에서만 눈에 띄는 위험 |
| clutterHazardPerS | 0.004 | 시간 기반 낮은 위험, 틱 수 독립 |
| clutterIncidenceFloor | 0.15 | 거의 수평 비행에서도 작은 해면 반사 항 |
| clutterSeedSalt | 0x419b1001 | 포탄 독립 RNG 도메인 분리 |
| maxMeasurementAgeS / readyAgeS | 3 / 1.5 | 공중 표적 관측 신선도 게이트 |
| maxPositionSigmaM / readyPositionSigmaM | 150 / 30 | 3D 위치 측정 품질, 임의 명중률 대신 표시/거부 |
| maxVelocitySigmaMps / readyVelocitySigmaMps | 30 / 8 | 3D 속도 불확실성 |
| maxTofS / readyTofS | 40 / 20 | 공중 예측의 제한, 사거리 근사 모델 추가 없음 |
| autoRangeM | 9000 | 사용자 지시값, 실제 대공 유효거리 아님 |
| autoTtcHysteresisS | 1 | 비슷한 위협 사이 불필요한 포 전환 억제 |
| diagnosticLogLimit | 256 | 게임 메모리 상한 |
| autoDefault | ON | 사용자 결정, 함별 transient; 로드 후 ON |

주기/회전/급탄/고각/사계/탄도/지형/기본 pointing gate는 기존 모듈을 그대로 사용한다. UI 라벨/점선/작은 표식은 presentation-only. 현 단계에서 새 대공 유효거리표를 계산하지 않는다.

## 공개 출처 확인

- USNI, Edward J. Walsh, 2008-02, [Naval Systems: Cruiser Updates Begin](https://www.usni.org/magazines/proceedings/2008/february/naval-systems-cruiser-updates-begin): CG52 Mk45를 54→62구경 Mod4로 교체한다고 명시.
- [미 해군 Mk45 Fact File](https://www.navy.mil/DesktopModules/ArticleCS/Print.aspx?Article=2167864&ModuleId=724&PortalId=1): CG52–60/62–64 Mod4, 순양함 1200발 표기 확인.
- 기존 `CG52_2021_MK45_MOD2_PHOTO_CAPTION__5IN54_PUBLIC`: **현역 후기 CG52 근거로 대체됨**, 원래 Mod2 모듈의 역사적 정의는 보존.
- 공개 MK419 설명은 모드/장입/클러터 필터의 존재만 참고. 실제 신관/탄두 상세 성능이나 제작 정보는 본 게임 파라미터의 근거가 아니다.

## 검증 방침

구현 전/후 source symbol 비교로 비행 지문281개와 ENV_D 블록을 확인. 기존 검수는 자동 대공을 테스트 설정에서 OFF로 하고 실행, 새 ON 검수는 별도 기록. 승인 raid 기대값은 바꾸지 않는다. CG Mod4 관련 차이는 실패로 숨기지 않고 원인과 함께 보고. 실제 최신 HTML을 계측해 테스트하며 별도 근사 비행 모델은 만들지 않는다.
