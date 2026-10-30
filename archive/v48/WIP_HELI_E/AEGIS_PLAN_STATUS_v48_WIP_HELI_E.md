# AEGIS v48 WIP HELI_E — AN/APS-153(V)

구현·런타임·브라우저 회귀를 완료했다. 기준은 HELI_D `e64f7af233897aa01e0bb7541c7cce88101b2638`, 작업 브랜치는 `helicopter-radar-e`, 구현 소스는 `5702606`이다. [조작·계산·재현](docs/helicopter/F/README.md), [구현 전 계약 대조](docs/helicopter/F/CONFLICTS.md), [최종 검증](docs/helicopter/F/evidence/verification-summary.json), [원격 원본 확인 기록](docs/helicopter/F/remote-publication.json)을 함께 따른다.

- 원본: **16,071,945bytes**, D 대비 **12,992bytes (+0.08090%)** 증가.
- HTML SHA-256: `e34cb884f375600a1c5bb3b0441bb89a385075f4167cfad04242594e26df9bcb`.
- packed13 SHA-256: `2309efad20a0a22d8a24cdcc22c1b774fd0bbe966144620ee8262a2fe8872706`.
- 나머지13개 packed 자산, 기존 항공 모델·rig와 질점 비행 수학은 동일하다.

## 구현

AIR에서 기체별 STBY/LONG/SHORT/PERI를 선택한다. 모드 전환 후 새 모드 한 회전 동안 데이터가 없다. 2.1° 방위 빔의 틱 내 통과 적분, 8°/csc² 고각, 40° 직하 사각, ±30° 안정화와 자동 틸트를 사용한다. 공통 RF·R⁻⁴·기상·해면 셀·CFAR를 유지하고 기존 별도 해면 scalar 감쇠를 제거했다. 모든 APS-153 수치는 SIM_TUNED이며 참고 출처를 구분한다.

단일 주사 검출 뒤 PERI4-of-9, LONG/SHORT2-of-3을 한 번 적용한다. 여러 회전의 에너지 적분은 없다. 마지막 주사가 miss여도 완성된 창에서 충분히 검출됐으면 확정한다. 잡음 측정·SI3×3 공분산·분해능 병합·기하 연관을 사용하며 후단에 표적 ID/truth를 넘기지 않는다. 접촉200개, 제한된 후보 수와 회전별 만료·공간 인덱스를 사용한다. 이동하는 헬기의 게이트 기준도 회전마다 갱신한다.

Hawklink는 확정 접촉의 실제 측정 시각·위치·공분산·도메인 증거만 기존 스키마로 전송한다. 두 기의 동일 할당량과 queue 보호를 적용하고 초과·단절 보고는 버린다. 재전송은 없다. D1 저장의 radarOn OFF→STBY, ON→LONG으로 옮기며 비행 필드는 보존하고 센서 transient는 초기화한다.

실제 RF 수평선은 반사체/함정 프로파일 높이를 사용한다. AIR와 지도·3D는 표적 기준높이30m의 기하상한을 표시하고 SNR 한계와 구별한다. 자체 RCS는 관측 방향에 따라 정면3m²→측면8m²다. 지도에는 계기 실선·수평선 점선·PERI 최소거리 원, 3D SENSORS의 **AN/APS-153**에는 별도 링·직하 사각·쐐기·잔상·고각 띠를 표시한다. DEBUG 성능표는 복사할 수 있다. 렌더와 진단은 시뮬 상태·전투 RNG를 바꾸지 않는다.

## 검증

같은 최종 HTML **355/355 PASS /9 suites**, 브라우저 오류0건이다. static39 / model25 / transport9 / native28 / IFF39 / policy42 / regression56 / UI100 / visual17이며 이전 D414와 중간 후보 검사는 합산하지 않는다.

앵커는 고도152m / 표적1m²·높이1m / 35km / Hs0.9m다. 실제 공통 RF·접촉 처리에서 완전한9주사 창5,000개를 시험한 최종 확정률은 **50.12%**다. 목표는 창 하나에서50%이며 장기간의 eventual acquisition이 아니다. 진단 수식의 Pd50 거리는35.000km다.

확정 후 신규 허위 접촉을 세는 모드별8시간 수치 가속 시험은 LONG9회 / SHORT11회 / PERI6회, 즉 **1.125 / 1.375 / 0.750회/시간**이다. 전체 월드8시간 실시간 플레이나 실장비 성능 시험은 아니다. 모든 이진 창, 마지막 miss, 병합/분리, 접촉200개와 이동 기준 좌표를 검사했다. 두 기×200접촉의 포트 stress에서는 REPORT_QUEUE_FULL0, queue peak48, 양쪽1942전송과 전체 접촉의 순환 표본을 확인했다.

DDG-119/CG-52의 대기·8발Kh-32 AUTO·피격6조건에서 기존 상태/RNG/포트가 D와 일치했다. 두 헬기의 실제 준비·비행·레이더·IFF·Hawklink를 돌린1/8/16/64×의 동일 fixed tick 결과도 일치했다. 기존 IFF·레이더 EMCON과 링크 독립·LOS/최대거리 단절·coast·공유 전용 발사 금지·현지 관측 및 좌표 하푼을 회귀 검사했다.

PC1000×760 / touch390×844, native Three/SwiftShader에서 UI와 렌더 읽기 전용·자원 재사용·일회 폐기를 확인했다. 실제 휴대폰/하드웨어 FPS는 측정하지 않았다. 큰 JSON 증거는 lossless gzip으로 보존한다.

## 보존과 다음 단계

120초 준비, 두 기 갑판 대기열, 로터·문·착륙장치, 다중 경로·급선회·추종,25–3962.4m 고도, CAMERA와 기존 함정 피해·물리·무장을 유지한다. IFF와 공유 전용 발사 금지, 레이더 EMCON과 Hawklink 독립 정책도 유지한다.

실제 헬기 피격·격추, 회수·무장·연료·로터 공력, FLIR/ISAR/ARPDD/ESM/재밍/공중탐색/Link16 확대는 후속이다. 다음은 헬기 센서 기반 OTH 표적지시·공유 정책을 별도로 결정하는 단계다.

D 네 파일은 `archive/v48/WIP_HELI_D/`에 동일 bytes/blob으로 보존한다. stable v48와 이전 A–E 소스·자산·증거는 변경하지 않는다. §7.1에 따라 원본 전체를 작업 브랜치에 올리고 GitHub blob을 독립 readback한다. Actions는 실행하지 않으며 수동 workflow만 준비한다. main/이전 브랜치 병합·새 PR 생성은 하지 않는다.
