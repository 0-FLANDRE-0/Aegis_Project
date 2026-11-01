# 작업 인계용 체크포인트 — 최종 보고 아님

실행 환경 /tmp/aegis-gun-b2/repo, branch gun-b2, HEAD831795e0dfcbb95f77fb69c5193b30a6ff1d3809. 아직 새 커밋·push·PR 없음. 사용자 승인 PHASE1_START1→5, OFF=AIR_ORIGIN_A4c519175…697eeb. 피해RNG/Pk계수 변경 금지, 기대값 추가 승인 금지, main병합/release/tag 금지. NO SUBAGENTS.

물리 최종925178b5b06bcd81304f6b98da4436fda4fd85eaf7ea8de3813a981981f0da71 / mainb0a95a0e…1aacc. measurement-build.json 고정. **G7/legacy검사 끝날 때까지 루트 제품 빌드 금지**. 최종표/링 UIpreview /tmp/aegis-gun-b2/phase1-ui.html SHA c48c2396932e07c8051b7a07d2da282951587283d768f2caa384a48936a0ed8b. 끝난 뒤 build.py --stage all 하면 같은 bytes 예정. 압축main/manifest 같이재생성. ring은표시만, auto9km유지.

완료: 정합만16(OFF8정확4c), native앵커400초기31.696m→49.5목표80:20유한차분→별도400 σ50.849749984m/cross3.4819986m; 최종400재검증동일. σMV .0021561842388671667/el .6484094047367095mrad/train .20mrad; nominal823유지. AIR창8, 최종물리18, 빠른구거절12000, 입력캐시4(관측/공분산/원점/환경/same tick), 독립stream/RNG0. 281보호/ENV120/기존피해·SAM/RF/EKF/저장byte동일. 전체허용변경역복원=4c정확.

최종거리1440시도=1400발, CG정면1km40은nativeMOUNT_OCCLUDED미발사. 실행470.33s. 실제6native함수hash브라우저4조합모두확인. range-table.json은실행시고정fingerprints에서만생성(나중코드에서추정하지않음). native계측/비계측6fresh쌍정확(+2ms,한budget/pass). final-pairs16PASS, OFF8=4c정확43발, ON8=25발 모두age/origin/observedposition/velocitydelta0. analyze_pairs결과evidence/release-reconciliation.json. 4negativebuildguards모두출력전거절/원제품불변. 최종UIpreviewPC1400/폰832 MAIN/PIP glyph실측8PASS. plots single-shot-pk/dispersion-anchor 이미최종데이터로생성.

곡선 정면 DDG 평균[0,0,.0194,.0594,.0866,.2148,.2892,.2641,.4540], CG[미발사,0,.0190,.0599,.0870,.2149,.3131,.2147,.4536]. 90도1~3km0. 바깥.05하강안나옴→우측검열≥9km 제안, 확정된최대사거리아님/안쪽모두유효아님. 탐지50~90deg/+2ms와몸체파편90±20deg의상대운동때문근거리띠밖많음. 수치결과맞춤금지. 기존 GUN_B1_FRAGMENT/APPLY_RESULT와계수byte유지. 새복사본밀도는몸체R²4πsin20; 초기v1세계입체각×몸체반경혼합발견수정후새로거리/G7. v1 및 cache-input-before 미완료성과는final에섞지않음, archive sources/diff/rows보존.

