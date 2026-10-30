# 재현

이 폴더의 검사는 저장소 전체 checkout 기준이다. 보고서 ZIP은 증거 모음이며, 다른 단계의 원본 검사·기준 HTML은 저장소에서 읽는다. Python Playwright와 Chromium, Node의 acorn(기존 source.cjs가 사용)이 필요하다. 아래 명령은 저장소 루트에서 실행한다.

```sh
python docs/map/D/build.py
node docs/map/D/static_verify.cjs
python docs/map/D/run_domain.py
python docs/map/D/run_final_native.py
python docs/map/D/run_final_ui.py
python docs/map/D/verify_d_native.py
python docs/map/D/verify_d_ui.py
python docs/map/D/verify_d_edges.py
python docs/map/D/acceptance.py
python docs/map/D/write_report.py
python docs/map/D/package.py
```

build.py는 지정 MAP_C SHA를 검사하고 새 HTML/압축 manifest를 재생성한다. 검사 때 쓴 브라우저 backend와 fixture는 각 evidence/test-migration.json 및 TEST_HARNESS_NOTES.md에 기록한다. 승인된 paired 기준값은 사용자 승인 DDG3+CG3을 그대로 사용하며 guard만 산출물 UI 코어 해시와 일치해야 한다. 새 게임 코드가 바뀌면 guard를 검토 없이 재사용하지 않는다.

배포는 map-d 브랜치만 push한다. main 병합·release·tag 생성·aegis-smoke.yml 수정은 하지 않는다. 원격 readback은 별도 영수증 커밋으로 기록해 ZIP 자체 해시 순환 참조를 피한다.
