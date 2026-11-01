# R4 six-target causal run: static consumer paths

This is a bounded, read-only source audit. It adds no experiment, product change, coefficient change, expectation update, or approval. Line references below mean the decompressed `data-c55-index="13"` game script in the actual frozen HTML, rather than the packed HTML's outer line numbers.

## Frozen sources and observed boundary

| Product | HTML SHA-256 | Script 13 SHA-256 |
|---|---|---|
| R3 | `a1e09f0ba815a84152b140ffeafcf139b0cbbf82911713d6c5802ed797fb0561` | `796d685b5a098ac2de9acf09c07dfc393bbf5d929ad7c1b26dd695222f1ceb8d` |
| R4 `Aegis_SIM_v48_WIP_TRACK_B_STABLE_D.html` | `48b023c580db02b08f165fa7ac68f973734d82e8fb4daa5981dcc90b7e04e4ab` | `6163ada1a49dc86ce8b179b81650fa2da78ecc8d9273015142a721748abf6a64` |

The native observations, not this static audit, establish the first divergence. [FIRST_reacqExtra.json](FIRST_reacqExtra.json) records step 1885 / 31.4166667 s: scheduled owner `300000005`, `TRACK_REACQUIRE`, sequence 9142, accepts a return into recipient `300000007`. Before finalization, the recorded state vector, covariance diagonal, NIS, quality, lifecycle and counters are equal. R3 then sets `reacquiring=true`, consecutive misses 2, reacquire hits 1 and FCQ `0.4963468367372838`; R4 preserves a firm file, clears those counters and retains FCQ `0.9926936734745676`.

Immediately after that finalizer call, **the recorded state vector and covariance diagonal are still equal**. Both products also record the same task/source and expected revisit 0.1 s, changed from 0.075 s. The first captured later NIS difference is step 1888 / 31.4666667 s, plot 1 → file 007: `9.392787` versus `9.410279`. The first captured different covariance is after an actual correction. These observations do not directly measure the intervening prediction's complete P, acceleration sigma or numeric Q. In particular, they do not establish that a correction was the first operation to change P.

## Existing native paths that consume the changed metadata

All locations and coefficients in this table are from the actual R4 script. They describe existing consumers; no RF, EKF or AI equation was edited by this audit.

| Path | Actual source | What the source establishes |
|---|---|---|
| Accepted return → lifecycle | `spyFinalizeAcceptedTrackV31`, L27413–27439 | R4's mode/ownership guard at L27422 prevents a firm foreign recipient inheriting the scheduled file's reacquire state. Already-reacquiring recipients and their original recovery path remain outside that exemption. The task's actual source, revisit and face are written before the branch at L27417. |
| Reacquiring → process acceleration sigma | `TRACK_FILTER_MODEL`, L26250–26251; `trackProcessAccelSigma`, L26336–26344 | The existing ASM base is 22 m/s²; the existing reacquire floor is 42 m/s². `opts.reacquire || tr.reacquiring` selects the floor, followed by the existing maneuver-probability multiplier. These are pre-existing game values, not new tuning. |
| Sigma → predicted covariance | `trackEkfPredict`, L26345–26368 | The CV mean propagation is at L26348. L26358 squares the selected sigma into `q`; L26359 forms `qpp=.25*dt^4*q`, `qpv=.5*dt^3*q`, `qvv=dt^2*q`. The existing low-altitude vertical multiplier and symmetric covariance writes follow. A changed reacquire flag can therefore change **the next native predicted P even with the same accepted measurement and same mean at finalization**. This is a demonstrated source path, not a captured numeric-Q attribution for step 1888. |
| Tick lifecycle → prediction | `updateRadar`, L40206–40264, especially L40231–40252 | Fresh `lastUpdateSeen` does not itself clear an already-reacquiring file. At L40252 the tick passes `{memory:tr.memActive,reacquire:tr.reacquiring}` to the existing predictor. Dwell-failure/miss logic and overdue/coast logic are distinct. A global HOLD does not directly increment the native dwell-miss counter. |
| P / measurement → NIS | `trackRadarAssociationNisV31`, L26457–26468 | The native association kernel uses predicted covariance/measurement geometry, constructs the measured innovation and R from the actual plot sigmas, and evaluates `innovationᵀ S⁻¹ innovation`. A later predicted-P difference is a concrete route to the observed NIS difference. Actual measurement or geometry changes can also contribute later; the trace does not isolate a numeric share for each term. |
| Lifecycle / misses → future scheduling | `spyDesiredRevisitS`, L26998; `spyTrackTask`, L27059; `buildSpySchedulerTasks`, L27101 | Existing reacquire state/miss counters affect task selection, age/urgency/deadline, revisit requests and beam padding. The miss pad is capped by existing code; covariance also contributes to scheduling. These consumers can alter **later** serviced tasks and returned measurements without changing their coefficients. |
| Task kind → existing measurement parameters | `spyTaskMeasurementParams`, L27211–27226 | Existing task-specific sigma multipliers differ: `TRACK_REACQUIRE` uses 1.18 / 1.28 / 1.32 / 1.15 at L27223, whereas high-threat/support uses .78 / .76 / .80 / .72 at L27222. This is a future task→R/measurement path. At the first step-1885 finalizer boundary, the task/source/revisit are equal; the guard did not retroactively alter the measurement already accepted. |
| Lifecycle → current FCQ | `trackRefreshDerivedQuality`, L26603–26611 | L26607 explicitly multiplies FCQ by .50 when reacquiring. This directly explains the first recorded factor-of-two quality difference without requiring a covariance difference. Revisit and age also enter the existing freshness term at L26604–26605, but revisit is equal across products at that first boundary. |
| Lifecycle / quality → fire-control permission | `trackIsFireControlQuality`, L27723–27735; `wip119EvaluateRow`, L50340–50345 | The existing quality gate rejects `reacquiring` even with fresh sensor age. `wip119EvaluateRow` returns `FCS_QUALITY` before its automatic A3 authority and subsequent release checks. This is a consumer of the changed association metadata, not a new AI permission rule. |

