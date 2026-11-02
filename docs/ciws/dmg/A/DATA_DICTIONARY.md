# 원시 로그 단위·해석

모든 자료는 진단 전용이다. AFTER_ACTION_TRUTH_TEST_ONLY 자료를 센서/AI/교전 판단에 입력하지 않는다.

| 필드 | 단위/공간 | 주의 |
|---|---|---|
| step / tS | fixed tick / 시뮬레이션 초 | 1/60s. 함수 내부와 tick 종료 계측의 시각은 최대1틱 다를 수 있다. |
| rangeM, thresholdKm, quality | m, km, 기존 무차원 품질 | range crossing은 자함 중심 수평 거리다. CIWS rangeM은 센서의 경사/상대 거리일 수 있어 동일값이 아니다. |
| arc-*.json axis/muzzle/registration | 함 로컬 m, +X 선수/+Y 우현/+Z 위 | 경계는0.1° 표본. 실함 제원이 아니다. |
| SHIP_IMPACT impactPoint, COMPARTMENT_BLAST event position | 함 로컬 m | 수선/침수 모델의 기존 함 로컬 수직 기준을 그대로 사용한다. |
| WEAPON_LAUNCH.position / RANGE_CROSSING.position | **기존 게임 world X/Y**, Z는 m | 로그는 native 필드를 손대지 않고 보존했다. X/Y를 m로 읽으면 안 된다. 변환은 제품의 worldToMeters/metersToWorld 계약을 따른다. |
| after.nav vx/vy | 기존 world units/s | speed는 m/s, heading은 rad. |
| CIWS azBodyRad/elBodyRad/turretErrorRad | rad | C1 각도 CSV와 보고서의 deg 표기와 구별한다. |
| HP/모듈 dmg | 기존 게임 손상 척도 | 에너지 Joule/폭약 kg와 동일하지 않다. parts.dmg와 적용 직전×3.5, clamp 후 모듈 상태를 구분한다. |
| blastChannels | 기존 커널의 응답 성분 | 단순 합계가 최종 moduleDamage.dmg 또는 HP가 되는 것은 아니다. |
| ledger *J / strength absorbedEnergyMJ | J / MJ | HP와 직접 더하지 않는다. 열/파편/충격 에너지 장부는 별도다. |
| flood waterM3 / flowM3s | m³ / m³/s | 피격 직후0은 장시간 침수까지0이라는 뜻이 아니다. 원 시나리오는 위협 소실/명중 직후 끝난다. |
| legacy ciwsUsed | **모든 CIWS mount 잔탄 차의 합** | 20mm와 RAM을 섞어 더한 카운터다. 분석은 CIWS_FIRE와 RAM_AMMO로 분해했다. |
| shipHits | 기존 shipHitHistory 길이 | 정상 폭발뿐 아니라 불발/잔해 접촉도 포함한다. |
| shipAlive | 기존 시험의 shipHP>0 | 실제 수밀/복원성 solver의 survival.state/lost/irreversible과 구분한다. HP0이어도 NORMAL일 수 있다. |
| CONTACT_AUDIT localId / cmsTrackId | CIWS 로컬 파일 / 전투체계 트랙 번호 | mount마다 로컬 파일이 다르다. 항상 첫 파일이 실제 선택 파일인 것은 아니다. 분석은 CIWS_STATE에 기록된 선택 파일을 추적한다. |
| PROTECTION_ASSOCIATION sourceKey | 계측용 원시 RF 경계 source key | native WeakMap의 상태를 읽기만 했다. OWN_RAM과 ASM의 개별 숫자 id가 같아도 source key는 구별된다. |

기본 run은 기존 MANUAL/AutoAAOFF fixture다. SM/ESSM0발을 AUTO 방어 성능의 측정값으로 사용하지 않는다. 별도 표기가 없는 평균은 각 표의 실제 회차 수로 나눈 산술평균이다.
