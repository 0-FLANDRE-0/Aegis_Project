# SEEKER_CLOSE_A final closure report

## Outcome

SEEKER_CLOSE_A remains a **product-unchanged diagnostic closure**. The
authority executable is the exact HP_A product:

- file: `Aegis_SIM_v48_WIP_HP_A.html`
- bytes: 22,200,135
- SHA-256: `9121c44884ff808b295a4ddff61af93a3ed47f6e8c63956acf7a3339d24836fa`
- product/packed-main change in PR #78: none

The correction fixes after-action evidence semantics and makes the bounded
diagnostic independently reproducible in Actions. It does not modify seeker,
guidance, RF physics, countermeasure strength, weapons, damage, RNG, or save
code.

## State ledger

| State | Result |
|---|---|
| IMPLEMENTED | Structured decoy, defense, and EMCON evidence; corrected fixed 19-shot runner; PR #78-specific Actions closure gate |
| TESTED | Local corrected Chromium 19/19; same-seed and 1x/8x/16x exact; DDG/CG Harpoon support; two fixed Kh-32 boundary probes; protected hashes exact |
| APPROVED | HP_A precondition and this user-directed closure correction scope only; no tolerance or product expectation changes |
| UNRESOLVED | Historical Kh-32 60 km population not remeasured; `CONFIRMED_ONLY` performance unverified; inherited regression debts unchanged |
| RELEASE | None. No new product, merge, release, or tag. PR #78 remains a user decision. |

## Corrected authoritative result

The previous 17-shot output is superseded, not pooled with the corrected
matrix. The corrected matrix contains 19 fixed shots:

| Category | Count |
|---|---:|
| TARGET_HIT | 16 |
| DEFENSE_INTERCEPT | 1 |
| DECOY_SEDUCTION | 2 |
| UNCLASSIFIED | 0 |

All 19 ended in a native terminal state or the fixed qualified-egress endpoint.
The local run completed in 100.109 s with page/console errors 0 and core failures
0. Detailed rows are in `evidence/limited/RESULTS.json` and `SHOTS.csv`.

## Decoy conclusion

All six requested chaff and six requested Nulka paths used the real deployment
and RF-return paths. Each was physically observed, constructed as a candidate,
and selected.

The evidence now distinguishes two facts that the prior classifier conflated:

- 12/12 paths contain a real later anonymous SHIP association after the first
  decoy selection (`firstShipRecoveryEvents`).
- 10/12 paths contain a SHIP association after the last decoy selection and
  end as `SELECTED_THEN_RECOVERED_TARGET`.
- The repeated seed contains two Nulka paths in which an early ship recovery
  was followed by a later Nulka reselection. Nulka remained the last valid,
  decoy-only association through qualified egress. These are the two proven
  `SEDUCED` / `DECOY_SEDUCTION` outcomes.

There are zero selected-but-unresolved outcomes in this fixed matrix. The
classifier never promotes a target hit to recovery without a later SHIP event.
No seeker or decoy tuning follows from these bounded results.

## Defense conclusion

`enabled`, `engaged`, `hit`, and `kill` now have distinct meanings and are
backed by actual fire, close-in, gun, physical-hit, or retirement events.

- DDG hard-kill produced an actual `INTERCEPT_KILL` retirement attributed to
  `5in MFF`: engaged/hit/kill are true.
- CG hard-kill fired three Mk45 MFF rounds: engaged is true, kill is false,
  and nonterminal hit remains `null` because no such event is exposed.
- No CIWS engagement is claimed. Where the complete close-in event view is
  unavailable, `engaged` is explicitly `null` with a reason.
- Soft-kill request, deployment/effect, observation, and selection are separate.

The legacy compatibility intervention fields now mirror actual observed
engagement/effect rather than configuration requests.

## EMCON conclusion

The old scene is renamed `RADAR_MASTER_SILENT_ECM_ON`. It represents the
legacy radar master being silent while ECM is requested and effective. Its
allocator, physical ECM output, receiver coupling, and HOJ evidence are
nonzero, while radar emission remains zero.

One true `ALL_RADIATION_SILENT` scene per ship uses the current UI authority
path. In both scenes the ECM technique request remains present, but allocator
resource, radar output, ECM output, jammer coupling, and HOJ evidence are all
exactly zero. The two policies are therefore demonstrated, not conflated.

## Integrity and reproducibility

- diagnostic build: 22,215,311 bytes,
  `eb1e1ab95740d1e2f1f12af5d7ff81b6ea224e8e3248ce5c7e1c82459c98a5e4`
- protected product functions before/after instrumentation: exact
- physical-return producer: one original call per observation; return unchanged
- classifier truth feedback / tactical consumer writes: 0
- common-layer RNG consumption: 0
- common save-schema mutation: 0
- same seed repeat: exact
- 1x / 8x / 16x physical state: exact
- Harpoon core/seeker/tube support: PASS on DDG and CG
- Kh-32: supporting fixed probes only, not a replacement population
- broad/MAX_THREAT regression: not rerun because product bytes are unchanged

The first PR #78 closure run (`42571169676`) passed the unchanged
current-candidate gate but exposed a raw JSON comparison issue in the new
closure job. Reproduction with Playwright 1.55 found 156 finite-float
last-bit differences, with maximum absolute drift `9.919176591210999e-12`
and maximum relative drift `6.871720048359798e-13`; discrete state, outcomes,
RNG, transitions, and evidence had zero differences. No product value or
expected outcome was changed.

The closure-only Actions job rebuilds the diagnostic exactly, executes the
actual 19-shot Chromium matrix, compares committed simulated evidence while
excluding wall-clock elapsed time, reruns the HP_A outcome/save contract with
all 19 checks, deterministically rebuilds the HTML-free report ZIP, and uploads
the receipts. Every discrete field, RNG state, transition and outcome is exact.
Finite binary64 diagnostic telemetry alone has a fixed `1e-12`
absolute/relative cross-runner portability bound; accepted drift count,
maximum and paths are preserved in `SEMANTIC_COMPARE.json`, with no rounding
of evidence and no gameplay/regression tolerance change. The exact final-head
run URL is recorded in the PR delivery comment after GitHub completes it.

## Inherited debt and exclusions

- `CIWS_SEED_419025_FAIL`, paired observer delta 2, and the fixed WIP12D
  CIWS time-scale debt remain inherited and are not reclassified here.
- `CONFIRMED_ONLY` performance remains UNVERIFIED.
- SOV Mineral/Band Stand/MR-184, Moskit cue, communications EMCON,
  FIRE_CONTROL registry, and enemy-aircraft rebuild are out of scope.
- A full Kh-32 population study remains separate unless it demonstrates the
  same current-product contract defect.

## Delivery

- branch: `seeker-close-a`
- PR: [#78](https://github.com/0-FLANDRE-0/Aegis_Project/pull/78), kept open
- merge/release/tag: not performed
- executable delivery: unchanged HP_A HTML ZIP
- report delivery: deterministic HTML-free SEEKER_CLOSE_A report ZIP
- next sequence after user merge: integrated baseline freeze, then
  engagement/defense OODA
