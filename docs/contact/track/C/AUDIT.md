# TRACK-C source and information-contract audit

Baseline: main `d328c941d71e39ef616d4136c70bed0eeebe7f06`; packed main SHA `6163ada1a49dc86ce8b179b81650fa2da78ecc8d9273015142a721748abf6a64`. `SOURCE_AUDIT.json` supplies function occurrence, original main line, source SHA and lossless source excerpt. Line numbers below refer to that baseline uncompressed main, not the packed HTML line.

## Native stores and lifecycle

| Route | Native ordering / lifecycle | C behavior |
|---|---|---|
| Player canonical TrackStore | `updateRadar:40206` ages sensorAge and TTL, predicts, accepts RF, applies existing miss/revisit MEMORY/COAST/REACQUIRE policy and drop gates. Accepted RF resets native age/TTL; no received packet is invented as an independent observation. | Read existing fields. No new lifecycle engine or cadence. |
| NPC owner TrackStore | `stepObserversC:5148`: owner clock, age/TTL, prediction, independent owner's sensors and auxiliary reports. Native memory age >4s, coast >.65s; existing age/covariance drop policy retained. | Each owner remains separate; no global merged truth store. |
| Confirmation | `updateSensorTrackMeasurement:28008` retains player accepted-plot hit policy. `observerAcceptPlotsC:5048` retains NPC .15s independent-hit spacing and 3-hit confirmation. | `lastIndependentFixAtS=null` when not stored. A sequence number or receipt is not called a new RF look. |
| C55 files | `c55StepSensors:8163` (NPC) and player occurrence: predict state and native axis covariance; age; expire after 2s; run RF; correlate existing CMS veto; coast/confirmation checks; local defense winner selection. Native 5 hits, .32s confirmation span and .22s release freshness unchanged. | The view labels C55 as a local RF file, not a canonical track. Owner/mount namespaces remain independent. |

`trackCLifecycleViewC()` returns native confirmation/lifecycle, age/TTL, measurement/filter epochs, contributors and evidence. This is a detached read-only compatibility view. `sample()` changes diagnostic storage only and is opt-in; it never ages tracks, predicts, samples RF or grants authority. It does not infer absent timestamps.

## Observation and receipt epochs

* RF accepted measurement: use `_lastMeasurementStep`, or existing `lastMeasurementS`. The after-action trace records the actual current filter epoch and accepted anonymous measurement.
* Remote report: `observationReportsC.remote` supplies its existing measured and received times, source and sequence. Legacy contributor records with no receipt expose null and explicitly say it is not stored.
* Network estimates preserve their native estimate epoch. A replay/reconciliation status update is not elevated into a measured timestamp or independent hit.
* ISAR remains evidence only. No position hit is fabricated from classification information.
* `trackHasAirObservationFC:27913` and `trackNoteAirObservationFC:27916`: native 3D AIR evidence is valid for `TRACK_HARD_TTL=16s`; an accepted 3D observation clears the 2D surface prior. The 8m surface motion prior is a model constraint, never measured elevation. These functions are byte-identical.

## Identification and protection evidence

| Field | Existing origin / lifetime / revalidation | Inheritance |
|---|---|---|
| classification | Existing measured domain/kinematic classifier and confidence; reflects observations and can change. | Not copied by alias. Not an identity or permission. |
| identity | Existing resolver combines first-party own-launch correlation, authenticated IFF, operator annotation and existing kinematic hostile-intent policy. | New file resolves its own evidence. No IFF nonresponse promotion. |
| `_operatorIdentity` | Explicit persistent annotation; legacy surface IFF also writes this field. Original source does not always distinguish the two. | No new expiry or alias copy. View identifies this provenance limitation instead of inventing an operator timestamp. |
| threatStatus | Existing threat assessment / BDA / kinematics. Separate from classification and identity. | Only the original unique, observation-qualified engagement-memory path can migrate BDA. |
| engagementAuthority | Existing resolver (`updateTrackOperationalStateA3` occurrences at 13729/26683/65286) checks identity, freshness, FCS, mode and protections. | Never copied from old track. Uncertain aliases cannot transfer FCS state. |
| AIR IFF | `heloIffStepE:4782`; authenticated noisy-geometry response; native expiry. `heloIffExpireE:4774` removes expired AIR IFF, reverts FRIEND to operator identity or UNKNOWN, withholds authority. | Native expiry unchanged. Manual FRIEND remains persistent. |
| Legacy surface IFF | `stepFriendlyIffF:2893` every30 fixed ticks: geometric measured reply gate; sets `iffF`, FRIEND and persistent `_operatorIdentity`. No native expiry. | Difference from AIR IFF is documented, not harmonized. |
| Own Harpoon correlation | `harpoonTrackIdentityC:5905`; actual first-party launch receipt plus radar measurements, native coast/reacquisition limits. No datalink/truth position disclosure. | C view only reads `_harpoonOwnC` and stored authority reason. It never calls this mutating correlator. |
| C55 ownFireEvidence | Existing actual-own-launch RF partition in `navalCiwsSourcesD` and both local sensor paths; persists with native file lifetime. | Non-own measurements cannot associate with own-fire files and vice versa. No proximity-based own identity creation. |
| C55 protectedIdentity | Existing geometric CMS protection veto or actual-own-launch partition. Native file lifetime; no stored confirmation timestamp. | Read as existing latch. C adds no expiry, promotion or protection removal. |

