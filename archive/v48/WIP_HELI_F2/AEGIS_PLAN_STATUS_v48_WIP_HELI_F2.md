# AEGIS v48_WIP_HELI_F2 — EMCON 수동 지정 + APS-153 ISAR

0번 `helicopter-emcon-f2-0` `1b26a0f`을 별도 완료/124개 검사/원격 원본 확인/사용자 보고한 뒤, `helicopter-isar-f2`에서1번 이후를 구현했다. 소스 `aa9dcf3`. [우선순위·범위](docs/helicopter/L/CONFLICTS.md), [운용·재현](docs/helicopter/L/README.md), [검증](docs/helicopter/L/evidence/verification-summary.json), [원격 원본 확인](docs/helicopter/L/remote-publication.json).

원본 **16,099,946bytes**,0번 대비 **18,178bytes 증가**. SHA256 `100b12c24355666627c76f7e79c88b98a1a7a963e9bb777ea8f9f7e9c908bb94`. packed13 `de52c3cc2b45742617318071f47128148271a3ff457d6a87ce27f3d1e4703a8d`. 나머지13자산/모델, DDG/CG 시설·120초 출격·기존 운동·고도/IFF/탐색·Hawklink/Link16/F1 발사 정책은 그대로다.

## 결과

AIR [ISAR] → 지도 수상 트랙 탭. 기체의 자기 익명 접촉을 위치/방위 게이트로 고르고, 고정 방위·0rpm·9.3–296km 경사거리/수평선/SNR 조건으로16초 적분한다. 탐색과 M-of-N 창을 멈추고, 종료/취소 후 직전 모드로 돌아가 한 주사 전환 공백을 둔다. 링크와 독립된 운용이다.

물리 프런트엔드만 형상/실제 자세·침로와 미구현 해상 각운동 추정을 사용한다. 공통 RF 에코 뒤에는 잡음 측정 특징/공분산만 있다. λ/(2Δθ)·SNR·완료도/유효 표본이 품질과 오차를 결정한다. DDG/CG/대형 상선의 기존 기하에서 오프라인 추출한 라이브러리와 측정 전장±σ/상부구조 높이/마스트 위치를 비교한다. 표적 profileId/entity id로 정답을 고르지 않는다. 모든 숫자는 SIM_TUNED와 기존 reference 체계다.

새 strict `AEGIS_OFFBOARD_ISAR_C_1`은 위치/공분산/후보·신뢰도/특징/원래 시각/source만 전송한다. 판독 결과만 기체8개 버퍼 예외, 모함 큐/자료 각16개·최대600초. 단절 복구/트랙 소멸 뒤에도 원래 시각과 위치 게이트를 쓰며 identity/authority는 넘기지 않는다. radar plot 무버퍼/64개 포트/나이 규칙은 같다.

ISAR 수신은 identity/sensorAge/hits/confirmed를 바꾸지 않는다. 운용자가 식별할 때만 ISAR 후보·신뢰도·시각·경과시간을 근거로 복사하고, 발사 로그에 그 판단과 launchEmcon을 고정한다. 없으면 기존 OPERATOR_ONLY/LOCAL_SENSOR다. 발사 후 무DL, 종료만 AFTER_ACTION_TRUTH다. ISAR 뒤 탐색 보고가 늦으면 기존 하푼10초/바스켓 검사를 그대로 통과해야 한다.

AIR 진행/품질/결과/취소, 지도/트랙 정보 ISAR·경과시간,3D 고정 빔·잔상 없음·ISAR 라벨, DEBUG 복사 가능한162조건 판별표를 제공한다. 진단/렌더가 실시간 시뮬 상태나 난수를 바꾸지 않는다. 작전 저장은 진행 중 ISAR 대신 직전 탐색 모드 설정만 저장하며 전투 transient는 복원하지 않는다.

## 검증

최종 동일 원본/정확 재빌드 소스 기준 **227/227 PASS /8 suites**, 브라우저 오류0: 정적43/순수 모델·포트21/CG 전체 흐름36/실제 DDG·CG RF8/모바일·3D38/배율12/기존 EMCON27/기존 전투42.

- 실제 CG H1의120초 출격/300m → LONG40km → ISAR → 운용자 HOSTILE → ARM 무방사 지정 → 하푼 → 중립 상선 실제 피격. 로그 ISAR·launchEmcon=true·AFTER_ACTION_TRUTH/NEUTRAL_MERCHANT. ISAR 없이 OPERATOR_ONLY로 발사하는 기존 경로도 같은 HTML에서 확인.
- ISAR 중 주사 mask/turn 유지·다른 함 트랙 코스팅·고정 방위·복귀 전환, UNKNOWN 자동 변경 없음, 새 트랙에 자료 위치 재연결. 유효 탐색 갱신 후 발사 관문 통과.
- 실제 LOS 밖150km/최대거리 밖200km의 명시적 물리 포즈 fixture에서 모드/적분 가능, 결과 버퍼, 복구 후 원래 시각 전송, plot 버퍼0.
- 실제 재사용 DDG/CG 물리 형상에서 익명 RF→측정→함급 후보 확인. 초기3종(상선 포함) 및0/45/90°·해상3조건·거리3조건·직진/선회162행 진단. 실제 장비 판별 성능으로 주장하지 않는다.
-1100×800/390×1000 포인터 모드/지도 지정/취소/복사·스크롤/레이아웃, 소프트웨어 WebGL 고정 쐐기/라벨/수평선·계기링/상태 불변/texture 해제.
-1×/8×/16×/64× 각1024 fixed ticks에서 기체/레이더/ISAR/RNG 동일. DDG/CG 대기·8Kh32 AUTO·손상6조건의 기존 물리/피해/배치/전투 RNG/observer/offboard 상태가0번과 동일.

직전0번 네 파일은 archive/v48/WIP_HELI_F2_0에 byte-identical 보존한다. 과거 A–K와 stable을 유지한다. 원본 전체 직접 업로드 후 독립 GitHub decoded blob 대조. Actions dispatch/main·이전 브랜치 병합/새 PR 없음.