The first branch is therefore not merely a display change: it has both an immediate existing quality/permission consumer and a subsequent existing predictor/scheduler consumer. Conversely, the source alone does not prove which later RF draw, covariance element or scheduler decision caused the final damage difference. The measured sequence in [RESULTS.md](RESULTS.md) remains authoritative: metadata, later NIS/assignment/planning changes, then different release/defense events. The worse R4 combat result remains **NOT_APPROVED**; this audit neither relabels it nor updates its expected value.

## `shipHitHistory[*].time`: wall-clock leaf audit

[HIT_TIME_SOURCE_PROOF.json](HIT_TIME_SOURCE_PROOF.json) records both frozen products' hashes, 79 `shipHitHistory` / `shipLastHit` references per product, and 11 performance-clock timestamp writes per product. The actual writers attach `time:performance.now()` to hit/miss records; examples in R4 include L32516–32517 (dud contact), L32562–32563 (normal contact), L32582 (sea-impact record) and L32588 (battlespace-exit record). This field is a browser monotonic presentation clock, distinct from fixed simulation time, missile life or observation epochs.

The four explicit history-hit `.time` consumers identified in the actual R4 executable source are:

| R4 script line | Consumer |
|---|---|
| L52360 | Top-view terminal debug overlay hold/fade, `(now-h.time)/1000` |
| L52362–52364 | Top-view hit-marker 120-second age/fade |
| L52470 | Side-view terminal debug overlay hold/fade |
| L52474–52476 | Side-view hit-marker 120-second age/fade |

This conclusion applies to the **`.time` leaf**, not the entire hit-history object. The latter has genuine non-presentation consumers: the mass/geometry path at L33230–33233 and `mastSupportLostV12` at L34593–34598 consume solved scar/support geometry. Those paths use history identity/count, damage, penetration and blast fields. The called `createShipDamageVisualStateV1` body at L34335–34379 contains no hit-time access: scars and openings persist until reset (L34371–34373), rather than expiring according to presentation age. `wip12bRecordLegacyAsmTerminalEffect` at L24589–24601 reads solved geometry, energy, fuze delay and damage data; its elapsed-time fields derive from fuze/terminal state, not `hit.time`. Whole-record exports/copies preserve the presentation leaf in diagnostics but do not themselves consume it as a physical clock. Other generic `last.time` accesses belonging to wake/power histories are different objects and are not evidence of a hit-clock physics dependency.

The preserved literal event comparisons did fail on these performance-clock leaves: one R3 assertion and four R4 assertions. Their raw failures are retained in [GUARDS_LITERAL_EVENT_FAIL.json](GUARDS_LITERAL_EVENT_FAIL.json), [R3-EVENT_LEAF_DIFFERENCES.json](R3-EVENT_LEAF_DIFFERENCES.json), and [R4-EVENT_LEAF_DIFFERENCES.json](R4-EVENT_LEAF_DIFFERENCES.json). The separate operational guards are 18/18 per product as reported in [GUARDS.json](GUARDS.json). Source/read-consumer evidence supports classifying those specifically enumerated `hit.time` differences as presentation-clock differences under the parent's bounded semantic guard. It does **not** turn the literal comparisons into passes, authorize ignoring general timestamps, hide any other raw difference, or establish combat equivalence between R3 and R4.

## Remaining limits

- No additional RF/NIS/prediction/update/RNG call, browser run or product edit was performed for this document.
- Numeric Q at the intervening prediction was not captured. The source proves a valid dependency; the native trace proves the metadata-first / NIS-later order. It does not separately quantify every contribution to the later P/NIS values.
- The R4 mode/ownership guard corrects a demonstrated foreign-task metadata propagation path. That fact does not approve its changed downstream combat outcome.
- No physical or AI coefficient, expectation, tolerance, source receipt or archived failure was changed.
