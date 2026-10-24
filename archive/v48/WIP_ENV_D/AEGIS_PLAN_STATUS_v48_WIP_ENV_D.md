# v48 WIP ENV_D 상태

- 기준 KAPPA_PIP_LOS_A `80b65143d10f0fc42072d068dacbbc69a2b78fc3`, 별도 시험 브랜치 `reg-k-env-d`.
- HTML `Aegis_SIM_v48_WIP_ENV_D.html` / 18433996bytes / SHA-256 `7d442b1fb254033b8bf281737c9c3d69745107d538e65fdbf6483acf809ce8a3`.
- 기존 게임 JS는 새 데이터/API 블록을 제거하면 byte 동일. 게임 함수·계수 변경0, 지도/발사/AI/저장 연결0.
- 기존420회귀+UI88, 종료기16, 자연센서→LOCK→정식VLS→전체fixed tick→실제WebGL8발 검수 완료. 이전 기준 대비 성공→실패0건, 실패→성공2건. 모든 결과/CPA/비행시간 차이는 보고서 CSV에 보존했다.
- 무표적120초 hash 동일. SM-6 100km/5km/접근250/seed12002 전투는 양쪽 최종 비명중이며 최근접/종료시간이 달라졌다. 수정하지 않았다.
- ENV_D 실제 ASM 피해 경로: 기본120칸+Kh-32 보조6칸,5개 독립 RNG/항법 seed. 유효 범위는5km부터 연속3/5 KILL/STRUCT_FAIL, 최대는1/5 이상 native 효과. 0km도 정의에 따른 결과다.
- 측정 175,955발, 전수1회. 경계와 고정 무작위30궤적만 반복. 실제 게임/독립 진단 ASM/횡단 포함6조건 오차0, world/RNG/tick 변화0.
- ENVELOPE_TABLE_D120칸, profile hash `9eedaab4c23edcb8e2fb06f36b3e9f367517e3724e1d660efe5f3de5b6f00000`. `__ENV_D__.status()` 일치. 이전 AIR용 진단/ENV_C 원시 결과는 별도로 보존했다.
- 초기 계통손상 콜백 누락 시도는 중단·무효 표시했으며 최종 표에 포함하지 않았다. 센서/교전 지원은 이상 조건, 결과는 SIM_TUNED 게임 모델이다.
- [보고서](docs/envelope/D/REPORT.md), [검증](docs/envelope/D/evidence/verification.json), [전체 표](docs/envelope/D/ENVELOPE_TABLE_D.json), [재현](docs/envelope/D/README.md).
- 실행 HTML ZIP과 리포트 ZIP 분리. 이전7파일 같은 bytes/blob 보존. 기존 브랜치/main 병합, PR, Actions 실행 없음. 원격 전체 readback 영수증은 발행 후 추가한다.
