# ENV_D 재측정 A

기준 HTML: `Aegis_SIM_v48_WIP_NEAR_VERTICAL_PATH_FIX_A.html` (`38a4f97527b48027fa64f0673cea14a9c83c116d`).
출력: `Aegis_SIM_v48_WIP_ENV_D_REMEASURE_A.html`.

최신 제품에서 함수 원문을 추출한다. 관측은 ENV_D의 이상 조건, 표적은 native ASM 엔티티의 직선 등속 운동이다. native VLS → SAM 비행/유도/신관 → Pk/피해 → ASM 손상 prefix 순서를 보존한다. 비행/피해 계수 변경은 없다.

Node 24, Python 3.12, Acorn 8, Playwright/Chromium 사용. 저장소 루트에서 실행한다. `NODE_PATH`는 설치한 Acorn/eslint-scope의 node_modules 경로로 지정한다. 브라우저 임시 디렉터리는 `TMPDIR=/dev/shm`을 사용했다.

```bash
node docs/envelope/D2/prepare.cjs
python docs/envelope/D2/capture.py
node docs/envelope/D2/export_path.cjs
python docs/envelope/D2/verify_path.py
node docs/envelope/D2/pilot.cjs
# COST_ESTIMATE.json의 6시간 기준 확인 후 전수 실행
node docs/envelope/D2/suite.cjs --execute-full
node docs/envelope/D2/finish_measurement.cjs
python docs/envelope/D2/build.py
python docs/envelope/D2/verify_delivery.py
python docs/envelope/D2/report.py
python docs/envelope/D2/verify_results.py
python docs/envelope/D2/package.py
```

전수는 1회만 실행한다. suite는 완성된 칸의 gzip 결과를 재사용해 중단 시 재개한다. 다른 코드/설정으로 재개하면 안 된다. 후속 재시험은 경계와 고정 무작위30개 궤적뿐이다. 원래 ENV_D와 같은 156개 궤적 슬롯(기존120 + 횡단36)을 유지한다. 사거리 밖 슬롯은 도달 불가로 표기한다.

`results/cells/*.json.gz`가 5시드별 원시 사격 결과다. `ENV_D_BEFORE_AFTER.csv`는 과거 ENV_D와 최신 결과를 비교한다. 과거 ENV_C는 항공기 점 표적·이전 유도 코드이며 HISTORICAL로만 제공한다.

새 HTML은 역사적 ENV_D 데이터/API 블록만 교체한다. 저장 스키마·시뮬레이션 함수·지도·발사 관문·AI는 바뀌지 않는다. `__ENV_D__.status()`는 함수·모델·설정 fingerprint를 확인한다. 자동 측정은 시작하지 않는다.

최종 판정은 `evidence/verification.json`, `evidence/delivery.json`에 있다. `*-initial-*` 로그와 `pipeline-initial.log`는 초기 포장 단계의 문법/직렬화 불일치를 보존한 기록이며 최종 판정이 아니다. 링크 포트의 함수 멤버가 Playwright에서 null로 전달되는 것과 JSON에서 생략되는 차이만 fingerprint에서 정규화했다. 측정 입력·비행 함수·183,370발 결과는 그대로 보존했다. 최초 비용 예상과 실측 차이는 `ACTUAL_COST.json`에 기록했다.
