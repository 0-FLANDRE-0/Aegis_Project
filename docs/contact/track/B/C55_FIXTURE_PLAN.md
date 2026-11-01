# C55 TRACK-B 시험 계획 — 미실행

이 파일은 **시험 설계**이며 PASS 결과가 아니다. live 연관/제어 변경·브라우저 사격·기대값 갱신 없이 작성했다. shadow module/patch manifest는 준비됐으며 shared pure helper와 native 경로의 실제 합성·검증 범위는 별도 증거로 확인해야 한다.

## 1. 순수 helper fixture

모든 fixture는 자함/NPC의 같은 DTO를 각각 제공하고 동일 helper 결과를 비교한다. file ID는 해당 문맥의 전술 local ID이며 목표 physical ID가 아니다. geometry truth label이 필요하면 AFTER_ACTION assertion에만 둔다.

| ID | 조건 | 필수 판정 |
|---|---|---|
| C55-B01 | 분리된2개 track/plot, 각각 후보1개 | source/track 입력 순서 permutation에도 같은 일대일 mapping, ambiguity0 |
| C55-B02 | AUDIT의 scarce-edge 반례(T4000/4200, P4099/4000, hits8/age.05) | 기존 greedy의 source-order별 birth 차이를 재현. shadow가 2-matching을 찾지만 component를 ambiguous로 표시. 단순 birth 감소를 ID 정확성 PASS로 세지 않음 |
| C55-B03 | 동일 noisy 위치 또는 완전 대칭 tie | 임의 physical ID/faction으로 tie를 깨지 않음. ambiguity와 exact tie 기록, 같은 관측에서 사실상 구분 불가를 명시 |
| C55-B04 | own RAM과 non-own ASM이 위치·분산까지 동일 | own/non-own partition별 각각 독립 후보. own 측정이 non-own 파일을 갱신하거나 반대 경우0. source 순서 반전에도 보호 오염0 |
| C55-B05 | own 아닌 Harpoon과 적 ASM이 겹침 | 숨은 owner/weapon type을 추가 gate로 쓰지 않음. 관측 모호성만 보고. Harpoon을 강제로 FRIEND로 지정0 |
| C55-B06 | warm-up hits<5, broad coast term, 인접 noise-tail plot | 기존 gate 그대로. 폭넓은 covariance/초기 prior만으로 강제병합·confirmed 승격0. ambiguity/candidate 증가를 기록 |
| C55-B07 | GUN .70s / RAM .85s coast 경계와2.0s expiry | native exact 경계 유지. stale/expire와 ambiguous를 혼동하지 않음. shadow가 age/hit/quality를 refresh하지 않음 |
| C55-B08 | gate 거리와 정확히 같음 / 바로 안쪽 / 바로 바깥 | 기존 strict `<gate` 유지. helper 계산 순서가 동일한 native 비교 결과인지 확인 |
| C55-B09 | 현재 gate 안의 관측 FRIEND/NEUTRAL CMS, nearest는 다른 row | 기존 conservative veto 유지. helper가 CMS authority/분류를 새로 만들거나 보호를 해제0 |
| C55-B10 | protectedCmsId가 있었고 현재 CMS match 없음 | 기존 sticky 결과를 명시적으로 보존·진단. 새 TTL/expiry fix를 B에 섞지 않음 |
| C55-B11 | file capacity48 및 추가 accepted plot | maxFiles/drop 정책과 local ID 할당 순서 baseline 유지. shadow overflow는 진단만, 실제 source/파일을 조용히 삭제0 |
| C55-B12 | null, attemptedfalse, acceptedfalse, NaN/Infinity, 부분 geometry | 미측정/거부를 정상 plot으로 승격0. 후보 evaluated 여부 구별. 없는 NIS/속도를 생성0 |
| C55-B13 | 동일 local ID를 가진 서로 다른 함/같은 위치 mount들 | 호출 문맥별 독립 graph/store. 타 함 private track/FCS 상태 직접참조0 |
| C55-B14 | payload에 truthRef/objectId/faction/owner/label/실제속도 주입 | normalized/shared helper가 해당 필드를 읽지 않거나 결과에 영향0. actual observable geometry만 같으면 출력 동일 |
| C55-B15 | 이미 used인 file에 두번째 plot 또는 같은 payload 반복 | one-to-one 충돌을 기록. duplicate observation/hit 정책을 제멋대로 바꾸지 않음. 한 file의 중복 update0인 native 계약 유지 |
| C55-B16 | selected source가 sweep 중 다른 file로 잘못 연관될 가능성이 있는 배열 | native source order·TRACK/SEARCH mode·dwell·private RNG 호출이 shadow OFF/ON에서 같음. 측정 batch 지연이 mode를 바꾸는 사례를 찾아 live 적용 위험으로 기록 |

