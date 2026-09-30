# AEGIS v48 WIP14 — Missile Navigation, Weapon Link, and Loft Plan

작성일: 2026-09-29 (KST)  
계획 기준: GitHub `main` commit `a8d14e3484200098be2143e0547c8e922642c042` + 로컬 `Aegis_SIM_v48_WIP14B1.html` 후보

## 1. 이번 검토 결론

기존 B2(단방향 DL packet transport)와 B3(제한적 양방향 DL)는 **하나의 구현 단계 B2로 통합하는 편이 낫다.** 둘은 지연·손실·순서·age·지원 종료시각·채널 상태를 같은 범용 transport가 소유해야 하며, 따로 구현하면 두 번째 단계에서 queue와 지원 상태를 다시 뜯어고칠 가능성이 크다. **양방향 기능은 SM-6 전용 구조로 만들지 않는다.** 공통 weapon-link가 uplink와 return-link를 모두 지원하고, 각 미사일 profile이 활성화 여부와 세부 링크 스펙을 선언한다. 현재 WIP14에서는 SM-6가 return-link를 실제로 활성화하는 첫 profile일 뿐이다.

다만 한 번에 섞어 구현하지 않고 같은 B2 안에 독립 gate를 둔다.

| 내부 gate | 범위 | 종료 조건 |
| --- | --- | --- |
| B2a — 공통 transport + 단방향 uplink | 모든 적용 미사일의 launcher→missile target-state packet, delay/loss/sequence/age/uncertainty | 단방향 무장 회귀와 DL hard-cut/IOG 전이가 먼저 통과 |
| B2b — 범용 return-link transport + 첫 활성 profile | 공통 missile→launcher return 경로; 현재 WIP14에서는 SM-6 profile이 onboard-nav/uncertainty/phase/health 반환을 활성화 | 특정 미사일 하드코딩 없이 profile별 enable/payload/cadence/link-spec을 따르고, 반환값이 물리 truth를 노출하거나 지원 종료시각을 연장하지 않음 |
| B2c — bounded assistance 및 통합 회귀 | return-link가 활성화된 profile의 onboard state와 launcher track만으로 profile-bounded advisory 생성; 현재 첫 적용은 SM-6 | assistance age-out, profile 상한, link cut, 1×/8×/16× 결정성 통과 |

이렇게 하면 한 branch/한 release gate에서 transport를 완성하면서도 B2a가 실패한 상태에서 B2b를 정상으로 오판하지 않는다. 기존 `B3` 번호는 **B2에 흡수됨**으로 남기고 다른 기능에 재사용하지 않는다. `B4` 로프팅 번호도 그대로 유지해 기존 대화·증거의 참조가 바뀌지 않게 한다.

## 2. 단계 갱신

| 이전 대응 | WIP14 단계 | 상태/결정 |
| --- | --- | --- |
| A15 | B1 — onboard INS/GPS 및 DL truth boundary | 로컬 후보 구현·결정적 검사 완료, 원격 대형 HTML 미업로드 |
| A16 + A17 | B2 — 공통 weapon-link transport + 범용 양방향 capability (SM-6 first enabled profile) | **통합 승인안**, 아직 미구현 |
| B3 | B2에 흡수 | 독립 구현/산출물 없음 |
| A18 | B4 — 미사일별 stateful loft profile | 미구현, B2와 분리 유지 |

B2와 B4를 같이 구현하지 않는다. DL state/latency 변화와 loft state 변화는 모두 장거리 궤적에 영향을 주므로 같이 바꾸면 180 km 저고도 표적 실패의 원인을 분리할 수 없다.

## 3. B1 기준선

B1 후보가 확립한 경계는 B2에서 보존한다.

- SM-2MR, SM-2ER, ESSM은 무장별 INS own-state를 사용한다.
- SM-6는 GPS/INU own-state와 0.5 s 간격의 `SIM_TUNED` 보정을 사용한다.
- DL target state, seeker 상대측정, PIP/PN/APN/ZEM/Kappa/autopilot/planner는 미사일 onboard navigation frame을 소비한다.
- DL hard-cut 뒤에는 global track 또는 target truth를 직접 읽어 갱신하지 않는다.
- 물리 truth는 비행물리, RF echo 합성, 충돌·신관·피해, 진단 비교에만 남는다.

2026-09-30 추가 감사에서 이 B1 own-state 경계가 현재 SM-2MR/SM-2ER/SM-6/ESSM v1 경로에만 적용되고, Kh-35U/Kh-32와 RAM에는 raw physical own-state guidance consumer가 남아 있음이 확인됐다. 상세 내용은 `docs/wip14/B1/AEGIS_WIP14B1_OWN_NAV_COVERAGE_AUDIT.md`를 따른다. 따라서 범용 return-link transport는 **어떤 미사일의 physical `x/y/z/vx/vy/vz`도 return payload의 onboard state로 직접 포장하지 않는다.** ASM/RAM 등 다른 계통에서 return-link를 활성화하려면 먼저 해당 계통의 error-bearing onboard navigation adapter를 연결해야 한다.

## 4. B2 통합 아키텍처

