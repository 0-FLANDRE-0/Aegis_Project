# 재현과 결과 파일 선택

기준 `reg-k-env-d@058273c1f4b91c0d0c595e5399aaa967aa443f1c`, 별도 `fuze-zem-a`. 실행 HTML은 `Aegis_SIM_v48_WIP_FUZE_ZEM_A.html` (DZT)이다. 원본 ENV_D 전달 7파일은 `archive/v48/WIP_ENV_D/`에 byte/blob 동일 보존했다. main과 원본 브랜치는 병합하지 않는다.

Node 24 + acorn, Python 3.12 + Playwright/Chromium + matplotlib 환경에서 저장소 루트에서 실행한다. `NODE_PATH`는 acorn이 설치된 node_modules로 지정한다. 기존 `docs/performance/F/node_modules`가 있으면 재사용할 수 있다. 패키지 설치물·브라우저 바이너리·자격증명은 전달 ZIP에 넣지 않는다. 제한된 실행 환경에서 Chromium은 로컬 소켓 허용이 필요하다.

```
node docs/missile/fuze-zem/A/build_variants.cjs
node docs/missile/fuze-zem/A/test_core.cjs
node docs/missile/fuze-zem/A/test_deterministic.cjs
node docs/missile/fuze-zem/A/test_term.cjs
node docs/missile/fuze-zem/A/verify_clutter.cjs
node docs/missile/fuze-zem/A/verify_static.cjs
node docs/missile/fuze-zem/A/verify_repeat.cjs
node docs/missile/fuze-zem/A/run_revision.cjs
node docs/missile/fuze-zem/A/export_fixture.cjs
python docs/missile/fuze-zem/A/verify_equivalence.py
python docs/missile/fuze-zem/A/verify_browser.py
python docs/missile/fuze-zem/A/run_natural.py --variants T ZT DZT
python docs/missile/fuze-zem/A/run_release.py
```

빌드는 9개 A/B HTML을 `/tmp/aegis-fuze-zem/builds`에 만든다. 이는 실험용이며 게임 전달 ZIP에는 DZT 하나만 넣었다. API 기반 자동 최대사거리 측정은 호출하지 않는다. `run_limited`, `run_deterministic`, `run_revision` 모두 고정된 소규모 조건표일 뿐 이분 탐색/ENV_D 전수 측정이 아니다.

## 권위 있는 비교 데이터

| 파일 | 이번 보고서에서 사용하는 부분 |
|---|---|
| results/limited.json.gz | BASE / F / Z 각180발. T/FZT는 종료기 v1 과거 반복 기록 |
| results/deterministic.json.gz | D 180발. 안의 DZT는 종료기 v1 기록으로 최종 결과에 사용하지 않음 |
| results/revision3.json.gz | TERM_REVISION_3의 T / ZT / DZT 각180발; FAST680 80발; RESEARCH_LOG 16발 |
| results/natural-v1.json.gz | BASE28, F/D/Z 각16. 안의 T 관련 행은 v1 과거 자료 |
| results/natural.json.gz | 최종 종료기 T / ZT / DZT 각28발 |
| results/equivalence-details.json.gz | 최종 D/DZT 8조건, Chromium 실제 함수와 private의 전체 비교 |
| evidence/deterministic-replay.json | 최종 D/DZT 48조건 쌍 =96발, 전체 반환값 비트 동일 |
| evidence/release-BASE,DZT | 변경하지 않은 기존 정상/대체 지원/RF fault/배터리/정식VLS 입력 |
| evidence/observed-BASE,DZT | 자연 탐지→LOCK→VLS→전체 fixed tick, 각8발 모두 실제 WebGL |

**최종 A/B 표는 `AB_RESULTS.csv`와 `SUMMARY.json`**. 단순히 results 폴더의 같은 variant 행을 모두 합산하면 버전이 다른 T를 섞게 된다. `predeclared-*.json`에 각 실행의 코드 해시·조건이 있고 `history/`에 종료기 이전 반복 소스가 있다. 진단 로그의 truth는 사후 계측 전용이며 게임 제어로 역유입되지 않는다.

`engine.cjs`는 기존 ENV_D의 463-declaration native capsule을 읽고, live main에서 추출한 동일 함수 문자열과 새 helper를 적용한다. private의 ideal RF covariance는 0으로 명시했다. BASE는 기존 ENV_D 엔진과 물리 출력/궤적 동등성을 별도 확인했다. 순수 공중 진단에서 표면 충돌은 기존 fail-closed `ENV_AIR_ONLY_BOUNDARY`를 유지한다. 수상 proximity는 실제 브라우저의 원래 표면 파이프라인에서 별도로 검사했다.

built-in `ENVELOPE_TABLE_D` 120행은 **과거 ENV_D 결과**로 유지된다. `__ENV_D__.status()`는 후보에서 `match:false`, `recalculationRequired:true`를 반환해야 한다. 새 사거리표가 아니며 지도/발사 판정에 연결하지 않았다. 새로운 독립 진단의 소스·해시·동등성 증거는 이 폴더를 따른다.

## 결과/그림 재생성

```
MPLCONFIGDIR=/tmp/aegis-fz-mpl python docs/missile/fuze-zem/A/analyze.py
```

다른 출력 파일을 덮어쓰지 않도록 재시험은 별도 checkout에서 권장한다. 과거 v1/v2 종료기 결과는 최신 코드를 다시 실행해 일치한다고 주장하지 않는다. 최종 승인 비교는 위 권위 행만 사용한다.