The current native resolver can infer ASSUMED_HOSTILE from a confirmed missile-like threatening measured trajectory. This is the unchanged existing kinematic policy; it is not a consequence of missing IFF and C does not add such a rule.

## Alias, FCS and BDA

Original `wip121TryAliasReacquire` (NPC14060 / player50033) used an old engagement coast file's observed position and velocity gates. Its native path can transfer BDA, autonomy response, in-flight owner track references, SPG reservations/servo target, close-in engagement references and network alias. Source at `wip121TransferEngagementMemory` (NPC14171 / player50278) is preserved.

C adds a guard before that original transfer: the new file must be a fresh confirmed observed file; no FRIEND, NEUTRAL, TRAINING_TARGET or valid friendly IFF protection; exactly one old predecessor passes the unchanged position/velocity gates; no competing live confirmed successor passes the same gates. Ambiguous, tentative, memory or reacquiring cases do not transfer BDA/FCS. A unique match still uses the original transfer; no RF, EKF, permission or weapon coefficients change. The old classification, identity, operator annotation, IFF and authority are not copied.

## C55 and SPQ AIR candidate

* SPQ AIR: calculate existing native AIR NIS/cross-domain gates and R4 geometry/evidence at one prediction epoch, call common R4 solver with unchanged δ=1, consume each accepted observation/file at most once. Preserve existing SPY-preferred no-extra-hit policy. HOLD cannot create a replacement file from the held observation.
* C55 own and NPC: preserve the old physical distance eligibility gate exactly. Contrary to the first audit assumption, the existing axis KF stores `_c55P`. The candidate derives NIS from that native position variance plus the same measurement variance/R floor as `c55UpdateFile`; no covariance or gain is invented or changed. Native axis independence remains as implemented.
* C55 cost is `sum((measurementAxis-stateAxis)^2/(Paxis[0]+max(.5,Raxis)))`. Measurement fallback `[36,100,100]` is copied from the existing corrector, not a new tuning. The dynamic solver gate admits every distance-eligible finite cost and adds no NIS rejection threshold. Invalid native covariance or an unchanged solver sentinel-domain overflow yields conservative diagnostic HOLD.
* Common solver δ=1 and large-component R4 policy remain unchanged. No coefficient selection from combat results. All RF synthesis and native correctors are byte-identical; association may legitimately change later tracking/RNG call branches, which must be assessed in actual combat.
* SHADOW freezes native prediction state/covariance, computes the same proposals and compares native assignments without consuming proposals. Only the ACTIVE candidate changes assignments. Production diagnostics default OFF.

## After-action physical lineage boundary

The standalone product never stores physical target labels. A test-build callback at the existing RF echo append and C55 accepted-measurement boundary records a private physical label outside plot objects. Anonymous cloned RF plots are joined by exact measured polar fingerprint + owner + sensor + tick; collisions are reported as ambiguous, not resolved with nearest truth. Accepted association and before/after KF epoch are then joined by the original diagnostic callback. The full test probe diff and original function hashes are retained per run.

Accepted measurements, no-echo/NO_ASSIGNMENT diagnostics, unresolved fingerprints, native memory reacquisition, native DROP/reinitialization, overlapping FIRM files, live physical reassignment and reciprocal same-epoch ID swaps are separate categories. Physical labels and native target-alive status are AFTER_ACTION_TRUTH only. They are never read by association, KF, classification, authority or AI. Independent owners and distinct C55 mount stores are not duplicates.

ASM egress classification reads already accepted native seeker signals and existing seeker state only in the recorder. Decoy-only accepted Nulka/chaff signals with retained RF guidance support DECOY_LURE; search/reacquisition or an invalid track supports SEEKER_LOSS; mixed/ambiguous or other signals are OTHER with the observed reason. This is an audit classification, not a seeker correction or proof of a unique counterfactual cause.

## Scope proof

`SCOPE.json` and inverse patch verification establish that removing the inserted module and reversing the five reviewed function edits restores the complete baseline packed-main source byte-for-byte. RF physics, native KF prediction/correction and coefficients, IFF/ROE resolver, missile/gun/damage/AI physics and save schema remain unchanged. The test-only physical callbacks do not ship in the standalone HTML. Native OFF/ON and R4/SHADOW final-state/private-RNG controls are required before claiming that the recorder is passive.
