# Multi Ship C 원격 인계

사용자 승인과 [지침7.1](../../../AEGIS_PROJECT_INSTRUCTIONS.md#71-github-직접-업로드-및-확인)에 따라 Codex가 원본 HTML과 지원 파일을 직접 push/readback한다. 사용자 수동 업로드는 필요하지 않다.

- 저장소: `0-FLANDRE-0/Aegis_Project`.
- branch: `multiship-sensors-c`, 기준 B head `ae94326caea7cd0329233f381933cdc240bedb47`.
- B [PR #46](https://github.com/0-FLANDRE-0/Aegis_Project/pull/46), A PR #45는 착수 시 미병합이다. 새 PR은 `multiship-physics-b` 위에 연결한다. 이번 단계 요청은 병합 승인이 아니므로 A/B/C를 임의 병합하지 않는다.
- HTML `Aegis_SIM_v48_WIP_MULTI_SHIP_C.html`, 15,344,725 bytes, SHA `e306f755cad27cd32aef4ad2dff6c108ee56511cc9909f0609434558f0865363`.
- B HTML/status/SHA/workflow는 `archive/v48/WIP_MULTI_SHIP_B/`에 같은 bytes로 보존한다. stable v48과 원본 asset records0~12·장비 revision을 유지한다.
- 로컬 직접 검사 숫자는 [집계](evidence/verification-summary.json), actual CI는 같은 head의 GitHub checks를 따른다. 이전 B workflow/support manifest는 역사 기록이며 현재 workflow는 C다.

push 전 remote main/A/B 예상 head와 새 C branch 부재를 확인한다. 독립 원격 bare fetch에서 HTML·지원·B archive·stable의 bytes/SHA/Git blob을 대조한다. 최초 publication 증거를 이후 commit에 추가할 수 있으며 HTML bytes는 그대로 유지한다. 기록 자체를 포함하는 commit은 최초 publication과 구분한다.

현재 `.github/workflows/multiship-c.yml`는 checksum/static/exact rebuild/guidance 뒤 observer/propagation/clock/baseline/native/physical-native/departure/routes/knowledge/DDG를 실행한다. physical-native는 기존 B의 실제 원본 mesh·입출구 구멍·후속 draw/tick·reset fixture를 8배속에서 그대로 검증한다. 호스트 SwiftShader 1배속120초 wait timeout 예비 실행은 PASS로 세지 않는다. smoke의 역사 payload checks도 C 직접 판정에 합산하지 않는다.

## 원격 publication 확인

[PR #47](https://github.com/0-FLANDRE-0/Aegis_Project/pull/47)을 B branch 위에 생성했다. 최초 publication `e1cf3b55966cb87ede1f4d1a45f3af453bec8bee`의 HTML·지원·B archive·stable **104개 파일**을 독립 원격 bare fetch에서 다시 읽어 byte-identical임을 확인했다. 원본 C Git blob `9ab03765b1df538c2c22f16ea184ac715e9280ce`, HTML SHA `e306f755cad27cd32aef4ad2dff6c108ee56511cc9909f0609434558f0865363`다. [원격 증거](evidence/remote-publication.json). 기록 자체를 포함하는 후속 commit도 HTML bytes를 유지하며 실제 CI는 해당 최신 head checks를 따른다.
