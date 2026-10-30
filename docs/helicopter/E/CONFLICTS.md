# 구현 전 계약 대조와 사용자 결정

2026-10-15, HELI_C `370d924a7bba5fa739498b9cd9e220e07abde823` / SHA `65c1f2ec7deb4bc4740a0477754edd210a6c09bacbefad41e93a3ae9675e6ff6` 기준. A 실행 코드 작성 전에 아래1–4를 대화로 보고했으며 사용자가1·2·4를 승인하고3을 수정했다.

1. `spq9bSurfaceAttemptWip13B1(obj)`는 legacy 경로다. 기존 공통 RF 장면→측정 잡음→익명 echo/plot 계약을 우선한다. SPQ 수상 SNR·해면·기상 모델을 공통 수신기 상대 경로에서 재사용한다. truth 종류·ID를 후단 분류에 전달하지 않는다.
2. 기존 IFF는 수상함 전용이며 영구 FRIEND 표식을 사용한다. 기존 함정 동작은 유지하고 새 AIR IFF에만 재인증·만료를 적용한다. IFF 증거와 운용자의 독립 식별을 분리한다. OFF/무응답이 HOSTILE을 뜻하지 않으며 UNKNOWN 자동발사 금지 ROE는 유지한다.
3. **사용자 최종 변경: 현재 EMCON은 레이더 방사 통제다. Hawklink도 기존 Link16처럼 EMCON 영향을 받지 않는다.** 기존 요청의 EMCON 단절 시나리오는 LOS 밖/최대거리 초과로 대체한다. 통신 EMCON은 Link16·Hawklink에 함께 적용할 후속 항목으로 남긴다. IFF interrogator 등 기존 레이더/식별 동작은 이 통신 정책 변경으로 확장하지 않는다.
4. 기존 offboard-only 트랙은 FLEET/SAM 경로에서 보호되지만 ARM 하푼 직접 트랙 발사에는 현지 관측 조건이 빠졌다. 새 연결로 의도하지 않은 OTH 발사가 열리지 않도록 실제 트랙 기반 발사 게이트에서 현지 관측을 재검사한다. 기존 좌표 지정 검색 발사는 보존한다.

이전 HELI_A~C의 센서·IFF·offboard 제외는 당시 범위다. 이번 A→B→C에서 명시적으로 연결한다. HELI_C의25–3962.4m 고도/50m 기본값,120초 출격, 경로·함선 추종, AIR 배치/단일 출격·취소, AIR 보기 삭제/CAMERA 추적 유지, 로터·격납고·바퀴 수정은 유지한다.

추가 범위 확인에 사용자가 답했다: **이번에는 식별·교전 허용/차단 판정까지 검증하고, 실제 헬기 피격·격추는 후속 단계**다. 피탐 등록만으로 헬기 파괴 물리를 구현했다고 보고하지 않는다.

실제 포트 서명은 `configureOffboardSourceC(motherRuntime,config)` / `ingestOffboardReportC(motherRuntime,report)`다. H1/H2 ID는 수신 함정별 소유다. 기존 익명7필드 스키마, 공분산·나이·재전송 검증, 단절 시 pending queue 폐기를 유지한다. 링크 평가를 queue drain보다 먼저 수행한다.

공중 표적 탐색 모드는 추가하지 않는다. 공통 RF 물리 장면에는 물체 반사가 함께 존재하지만 APS의 출력 채널은 수상 관측 전용이다. 모호한 물리 반사를 truth 종류로 지워 완벽한 식별을 만들지 않는다. 기존 함정 로컬 트랙의 Link16 처리는 그대로이며, Hawklink 전용 관측의 전단 공유 기능은 추가하지 않는다.
