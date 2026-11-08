# SEEKER_UNIFY_U4 작업 전 감사

- IMPLEMENTED: 감사 산출물만 구현; 제품 코드 변경 없음
- TESTED: 병합 제품 bytes/SHA, packed-main 구문, 함수 해시·중복 경로 정적 감사
- APPROVED: PR #75 승인 head의 merge commit 병합 결과만 승인됨
- UNRESOLVED: U4 A/B/C의 SHADOW 및 ACTIVE 동등성은 후속 게이트 대상
- RELEASE: 아니오

## 고정 기준

- main merge: `f17d3777a625699ab26f6a40de80a383f675ae85`
- product: `Aegis_SIM_v48_WIP_ESM_A.html` (22,182,527 bytes)
- product SHA-256: `5dcc6201d6acf32f56d570b01bbb33b673d835505ff877e70796e60a4bd3dad7`
- packed main SHA-256: `280458afa6207bfbb2a7aa078e47445b4cd449b78b244834a5a267d4360fbbc3`

## 함수·호출 경계

| 그룹 | 함수 | 발생 | line | bytes | SHA-256 | 외부 참조 수 |
|---|---|---:|---:|---:|---|---:|
| common | `seekerEchoSampleU1` | 1 | 56328 | 1069 | `ad00cce123d4b818…` | 5 |
| common | `seekerResolvedCellU1` | 1 | 56340 | 574 | `71510a38012a6cb1…` | 3 |
| common | `seekerMeasurementU1` | 1 | 56346 | 1180 | `4032b9e548510b5b…` | 4 |
| common | `seekerEstimateU1` | 1 | 56356 | 715 | `aa0dc08e1f151713…` | 4 |
| common | `seekerProfileViewU1` | 1 | 56364 | 2154 | `c2ceb7f407139454…` | 1 |
| common | `seekerRngAdapterU1` | 1 | 56374 | 193 | `7a2fba6d49026c2b…` | 7 |
| common | `seekerDelegateU1` | 1 | 56375 | 179 | `e69b7a35e210601d…` | 11 |
| common | `seekerSynthesizeMonostaticPowerU2` | 1 | 32629 | 1308 | `d5b132d5c46c0089…` | 4 |
| common | `seekerResolveCellsU2` | 1 | 32651 | 723 | `0afe4c1a7228bbac…` | 4 |
| asm_harpoon | `asmSeekerAssociateMeasurements` | 1 | 32951 | 3584 | `6d9a017285c8a40c…` | 5 |
| asm_harpoon | `updateAsmSeeker` | 1 | 32991 | 5337 | `bcc8823958afd4bf…` | 3 |
| asm_harpoon | `asmUpdateHojTrack` | 1 | 32306 | 749 | `9a4c0ffe3d6030b7…` | 3 |
| asm_harpoon | `asmPassiveRfMeasurementB2` | 1 | 44070 | 4879 | `47509b5d3a06b976…` | 3 |
| asm_harpoon | `harpoonMemoryA` | 1 | 58177 | 860 | `70b445a004f1c19c…` | 4 |
| asm_harpoon | `harpoonPredictionA` | 1 | 58186 | 480 | `1def723237831730…` | 7 |
| asm_harpoon | `harpoonRfObservationsA` | 1 | 58379 | 2850 | `2643b0fc1f4be509…` | 4 |
| asm_harpoon | `harpoonSeekerA` | 1 | 58409 | 4595 | `5fe758bb71311762…` | 11 |
| sarh_arh | `_sarhTruthReflectorPool` | 1 | 45142 | 347 | `472d091247ae4509…` | 7 |
| sarh_arh | `buildNavalSarhEchoPool` | 1 | 10763 | 3846 | `430cd54d3815a919…` | 2 |
| sarh_arh | `buildNavalSarhEchoPool` | 2 | 45155 | 3848 | `51f3f8d96b2b0d23…` | 2 |
| sarh_arh | `_sarhClusterEchoes` | 1 | 45184 | 426 | `2562cb39054e59ff…` | 3 |
| sarh_arh | `_sarhMonopulseMeasurement` | 1 | 10786 | 2684 | `3e1c9b081cc32f18…` | 3 |
| sarh_arh | `_sarhMonopulseMeasurement` | 2 | 45193 | 2686 | `5c6878c1ecc3b2ca…` | 3 |
| sarh_arh | `_sarhBuildMeasurementSet` | 1 | 10804 | 580 | `3a46e3f5f401a9ef…` | 5 |
| sarh_arh | `_sarhBuildMeasurementSet` | 2 | 45211 | 582 | `13aea10e52741a80…` | 5 |
| sarh_arh | `_sarhAssociateMeasurements` | 1 | 45267 | 1929 | `a00e9e6443e7500c…` | 5 |
| sarh_arh | `_sarhUpdateStateMachine` | 1 | 45298 | 1825 | `c92f635e8294654b…` | 3 |
| sarh_arh | `_v1UpdateSarhMeasurementCore` | 1 | 10809 | 2693 | `405509ce33fe59ca…` | 10 |
| sarh_arh | `_v1UpdateSarhMeasurementCore` | 2 | 45325 | 2695 | `e55814824ca6cb2c…` | 10 |
| sarh_arh | `_v1StepSarhSensorV1` | 1 | 10827 | 1107 | `0db6783e62c99752…` | 9 |
| sarh_arh | `_v1StepSarhSensorV1` | 2 | 45439 | 1109 | `ffc69f2298091aa4…` | 9 |
| sarh_arh | `getSarhTargetStateV1` | 1 | 10846 | 1743 | `f354d3203371344a…` | 6 |
| sarh_arh | `getSarhTargetStateV1` | 2 | 45459 | 1745 | `1319eaa58961df8a…` | 6 |
| sarh_arh | `_v1SelectGuidanceSource` | 1 | 44738 | 4797 | `3d3b986413f1a630…` | 11 |
| sarh_arh | `_arhAssociateMeasurements` | 1 | 45925 | 3245 | `c005213851ebf779…` | 9 |
| sarh_arh | `_arhUpdateStateMachine` | 1 | 45743 | 1124 | `0bbffffbd48aea6f…` | 4 |
| sarh_arh | `_v1UpdateArhMeasurementCore` | 1 | 10935 | 3164 | `541cc241de7536ac…` | 9 |
| sarh_arh | `_v1UpdateArhMeasurementCore` | 2 | 45958 | 3166 | `a3787bc68dccd919…` | 9 |
| ram | `ownerRamRfD` | 1 | 7744 | 1544 | `710a021320f59ec4…` | 1 |
| ram | `ramEmitterStrength` | 1 | 39418 | 334 | `fac9ec61d61cf0f6…` | 2 |
| ram | `ramIrSourceSignal` | 1 | 39462 | 721 | `07b796e2769be9a3…` | 2 |
| ram | `ramRfMeasurement` | 1 | 7914 | 118 | `f9b1864c781645af…` | 5 |
| ram | `ramRfMeasurement` | 2 | 39443 | 1654 | `62794f82c6fa1566…` | 5 |
| ram | `ramIrMeasurement` | 1 | 9182 | 3375 | `8ff27eec47982c15…` | 5 |
| ram | `ramIrMeasurement` | 2 | 39471 | 3407 | `35e231fb9e4163a1…` | 5 |
| ram | `ramNewAngularTrack` | 1 | 39383 | 370 | `5cfdff42fd902977…` | 10 |
| ram | `ramUpdateAngularTrack` | 1 | 39392 | 1438 | `14ac15ccd2a96043…` | 5 |
| ram | `ramUpdateSeekerAuthority` | 1 | 39507 | 2414 | `6fb8873c2cbb8be4…` | 4 |
| ram | `ramGuidanceTrackForAuthority` | 1 | 39539 | 613 | `5744dc0619c2c8c5…` | 2 |
| ram | `ramGuidanceFromEstimateB2` | 1 | 9232 | 3243 | `6b7ebe71565bc5a8…` | 7 |
| ram | `ramGuidanceFromEstimateB2` | 2 | 39567 | 3245 | `960b70fe9c71dbba…` | 7 |
| ram | `initializeRamSeeker` | 1 | 9211 | 1231 | `5943dc8cb87b071a…` | 5 |
| ram | `initializeRamSeeker` | 2 | 39546 | 1233 | `6e1d2f2e57fa8e7e…` | 5 |
| ram | `updateRamMeasurementSeeker` | 1 | 9223 | 654 | `f62abb15d0adab68…` | 4 |
| ram | `updateRamMeasurementSeeker` | 2 | 39558 | 656 | `914922b3e7418ddb…` | 4 |
| ram | `ramSelectedSeekerTrack` | 1 | 39500 | 177 | `95aafd4b25c2d512…` | 6 |

