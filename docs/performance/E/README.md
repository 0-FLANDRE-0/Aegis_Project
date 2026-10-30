# 최적화 5단계 PERF_E

PERF_D final `b4b58dcf61cff18674ec58f5798a2a15ca178ae9` 위다. 원본 packed13만 변경한다. 등록 모델·삼각형·envelope 원본과 packed0〜12,14는 동일 bytes다. physical damage/flight/sensors/AI/actual release/RNG/fixed60/120/20Hz와 PERF_A/B/C 캐시는 유지한다.

갑판 주변 x12/z4 CG 피격을 native RAF/SwiftShader에서 추적했다. D에서 entry/exit anchor 둘 다 맞았고 약101.5초 뒤 실제 cut 메쉬가 제출됐다. 주변 구조물·fittings·sensors의 42,676회 cooperative steps가 첫 공개를 늦췄다. 이것은 D의 이번 재현 결과이며 과거 C의240초 timeout 원인을 소급 확정하지 않는다. [D 입력·추적](investigation/provenance.json)을 보존한다.

현재 등록 CG/DDG 모델의 quick job은 모든 scar anchor 메쉬를 먼저 끝내 양측 cut/fold를 함께 공개한다. 한 메쉬의 반만 공개하지 않는다. 주변 메쉬와 동일 scorch/edges/detail 작업은 계속한다. 각 메쉬의 기존 hole 순서·cutter·최종 형상은 보존한다. 아직 처리하지 않은 옛 메쉬를 조기 복원하거나 dispose하지 않으며, 원본 records를 유지해 후속 incremental cutting이 같은 입력을 읽도록 한다. 마지막 공개는 이미 붙은 anchor 버퍼를 유지하고 새 주변 버퍼를 교체한다. cancellation은 미공개 새 버퍼만 회수하고 reset/import/owner retirement가 live cut geometry를 회수한다. 큰/작은 LOD proxy도 첫 공개 revision을 같은 draw 전에 확인한다. legacy 비등록 모델은 기존 공개 경로를 따른다.

폴리곤 split은 같은 정점의 plane distance를 다음 edge에서 재사용한다. triangle bound는 같은 세 좌표에 Math.min/max를 직접 적용해 임시 배열3개를 줄인다. plane 순서·epsilon·mix/정점 순서·부동소수 산술·색상과 법선 결과는 유지한다. shape fixture는 실제 원본 THREE의 quick/detail/sealed/추가 피격 전체 attributes/index/groups/bounds/bindings를 직접 비교한다. generator 제어 완료는 형상 검사이며 native latency 측정이 아니다.

연기 shader/정렬·모드·투영·opacity·시간·pool/수명/난수는 바꾸지 않는다. 일곱 instanced attributes의 정확한 Float32 값을 비교해 바뀐 범위만 전송한다. pending range는 실제 Three onUpload 또는 r140이 소비한 updateRange를 확인한 뒤에만 비우므로 여러 flush, 숨김/재등장, 줄어든 tail에서도 데이터가 빠지지 않는다. camera/origin/순서/색상/age 변화는 매번 계산한다. WebGL2 getBufferSubData로 실제 GPU buffer bytes를 대조한다. 단순 paused dirty-range 절약을 전체 FPS 개선으로 표현하지 않는다.

성능은 전체 회귀 종료 후 직렬로 세 가지를 측정한다. H4A→E 같은 실행의 누적 host fixed-tick CPU, D→E native 첫 anchor cut submission, D→E native RAF CPU submit/driver transfer다. 단계별 개선율을 더하지 않는다. 최초 H4A→D 탐색 측정은 static 검사와 겹쳤으므로 최종 개선율/PASS에는 넣지 않는다. 최종 증거/조건/한계는 [성능](PERFORMANCE.md), [검증](evidence/verification-summary.json), [재현](GITHUB_HANDOFF.md)을 따른다.

full original 직접 upload/readback은 기존 §7.1 사용자 승인 범위다. main/선행 branch 병합·새 PR·Actions dispatch는 하지 않는다. 다음은 최종 과부하/종료·자원 회수 점검 이후 헬기/초수평선 탐지 → RGM-109E Block Va다.
