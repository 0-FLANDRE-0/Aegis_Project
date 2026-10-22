# v48 WIP ALL4_TERM 상태

최신 PIP_B 위 누적 이식이다. 원본 v48 stable과 이전 데이터는 보존한다.

- HTML: `Aegis_SIM_v48_WIP_ALL4_TERM.html`, 18,278,162bytes
- SHA-256: `c6e10449c54b8b99aa2a51e2b7b1d3c020d15e36986c05f5941a172b90d15800`
- 새 브랜치: `missile-b4-termination` (기준 `294bbb066df41489e77f5f16d0ad6a84eec32f91`)
- 네 종류 Dynamic B4, 관측 기반 비행 종료, SM-6 배터리 480초를 반영했다. 신관/추진/항력/시커/Kappa 함수 166개는 동일하다.
- 원안의 대체 SARH/DL 유도 중 조기 종료 16조건과 종료 시계 65초 상한을 종료기에서만 보완했다. B4 수치·Kappa90초는 유지했다.
- 실제 게임 240발 ON/OFF 120쌍과 대체 지원 36발에서 기존 명중 99건 모두 유지, 조기 종료 0. 실제 RF 소실/재획득/미획득 및 배터리·정식 VLS 요청 검사 통과.
- 자연 SPY 트랙→LOCK→VLS→전체 fixed tick→실제 WebGL 8발 비교도 기존 명중 보존. 비명중 SM-6/ESSM은 OFF도 비명중이며 새 종료기로 먼저 정리된다.
- 기존 관련 회귀 420/420 (15 suites), UI 88/88. 실제 네이티브/독립 진단 5,894샘플 비교 오차0.
- ENV_B 96조합/120궤적을 2회 각각11,458사격으로 재측정, 원시46,068,182bytes 동일. 최종 Chromium 경계151건 모두 일치. 프로파일 해시 `f50d26e39ca3f231525dcf9a0923edd352fc2cd228f52e5deadff29e760a8108`.
- **알려진 B4 결과 변화:** SM-6 100km/5km/접근250m/s/seed12002는 구판 명중, B4 후 종료기 OFF도 SEA_IMPACT (3회 재현). B4 수치를 유지하라는 요청에 따라 임의 밸런스 수정하지 않았다. 종료기 조기 종료와 구분하며 전면 안정판으로 승격하지 않는다.
- 배터리 검증은 실제 비행 뒤 시계 체크포인트를 이용한 전원 경계 시험이다. 자연 비행480초 완주/실물 성능 보장은 아니다.
- PIP_B HTML/상태/SHA/두 ZIP/체크섬/workflow8개는 동일 bytes/blob archive, ENV_A 자료 변경0.
- [상세 보고](docs/missile/termination/A/REPORT.md), [재측정/전후표](docs/envelope/B/REPORT.md), [재현](docs/missile/termination/A/README.md).
- 실행용 HTML 1개 ZIP / 리포트 ZIP 분리, 원본 HTML 별도 업로드·전체 원격 readback. Actions 미실행, PR/병합 없음. 실제 발행 영수증은 `docs/missile/termination/A/remote-publication.json`.

후속: 알려진 B4 사격 변화 검토(수치 변경은 별도 요청), 그 뒤 기존 MAP_B 계획을 이어간다.
