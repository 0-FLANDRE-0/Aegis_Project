# R2 SHADOW native 통제

제품 `a5455eda8cb3e6751047a5d81887dc2b956073a74127eb63efebd0bcf49ca1d2` / module `499198392351c415cbf54d35d5731f393f650c6e1b00a694dd714ee318ed03bb`의 scoped SHADOW native 통제를 **PASS**했다. 실행은 baseline B + SHADOW OFF/ON3페이지, 48.84초다. ACTIVE 제품은 실행하지 않았다.

- R1 helper 원문·기존 기대값을 그대로 사용했다. 실행 전 R1/canonical 지원14개 source pin을 검증했고, helper SHA와 receipt를 PROVENANCE에 보존했다.
- 기존 대표5그룹19/19, 실제 native S/차원/epoch/full-Doppler callback18/18이 OFF/ON 모두 통과했다.
- 새 ACTIVE 양성 기대는 SHADOW에서 실제 적용하지 않아 **19/23 raw FAIL4**다. 이 실패를 PASS로 바꾸지 않았다.
- 별도 통제에서는 원 B와 fixture별 filter/P·physical·private/global RNG 및 마지막 전체 상태가 정확히 같았다. OFF/ON native 결과와 metadata 계산도 같고 query·ENV·API 검사가 통과했다.
- own surface와 NPC의 동일 NIS winner를 지지하는 우도 제안 로그가 실제 제품에서 기록됐다. 이 제안 로그는 SHADOW의 실제 적용 성공이 아니다.

원시 결과는 보조 조회 전에 저장했다. R1 source·실패 자료·기대값은 수정하지 않았다. R1 자연13기 교전 악화는 여전히 실패로 남고, 이번 통제가 R2 전투 성능을 승인하지 않는다. 별도 순수 captured-input 감사도35개 logger record 중14개 pairs 배열만 사용 가능했고21개는 unavailable이므로 전체35개 성공으로 세지 않는다.

브라우저와 한 공유 lease를 반환했다. 현재 결과는 scoped 대표 native 통제이며 원 native23그룹 전체 재실행·자연 RF/전투·R2 ACTIVE 검증은 별도 GO 이후 수행한다. 권위 raw 요약은 `evidence/native-shadow/SUMMARY.json`, 집계는 `NATIVE_SHADOW_SUMMARY.json`이다.
