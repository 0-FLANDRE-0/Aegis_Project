# v48 WIP MULTI SHIP F — 배치 분리·receiver 전자전·함정 해상효과

- 기준: E head `bdcf8d1724a72587f9d42e4b1cf70ba4cbe57ef6`, HTML SHA `d1aa4b1876bea2739aec17f6f2c4e421e5ecef9957aa28113fab14d4117d0af2`.
- 최종 HTML: `Aegis_SIM_v48_WIP_MULTI_SHIP_F.html`, **15,638,513 bytes**, SHA `438c4ea21c7c762243728092dcee269d12334af4c8265163300eb9b9b03f29d7`.
- decoded main: `cbed31af60addb8a757225251783df462336c449730975d1a5d836fc7c487b16`. 변경 packed record13, assets0~12·모델·원본 profile 및 stable v48 보존.
- 판정: 이번 배치 분리와 전자전 범위 **완료**. 직접 정적·런타임·실제 브라우저/3D 검증 **593/593 PASS**, page errors0/core failures0. GitHub Actions는 사용자 사용 불가 조건에 따라 마감 gate가 아니다. 원격 상태는 F PR과 `docs/multiship/F/evidence/remote-publication.json`을 따른다.

## 완료 범위

1. 출항 전 시험 표적함·아군·적군·각 초기 레이더 EMCON·항공기 ON/OFF 독립 선택/동기화. 아군 근처 배치와 seed 기반 적10~30km 해상 배치·지형/중첩 회피. role/faction은 시나리오 소유이며 CIC 적성·좌표 truth를 주입하지 않는다.
2. 세 함정의 원래 항해·침수·피해·승조원·무장·방어 AUTO를 독립 owner로 실행. 일반3D 버튼은 아군 focus. 실제 피격 후 draw 지속 및 import/reset의 동일ID 모델 재생성 검증.
3. receiver별 익명 ESM 방위/오차/세기/대역·12초 coast/expire·cap96. 자함 CIC는 자기 측정만 표시하고 거리 미확정·UNKNOWN 유지. 실제 RF 방사·대역·수신빔·기상/지평선/지형·건강도를 적용한다.
4. 기존47개 soft-kill/SLQ-32 커널을 owner closure에서 재사용. noise/replay 자원 배분·실제 시커 capture/pull/HOJ 및 radar 측정 잡음/바이어스. 기본 외함 EW AUTO는 observed threat 없으면 STANDBY. 실제 좌표·사각·owner 재고로 Nulka/SRBOC 발사·재장전·질량 변화. CG RAM0 보존.
5. 인증 IFF의 측정 응답을 기존 fresh SURFACE 파일에 연관하여 FRIEND/WITHHELD 보호. 새 트랙/아군 네트워크/CEC를 만들지 않는다.
6. strict F 배치/fleet·EW·soft-kill 재고 preflight 및 invalid import zero mutation. A_1/E_1/B legacy 명시 변환. 정상 복원에는 설정/재고만 이어가고 센서/ESM/비행/기법 timeline은 deferred transient.

7. 자함의 기존 wave shader/항적 커널을 보존하고 아군·적군의 함수파/선미 포말/항적에 해당 함종 수선면을 적용. 독립 bounded world history·floating origin·재시작/import 폐기 및 실제 moving foam/draw 검증.

## 직접 검증과 한계

12 suite의 최종 SHA별 집계·입력·trace는 `docs/multiship/F/evidence/verification-summary.json`과 압축 원본 report다. 두 함종 실제 Kh-35U 접근에서 자기 radar/ESM 기반 AUTO 눌카/SRBOC·재밍·시커 J/N/coherent capture, 세 척1/8/16/64×1536 full ticks exact, desktop/mobile UI·원본 native RAF 피격/복원을 확인했다. E 방어 승인/차단/BDA와 D manual 무장·Harpoon INS/ARH/waypoint/DL0·실제 no-DL 표시도 최종 F에서 재검사했다.

- DDG에는 별도 EW 안테나 registry가 없어서 기존 RF 기준점+CDC/발전기/offline 가용성으로 유지한다. CG는 등록된 양현 SLQ-32 위치·손상을 사용한다. DDG 실제 안테나 위치/개별 피해는 후속 등록이다.
- 전력·감도·ECCM·replay·IFF 오차 등은 SIM-TUNE. native SwiftShader는 실제 모바일 FPS가 아니다. S-band SPY에 기존 I/J/X 재밍을 강제 적용하지 않는다.
- ESM RNG 격리로 E와 같은 seed의 raid 순서/재고가 old-version exact는 아니다. 이번 비교는 HP/침수·layout/CIWS 동일, CG VLS1셀 delta를 남겼다. F 내 배속/RNG exact는 통과했다.
- IFF 보호 표식의 정교한 재인증/운용자 해제, 아군 링크/정정/EMCON·방어 분담·합동교전, 기동/공격 전술 AI와 헬기는 다음 단계다. 추후 토마호크 대상은 RGM-109E Block Va다.

## 반영

E HTML/status/SHA/workflow는 same bytes로 `archive/v48/WIP_MULTI_SHIP_E/`에 보존한다. F HTML/status/SHA·README/지침·support/evidence·수동 workflow를 함께 반영한다. `multiship-ew-f`를 E 위에 직접 업로드/readback하며 main/선행 PR을 임의 병합하지 않는다. 새 기능은 F에서 이어간다.
