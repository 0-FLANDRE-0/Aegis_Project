# D 원격 인계

사용자의 직접 업로드 승인과 [지침7.1](../../../AEGIS_PROJECT_INSTRUCTIONS.md#71-github-직접-업로드-및-확인)에 따라 원본 HTML/support를 직접 push/readback한다.

- 저장소 `0-FLANDRE-0/Aegis_Project`, branch `multiship-weapons-d`.
- 기준 C head `a57ed7ee1007bfa549b82b8f9f8ee8396241cae9`, [C PR#47](https://github.com/0-FLANDRE-0/Aegis_Project/pull/47).
- PR base는 `multiship-sensors-c`. A/B/C/main 예상 head를 확인하고 기존 branch는 수정/병합하지 않는다.
- C HTML/status/SHA/workflow는 `archive/v48/WIP_MULTI_SHIP_C/`에 같은 bytes로 보존한다. 안정 v48·packed assets0~12·profile/module revision을 유지한다.
- 현재 workflow는 `multiship-d.yml`. static/checksum/rebuild/guidance 뒤13개 browser suite와 저장소 smoke를 검사한다.
- 최초 push 후 독립 bare fetch에서 HTML·D support·C archive·stable의 bytes/SHA/Git blob을 대조한다. 원격 증거 자체를 포함하는 후속 commit과 최초 publication을 구별한다. actual CI는 PR 최신 head checks를 따른다.

[PR #48](https://github.com/0-FLANDRE-0/Aegis_Project/pull/48)을 C 위에 연결했다. 최초 publication `a7e12462427a5707f1dc187948a075b475cc804e`에서 원본과 support/보존 파일379개를 독립 원격 bare fetch로 byte-identical 확인했다. [증거](evidence/remote-publication.json)는 당시 pre-reset HTML SHA `af9c44d53589b1a9ee82031fa0d1277d4ffb21d3db599f0337f3dc64ad1dd687`와 해당 Git blob을 기록한다. 해당 D workflow의 static+13 browser suite는 성공했다. 이 증거를 새 final HTML의 readback/CI로 세지 않는다.

최종 HTML SHA `babac7fba08e4d59628c25245b1c657a87516f6774f6ec505c2314b1e3c1bf6e`에는 자함 피격 중복 방지 기록 reset 보강이 추가됐다. 같은 번호를 재사용하는 실제 Harpoon 반복 명중이 PASS다. 후속 publication commit의 같은 head에서 전체 D workflow와 smoke를 재검사한다. 최신 head readback은 작업 공간의 final-publication.json과 PR 실제 checks에서 확인한다. 원본 HTML bytes는 그 metadata commit에서 유지하며 A/B/C/main을 병합하지 않는다.