## 2. native crossing/모호성 시나리오

1. 근접한 실제2 ASM의 교차: 원래 센서 noise/RF 사용. source enumeration 순서 변경은 **fixture comparison**으로만 하며 제품의 배열을 재정렬하지 않는다. false merge, false split, ID swap, 실제 drop/reacquire, duplicate birth와 age를 분리한다.
2. own RAM/non-own ASM 및 own no-DL Harpoon/non-own ASM 근접: 알려진 발사 증거와 CMS 관측만 사용해 보호되는지 확인한다. 물리 truth는 사후 source↔file 계보 판정에만 사용한다.
3. 실제 헬기 IFF ON/OFF/expiry와 CMS보호: IFF ON AUTO에서 VLS/ESSM/CIWS 소모0. IFF OFF를 truth exception으로 보호하지 않는다. 모호한 file을 HOSTILE로 자동 승격0.
4. 다함정 owner: DDG/CG의 player와 NPC 각각 C55 동작, independent banks/private RNG, 공통 helper 결과를 확인한다. 같은 전술 번호·같은 위치가 다른 함 store에 있어도 결합0.

## 3. 기존 필수 회귀

- CIWS30: seeds419010~419039, DDG-119, bearing90°, Kh-35U1발/11km, MANUAL, 함포 AutoAA OFF, native1/60s. shadow ON/OFF 및 baseline 비교에서 전체 결과/RNG 서명 동일이어야 한다. 419025는 상세 타임라인 별도.
- A 자연 재현3개: 헬기 hover60s/route120s, Harpoon route75s. C55 shadow를 켜도 native tracker/센서/무장 결과 차이0.
- 실제 C55 receiver mode, sensor dwell, bank RNG, gun aim/shot RNG, global RNG, local ID birth 순서, selected file, 보호 증거·발사 동의, 탄약/피해를 같은 fixed tick에서 비교한다. host wall-time만 별도 제외한다.
- 1/8/16/64배속, owner당1회/tick, query 무쓰기·무RNG. 새 shadow가 기존 candidate 계산을 재실행해 lazy state를 만들지 않는지 확인한다.
- 성능: trace OFF 기본 overhead, shadow ON의 평균/p95 CPU·allocations·accepted plots/candidates/component 크기와 ring overflow를 별도 보고한다. diagnostics overflow를 시험 coverage 성공으로 세지 않는다.

## 4. 비교 자료/판정 파일 계획

각 run에 `buildHash`, 조건/seed, source **전술/diagnostic** measurement ID, owner/mount, native mapping, shadow proposals, component ambiguity, 실제 evaluated 거리/gate 및 reject 이유, 생성/유지/expire, before/after whitelist 상태, 실제 sensor mode/dwell 및 RNG 서명을 기록한다. physical source와 truth는 별도 AFTER_ACTION 로그에만 둔다.

`PASS`: 실행한 조건에서 순수성·one-to-one·partition·native 동등성 등이 확인된 항목만.

`KNOWN_DELTA`: root가 원인 증거로 확인한 기존 차이. 미승인 결과를 기대값 갱신으로 제거하지 않는다.

`FAIL`: source order나 helper 진단 때문에 RF/RNG/무장 상태가 바뀌거나 보호 오염, false merge/ID swap/무방비 전환이 생긴 경우.

`BLOCKED/INCOMPLETE`: native fixture·검증 미실행 또는 legacy/환경 문제. 이 문서의 모든 예정 항목은 현재 여기에 해당한다.
