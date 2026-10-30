# MAP_D 구현 전 확인

- 기준 main `9f8e77f96a39cafe017728a0734bc8dd0102a4f6` / MAP_C SHA `84fa5df960772cdb9c9904310ca7af752e3cedae025fd864dc1b27a9de6f8d7b` 확인. 별도 map-d, 지정 noreply 이메일 사용. CREDITS.md 보존.
- 하푼 자동 관문/경로 관문에는 발사 쓰기가 없지만 shipGameFrameV1의 공유 WeakMap 프레임 캐시가 갱신될 수 있다. 원본 gate 함수 본문을 추출하여 관측 트랙/발사기 사본과 private 프레임으로 실행한다. 기존 readiness도 같은 관측 Map에 묶어 BDA/support 조건이 빠지지 않게 한다. 요청·발사·UI 갱신 함수는 미리보기에서 호출하지 않는다.
- CG 각 gunMount 런타임은 spec/installation/command/requestFire/startContinuousFire/stopContinuousFire/clear/snapshot을 독립 제공한다. selectedGunId/mainGun 포인터는 건드리지 않는다. 각 command 결과와 native bunkerGunClearance를 사용한다.
- 공통 MAP_A.currentTool은 harpoonRouteEditingE()가 참이면 HARPOON_INS가 NAV보다 우선이다. 기존 AIM 버튼과 harpoonRouteToggleE를 명시적 입력에서 호출한다. 2D/PiP 모두 기존 탭 라우팅·간격/개수 규칙·제어 전환 금지를 그대로 쓴다.
- CUE 해제 API clear(), 단발 보류 취소 cancelPendingSingleFire(), 연속 중지 stopContinuousFire()가 있다. 표적/무장 해제에서 지도 명령에 속하는 CUE/사격 동의만 이 API로 정리한다.
- DDG에는 하푼 설치가 없다. 프로파일/인벤토리 변경 없이 RGM-84 칸 부재를 검증하고, 실제 하푼 시험은 CG로 한다.
- 기존 harpoonGateA는 options.mode/automatic을 검사한다. 새 지도 경로는 현재 engagementControlMode를 명시하여 AUTO/SEMIAUTO 거부가 적용되게 한다. 기존 ARM 버튼과 H3 attackH3 경로는 바꾸지 않는다. 수동 MANUAL 중에는 원래 tacticalActiveH1/H3가 비활성이며, 편집 중 H3의 MANUAL_HARPOON_ROUTE_PRIORITY는 그대로 유지된다.
- 하푼/함포 발사는 지도 입력이 만든 큐를 fixed tick에서만 디스패치한다. 탄종 선택과 CUE는 명시적 사용자 입력에서 기존 공개 API를 직접 호출한다. 표시 갱신/그리기에서는 이 명령을 호출하지 않는다.