### 4.1 공통 transport 소유권

각 발사탄은 하나의 weapon-link record를 가진다. 공통 record가 다음을 소유한다.

- 익명 target track ID와 link/channel ID
- launch-time support plan 및 **불변 support deadline**
- uplink/downlink별 tx/rx sequence, next transmit time, pending delivery queue
- packet 지연, 손실, out-of-order, 마지막 수신 시각과 link health
- source track timestamp, packet age, target covariance와 age에 따른 uncertainty growth
- transport 전용 결정적 RNG stream

transport core는 `missileType === 'SM6'` 같은 무장별 특수분기로 양방향 기능을 결정하지 않는다. 각 무장의 link profile이 최소한 `uplinkEnabled`, `returnLinkEnabled`, 송신 주기/대역·payload class, delay/jitter/loss/out-of-order, max age/TTL, uncertainty growth, assistance 허용 여부와 상한을 선언한다. 현재 profile에서 return-link가 꺼진 무장도 나중에 profile 변경만으로 같은 공통 transport를 사용할 수 있어야 하며 core queue/scheduler를 다시 작성하지 않는다.

렌더러, 로그, 진단은 queue를 소비하거나 RNG 순서를 바꾸지 않는다.

### 4.2 Uplink payload

launcher→missile packet은 센서/트랙 계층이 가진 정보만 보낸다.

- target position/velocity estimate와 covariance
- track sample time, transmit time, sequence
- predicted intercept/PIP 관련 bounded advisory
- 지원 종료시각과 link health
- return-link와 assistance가 활성화된 profile에 한해 최신 return packet을 사용해 계산한 bounded guidance advisory; 현재 WIP14 첫 활성 profile은 SM-6

target object reference, 실제 target position, 실제 생존 상태, 미래 truth 궤적은 payload에 넣지 않는다. 수신 측은 새 sequence만 채택하고, packet age와 covariance를 증가시킨다. 지연되거나 역순인 packet은 기록만 남기고 권위 상태를 되돌리지 않는다.

### 4.3 범용 return-link payload/profile

return-link는 공통 weapon-link transport의 선택 기능이다. core 구현은 특정 미사일에 종속되지 않으며, 각 미사일 profile이 `returnLinkEnabled`, payload capability와 송신 주기·지연·손실·freshness/TTL 등 세부 스펙을 가진다. 현재 WIP14에서는 SM-6 profile만 이 기능을 활성화하고, 그 첫 payload는 다음으로 제한한다.

- 미사일이 스스로 추정한 nav position/velocity
- onboard position/velocity uncertainty
- guidance phase와 seeker handoff/terminal acknowledgement
- nav aid/link health
- sequence, sample time, transmit time

어떤 미사일 profile이 return-link를 활성화하더라도 반환 packet은 물리 좌표나 표적 탐지 truth를 보내는 통로가 아니다. launcher는 반환된 onboard nav state를 coast할 수 있으나 freshness가 끝나면 launch-time plan으로 후퇴하거나 assistance를 중단한다. 다른 미사일이 나중에 양방향 DL을 사용하더라도 이 공통 payload/envelope 계약 위에 무장별 capability만 추가하며 별도 transport를 만들지 않는다.

### 4.4 Bounded assistance

launcher assistance는 직접 가속도나 조종면 명령이 아니라 다음 advisory에 한정한다.

- PIP/expected TGO 보정
- pursuit/loft scale의 제한된 보정
- corridor altitude 및 terminal handoff 권고

confidence, packet age, target covariance, missile nav covariance로 가중하며 profile별 상한을 둔다. assistance 자체도 profile capability이며 return-link가 있다고 자동 활성화되지 않는다. return link는 최초 support deadline을 갱신하거나 연장할 수 없다. deadline/cut 이후에는 pending packet도 폐기하고 미사일 local IOG/seeker가 권위를 갖는다.

## 5. 무장별 link 계약

| 무장 | Own navigation | Uplink | Return link | 종말 권위 |
| --- | --- | --- | --- | --- |
| SM-2MR | INS | one-way target-state | 현재 profile 비활성 — 공통 return-link 사용 가능 | SPG-62/SARH 측정 |
| SM-2ER | INS | one-way target-state | 현재 profile 비활성 — 공통 return-link 사용 가능 | SPG-62/SARH 측정 |
| SM-6 | GPS/INU | target-state + bounded advisory | **현재 활성 profile** — onboard nav/uncertainty/phase/health만 | onboard ARH/seeker |
| ESSM Block 2 | INS | one-way target-state | 현재 profile 비활성 — 공통 return-link 사용 가능 | onboard ARH/seeker |
| AIM-174B | 참고용 | 참고 HTML의 구조만 검토 | 참고용 | **함정 VLS/운용 무장에 추가 금지** |

SM-2의 SPG-62 지원과 weapon-link transport는 서로 다른 상태다. DL 손실이 SPG illumination을 자동 종료시키거나, 반대로 illumination이 DL deadline을 연장하지 않는다.

## 6. B2 필수 검증

