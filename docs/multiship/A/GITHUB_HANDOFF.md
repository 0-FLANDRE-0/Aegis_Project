# Multi Ship A 업로드 인계

원격 준비 브랜치는 `multiship-runtime-a`다. 기준은 `main@cb70a637105ce00e7c0619270237cc35a83d39c2`이며 저장소는 `0-FLANDRE-0/Aegis_Project`다.

`AEGIS_PROJECT_INSTRUCTIONS.md` 7.1의 기존 분담을 따른다. 사용자는 **Aegis_SIM_v48_WIP_MULTI_SHIP_A.html 하나**를 브랜치 루트에 업로드한다. Codex는 업로드 bytes/SHA/parent를 확인한 뒤 작은 지원 파일·상태·SHA·문서·workflow를 반영하고 PR/Actions를 진행한다. 현재 원격 브랜치는 기준 commit에 있고 새 HTML/support 업로드·PR·CI·병합은 아직 실행하지 않았다.

새 HTML SHA는 `SHA256SUMS_v48_WIP_MULTI_SHIP_A.txt`, 크기와 실제 검사 결과는 `AEGIS_PLAN_STATUS_v48_WIP_MULTI_SHIP_A.md`를 따른다. 별도의 전달 support ZIP은 백업이며 큰 HTML을 재업로드하는 대상이 아니다. 원본 E 세트와 당시 workflow는 `archive/v48/WIP_HARPOON_E/`에 같은 bytes로 이동한다. 원격 E HTML은 기존 blob을 이동하며 새로운 API Base64 업로드를 하지 않는다. 기존 stable/historical fixture 예외는 유지한다.

최신 CI는 `.github/workflows/multiship-a.yml`이다. 기존 `harpoon-e.yml`과 `harpoon-upload-check.yml`은 E archive에 같은 bytes로 보존하고 활성 workflow에서 제거한다. E 루트 파일 삭제가 옛 업로드 검사를 실행해 실패하지 않도록 한다. 과거 E의 178건이나 K의 284건을 이번 A에서 재실행한 수로 합산하지 않는다.