## 분류

| 영역 | 분류 | 근거 |
|---|---|---|
| U1/U2 anonymous DTO and ASM/ARH/Harpoon echo-cell route | `LEGACY_EQUIVALENCE` | U1 delegates and U2 ACTIVE families already preserve existing front-end values and RNG ownership. |
| SARH two-leg path, SPG allocation/emission, two LOS and TX/RX beams | `HARDWARE_DIFFERENCE` | buildNavalSarhEchoPool derives tx/rx geometry and rejects missing physical illumination before measurement. |
| SARH anonymous clustering/measurement/association/state | `IMPLEMENTATION_DIVERGENCE` | Separate SARH implementations duplicate ARH-shaped lifecycle responsibility while retaining a bistatic observable. |
| RAM player versus owner/NPC RF/IR producer paths | `IMPLEMENTATION_DIVERGENCE` | ownerRamRfD plus closure-local IR path coexist with global ramRfMeasurement/ramIrMeasurement implementations. |
| RAM passive RF/IR observation model and RF-first/IR authority | `HARDWARE_DIFFERENCE` | Bearing-only passive RF and IR measurements cannot be represented as active monostatic radar echoes. |
| RAM emitter signal ownership | `DEFECT_CANDIDATE` | ramEmitterStrength multiplies physical emitter strength by em.seeker.trackQuality/_seekerQuality; transmitter output is coupled to a local tracking state. |
| Common association/state transition ownership | `IMPLEMENTATION_DIVERGENCE` | ASM, Harpoon, SARH, ARH and RAM each retain separate gate selection and transition code. |
| Historical debug source fields on physical echo/IR candidates | `UNRESOLVED` | Debug fields exist in front-end products; U4 must prove they are absent from tactical association and common outputs rather than silently deleting diagnostics. |

