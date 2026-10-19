# 정보창 데이터 출처 감사

정보창은 `mapObservedObjectsA()` → 필드 화이트리스트 → `information(o)` 경로로만 만든다. 진실 엔티티/표적 프로파일/사후 교전 로그로 미관측 표적 정보를 보충하지 않는다. 읽기 전용 필터는 기존 트랙 표시 필터와 같되 EKF를 지연 초기화하지 않는다. 별도 연관 알고리즘도 추가하지 않는다.

| 출처 | 사용하는 값 | 경계 / 코드 |
|---|---|---|
| 자함 항법 | 자함 좌표·속력·침로, 함명/함번 | 자함 보유 정보. `observations.js:4` |
| `tracks` 관측 트랙 | 융합 추정 위치/고도·식별·품질·마지막 측정 나이·표시 번호 | `mapTrackVisibleA`, `mapTrackReadA`, `observations.js:6–15`. truthRef, truth id, `associationDomain` 읽지 않음 |
| `surfaceSensorContributorSnapshotWip13B9` | SPY/SPQ/항해 레이더의 기여 이름·나이·σ | 개별 원시 측정 위치는 보존되지 않으므로 융합 좌표를 센서별 측정으로 꾸미지 않음 |
| `observationReportsC` | Hawklink sourceId·sequence·측정/수신 시각 | 제공된 메타데이터만. `observations.js:9` |
| `isarEvidence`, `iffF`, `identificationEvidence` | 기존 후보/신뢰도·전장±σ·시각·제공자, IFF 응답, 기존 식별 근거 | 식별을 자동 변경하지 않음 |
| `esmContacts` | 방위·방위오차·대역·방사체 계열·신뢰도·나이 | `mapEsmReadA`, `observations.js:16`. x/y/z/range 없음. 거리 ‘알 수 없음’. 기존 동일 트랙 키일 때만 관측 트랙과 함께 표시 |
| `networkPictureG` | 이미 수신된 Link 16 위치 추정·identity·age·sources | `mapReceivedNetworkA`, `observations.js:21–24`. SELF 아군 표시와 기존 `localTrackId` 연관만 사용. 함대 truth 위치에 접근하지 않음 |
| 자함 AIR inventory + 소유 기체 항법 | 자함 헬기 id·위치·단계·속도·레이더 모드·경로 수 | `mapOwnHelosA`, `observations.js:17–20`. 소유자 확인 후 필드 투영. RF 센서/ISAR 내부 상태 전체 snapshot 복사 금지 |
| 자함 `missiles` / `ramMissiles` | 기존 MSL STATUS·지도에 쓰는 자함 무장 위치·단계·표적 트랙·수명 | `mapOwnMissilesA`, `observations.js:25–29`. 타함 소유 무장 제외. 제공되지 않은 남은 시간은 ‘알 수 없음’ |
| `harpoonRuntimeA().launches` | releaseStep·고정 memory.trackId·고정 routeProgram.pointsM | `mapLaunchReceiptsA`, `observations.js:7`. 자함 발사 영수증. 현재 위치·boosters·시커·INS·종료 truth 읽지 않음. 실제 위치 기반 하푼 아이콘 추가 없음 |
| `routePoints` / `routeDraft` | 자함 항해/발사 전 계획의 번호·좌표 | `mapRouteObjectsA`, `observations.js:30`. 계획 객체이며 탐지 표적이 아님 |

`ENGAGEMENT_RUNTIME` 직접 접근, 적 엔티티 lookup, truthRef/associationDomain, 적 형상 프로파일 접근은 정보창 소스에 없다. 테스트에서는 진실 참조·private association 필드와 자함 헬기 RF 내부를 getter로 막은 뒤 조회/메뉴를 실행했고 getter 읽기 0, 오류 0이었다. 진실을 사용하는 테스트 fixture 및 해시 검사는 제품 정보 경로와 분리되어 있다.

`MAP_A_LEGACY_CURSOR_BRIDGE`는 `observations.js:39–44`, 호출은 `map.js:20`이다. 위치 있는 TRACK/NET 조회 때 lockCursor x/y/nx/ny만 변경한다. selectedLockId·PD·레이더 모드·EMCON·발사는 변경하지 않는다. MAP_B에서 사격 지정 슬롯과 명시적 무장 명령이 연결되면 이 함수/호출을 제거하고, 조회 무명령 검수와 기존 LOCK 회귀를 다시 실행한다.

명령은 정보창/메뉴의 명시적 버튼에서만 기존 함수로 위임한다: 정밀추적 `lockByCursor(id)`, 식별 `setTrackOperatorIdentityA3`, 항해 `addWaypoint`/`undoLastWp`, 헬기 `heloCommandA`, ISAR `ISAR_TARGET`, 3D 기존 포커스 함수. 마지막 하푼 계획 취소만 작은 어댑터 `harpoonRouteUndoMapA`를 추가했으며 `routeDraft` 외에는 쓰지 않는다. 무장 발사 함수는 MAP_A 지도 입력에 연결하지 않는다.
