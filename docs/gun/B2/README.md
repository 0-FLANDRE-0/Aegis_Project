# GUN_B2 — Phase 0 인계

현재 단계는 **진단만 수행한 Phase 0**이다. 게임은 기준 GUN_B1 그대로이며
`Aegis_SIM_v48_WIP_GUN_B2.html`은 만들지 않았다. 지시서 §2/§12에 따라
보고서를 push한 뒤 사용자 승인을 기다린다. Phase 1 초안은 구현된 기능이 아니다.

- [PHASE0.md](PHASE0.md): 최종 2,400회 진단과 A–D 비교, 오차 분해, 제안.
- [ORIGIN_CONTRACT_FINDING.md](ORIGIN_CONTRACT_FINDING.md): 원점 누락 경로와 범위 충돌.
- [PROTOCOL.md](PROTOCOL.md): 조건, 새 페이지 격리, 중단/검열, 과거 자료 비교 규약.
- [PHASE1_PROPOSAL_DRAFT.md](PHASE1_PROPOSAL_DRAFT.md): 미적용 SIM_TUNED 초안 전체.
- [evidence/acceptance.json](evidence/acceptance.json): 완전성·동등성·보존 검수.
- [approved-gun-baselines.json](approved-gun-baselines.json): 사용자 승인 CG 3건/EW 2건의 이전·새 값과 해시.
- [REMOTE_READBACK.json](https://github.com/0-FLANDRE-0/Aegis_Project/blob/gun-b2/docs/gun/B2/REMOTE_READBACK.json): 실제 GitHub 다운로드 검증 영수증. ZIP 생성 뒤 별도 커밋에 둔다.

보고서 ZIP의 `REPORT.html`을 열면 표와 그래프를 볼 수 있다. 게임 HTML은
리포트 ZIP에 포함하지 않는다. 이 단계에는 새 게임 파일이 없다.
`CHECKSUMS.sha256`의 기준 GUN_B1 HTML 항목은 ZIP 밖의 원본 게임 파일을 뜻한다.

## 재현 환경

전체 저장소 checkout, Python Playwright와 시스템 Chromium, Node.js와 Acorn,
Matplotlib이 필요하다. 진단 도구는 기존 `docs/` 공통 하네스와 실제 제품 함수를
불러오므로 보고서 ZIP만으로 게임 회귀를 실행할 수는 없다.

게임 기준 SHA-256:
`c9ec99f0b04e24127cc494833b8b1de24492a7ef0c00c2ee1432dba131f83ccc`.
`diagnostic/build_fixture.py`는 이 값을 검사하고 계측 소스를 메모리에서만 만든다.
제품 HTML에는 계측 코드·A–D 플래그를 기록하지 않는다.

## 시험 실행

새 출력 경로를 사용한다. `--output replay`는 `evidence/replay/`에 기록한다.
아래 명령의 worker 번호를 0, 1, 2, 3으로 달리해 네 프로세스로 실행한다.
이는 독립 브라우저 시험이며 한 게임 월드나 RNG를 공유하지 않는다.

```sh
TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python docs/gun/B2/diagnostic/run_trials.py --worker 0 --workers 4 --experiments BASE,A,B,C,D --transport http --output replay
```

전체는 80조건 ×30시드=2,400회다. `--seeds 1`은 빠른 행렬 확인용이다.
이 축소 실행을 정식 30시드 결과로 대체하지 않는다. 동일 출력 디렉터리에서는
caseId로 완료 회차만 건너뛰므로 서로 다른 행렬 크기를 섞어 재개하지 않는다.
모든 회차는 새 게임 페이지에서 부팅한다. 원시 JSONL은 발별 계측을 포함한다.

- `diagnostic/verify_hooks.py`: native와 계측/플래그 OFF의 8조건 비교.
- `diagnostic/verify_repeats.py`: 사전 지정 A–D 8조건 반복 검증.
- `diagnostic/verify_http_boot.py`: CDP/HTTP 전달만 다른 4조건 비교.
- `diagnostic/unit_probes.py`: native 초기 산포, RNG, 틱 CPA, 수상 shadow 진단.
- `diagnostic/origin_contract.py`: 잡음 없는 private 원점 계약 16조건.
- `diagnostic/replay_a_stop.py`: 피격 후 private sway까지 지우는 A 보완본 480회.
  보존된 원본 `evidence/trials/`에서 동일 caseId/입력을 읽는다. worker 0…3으로
  실행한다. `--probe`는 문제 A 1건과 non-A 격리 4조건 비교용이다.
- `audit_a_stop.py`: 최초 strict 정지 실패 10발, A 480회 전부 대체, 새 A의
  문제 조건 반복 재현과 non-A 4조건 동등성을 검사한다. 오차 허용치 완화 없음.
- `static_audit.cjs`: 제품/보호 함수 281개/ENV_D 보존과 소스 위치.
- `validate_approved.py`: 승인값과 코어 해시 guard, 부정 입력 거부 검사.
- `analyze.py`, `verify_phase0.py`, `plot.py`, `make_report.py`: 최종 정식 자료 수집.

마지막 네 도구는 원래 trials의 non-A 1,920회와 a-stop-corrected의 A 480회를
같은 caseId로 읽는다. 첫 run_trials 명령은 원래 2,400회를 재현하며 A 보완은
별도 replay_a_stop 명령이다. 기존 결과 폴더를 보존한 뒤 새 폴더에서 실행해야
완료 회차 건너뛰기를 피할 수 있다. 최종 보고 생성기는
2,400회가 완성되지 않았거나 검수가 실패하면 최종 보고를 만들지 않는다.
`NODE_PATH`에는 Acorn 설치 경로를 지정한다. `/dev/shm`/`MPLCONFIGDIR` 설정은
이번 실행 환경의 디스크 제약 대응이며 게임 규칙과는 관계없다.

## 과거 자료와 개발 기록

과거 B1 G7는 페이지 재사용 방식이어서 새 페이지 격리 결과와 비쌍대 비교다.
같은 제품의 회귀는 동일 입력의 native/계측 비교로 확인했다.
초기 혼합 실행은 NAV 일시 상태가 남아 묶음 전체를 무효화했다.
`evidence/development/interleaved-invalid/`와 pilot 자료는 정식 표본에 합산하지 않지만
검토 가능하도록 그대로 보존했다. 실패한 발만 선택적으로 제외한 것이 아니다.
또한 원래 A 480회 전체를 보존하고 보완 A 480회를 추가했다. 최종 행렬은
2,400회이며 실제 행렬 실행 합계는 2,880회다. 최초 A 실패 acceptance/log도 남긴다.

도메인 420건은 B1 승인 증거 378건 재사용 + 현재 게임의 새 실행 42건이다.
모든 420건을 새로 실행했다고 주장하지 않는다. 원래 실행 SHA는 유지한다.
게임 코드, 센서, 저장 스키마, CI, main, release/tag는 변경하지 않았다.
