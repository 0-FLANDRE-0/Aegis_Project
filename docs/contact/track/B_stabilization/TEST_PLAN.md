# TRACK-B stabilization: independent policy and native fixture plan

This lane changes test files only under `B_stabilization/`. Existing B solver47,
native90 and supplemental14 assertions, helpers, fixture inputs and expected
values remain immutable. No browser is launched until root grants a lane.

The proposed evidence path keeps the original NIS assignment and original
`ambiguityDeltaNis = 1`. A HOLD can be removed only when a valid, same-dimension,
same-epoch native innovation-covariance likelihood independently supports that
same assignment. A conflicting likelihood, missing evidence or unresolved contact
keeps HOLD. No policy coefficient is selected to match seed419012.

## Test boundaries

- Pure tests load the actual candidate product module and the original native
  `bridgeMasterEMinCostAssignmentV35`, not a second association solver.
- Native fixtures call actual `spyGlobalAssignmentsV36`,
  `surfaceAssignmentsPreferEstablishedWip13B14`, `observerAcceptPlotsC` and the
  existing offboard ingestion paths where integrated. Their anonymous inputs are
  measured geometry or explicitly declared receiver-owned estimator initial
  conditions. No physical target, faction, source key or truth reference enters
  the association API.
- Diagnostic queries cannot initialize an EKF, update a predicted state, advance
  a clock, call a lazy geometry getter, resample a sensor or consume RNG.
- Measurement evidence describes the model actually consumed by native NIS:
  AIR four rows; surface position-only two rows even if the input plot includes
  Doppler; surface radar two/three according to actual Doppler use; Cartesian
  reported-position three rows without claiming physical 3D RF measurement.
- Full browser/native execution is a separate step from syntax/unit checks. Native
  anonymous-ingress fixtures do not establish natural RF/Pd or combat success.

## Policy cases prepared before implementation

| Group | Evidence | Expected result |
|---|---|---|
| P01 | Existing NIS winner, gap below1; same-epoch covariance likelihood strongly agrees | Release HOLD to the existing winner only |
| P02 | Same NIS graph; likelihood favors the other assignment | Keep HOLD; never replace NIS winner |
| P03 | Identical innovations and covariance | Keep HOLD independent of ID/insertion order |
| P04 | Same evidence but only age/hits/confirmation/source/identity labels differ | Labels alone cannot force resolution |
| P05 | Same covariance at every pair in a full two-by-two permutation | Log-determinant sums cancel; keep the original near-equal HOLD |
| P06 | Evidence absent, invalid/nonfinite, wrong dimension or inconsistent epoch | Original HOLD behavior, no made-up defaults |
| P07 | One decisive component and one genuine ambiguity | Resolve only the decisive component |
| P08 | Strong evidence outside original NIS gate or2500m/180mps sanity | Still rejected |
| P09 | Actual receiver velocity and surface position-only observation | Match native row contract; no invented Doppler/elevation |
| P10 | Same graph/evidence reordered, IDs renamed | Semantic decisions invariant; no numeric-ID tie break |
| P11 | Frozen input, returned-object mutation, repeated queries, forbidden RNG/time | Pure, detached, deterministic; input/RNG unchanged |
| P12 | Oversized indistinguishable257-plot component | Still bounded HOLD, no duplicate birth or exception |

Additional bounded-component peeling will receive separate positive/negative
cases only after root publishes its policy. The existing oversized-component
checks are not silently removed or weakened. Distinguishable and truly identical
large components must not be conflated.

## Native scenarios

1. **Declared covariance-positive fixture, not seed419012:** precise4000m file and
   broad5000m file; anonymous surface measurement near4001m. Native NIS must prefer
   the precise file by less than1. Native S evidence must support that same file.
   Query-only assignment must not change either file; actual surface acceptance
   updates exactly that file once and creates no tentative duplicate.
2. **Covariance conflict:** broad estimate produces the lower native NIS while
   normalized likelihood favors the precise file. This remains HOLD, unchanged
   files and no false birth. It tests the guard against replacing the NIS winner.