실행중:
- run_g7.py 3workers, session88554. **full960** freshpage/context, count1..4/ship2/bearing2/seed419010..419039/AutoAA OFF/ON(전B2flagsON). 20:55UTC218/960. 로그 /tmp/gun-b2-g7.log +evidence/g7/worker*.log. resume동일SHA한정. observer읽기전용실제ASMrefs+first3km/death+bursts, legacyshipHits/gunPreCiwsKills틀린카운터로실적보고금지. collect_effects.py 마지막960후완주엄격검사32groups30/pageerrors0/source925/core0. 현재effects-summary는partial/false므로완료후재생성. matched4c60baselineHP악화사례모두공개, user기존DDG90seed419023승인은이전원점복구사례하나만이지새악화자동승인아님.
- main run_regression.py PID203950 OFF후ON, session과/tmp/gun-b2-regression.log. 14domain378PASS/OFFpaired42raw4불일치+world1은이미AIR승인5, reconcile_approvals.py로기존4c승인hash먼저검증/값정확비교PASS. EXPECTED추가수정0. OFFrelease300=baseline4c새실행300과모든row/event/trajectory/RNG정확222/300동일; 자연28도기존4c와정확. OFFWebGL8PASS. mapE UI88/MapB91/extras/network/warnings/new-ui135PASS; 뒤motion/rules/rings/dom 진행중. Composite done는하위10suite끝까지갱신안됨, progress.py now하위UI진행추가.
- queued_gun_regression.py가main종료대기하던oldPID210567는종료했고, 최종v2checks후시작하도록변경. run_gun_regression.py현재실행/tmp/gun-b2-gun-regression.log. OFFnative/auto/geometry/mod4/physical_adapter/mass_split/ui/ui_handoff/label모두PASS. ONnative예상dispersionG2false6및beam밖eventNone에서원본crash보존, ONgeometryrelativeCPA기대false, ONautoPASS. ONmod4이후진행. 맨뒤기존B1 ui/edges migration4실행(원래지시의AIR VELOCITY_UNCERTAINTY+Mod4 24km,새완화아님).
- queued_continuation.py session41373는ONlabeldone후 continue_native_assertions.py/continue_adapter_assertions.py를별도기록. None이벤트는FALSE로남기고원래null-deref후나머지CG/adapter체크까지도달시키는privatecopy. 원본실패/원본파일보존, 기대완화X.

회귀원시실패 구별:
- raw PIP_B UI85/88는MAP_B/E의커서bridge제거전오래된lockentry. canonical docs/map/E/verify_ui88.py는정확native mapPrecisionCommandA 경로로88PASS. 같은기존test원본무수정.
- raw MAP_D UI205/213는AIR일괄NOT_SURFACE_TRACK 기대8, rawedges CG22km는B1부터obsolete. 기존B1run_test_migrations ui/edges대기. no新기대값.
- rawEWsamefalse2는정확24/28개Mod4/HE180+MFF180inventoryscalar, audit_ew_reuse.py 기존B1predicate로PASS; nativeEW94/H3195PASS. 原raw변경없음. ON도끝나면재실행.
- collect_regressions.py는rawchecks/failed CSV목록(아직partial), 최종다시실행. 새ON차이는항목별분류/설명, 사용자기대값갱신없음. OBSOLETE반복과실제B2요청변화혼동금지. temporalUI실패있으면idle에서원assert그대로재검사하고원시보존.

남은 작업:
1) full960/mainreg/명시적B1검사/continuation모두끝까지. 실패면harness만최소고침/재시험, 계수/검사완화X. 고각/PN등전혀손대지말것.
2) verify_g7_repeat.py 2개최종90도count4seed419010(DDG/CG) naturalfulltick신선페이지반복. 새read-onlyperfwrapper가ticks/refresh ms기록. 기존원시결과/RNG대조때host elapsedMs/refreshMs만빼고정확, 성능은headlesshost CPU/동시부하/observer포함, 폰FPS주장금지. root아직925인동안실행.
3) collect_effects.py(960엄격), plot_g7.py, analyze_pairs.py, reconcile_approvals.py(OFF+ON), audit_ew_reuse.py(둘), compare_native_sam.py(OFF+ON300/28), collect_regressions.py. ONraw실패목록원인전부보고, 기대값자동승인하지않음. 추가승인요청전결과concretePR완성.
4) 모두끝난후 build.py --stage all 루트최종c48UI로, static.cjs(compactAcorn) +audit_product.py +verify_label.py(B2_LABEL_HTML루트, 최종스크린샷별도E) 검증. 측정함수/σ/spec/factory fingerprints동일 guard. static281/ENV120, assets0..12/manifest다른부분동일, 4c/B1원본/oldraw/기대값/schema변경0. audit_product.py만아직안실행(최종UI전에는preview불일치실패가정상).
5) REPORT.md/README/status/topB2BUILD_STATUS+STATUS/INDEX 완성, CHECKPOINT/WORKING_STATE는명확한historical개발경로로이동. PHASE0/post-origin/PHASE1_START원시불변.
6) package.py아직없음. separateHTMLZIP/reportZIP underdownloads. **PNG현재222장81.9MB이미초과근접, 전부넣으면100MB제한넘음**. reportZIP는모든JSON/CSV/log/tools/plots+대표최종스크린샷만포함, 나머지PNG원본은repo보존+media index(SHA/경로/포함여부)명시. 선택은성공/실패은폐X, 중복전체회귀화면때문. HTML별도체크섬, BUNDLE_CHECKSUMS.zip내부검증, repo전체CHECKSUMS별도. ZIP100MB미만CRC/멤버SHA모두검사.
7) git add --sparse 새HTML/phase1/상태/downloads, authorDagoku Suika/110261808+0-FLANDRE-0@users.noreply.github.com, 커밋+gun-b2normalpush(권한계속승인됨). main/release/tagX. remoteZIP/raw/member readback(연결GitHubbinary미지원이라urllibrawfallback), receipt-only커밋push/readback. 보고ZIP는첫artifactcommit고정link, receipt는후속commit로자기해시순환피함. GitHub tools createPR(main←gun-b2)사용, noexistinggun-b2PR. 새ON/근거리결과검토필요면draftPR구체적설명. final간결한국어+직접다운로드rawGitHub HTMLZIP/reportZIP+PR.

