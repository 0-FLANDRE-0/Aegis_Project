# ENV_B — 누적 ALL4_TERM 게임 내 비행 모델 재측정

이전 ENV_A를 덮어쓰지 않는다. 기존 `docs/envelope/A/`의 코드·표·원시 데이터·그래프는 당시 결과 그대로 보존한다. 이번 B는 최신 PIP_B 위 ALL4 B4 + 관측 기반 종료 + SM-6 게임 배터리 480초를 반영한 네이티브 함수에서 생성한다.

실제 무기 자료 입력이나 실물 성능 비교는 없다. 모든 표는 `GAME_ENGINE_COMPUTED`다. 정지·해면·수직 발사, 직선 등속 항공기 점표적, 지속적인 이상 유도 정보를 같은 경계에서 공급한다. 실제 게임 RF 조건의 승률이나 모든 거리에서의 요격 보장은 아니다. 비단조 성공 구간 때문에 이분 탐색 후 더 먼 모든 정수 km도 확인한다. 300km는 검사 상한이다.

새 종료기는 RF EKF도 읽으므로, 이번 이상 유도 경계는 잡음 없는 RF 추정 관측을 매 틱 제공한다. 종료기를 OFF로 하고 이 RF 기록을 넣은/넣지 않은 60궤적을 비교하여 기존 이상 유도 비행 결과가 같은지 검사한다. 전역 월드·RNG·틱은 사본 안으로 들어오지 않는다.

API는 기존 SYS 연결을 보존하기 위해 `window.__ENV_A__`를 유지하고 `window.__ENV_B__` 별칭을 제공한다. `run()`은 명시적 요청으로만 실행한다. 시작 시 자동 진단은 없다. `status()`는 네이티브 함수 해시, 프로파일·설정, 진단 경계 해시를 비교하고 다르면 '재계산 필요'를 반환한다.

```bash
node docs/envelope/B/run.cjs /tmp/env-b-results.json
MPLCONFIGDIR=/tmp/aegis-mpl python docs/envelope/B/report.py /tmp/env-b-results.json /tmp/env-b-report
python docs/envelope/B/generate.py
python docs/missile/termination/A/build.py
```

네이티브 소스/모델이 바뀌면 먼저 `extract.cjs`, `generate.py`, `verify_browser.py`로 현재 코드를 다시 캡처해야 한다. `inputs.json`의 detached 데이터와 원본 함수 해시는 이번 계산의 정확한 입력이다. 표는 새 프로파일 해시와 함께 내장하되 지도 표시와 교전 권한에는 사용하지 않는다.

[변경 전 구버전 결과](../A/REPORT.md) / [누적 수정 결과](REPORT.md). 실제 브라우저 RF 회귀와 의도적 비명중은 [ALL4_TERM](../../missile/termination/A/README.md)에 별도로 기록한다.

내부 무기 키 `SM2`는 SM-2MR Block IIIA, `SM2ER`는 SM-2ER Block IV, `SM6`는 SM-6 Block IA, `ESSM`은 ESSM Block 2다.
