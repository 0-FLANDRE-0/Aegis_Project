# RF attribution and SAM physical-subject audit

**Read-only investigation and diagnostic proposal; no browser/test/product change.** R1/R2 products, sources, raw results, expectations and tolerances are untouched. The reported natural-13 outcome delta motivates this review; this document does not prove an association swap, wrong-body fuze actuation, or the cause of that delta.

## Source provenance and scope

Line references use the actual frozen B input `/dev/shm/track-b-stable-base.js`, SHA-256 `616cb07bd7443031c36eece9419c4b7e249eee5d8e3494ed4539683a5b07e8be`. R2 ACTIVE is `Aegis_SIM_v48_WIP_TRACK_B_STABLE_B.html`, SHA `c8a9266fe12d6543cf09a1e851af5a0c717e73117945291c5bb5babc9670d584`, main SHA `18cd0131dd6ce8d41d66fb7afe470334f27b6bdb5ff0137e8a9cad15328ff2d1`; see `BUILD.json`, `SOURCE_PROOF.json`, `SCOPE_VS_B.json` here. The R2 scope receipt reports 189 protected/161 nested protected symbols, forbidden changes/additions empty. In particular it independently hashes these unchanged kernels:

| Kernel | Equal before/after SHA-256 |
|---|---|
| `shipboardRadarEchoFieldWip13B13` | `2af5d61df70790096111bb6e95a9a09633e8d01620ccc27b9fffef48c7caf947` |
| `updateMissileBodyB3` | `ed94c9c270d0739ccaad07fa123a0c465dcd5e49d881ef360781fa6d224626e7` |
| `applyInterceptResult` | `66aaa8fa5688a3e60c43673b925bdd0ef8ed2f7b207c55e946abb484ef3f8ecd` |

The investigation concerns existing RF/observation/physical-weapon boundaries, not new AI or a proposal to tune their models.

## 1. What target information each consumer actually uses

| Existing path | Source and actual behavior |
|---|---|
| Standard/ESSM launch | L39366/L39755 stores the selected combat track as `assignedTargetId`. This is a track identifier, not automatically a physical-object identifier. |
| Explicit file transfer | `wip121TransferEngagementMemory`, L14019–14030 can transfer assignments during an existing track-file transfer. Thus the assignment is not absolutely immutable. |
| Native launcher DL | `weaponLinkB3UplinkPayload`, L42892–42902 copies measured track kinematics, covariance, quality/classification and sample/state steps. It does not send a truth object/ref. Receiver snapshot L42904–42912 and local cue L42992–43002 feed missile observation state. |
| Normal v1 guidance | `getGuidanceTargetStateV1`, L43309–43364 selects SARH/ARH RF EKF, received DL and retained memory. `getMemTargetStateV1`, L44483–44503 propagates the last received/observed fix. |
| Private ideal-observation exception | `_v1FindTarget`, L43075–43078 calls the physical resolver, but the nearby `_wip75DeterministicSarhState`, L43292–43305 is explicitly a private diagnostic surrogate. It must not be used to claim normal gameplay guidance follows hidden coordinates. |
| ARH legacy mirror | `_v1UpdateArhMeasurementCore`, L44386–44396 sets `seekerLockType='RF_EKF'` and **`seekerLockId=null`**. A valid ARH estimate need not identify a canonical physical object through that legacy ID field. |
| Fuze physical selection | `updateMissileBodyB3`, L47663–47684 selects a separate local `killTarget`. With physical NPC ships present it first calls `navalFuzeTargetD`; otherwise/failing that it prefers a non-null legacy seeker-lock ID, then assigned track ID via `truthObjectForTrackV27`. |
| Nearest-flight-body branch | `navalFuzeTargetD`, L6670–6675 scans native flight bodies, excludes self/same owner/dead, and returns the nearest within 2,200 m. This branch means the fuze is **not always fixed to the launch track's original physical object**. |
| Physical reference resolver | `truthObjectForTrackV27`, L26606–26627 first reads `tr.truthRef ?? trackTruthRefIndexV27.get(trackId)`. If present, it looks up that exact AIR/ASM/SURFACE object. If absent and the track exists, it transiently chooses a nearby physical AIR/ASM object using the current estimated position/velocity and covariance-bounded gates. The transient result is not stored in the track. |
| CPA/signal/burst | The selected `killTarget` supplies relative geometry at L47706–47739. At L47893 the normal four v1 SAM profiles use **`samFuzeSignalSweepA(m,killTarget,…)`**; the legacy `_wip99Stage2CandidateDecision`/`_wip99FuzeDetectionInfo` is an alternate path, not sufficient instrumentation for today's normal four SAMs. |
| Actual Pk/damage | L47979–47989 calls `applyInterceptResult(pk,killTarget,…)`; aircraft treatment L48031–48036 likewise uses the selected physical body. Physical truth here is an allowed fuze/damage boundary, not sensor information. |
| Separate WIP112 system effect | `wip112ResolveInterceptorTarget`, L22799 resolves assigned track again; the `_deathReason` setter in `wip112InstallInterceptorObserver`, L22800–22802 passes that result into `wip112RecordFragmentSystemDamage` on `PROX_DETONATION_*`. Its physical subject is not proven identical to the earlier `killTarget` by the source. |

