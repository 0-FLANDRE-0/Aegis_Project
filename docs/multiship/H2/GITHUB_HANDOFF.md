# H2 직접 업로드와 원격 확인

기준 H1 head `43021f9693dc0500b5f2def531ec5d0d9e17bf0b`, 작업 branch `multiship-tactical-h2`, PR base `multiship-tactical-h1`이다. 사용자의 직접 업로드 허가에 따라 원본 HTML까지 반영하고 독립 readback한다.

H2 HTML/status/SHA·README/작업 지침·지원 소스/검사/evidence·수동 workflow를 함께 반영한다. H1 HTML/status/SHA/workflow는 same bytes/blob으로 `archive/v48/WIP_MULTI_SHIP_H1/`에 보존한다. stable v48과 선행 support는 변경하지 않는다. force push·main/선행 branch 병합은 이번 범위에 없다.

최종 원본 로컬 검증 → package/support pin → 정상 commit/push → H1 위 H2 PR → independent remote tree/blob 및 raw/base64 readback을 수행한다. `evidence/remote-publication.json`은 자기 checksum에서 제외한다. 후속 evidence-only commit은 검증한 HTML/support blob을 보존하며 최종 branch head·PR 상태와 payload를 다시 읽는다.

사용자가 GitHub Actions를 사용할 수 없으므로 로컬 검증이 마감 gate다. workflow는 수동 실행용이며 dispatch하지 않는다. 기존 checks의 실제 상태는 별도로 기록하며 성공으로 바꾸어 표기하지 않는다.
