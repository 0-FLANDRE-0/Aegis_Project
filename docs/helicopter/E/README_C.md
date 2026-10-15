# Stage C: Hawklink

The pinned builder applies A → B → C. Stage C was activated after both preceding validation gates passed. Its first complete gate uses HTML SHA256 `843c86ac5de6f99ee3b9c24dcf425a79e5c0a55a11f0bc1cdec7c7c1546b25ac`: 42 native browser checks and 32 isolated transport checks passed. Exact evidence is in `evidence/stage-c/native/stage-c.json` and `evidence/stage-c/transport/transport-unit.json`; final release evidence is rerun against the final HTML.

## Interfaces and ownership

- `heloHawklinkBeforeObserversE(dt)` runs once per `SIM_FIXED_DT` before `stepObserversC(dt)` drains incoming reports. It resolves the original mother by `h.ownerEntityId`; FLEET selection does not transfer aviation ownership.
- `heloPublishRadarPlotsE(h, plots)` accepts only current-step anonymous measurements `{measuredAtS,positionM,covarianceM2,domainEvidence}`. Stage C packages strict `AEGIS_OFFBOARD_PLOT_C_1` reports with receiver-local source IDs H1/H2 and monotone per-source sequences. No target ID, truth reference, target velocity, or friendly identity is sent.
- `heloHawklinkResetE(r)` removes the owned H1/H2 source entries and pending reports. Existing receiver tracks retain ordinary coast/drop processing; they are not deleted on a link transition.
- Per-aircraft link transient state lives in the existing `owner.aviation.heloSensorsE` map via `heloSensorStateE(h)`. Link state is not a saved flight attribute. The root sensor save migration persists only IFF/radar operator toggles.

## Link policy

All new numeric parameters carry `SIM_TUNED` source tags. Values: maximum distance 160 km, latency 0.4 s, mother antenna height from the existing navigation-radar hardpoint, recent-transmit count over the last 10 s. These are simulation settings, not asserted Hawklink performance.

Priority for displayed unavailability reason: ONBOARD/LOST, MOTHER_UNAVAILABLE, RANGE, LOS. Mother radio availability also follows the existing fleet limits: combat-center damage below 80% and mast damage below 85% (`SIM_TUNED`). Available airborne helicopters connect regardless of radar ON/OFF: a connected radio can carry zero radar reports. User policy update: EMCON currently suppresses radar only. Hawklink remains connected in EMCON, like the existing fleet network. A future communications EMCON policy governing both Link 16 and Hawklink is deferred.

Use `radarHorizonKm(heloMSLAltitudeM, motherAntennaMSLAltitudeM)` and planar SI distance, with strict finite positive heights. `configureOffboardSourceC(motherRuntime, {sourceId,connected,latencyS})` runs every tick so any newly disconnected source purges the existing transport queue before its next drain. Link transition logging occurs only when availability/reason changes.

Every disconnected plot is discarded immediately, without a backlog or replay. Connected plots go through `ingestOffboardReportC`; its unchanged strict schema, covariance validation, 15 s maximum measurement age, queue bound, sequence replay protection, and receiver covariance aging remain authoritative.

## Preserve weapon and network authority

Pure OFFBOARD_C files already fail `networkLocalAgeG` and native SAM fire-control source checks, and are excluded from `networkBuildReportsG`. Preserve these existing gates and do not connect helicopter sources directly to the fleet network.

Direct track-based ARM Harpoon currently has a provenance gap. Add a local-observation freshness gate to the track branch of `harpoonGateA`, including the final release recheck. Leave coordinate-search route release unchanged. Check the separate `observationReportsC.localAtS` timestamp rather than the latest source label: a genuine fresh local+remote mixed file remains eligible even when the most recent update is external. Pure remote files have no local timestamp. A remote report never freshens that timestamp or grants local fire-control authority. The foreign native observer successful-measurement path gains the same timestamp update already present in the player native observer, so real local reacquisition refreshes provenance for both owners.

## Own-navigation surface-return blanking

Stage B physically observes the mother just like any other surface reflector. Stage C uses only the anonymous measured position/covariance plus the mother's own navigation and profile hull bounds to blank reports inside its known hull footprint with a 3-sigma projected uncertainty margin, capped at 75 m per body axis (`SIM_TUNED`). This avoids a zero-range self track without target IDs, faction hints, or IFF labels. Nearby unresolved contacts inside the same small uncertainty footprint are also blanked; distant contacts remain unchanged. The generic offboard schema and ingestion port are unchanged.

## Required verification

1. Two real airborne helos each register H1/H2 under their mother; FLEET selection does not move them.
2. Connected anonymous radar reports reach the ordinary receiver port only after configured latency; no truth/target IDs enter the message.
3. Mother EMCON leaves Hawklink connected and reports still arrive. Same-tick offline equipment, LOS loss, and max-range loss each disconnect before pending transport drain. Pending packets are purged and disconnected new packets are discarded without backlog.
4. Reconnection transmits only newly measured plots, with monotone sequence numbers and no repeated measurement confirmation.
5. With ship active radar disabled and one offboard-only surface file, link loss leaves its last estimate coasting, then naturally drops it; no fresh measurement is forged.
6. Per-helo radar OFF sends no plots but does not disconnect an otherwise available radio.
7. Shared-only files cannot release Harpoon/SAM/GUN through native/FLEET paths; coordinate-search Harpoon path still passes its original conditions. Fresh local reacquisition can restore the original release path.
8. Changing IFF or radar flags remains per aircraft; resets/imports clear link transients/sequence map and do not replay pre-import plots.
9. Snapshot link summaries are detached, finite and bounded. Render/camera/radar-visualization calls do not modify link counters or simulation state.
10. At 50 m versus 300 m the same surface target has different geometric horizons through Stage B; radar and link envelopes are independently checked so a radar detection outside Hawklink LOS is lost to the mother until a new connected observation.
