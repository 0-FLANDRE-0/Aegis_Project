# MAP_E 재현

보고서 ZIP은 결과 열람용이다. 시험 재실행은 같은 산출물 커밋의 저장소 전체와 공용 의존성을 준비한다.

기준 `main 7b9ca6e3e2d2dd26406b93c395d376f7f1b30c06`, MAP_D HTML SHA `5be55bdc1390d79f7b74bbfa5f128af916ffecdcf28693d0524578646955f40f`. Python/Playwright+Chromium, Node+Acorn 필요. 저장소의 기존 browser backend/fixture를 재사용한다. 이 환경은 `TMPDIR=/dev/shm`, `PYTHONDONTWRITEBYTECODE=1`, Chromium `/usr/bin/chromium`을 사용했다. Acorn이 일반 node_modules에 없으면 설치 경로를 NODE_PATH로 지정한다.

```sh
node docs/map/E/extract_functions.cjs
python docs/map/E/build.py
node docs/map/E/static_verify.cjs
python docs/map/E/run_domain.py
python docs/map/E/run_final_native.py
python docs/map/E/run_final_ui.py
python docs/map/E/run_d_tests.py
python docs/map/E/verify_ew_h3.py
python docs/map/E/verify_e_policy.py
MAP_E_NATIVE_ONLY=1 python docs/map/E/verify_e.py
MAP_E_UI_ONLY=1 flock /tmp/aegis-map-e/gpu.lock python docs/map/E/verify_e.py
python docs/map/E/acceptance.py
```

- 실제 WebGL 검사는 같은 gpu.lock으로 순차 실행한다. 게임 계수나 테스트 판정은 바꾸지 않는다.
- `legacy_test_adapter.py`는 기존 ARM 리스너를 test-only 준비로 호출한다. 제거한 DOM을 다시 넣지 않는다. 새 E 검수에는 설치하지 않는다.
- `TEST_MIGRATIONS.md`에 UI 준비·오래된 H3 스키마 기대값 이관을 기록했다.
- 표시 폭 보정 전에 끝난 native 증거는 원래 실행 SHA를 유지한다. `presentation_equivalence.cjs`는 저장된 prior-presentation.js로 이전 main 소스를 재구성해 해시를 확인하고, **MAP_E_UI 블록 밖 전체 코드 byte 동일**을 검증한다. 원본 임시 HTML이 없어도 재현 가능하다. 최종 UI 검수는 최종 HTML에서 실행했다.
- 신규 E 결과는 `e-new/native-results.json`(10개 단계 검사+오류 검사), `e-new/results.json`(8개 UI 조합), `e-policy/policy.json`에 나뉜다.
- 비교/회귀 파일은 실제 실행한 제품 SHA를 기록한다. 결과의 SHA를 최종 제품 SHA로 덮어쓰지 않는다.
- `package.py`는 HTML ZIP과 보고서 ZIP을 따로 만들며, `readback.py <artifact-commit>`은 GitHub 원격 bytes/ZIP CRC/내부 HTML을 확인한다.
