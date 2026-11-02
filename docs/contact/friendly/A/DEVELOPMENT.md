# 시험 준비·재시도 기록

제품 코드를 테스트 결과에 맞춰 조정한 기록은 없다. 아래는 시험 도구/환경 문제이며 합격으로 계산하지 않는다.

1. 최초 Harpoon 재현 도구가 존재하지 않는 `harpoonFireA` 함수를 호출했고, 경로 API 인자 형식을 잘못 사용했다. 공개 진단 포트 `__HARPOON_DIAG_A__.routeAdd({x,y})` 및 `fire()`로 수정해 그 사례를 다시 실행했다. 이 API는 m를 world로 변환한다. 헬기 기존 결과 2개는 보존했다. 초기 before-execution.json의 시간은 마지막 Harpoon 단독 재실행 시간이며, 세 사례 총시간으로 해석하지 않는다.
2. 최초 도메인 실행은 sparse checkout에서 빠진 과거 HELI_CG_A HTML을 요구해 실패했다. 필요한 과거 파일을 체크아웃했다. 또한 MAP_E의 이미 제거된 DOM을 직접 요구하므로 기존 retired-node 어댑터와 B2 설정을 적용해 다시 실행했다. 초기 lane은 중단하고 `evidence/domain/`에 보존했다.
3. 어댑터를 적용한 뒤에도 과거 EMCON UI 시험은 제거된 `#lockBtn`의 bounding box를 요구한다. 이 단언을 몰래 바꾸지 않았다. 현재 UI 시험 및 native EMCON 시험과 구분한다.
4. 동시 대형 Chromium 시험 중 helicopter-flight와 harpoon-f1에서 Target crashed가 발생했다. cgroup 메모리 로그에 OOM/kill이 기록돼 있었다. 런타임 제품 오류로 단정하거나 합격으로 바꾸지 않는다. 원시 실패 로그를 유지한다.
5. isolated.py의 첫 실행은 다른 진단 모듈이 sys.path 앞에 둔 `build.py`를 가져와 ImportError였다. 파일 절대경로로 고유 모듈명을 사용해 해결하고 두 성분 시험을 재실행했다.
6. 첫 AUTO IFF 시험의 inventory 비교는 VLS의 가동 타이머까지 비교해 false였다. 탄약 비교 대상을 셀 type/essmCount 및 CIWS ammo로 제한했다. 중간 count 필드는 실제 ESSM 재고명이 아니므로 essmCount로 바로잡았다. 중간 도구 실행은 중단하고 최종 도구로 재실행했다. 제품이나 발사 관문은 수정하지 않았다.
7. 계약 시험의 ENV_D status는 비동기다. 최초 도구의 fallback true를 제거하고 실제 status를 await한 결과 match=true, changedNativeFunctions=[]를 확인했다.
8. 진행 중 말한 하푼 24회는 새 파일 요청/거부까지 포함한 기록 수였다. 최종 분석에서는 성공한 신규 생성만 집계한다: **기존 22개 → 후보 2개**, 마지막 잔존 11개 → 1개. 실패한 업데이트는 신규 생성으로 세지 않는다.
9. UI 213 첫 실행에는 기존 PIP_B의 headless CPU Canvas2D 백엔드가 적용되지 않았다. 진행 로그를 보존한 채 중단하고, 기존 browser_backend.install()을 적용해 원래 단언을 다시 실행했다. 실제 WebGL은 계속 사용한다. UI 213은 재실행 결과만 최종 판정에 사용한다.
10. 두 함정의 paired baseline에서는 습격 시 observer 정확 상태 비교 2개가 달라졌다. 실제 물리 상태·전역 RNG·탄약·피해·표적 상태 비교는 같다. 새 연관/고도 제약 경로 때문에 관측 수·분류·공분산·스케줄러가 달라지는 내역을 analysis/paired-observer-delta.json에 기록했다. 이 차이의 기대값은 승인 없이 갱신하지 않았다.

현재 제출 증거는 위 도구 수정 후 실제 실행 결과다. 제출 제품 HTML의 SHA는 BUILD.json에 고정돼 있다. 도구 수정으로 제품 HTML을 다시 패치하지 않았다.
