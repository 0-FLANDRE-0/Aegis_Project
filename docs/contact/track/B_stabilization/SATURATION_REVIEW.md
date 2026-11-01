# Saturation review — actual native Hungarian, isolated JS

This lane runs **no browser** and changes no production module, mode, EKF P/R, sensor/RF/weapon/physics coefficient or existing regression. `test_saturation.cjs` loads the candidate policy source and extracts the real game's `bridgeMasterEMinCostAssignmentV35` byte-for-byte. The covariance-disparity family also calls the extracted native Cartesian NIS and native SI conversion functions; the other families are declared association-cost graph fixtures. They are not natural-RF/SNR or gameplay/FPS measurements. C55 and SPQ shadow-only scope is unchanged.

## Initial defect reproduced

Frozen B module SHA `3a4bac5b74c03033490e92f5d3d69cadd4e4214309e7479afcdfe3c5cf954e46` holds an entire connected component whenever either side exceeds12. All28 fixtures at13/16/32/64 reproduce it, with zero native Hungarian calls:

- Sparse chains with clearly separated diagonal winners: every update held.
- Dense graphs with unambiguous diagonal winners: every update held.
- Position/measurement covariance-disparity graphs with native NIS and unique zero-residual diagonal: every update held.
- A two-contact ambiguous island attached to many clear contacts: every clear update held too.
- A globally resolvable greedy trap embedded among clear contacts: every update held.
- Dense equal-cost and unbalanced equal-cost graphs: HOLD is appropriate here; arbitrary numeric-ID matching would be wrong.

Evidence: [saturation-baseline.json](evidence/saturation-baseline.json). This is `BASELINE_DEFECT_REPRODUCED`, not approval of that policy. Ignoring every normal measurement in a large component can prevent native track refresh; a low runtime cost alone does not make that acceptable.

## Proposed certificate: sound, intentionally conservative

Let the native rectangular Hungarian optimum have full objective **B**, including every row's real or dummy assignment. Let `m[r]` be each row's minimum cost over **all real and dummy columns**, and `L=sum(m[r])`.

For a selected real edge `(a,b)`, forbid it only in that row and compute:

`L_alt = L - m[a] + min(cost[a][j], j != b)`.

Every feasible matching omitting `(a,b)` costs at least `L_alt`: allowing different rows to reuse the same columns is a relaxation, so independent row minima can only underestimate the objective. Therefore `L_alt > B + delta + epsilon` proves that edge occurs in **every** near-optimal matching within the declared objective tolerance. It is safe to retain that edge. Failure to prove it is not proof of ambiguity; conservative HOLD is the correct result for this bounded method.

Important implementation conditions:

1. Count dummy costs in both `B` and row minima. Comparing a real-only objective to a full objective invalidates the proof.
2. Solve the native global problem first. Local mutual-best/row-gap peeling can reproduce the original greedy trap even when local gaps look strong.
3. Hold uncertified rows, including unmatched rows, so unresolved dense traffic does not become a burst of new tentative births.
4. Protect certified columns from the held-track set. A losing row's candidate list must not erase another row's mathematically certified edge.
5. Preserve exact tie handling. Equal-cost matchings must not be resolved by track number, insertion order or a fabricated confidence.

Exhaustive proof checks use deterministic seed `0x51a7c0de`:120 small graphs,504 enumerated near-optimal assignments,96 reference certificates, zero unsound certificates. Each core was also embedded inside a connected13-row graph and run through the **actual candidate solver**:1,236 returned edges checked, zero unsound releases. These are finite counterexample checks supporting the mathematical argument, not a proof of every arbitrary implementation.

## Candidate result, preliminary source-level validation

Candidate policy SHA `ec66a28a8bb92888228a45a6a626007f288c440b3054e2e203730bbe9e8e4c71` passes32 cases. It keeps the exact small-component alternate-forbid path, uses one native Hungarian call plus lower-bound certificates for larger components up to128, and explicitly bounds computation above128. This is **candidate module validation**, not final packed-build/native-game acceptance; rerun on the final source hash if root changes the candidate.

| 64-row family | Frozen B selected / held | Candidate selected / held | Native Hungarian calls |
|---|---:|---:|---:|
| Sparse clear chain | 0 / 64 | 64 / 0 | 1 |
| Dense equal cost | 0 / 64 | 0 / 64 | 1 |
| Dense clear diagonal | 0 / 64 | 64 / 0 | 1 |
| Native-NIS covariance disparity | 0 / 64 | 64 / 0 | 1 |
| Local ambiguous island | 0 / 64 | 62 / 2 | 1 |
| Embedded greedy trap | 0 / 64 | 63 / 1 | 1 |
| More equal-cost rows than tracks | 0 / 64 | 0 / 64 | 1 |

