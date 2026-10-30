# 최적화 1단계 PERF_A

기준은 H4A final `b97925cb5fb27d4dad26d62db78520641ee70857`이다. 새 원본은 `Aegis_SIM_v48_WIP_PERF_A.html`이며, 직전 HTML/status/SHA/workflow는 `archive/v48/WIP_MULTI_SHIP_H4A/`에 같은 bytes/blob으로 보존한다.

이번 단계는 세 경로만 바꾼다.

1. 외부 함정의 `shipSystemDamageB`가 불변 등록 hitbox를 system별 고유 module name 색인으로 조회한다. 실제 손상 값은 호출할 때마다 해당 owner의 현재 flooding에서 읽는다. active player 경로는 기존 함수 그대로이며, 가변 geometry에는 기존 scan을 사용한다. geometry 교체·함종별 배열·owner별 피해를 혼합하지 않는다.
2. 기존 EW의 IJ 대역 조건을 요청/전력 배분 검사 뒤, pod 위치·건강·사각 계산 앞으로 옮긴다. 지원 대역의 출력·LOS·빔·ERP·손상·EMCON 계산은 그대로다.
3. 동일 Kh-32의 기존 2048×2048 도색을 view/THREE context와 실제 도색 입력별로 공유한다. 재질·geometry·plume은 미사일마다 유지한다. body geometry가 소유하는 idempotent lease를 해제하고 마지막 lease에서만 texture를 dispose한다. 마지막 제거 이후 새 모델은 새 texture를 만든다.

캐시는 파생 데이터이며 snapshot에 저장하지 않는다. 고정 물리60Hz·침수/힘120Hz·정수압20Hz, 시뮬레이션 RNG, RF/search/CMS 분류, AI·발사 권한, Harpoon INS/ARH/DL0, 탄도·충돌·피해·채프/눌카·CG Phalanx-only·DDG 장비를 변경하지 않는다. 플레이 조작도 기존과 같다.

도감은 기존 설계대로 닫은 뒤에도 현재 모델 하나를 보관한다. 이 참조가 남아 있으면 texture를 유지하며, 다른 모델 선택 또는 `disposeCurrent`에서 해제한다. 실전 미사일·MAIN 잔해·도감이 같은 도색을 사용할 때도 한 경로의 제거가 다른 경로의 도색을 폐기하지 않는다.

`cache.js`, 정확한 원본 함수 offset/SHA를 가진 `patch-index.json`, 결정적 `build.py`로 변경 범위를 재현한다. `verify_static.py`는 packed records/assets, 전체 문법/scope와 정확한 rebuild를 검사한다. `verify_semantics.py`는 EW 72조건과 실제 양 함종 selftest, `verify_resources.py`는 WebGL에서 도색 픽셀/geometry parity·64모델 공유·부분/전체 제거·import/reset·도감 수명을 확인한다. 기존 H4A 26 browser suites도 새 원본에 직접 실행한다.

실행 예시는 `GITHUB_HANDOFF.md`를 따른다. 최종 검사 수와 원본별 SHA는 `evidence/verification-summary.json`, 별도 직렬 성능 비교는 `PERFORMANCE.md`와 `evidence/benchmark.json`을 따른다. Actions 계정 제한으로 수동 workflow만 준비하며 CI PASS를 주장하지 않는다.
