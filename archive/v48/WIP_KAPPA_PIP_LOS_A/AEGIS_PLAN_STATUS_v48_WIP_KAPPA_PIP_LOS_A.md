# v48 WIP KAPPA_PIP_LOS_A 상태

- 기준 `range-loft-recovery-a` / `5af4726113994b4e38bbfe5da8283424f04856fe`. 별도 시험 브랜치 `kappa-pip-los-a`.
- HTML `Aegis_SIM_v48_WIP_KAPPA_PIP_LOS_A.html` / 18,271,532bytes / SHA-256 `b81e2f3fbf45eeaa750e7d6edea59c2c024ed0128eaf6a0b695c9ea2bd84e58e`.
- 자함/NPC `_wip79KappaPipState`의 수평 종말 방향2블록만 관측 PIP의 dx/dy로 변경. B4·설계/RMAX·fullLoft·추진/항력/질량/시커/신관/피해/배터리/종료기/해면판정/UI 및 TGO90초 유지.
- 14조건 A/B×2: 지정 SEA_IMPACT4건 모두 명중, 정상6건 유지, 횡단2/4→4/4. 기존 성공8건 유지·신규실패0. 이는14조건의 제한 합격이며 전체 안정성 보증이 아니다.
- 두28발 실행 원시 JSON 비트 동일. 실제 월드/독립 진단28쌍 25,529샘플 오차0, 진단 전후월드/RNG/틱 변화0.
- 새 실행 JS에서 진단 캡슐·함수 해시를 재생성해 불일치0. 현재 사거리표는 rows0/profileHashnull/envelopeMeasured=false. 기존 ENV_C·RECOVERY_A 결과는 구 유도 코드의 HISTORICAL 자료로 표시했다.
- 전체96조합/500km스윕, 새최대거리, 비기본정책, 전체420+UI88 및 자연센서 종합회귀는 실행하지 않았다. 추가 계수 조정이나 기존브랜치/main 병합·새PR·Actions 실행 없음.
- [보고서](docs/missile/kappa/A/REPORT.md), [실행 diff](docs/missile/kappa/A/game-change.diff), [검증](docs/missile/kappa/A/evidence/verification.json), [재현](docs/missile/kappa/A/README.md).
- 실행HTML ZIP / 보고서 ZIP 분리, 기존 RANGE_RECOVERY_A 전달세트7파일 동일 bytes/blob archive. 원격 전체 readback 기록은 발행 후 추가한다.