13/16/32 produce the corresponding same patterns. For the embedded trap, the one uncertified but globally optimal edge remains held because the row relaxation is loose; no old greedy steal is reinstated. This is a disclosed conservative limit, not a reason to lower the ambiguity threshold.129/257 connected clear-chain and dense-equal cases produce explicit `COMPUTATION_BOUND_HOLD`, with zero solver calls and no exception. No selected row/column also appears in the held sets. All tested input graphs remain unchanged and reversed edge order yields identical results.

Evidence: [saturation-candidate.json](evidence/saturation-candidate.json). Source extraction pins native Hungarian SHA `17df9b438b348a39973865188f38771575537b96cfb832a8a5d55239a41c3341`; all extracted kernel/unit hashes and input provenance are in the JSON.

## CPU and alternatives

For `r` rows and `c` real columns, the native rectangular matrix has `c+r` columns. One native Hungarian call has worst-case `O(r²(c+r))` work and `O(r(c+r))` matrix storage. The row-minimum certificate adds `O(r(c+r))` work. The old per-selected-edge alternate solver is up to another `r` Hungarian calls, or `O(r³(c+r))`; retaining that exact method only for small components avoids a large quartic tail.

Mutual-best peeling is cheaper but unsafe without a global certificate. Dual/reduced-cost alternating-path certification could release more edges than the row bound, but needs additional correctness proof and implementation complexity. The current lower bound is a reasonable bounded first step: ordinary clear components update, true or unproved ambiguity stays held, and one global optimum prevents greedy steals.

Isolated host timings for64 rows (9 timed calls after warmup):

| Family | Mean ms | p95 ms |
|---|---:|---:|
| Sparse clear chain | 0.63 | 0.65 |
| Dense equal | 7.45 | 8.40 |
| Dense clear diagonal | 4.98 | 5.96 |
| Covariance disparity | 0.57 | 1.21 |
| Local ambiguous island | 2.56 | 3.24 |
| Embedded greedy trap | 0.37 | 0.97 |
| Unbalanced equal | 3.87 | 4.46 |

Other browser lanes were allowed to run on the host. These timings include candidate graph handling and native solver work, exclude fixture construction, and are **not game FPS or mobile performance**. Dense64 work is materially more expensive than the old blanket HOLD's roughly2–3 ms graph handling. Natural saturation/pilot and existing mean/p95 game-loop checks remain necessary; correctness PASS must not be substituted for that evidence.

### 128-row bound: explicit60 Hz budget concern

The same frozen `ec66a28a…` module was also measured at its128-row limit:2 warmup calls, then5 timed calls per family, one actual native Hungarian per call. All four association-correctness checks pass. The timing result is **not a60 Hz budget PASS**:

|128-row family|Selected / held|Mean ms/call|p95 ms/call|Compared with16.7 ms|
|---|---:|---:|---:|---|
|Sparse clear chain|128 / 0|2.96|4.02|Below|
|Dense clear diagonal|128 / 0|20.88|28.33|Exceeds|
|Dense equal|0 / 128|36.88|42.31|Exceeds|
|Weak ambiguous island|126 / 2|18.58|26.80|Exceeds|

With five samples, the reported nearest-rank p95 is the largest timed sample. Dense-equal128 also spent22.50 ms in the native Hungarian during its first validation call; clear-diagonal's native call was0.35 ms, so its total20.88 ms mean shows substantial graph/matrix/metadata handling cost as well. These single-call tails must not be hidden by average FPS. Multiple such components or owners in one fixed step could add their costs. This lane made **no automatic reduction of128, ambiguity threshold, P/R or any game coefficient**. The bound/cost tradeoff and any further optimization require root review and natural workload evidence.

Evidence: [saturation-128.json](evidence/saturation-128.json). The weak island has a genuine near-optimal alternative (core off-diagonal1.2 versus diagonal1.0, total alternative gap0.4 within delta1); its two rows stay held without arbitrary IDs or new births.

## Reproduction and scope

```sh
node docs/contact/track/B_stabilization/test_saturation.cjs --phase baseline --samples 5
node docs/contact/track/B_stabilization/test_saturation.cjs --phase candidate --module docs/contact/track/B_stabilization/association.js --samples 9
node docs/contact/track/B_stabilization/test_saturation.cjs --phase candidate --module docs/contact/track/B_stabilization/association.js --expect-module-sha ec66a28a8bb92888228a45a6a626007f288c440b3054e2e203730bbe9e8e4c71 --sizes 128 --families sparse_chain_clear,dense_diagonal_clear,dense_equal,weak_ambiguity --no-cap-cases --samples 5 --out docs/contact/track/B_stabilization/evidence/saturation-128.json
```

The original baseline28-case evidence predates the four explicit129/257 cap cases; rerunning the current script also includes those cap cases. The covariance-disparity fixture declares input variances `[4,25,225,2500] m²`; it does not alter production P/R or assert a new relation between RF SNR and covariance. This review does not validate normalized-likelihood semantics, time alignment, missing covariance/epoch policy, IFF/authority, actual caller birth suppression, natural saturation or C55/SPQ behavior. Those belong to the other native/runtime lanes and final complete report. No release or merge is approved here.
