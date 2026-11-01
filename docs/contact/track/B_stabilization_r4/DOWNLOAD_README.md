# TRACK-B 안정화 검토용 HTML — ACTIVE 미승인

**TRACK-B는 INCOMPLETE이며, 이 묶음은 완료·배포 승인본이 아닙니다.** 파일명의 `STABLE_D`는 후보 구분자입니다.

- `Aegis_SIM_v48_WIP_TRACK_B_STABLE_D_SHADOW.html`: 기존 B ACTIVE의 실제 선택·상태 처리를 유지하고 새 연관 제안을 비교하는 SHADOW입니다. 기존 B 자체의 미해결 문제를 고친 완료본이라는 뜻은 아닙니다.
- `Aegis_SIM_v48_WIP_TRACK_B_STABLE_D.html`: 새 연관 및 작업 소유권 수정을 소비하는 **검증용 ACTIVE 후보**입니다. 6기 전투의 실제 피해 악화가 확인되어 적용·병합을 권고하지 않습니다. 재현·검토 용도로 제공합니다.

콘솔 확인은 `window.__TRACK_B__.stabilizationMode`를 사용합니다. 호환성을 유지한 기존 `mode` 값은 두 파일 모두 원 B의 `ACTIVE`이므로 새 후보의 소비 여부를 뜻하지 않습니다.

압축을 풀어 HTML을 열 수 있습니다. GitHub의 HTML 링크가 소스를 표시하는 문제를 피하기 위해 바이너리 ZIP으로 전달합니다. HTML의 SHA-256은 동봉한 `VALIDATION.json`과 별도 `SHA256SUMS.txt`/보고서에서 확인할 수 있습니다.

보고서·diff·시험 도구·원시 로그는 별도 REPORT ZIP입니다. 기존 실패와 미실행 자료도 포함되어 있으며, R1/R2/R3의 통과를 R4 통과로 재사용하지 않습니다. 재현 도구는 `0-FLANDRE-0/Aegis_Project` 체크아웃을 기준으로 하며 경로·함수·제품 해시를 검증합니다. 게임의 비행·RF·EKF·IFF·ROE·무장/피해 계수나 기존 기대값을 맞추는 조정은 하지 않았습니다.

main과 기존 기준 브랜치에는 이 작업을 반영하지 않았습니다. 최종 판정과 남은 미승인·미측정 항목은 보고서의 `REPORT.md`, `VALIDATION.json`을 참조하십시오.