3. **Equal-S two-file ambiguity:** identical predicted states, P and measurement;
   existing HOLD/no birth survives. ID/order permutations preserve that result.
4. **Surface prior and missing dimension:** change the stored estimated altitude
   and8m surface prior only. A position-only association remains two-dimensional;
   no fabricated z or zero-Doppler evidence resolves a real ambiguity.
5. **Freshness/epoch:** same exact geometry but mismatched actual measurement
   epochs, an absent epoch or delayed offboard position. Original transport age,
   replay guards and age-squared covariance remain unchanged; unknown alignment
   cannot be promoted into precise evidence.
6. **Independent owners:** actual private observer files receive the same anonymous
   batch. Selection in one owner cannot read/update another owner or global store.
7. **Hawklink preservation:** original per-pair replay, stale/future limits,
   reported covariance and two-contact cohort proofs continue to run unchanged.
8. **C55/SPQ AIR boundaries:** existing live policy remains unchanged unless root
   explicitly integrates a reviewed batch policy. Shadow output is not a live
   implementation claim and cannot be used to waive natural combat differences.

## Real419012 and paired combat evidence

The first actual419012 HOLD is around1796/29.9333s SEARCH_HORIZON; both files were
updated by HIGH_THREAT at1795. Native NIS is approximately1.4913444 versus1.153679
and measurement R dominates parts of the state covariance. The older002
VISUAL/broad/aged state at29.0s is not the state at this first HOLD. The separate
covariance-positive fixture therefore cannot be called a419012 reproduction or
proof of repair. Actual final cue references, timestamps, hits, ammunition,
physical states and all private/global RNG are compared without ignoring fields.
No expected value is updated by this lane.

## Execution and reporting

1. Pin candidate module/native Hungarian/source hashes; run standalone policy
   tests without a browser. BLOCKED is distinct from PASS.
2. With a root-granted browser lane, execute old native helpers unchanged and new
   fixtures separately for old B/candidate OFF/ON. Save raw results before any
   auxiliary query. Confirm exact per-fixture OFF/ON passive/P/RNG state.
3. Preserve every failure/precondition error and source hash before changing a
   fixture. A native matrix that does not meet its stated premise is a fixture
   non-reproduction, not an approved product PASS.
4. Root runs natural combat/regression separately. Existing strict differences,
   including419012 and paired physical/observer differences, remain unapproved
   until the same actual scenario establishes a cause and satisfactory result.

## Additional actual-matrix checks (root-authorized after SHADOW proof)

`test_support/native_metadata.js` is separate from the already executed five-case
helper. All products receive the same actual native inputs and120 additional
fixed ticks, including baseline builds without the new evidence API. Missing API
is reported as unsupported; it does not bypass the native fixture work.

- Capture the actual matrix passed to `_matInv` during exactly one original
  AIR4, surface-position2 or reported-Cartesian3 NIS evaluation. A pass-through
  wrapper invokes the original once and is restored in `finally` before evidence
  queries and the protected ENV status check.
- Compare the product evidence helper's log determinant against independent
  Gaussian-elimination algebra on that captured matrix (new diagnostic tolerance
  `1e-10`; no original regression tolerance changes). This is matrix-algebra
  validation, not a second sensor, NIS or association model.
- Confirm nonzero receiver position and velocity, all AIR rows, reported
  off-diagonal covariance, input/prior preservation and the distinction between
  a reported3D position and a physical3D radar observation.
- Actual delayed offboard covariance retains its native age-squared inflation;
  mismatched measurement/prior epochs, missing receiver velocity and a surface
  prior supplied as Cartesian physical elevation remain ineligible.
- A true three-row surface-radar callback with measured Doppler is queried
  through the actual common surface-assignment API. It must not receive a
  two-row position-only likelihood certificate. Its near-equal pair remains HOLD.

The first SHADOW run at57f3d3ea…936ff is retained in `evidence/native-shadow/`.
It proves original-B behavior preservation for the first five scenarios and
actual positive proposal logs. A later integration guard correction receives
new product hashes and fresh SHADOW/ACTIVE evidence; it does not replace or
retroactively relabel that earlier source epoch.
