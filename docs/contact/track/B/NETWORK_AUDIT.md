# TRACK-B: Hawklink / Link 16 association audit and bounded proposals

This is a **read-only source audit and fixture plan**, not a claim that the proposed behavior has been implemented or tested. No browser, product change, coefficient change, expectation update, commit, or merge was performed for this audit. TRACK-C evidence lifecycle and TRACK-D lineage/integration remain out of scope. The inherited CIWS seed `419025` failure and two historical paired-observer differences remain **unapproved**.

## Pinned input and live scopes

- Work branch: `track-b-association`, parent `ee960dbb7c796e3c91cbe4b6d3d5f59948a0e561`.
- Input HTML: `Aegis_SIM_v48_WIP_TRACK_A.html`, SHA-256 `e2c1976a8a21eae6a494bf6caf0ec5b702663bd97721763ef7e92c6d6096d67a`.
- Decompressed current main: `/dev/shm/track-b-baseline-source.js`, SHA-256 `8d2de4f64cb18e3248156e36fa454daee91b5603e03fee5a8f7bd372e0d5780e`.
- All JS line numbers below refer to that **pinned current main**, not the old source fragments under `docs/multiship/`.
- Canonical network definitions are JS5012–5338. The similarly named functions around JS64798 are nested inside `mapBNativePreview`; they are not global overrides and must not be patched as the live fleet receiver.

| Live scope | Line | Owner / input / writes |
|---|---:|---|
| `heloPublishRadarPlotsE` | 4658 | Helicopter reports only received measurement position/P/domain, source `H1/H2`, sequence, original measured time; no contact/truth ID or velocity on the wire |
| `stepObserversC` | 4855 | Calls each owner's offboard drain once per fixed step; NPC local filters are predicted before their drain |
| `ingestOffboardReportC` | 4895 | Receiver-owned `observerC(r).offboard`: strict schema/PSD/time/link/sequence checks, queue only |
| `offboardPlotC` | 4910 | Converts reported meters to world XY and inflates position covariance for age; does not invent velocity |
| `acceptOffboardC` | 4917 | Chooses nearest Cartesian-NIS track, updates that owner's canonical EKF/file/hits/age, records remote timestamp |
| `drainOffboardC` | 4944 | Sequential due queue processing; no batch candidate snapshot, used set, or ambiguity test |
| `networkNisG` | 5055 | 6D reported-state NIS plus existing independent distance/speed sanity caps |
| `networkIntersectionG` | 5062 | Existing **fixed 0.5 CI**, not independent-measurement Kalman fusion |
| `networkReceiveG` | 5103 | Strict authenticated sender/packet validation before heartbeat/picture/control changes; reports processed sequentially |
| `networkFileEstimateG` | 5117 | Receiver-owned remote files; predictions to a common epoch and deterministic sorted-source CI |
| `networkAcceptReportG` | 5122 | Anonymous `(senderId,fileId)` affinity, repeated-fix status-only handling, new-source association/birth |
| `networkReconcileG` | 5140 | Remote-file to local-display association; existing row ambiguity and one-to-one local-track usage |
| `networkProtectionG` / `networkPresentationTrackG` | 5155 / 5161 | Consumers of already reconciled remote files; geometry errors can therefore affect displayed FRIEND/NEUTRAL protection |
| `networkBuildReportsG` / `networkFixedStepG` | 5175 / 5190 | Local-report production; owner clock, delayed queues and transport scheduling |
| `trackCartesianAssociationNisV33` / Cartesian update | 26202 / 26212 | Existing three-position-component NIS/update kernel; **NIS helper calls `trackEkfInit`** |
| `updateSensorTrackMeasurement` | 27603 | Actual player updater; `OFFBOARD_C` birth does not count the same first covariance twice |

`docs/multiship/C/offboard.js` is useful provenance but lacks the current ISAR dispatch/drain, current identification-evidence field, implemented-helicopter flag and TRACK-A hooks. `docs/multiship/G/network.js` contains the same canonical association/CI decisions but lacks TRACK-A trace statements and RC2 reconciliation timestamp metadata. Neither fragment may replace the current packed live function wholesale.

## Hawklink: exact behavior and failure mechanisms

The current drain is effectively:

