# AEGIS v48 WIP14 — Branch / Handoff Status

갱신: 2026-10-01 (KST)

## 현재 판정

**B4 로컬 구현·범위별 회귀 통과 / 전체 CLOSED 보류.** 기존 침수 core 실패1건, WebGL 시각 검증 및 일부 장거리 미스가 남아 있다. 최대사거리/전 조건 명중을 인증한 빌드가 아니다.

- 로컬 결과: `Aegis_SIM_v48_WIP14B4.html`
- 크기: `7,319,028 bytes`
- SHA-256: `03de975ddac38c192eae1572b2588bba49defcb148a2fd9ae7b6921f4e7355e2`
- decoded main SHA-256: `62aa1f6e8a4ff9445f3fde2f4d86e581e6457616daada424bf3c8a4164ba186b`
- 상세 상태: `docs/wip14/B4/AEGIS_PLAN_STATUS_v48_WIP14B4.md`
- 대화 지원 ZIP: `AEGIS_v48_WIP14B4_SUPPORT.zip`
- 지원 ZIP SHA-256: `d264627913a7eba1f7ebfe94dbdf4f3328099cf4d7a44594fd7c3710b979ab20`

대형 HTML/지원 ZIP은 이번에 원격 업로드하지 않았다. 사용자 업로드 후 실제 파일 해시를 확인해야 한다. 문서 갱신만으로 main/runtime 기준/release를 승격하지 않는다.

## 원격 기준 기록

- 저장소: `0-FLANDRE-0/Aegis_Project`
- 작업 branch: `WIP14`
- 분기 기준 main commit: `a8d14e3484200098be2143e0547c8e922642c042`
- 분기 기준 tree: `92caa0163006e916d98b422440deb80f5cd0d9eb`
- 기존 원격 기준 기록: `Aegis_SIM_v48_WIP13C22.html`

## B4 구현

사용자의 MR160km대/ER·SM-6 240km 이상 요청을 게임 설계·검증 목표로 반영했다. 실제 무장 성능값이 아니다.

- MR/ER/SM-6/ESSM별 SIM_TUNED 단계 프로필과 미사일 소유 `_loftB4` 상태.
- CLIMB → CRUISE → DIVE, 필요 시 중간 단계 생략, DIVE 이후 재로프트 금지.
- 기존 실제 유도 경로에 연결하고 국부 경로 control horizon과 실제 표적 PIP/TGO를 구분.
- B2 자체 항법 추정치를 사용. 물리좌표·추력·피해 강제 변경 없음.
- 단거리와 프로필 회랑보다 높은 표적은 기존 DIRECT 경로 보존. ESSM은 mild-loft, RAM은 B2 직접 유도/해면 회피 보존.
- 관제 게임 검토 범위 MR160/ER260/SM-6 260km. 기존 FCQ/권한/시선/SPG/NEZ/재고 게이트 보존.
- DEBUG의 읽기 전용 B4 단계/회랑/고도/잔여거리 표시.

## 확인된 거리 결과

명시적 합성 관측 트랙 fixture이며 초기 자연 탐색/ECM/회피 캠페인이 아니다. 초기 수평 분리거리와 실제 요격 위치의 함정 거리를 구분한다.

- MR160km: 고도2km/10km 고정 표적 요격.
- ER240/260km: 고도10km 고정 표적 요격. 260km 사례 실제 요격 위치는 함에서259.987km.
- SM-6 240km/고도10km 고정 표적: seed142000 미스,142001/142002 요격. 2/3은 통계적 Pk 또는 안정적 최대사거리 증명이 아니다.
- SM-6 초기260km/고도10km/접근250m/s 표적: 함에서215.230km 지점 요격. 260km 고정 표적 seed142000은 약259m 미스.
- ER240km/고도2km는 `NO_CHANNEL` 발사 거부; SM-6 같은 저고도/거리는 비행 후 미도달.
- ESSM25km/고도2km 고정 표적은 요격. 여러 중장거리 조건은 에너지 부족으로 실패.

36개 주 조건과2개 추가 조건의 성공/미스/거부를 모두 지원 evidence에 기록했다.

## 검증

단계33/33, B4런타임8/8, B3transport49/49, B3런타임25/25, 패키지52/52, B2nav38/38, VLS시간12/12, 발사정책22/22, 데스크톱/모바일 크기 조작2/2 PASS. 일부 하위 검사는 중복된다.

MR160 고정/ER260 고정/SM-6 초기260 접근 표적의 전체 단계 비행을1×/8×/16×/64× fixed-step 배치로 반복해 상태 이력 일치. B3 DL/GPS/지원 종료 불변, B2 VLS/ASM/RAM, 공력·추진·질량 동결 hash와 기존 셀 이탈·신관·피해 권위 보존. 압축 자산0~12 B3 byte-identical, B3→B4 재생성 exact.

## 잔여와 다음 확인

1. 기존 `V48 WIP13A surface target submergedBreachFloods` core 실패1건: B3/B4 모두 동일. 검사를 삭제하거나 침수 물리를 변경하지 않음.
2. Native file URL 관리자 정책 차단으로 전체 HTML set_content 실행. 빈 페이지에서도 WebGL context 실패. 실제 함체/연기/카메라 및 모바일 GPU/FPS 미검증. 3D FIRE handler 통과와 구분.
3. SM-6 고정 장거리 미스, ESSM 에너지 부족, 저고도 원거리 지원 한계와 미시험 회피/횡단/도주 조건.
4. 사용자 B4 HTML 원격 업로드 후 해시 대조 및 README/고정 지침/테스트·체크섬의 원격 산출물 정리.

## 보존한 이전 기록

- B3: `docs/wip14/B3/AEGIS_PLAN_STATUS_v48_WIP14B3.md`; HTML `c6a75f9f2c03e925ec298d0cb5885fa9b043c066aeb62117cf4674ec0c313123`,7,317,076 bytes. 범용 one-way/two-way DL, SM-6 첫 return/assistance profile, 독립 GPS 보정, deadline 불변.
- B2: `docs/wip14/B2/AEGIS_PLAN_STATUS_v48_WIP14B2.md`; HTML `0aefeadc27f5fc4cd34e076f31bd570eadb5f6fdc950bcf37dc07b5f6cb103da`. Generic own-nav/ASM/RAM, VLS기본0.8초 및0.6~1.0초 설정. 당시 core0 기록은 후속 seed142000 재검사에서 기존 실패1건이 확인된 한정사항과 함께 읽는다.
- B1: `docs/wip14/B1/`; HTML `7c26f0e86b9ae5e7f6ce17506dbfc891b656aedcf413d30ecdf5fb3337964d45`. 원래 report/evidence/checksum과 own-nav coverage audit 보존.

단계 순서는 `docs/wip14/WIP14_GUIDANCE_DATALINK_LOFT_PLAN.md`의 B2→B3→B4를 따른다. 최신 B4 거리 시험 목표와 결과는 B4 상태 문서를 함께 읽는다. 예전 B3 흡수/SM-6-only 문구를 최신 계획으로 사용하지 않는다.

main/PR/merge/release/tag, 원격 runtime HTML, VLS loadout, AIM-174B 운용 등록은 변경하지 않았다.
