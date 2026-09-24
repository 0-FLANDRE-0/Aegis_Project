# WIP13C6 Manual HTML Upload

브랜치: `feat/v48-wip13c6-surface-guidance-essm-arh`

대형 HTML은 사용자 수동 업로드 대상으로 유지한다.

## 업로드 대상

- 파일명: `Aegis_SIM_v48_WIP13C6.html`
- SHA-256: `50c41eff6e1e35b809786073353f880ac63673f05ce9c18012f03cccad78cede`
- 기준: `Aegis_SIM_v48_WIP13C5.html`
- 기준 SHA-256: `8d461aa383950729fd8a2f81963fd70e3f8bb323ed40d7ebea7a00a421bd96d7`

## 수동 업로드 후 확인

1. 위 브랜치 루트에 정확한 파일명으로 업로드한다.
2. 업로드 직후 원격 파일 SHA-256과 위 값을 대조한다.
3. `tests/surface-missile-wip13c6-guidance-regression.cjs`를 실행한다.
4. Actions와 사용자 실제 브라우저 임의방위 발사 확인 전에는 `main`에 병합하지 않는다.

브라우저 실플레이에서 우선 확인할 항목:

- SM-2가 VLS 이탈 후 표적함 방위로 pitch-over하는지
- SM-2가 seeker track을 가진 상태에서 좌우 hunting 후 해면에 박히는 현상이 줄었는지
- ESSM 수상표적 발사가 공중 FCQ 이유로 부당하게 차단되지 않는지
- ESSM ARH가 표적함을 통과하지 않고 실제 hull contact 또는 물리적 miss/sea impact로 끝나는지
- 명중 시 WIP12F 파괴구/화재/침수 damage가 1회만 적용되는지
