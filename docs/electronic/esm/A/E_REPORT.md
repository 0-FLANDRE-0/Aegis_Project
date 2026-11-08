# ESM_A Commit E report

## Status

- IMPLEMENTED: profile-bound DDG-119/CG-52 passive receivers, strict owner/receiver binding, receive/EA separation, damage/offline/disable gates, save/migration/reset/retire ownership, and cached unchanged-history estimates.
- TESTED: each real profile twice, cooperative raw transfer in both profile directions, synthetic ship-neutral fixture, EMCON silence, damage/offline/disable, SOV baseline, persistence and invalid-import paths.
- APPROVED: directive boundaries and predeclared constants only; the completed branch still awaits user review.
- RELEASE: false.

## Receiver adapter contract

`ShipProfile.equipment.esmReceiver` is separate from the emitter registry and from `AN_SLQ_32_EA`. It declares only the passive capability and observables supported by the common adapter. The exact public SLQ-32/SEWIP variants remain `PUBLIC_UNKNOWN`; no unpublished sensitivity or range was introduced.

| Profile | Receiver ID | Damage binding | Exact variant |
|---|---|---|---|
| DDG-119 | `DDG119_EXISTING_PASSIVE_EW_RECEIVE_PATH` | `CDC` | `PUBLIC_UNKNOWN` |
| CG-52 | `CG52_EXISTING_PASSIVE_EW_RECEIVE_PATH` | `EW` (the two registered SLQ-32 pod modules) | `PUBLIC_UNKNOWN` |

The adapter resolves the owning profile, install/enable state, explicit receiver disable, the owning ship's offline state, and its declared damage system before producing a raw DTO. Local measurements and network packets must also carry the exact receiver ID bound to the platform; a DDG/CG ID substitution fails closed with `RECEIVER_ID`. Receiver state never grants ECM transmission, and ECM decisions remain byte-for-byte unchanged when receive is disabled.

`ALL_RADIATION_SILENT` produces zero declared ship emissions while the passive receiver continues to accept a foreign RF source. Explicit disable, full receiver-system damage and owner offline state each produce zero observations.

## Lifecycle and persistence

`AEGIS_ESM_SAVE_A_1` owns bounded raw histories, the derived-contact serial, clock/frequency-reference state, unsent raw observations, delayed network packets, replay/peer state, counters and operator-only cue records. Restore validates the entire detached payload before mutation, rebases measurement/queue times to the current simulation epoch, reconstructs estimates only from saved anonymous raw history, and always restores identity as `UNKNOWN`.

Operational save/import now includes player and fleet `esmA` state. A pre-ESM save migrates to a profile-bound empty default and records `LEGACY_ESM_A_EMPTY_DEFAULT`. Unknown fields or mismatched profile/receiver data are rejected before mutation. Engagement transient reset clears player ESM contacts and runtime queues; electronic reset and physical retirement clear every owner independently. The gate confirms direct and operational round trips are exact, invalid import is zero-mutation, and reset/retire leave no queue, outbox, contact or deferred restore reference.

## Port for future receivers

A future Mineral/Band Stand adapter must provide a valid `AEGIS_ESM_RECEIVER_PROFILE_A_1`, then feed the existing anonymous raw DTO fields: receiver pose/velocity/covariance, clock/frequency-reference state, measured angles/covariance, optional measured frequency/timing/fingerprint and quality. It must use the common validator, localizer, presentation, network and cue contracts. It may not add emitter/target IDs, truth position/velocity, faction, a parallel geolocator, or an automatic identity/fire-authority path.

No SOV receiver binding is registered in this product. Band Stand, MR-184, sensors, EW and weapons remain baseline-inactive; declared physical emitters, ESM contacts and raw network reports are all zero. The complete selected SOV profile and runtime probe are exact against the merged EMCON_B baseline.

## Performance

The original fixed-step path re-solved unchanged AOA/TDOA/FDOA geometry for every retained contact at 60 Hz. Commit E caches the geometry solution by the last observation identity and updates only age/COAST covariance between observations. The cached result is exact against the uncached estimator at fresh, coast and lost ages.

At 96 contacts with three receiver observations each, the unchanged-history fixed-step measurement was median `0.0 ms`, p95 `0.10 ms`, max `0.20 ms`, below the predeclared `2.0 ms` budget. The diagnostic also records a deliberately synchronized cold recomputation of all 96 contacts at `16.4 ms`; this is a restore/all-dirty stress reference rather than the normal 60 Hz path and is retained in evidence instead of hidden.

## Gate

`E_GATE.json` is PASS:

- DDG/CG actual RF scene → raw DTO → localizer → UI/network works and repeats exactly;
- profile/runtime/receiver-ID cross-leakage is zero;
- receive and EA state are independent;
- global silence, damage, offline and explicit-disable contracts pass;
- the unregistered synthetic profile uses the common DTO, localizer and lifecycle;
- SOV profile/runtime output is baseline exact and remains inactive;
- save exact/migration/invalid-zero-mutation/reset/retire all pass;
- observer tracks, identity and automatic engagement authority remain unchanged;
- product candidate contains no diagnostic adapter and browser/page errors are zero.

Candidate SHA-256: `1f0b041b8c353f0b9014b8dd46cf144041ecb73d22698f938b1b15c87548209e` (22,182,147 bytes). Packed-main SHA-256: `f1b26391e673f7be0545f98660628f39e985a857e118277da9f62176905d46b6`.

## Unresolved

- Exact public DDG/CG SLQ-32/SEWIP receiver variants and performance remain unknown and are not asserted.
- SOV Mineral/Band Stand receive and Moskit cue/fire remain disabled for the later SOV sensor/weapon stage.
- The synchronized 96-contact cold recomputation spike is recorded above; normal cached fixed ticks pass budget.
