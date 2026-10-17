# HELI_F2 — AN/APS-153 ISAR

0번을 별도 완료·보고한 `helicopter-emcon-f2-0` 위에서 진행한다. `build.py`는 그 HTML SHA를 고정하고 packed13만 수정한다. 나머지13개 자산은 동일하다. 사용자 요청 범위와 기존 정책의 우선순위는 [CONFLICTS.md](CONFLICTS.md)를 따른다.

AIR의 ISAR → 표시된 수상 트랙 탭. 지정은 헬기 자신의 익명 확정 접촉을 위치·방위 게이트로 고른다. 함 트랙 ID는 헬기에 보내지 않는다. 9.3–296km 경사거리, 반사체 높이 기반 수평선·기상·클러터·빔·SNR 관문을 거친다. 안테나는 지정 방위에 고정하며, 탐색 출력/이진 M-of-N 창을 정지한다. 취소/완료 후 직전 모드로 복귀하고 한 주사 전환 공백을 둔다. 새 주사 ordinal만 진행해 오래전 같은 주사의 attempted 표시가 복귀 후 새 탐색을 억제하지 않게 한다.

공통 `shipboardRadarEchoFieldWip13B13`에 optional ISAR receiver/feature 합성 분기만 넣는다. 기존 탐색 호출은 그 분기를 실행하지 않아 기존 RNG 순서를 유지한다. `physical.js`만 실제 형상/침로/자세를 읽는다. 기존 survival heel/trim은 실제 물리값을 사용하고, 현재 선체 물리가 제공하지 않는 해상 주기 각운동 성분만 SIM_TUNED 추정한다. 향후 waveRoll/Pitch/YawRad가 제공되면 추정을 대체한다. 이후 처리는 익명 위치·공분산·측정 특징·위상 각변화만 읽는다.

16초 적분, 0.5초 간격 RF 측정, λ0.032m/(2Δθ), 거리 분해능2m는 모두 SIM_TUNED 일반 원리 설정이다. SNR/분해능/적분 완료도·유효 표본 비율로 품질을 산정하고 품질이 나쁘면 전장·높이 분포·최고점 위치 오차를 늘린다. 선수/선미 전장 관측성 우선은 이번 사용자 지정 단순화이며 모든 실제 ISAR 관측의 보편 법칙으로 주장하지 않는다.

`library-input.json`은 기준 HTML의 기존 프로파일 기하에서 오프라인으로 추출한 입력이다. `library.cjs`가 실제 RF와 같은 순수 기하 추출 함수를 써 `library.json` 정보자료를 만든다. 새 함급은 input의 registration 한 항목을 추가해 생성한다. 실시간 분류는 전장/구간 높이/마스트 위치와 해당 측정 σ만 비교하고 선수/선미 모호성을 허용한다. 실시간 표적 profileId/entity id로 라이브러리 항목을 고르지 않는다. 실측 APS-153 성능이나 고해상도 SAR 영상을 구현했다고 주장하지 않는 특징 기반 ISAR 단순화다.

별도 `AEGIS_OFFBOARD_ISAR_C_1` strict schema를 기존 ingest에서 분기한다. 결과 위치/양의정부호3×3 공분산/후보·신뢰도·특징/측정 시각/source H1/H2만 받는다. unknown/truth 필드·재전송·미래/600초 초과 시각은 거부한다. 각 기체8개 결과 버퍼, 모함16개 도착 큐/16개 정보 보관, 기존 링크 지연을 적용한다. 링크가 끊겨도 모드/판독을 조작할 수 있으며 복구 시 원래 측정 시각을 보낸다. plot64개 포트/나이/무버퍼는 그대로다.

함은 결과를 위치·증가한 위치 불확실성으로만 SURFACE 트랙에 연결한다. 기존 접촉 소멸 뒤 새 파일이 생겨도 자료를 재게이트할 수 있으나 identity/교전권한/운용자 식별은 복사하지 않는다. 정보는 트랙 상태를 갱신하는 radar plot이 아니므로 sensorAge/hits/confirmed를 변경하지 않는다. ISAR 중 마지막 탐색 보고가10초를 넘으면 하푼은 기존 관문에서 거부된다. 종료 뒤 탐색 갱신을 기다려야 한다.

운용자가 식별을 지정할 때만 유효 ISAR 근거를 스냅샷한다. 교전 로그에는 그 판단 당시 후보/신뢰도/측정 시각/판단 시각/그때와 발사 때의 경과시간을 복사한다. 나중 판독 결과가 이전 발사의 근거를 바꾸지 않는다. 종료만 기존 AFTER_ACTION_TRUTH 사후 기록이다.

AIR 진행률·품질·결과/취소, 지도/트랙 정보 태그·경과시간, 3D 고정 쐐기/잔상 없음/ISAR 라벨을 제공한다. 뷰는 detached render snapshot만 읽고 라벨 texture를 수명주기 종료 시 해제한다. DEBUG ISAR 판별표는 로컬 RNG로162가지 가정 조건을 계산하고 실시간 상태를 바꾸지 않는다. 범위/SNR 미달 행은 가정 분류 결과이며 실제 판독 가능성을 주장하지 않는다.

`window.__ISAR_F2__.snapshot()` / `.diagnostic()` / `.diagnosticText()`는 진단 전용이다. 결과/버퍼/주사 창/수신 상태는 detached JSON이다. 모든 APS 숫자는 SIM_TUNED와 기존 reference 체계를 유지한다.

재현 명령은 최종 증거·상태 문서의 고정 HTML 체크섬을 기준으로 실행한다. Actions는 수동 workflow만 제공하며 dispatch하지 않는다. 브랜치 원본 업로드 후 독립 GitHub decoded blob 대조로 게시를 확인한다.

```sh
node docs/helicopter/L/library.cjs
python docs/helicopter/L/build.py archive/v48/WIP_HELI_F2_0/Aegis_SIM_v48_WIP_HELI_F2_0.html /tmp/HELI_F2.html
python docs/helicopter/L/run_suite.py archive/v48/WIP_HELI_F2_0/Aegis_SIM_v48_WIP_HELI_F2_0.html Aegis_SIM_v48_WIP_HELI_F2.html artifacts
```

진단 그리드의300m 고도,0/45/90° aspect, Hs0.1/0.9/3m,15/40/90km, 선회1°/s도 `SIM_TUNED / GENERIC_RADAR_PRINCIPLE` 계산 조건이다. 라벨 canvas 픽셀/폰트 크기는 presentation-only이고 물리 수치가 아니다. 최종 검증: [verification-summary.json](evidence/verification-summary.json). 센서/물리용 HTML에 이 진단의 정답 라벨·정분류 결과가 역입력되는 경로는 없다.
