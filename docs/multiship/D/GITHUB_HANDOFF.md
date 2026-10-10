# D 원격 인계

사용자의 직접 업로드 승인과 [지침7.1](../../../AEGIS_PROJECT_INSTRUCTIONS.md#71-github-직접-업로드-및-확인)에 따라 원본 HTML/support를 직접 push/readback한다.

- 저장소 `0-FLANDRE-0/Aegis_Project`, branch `multiship-weapons-d`.
- 기준 C head `a57ed7ee1007bfa549b82b8f9f8ee8396241cae9`, [C PR#47](https://github.com/0-FLANDRE-0/Aegis_Project/pull/47).
- PR base는 `multiship-sensors-c`. A/B/C/main 예상 head를 확인하고 기존 branch는 수정/병합하지 않는다.
- C HTML/status/SHA/workflow는 `archive/v48/WIP_MULTI_SHIP_C/`에 같은 bytes로 보존한다. 안정 v48·packed assets0~12·profile/module revision을 유지한다.
- 현재 workflow는 `multiship-d.yml`. static/checksum/rebuild/guidance 뒤13개 browser suite와 저장소 smoke를 검사한다.
- 최초 push 후 독립 bare fetch에서 HTML·D support·C archive·stable의 bytes/SHA/Git blob을 대조한다. 원격 증거 자체를 포함하는 후속 commit과 최초 publication을 구별한다. actual CI는 PR 최신 head checks를 따른다.

최종 원격 head·PR·readback/CI는 publication 뒤 아래에 기록한다.
