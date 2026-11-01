# TRACK-B/C/D 설계와 예상 위험 — 구현하지 않음

상태: **DESIGN_ONLY**. Baseline Audit와 TRACK-A의 실제 동작 동등성·비누수·성능 검증이 끝나기 전에 아래 기능을 소비자에 연결하지 않는다. PR/병합/release/tag도 현재 승인 범위가 아니다. 이 문서는 새로운 OODA·전술 점수·AI 성향 설계가 아니다.

## TRACK-B: 차원에 맞는 연관을 shadow로 비교

1. 먼저 현재 `trackRadarAssociationNisV31`, surface NIS, NPC greedy, C55 file, Hawklink Cartesian NIS, network estimate NIS의 실제 후보/반환값을 A trace에 모은다. filter를 추가 호출해 후보를 재계산하지 않는다.
2. 공유 가능한 부분은 **입력 시각 정렬·측정 차원·출처·상관 여부 표시**와 후보 평가 결과 구조다. TrackStore/RNG/FCS 소유권은 통합하지 않는다.
3. ownship/NPC의 가장 작은 범위에서 crossing fixture를 만들고 기존 판정/개선 후보를 shadow comparison한다. 기존 NIS와 RF 계수는 유지하며 후보가 여러 개면 임의 병합보다 보류/tentative를 우선 검토한다. 일대일 할당의 실제 채택은 단일 경로별 회귀 후에만 한다.
4. 2D-only→3D와 3D→2D는 단순 `AIR` 분류값이 아니라 관측 가능한 차원과 prior를 구분해야 한다. 수면 prior 해제/적용은 수치 변경 여부를 따로 검토한다. 기존 성능·게이트 임계값을 일괄 완화하지 않는다.
5. C55 own-fire partition은 유지한 채 교차·동일거리·서로 다른 도플러·재획득을 시험한다. native 자함/NPC 두 문맥에서 incoming ASM의 보호 오염 0을 확인한다. 419025는 “사격이 늘어났으니 정당함”만으로 통과시키지 않는다.

주요 위험: 공분산 증가가 먼 접촉을 끌어오는 false merge, 낮은 Doppler를 SURFACE로 단정, class를 identity로 혼동, 동시 후보 greedy ID swap, 다른 owner를 같은 필터에 쓰는 상태 누수, 동일 source 보고의 이중 confirmation. APS의 동일-turn row 처리와 offboard sequential receipt에는 특히 추가 one-to-one 검증이 필요하다.

예상 규모: 공유 관측/candidate utility와 경로별 adapter 및 시험으로 나눠야 한다. 먼저 ownship/NPC 한 쌍, 이후 C55/Hawklink, 마지막 network 순서의 독립 커밋이 적절하다. 대형 MHT/JPDA나 전체 tracker 교체는 범위 밖이다.

종료 기준: 세 기존 자연 RF 재현·정당한 재획득·분리된 다표적·모호성·C55 보호를 동시에 통과. 도메인/실제 전투 차이마다 원인이 남고 무방비 전환/새 전투 손실이 있으면 FAIL 또는 미해결로 유지한다.

## TRACK-C: 수명과 식별 근거의 분리

1. 기존 `sensorAge`, `_lastMeasurementStep`, local/offboard provenance, TTL와 FIRM/COAST/MEMORY/REACQUIRE/DROP를 합쳐 설명하는 **detached view**부터 작성한다. 제2 lifecycle/제2 mutable track manager를 만들지 않는다.
2. 독립 hit·마지막 실제 fix·출처별 나이·3D 관측 유효기간·prior·alias/재획득 사유를 기록한다. 재전송과 새 측정의 구분은 source/sequence뿐 아니라 실제 measurement timestamp/lineage를 검토하되 기존 저장 스키마를 함부로 바꾸지 않는다.
3. identity, classification, threatStatus, authority, ownFireEvidence와 IFF는 각각 근거/시각/expiry/승계 규칙을 문서화한다. 새 file ID에 기존 FRIEND를 그대로 복사하거나 IFF 만료를 operator HOSTILE로 자동 바꾸지 않는다.
4. 수상함 IFF가 `_operatorIdentity='FRIEND'`에 남는 기존 동작과 헬기 AIR_IFF_E 만료 동작은 사용자 결정이 필요한 정책 차이다. 기존 아군 보호를 임의로 삭제하지 않는다.
5. false alarm, duplicate, false merge, ID swap, 정상 재획득을 별개 사후 진단 유형으로 집계한다. truth 판정은 fixture/after-action 전용이며 live consumer에는 전달하지 않는다.

주요 위험: 상태명의 형식 통일이 기존 ROE·UI·FCS를 바꾸는 것, ISAR가 contact hit를 freshen하는 것, 재획득에 보호를 무조건 승계하는 것, 시간이 되돌아간 load/reset에서 과거 evidence가 살아남는 것. 독립적 read-only 조회가 lazy initializer를 호출하는 부작용도 막아야 한다.

종료 기준: 수명·근거·재획득 계보 fixture와 IFF/neutral/ROE/수동 명령 회귀. 기존 releaseApproved=false나 사용자 미승인 기대값은 이 단계에서 자동 정리하지 않는다.

## TRACK-D: 함별 소비자와 네트워크 최종 연결

1. Hawklink PLOT 무버퍼/원 시각/지연·P 확대, ISAR 결과만 제한 buffer, ESM bearing-only를 각각 유지한다. Hawklink의 위치는 observed polar에서 계산된 reported position이며 무관측 고도를 측정처럼 설명하지 않는다.
2. 네트워크의 separate receiver files, NIS36+거리/속도 sanity, fixed 0.5 CI, fresh/coast, packet/measurement replay 차이를 유지한다. sender의 EKF estimate를 독립 원시 6D 측정으로 바꾸지 않는다.
3. 원정보 lineage/다른 sender를 경유한 순환의 상관을 진단한다. CI가 있다는 사실만으로 전체 순환 비과신을 증명한 것으로 간주하지 않는다. 원격 file은 표시/보호·협동 배분 자료이고 local FCS/기존 동의를 대신하지 않는다.
4. H1~H4/CIC/MAP/FCS에 freshness/불확실성/provenance를 복사본으로 읽게 하는 adapter를 단계별 연결한다. AI 점수·성향·적성 정책·OODA는 추가하지 않는다.
5. superseded 필드는 실제 사용자 목록과 회귀를 확인한 뒤에만 제거한다. 과거 모듈 원본을 packed live 코드에 통째로 덮어쓰지 않는다.

주요 위험: report 순환으로 local hit로 위장, network SELF와 target truth 혼동, 원격 FRIEND 보호가 위치 오연관으로 다른 적 탄에 전파, remote-only에서 CEC/발사권한으로 승격, 공용 알고리즘 때문에 함별 RNG/필터 상태 공유, UI 렌더가 lazy init/consumer state를 쓰는 것.

종료 기준: A~C 전체와 네트워크/Hawklink/ESM/IFF/ISAR·모든 소비자·UI·저장·배속·owner당 tick·CPU/할당 회귀. 419025, paired observer 차이, 기존 미완료 UI가 남으면 이름 그대로 공개하고 최종 CLOSED 또는 all-green 선언을 하지 않는다.
