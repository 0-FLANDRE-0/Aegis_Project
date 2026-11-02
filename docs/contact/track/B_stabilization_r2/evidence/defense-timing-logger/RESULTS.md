# R2 방어 소비 경로 원인 계측 — 미승인

oldB/R2 각OFF→ON 동일성16/16, 합계32/32. 모의 관찰기 순수성14/14. 실제 게임 함수 추가 호출0, 제품·계수·기대값 변경0. 두90초 페이지 완료 후 브라우저/lease를 반환했다.

## 직접 확인한003 재사격 지연

이번 비교는 **oldB17.0초 → R217.6초(0.6초)**다. R1의21초는 별도 역사 자료이며 이번 R2 결과에 섞지 않는다.

| 시점 | oldB 실제 소비 | R2 실제 소비 |
|---|---|---|
| 12–14초 | 기존SAM5/6 생존, IN_FLIGHT | 동일 |
| 14.6초 | FUTURE, 계획delay2.5초 | 동일 |
| 17.0초 | FCQtrue → A3ok → brakeok(2.2/12.8s) → 발사 | FCS_QUALITY, reacquiringtrue; A3/브레이크는 해당평가에서 미호출 |
| 17.2–17.4초 | 이미 재사격 진행 | reacquiringtrue/FCS_QUALITY, 최신 센서Age≤0.0667초 |
| 17.6초 | 기존 후속발 대기 | FCQtrue → A3ok → brakeok(2.8/13.4s) → 발사 |

`trackIsFireControlQuality`는숫자FCQ/공분산검사보다먼저memActive/reacquiring를hard-reject한다. 실제runtime소스SHA는두제품동일: FCQ`be418119…`, EvaluateRow`ccf03716…`, A3`e2e7c681…`. 따라서이0.6초의직접거부관문은현재재획득상태를읽는FCQ이며, 고정cooldown·탄약·pending지연이라고보지않는다. 실제반환이없는관문을진단기가다시호출하지않았다.

재획득flag의정확한setter원인은아직미확정이다. source상focused dwell미스누적과레이더의miss분기, 첫accepted reacquirehit의2-hit확인과정이구분된다. 단순stale/overdue분기는COAST/MEMORY로별도다. 다른파일의재획득task가GLOBAL remainder로전파되는가능성은별도guarded실제Finalize/task소유권계측전에는확정하거나수정하지않는다.

## 남은큰성분HOLD

실제R2큰graph18/18가동일원입력의pure결과와일치한다. NIS-only정확참조가보류했는데R2가수용한pair0. 반대로정확참조로해결가능한데남은HOLD는3graph/35pair출현이다: tick7=13, tick80=11, tick236=11. 전부LBcert0/residualSolved0이라R2조건부잔여검사에들어가지못했다. 35개고유표적을뜻하지않는다. `LARGE_EXACT_REVIEW.json`과원37개graph를보존했다.

## 90초잔존ASM 해석

두제품의90개1Hz표본에서ownchaff/activeDecoy는0, noise/deception/softKillAuto 명령은false였다. 시커의기만/HOJ도OFF다. 이는관측된기만성공의증거가없다는뜻이며, 매RF순간전체를관측했다는주장은아니다.

oldB잔존1기와R2잔존3기는모두이미자함을통과한뒤13.0–14.5km에서약289–291m/s로멀어지고있다. old1기와R2의18/22는SEARCH/trackValidfalse/INS, R2의24는TRACK/RF_EKF이며미분류RF_OBJECT를추적한다. RF_OBJECT를기만체나자함으로추정하지않는다. 따라서이들은90초현재incoming으로세지않지만영구무해·임무파괴로도판정하지않는다. 1Hz최근접은native sweptCPA가아니고원래lifecycle미종결조건도변경하지않았다.

원반환전체·타임라인·source해시·기하/시커이력은`RESULTS.json`, 평가행은`EVALUATIONS.csv`, 원자료는제품별gzip파일에있다. R2/R1및기존strict차이는미승인으로보존한다.
