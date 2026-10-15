# HELI_D — 헬기 피탐·IFF·수상 레이더·Hawklink

기준은 HELI_C `370d924a7bba5fa739498b9cd9e220e07abde823`이다. 기존 120초 준비, 두 기의 갑판 대기열, 다중 경로·함선 추종, 25–3,962.4m 고도 조절, 로터·격납고·착륙장치 수정과 공통 압축 모델을 유지한다. [구현 전 계약 대조와 사용자 결정](CONFLICTS.md)을 우선한다.

## 조작과 정책

AIR에서 H1/H2를 선택해 **IFF ON/OFF**, **레이더 ON/OFF**를 각각 조작한다. 기본은 IFF ON / 레이더 OFF다. 목록에는 링크 연결 사유와 최근 10초간 전송 plot 수를 표시한다. 기존 고도·경로·출격/대기 취소 버튼은 그대로다. AIR에 헬기/모함 보기 버튼을 다시 넣지 않으며 3D CAMERA의 H1/H2 추적을 유지한다.

선택한 비행 헬기의 수상 탐지 수평선을 지도에 점선으로 표시한다. 이는 현재 고도와 SIM_TUNED 표적 마스트 높이에 따른 기하학적 범위이며 확정 탐지나 무장 사거리를 뜻하지 않는다. 3D CONTROLS → SENSORS → **HELO RADAR**는 방사 중인 헬기의 범위와 실제 주사 위상을 읽어 표시한다.

현재 EMCON은 레이더 방사 통제다. **Hawklink는 Link 16처럼 레이더 EMCON의 영향을 받지 않는다.** 통신 EMCON을 두 링크에 함께 적용하는 정책은 후속 단계다. Hawklink는 모함 장비 상태, 전파 수평선 LOS, 최대 거리로 연결을 결정한다. 레이더 OFF라도 링크는 연결될 수 있다.

## 단계별 경계

- A: 비행 단계만 공통 RF·CIWS 센서 입력에 등록한다. 갑판/격납 단계는 별도 반사체가 아니다. IFF는 잡음이 있는 거리·방위·고각을 관측 트랙에 연관해 유효기간이 있는 아군 증거를 붙인다. truth ID로 트랙을 찾거나 헬기라는 이유로 AUTO를 예외 처리하지 않는다. OFF/무응답은 UNKNOWN 등 기존 식별 규칙으로 돌아가며 곧바로 HOSTILE을 뜻하지 않는다. 기존 함정 IFF와 운용자의 별도 식별은 유지한다.
- B: [수상 탐색 레이더 계약](README_B.md). 기존 공통 RF/SNR·해면·기상 경로를 헬기 수신 위치에서 재사용한다. 360° 회전당 각 물리 반사체에 한 번 탐지를 시도한다. 잡음이 있는 측정과 SI 공분산만 출력하며 표적 ID·truth 참조·속도를 넘기지 않는다. APS-153급의 밴드·출력·거리·오차는 모두 SIM_TUNED 가정이며 실제 장비 성능으로 주장하지 않는다.
- C: [Hawklink 계약](README_C.md). 원래 모함의 H1/H2 offboard source로 익명 plot을 지연 전송한다. 단절 시 pending을 폐기하고 신규 plot도 버리며 재연결 때 재전송하지 않는다. 수신 함정의 일반 트랙은 기존 코스팅·소멸을 따른다. 순수 원격 관측만으로 무장을 발사할 수 없으며, 하푼의 기존 좌표 검색 발사는 유지한다. 전단 Link 16로 Hawklink 전용 트랙을 전달하는 기능은 추가하지 않는다.

모든 센서·링크 상태는 fixed60Hz 시뮬레이션이 소유한다. 렌더와 `window.__HELO__.snapshot()`은 읽기 전용이다. 저장 D1에는 IFF/레이더 설정만 추가하며 scan/RNG/IFF 이력/링크 queue·sequence는 저장하지 않는다. 구형 저장은 비행 상태를 유지하면서 IFF ON / 레이더 OFF로 migration한다.

이번 단계는 **식별과 교전 허용/차단 판정까지**다. 실제 헬기 피격·격추, FLIR/ISAR·ESM·소나·공중 탐색·무장·연료·회수·로터 공력은 후속 범위다. 현재 수상 탐색 모드는 측정 특성으로 공중/배경 반사를 걸러내며 truth 종류를 후단에 보내 완벽한 식별을 만들지 않는다.

## 검증과 재현

단계 A는 `856475f`에서 독립 고정했다. 동일 A 후보 SHA `8f524591e60852ff1b4b14e09b4d666a6372107527ab1ff9ee3597d0880c59bb`의 static46 + codec26 + runtime39 = **111/111 PASS**다. [A 게이트](evidence/stage-a/gate.json)는 당시 검증이며 최종 C 후보의 검사 수에 중복 합산하지 않는다. `build.py --phase A`는 이 커밋의 소스로 재현한다.

최종 원본과 최종 검사 수는 배포 시 `evidence/verification-summary.json`으로 고정한다. Chromium/SwiftShader와 desktop/touch viewport 검사는 실제 휴대폰 또는 hardware FPS 측정을 뜻하지 않는다.

```sh
npm ci --prefix docs/performance/F --ignore-scripts --no-audit --no-fund
pip install -r docs/helicopter/E/requirements.txt
python -m playwright install chromium
python docs/helicopter/E/build.py archive/v48/WIP_HELI_C/Aegis_SIM_v48_WIP_HELI_C.html /tmp/Aegis_SIM_v48_WIP_HELI_D.html --phase C
python docs/helicopter/E/run_suite.py static Aegis_SIM_v48_WIP_HELI_D.html /tmp/heli-d-static
python docs/helicopter/E/run_suite.py stage_a Aegis_SIM_v48_WIP_HELI_D.html /tmp/heli-d-a
python docs/helicopter/E/run_suite.py stage_b Aegis_SIM_v48_WIP_HELI_D.html /tmp/heli-d-b
python docs/helicopter/E/run_suite.py stage_c Aegis_SIM_v48_WIP_HELI_D.html /tmp/heli-d-c
python docs/helicopter/E/run_suite.py transport Aegis_SIM_v48_WIP_HELI_D.html /tmp/heli-d-transport
python docs/helicopter/E/run_suite.py codec Aegis_SIM_v48_WIP_HELI_D.html /tmp/heli-d-codec
python docs/helicopter/E/run_suite.py ui Aegis_SIM_v48_WIP_HELI_D.html /tmp/heli-d-ui
python docs/helicopter/E/run_suite.py visual Aegis_SIM_v48_WIP_HELI_D.html /tmp/heli-d-visual
python docs/helicopter/E/run_suite.py regression Aegis_SIM_v48_WIP_HELI_D.html /tmp/heli-d-regression
```

기존 SH-60 자산과 [CC BY4.0 attribution](../A/ATTRIBUTION.md)을 재사용한다. 원본 HTML 전체를 `helicopter-sensors`에 직접 업로드하고 독립 GitHub blob readback으로 확인한다. 이전 C 네 파일은 같은 bytes/blob으로 archive하며 stable v48과 이전 source/evidence는 보존한다. Actions는 실행하지 않고 수동 workflow만 준비한다. main/선행 브랜치 병합이나 새 PR 생성은 하지 않는다.
