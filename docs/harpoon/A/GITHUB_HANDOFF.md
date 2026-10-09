# Harpoon A GitHub 인계

완성 HTML은 `Aegis_SIM_v48_WIP_HARPOON_A.html`, **14,962,500 bytes**, SHA-256 `ffd976a211c530bc4d193597751e49febbd755646b865e6ad2685cd9e06aab77`이다. 사용자 제공 하푼 모델과 필요한 자료를 모두 내장한다.

[프로젝트 지침 7.1](../../../AEGIS_PROJECT_INSTRUCTIONS.md#71-github-업로드-분담)에 따라 원격 [harpoon-block1c-a](https://github.com/0-FLANDRE-0/Aegis_Project/tree/harpoon-block1c-a)는 먼저 `main@f51247496725aa8aadad69d5c8d3449c5bbc3a81`에서 생성했다. 사용자는 **이 HTML 하나만 해당 브랜치의 루트에 같은 이름으로 업로드**한다. 현재 원격에는 Harpoon HTML·지원 자료·PR이 없으며 새 CI도 실행하지 않았다.

업로드 뒤 Codex는 원격 HTML의 크기·SHA·Git blob·branch ancestry를 실제 로컬 파일과 대조한다. 기존 source를 변경하는 PR가 섞였으면 재검사한다. 파일명이 같아도 bytes가 다르면 검증본으로 취급하지 않는다.

대조가 끝나면 다음 작은 지원 자료를 반영한다.

- `docs/harpoon/A/`의 프로필·core·renderer·재현 빌더·작은 압축 asset·원본 관 등록·검사·출처·실행 evidence.
- root 상태 문서·SHA·README·작업 지침, Harpoon 전용 workflow.
- 기존 K HTML/상태/SHA를 archive로 **동일 Git blob 이동**. K HTML은 이미 remote object store에 있는 기존 blob이므로 다시 업로드하지 않는다.
- K workflow의 root candidate 존재 확인. 역사 K 지원 checksum은 당시 근거로 보존하며 새 branch 검사는 Harpoon support manifest를 사용한다.

그 뒤 구체적인 PR을 만들고 Harpoon 전용 static/runtime/native/64× salvo/CG/DDG Actions를 같은 업로드 bytes에서 실행한다. main 병합·정식 승격은 새 승인 지시가 있을 때 진행한다. 사용자의 이전 PR #43 병합 지시는 해당 K 단계에서 완료되었다.

큰 HTML의 `gh api` Base64 blob 전송이나 Git push는 이 인계에서 실행하지 않았다. small support를 먼저 올려 candidate가 없는 CI를 만들지도 않았다. 로컬 지원 package를 보존하고 원격 업로드가 오면 이 순서로 이어간다.
