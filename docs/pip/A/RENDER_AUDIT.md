# drawRadar 부작용 및 정보 출처 감사

## 공통 경로

`pipPrepareChartFrameA()`가 기존 메인 프레임당 한 번의 표시 유지 작업을 수행하고 관측 트랙·자함 장비·알려진 해도 데이터를 명시적 필드 목록으로 복사한다. `drawRadar(view)`는 `{context, rect, km, center}`를 받아 같은 픽셀 그리기를 실행한다. 기존 함수들이 사용하는 `ctx/mapZoom/tacticalViewKm/camOffset`은 동기 호출 안에서만 임시 바인딩하며 `finally`로 복구한다. `worldToScreen/screenToWorld`는 이 뷰를 사용하고 입력에는 명시적 뷰를 전달한다.

메인 RAF는 준비 1회 후 2D가 주화면일 때만 메인 지도를 그린다. 3D가 주화면일 때 숨겨진 메인 2D 픽셀 그리기는 0회다. PiP는 기본 유휴 4Hz, 입력/선택 변경 다음 프레임부터 1초간 프레임별 갱신이다. 기존 `drawAuxCic(st)` 간이 지도는 원문을 남기고 `DEAD_LEGACY` 조기 반환으로 비활성화했다.

## 원본 그리기에서 발견한 변경 경로 전수 분류

| 원본 경로 | 변경 내용 | 처리 |
|---|---|---|
| drawRadar → vpUpdateMapZoomA | 전역 mapZoom 갱신 | 뷰별 임시 값, finally 복구 |
| drawRadar → updateTacticalScaleLabel | 메인 버튼 DOM 텍스트 | 공통 준비 1회로 이동, PiP 페인트에서 호출 안 함 |
| trackIsDisplayable → trackCovarianceMetrics → trackEkfInit | 없는 `_kfX/_kfP` 지연 초기화 | 준비 단계에서 기존 경로 1회, 페인트는 캐시 값만 |
| 선택 트랙/카드 → trackIsFireControlQuality → trackRefreshDerivedQuality | quality, sigma, mem sigma, covarianceEllipse 갱신 | 기존 선택 트랙 준비 경로로 이동, 픽셀 함수는 `_chartReady/_chartUq` 읽기 |
| ensureTerrainChartProfile/지형 하위 함수 | `_chartProfile` 등 지형 등고선 캐시 | 준비 단계, 페인트는 알려진 해도 점/등고선만 |
| ciwsWorldArcSegmentsV1 | mount._worldArcsV1 캐시 | 준비 단계, 페인트는 chartArcs만 |
| networkPictureG → prepareNetworkG | 네트워크 표시 상태 지연 준비 | 준비 단계, 수신 네트워크 표시 레코드만 사용 |
| MAP_A.draw → records | 조회 객체 캐시 | preparePaint로 이동, 마커는 캐시 그림만 |
| drawAuxCic | lastTargetMap, 캔버스 크기, caption DOM | 기존 경로 비활성, 새 창 스케줄이 DPR/크기/caption만 처리 |
| Canvas2D 호출·스타일·변환 | 픽셀/그리기 상태 | 허용된 출력; save/restore + 어댑터 finally |
| 렌더 횟수/주기/입력 지연 카운터 | UI 진단 통계 | 표시 전용이며 전술·센서·판정에서 읽지 않음 |

원본 drawRadar 및 그 하위 레이어에서 트레일 적분, 알림 생성, 타이머 진행, 난수 사용은 발견되지 않았다. lockCursor 위치 갱신은 그리기가 아니라 기존 fixed-step 경로에 있었으므로 그대로 둔다. PiP 페인트 전후 통제·조회·커서·항로점·알림 수 불변을 동기 검사했다. PiP ON/OFF 7200틱(120초)의 물리/센서/무장 상태 해시도 동일하다.

## 기존 미관측 정보 누출 제거

- SPY 빔 라벨의 `trackTruthDomainV27`은 truthRef를 따라갔다. 공통 지도에서 기존 관측 `classification`으로 바꿨다.
- SAM 시커 선의 CHAFF/FLARE 끝점을 적 대응체 실제 배열에서 찾던 fallback을 제거했다. 자체 무장이 보고한 RF 추정과 이미 관측된 트랙만 사용한다.
- 무DL 하푼의 현재 위치는 프레임에 포함하지 않는다. 발사 전 계획 경로만 공통 지도에 그리며 MAP_A 정보창의 자함 보유 발사 정보 정책을 보존한다.

PiP 페인트는 `ENGAGEMENT_RUNTIME`, 적 truth 배열, `truthRef`, `associationDomain`, `get3DRenderState`를 조회하지 않는다. 테스트에서 적 엔티티/트랙 truth 필드 getter를 차단한 상태로 10회 페인트해 접근 0회를 확인했다. 준비 단계의 기존 `networkPresentationTrackG`가 내부적으로 원본 트랙을 펼칠 수 있지만 출력 DTO는 명시적 화이트리스트이며 truth 필드를 유지하거나 역참조하지 않는다. 자함 헬기/장비 위치는 소유자 확인 후 자함 텔레메트리로만 사용한다.

## 표시 레이어별 입력

| 레이어 | 읽는 출처 |
|---|---|
| 트랙, MEM, 불확실성, BDA | 기존 관측 트랙·기존 연관된 네트워크 투영 결과 |
| ESM 선 | 기존 방위·오차·계열·나이; 거리 생성 안 함 |
| 아군 네트워크 | 수신 SELF/공유 보고, 기존 연결 관계 |
| 자함/항로점 | 자함 항법/운용자 계획 |
| 헬기/자함 대응체/구명정 | 현재 자함 inventory/owner 확인 후 자함 장비 상태 |
| 아군 SAM/RAM/탄체 | 기존 자함 무장 텔레메트리·시커 추정; 하푼 actual 위치 제외 |
| 섬·해안·등고선 | 기존 공개 해도 지형 캐시 |
| 선택/통제 마커 | MAP_A의 같은 네 UI 슬롯과 준비된 표시 객체 |

독립 고도 플롯/손상 패널/상단 HUD의 내부 배치는 이번 지도 렌더 분리 대상이 아니다. 3D 센서/장비 표시, 모델과 물리 피드백 경로도 변경하지 않았다. 함수 단위 변경 목록과 패킹·저장·자산 동일성은 [정적 증거](evidence/static/static.json)에 있다.