Two distinct structural hypotheses therefore exist, neither proved to occur in the R2 battle:

1. A **legacy truth-linked** canonical file could consume observations produced by a different physical reflector while its reference remains fixed. Normal guidance would follow the observations, whereas a resolver with the retained reference would still select the original body.
2. An **anonymous** file has no such fixed binding. Its current KF can resolve transiently to one body while the missile's own ARH/SARH estimate follows another return/composite. The nearest-flight-body override and separately resolved WIP112 subject add further branches that need actual object-identity evidence.

Do not assume hypothesis 1 applies to the natural-13 fixture: its native spawn path does not call `_wip75SyncTrack`, starts at zero tracks, and ordinary RF/visual anonymous ingress creates no truth index. `updateSensorTrackMeasurement` L27851–27860 reserves/binds truth only when `meta.truthRef` is actually provided; normal `updateVisualDetection` L29615–29643 supplies only anonymous optical measurements and an observed category. Read the actual reference/index presence rather than inferring it from the existence of `assignedTargetId`.

Another observation worth testing, not fixing: `samFuzeSignalSweepA` L283 onward maintains signal energy per **physical target object** in `m._fuzeSignalChannelsA` (WeakMap), while L47894 onward latches `_fuzeStage2Detected`/`_fuzeStage2DetectionSnapshot` on the missile. If the native selected physical body changes during an encounter, record the actual channel/first-detection/trigger/Pk subjects and values. Do not invent or reset a channel, and do not tune the signal threshold to make a desired outcome.

## 2. Exact physical-object → anonymous-plot boundary

`physicalRfReflectorRegistryWip13A2` L31011–31032 creates physical reflector descriptors with private `_truthObject`, `_physicsKind`, RF source/seed and geometric fields. `shipboardRadarPhysicalSceneWip13B13` L31093–31098 caches the non-sea scene per band/fixed step. Receiver-local `shipboardRadarEchoFieldWip13B13` L31099–31131 computes native beam/LOS/propagation/clutter, one Pd draw and its actual noise samples, then emits an allowlisted anonymous echo at L31127. That echo contains no `_truthObject`, physical entity ID or semantic collection tag.

**Actual model limitation:** this shipboard echo function iterates extraction candidates and pushes one echo per detected `q.ref`. It does not merge two discrete ASM into a range/angle/Doppler resolution cell. Range resolution affects the local clutter calculation; it is not itself a discrete-return merger here. Do not invent a multi-object “merged contributor” list for an own-SPY echo, or claim the runtime merged those signals because their truth positions were close. Distributed clutter contributes native background energy separately.

`shipboardRadarEchoToAirPlotWip13B13` / `…ToSurfacePlot…`, L31143–31144 create new anonymous objects. Own-SPY unified collection L27192–27213 passes those AIR plot references into the actual global/focused association and then `updateSensorTrackMeasurement` (L27320–27341). Thus an exact diagnostic WeakMap can follow those references without reverse-engineering physical identity from nearest truth.

Other copy boundaries must be covered or labeled UNKNOWN:

- SPQ AIR goes through the new-object allowlist `spq9bAnonymousPlotContractV34` (L34535) after echo conversion (L34669–34679).
- NPC `observerExtractC` L4940–4949 makes an extra object spread for AIR origin metadata. Merely wrapping the shared conversion loses that final new reference; propagation is required at the actual clone point.
- SPY residual processing false alarms are created by `spyFalsePlotV31` without a physical reflector; label the actual constructor origin as processing false alarm, not the nearest ASM.
- Accepted UPDATE/CREATE should use the **actual incoming measurement reference** and actual returned/accepted canonical track ID (`updateSensorTrackMeasurement`, L27851–27923; existing TRACK-A event already supplies the incoming payload). Never call native NIS/update/predict again to obtain an attribution.

