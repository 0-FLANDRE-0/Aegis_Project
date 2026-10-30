# AEGIS v48 WIP HELI_F2_0 — EMCON 방사 없는 수동 지정 (0번 단독 보고)

CG_B `273c36f` 위 `helicopter-emcon-f2-0`, 소스 `83e76b0`. [대조](docs/helicopter/K/CONFLICTS.md), [운용·재현](docs/helicopter/K/README.md), [검증](docs/helicopter/K/evidence/verification-summary.json), [원격 확인](docs/helicopter/K/remote-publication.json).

원본 **16,081,768bytes**, CG_B 대비 **1,788bytes 증가**. HTML SHA-256 `abb0423050d974d878714510cf5356ad9913b4371d04ccc757602782e8d74b86`. packed13 `b197079270bb0a47a2d002b01b12ca04086cb4e8d8da355f0999ad68aabba314`. 그 외13자산과 과거 A–J/stable은 그대로다.

## 0번 결과

ARM LOCK은 EMCON 중에도 표시 가능한 수신 트랙을 지정한다. SPY 섹터 제한은 이 수동 지정에만 제외하고, mode=TWS/pdTracking=false/`지정 (EMCON · 방사 없음)`을 유지한다. EMCON ON은 PD만 종료하고 지정을 남기며 이전 AUTO/SEMI lock 소유권을 해제해 자동 취소가 운용자 지정을 지우지 않게 했다. OFF는 표시 트랙이 기존 SPY 섹터 안이면 PD, 밖이면 지정만 유지한다. 버튼/network group/진단 setter에 같은 전환을 적용하고 fixed updateRadar도 silent PD가 남지 않게 한다. MODE 버튼은 EMCON 중 PD를 시작하지 않는다.

지정 직후 기존 하푼 UI를 갱신해 이전 NO_TRACK 표시를 제거한다. F1의 수동 권한·식별·나이10초·예측 바스켓·사거리·손상·장비·좌표/경로 관문은 그대로다. EMCON을 이유로 한 새 하푼 허가/차단 조건은 없다. VLS/3D AUTO LOCK/AUTO TGT/3D 발사 버튼·SPG 조사·AUTO EMCON 차단은 유지하고 native SM2 AUTO_RADIATE/ESSM BLOCK_FIRE 정책 자체도 바꾸지 않는다. Hawklink/Link16은 EMCON 독립이다.

로그에 launchEmcon:boolean을 추가했다. 요청 시점이 아닌 최종 재검사/탄약 커밋 시점의 해당 함 EMCON이다. foreign owner도 그 함의 상태를 읽는다. DEBUG 복사 텍스트에도 표시하며64건/종료 AFTER_ACTION_TRUTH/전술·센서·AI의 로그 읽기 금지/발사 후 무DL은 같다. 저장 schema와 헬기·함선 형상은 변경하지 않는다.

## 검증

최종 동일 원본 **124/124 PASS /4 suites**, page errors0. static41/native27/UI14/기존 전투42.

- 실제 CG H1이300m PERI로40km 표적을 측정해 모함 Hawklink로 만든 순수 OFFBOARD 트랙을 ARM 포인터로 지정했다. 자함 SPY 물리 방사원0/빔 usedMs0/priorityUsedMs0/pdTracking=false를 확인한 뒤 실제 하푼을 발사해 OPERATOR_ONLY/launchEmcon=true/noDL을 기록했다.
-8km/450km 익명 보고에서 EMCON 수동 지정 허용, OFF의 기존 섹터 검사, ON의 PD 종료·지정 유지, AUTO의 수동 지정 보존/자동발사0을 확인했다.450km는 진단 전용 입력이며 실제 Hawklink 운용 범위가 아니다.
-390×1000/1100×800에서 실제 LOCK·AUTO TGT·VLS 버튼과3D guard를 확인했다. 요청은 EMCON ON에서 하고 실제 커밋 전에 OFF로 바꾼 경우 launchEmcon=false였다. 방사 없는 LOCK 레이블은 viewport 안에 표시된다.
- DDG/CG 대기·8Kh32 AUTO·손상6조건의 기존 물리·피해·배치·RNG·observer·offboard 상태가 CG_B와 같다. 소프트웨어 Chromium이며 실제 기기 FPS는 주장하지 않는다.

**요청 순서에 따라0번을 별도 완료/보고한다. ISAR1번 이후는 이 HTML에 없다.** 다음 버전에서 예약 ISAR 활성화와 판독 결과 전용 버퍼를 구현한다. plot 무버퍼/식별 자동 변경 금지/EMCON 통신 독립 정책을 유지한다.

CG_B 네 파일은 archive/v48/WIP_HELI_CG_B에 동일 bytes/blob으로 보존한다. 원본 전체 직접 업로드와 독립 decoded blob 대조를 한다. Actions dispatch/main·이전 브랜치 병합/새 PR은 하지 않는다.