```js
for (const q of o.offboard.queue) {
  if (!connected(q.sourceId)) continue;
  if (q.availableAtS > now) { pending.push(q); continue; }
  if (tooOld(q) || !acceptOffboardC(r,q)) o.offboard.rejected++;
}
```

The current selection and repeated-fix check, in that order, are:

```js
let match=null;
for (const [id,tr] of o.tracks) {
  const nis=trackCartesianAssociationNisV33(tr,meas);
  if (nis<=25 && (!match || nis<match.nis)) match={id,nis};
}
const existing=match ? o.tracks.get(match.id) : null;
if (existing?.observationReportsC?.remote[report.sourceId]?.measuredAtS
    >=report.measuredAtS) return false;
```

1. **Same-epoch distinct contacts can be lost as false replays.** If the first report creates/updates a nearby track and a second same-source, same-time but different-position contact selects that file, the second is rejected as `NATIVE_REPEATED_FIX`. It does **not** increment that file twice. The timestamp check follows nearest association and is not proof that the report describes the same contact.
2. **Different-epoch due reports can sequentially update one file.** There is no used-track set within a measurement cohort. Each report also sees the posterior/birth produced by earlier reports, so insertion order can change candidates and the winning file. A catch-up drain can contain legitimate multiple epochs; blocking every second update in the whole drain would also be wrong.
3. **No runner-up or reciprocal ambiguity test.** Equal/near-equal candidates choose whichever was first in map iteration. An ambiguous report can mix contact geometry and later evidence rather than being left uncertain.
4. **Broad covariance can overwhelm geometry.** Cartesian NIS has no independent separation/velocity sanity bound. A valid wire covariance near the accepted upper bound can make a distant contact have low NIS. Example: 50 km position residual with reported variance `1e10 m²` gives a one-axis NIS near `0.25`, below 25. This is an analytic source fixture, not a natural-RF reproduction or a measured incident.
5. **Surface Z is a prior, not an elevation measurement.** APS measures range/azimuth; its outgoing `positionM.z` is the surface reference. Nevertheless current `OFFBOARD_C` matching/update uses Cartesian XYZ, with no `trackMayAccept*CrossDomain` eligibility gate. A near-low AIR file can be pulled toward a surface prior. The existing 16 s AIR hold belongs to local surface-radar constraints and does not turn an external XYZ correction into an XY-only update.
6. **Age is honest but not full time alignment.** `offboardPlotC` leaves the original position unchanged, inflates XY by `age² * (12 or 180)²` and Z by `age² * (1.2 or 120)²`, and sets quality `exp(-age/8)*0.7`. These are existing uncertainty priors, **not measured velocity**. The current canonical track is normally at receiver time. Do not add truth velocity, backfill a Doppler channel, retimestamp a stale fix to now, or treat the speed prior as a hard physical maximum.
7. **Two replay guards have different scope.** Ingress rejects nonincreasing sequence per source. Acceptance rejects a nonnew fix only on the selected file. A new sequence is not an independent fix. Conversely, `(sourceId, measuredAtS)` is not a globally unique fix: a helicopter can legitimately send several contacts from one epoch. Global timestamp deduplication would corrupt normal traffic.
8. **Candidate inspection must be pure.** `trackCartesianAssociationNisV33` calls `trackEkfInit`. Normal live tracks usually already have a filter, but a future shadow/audit query must not lazily initialize or otherwise mutate native tracks. Build detached state views or initialize only in the existing native path.

Existing receiver behavior to preserve: strict seven wire fields, positive-definite 3×3 covariance, future/stale/replay rejection, 64-report queue, source capacity8, delayed availability, loss clearing queued plots, no outage buffering, original measurement age, no new remote FCS authority, original owner stores and scheduler.

## Link 16: protections already present

The current report key is a **sender's anonymous tactical file identity**, not a physical entity ID:

```js
const key=JSON.stringify([senderId,report.fileId]);
let file=[...n.files.values()].find(f=>f.sources.has(key));
```

An existing source remains attached only while domain and current geometry pass NIS36. New-source candidate selection additionally excludes a file already holding any other file from that sender:

```js
f.domain===report.domain && !f.sources.has(key)
  && ![...f.sources.values()].some(q=>q.senderId===senderId)
```

Therefore **distinct files from one sender already cannot normally merge into the same canonical remote file**. Replacing this with a blanket used set across all senders would break legitimate fusion of two allied observations of one contact. The exclusive assignment unit is the source sender/cohort; cross-sender evidence may contribute to a common file under the existing correlation treatment.

