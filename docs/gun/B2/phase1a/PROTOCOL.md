# 시험 규약

- 모든 미사일·함포 수치는 게임용 SIM_TUNED다. 실제 무기 성능과 비교하지 않는다.
- 전체 벽시계 상한3시간. TASK_CLOCK.json은 검토 시작을 보수적으로 포함한다. 브라우저 동시 최대2, 자원 실패 재시도0.
- 원점·센서·비행·신관·피해를 별도 근사 모델로 대체하지 않고 실제 선택 HTML의 native함수를 실행한다. 측정 함수.toString SHA와 빌드지문을 확인한다.
- 산포: native16459m 무풍400발, 같은seed/serial400반복, 공칭823·MV/elevσ고정. globalRNG소비0, native착탄동등성0m.
- 단발: DDG/CG×0/90°×1~9km×592001~59204040시드=1440시도. 이상 지속 관측, Kh35U10m/280m/s, native발사/탄도/신호누적/신관/파편/Pk. CG정면1km40건 사계 미발사를 비명중으로 넣지 않는다.
- G7: DDG/CG×0/90°×1·4기×419010~41902415시드, AutoAA ON120회. 새page/context마다 자연RF+전체fixed tick1/60. B2기능은모두ON. 물리ASM 참조의 실제결과/첫3km진입/사망tick만 실적에 쓴다. legacy 혼입카운터는 보존만한다.
- G7 OFF120 및 지정 외회귀는 TEST_REUSE.json의 sourceguard 아래 Phase1 원본을 재사용한다. 새ON120과 같은B2ON120은 동일입력으로비교한다. 전부새실행으로표기하지않는다.
- 수상: DDG/CG×5/10/15km×723001~72301515시드 ON90회. 첫발명중과전체fixture PASS를구분하고 meaningfulMovingFrame 기대를바꾸지않는다.
- 단언: 사용자§5의12/2/5/1/4개범위만교체한다. 4개CG단발은그대로다. fixture의 누락RF메타데이터는 기존native .06을보충하고 productRF계수는유지한다. 실제MISS가나온 하푼2개단언은미통과로남기며다른seed/통과거리를고르지않는다.
- CIWS 이상은참고통계만기록한다. main/release/tag는변경하지않는다.
