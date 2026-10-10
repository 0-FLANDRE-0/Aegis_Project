# E 직접 업로드·인계

[작업 지침 7.1](../../../AEGIS_PROJECT_INSTRUCTIONS.md#71-github-직접-업로드-및-확인)에 따라 원본 HTML과 지원 파일을 직접 업로드하고 독립 원격 readback/CI를 확인한다. 사용자 수동 업로드는 필요하지 않다.

- 기준 D head `c6da52b960b447d8b4eadb6cac904b9c0ebff730`, branch `multiship-defense-e`, PR base `multiship-weapons-d`.
- D HTML/status/SHA/workflow는 `archive/v48/WIP_MULTI_SHIP_D/`에 동일 bytes로 이동했다. D support/evidence는 역사 자료로 그대로이며 현재 manifest/workflow는 E다.
- root E HTML, 같은 token 상태/SHA, README/작업 지침, E support·검사·증거·workflow를 한 commit으로 반영한다. 원격 별도 bare fetch 후 모든 tracked bytes/blob을 대조한다.
- C observer 시험의 all-foreign WITHHELD는 AI 이전 계약이다. E 시험은 UNKNOWN/수상 보호와 측정 기반 ASM 승인 조건을 분리 검증한다. 기존 smoke는 역사 payload/기준 파일을 사용하며 E 동일 SHA 검사와 구별한다.
- 최신 commit의 `Multi Ship E defensive AI and aircraft scenario` static+18 browser suite, 기존 `AEGIS smoke check` 전체 결과를 확인한다. 구 commit/candidate의 PASS를 최신 head 인증으로 취급하지 않는다.
- main/A/B/C/D/E 임의 병합, release/tag와 stable 승격은 실행하지 않는다. 후속 EW/공격/헬기는 별도 범위다.

최종 원본 HTML SHA `d1aa4b1876bea2739aec17f6f2c4e421e5ecef9957aa28113fab14d4117d0af2`, main SHA `446f96c11279970cda4d9e5542137dad96ba86ee155f3f503cbf83fa51f2c105`. 결과/한계는 [README](README.md)와 [직접 검증 집계](evidence/verification-summary.json)를 따른다. PR checks/artifacts가 CI의 실제 상태다.
