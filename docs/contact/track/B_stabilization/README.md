# TRACK-B 안정화 R1 — 승인하지 않은 시험 후보

**R1 최종 판정: FAIL / 미승인.** 게임 HTML `Aegis_SIM_v48_WIP_TRACK_B_STABLE_A.html`(87da98bf…)는 최종 안정화본으로 승인하지 않는다. 원래 domain/UI/WebGL·native 기능 검증이 통과했어도 실제13기 포화에서 기존 B보다 나쁜 전투 지표가 관측됐다. 수정 후속은 형제 디렉터리 `../B_stabilization_r2`이며 R1 원자료와 제품은 보존한다.

- 기준: `track-b-association@1d92554`, 원 B ACTIVE0b3e5ad9… / TRACK-Ae2c1976a…
- 구현 커밋:5718f2d25f2e069f9ebd7948360fcf468bcdbb0b
- R1 ACTIVE:87da98bf8f6d8bd68ef87a3d2ac75ce9c355db9e95bd192ab060d01e5bdede18
- R1 SHADOW:75b845f5b353c576ea191a2508578edcb29b4110a69cbf97e532df6562747d4f
- 기존 expected values·허용 오차·게임 RF/EKF/IFF/ROE/무장·피해·함정물리/AI/저장 스키마 변경0. 보호189+161 byte동일.

권위 상태는 `VALIDATION.json`, 실제 전투는 `BATTLE_RESULTS.json/.md`, 원 회귀는 `REGRESSION_RESULTS.json`·`evidence/regression/FINAL_COMPARISON.json`이다. domain402 PASS/4기존FAIL/14retired UI미완료, D1A29/30·기존B30/30, UI213/213, WebGL8발29/29단언이다. 실제13기 포화는 모든비교HP0이며 90초 초기 잔존1→3, native격추7→6의 악화를 보존한다. 전원 격추 또는 전체 안정화 PASS로 바꾸지 않는다.

`evidence/ablation`과 `evidence/battle-ablation`은 독립S-only/large-only 진단이며 shipping 제품이 아니다. 첫 native13×13/86edges에서 하한 인증3개만 수용했지만 같은 NIS의 정확 대안검사로는13개 모두 구별됐다. R2는 미확정 잔여가12이하일 때 원래 정확 검사를 적용해 이 불필요 HOLD를 수정한다. 계수·기준1을 결과에 맞춰 낮추는 것이 아니다.

전체graph logger35기록 중21개는 `pairs:null`이라 exact 재생 불가다. 초기 `GRAPH_EXACT_COMPARISON.json`의35개 계산을35개 전체입력검증으로 세지 않는다. actual86edge 사례는 온전하며, 수정된 가용14/자료부족21 구분은 R2 `evidence/solver-r2.json`에 있다.

`ORIGINAL_RAID_PILOT_RESULTS.md`는 원 paired 진단습격의 TRACK-A/DDG 한정 파일럿이다. 초기 트랙을 진실로 심는 legacy fixture이고 실제 종료8개 중7개는 비자함 수상표적 접촉,1개만 ESSM격추다. 자연0-track 자함방어 성공이나 원4건의 승인으로 대체하지 않는다.

기존419025피격·observer2미승인·EMCON UI14는 상속문제다. C55/SPQ AIR 실제연관은 계속 SHADOW-only이며 완성기능으로 합산하지 않는다. 모든 실행기/입력 핀과 원시 결과를 보존했으며 전체 재실행은 고정저장소·원fixtures·Python/Playwright/Chromium/Node/acorn 및 명시된 경로/환경을 필요로 한다. standalone HTML과 standalone test environment는 다르다.
