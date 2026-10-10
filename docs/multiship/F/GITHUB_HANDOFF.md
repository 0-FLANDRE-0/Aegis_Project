# F 직접 업로드와 원격 확인

기준 E head: `bdcf8d1724a72587f9d42e4b1cf70ba4cbe57ef6` (`multiship-defense-e`). 작업 branch: `multiship-ew-f`, PR base: `multiship-defense-e`. main 및 선행 PR의 병합은 이번 작업 범위가 아니다.

원본 F HTML, 상태/SHA, README/작업 지침, F 지원·검사·evidence, 수동 workflow를 한 버전으로 반영한다. E 원본 HTML/상태/SHA/workflow는 같은 bytes/blob으로 `archive/v48/WIP_MULTI_SHIP_E/`에 보존한다. stable v48 및 모델·선행 support는 유지한다. 사용자가 직접 HTML을 올릴 필요가 없다.

1. 실제 remote main/E/F head·권한을 확인하고 선행 사용자 commit을 보존한다.
2. 최종 SHA의 로컬 직접 검증과 package/support checksum을 완료한다.
3. 정상 git push로 원본 HTML을 포함해 F branch를 반영한다. force/무관 브랜치 병합은 하지 않는다.
4. remote tree/blob 및 독립 raw readback으로 변경/새 파일 SHA와 original E/stable blob 보존을 확인한다.
5. E 위에 F PR을 만들고 조건/범위·검증·한계를 남긴다. 최종 원격 근거는 `evidence/remote-publication.json`에 기록한다.

사용자가 GitHub Actions를 사용할 수 없다고 명시했으므로 Actions 실행/성공을 이번 마감 조건으로 삼지 않는다. 새 F workflow는 수동 실행용이며 이번 작업에서는 dispatch하지 않는다. GitHub에 기록되는 기존 workflow 실패를 로컬 직접 검증 PASS로 바꾸어 표기하지 않는다.