환경: /workspace거의full, /tmp1.8GB남음, /dev/shm8GB이상. TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 MPLCONFIGDIR=/dev/shm/gun-b2-phase1-mpl. NODE_PATH=/workspace/aegis-performance-f/docs/performance/F/node_modules (Acorn8.19.0). 처음과도한병렬+fullAST4OOM은과거resource-retry보존, 현재OOMkill4이후추가0. 큰literal마스킹compact_source써서AST메모리한정, native원문은오프셋에서다시꺼내실제실행함수hash와확인. 새agent금지. 함수exec기타툴은Promisebatch, dependencies는순차. 사용자도움요청없이완주.

## 21:25UTC 추가 확인

OFF 전체 compositeUI10suite PASS(UI88/MAPB91/newUI135/motion/rules/rings/dom 등), ON domain85helo/20APS/ISAR계속PASS. G7 약359/960, 원래925물리불변. 기존B1 ON continuation36완료21PASS/15FAIL: 산포12, oldCPA prox/friendlySAM2, exactoverlapnativeKill1. geometry2false, physicaladapter3false, UI4false. 모두raw/continuation보존, 기대갱신없음. ONauto/mod4/masssplit/handoff/labelPASS. 기존B1 migration4아직실행중.

CG UI4 원인추가분리완료. evidence/ui-single-cause/cause.json/timeline.csv: OFF/ALIGNMENT만은두문각1발; WINDOW만/ALL은0. atstep223 수직miss1.67~1.69m가oldvertical7.5×.78허용하지만new1.5floor×.78=1.17넘음; pending나중TRACK_SUPPORT_BLOCKED. private PRECHECK_UNION(준비단계에서old또는newpointing통과시면fresh계산, finalgate유지) 실험도0이므로채택안함. **제품helper/runtime/model전혀수정안함**, G7중단/재시작불필요. 실험코드/이전이후함수원문을추가진단에만보존, 원모델625창수치유지. UI4 expected정상화미승인으로PR에공개.

package.py준비됨(아직실행금지-최종report/effects/invariant/repeat기다림). 모든raw수치/CSV/log/tools와대표PNG만reportZIP; 전체PNG는repo보존+MEDIA_INDEX.tsv(100MB제한). PACKAGE_RECEIPT는selfhash피해checksum/ZIP제외. verify_label.py에B2_LABEL_OUT설정추가해최종root테스트evidence/label-final로보관가능. audit_product.py는최종rootc48후실행.

## 사용자 속도 우려 후 부하 정리(22:26UTC) — 중요

사용자 최신 질문: 속도가 느려졌고11시간걸릴것같음, 게임성능악화인가. 이미댓글로4CPU/소프트웨어3D두개가약1.7CPU사용, 추가solve평균3.3ms(부하포함), FPS악화확정아님을설명. **새로운불필요한반복시험중단/정확범위재사용으로최적화**, 게임코드계수변경X. 이후평균G7평가22→16초, 최근부팅포함26초/worker,분당7건. 22:32UTC686/960, 남은약40분+마무리예상댓글전달. 추가탐색시험더늘리지말것.

