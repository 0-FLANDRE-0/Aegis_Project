# AEGIS v48 WIP14B4 — Stateful Game Trajectory Candidate

갱신: 2026-10-01 (KST)

**상태: 구현·범위별 회귀 통과 / 전체 CLOSED 보류.** 전 조건 명중이나 실제 무장 최대사거리 인증이 아니다.

## 기준과 로컬 산출물

- 기준: `Aegis_SIM_v48_WIP14B3.html`
- B3 SHA-256: `c6a75f9f2c03e925ec298d0cb5885fa9b043c066aeb62117cf4674ec0c313123`
- 결과: `Aegis_SIM_v48_WIP14B4.html`
- 크기: `7,319,028 bytes`
- B4 SHA-256: `03de975ddac38c192eae1572b2588bba49defcb148a2fd9ae7b6921f4e7355e2`
- decoded main SHA-256: `62aa1f6e8a4ff9445f3fde2f4d86e581e6457616daada424bf3c8a4164ba186b`
- 지원 ZIP: `AEGIS_v48_WIP14B4_SUPPORT.zip`
- 지원 ZIP SHA-256: `d264627913a7eba1f7ebfe94dbdf4f3328099cf4d7a44594fd7c3710b979ab20`

대형 HTML과 지원 ZIP은 대화 산출물이다. 이 문서 추가는 원격 HTML 업로드/main/runtime 기준 승격을 의미하지 않는다.

## 사용자 목표와 구현

사용자 최신 요청의 MR 160km대, ER/SM-6 240km 이상을 게임 설계·시험 목표로 사용했다. 실제 무장 제원이나 보장 사거리로 취급하지 않는다.

- MR/ER/SM-6/ESSM 각각의 `SAM_LOFT_B4_PROFILES`와 미사일 소유 `_loftB4` 상태를 기존 유도 경로에 연결.
- CLIMB → CRUISE → DIVE 단방향 진행. 가까운 경우 중간 단계를 건너뛸 수 있으며 DIVE 이후 재로프팅 금지.
- 자체 항법 추정치를 사용하며 실제 위치/속도/추력/피해를 강제 변경하지 않음.
- 국부 게임 경로 참조의 control horizon과 실제 표적 PIP/TGO를 분리하여 지원·종말 인계 시간을 혼동하지 않음.
- 단거리 및 프로필 최대 회랑보다 높은 표적은 기존 DIRECT 경로 보존. ESSM 고고도와 MR 고도20km 표적의 B3 비교 결과 일치.
- ESSM은 별도 mild-loft, RAM은 B2 각도 기반 직접 유도/해면 회피 보존. RAM에 새 고고도 로프팅을 추가하지 않음.
- 관제 게임 검토 범위 `effectiveRangeKmGameplay`: MR160, ER260, SM-6 260km. FCQ/권한/시선/SPG/NEZ/재고 게이트는 유지하며 이 수치로 명중을 보장하지 않음.
- DEBUG의 B4 단계/회랑/항법 고도/잔여거리 표시. getter/UI는 단계·항법·패킷을 진행하지 않음.

거리·속도 중심의 SIM_TUNED 단계형 게임 프로필이다. Mach/동압/에너지 높이/불확실성은 진단에 기록하며 완전한 에너지 최적제어기를 구현했다고 주장하지 않는다.

## 거리 시험 결과

명시적으로 합성 관측 트랙을 공급하는 독립 fixture에서 기존 실제 발사 게이트·SPG 예약/서보·비행·시커·신관·피해를 실행했다. 초기 자연 탐색부터의 전투 캠페인이나 기만/재밍/회피 기동 시험이 아니다. 거리값은 발사 당시 수평 분리거리다.

- MR160km: 고도2km 및10km 고정 표적 요격. 10km 사례는 약212.57초, 요격 위치의 함정 수평거리159.996km.
- ER240/260km: 고도10km 고정 표적 요격. 260km 사례는 약234.92초, 요격 위치259.987km.
- SM-6 240km/고도10km 고정 표적: seed142000 미스, 142001/142002 요격. 2/3은 통계적 Pk/안정적 최대사거리 증명이 아니다.
- SM-6 초기260km/고도10km/접근250m/s: 요격 위치는 함에서215.230km. 이를260km 지점 요격으로 표기하지 않음.
- SM-6 260km/고도10km 고정 표적 seed142000은 약259m 미스.
- ER240km/고도2km는 SPG 지원 `NO_CHANNEL`로 발사 거부. SM-6 같은 저고도/거리 조건은 비행했으나 미도달. 센서/지원 제한을 제거하지 않음.
- ESSM25km/고도2km 고정 표적 요격. 다수 중장거리 조건은 여전히 LOW_SPEED로 실패.

36개 주 시험과2개 추가 시험의 성공·미스·발사 거부를 모두 대화의 evidence에 보존했다. 고정 틱 샘플 최소거리는 연속 신관 계산의 정확한 CPA와 다를 수 있다.

## 실행한 검증

- 단계 단위33/33 PASS.
- B4 패키지 런타임8/8 PASS: MR160 고정, ER260 고정, SM-6 초기260 접근 표적의 전체 단계 비행 1×/8×/16×/64× 이력 일치 포함.
- B3 transport49/49, 패키지 런타임25/25 PASS.
- 패키지/정적 경계52/52 PASS; C55 14개 무결성/구문, 자산0~12 B3 byte-identical, B3→B4 재생성 exact.
- B2 nav38/38, VLS timing12/12, release policy22/22 PASS.
- 데스크톱/모바일 크기 2D/3D FIRE handler와 표시2/2 PASS. 실제 WebGL 렌더링 통과를 뜻하지 않음.
- B3 대비 ASM/RAM 분리 비행과 항법 배속 fixture 일치.
- B3 GPS/양방향 DL/고정 support deadline, B2 VLS 기본0.8초 및0.6~1.0초 설정 보존.
- 공력/추진/질량 동결 hash, 기존 셀 이탈·신관·피해 권위 보존.

묶음 간 하위 시험 중복이 있어 개수를 합산한 고유 시험 총수는 주장하지 않는다. 병렬 Chromium 실행 중 한 번의 page crash 후 최종 B4 런타임은 직렬로 다시 실행해8/8 통과한 evidence만 최종 판정에 사용했다.

## 한계 및 다음 확인

1. B3/B4 모두 기존 `V48 WIP13A surface target submergedBreachFloods` core 실패1건이 남음. 침수 코드나 해당 검사를 변경하지 않음.
2. Native file URL은 관리자 정책으로 차단, 전체 HTML set_content로 실행. 빈 페이지에서도 WebGL 생성 실패. 실제 3D 함체/연기/카메라 및 모바일 GPU/FPS 미검증.
3. SM-6 고정 장거리 seed별 미스, ESSM 중장거리 에너지 부족, 저고도 원거리 센서/지원 한계 및 회피/횡단/도주 조건을 추가로 확인해야 함.
4. 사용자 원격 HTML 업로드 후 위 해시를 대조해야 하며 현재 문서만으로 원격 runtime 기준을 승격하지 않음.

상세 보고서 `AEGIS_WIP14B4_REPORT.md`, 전체 결과 `AEGIS_WIP14B4_VALIDATION_SUMMARY.json`, 테스트·재생성 도구는 지원 ZIP에 포함된다. main/PR/merge/release/tag/AIM-174B 운용 등록은 변경하지 않았다.
