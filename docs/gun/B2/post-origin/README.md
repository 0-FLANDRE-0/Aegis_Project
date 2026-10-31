# 원점 복구 후 60회 재진단

[Phase1 착수 보고](../PHASE1_START.md), [시험 규약](PROTOCOL.md),
[전후 통계](evidence/summary.json), [그림](plots/comparison.svg).

제품은 AIR_ORIGIN_A 그대로다. 새 B2 기능은 아직 넣지 않았다.
과거 C9 도구·Phase0 2,400회 결과는 보존하고 같은 입력 60개를 비교했다.
DDG90 seed419023의 실제 자함 피해 악화 1건도 공개한다. 검수 pass는
진단 완전성/동등성에 대한 값이며 모든 전투 결과가 개선됐다는 뜻이 아니다.

전체 저장소, Python Playwright/Chromium, Node/Acorn, Matplotlib이 필요하다.
기존 자료를 보존하려면 별도 checkout에서 재현한다. TMPDIR=/dev/shm,
PYTHONDONTWRITEBYTECODE=1, MPLCONFIGDIR의 쓰기 가능한 경로를 사용했다.

```sh
NODE_PATH=/path/to/node_modules node docs/gun/B2/post-origin/static.cjs
python docs/gun/B2/post-origin/run_matrix.py
python docs/gun/B2/post-origin/verify_equivalence.py
python docs/gun/B2/post-origin/triage_adverse.py
python docs/gun/B2/post-origin/analyze.py
python docs/gun/B2/post-origin/plot.py
python docs/gun/B2/post-origin/report.py
python docs/gun/B2/post-origin/package.py
```

run_matrix는 2개 독립 브라우저 프로세스로 60회를 실행한다. 각 회차는 새 문맥이다.
원래 Phase0 builder는 바꾸지 않고 입력 파일/해시 줄만 메모리에서 바꿨다.
runtime 함수 해시와 native 4조건/90° 반복 2조건으로 같은 실제 게임 경로를 검증한다.
추가 악화 native 2회는 피해 RNG를 한 번 더 뽑지 않고 생성된 값을 읽기만 한다.
현재·과거 측정 결과와 각각 정확히 같아 로깅 부작용이 없음을 확인했다.

초기 HTML 보존 검사에서는 재귀 glob이 과거 보고서 INDEX.html을 게임으로
오인했다. 실제 제품 root HTML/checksum 검사로 대상을 명확히 하고 초기 실패
요약을 evidence/development에 남겼다. 회차·게임·허용 오차 변경은 없다.

REPORT.html을 열면 도표와 보고서를 볼 수 있다. 게임 HTML은 ZIP에 포함하지 않는다.
원격 readback 영수증은 산출물 커밋 뒤 별도 커밋에 둔다.