실제중단: OPTIONAL final_alignment_sample.py8ON(새로추가한중복,직전시작; Ealignment-final부분자료는CANCELLED,현재완료결과로쓰지않기), 그리고 mainreg의중복rawONverify_d_ui child PID276711(원래구식8개단언,이미canonicalON migration213/213검증완료). 후자는원본log와rc−15 stamp보존. 필수G7960/모든새물리/산포/새GUN UI/300/28/WebGL8/EW-H3는유지.

mainreg미래4개중복jobstamp는 exit:null,statusCOVERED_BY_EXACT_CANONICAL_OR_UNCHANGED_PATH_REUSE로**fresh실행처럼위조안함**. 목록 ON-verify_d_edges(별도B1ON기존migration완주PASS),ON-verify_e/verify_e_policy(OFF전체완주·똑같은UI/정책소스,시험이Mk45/MFF요청안함+AutoAAOFF),ON-run_final_ui(OFF9generic시험재사용;ONcanonicalUI88은실제로추가실행). 모든새GUN/표시전용ring은별도ON실제검증유지. 근거evidence/validation-load-reduction.json,후속unchanged-ui-reuse.json. 원래reg.execution54개는48완료+중복중단1+재사용4+EW-H3남음, None/−15는통과실행수에세지말것.

finish_canonical_ui.py session50342실행중: mainON EW-H3끝나면 actualcanonicalONUI88만실행. OFF10UI전체pass와11개generic/EMCON정책스크립트의Mk45호출없음 및byte동일범위검증manifest작성. ON새UI76이미72/76(의도창차이4)원시보존. ONmigrationUI213/213 및ONedges완료PASS; gun-regression.execution.json완성. MainEW-H3끝나면남은주작업은G7960. progress.py는실행/재사용/중단구분하도록수정했고전체회귀완료는canonicalONUI88완료까지기다림.

source정적925증거는 evidence/static-measurement.json에복사해고정, 최종rootc48감사로static.json덮어써도재사용manifest의과거hash유효하도록 staticProofPath를그파일로연결할것(queuedscript이미시작전컴파일된oldpath가있을수있으나hash는같은925;후속문서에path보충만가능). 측정build.json고정은measurement-build.json에이미있음. 게임루트는여전히925, UIpreview여전히c48; **G7repeat2까지끝나기전재빌드금지**.

추가tools준비: generate_report.py(완료된evidence만모아REPORT.md작성, 아직실행금지), package.py. reportgenerator ONcomposite는 fresh10이라고하지않고 actualON88+OFF9근거재사용으로표기하도록수정. 90cross비교 analyze_cross.py결과 evidence/cross-comparison.json/csv(추가발사없음, 최초alignment16은c1e2…당시측정, 최종전체16은925;population/기폭끝점변화경고). reportbody에90평균·std·표본수동적추가. 최초단독90:DDG−2.129→−5.454,CG3.361→−5.768(작은2시드/표본조건변화); 최종전체90:DDG−2.129→−.945,CG3.361→.891. 개선율인과단정금지.

surface-summary.json 추가: firstRoundHit는OFF30/30모두,ON29/19/14각30으로기존요약맞음. **fixture전체pass와다름**: 원래15km이동검사의meaningfulMovingFrame조건은5/10km짧은거리에서OFF/ON모두false. 이단언완화하지않고raw보존,표의명중은checks.firstRoundHit라고reportgen에명시. 전체360/360통과라고하면안됨.

현검토수치: paired4c60개HP악화29회(507개이후60개모두채워진동일고정cohort이므로최종에도29). 사용자에게이미알림,단순RNG로단정X/계수조정X/승인X. domain420OFF/ON+world120둘모두기존승인과정확PASS. SAM300OFF/ON모든row/event/trajectory정확(222/300동일), natural28둘정확, WebGL8둘PASS. compare_native_sam.py이미4rowsTrue. canonB1OFF9suite전부PASS,ON새차이24체크(12산포+2축상beam+1r0+2CPA+3adapter+4UI),auto/mod4/mass/handoff/labelPASS; migration4모두PASS.

새보고서/상태/ZIP/커밋/push/readback/PR은**아직안함**. 원계획완주필수. 준비code ast.parse통과. reportgen의hardcoded새ON差이24는다른未知差이가없는지최종collect_regressions로확인,재사용/중단정확히표기. 마지막진행추정1시간안팎으로줄어든상태.