Preserved numeric behavior:

- NIS gate36, runner-up separation4 for new-source choice.
- Additional 3D position residual cap `min(2500m, 5*sqrt(sum position variances))` and velocity residual cap `min(180m/s, 5*sqrt(sum velocity variances))` in `networkNisG`.
- Reports are predicted from `stateAtS` to `now` with the existing domain process prior. `measuredAtS` controls freshness; it is not replaced by state epoch or receive time.
- Fixed weight0.5 CI in `networkIntersectionG`; sender-sorted reduction in `networkFileEstimateG`. With three or more sources the pairwise reduction has deterministic unequal effective weights; B must not silently change those weights/order or claim statistical independence.
- A new packet sequence containing the same/older source fix updates only bid/assessment/identity status; no P/time/hits refresh. That existing status policy is evidence/authority scope, not a B geometry patch target.
- Fresh2 s/coast12 s, queue bounds, packet report-file uniqueness, authenticated sender/link checks, sender-local file IDs, no remote-only automatic release.

### Remaining B association defects / risks

**Receive is sequential despite source exclusivity.** With two new sender files and two canonical candidates, the first accepted report changes the candidate estimate/source occupancy for the second. Existing source exclusivity prevents a same-sender two-to-one merge but does not guarantee permutation-invariant or least-ambiguous pairing. Preserve stable valid source affinity; shadow a cohort matrix before replacing this loop.

**Reconciliation is already one-to-one, but ambiguity is only one direction.** Current code:

```js
pairs.sort((a,b)=>a.nis-b.nis || a.id-b.id || a.file.serial-b.file.serial);
// bestByFile marks one file competing for two near-equal local IDs.
for (const p of pairs) {
  if (ambiguous.has(p.file.serial) || p.file.localTrackId!=null || used.has(p.id))
    continue;
  p.file.localTrackId=p.id;
  p.file.fused=networkIntersectionG(p.e,p.estimate);
  used.add(p.id);
}
```

Two remote files each having the same single local candidate are not marked ambiguous by `bestByFile`. `used` prevents two assignments, but the lowest score/serial winner can still be arbitrary. In particular, the chosen file's FRIEND/NEUTRAL source may protect that local track. A symmetric local-track→remote-files ambiguity check can defer this uncertain association without changing identity or CI math.

There is also an exact-boundary inconsistency: new-source receive chooses a winner only if the NIS gap is **>4**, whereas reconciliation flags a competing row only when its gap is **<4**. Any shared helper must document the existing boundary and test gap `4±epsilon`; changing it is a visible B decision change, not a coefficient relaxation.

### Correlation / lineage boundary retained for D

The receiver does not store upstream independent-fix lineage beyond its immediate sender/file/time. `networkBuildReportsG` exports local canonical estimates, not the presentation-only Link16 CI copy, which avoids directly rebroadcasting the display correction. However a locally mixed file can include Hawklink plus local measurements, and its export does not encode that covariance correlation. Repeated-source checks and fixed CI help but do **not** prove source lineage deduplication. Do not add a global lineage store, evidence expiry, new remote release authority, lifecycle redesign, or network rebroadcast protocol in B.

RC2 synthetic reconciliation metadata remains correct: `stateAtS=now`, `measuredAtS=null`, `receivedAtS=null`; its reported6D state is not six independent physical observations or a fresh local hit.

## Minimal B implementation candidates, in order

