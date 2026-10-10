# Multi Ship A 업로드 인계

작업 브랜치는 `multiship-runtime-a`다. 기준은 `main@cb70a637105ce00e7c0619270237cc35a83d39c2`이며 저장소는 `0-FLANDRE-0/Aegis_Project`다.

이번 최초 HTML은 사용자가 commit `28dfc4fcefb22e8c0989617b2212e37d096c05d6`에 업로드했다. parent는 기준 main이며 변경 파일은 새 HTML 하나다. 원격 크기 15,314,629 bytes·SHA `704d072429de73de843357235f665474f1827faf4db2328a2822cc23e8fa6685`·Git blob `0232701c8acf6dc4330bcaba4243dd99ccf1d96d`를 로컬 검증본과 대조했다. [증거](evidence/remote-upload-check.json). 검증한 사용자 commit을 parent로 지원 파일과 규칙을 반영한다.

2026-10-10 사용자가 원본 HTML 직접 업로드를 승인해 `AEGIS_PROJECT_INSTRUCTIONS.md` 7.1을 바꿨다. 앞으로 Codex가 큰 HTML과 지원 파일의 업로드·원격 검증·PR/CI까지 진행한다. Git push 또는 사용 가능한 API/blob 방법으로 원본 bytes를 그대로 전송하고 remote readback 크기/SHA/blob을 확인한다. 사용자의 수동 HTML 업로드를 필수로 요청하지 않는다. 이미 검증된 이번 HTML blob은 재사용한다. 병합은 해당 작업에 대한 사용자 요청을 따른다.

새 HTML SHA는 `SHA256SUMS_v48_WIP_MULTI_SHIP_A.txt`, 크기와 실제 검사 결과는 `AEGIS_PLAN_STATUS_v48_WIP_MULTI_SHIP_A.md`를 따른다. 별도의 전달 support ZIP은 백업이다. 원본 E 세트와 당시 workflow는 `archive/v48/WIP_HARPOON_E/`에 같은 bytes/blob으로 이동한다. 기존 stable/historical fixture 예외는 유지한다. PR/Actions 결과는 해당 GitHub 기록을 따른다.

최신 CI는 `.github/workflows/multiship-a.yml`이다. 기존 `harpoon-e.yml`과 `harpoon-upload-check.yml`은 E archive에 같은 bytes로 보존하고 활성 workflow에서 제거한다. E 루트 파일 삭제가 옛 업로드 검사를 실행해 실패하지 않도록 한다. 과거 E의 178건이나 K의 284건을 이번 A에서 재실행한 수로 합산하지 않는다.
