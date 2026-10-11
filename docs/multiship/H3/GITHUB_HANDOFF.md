# H3 직접 업로드 계약

사용자가2026-10-10에 원본 HTML을 포함한 GitHub 업로드/확인을 위임했다. `AEGIS_PROJECT_INSTRUCTIONS.md` §7.1이 해당 standing authorization을 기록한다. 원본을 배제하거나 새 manual-upload 승인 흐름을 만들지 않는다.

기준은 H2 final head `59fad37cc170c760c1659b916febc168021a31b4`, 작업 branch `multiship-tactical-h3`, PR base `multiship-tactical-h2`다. main/선행 PR 병합·force push는 이번 범위에 없다. H2 HTML/status/SHA/workflow는 bytes/blob을 유지해 `archive/v48/WIP_MULTI_SHIP_H2/`에 보존한다. stable v48과 역사 support를 변경하지 않는다.

최종 HTML, 상태/설명, root/support SHA, 재현 build/index, 직접 검사/캡처 및 manual workflow를 normal push한다. GitHub Actions는 dispatch하지 않는다. PR의 자동 smoke가 계정 billing 제한으로 시작되지 않더라도 직접 시험 PASS를 CI PASS로 바꾸어 쓰지 않는다.

[verify_remote.py](verify_remote.py)는 branch head/tree와 변경된 각 파일의 원격 bytes를 독립 조회한다. raw transport 실패 시 blob API/base64로 실제 원격 bytes를 읽고 exact 비교한다. 업로드 증거는 자기 checksum 순환에서 제외한다. 후속 proof-only commit은 검증된 HTML/support blob을 변경하지 않으며 최종 head도 다시 확인한다. 기록된 SHA/checks와 원격 branch/PR의 실제 상태를 함께 확인한다.
