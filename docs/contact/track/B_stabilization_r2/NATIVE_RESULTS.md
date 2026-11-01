# R2 native 통합 검증

승인된 scoped native 검증은 모두 **PASS**다. 추가 진단 필드와 기존 strict 기대값 차이는 별도로 보존했다. 자연13기 교전과 전체 회귀의 승인 여부는 다른 lane 결과를 기다린다.

| 범위 | 결과 |
|---|---|
| 원문 R1 정책 단위시험 | 39/39 |
| 신규 residual 음성·순수성 | 15/15 |
| 원 B47 strict | **46/47, 기존 포화 정책 차이1건 FAIL 보존** |
| 추가 ACTIVE native | 기존 대표19/19 + 새 native23/23 + 실제S/epoch/callback18/18, OFF/ON 모두 |
| 원 native 전체23그룹 | SHADOW/ACTIVE 각각OFF84/84·ON90/90 |
| 원 cohort14 | fresh4 contexts 모두14/14, 원helper가진단ON강제 |
| 실제 native 포화 | oldB42/42·SHADOW42/42·ACTIVE44/44 |

SHADOW는 새 ACTIVE 기대4건을 실제 적용하지 않으므로 raw19/23 FAIL4를 유지했다. 별도 통제에서는 원 B와 모든 fixture의 filter/P·physical·private/global RNG 및 마지막 상태가 정확히 같았다. R1 helper 원문과 기존 기대값/허용 오차를 바꾸지 않았다.

실제 packed main을 원래 packer로 읽어 module occurrence1과 mode token을 확인했고, unpack→pack 바이트 roundtrip도 두제품 모두 일치했다. 실제 제품을 실행해 query/ENV·snapshot·OFF/ON·함수복원 통제를 검증했다.

- ACTIVE `c8a9266fe12d6543cf09a1e851af5a0c717e73117945291c5bb5babc9670d584`
- SHADOW `a5455eda8cb3e6751047a5d81887dc2b956073a74127eb63efebd0bcf49ca1d2`
- module `499198392351c415cbf54d35d5731f393f650c6e1b00a694dd714ee318ed03bb`

ACTIVE 추가native3페이지는 46.31s, 원native/cohort8freshcontexts는 138.81s, 실제포화3contexts는 43.82s다. 기존published B의 전체 nativeResult(schema/header/A진단 포함)와 fixture fullstate hash는 원native8contexts에서 모두delta0이었다.

원래 nativeResult 밖의 controller/B 진단 snapshot도 별도 전수 leaf-diff로 남겼다. 원native8contexts의 outer 진단은 R1 대비delta0이지만 oldB 대비3/23/2347개leaf 차이가 있다. 이것은 상속된 R1 진단·초기 header 차이로 원시 자료를 보존했으며 전체 artifact가 byte동일하다고 표시하지 않았다.

실제 포화 자료에서는 R1 대비 SHADOW nativeResult12개·ACTIVE24개 leaf가 추가됐다. 모두 다음 네 진단 scalar의 추가다: lowerBoundCertifiedCount, exactResidualCertifiedCount, residualComponentsSolved, residualRefinementRejected. outertrace는 각12개 추가, filter/private-state hash차이는0이었다. 전체 diff와 추가값0/13/16을 보존했고 자동 승인·원값 변경·검사 제외를 하지 않았다.

실제포화 clear13/16은 ACTIVE에서 선택13/16·원필터각1회correction·birth0이며, oldB/SHADOW는원래HOLD를소비했다. 같은위치equal13은모든제품에서HOLD13·correction0·birth0·전체private-state동일을유지했다. 이 fixture는 명시한owned prior/익명측정의 native 경계시험이며 RF echo 발생증거가 아니다.

R2 residual의 captured-input 감사는 독립 자료다. logger35records중14개만pairs배열이있고21개는unavailable이므로전체35개성공이나emptygraph로세지않는다. R1 자연13기 악화 결과도 그대로 남기며, 이번 native PASS가 그 실패나 기존 원B47 strict1건을 승인하지 않는다.

권위 raw는 evidence/native-shadow, native-active, original-native-full, native-saturation의 SUMMARY/PROVENANCE와 raw-before-aux 파일이다. 추가 진단차이는 evidence/native-diagnostic-deltas/에 전부 남겼다. 집계는 NATIVE_SUMMARY.json, 실제몸체증거는 evidence/RUNTIME_PRODUCT_RECEIPT.json이다.

브라우저와 공유 lease를 모두 반환했으며 이후 추가 브라우저를 실행하지 않았다. 검증 중 고정 제품/R1 source/기존raw·기대값·계수의 추가 수정은0이다.