There **are** real multi-return mergers elsewhere: `_sarhClusterEchoes` → `_sarhMonopulseMeasurement` L43611–43640, `_arhClusterEchoes` → ARH monopulse L44110 onward, ASM `asmSeekerCompositeReturns` L31259 onward, and helicopter `apsMergeMeasurementsF` L4525–4528. For those, capture the actual native cluster/member references once. Do not apply their grouping rules retroactively to a different receiver's shipboard plots. The natural-13 ownship question initially needs own-SPY/SPQ and actual interceptor receiver attribution; APS/Hawklink expansion is not required merely to claim coverage.

## 3. Minimum diagnostic-only implementation proposal

This section is a proposal, **not implemented**. Every hook would run only in a private diagnostic copy, original call once with unchanged `this`/arguments/return. No production/tactical consumer reads the maps and no new property is attached to a native object, plot, track, packet or wire schema.

1. **One local RF emission observer.** At the existing echo-creation site where both native `q.ref` and the just-created echo exist, store `WeakMap<echo, provenance>` and `WeakMap<physicalObject, diagnosticSerial>`. Record native single-source object key, receiver/time/dwell, and the already-computed geometry/signal/SNR/background primitives. Snapshot physical values there, before later movement in the same tick. This is not a second RF calculation. An outer wrapper of `shipboardRadarEchoFieldWip13B13` alone cannot recover the lost `q.ref` reliably; nearest-truth reconstruction is not an equivalent replacement.
2. **Exact reference propagation and actual acceptance.** Wrap the real echo→plot converters/allowlist copies and, where needed, observe the NPC spread once. Propagate only in a test WeakMap. Observe existing actual candidate/assignment/accepted-update events or the original ingress function once, recording plot key ↔ accepted canonical ID, precomputed native NIS/model/time/covariance information. An unattributed copy remains UNKNOWN; do not “repair” it with a guessed physical object.
3. **Actual interceptor subject chain.** Sample new missiles' assigned ID and existing ref/index presence without invoking a resolver. Observe the native returned guidance state/DL sequence, actual `navalFuzeTargetD`/truth-resolver returns where naturally called, and **`samFuzeSignalSweepA` input target and returned detection/energy**. Observe actual `applyInterceptResult` and `wip112RecordFragmentSystemDamage` target arguments. Correlate same missile/step using object keys; distinguish selection branch, first detected channel and trigger/damage subject. No diagnostic call to any getter that advances a seeker, creates a filter or resolves a body a second time.
4. **Actual seeker composites when needed.** Wrap original SARH/ARH pool/cluster/monopulse functions to retain member-reference sets and accepted measurement provenance in private WeakMaps. Existing physical echo `_debugSourceId` fields may be read only inside this diagnostic physical boundary, never copied into tactical measurements. Member powers may be logged as already generated; inferred weights must be labeled offline derived unless the native local weight itself is observed.

The first item requires a small declared **test-copy local observer insertion**, because `q.ref` is local and deliberately erased. If preserving native function-body bytes is absolute even in a diagnostic copy, this attribution is not available through a plain outer wrapper; report that limitation instead of silently changing the contract or claiming exact physical attribution. A future instrumented copy needs its own source hash, exact hook diff, reversible source proof and native-function hash/restoration policy. Product R1/R2 files remain unchanged.

## 4. Required interpretation and controls before conclusions

- With identical physical signal inputs, anonymous IDs can exchange meanings without a structural one-to-one violation. A diagnostic physical key is an evaluation label, not information available to association. Distinguish statistically ambiguous measurements from a demonstrably separated, strongly supported contradictory assignment using the **actual native measurement model/S and epoch**, not a truth-distance threshold invented to blame an assignment.
- Preserve all same-epoch native assignments, HOLDs, actual observed measurements, incoming DL fixes, seeker accepted member sets and physical fuze subjects. First show which input or physical subject differs; do not jump from a KILL-count delta to “association swapped IDs.”
- Verify instrumented vs frozen OFF signatures on the same executable fixture: call counts/order, native RNG/ticks, actual outcomes/resources, selected/held pairs, track/filter states, wire/object enumerable keys, query purity and restored ENV status. Any difference caused by instrumentation invalidates attribution until explained. Record raw failures, not selected matching fields.
- Preserve ship ownership/independent observations, EKF, RF Pd/noise/RCS/beam, IFF/ROE/authority, guidance, fuze accumulation, Pk/damage and all tuning. If the actual failure belongs to a physical-subject consumer rather than association, document its exact path and request a separately scoped decision; do not repair it inside this association stabilization candidate.

No extra original-raid, natural-13, R1/R2 or full regression run was launched for this audit. No existing raw result was rewritten. The present evidence does not support “no ID exchange,” “fixed truth binding caused the R2 failures,” or an automatic weapon/fuze change.
