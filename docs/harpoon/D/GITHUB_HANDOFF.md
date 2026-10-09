# Harpoon D GitHub 인계

대상 repo `0-FLANDRE-0/Aegis_Project`, 준비 branch `harpoon-block1c-a`, main/branch head `f51247496725aa8aadad69d5c8d3449c5bbc3a81`. 2026-10-04 API로 branch와 admin/push/pull 권한을 확인했다. 아직 새 HTML/support/PR/CI/병합은 실행하지 않았다.

사용자 업로드 파일은 루트 `Aegis_SIM_v48_WIP_HARPOON_D.html` 하나다.

- 크기 15,283,086 bytes.
- SHA-256 `e92aff9c19a074aa98c3ceca236abaa14b2a674f8417419df7a08dbc248700a1`.
- main SHA `aeaf6981dc163f3ae3ed67884830bfffb4df50eab83adb381edceda73039e683`.
- 직접 67/67 검사 PASS, 상세 scope는 README/evidence다.

업로드 뒤 remote bytes/SHA와 commit 부모·branch 기준을 확인한다. 사용자가 올린 큰 D HTML을 재업로드하지 않고, 작은 지원·상태·체크섬·README·지침·workflow를 `REPOSITORY_SUPPORT.sha256`에 맞춰 반영한다. K는 이미 존재하는 Git blob을 archive로 이동하고 A/B/C 큰 로컬 archive HTML은 API/Git 신규 업로드하지 않는다. 비교 C는 K → A → B → C 작은 authoring modules로 pinned SHA에 exact 재생성한다.

현재 workflow는 `.github/workflows/harpoon-d.yml`이다. 과거 C workflow/manifest는 역사 근거이며 현재 D 검사 대상으로 재사용하지 않는다. static과 selection/clock/native Actions를 동일 D SHA로 실행하고 결과를 확인한 뒤 요청된 PR/병합을 진행한다. ZIP에는 D+기존 K 큰 HTML과 필요한 작은 지원/역사 상태만 포함한다.

후속 장거리 검증은 docs/harpoon/long-range/D/REPORT.md·최신 status를 따른다. HTML SHA/bytes는 동일하고 장거리 gate 차단/최대거리 moving miss는 알려진 미수정 항목이다. 기존67/67은 자동 관 선택 회귀이며 장거리 전체 PASS로 바꾸지 않는다. 별도 지원 ZIP의 최신 작은 문서/근거를 D support manifest와 함께 사용한다. 원격 Actions는 아직 실행하지 않았다.
