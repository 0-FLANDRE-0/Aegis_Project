# v48 WIP RANGE_RECOVERY_A 상태

- 별도 시험 브랜치 `range-loft-recovery-a`, 기준 RANGE_A `d42284ae4666914c604f77adbde25045a915e93f`.
- HTML `Aegis_SIM_v48_WIP_RANGE_RECOVERY_A.html` / 18,283,317bytes / SHA-256 `9ee346084b0c1a32cf303127aae74517f11fed79305ce84678d85385a25bc826`.
- fullLoftKm만 ER360→240 / SM-6 450→260. nominalRmax/maxRmax와 rangeGoal360/450 유지. 추진/항력/Kappa/신관/배터리/종료기/UI/SM-2MR/ESSM 변경0.
- 정지6조건 BASE6/6 → RANGE_A0/6 → RECOVERY6/6. 접근300m/s는 세 버전 모두6/6. 원래 장거리에서 이탈150m/s는 모두0/6.
- 60km 이탈 확인 BASE6/6 → RANGE_A5/6 → RECOVERY5/6. ER60km/1km/이탈150의 SEA_IMPACT는 남았다. 전체 복구 완료나 병합 대상으로 판정하지 않는다.
- 본시험54+확인18조건 각각2회 원시 JSON 비트 동일. 실제월드/독립 진단72조건 167,236샘플쌍 최대오차0, 진단 전후월드/RNG/틱 변화0. 정적·종료기 원래6fixture 통과.
- 기존 ENV_C 96행 표는 보존했고 후보에서는 ‘재계산 필요’ 경고가 켜진다. 전체96스윕/새최대거리/420+88전체회귀/자연센서 종합 시험은 실행하지 않았다.
- [전체 보고](docs/missile/range/RECOVERY_A/REPORT.md), [검증](docs/missile/range/RECOVERY_A/evidence/verification.json), [재현](docs/missile/range/RECOVERY_A/README.md).
- 실행HTML1개 ZIP / 보고서ZIP 분리. 이전 RANGE_A 세트는 byte-identical archive하며 기존 브랜치와 ENV_C/종료기 자료를 보존한다. 원격 전체 readback 영수증은 발행 후 추가한다.
