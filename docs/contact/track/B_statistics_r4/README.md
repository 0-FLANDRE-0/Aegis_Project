# TRACK-B R4 통계 전투 비교

최신 사용자 지시에 따른 추가 시험만 수행한다. 기존 B와 R4 ACTIVE 제품, 센서·무장·피해·AI 계수는 변경하지 않는다.

- 사전 계획: `PLAN.json`. 6발×20, 13발×10, 2발/3발/교차×각10 시드. 60쌍/120전투.
- 실행: `run.py --run --resume`. 제품/원본 runner/helper 해시 검증 후 매 전투 fresh Chromium. 동시2, 총3시간 hard watchdog.
- 종료: 모든 초기 ASM native 종말 또는 자함에서30km 이상·10초 연속 이탈, 이후5초. 이탈은 격추로 세지 않고 게임 객체를 강제로 제거하지 않는다. 자함 피격 후에도 실행한다.
- 유효 표본: `VALIDITY_RULE.md`. 정상 실행됐으나 탐지/발사가 없었던 전투도 실패 성능 자료로 포함한다. 실행 오류·누락·미종결은 승인을 막는다.
- 집계: `analyze.py`. 모든120 전투 종료 후에만 실행. 같은 시드를 공유한 시나리오를 묶는 seed-block 검정과 층별 paired bootstrap95% 구간. 게임 RNG와 별도 고정 분석 RNG.
- 주요 지표: 고유 초기 미사일 유출 수 및 실제 피해 callback 회차. 잔해 추가 피격은 후자에 포함하고 전자에 중복 합산하지 않는다. 침수는 각 전투의 사전 정의한 종료 시각 물량이며 시각 차이를 공개한다. HP는 참고용.
- 승인/중단: 사전 계획의 사용자 조건에 따른다. 명백한 악화면 원인 보고 후 중단하며 기대값·main을 변경하지 않는다. 조건 충족 시에만 paired6/D1 419012의 정확 기대값7개를 갱신하고 범위 분할·ACTIVE 승격·체인 PR 병합을 수행한다.

## 실행 재현

저장소 체크아웃과 기존 Python/Playwright/Chromium 의존성이 필요하다. HTML 자체는 단독 실행할 수 있지만 시험 도구가 단독 패키지라는 뜻은 아니다.

```sh
TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python docs/contact/track/B_statistics_r4/run.py --run --resume
PYTHONDONTWRITEBYTECODE=1 python docs/contact/track/B_statistics_r4/analyze.py
```

새 재현은 기존 raw를 덮어쓰지 않는 별도 작업사본에서 수행한다. `--resume`은 같은 입력의 완료된 원시 증거만 재사용한다. 현 실행의 절대3시간 예산은 `evidence/BUDGET.json`으로 고정되므로 재현 시 새 evidence 디렉터리가 필요하다. 원 전투는 추가 반복하지 않으며 불리한 정상 결과를 제외하지 않는다.

최종 결과는 `RESULTS.json`과 `REPORT.md`가 생성된 뒤 확인한다. 이전 R4 보고서는 통계 승인 이전의 보존 자료다. C55/SPQ AIR를 이 시험으로 ACTIVE 구현한 것으로 세지 않는다.
