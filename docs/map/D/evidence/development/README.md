# 개발/준비 증거 (최종 통과 수에 포함하지 않음)

- pre-support-fix: 관측 해면충돌 표식 전달 보완 전 빌드. 기존 조건/초기 fixture 준비 로그를 보존한다.
- pre-display-policy-fix: BDA 숨김 관측 파일도 내부 관문에 전달하도록 정리하고 링 라벨을 분리하기 전 빌드. 진행 중 검사 출력은 여기로 옮기고 최종 HTML로 다시 실행했다.
- support-before.json: 표시 가능한 관측 해면충돌+BDA 파일에서 미리보기 OK / 실제 TRACK_SUPPORT_BLOCKED가 갈리던 실제 재현. 최종 native 검사에서는 숨김/표시 조합을 포함해 모두 일치한다.
- d-edges-fixture.log: active 플래그만 세운 geometry stub으로 실제 PiP 입력을 마운트하지 못한 준비 실패. 제품 수정 없이 실제 3D open/ready 경로로 바꾸고 재실행한다.
- 중복 개발 PNG는 보고서 용량을 줄이기 위해 제외했다. 최종 캡처는 evidence/d-ui, d-edges와 기존 회귀의 각 폴더에 있다.

최종 판정은 상위 evidence/acceptance.json과 그 파일이 지정한 최종 HTML SHA를 사용한다.
