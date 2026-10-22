# RANGE_A

기준: `missile-b4-termination`의 `9a6838aade07c37262453e21cfe415d04d123d8c`, ALL4_TERM HTML SHA-256 `c6e10449c54b8b99aa2a51e2b7b1d3c020d15e36986c05f5941a172b90d15800`.

사용자 승인 범위는 ER/SM-6 설계 사거리8개 숫자뿐이다. `nominalRmaxKm`를 이상 조건 설계 기준과 같게 두고 `maxRmaxKm`는 같은 설계 상한, `rangeGoalKm`는 같은 목표, `fullLoftKm`는 해당 거리에서 shelf 보간이 포화되도록 같은 값으로 정렬한다. 게임의 계산 함수나 다른 제어 상수는 바꾸지 않는다. 이는 실제 최대 사거리를 강제로 제한하거나 보장하는 장치가 아니다.

- 순서: 변경 없는500km stage0×2 → 결과 보고 →8숫자 정렬 → 같은6조합×2 → ENV_C96/120×2.
- 저고도 해면 충돌은 조사만 한다. 수상충돌/고도하한/유도/자동조종은 수정하지 않는다.
- R1은 live source 역치환과 전 네이티브 함수 해시를 비교한다. 내장 진단 source 문자열을 live 코드와 분리한다.
- 실제 게임 발사 회귀는 기존 `docs/missile/termination/A/verify_live.py`와 원래 케이스를 그대로 사용한다.
- 실제 월드/독립진단 동일 경로는 `docs/envelope/C/verify_path_all4.py`로 비교한다.
- 기존420도메인/88UI 회귀는 원래 스크립트를 사용한다. 웹브라우저 실행은 native WebGL과 기존 headless2D backend 보정을 사용한다.
- 실행 HTML과 리포트는 별도ZIP으로 전달하며, 이전 ALL4_TERM8파일은 동일 bytes/blob archive한다. 원본 ENV_A/B와 사용자 제공 kit는 변경하지 않는다.

## 실제 게임 회귀 명령

정상240발/대체지원36발/손실·재획득12발/배터리8발/정식VLS4발은 기존 종료기 fixture와 시나리오를 그대로 사용한다. 아래 `OUT`은 새 검사 결과를 쓸 별도 폴더 이름으로 바꾼다. 후보/최종 HTML SHA를 결과에서 임의로 바꾸지 않는다.

```bash
python docs/missile/termination/A/verify_live.py Aegis_SIM_v48_WIP_RANGE_A.html OUT/normals-release.json --cases docs/missile/termination/A/cases/normal.json --batch 8
python docs/missile/termination/A/verify_live.py Aegis_SIM_v48_WIP_RANGE_A.html OUT/dual-release.json --cases docs/missile/termination/A/cases/dual.json --batch 8
python docs/missile/termination/A/verify_live.py Aegis_SIM_v48_WIP_RANGE_A.html OUT/faults-release.json --cases docs/missile/termination/A/cases/fault.json --batch 4
python docs/missile/termination/A/verify_live.py Aegis_SIM_v48_WIP_RANGE_A.html OUT/battery-release.json --cases docs/missile/termination/A/cases/battery.json --batch 4
python docs/missile/termination/A/verify_live.py Aegis_SIM_v48_WIP_RANGE_A.html OUT/release-request-final.json --cases docs/missile/termination/A/cases/release-request.json --batch 4
python docs/missile/termination/A/verify_live.py Aegis_SIM_v48_WIP_RANGE_A.html OUT/validation-release.json --cases docs/missile/range/A/cases/validation.json --batch 8
node docs/missile/range/A/verify_static.cjs Aegis_SIM_v48_WIP_RANGE_A.html OUT/static.json
python docs/missile/termination/A/verify_live_results.py OUT
python docs/pip/B/run_domain.py Aegis_SIM_v48_WIP_RANGE_A.html OUT/domain --parallel 2
python docs/missile/termination/A/verify_observed_world.py Aegis_SIM_v48_WIP_RANGE_A.html OUT/observed-world
python docs/missile/range/A/verify_truth120.py Aegis_SIM_v48_WIP_RANGE_A.html OUT/truth120
python docs/missile/range/A/verify_causality120.py Aegis_SIM_v48_WIP_RANGE_A.html OUT/causality120
```

PiP88검사는 원래 `docs/pip/B/verify_ui.py` 앞에 `docs/pip/B/browser_backend.py`의 `install()`을 적용해 실행한다. 전투120초 인과 대조는 생산 HTML을 수정하지 않고 메모리의 버리는 페이지에만8값을 복원한다. 대상 AI와 실제 SPY 관측/정식 발사 경로를 유지한다.

이전 실행 HTML이 필요한 정적/전투 대조는 저장소의 `archive/v48/WIP_ALL4_TERM/`를 읽는다. 리포트 ZIP에는 실행 HTML이 없으므로 저장소 checkout 또는 별도 실행 ZIP을 준비한다. 전체 측정 명령은 [ENV_C 재현](../../../envelope/C/README.md)을 따른다.