1. **Shared pure candidate result, not a shared TrackStore.** Use detached owner-scoped state/measurement views; retain actual dimension-specific NIS/distance kernel and expose eligibility, distance/speed sanity rejection, score, runner-up gap and assignment. Truth/owner/faction/contact entity IDs cannot be inputs. Shadow old/new decisions first.
2. **Hawklink simultaneous cohort assignment.** Prepare due eligible reports before mutating canonical files. Use source and original measurement epoch to distinguish simultaneous reports from successive updates; freeze the candidate state for that cohort. Enforce one report per file per cohort with row and column ambiguity handling. Keep distinct unmatched observations tentative under existing capacity/birth rules; do not force every report into an existing ID. Do not infer a scan/contact ID absent from the wire. Exact same payload/time replay within a cohort can be distinguished from different-position same-time contacts; across drains the existing repeated-fix guard must remain safe. A timestamp-only global replay cache is explicitly rejected.
3. **Hawklink surface observability / cross-domain gate.** For the known surface-prior path, use XY-only reported-position association/update and preserve prior acquired AIR Z/VZ distributions, rather than treating Z=8 as observed altitude. Reuse the existing EKF math for the correct projected observation matrix; do not fabricate polar geometry or tweak gains. New surface files may retain their existing initializer prior. This requires explicit native player/NPC fixtures before connection.
4. **Hawklink independent geometry bound.** The reviewed B design adopts the existing network association limits as explicit `SIM_TUNED` geometry sanity caps:2500 m position innovation and180 m/s radial innovation when a real radial measurement and receiver velocity are provided. Neither measurement nor filter covariance may enlarge these caps. These are game association policy, **not physical speed/range limits or RF tuning**. Validate normal coast/reacquisition against them; do not quietly use the 12 m/s covariance prior as a speed limit or weaken NIS to hide a rejected reacquisition.
5. **Link16 reconciliation symmetric ambiguity only, first.** Retain its existing `used` one-to-one logic, NIS36 and CI0.5. Add reciprocal competitive-candidate ambiguity so one local file with two indistinguishable remote files remains unassociated. Do not clear valid local IFF/own-fire evidence or rewrite remote identities. Unknown geometry remains uncertain.
6. **Link16 receive batch only if shadow fixtures demonstrate need.** Retain sender-file affinity and same-sender exclusion; compare simultaneous new-source reports from one packet against a precommit file snapshot. A deterministic bounded assignment may defer competing pairs, while two different senders may still CI-contribute to one unambiguous canonical contact. Keep `networkNisG`, `networkIntersectionG`, freshness/replay/packet/control/FCS paths byte-identical unless a separately evidenced B defect demands a minimal change.

Single indistinguishable reports from two observers cannot be proven to refer to one or two physical objects using geometry alone. A correct B result may retain uncertainty; it must not use hidden truth to force either outcome or claim universal zero false merges.

## Proposed fixtures — NOT EXECUTED in this audit

All injected data below is explicitly `DIAGNOSTIC_ONLY`, in meters/SI, anonymous reports. Fixtures must run against extracted **actual current functions** before browser/native acceptance, with source hashes recorded. No fixture changes RF Pd/noise, EKF gains or authority rules.

| ID | Input / comparison | Required evidence |
|---|---|---|
| H-B01 | Two distinct positions, same H1/time/sequence-increasing, both near the first file | Baseline false replay/loss reproduced; candidate preserves separate uncertainty instead of treating time as contact ID |
| H-B02 | Same two positions, reversed queue order | Assignment/birth/hold cause independent of insertion order where geometry is unambiguous; no number swap hidden by sorting |
| H-B03 | Two existing clearly separated tracks and two H1 same-epoch reports | Two one-to-one updates, no second hit to either file, no extra birth |
| H-B04 | One report with two near-equal candidates; two reports competing for one candidate | Row/column ambiguity recorded, no arbitrary merge or evidence copying |
| H-B05 | Successive epochs of one moving contact delivered in one drain | Legitimate ordered updates not rejected by a drain-wide used set; original measured times/age retained |
| H-B06 | Same report payload/time with new sequence; exact packet replay; distinct same-time contacts | Replay unchanged hits/P/age; distinct simultaneous contacts not globally deduplicated |
| H-B07 | Valid covariance `1e10`, 50 km residual, ordinary local P | Baseline low NIS analytically confirmed by actual function; candidate sanity gate rejects distant forced merge, with explicit reason |
| H-B08 | Prior valid AIR3D track plus surface report at same XY/Z prior8 | XY can associate if eligible; AIR Z/VZ and vertical uncertainty are not replaced by a synthetic height measurement |
| H-B09 | Coasting contact, delayed fix, normal gap and reacquisition | Original report time, age covariance inflation and reacquisition retained; no invented velocity/retimestamp |
| H-B10 | Player and NPC receiving the identical detached report sequence | Matching decision rules but separate owner stores; actual player/NPC EKF/hit differences accounted for |
| H-B11 | Truth/targetId/owner/faction poison keys, malformed covariance/time | Existing strict ingress rejection preserved; no hidden-input read by common helper |
| N-B01 | One sender, two distinct file IDs, two remote canonical candidates; reversed packet report order | Existing same-sender exclusion preserved; no two-to-one merge; ambiguous/order-dependent assignment exposed |
| N-B02 | Two senders observing one unambiguous contact | Both contribute to one remote file; no blanket cross-sender used-set rejection; exact fixed CI result |
| N-B03 | Remote F1/F2 at ±10 m with same P/velocity; one local track at0 | Baseline greedy winner reproduced; candidate reciprocal ambiguity defers, no arbitrary protected local ID |
| N-B04 | One remote file and two near-equal locals; gaps `4-eps`, `4`, `4+eps` | Existing row guard and chosen exact-boundary policy explicitly logged; no silent threshold change |
| N-B05 | Identical input estimates; repeated/older fix under newer packet sequence | CI does not halve P; hits/P/state epochs unchanged on status-only path |
| N-B06 | Broad P with residual beyond2500 m or speed residual beyond180 m/s | Existing geometry gates unchanged and no distant/opposite-velocity merge |
| N-B07 | Different stateAt/measuredAt/receive epochs; fresh/coast expiry/link loss | Existing prediction and freshness semantics retained; no stale-hit freshening |
| N-B08 | Shared-only remote file, then display reconciliation, then native VLS gate | Canonical FCS means/P/hits and SHARE-only release prohibition unchanged; no CEC/authority promotion |
| N-B09 | Mixed local/Hawklink file reexported, then repeated multi-peer reception | Record present correlation limitation; do not call unimplemented lineage handling PASS |
| BOTH | Trace OFF/ON; repeated snapshots; owner tick at1/8/16/64× | Shadow/diagnostic queries do not initialize filters, alter RNG/ticks, update hits or change assignments |