## 상태·RNG·수명주기 소유자

| 계열 | local state | RNG | lifecycle | 보존 훅 |
|---|---|---|---|---|
| ASM | per-ASM seeker object | ASM seeker RNG on weapon | weapon lifecycle | HOJ hook retained |
| Harpoon | m.seeker + m.memory/cueHandoff | per-Harpoon seeded seeker RNG | launch/destroy missile lifecycle | route/INS/HOJ hooks retained |
| SARH | m._sarhSensorV1 | m._sarhRngState | v1 missile lifecycle | SPG allocation and source arbiter retained |
| ARH | m._arhSensorV1 | m._arhRngState | v1 missile lifecycle | SARH/DL source arbiter retained |
| RAM player | rm._ram*Track + authority fields | simRandom/gaussRand stream | RAM missile lifecycle | MEM/RF/IR authority retained |
| RAM owner/NPC | owner RAM rm._ram* fields | owner weapon RNG callback | owner runtime lifecycle | same authority/guidance contract |

## 최신 코드와 A 설계 문서의 차이

- U1에는 네 관측 차원 enum이 이미 존재하고 U2 ACTIVE에는 ASM, SAM ARH, Harpoon echo/cell 계열이 연결돼 있다.
- SARH는 최신 코드에서 `buildNavalSarhEchoPool` → `_sarhClusterEchoes` → `_sarhMonopulseMeasurement` → local EKF/NIS 순으로 독립 구현돼 있다.
- RAM은 owner/NPC closure와 player 경로가 중복돼 있고, 각각 기존 RNG 소유자를 달리한다. 공통화는 RNG callback을 주입해야 한다.
- `ramEmitterStrength`의 추적 품질 역의존은 물리 방사원 소유권 결함 후보로 확인됐다. U4 B에서 기존 기본값이 암시하던 수치만 보존해 좁게 분리하고 별도 보고한다.

## 정보 비누수 경계

물리 프런트엔드는 실제 장면을 읽을 수 있다. 공통 DTO, 연관, 상태기계와 유도 소비자에는 익명 관측값·공분산·시각·품질·익명 key만 전달한다. `_debugSource*` 필드는 제품 판단에 사용하지 않으며 진단 사후 비교로만 제한한다.
