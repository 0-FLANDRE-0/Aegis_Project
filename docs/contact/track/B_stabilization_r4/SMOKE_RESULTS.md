# R4 fresh six-page smoke

최종 ACTIVE `48b023c580db02b08f165fa7ac68f973734d82e8fb4daa5981dcc90b7e04e4ab`에서 원 실행기6페이지를 새로 실행해 **PASS**했다. 실행시간141.52s이며3개 worker 모두 exit0이다. 기존 R1 controller에서 바꾼 것은 후보 파일명과 SHA 두 상수뿐이다. 원 실행기·helper·assertion·비교·기대값을 바꾸지 않았다.

| 새 실행 | 결과 | 실제 비교 범위 |
|---|---|---|
| helo-hover, helo-route, harpoon-route3페이지 | PASS | 원 result, 전체 observer/track/P/private RNG snapshot·원 state 문자열 SHA·압축 bytes가 frozen A/B와 정확히 동일 |
| autoIFF1페이지 | PASS | 원 checks/result/rng 동일; 재고 유지·IFF FRIEND·단일 file·core 모두 통과 |
| idle before/after1202페이지 | PASS | 원래 legacy CG_TURRET_A와 현재 R4를 각각 새로 실행; truth/rng·DOM·core 및 world snapshot bytes 동일 |

idle 두 페이지 모두120초에서 truth SHA는 `bc09d108079c46897aab41878397c3e5888443d3db3becbf2f006abd7ae4110f`, 저장한 world snapshot 파일 SHA는 `d13b78e61f24e32679f41be103133c57bc75987a0f9aade85edbd859fe7ad033`, 관측한 rng는12002다. frozen A/B의 해당 원시 자료와도 정확히 같다. before를 A/B 실행으로 바꿔 부르지 않으며 원래 legacy before/current after 계약을 유지했다.

autoIFF는 원 result.rng419010까지 대조했다. autoIFF와 idle의 과거 전체 observer/P/private RNG snapshot은 없으므로 해당 비교는 **불가**이며 통과로 세지 않았다. idle truth hash만으로 KF/P 동일성을 주장하지 않는다.

autoIFF와 idle raw envelope는 A/B/공식A와 각각1개 leaf가 달랐으며 전부 `/wallS`다. 원본과 전체 diff를 보존하고 승인하지 않았다. native checks/result·idle rows·world bytes 비교와 host 실행시간 차이를 구별한다.

권위 자료는 `evidence/smoke/SMOKE_RESULTS.json`, 보이는 비교 범위와 실제 hash/rng readback은 `evidence/smoke/READBACK.json`이다. source adapter와 고정 입력은 `SMOKE_ADAPTER.json`, `evidence/smoke-adapter.diff`, `evidence/smoke/PLAN.json`에 있다. 과거 R1 통과를 현재 실행으로 재사용하지 않았다.

두 shared lease가 반환된 것을 직접 확인하고 브라우저/controller 종료를 root와 cost lane에 알렸다. 이후 추가 브라우저를 실행하지 않았다. 이 smoke는 기존 실제 전투의 피해 퇴행·미승인 strict 차이·물리 ID 지표 공백을 승인하거나 상쇄하지 않는다.
