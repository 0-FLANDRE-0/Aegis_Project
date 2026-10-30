# F 직접 실행 환경과 경계

최종 HTML 15,638,513 bytes / SHA `438c4ea21c7c762243728092dcee269d12334af4c8265163300eb9b9b03f29d7`, decoded main `cbed31af60addb8a757225251783df462336c449730975d1a5d836fc7c487b16`. seed `1831565813`. 실제 Python Playwright·시스템 Chromium에서 원본 bytes를 오프라인 route로 제공했다. CPU 고정 tick 시험과 SwiftShader native RAF/WebGL을 구별한다. 여러 suite가 이 호스트에서 동시에 실행되어 wall-clock 측정에는 경쟁 부하가 있다.

최종 직접 실행 593/593 확인 항목 PASS, page errors0, core self-test failures0. count는 suite별 `checks`이며 시나리오 수나 격추 수가 아니다. 이전 버전·중간 candidate 결과는 합산하지 않는다.

세 척 clock: 두 혼합 함종 편성 ×1/8/16/64 ×1536 full ticks(25.6 simulated seconds). 실제 accumulator, enemy AUTO 실발사·피해 fixture와 receiver/weapon/defense/physics/world clock 및 난수 signature를 비교했다. 모든 배속의 상태/RNG exact. 원본60/120/20Hz 주기를 낮추지 않았다. CPU 소요는 `clock-three-ships.json.gz`의 case별 elapsedMs·profiler를 따른다. 단일 측정으로 speedup/FPS를 주장하지 않는다.

native: 아군·적군의 함수파/항적 mesh5개·독립 history·shared wave shader와 reset 효과 폐기 및 원본 RAF의 세 ship model(자함1+외함2), profile별 VLS/SPG/SeaRAM 여부·아군 focus·실제 관통 ENTRY/EXIT 구멍·지속 draw·import/reset root 폐기를 두 편성에서 검사했다. damage job을 강제로 끝내거나 렌더러에서 물리를 진행하지 않았다. SwiftShader는 소프트웨어 렌더링이며 실제 사용자의 휴대폰 성능 결과가 아니다.

원본 E 대비 ownship: idle/damaged 물리는 같고, ESM RNG를 분리한 F는 old shared RNG를 이어 쓰지 않는다. raid의 양쪽 HP100/침수0·동일 고정 layout/CIWS 재고이며 CG loaded VLS는 E115/F116. 이를 의도된 RNG epoch delta로 기록한다. raid dynamics/발사 시각 old-version exact와 기존 E660건 전체 재실행을 주장하지 않는다. F 내부 결정성은 위 clock 증거다.

`verify_natural`은 실제 Kh-35U 방사/외함 레이더 관측·AUTO soft-kill와 실제 시커 J/N/coherent capture 증거다. manual/권한·IFF fixture는 synthetic measured-state 입력임을 구별한다. 지형 bypass를 사용하는 전투 fixture와 실제 배치 terrain/overlap 검사도 구별한다. 실전 검출률·요격률·전자전 성공률·전 해역 배치·장거리 신규 함정전 인증은 범위 밖이다.