Existing useful tests to retain: `offboardFixtureC` (JS4960), `docs/multiship/G/verify_network.py` (strict packet/replay/status-only/CI/opposite velocity/delay/expiry/authority), `docs/multiship/G/verify_remote.py`, `verify_cooperation.py`, `verify_clock.py`, `docs/helicopter/F/verify_transport.cjs` (publisher quotas/queue/strict wire/no backlog), current H/L native ISAR/Harpoon tests, and TRACK-A ingress47. Their existing passes do not cover the new simultaneous ambiguity fixtures above. Old fragment-only fixtures are not proof that the packed current hook path ran.

## Kernel freeze anchors

Hashes use the exact current function scope through the next same-indent function declaration, matching the Stage-A scoped extraction convention. They are audit anchors, not runtime checks performed here.

| Scope | SHA-256 |
|---|---|
| `networkNisG` | `69fb9c1ac866cf7b235bda1ec8e712690cecfe5eddfd5274e77351c943d4d533` |
| `networkIntersectionG` | `c5c9dc1791fcbc1a197906ce7ded717f816513cbc6e7e01ef3fadad354d8c1d1` |
| `networkFileEstimateG` | `ec9557151b9f20cacdd76d495c38bbb4ecc98117ef19ad9a64a91c5dfeff2ef1` |
| `networkReceiveG` | `d8634307fbd4fd60a6887f609828e51335c11b685f0c8a033d7b2b8e572e6029` |
| `networkAcceptReportG` | `b6cc6bfb3e06ce0b11567fc332270e71315023d738a97fdbbfe1c64a621be07d` |
| `networkReconcileG` | `9936c04661aab7e47a75bb5f14818a3634cadf4ef85eb2c26231890eea371e0a` |
| `acceptOffboardC` | `7d7f5855e74c326f8464639b78d3913d703fd111784b5405273c7fd6485799fc` |
| `drainOffboardC` | `6b3960cd2af03c9913f336052ab19a683b593377424e04ad45c9f12da6d0c55f` |

Completion requires actual shadow/native evidence and affected regression comparisons. This audit alone approves no behavioral change, no legacy expectation update, and no merge.

## Manifest submitted for review after this audit

`patches-offboard.json` contains only the bounded Hawklink subset. It adds source/original-epoch cohort selection, pre-update candidate scoring, replay/ambiguity holds, and delegates direct private acceptance calls through the same single-cohort path. It does **not** implement the proposed XY-only EKF projection or any Link16 change. A surface-prior report near fresh measured AIR evidence is conservatively held rather than changing the AIR vertical filter or creating a competing surface birth there. The exact native correction/hit/age body remains the commit path for accepted assignments.