1. zero-delay/zero-loss fixture에서 B1 유도 결과가 허용 오차 안에 유지된다.
2. 고정 delay/loss/out-of-order 패턴을 같은 seed로 반복하면 packet sequence와 비행 결과가 exact 또는 명시 오차 안에서 같다.
3. 1×/8×/16×가 같은 fixed-step packet 이력과 결과를 만든다. 64×는 별도 성능 검사다.
4. 오래된 packet은 새 state를 덮지 못하고 packet age/covariance가 단조 증가한다.
5. hard-cut/support deadline 뒤 global track/truth 갱신은 0회다.
6. 현재 무장 profile 기준으로 SM-2MR/ER와 ESSM에는 return packet이 0회이며 SM-6 profile만 제한된 return을 만든다. 이것은 **현재 profile 설정의 결과이지 transport core의 무장 제한이 아니다.**
7. synthetic/profile fixture에서 다른 무장의 `returnLinkEnabled`를 켜면 core 수정 없이 같은 queue/scheduler/envelope로 return packet을 만들 수 있어야 한다.
8. SM-6 return의 position은 onboard nav solution과 같고 physical truth와 의도적 오차가 존재한다.
9. return packet 수신 전후 `initialSupportEndS === finalSupportEndS`가 유지된다.
10. assistance는 profile 상한, age-out, low-confidence fade를 지키며 terminal seeker 권위를 덮지 않는다.
11. GPS aid 중단, uplink 중단, return-link 단독 중단, 완전 link cut을 각각 분리해 검증한다.

## 7. B4 — 무장별 stateful loft

B4는 공통 상태기계 `CLIMB → CRUISE/ENERGY-SHELF → DIVE`를 사용하되 **전이 조건과 corridor는 미사일별 profile로 분리한다.** DIVE 진입 뒤 CLIMB로 재진입하지 않는다.

| 무장 | 별도 profile 방향 |
| --- | --- |
| SM-2MR | 중거리용 완만한 climb와 짧은 shelf, SARH 지원·terminal geometry를 고려한 조기 descent |
| SM-2ER | booster 에너지를 이용한 장거리 climb/shelf, booster 분리·q/Mach·에너지 reserve 기반 전이 |
| SM-6 | 가장 긴 networked midcourse shelf, GPS/INU와 B2 assistance를 제한적으로 소비하되 onboard state가 최종 권위 |
| ESSM Block 2 | 단거리/중거리 direct 또는 mild loft, 불필요한 고고도 climb 금지 |

각 profile은 최소한 launch range, target altitude, remaining range/TGO, Mach, dynamic pressure, energy height, nav/track uncertainty를 입력으로 사용한다. 단일 고정 `tgo <= 30 s` clamp나 모든 미사일 공통 pitch bias로 장거리 loft를 결정하지 않는다.

180 km, 표적고도 2 km 회귀에서는 특정 apex를 하드코딩하지 않는다. 대신 다음을 확인한다.

- SM-2ER/SM-6가 약 2.4 km에서 장거리 수평비행을 계속하는 기존 비정상 패턴을 벗어나는가
- profile이 CLIMB/CRUISE/DIVE 전이를 실제로 기록하는가
- apex, q, Mach, specific energy, remaining range/TGO가 유한하고 전이 뒤 재-loft가 없는가
- 표적 도달/실패가 에너지·지원·시커 조건으로 설명되며 좌표 truth 주입으로 보정되지 않는가

권장 envelope는 40/80/120/180 km × 표적고도 0.05/2/10 km이며, 동일 seed의 1×/8×/16× 궤적 milestone을 비교한다.

## 8. 참고 HTML에서 재사용할 개념

`references/wip14/Radar_v7_64_ECCM_SUSTAINED_STRESS_ENEMY_DEFENSE_TOGGLES.html`은 공대공 시뮬레이터라 AEGIS 코드의 직접 기준은 아니다. 아래 개념만 donor로 검토한다.

- `AIR-NAV-1`: missile physical state와 onboard INS/GPS solution 분리
- `AIR-DL-1/2`: launch-time support plan, packet queue, delay/loss/sequence, one-way와 two-way 공통 transport
- two-way/return-link는 특정 무장 전용이 아니라 profile-capability로 활성화하며, 현재 WIP14에서는 SM-6가 첫 활성 예시
- return packet은 profile이 허용한 onboard nav/uncertainty/phase/health 등만 반환하고 support deadline을 연장하지 않는 invariant
- 반환 state와 target track으로 계산한 profile-bounded guidance assistance
- AIM-174B `CLIMB → CRUISE → DIVE` latched corridor와 DIVE 이후 re-loft 금지

수치, 공대공 radar/FCS, AIM-174B 성능값을 그대로 이식하지 않는다. AIM-174B는 SM-6 계열 설계 아이디어 비교용일 뿐 함정 VLS inventory나 교전 UI에 추가하지 않는다.

## 9. 이번 branch에서 하지 않은 것

- B2/B3 코드 구현 또는 튜닝
- B4 loft 구현 또는 무장별 수치 선정
- `Aegis_SIM_v48_WIP14B1.html` 대형 파일 업로드
- 현재 `main` 수정, PR 생성, 병합, release/tag 생성

