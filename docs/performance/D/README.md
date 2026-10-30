# 최적화 4단계 PERF_D

PERF_C final `5ddd05ce9358e9a23c11d26030bff05c6f18fa1d`를 기준으로 한다. 구멍·외형 변형의 첫 화면 반영을 앞당기고, 두 함종의 등록 단면 convex 입력 중복 제거와 변형 경계의 임시 객체 생성을 줄인다.

단면 좌표 두 개의 기존 Math.round(×1e5) 키, Map의 첫 삽입 순서·마지막 값, 좌표 정렬과 convex 산술을 그대로 유지한다. CG main13과 DDG layout2만 바뀐다. 등록 모델·삼각형·envelope 원본은 동일 bytes다. 변형의 radialRadius는 같은 뺄셈·곱셈 순서를 scalar로 계산한다.

기존 cooperative mesh job이 모든 구멍과 fold를 완성하면 quick snapshot을 한 번에 publish한다. 그을음과 윤곽선은 동일 generator에서 이어서 완성한다. detail 단계는 기존 최종 교체 순서를 사용한다. 한 메쉬의 절반만 공개하지 않는다. publish 시 live geometry 소유권을 이전하므로 후속 장식 취소가 붙어 있는 메쉬를 dispose하지 않는다. 미공개 버퍼·장식은 finally에서 dispose하며 기존 reset/import/owner retirement가 live 형상을 회수한다. `_damageOpeningRevisionPerfD`는 presenter 전용 진단 값이며 physics/snapshot에 저장하지 않는다.

자함의 quick 작업은 다른 owner 작업 이후 기존 6ms frame allowance에서 남은 부분을 빌린다. 전체 allowance, 다른 owner share, detail slice와 60/120/20Hz 물리 주기는 유지한다. cooperative next 하나가 예산을 넘을 수 있는 기존 특성도 남아 있다. 표시 작업이 전투 난수·센서·피해·발사·시간을 적분하지 않는다. 관통·폭발·침수·장비 손상 및 실제 release 함수, PERF_A/B/C caches는 source byte 단위로 유지한다.

`verify_damage.py`는 실제 원본 브라우저/THREE에서 generator를 진단용으로 완료해 quick/detail/sealed의 모든 geometry attribute bytes·index·group·bounds와 binding을 비교한다. 이는 형상·취소/초기화 검증이며 native latency 증거는 아니다. `benchmark_damage.py`는 별도 직렬 native RAF/WebGL AB/BA 비교로 실제 attached cut/fold의 첫 render submission을 측정하며 queue를 강제 진행하지 않는다. `verify_envelope.py`는 등록 레이아웃의 3,072 query와 384 convex 경계 사례를 비교한다. 기존 전체 runtime/browser/native 회귀는 최종 원본에서 다시 실행한다.

최종 결과·SHA·조건·한계는 [검증](evidence/verification-summary.json)과 [성능](PERFORMANCE.md), [재현](GITHUB_HANDOFF.md)을 따른다. full original 직접 upload/readback은 기존 §7.1 승인 범위다. main/선행 branch 병합·새 PR·Actions dispatch는 이 단계에 포함하지 않는다.
