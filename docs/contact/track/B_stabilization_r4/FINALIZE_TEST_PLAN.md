# R4 actual-finalizer behavior and integration test plan

The isolated native-function matrix has completed; native integration below is a separate planned requirement. Product/core/expectation editing is outside this test's scope.

## Isolated actual-function matrix

Frozen B main SHA: `616cb07bd7443031c36eece9419c4b7e249eee5d8e3494ed4539683a5b07e8be`. Inputs are the root-frozen R4 ACTIVE/SHADOW packed HTMLs. `tests_finalize_r4.cjs` validates unique canonical AST scope and native quality/sea-clear equality before executing the real native functions. It does not apply a patch or generate HTML.

Each case runs all four legacy/stabilization ACTIVE/SHADOW combinations and AUTO/MANUAL/SEMIAUTO contexts. Cases include both TRACK_REACQUIRE and PRECISION_REACQUIRE:

- foreign accepted non-reacquiring file, one and repeated successful returns;
- no pre-existing reacquiring property;
- foreign already-reacquiring first and second hit, and a complete two-hit sequence;
- scheduled own first/second hit and complete two-hit sequence;
- null and undefined owner, preserving the original diagnostic/native path;
- tentative/unconfirmed file, keeping its native quality/confirmation behavior;
- fallback expected revisit and explicitly supplied zero revisit;
- existing/no sea-impact inference, preserving native clear/restore callback behavior;
- ordinary TRACK_REVISIT/TRACK_CONFIRM/HIGH_THREAT/MISSILE_SUPPORT/SPG_HANDOFF/PRECISION_LOCK/SEARCH_HORIZON, firm and already reacquiring.

For conditions outside the precise guard, compare the **entire** output against the unmodified B native function with no field exclusions, plus native dependency call sequence. For a guarded condition, the oracle is the **unmodified native ordinary-return branch** (TRACK_REVISIT, or PRECISION_LOCK to preserve the existing precision confirmation side effect). Only the oracle task-provenance label is restored to the real waveform and then checked explicitly against the real input; it is not silently excluded from comparison. Native input measurement/filter references and content, actual task fields, return reference and dependency call ordering are independently checked.

Quality is the actual native equation evaluated with declared fixture covariance metrics. Those fixture metrics are not product coefficients or a new RF/EKF approximation. The test cannot infer real sensor performance from them.

Executed commands:

```bash
node docs/contact/track/B_stabilization_r4/tests_finalize_r4.cjs --candidate Aegis_SIM_v48_WIP_TRACK_B_STABLE_D.html --out docs/contact/track/B_stabilization_r4/evidence/finalize-native-vm.json
node docs/contact/track/B_stabilization_r4/tests_finalize_r4.cjs --candidate Aegis_SIM_v48_WIP_TRACK_B_STABLE_D_SHADOW.html --expect-candidate-main-sha 2ca44bf9914907e9f3c294791bc2d34431013e9045cfb9b19adf069db8e1f730 --out docs/contact/track/B_stabilization_r4/evidence/finalize-native-vm-shadow.json
```

Each packed input passed 3096 checks / 600 native function transitions. See `FINALIZE_DESIGN_REVIEW.md` for pins, boundaries and counts.

## Native integration, not replaced by the VM matrix

1. Freeze the exact R4 HTMLs/module/patch/function hashes. Keep R1–R3 products/raw/expectations unchanged. Verify source scope/mode normalization and legacy SHADOW equivalence before interpreting changed ACTIVE results.
2. Run the same actual native battle with the causal finalizer observer. At each corrected event verify actual foreign owner, reacquisition task kind and before non-reacquiring state; after the accepted update verify no new reacquiring flag. Existing own scheduled and already-reacquiring first/second transitions must remain intact. Null-owner diagnostic fixtures must retain original behavior.
3. Before interpreting the observer, require complete same-product OFF/ON native/passive/RNG/association/sample/final-state equality and source receipts. Preserve every mismatch/drop/fault. First captured event is bounded by the observer window; do not call it the first global divergence without earlier coverage.
4. For natural-13 compare actual first native divergence and each per-target native terminal result, own damage/survival and resource use against frozen references. Retain unresolved threats and failures. Removing a false recovery state can alter later native scheduling/process uncertainty and outcomes; report those rather than claim global P/RNG invariance inside a corrected case.
5. Execute existing native/domain/UI/weapon/IFF/EW/air-contact/paired/world120 regressions required by the root plan. Guard-absent scenarios and SHADOW should preserve exact reference outputs. Actual success→failure or strict-state differences are reported without approving expectations or adjusting RF/KF/AI/weapon coefficients.
6. Keep original strict failures, seed419025, seed419012 and original-raid limitations distinct from this consumer-metadata fix. A passed finalizer matrix is neither evidence for a wrong-body fuze hypothesis nor approval of unrelated contact/weapon outcomes.

No browser run, physical model simulation, full ENV remeasurement or original-raid follow-up was performed by this test author.
