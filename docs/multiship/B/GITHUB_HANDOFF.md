# Multi Ship B 원격 인계

사용자 승인과 [저장소 지침 7.1](../../../AEGIS_PROJECT_INSTRUCTIONS.md#71-github-직접-업로드-및-확인)에 따라 Codex가 대용량 원본 HTML과 지원 파일을 직접 Git push하고 원격 bytes를 확인한다. 사용자 수동 HTML 업로드는 필요하지 않다.

- 저장소: `0-FLANDRE-0/Aegis_Project` (private, push/admin 권한 확인).
- branch: `multiship-physics-b`.
- 시작 head: `3fab03782abb313cd3ece1bbfe254cdb77981231`, 동일 A branch head.
- main: `cb70a637105ce00e7c0619270237cc35a83d39c2` (PR #44 Harpoon E).
- A PR [#45](https://github.com/0-FLANDRE-0/Aegis_Project/pull/45)는 시작 시 open/unmerged이다. B PR은 `multiship-runtime-a`를 base로 연결한다. 이번 요청에 병합 지시는 없어 A/B를 임의 병합하지 않는다.
- 최종 HTML `Aegis_SIM_v48_WIP_MULTI_SHIP_B.html`, **15,328,273 bytes**, SHA `1165c72aecf59fe42b38ac46b9ef8cde771e61dc8673e45d06c4c027565c2946`.
- 직접 최종 파일 검증 **466/466 PASS**, 과거 합산0. [검증 집계](evidence/verification-summary.json).
- A HTML/status/SHA/workflow는 동일 bytes/blob으로 `archive/v48/WIP_MULTI_SHIP_A/`에 보존하며 stable v48은 unchanged SHA `9e786ddb1331fcd496b6b9604cec87317667ebc501e99270cc33fd6ba1ab9e83`다.

push 전 remote expected head를 확인하고 fast-forward로 반영한다. 독립 원격 bare checkout에서 HTML 크기/SHA/Git blob, 지원 manifest, A archive와 stable을 다시 읽어 대조한다. 원격 publication 기록은 `evidence/remote-publication.json`에 추가한다. 해당 기록의 publication commit 뒤에는 기록 자체를 포함하는 후속 commit이 있을 수 있으며 HTML bytes는 동일하다.

현재 CI는 `.github/workflows/multiship-b.yml`다. static/checksum/rebuild/guidance 뒤 departure/runtime/contacts/baseline/native/fleet clock/routes/knowledge/Harpoon clock/DDG의 10 browser jobs를 실행한다. 기존 smoke는 역사 payload 검사도 포함하며 최신 B의 466개 직접 판정에 합산하지 않는다. 실제 PR/Actions 완료 상태는 GitHub의 해당 head 결과를 따른다.

## 원격 publication 확인

[PR #46](https://github.com/0-FLANDRE-0/Aegis_Project/pull/46)을 A branch 위에 생성했다. 최초 publication commit `6b060dd156405ef97d59c2f7b5eb4ad77a95032f`을 독립 원격 bare repository에서 다시 읽어 HTML·지원·A archive·stable **56개 파일**을 byte 단위로 대조했다. 모두 일치하며 원본 B Git blob은 `f534ffd1de49b5a7a1c81a6efc6753b710fa4aa8`이다. [원격 기록](evidence/remote-publication.json). 후속 commit은 이 기록/문서와 manifest를 포함하며 HTML bytes는 동일하다. 같은 최종 파일의 Actions 실제 결과는 PR checks를 따른다.
