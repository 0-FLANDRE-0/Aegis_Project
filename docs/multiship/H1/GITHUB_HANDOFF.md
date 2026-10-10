# H1 직접 업로드와 원격 확인

기준 G head는 `d902d24486918c23d43e3067be16ab03fbaedde2`, 작업 branch는 `multiship-tactical-h1`, PR base는 `multiship-network-g`다. 사용자의 직접 업로드 허가에 따라 원본 HTML까지 반영하고 독립 readback한다.

H1 HTML/status/SHA·README/작업 지침·지원 소스/검사/evidence·수동 workflow를 같은 버전으로 반영한다. G HTML/status/SHA/workflow는 same bytes/blob으로 `archive/v48/WIP_MULTI_SHIP_G/`에 보존한다. stable v48과 선행 support를 유지한다. force push, main 또는 선행 branch 병합은 이번 요청 범위에 없다.

최종 SHA의 로컬 검증 → package/support checksum → 정상 commit/push → G 위 H1 PR → remote tree/blob 및 독립 raw/base64 readback을 수행한다. readback 기록은 `evidence/remote-publication.json`이며 이 파일을 자기 checksum에 넣지 않는다. 이후 evidence-only commit은 원래 검증 HTML/support blob을 보존하고 최종 head·PR 상태와 같은 payload를 다시 확인한다.

사용자가 GitHub Actions를 사용할 수 없으므로 로컬 직접 검증이 마감 gate다. workflow는 수동 실행용으로 준비하며 dispatch하지 않는다. 기존 GitHub checks를 성공으로 바꿔 표기하지 않는다.
