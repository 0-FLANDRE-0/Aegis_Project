# v48 WIP RANGE_A 상태

- 기준 ALL4_TERM `9a6838aade07c37262453e21cfe415d04d123d8c` 위 `range-a-env-c`. 원본v48 안정판은 보존한다.
- HTML `Aegis_SIM_v48_WIP_RANGE_A.html` · 18,283,304bytes · SHA-256 `8f504eb45c19c34e473d0d04f08180afde95a9c72b5ec935ec0204bd9d7246b5`.
- 0단계500km6조건×2 완료 후 ER/SM-6 설계 사거리8값만360/450km로 정렬했다. 3,884명명 함수와 나머지live source 보존. 추진/항력/질량/연소/시커/Kappa/신관/배터리/종료기/MR/ESSM 설정 변경0.
- 정렬 후 고도1/10/20km 최대 명중 최초거리: ER136/135/241km, SM-6 135/132/286km. 목표 미달·정지 표적 사거리 퇴행을 보존하며 수치를 더 맞추지 않았다.
- ENV_C96조합+120궤적×2, 각 26,714사격/50,178,372bytes 동일. 상한500km, 분해능1km, 실제요격점 거리 추가. [전표·전후 비교](docs/envelope/C/REPORT.md).
- R1–R5 통과. 기존420/420(15suites)+UI88/88+종료기16/16. 정상OFF/ON 각85명중/조기종료0, 기존83명중 보존+2회복. 자연SPY/정식VLS/전체fixed tick/WebGL8발29검사 통과.
- 게임/독립진단 6,806샘플 오차0, 무표적120초truth/RNG hash 동일, 전투120초는8값복원 시 기준판과 동일, 최종브라우저 경계 172건 일치. 최종 native/table 해시 및 변경 경고 검사 통과.
- SM-6 seed12002 100km/5km 접근250m/s는OFF3/ON3회 모두83.183333초 명중으로 회복. 고도15km 이탈250m/s 퇴행은 전표 참조.
- 저고도 이탈3+횡단18 조사 완료. 횡단11해면충돌, 원인 경로·유도/하한 기록. 수정0.
- [전체6항목 보고](docs/missile/range/A/REPORT.md), [검수](docs/missile/range/A/evidence/acceptance.json), [재현](docs/missile/range/A/README.md).
- ALL4_TERM8파일 동일 bytes/blob archive. ENV_A/B/기존 종료기 자료 변경0. 원본HTML/실행ZIP/리포트ZIP 분리. 원격전체bytes 대조 영수증은 발행 후 `docs/missile/range/A/remote-publication.json`에 기록한다. Actions/PR/main·이전브랜치 병합 없음.

추가 결정 전에는 추진·항력·유도·해면 보호를 수정하지 않는다. 설계 거리와 기존 정규화 로프트의 상호작용이 실제 최대 명중 거리를 낮춘 결과를 먼저 검토한다.
