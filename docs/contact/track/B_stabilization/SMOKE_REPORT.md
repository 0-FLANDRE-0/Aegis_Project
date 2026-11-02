# 원 실행기 smoke 결과

범위 결과: **6페이지 PASS · 140.06초**. 이 결과는 별도 natural13 material worsening을 승인하거나 기존 upstream FAIL을 변경하지 않는다. 제품87da와모듈ec66은 수정하지 않았다.

| 실제 실행 | 페이지 | 결과 | 과거 대조 |
|---|---:|---|---|
| 원B natural OFF: hover60 / route120 / harpoon75 | 3 | 원checks PASS,기존freshA state delta0 | A·deliveredB 원result/fullstate/observer/P/privateRNG·원state 문자열SHA·압축bytes 동일 |
| 원auto_iff.py 전체runpy | 1 | inventory/IFF/oneFile/core 모두PASS | A·B 원result·기존rng 동일 |
| 원idle_and_dom.py 전체runpy | 2 | fresh before/after truth·DOM 동일,core0 | A·B 원world120 truth/rng bytes 및 rows/checks 동일 |

idle before는 원harness의 CG_TURRET_A(af105075…4d933), after는현재ACTIVE(87da98bf…ede18)를각각새로실행했다. 두truth SHA는 모두 `bc09d108079c46897aab41878397c3e5888443d3db3becbf2f006abd7ae4110f`다. 과거A/B 결과를새실행으로대체하지않았다.

원state 문자열 SHA:
- helo-hover: `2108f9d8821b7923672aeefae6497cc806a3d434062d225c3fee61809d80dbea`
- helo-route: `d4abd2e723e4d4a793ba94cf4ad4fac93ac402b3a323e88c09b84339f381b20a`
- harpoon-route: `7e8cf69fda5ac1aced47f9b449fd07ade9d6abf76164f97e76989974d77a7a6c`

autoIFF와idle에는 과거의 full observer/P/private RNG snapshot이없다. 따라서각각원result/rng와원world STATE/rng·DOM 범위만실측대조했고없는기준을PASS로세지않았다. 원repro3에는해당full snapshot이있어엄격비교했다.

원auto/idle 외곽JSON의과거대조6건은모두`/wallS`만달랐다. 원시bytes·canonical SHA·전체leaf diff를보존했고시각차이를승인하거나삭제하지않았다. 원headers/schema를제외하는비교는하지않았다.

단일slot0으로실행했고parentPID410915가종료하며lease를반환했다. 종료후slot0는다른대기중인S_ONLY 진단worker PID411799가획득한것을/proc/locks로확인하여그lock을건드리지않았다. 원source·helper·제품·저장정책·기대값을바꾸지않았으며33개historical파일과source20핀을종료후재확인했다.

- [전체결과](evidence/smoke/SMOKE_RESULTS.json)
- [후속검사와대조범위](evidence/smoke/POSTCHECKS.json)
- [원실행로그와원시출력](evidence/smoke/)
- [원계획과제품매핑](SMOKE_PLAN.md)

Release/성능/자연전투악화 승인은 하지 않았다.
