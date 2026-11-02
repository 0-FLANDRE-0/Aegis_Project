# R2 residual refinement: independent review

This review changes no product, native function, NIS, δ1, P/R, sensor, identification, weapon, AI or physics coefficient and runs **no browser**. R1 source/raw evidence remains unchanged. R2 candidate source SHA is `499198392351c415cbf54d35d5731f393f650c6e1b00a694dd714ee318ed03bb`; this is pre-product pure-graph evidence, not a natural-battle result or release approval.

## Sufficient-condition argument

1. The original native Hungarian solution is computed globally first. Its LB-certified set **C** is present in every alternative within the declared full-objective tolerance, including the dummy costs used by that certificate. C is fixed; it is not guessed by mutual-best or a new greedy pass.
2. Refinement runs only when the parent assigns every row to a real column, C is nonempty, and some rows remain. Removing C's rows/columns from the **actual eligible edge graph** leaves independent residual components. Every remaining parent edge still exists in that residual graph.
3. The parent matching restricted to a residual component is optimal there. Otherwise replacing that component with a cheaper feasible matching while keeping C and other components would contradict the parent optimum.
4. For full/same-cardinality alternatives, every residual row must still be assigned. Component cost differences cannot compensate each other negatively: each component's parent restriction is already optimal. Consequently a small component's exact alternative-forbid certificate can be applied within that component without enlarging δ.
5. R2 accepts only child-returned edges that equal the original parent's selected edge. If the child chooses a different parent edge, that component is rejected instead of silently changing the matching. Certified columns are kept out of the held set.
6. Unaccepted residual rows/columns remain held. A residual component exceeding12 is not recursively solved as another large problem. Partial parents and zero-C large components do not enter this refinement. No unresolved row is turned into a new birth by this policy.

This argument preserves the existing **full/same-cardinality exact policy**. The frozen exact routine treats alternatives with fewer real assignments and dummy choices separately; the review does not invent a new clutter/unmatched prior, claim a calibrated probability, or generalize the result to every differently sized matching. Full-S secondary likelihood contracts are also separate from the metadata-free/identical-S NIS tests below.

## Actual first13 graph recovered

The separately preserved first13 graph is ordinal8 of the35 logger records: step158,13 plots,13 track candidates,86 eligible native edges. Several other calls at the same step have8/7/6 plots, so identifying the case by step alone is insufficient. Exact equality with `FIRST_13_GRAPH_158.json.nativeGraph` identifies the actual case.

| Same unchanged native input | R1 | R2 | Frozen exact NIS reference |
|---|---:|---:|---:|
| Accepted edges | 3 | 13 | 13 |
| Held rows | 10 | 0 | 0 |

R2 retained the3 LB certificates and accepted10 edges from one10-row residual component using the original small exact branch. There were12 actual native Hungarian calls: one global parent plus the10-row base and its10 edge-forbid alternatives. No large residual recursion occurred. The result is `LARGE_COMPONENT_REFINED_EXACT`; all13 accepted edges equal the unchanged parent/exact-reference edges. Edge-order reversal and bijective row/track-ID relabeling preserve the result; inputs are unchanged.

## Captured-input coverage:14 complete,21 unavailable

The logger has35 **records**, but only14 contain a complete `pairs` array.21 have `pairs:null`; some of those still contain selected output, which is not enough to reconstruct all candidate costs. The old graph comparison treated null as an empty input. This review does **not** count those records as replay PASS and does not infer missing NIS from selected output, before states or truth.

All14 complete graphs passed strict replay, retained every existing R1 edge, and agreed with/subset the frozen exact reference for this recorded input. All14 passed edge-order and row/ID-permutation checks, one-to-one, input immutability and held-row safeguards. The21 unavailable records remain explicitly `NOT_REPLAYABLE_MISSING_PAIR_GRAPH`.

The summary is therefore deliberately `INCOMPLETE_CAPTURE_COVERAGE`, with `availableInputTestsStatus: PASS`. This is an input coverage limitation, not an R2 policy assertion failure. A new guarded capture would be needed to claim35 full replays. No R1 logger/raw file is changed to conceal the limitation.

## Exhaustive and boundary tests

The separate `tests_r2.cjs` extracts real native Hungarian SHA `17df9b438b348a39973865188f38771575537b96cfb832a8a5d55239a41c3341`. The frozen exact reference is R1's original legacy-forbid routine with **only its computation ceiling12→128 in a private test VM**. Original cost values and all production source bytes remain unchanged.

- 200 deterministic small full-matching cores (sizes2–6, seed `0x7232c0de`) were embedded in connected13-row graphs. Every candidate edge was compared with exhaustive near-optimal full/same-cardinality core matchings and the real native exact reference.
- 2,265 R2-returned edges were checked, including311 additions relative to R1: zero unsound edges. Every embedded case recovered the exact-reference result, retained existing R1 certificates and was invariant under row/ID relabeling.
- Dense equal-cost13 with C=0 stays wholly held, with one global call and no refinement.
- A partial13-row/12-column parent stays held, with no refinement and one global call.
- A20-row graph with one fixed edge and a19-row ambiguous residual retains that one edge and holds the other19. It performs one global call and does not recurse into the oversized residual.

These are declared pure cost graphs and captured native costs, not regenerated sensor measurements or new natural-RF/weapon evidence. The first13 graph fix does not by itself prove that R1's observed combat regression is restored; that requires the separately planned actual-game comparison.

## Complexity and remaining risk

The global solve and128 cap are unchanged. Added exact work is limited to independent residual components of at most12 rows **and**12 columns. Each such component costs its base plus at most12 original forbid solves; no n-sized repeated global alternate pass is added. The asymptotic large-component quartic extension is avoided. The old128 dense single-call latency concern remains a separate measured risk; this graph correctness review does not claim an FPS improvement.

Raw result and provenance: [solver-r2.json](evidence/solver-r2.json); command log: [tests-r2.log](evidence/tests-r2.log). The source-selection precondition attempt is preserved under `evidence/attempts/selector-precondition/`. No old expectation, R1 result, or permissible tolerance has been updated.
