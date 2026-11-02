# TRACK-B 안정화 검토 자료

주 보고서는 `docs/contact/track/B_stabilization_r4/REPORT.md`, 기계 판정은 같은 폴더의 `VALIDATION.json`입니다. **INCOMPLETE / ACTIVE 미승인** 상태입니다. 함수 검사 통과를 전투 안정화 완료로 취급하지 않습니다.

- `TRACK_B_STABILIZATION_HTML.zip`: 독립 실행 HTML 두 개와 모드 설명. SHADOW는 기존 B 실제 동작을 유지하며 ACTIVE는 피해 악화가 확인된 검증 후보입니다.
- `TRACK_B_STABILIZATION_REPORT.zip`: 현재 보고서·전체 후보의 소스/diff/도구·R2/R3/R4 원시 로그·최신 스크린샷·도표. 기존 실패·중단·미실행 자료를 보존합니다.
- `TRACK_B_STABILIZATION_HISTORICAL_EVIDENCE.zip`: 이전 R1의 원시 로그·스크린샷 등 evidence 폴더 전체. GitHub의 단일 파일 100MiB 제한 때문에 분리했으며, 최신 R4 원시 자료·이미지는 주 REPORT ZIP에 있습니다. 이전 문서의 raw·PNG까지 보려면 이 ZIP도 주 보고서와 같은 폴더에 풀면 원 경로가 복원됩니다.

각 ZIP의 manifest에는 파일별 바이트 수·SHA-256이 있습니다. ZIP 자체 체크섬은 GitHub에서 옆에 제공하는 `SHA256SUMS.txt`와 별도 `ARTIFACTS.json`을 확인하십시오. 파일을 바꾸거나 손실 압축해 크기를 맞추지 않았습니다. 모든 기존 원시 로그·PNG는 세 ZIP의 합집합 및 저장소에 바이트 그대로 남겼습니다.

재현 도구는 `0-FLANDRE-0/Aegis_Project` 저장소 체크아웃을 기준으로 합니다. 기본 branch `track-b-association@1d925540…`와 동결 HTML·원 검사 해시를 확인하며, 실제 제품을 실행합니다. 게임 코드·기존 기대값·허용 오차를 바꿔 결과를 맞추지 않습니다. 브라우저가 필요한 검증은 자체 실행 환경과 의존성이 필요합니다.
