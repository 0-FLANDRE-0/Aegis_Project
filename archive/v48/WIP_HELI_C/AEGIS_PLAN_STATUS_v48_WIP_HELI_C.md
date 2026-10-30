# AEGIS v48 WIP HELI_C — 출구·착륙장치·AIR·설정 고도

- 원본 `Aegis_SIM_v48_WIP_HELI_C.html`, **16,041,537bytes**, SHA `65c1f2ec7deb4bc4740a0477754edd210a6c09bacbefad41e93a3ae9675e6ff6`, packed13 SHA `5b7e4a3c551f8ea50fa46875a549ff0ffc0382ddad03660840bb8b5558ac43e9`. [조작·계약](docs/helicopter/D/README.md), [제원](docs/helicopter/D/altitude-spec.md), [검증](docs/helicopter/D/evidence/verification-summary.json).
- 기준 HELI_B `b4052e7113c8808bf89be43a21cba2d078bdb22c`, SHA `e4da7d69b3a4fb70583b336f5659a9f4956b63ed85bcf4fbf9e763ebf30017c3`. `helicopter-c` 작업이며 packed13의 항공 모듈만 변경한다.
- 출구 앞 함정 부품과 경사진 갑판으로 인한 기수 간섭, 이륙 뒤 꼬리 착륙장치 중복을 실제 source 모델에서 재현하여 수정했다. 정확한 부품/위치와 수정 전후 결과는 `evidence/model/model.json`을 따른다.
- AIR 높이를 줄이고 왼쪽 조작/오른쪽 여백·스크롤 목록을 유지한다. 출격 요청 버튼은 QUEUED일 때 출격 대기 취소로 바뀐다. 준비가 시작된 뒤에는 취소할 수 없다.
- 사용자의 재확인대로 AIR의 헬기 보기/모함 보기 버튼만 삭제한다. 3D CAMERA H1/H2 추적은 유지한다.
- 기체별 목표 고도25–3,962.4m MSL를 대표값 또는 직접 숫자로 설정한다. 초기50m, 운용 상하3.5m/s, SI/fixed60Hz를 유지한다. 공개 ceiling13,000ft의 근거는 미 태평양함대/제7함대2014-03-10 공개문이다. ceiling의 MSL UI 상한 적용과 고고도까지 일정한 운용 상승률은 SIM_TUNED다.
- 고도 변경은 위치·속도를 순간 변경하지 않으며 경로/호버/함선 추종에 적용한다. DEPART는 고도 상한까지 제자리 상승을 기다리지 않고 안전한 측방 이탈 뒤 경로/추종 중 계속 상승한다.
- C1 저장은 targetAltitudeM과 상승·하강 중 상태를 검증한다. 실제 B/A 저장은50m 기본값으로 migration하면서 기존 비행 pose/velocity/heading을 유지한다. 갑판 준비 중인 구형 저장은 다음 fixed tick부터 새 지상 배치·경로를 적용한다. 잘못된 저장은 쓰기 전에 거부한다.
- 기존120초 준비/갑판 대기열/다중 경로/선회 감속/약410m 함선 추종/공유 모델/로터/LOD를 유지한다. 렌더 read-only 및 truth→sensor/IFF/offboard/센서/무장/연료/회수/로터 공력 격리는 그대로다.
- 이전 B 네 파일은 `archive/v48/WIP_HELI_B/`에 same bytes/blob으로 보존한다. stable v48/원본 자산/이전 source·evidence는 변경하지 않는다.
- §7.1 원본 HTML 전체 직접 업로드·독립 GitHub blob readback을 수행한다. main/선행 branch 병합·새 PR·Actions dispatch는 실행하지 않는다. 수동 workflow만 준비한다.

## 최종 검증

- **248/248 PASS / 6 suites**, 최종 HTML SHA `65c1f2ec7deb4bc4740a0477754edd210a6c09bacbefad41e93a3ae9675e6ff6`. static59, ui70, altitude44, model27, clearance10, regression38. 내장 core/page/GL 오류는 각 보고서에서0이다.
- 실제 H1/H2 경로·전체 관련 native 함정 면/접힌 헬기 면 교차 검사, 바퀴1개/지상·공중 전환, CAMERA/로터·공유자원, 직접 고도·경계/실제 A/B 저장, DDG/CG idle·8Kh32 AUTO·피격 복구6쌍과1/8/16/64 fixed-state/RNG 회귀를 포함한다.
- Chromium/SwiftShader와390×844 touch viewport 검사이며 실제 휴대폰/hardware FPS를 뜻하지 않는다. 과거 검사 수를 새로 더하지 않는다.
- HTML 증가는 B 대비 **3,916bytes (+0.02442%)**. 원본 헬기 payload223,419bytes/geometry77/material12 공유를 유지한다.
