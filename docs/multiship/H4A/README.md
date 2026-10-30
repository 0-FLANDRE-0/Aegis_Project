# H4A — 센서 기반 근접 자위 연결 보완

H4에서 새 출항한 CG-52가 5m급 하푼에 눌카만 쓰던 대응 연결을 수정한다. 레이더 반사·탐색·확률·CMS 분류·하푼/탄환 비행 및 피해 solver는 바꾸지 않는다.

- 기존 CMS 승인 + 자체 RF 확인 경로를 유지한다. CMS가 관측을 확보하지 못한 경우에도 CIWS의 확인된 fresh local RF, 연속 접근, 미사일 운동학, 예상 자함 통과 경로, 품질·설치·전원·사각·구동·탄약 조건을 통과하면 `LOCAL_SELF_DEFENCE_H4A` 권한을 만든다. UNKNOWN CMS를 HOSTILE로 쓰지 않으며 원거리 SAM 권한을 새로 부여하지 않는다.
- 실제 발사는 현재 owner/mount/pending 객체와 동일한 sensor file 객체를 다시 확인한다. 아군·중립·자함 발사 근거, 효과/BDA 보호, coast/오래된 측정, unconfirmed, HOLD, EMCON, 손상·잠김·전원 중단은 차단한다. 일반 자동 명령에 이 권한을 개방하지 않는다.
- EW는 읽기 전용 local RF의 거리·접근·오차와 passive ACTIVE_SEEKER 방위를 유일하게 연관한 경우만 채프 판단에 쓴다. 같은 mount의 여러 파일·다대일 연관·여러 emitter는 모호하면 보류한다. ESM 방위만으로 거리/TTC를 만들지 않는다. 기존 살보 간격·예비탄·재살보 상한·SLQ-32/눌카·발사 geometry 정책을 유지한다.
- CG는 양현 20mm Phalanx만 사용한다. DDG 장비와 자함 CIWS 커널은 그대로다. 하푼 무DL/INS/ARH, H4 팀·H3 공격·H2 기동·H1 유틸리티와 기존 저장 schema를 유지한다. 새 pending/local 파일은 기존 transient 수명주기를 따른다.

`build.py`는 H4 SHA를 pin하고 record13만 교체한다. `verify_static.py`는 exact rebuild, 전체 packed record, 모델·불변 커널·scope/문법·truth 경계를 검사한다. `verify_harpoon.py`는 fresh departure/실제 manual Harpoon/자연 센서/실탄·실제 파괴를 검사한다. `probe.js`는 DIAGNOSTIC_ONLY이며 자연 획득 pending의 진단 발사 phase를 맞추고 baseline admission을 먼저 확인한 뒤, 늦은 무효화의 각각 다른 차단 사유와 실제 발사의 탄약·탄체·RNG 변화 0을 확인한다. `verify_clock.py`는 같은 물리·sensor/EW·무장 상태와 RNG를 실제 accumulator의 1/8/16/64배속에서 비교한다.

`regression_closein.py`는 기존 E close-in fixture를 EW·기동 OFF에서 격리해 hard-kill mechanics를 검사한다. 원래 E fixture는 untouched H4에서도 CG actual-fire assertion이 실패한다. 동시에 운용되는 EW로 위협 궤적이 바뀌는 경우에는 탄약 소모를 강요하지 않는다. 원래 source/evidence는 변경하지 않는다. 기본 동시 방어는 새 자연 하푼 및 기존 natural-ew suite로 별도 검사한다.

재현:

```sh
npm ci --prefix docs/multiship/H4A --ignore-scripts --no-audit --no-fund
python docs/multiship/H4A/build.py archive/v48/WIP_MULTI_SHIP_H4/Aegis_SIM_v48_WIP_MULTI_SHIP_H4.html candidate.html
python docs/multiship/H4A/verify_static.py archive/v48/WIP_MULTI_SHIP_H4/Aegis_SIM_v48_WIP_MULTI_SHIP_H4.html candidate.html artifacts/static
AEGIS_CHROMIUM_EXECUTABLE=/path/to/chromium python docs/multiship/H4A/run_suite.py harpoon-defense candidate.html artifacts/harpoon-defense
```

최종 원본별 검증 집계는 `evidence/verification-summary.json`을 따른다. seed/해역/지형 bypass/SwiftShader 대표 조건이며 실장비 성능·보편적 요격률·사용자 하드웨어 FPS 인증이 아니다. 낮은 높이 접촉의 CMS 획득 실패가 항상 해결된 것으로 주장하지 않는다. 독립 local RF의 관측 거리와 사각 밖은 기존 제약을 유지한다.