Repeated-source-epoch and fresh-AIR exclusions are **per geometry-valid candidate pair**. A different valid selected file may still receive that report. Only when no valid assignment remains does the report's blocked-candidate marker prevent a false birth. A distant existing file with broad filter covariance but failing the independent geometry check must not veto a legitimate other assignment or new contact. This is not global `(source,time)` deduplication.

The final shared B geometry policy has hard caps of2500 m position innovation and180 m/s radial innovation. It reuses the existing canonical `networkNisG` outer sanity values; no covariance can remove the caps. The initial `max(2500 m, 5 * measurement sigma)` proposal was rejected during design review **before game fixtures** because huge measurement covariance could remove its effective ceiling. That rejected proposal is not the current policy, an approved baseline, or an outcome-tuned adjustment. The reported measurement covariance, original age² inflation and native NIS remain unchanged; no RF uncertainty is reduced to force a match/rejection. An eligible native NIS with huge reported covariance and a >2500 m residual must fail the added geometry check.

For Hawklink there is no measured radial velocity on the wire, so the180 m/s radial cap does not fabricate one. The2500 m position check uses local filter state already predicted to receiver `now` and the original delayed report position. `offboardPlotC` retains its original age² covariance inflation; B does **not** add a velocity/extrapolation model, propagate a stale report using truth, or claim a new common-epoch sensor model. `commonEpoch:true` in `HAWKLINK_COHORT` means that the reports share their original measurement timestamp for assignment, not that current filter state and delayed measurement were physically retimed to a new joint epoch.

`SHADOW` preserves actual original sequential calls and evaluates native NIS once at the original point after prior commits. Its `HAWKLINK_SHADOW` records explicitly state `sequential:true`, `commonEpoch:false`; they are **not** a full-cohort counterfactual matrix. The full comparison must use independent private A/SHADOW/ACTIVE owners receiving the same injected measurement history. `ACTIVE` scores each report/file pair once against a cohort's pre-update files and reuses the same transformed report for the unchanged native acceptance body.

The manifest has passed private reversible-transform and `node --check` checks only. No HTML/product build, browser, or behavioral fixture was run by this audit lane. Root review and actual private/native fixture evidence are still required before use.

### Explicit remaining limits after the read-only prefreeze review

- `EXACT_COHORT_FIX_REPLAY` identifies an equal **reported value tuple**: source, original timestamp, position, covariance and domain evidence; sequence is intentionally excluded. The wire has no contact ID or physical-fix lineage. Equal tuples are conservatively held and never count as another independent confirmation; this is **not proof of the same physical contact or fix**. Two unresolved contacts could produce identical reported tuples.
- This value-tuple set exists only for one source/epoch cohort in one drain. Across drains the existing per-file source timestamp and current geometry are still the available guards. If a newly sequenced old report no longer geometrically matches its former file, no cross-drain contact/lineage cache proves its identity; an anonymous birth remains possible. B does not silently add such a cache, global timestamp deduplication or TRACK-D lineage protocol, and does not claim universal replay/duplicate-birth closure.
- The fresh-AIR safeguard uses the existing `trackHasAirObservationFC` hold predicate. The16 s hold and its expiry are unchanged. B does not implement a new XY external-report EKF kernel or promise permanent vertical protection after that existing predicate expires.
- Geometry-valid replay and fresh-AIR exclusions remain **per pair**. A different valid selected file wins; an unrelated distant file with broad filter P cannot veto it. Unassigned rows with a valid-geometry blocked candidate are held without birth. This intentionally preserves uncertainty where the wire cannot disambiguate a repeated epoch from another nearby contact.
- Local state/filter covariance, reported measurement covariance, original measured/received epochs, and anonymous sender IDs remain separate concepts. No target truth, hidden owner/faction, inferred velocity, new timestamp or identity authority was introduced in this adapter.

The native fixture lane has separately reported passes for per-pair replay, distant-replay/new-birth and original Hawklink delay/age² behavior. Those are **direct anonymous native ingress fixtures**, not natural-RF or complete regression evidence; use their recorded source/product hashes and final current-SHA reports for acceptance. This audit lane has run no additional browser and changed no module or patch during this prefreeze review.
