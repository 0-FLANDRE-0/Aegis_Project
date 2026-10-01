# AEGIS v48 WIP14B3 작업 상태

작성: 2026-10-01 KST

**B3 구현·전용 검증 통과 / 기존 core 실패 1건 및 WebGL 시각 검증 잔여 / 전체 CLOSED 아님.**

- 기준 B2 SHA-256: `0aefeadc27f5fc4cd34e076f31bd570eadb5f6fdc950bcf37dc07b5f6cb103da`
- 결과 HTML: `Aegis_SIM_v48_WIP14B3.html`
- 크기: 7,317,076 bytes
- SHA-256: `c6a75f9f2c03e925ec298d0cb5885fa9b043c066aeb62117cf4674ec0c313123`
- decoded main SHA-256: `e15323d58d82af8c707b0ef4b7b24b1e2aaade82a39a2def3d73b7a3127dd71b`

범용 uplink/return queue, 방향별 지연·손실·순서·TTL, 불변 launch support deadline, profile-bounded PIP/TGO advisory를 구현했다. SM-6가 첫 양방향/assistance 활성 profile이며 SM-6 전용 core 분기는 없다. 기존 GPS/INU 자체 항법은 유지했다. GPS는 자기 INS 오차만 보정하며 return은 onboard 추정치만 반환한다.

Transport 49/49, packaged-browser runtime 25/25, package/static 41/41, B2 unit 38/38, VLS timing 12/12, release policy 22/22, desktop/mobile UI handler 2/2 PASS. Transparent-link 4종 비교는 위치·속도 1e-6 SI 허용오차 안에서 B2와 일치했고, ASM/RAM 항법·RAM 분리 비행은 exact다. B4 loft/공력/추진/질량/VLS loadout은 변경하지 않았다.

기존 `submergedBreachFloods` 자기검사는 seed 142000의 clean boot에서 B2와 B3 모두 실패한다. 과거 B2의 core 0 기록을 이 조건에서 재현하지 못했다. 해당 실패를 삭제하지 않았고, 침수계산은 수정하지 않았다. Native file URL은 administrator 정책으로 차단되며 빈 페이지에서도 WebGL context 생성 실패가 재현되었다. HTML은 set_content로 실행했으며 3D FIRE handler PASS와 WebGL 시각 PASS를 구분한다.

자세한 증거는 대화에 전달한 `AEGIS_v48_WIP14B3_SUPPORT.zip`의 report, validation summary, evidence, 재생성 도구 및 테스트에 포함한다. 대형 HTML 원격 업로드 및 main 승격과는 별개다. 다음 기능 단계는 B4이며 전체 종료에는 위 두 검증 잔여를 처리해야 한다.
