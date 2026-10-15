# Stage B — airborne surface-search radar adapter (design gate)

This file records the preimplementation contract. Stage B production code must wait until Stage A's IFF/airborne-detection gate passes. There is no offboard source or Hawklink delivery in Stage B; those belong to Stage C.

## Ownership and API

`h.radarOn` is the saved operator setting, initially false. `heloSensorStateE(h).radar` is transient simulation-owned state (the existing helper owns its parent map): scan angle/revolution, private RF attempt ledger, private RNG, attempts/plots/statistics, current-step anonymous plot batch. The radio-transmitting flag is true only for an airborne, alive, powered helicopter whose radar setting is ON. The signature is `heloRadarFixedStepE(dt)` from the existing fixed simulation step; no renderer or requestAnimationFrame integration is allowed.

`heloRadarSnapshotE(h)` returns detached sensor status/statistics and render sweep geometry. `heloRadarPlotsE(h)` returns a detached current-step anonymous measurement batch. The future optional callback `heloPublishRadarPlotsE(h, plots)` runs once per helicopter per fixed step and receives a bounded batch; Stage C packages each measurement into the existing offboard schema. Every B measurement has exactly:

```
{positionM:{x,y,z}, covarianceM2:[9 finite row-major SI values],
 domainEvidence:{surface,air,missile,background}, measuredAtS}
```

There are no target IDs, reflector IDs, truth references, class flags, source identities, target truth velocities, sourceId, or report sequences in the batch. Sequence/source are the responsibility of C. Current-step plot arrays contain no older cached positions; no target-persistence file or perfect track exists onboard the helicopter in this stage.

## Reuse and physical boundary

The current `spq9bSurfaceAttemptWip13B1(obj)` is a legacy hardwired active-ship adapter. Calling it directly or iterating only `surfaceContacts` would bypass the established unified RF-scene contract. Stage B instead reuses `shipboardRadarEchoFieldWip13B13` (receiver-relative range/RCS radar equation, sea/terrain clutter, weather, terrain LOS, noise) and its anonymous measured-observable surface evidence gate. The legacy SPQ surface sea-state/rain calibration is retained as an explicitly SIM_TUNED surface-mode term.

New shared front-end controls are strictly opt-in and default to the existing behavior. They may act on physical reflectors only inside RF synthesis. Stage B needs:

1. A precise swept-centre attempt gate: only reflectors whose bearing crosses `(previousAngle,currentAngle]` may make a detection attempt. A private RF-key/revolution ledger prevents duplicate attempts after target or observer motion. This ledger stays behind the physical echo boundary and is never returned in echoes, plots, renderer state, UI, or offboard reports.
2. APS-specific propagation-height selection for surface reflectors: the tagged 30m mast approximation is used for strict `radarHorizonKm(heloMSL,mastM)` gating and terrain/horizon propagation. Echo/plot altitude remains the anonymous surface reference, never the true mast height.
3. A wide SIM_TUNED surface downlook envelope instead of SPQ's narrow shipboard paired vertical lobes. It must cover the same surface at 50m and300m and preserve air/background rejection in the anonymous surface extractor.
4. An explicit per-helicopter RNG passed via `rngState`. An unknown `radarId` without this would fall back to SPY RNG, which is prohibited.

APS band/nominal transmit scale/SNR reference/max range/scan period/errors/RCS/mast height are all `SIM_TUNED`; no actual APS-153 hardware power, frequency or detection distance is claimed. X-band-like weather/RCS treatment is an assumption. The existing `radarHorizonKm` approximation is reused.

## Measurement and covariance

The sensor reports noisy range and azimuth only. A two-dimensional surface extractor maps noisy slant range into horizontal range using the helicopter's own MSL altitude and a fixed surface reference of8m; it must not use truth target height or measured-elevation noise to produce output position. If sigma starts in slant range, propagate it using `d(horizontal)/d(slant)=slant/horizontal` and impose the configured minimum horizontal range.

With `c=cos(measuredAz)`, `s=sin(measuredAz)`, `rr=horizontalRangeSigmaM²`, `tt=(measuredHorizontalRangeM*azSigmaRad)²`, and `nn=navSigmaM²`, the row-major Cartesian covariance is:

```
[rr*c*c+tt*s*s+nn, (rr-tt)*c*s,       0,
 (rr-tt)*c*s,       rr*s*s+tt*c*c+nn, 0,
 0,                0,                 surfaceZSigmaM²+nn]
```

The measured position is in simulation world-frame SI metres, z=8m. Covariance is symmetric positive definite with diagonal>=1 to satisfy the unmodified offboard port. The navigation error is sampled consistently with the added covariance. Longer range increases transverse uncertainty. Domain evidence comes from anonymous measured surface/air/missile/background features and the surface-only waveform; air and missile scores remain low for accepted surface plots. No air tracks or air reports are produced.

## Stage B gate

- Real native RF scene, same controlled surface target, helicopter50m vs300m. Demonstrate the expected horizon expansion without the selected range cap hiding it. Use deterministic controlled geometry and multiple seeds where reporting stochastic detection onset.
- Surface mast horizon gates before attempt; existing ship RF behavior is unchanged when B is absent/OFF.
- At most one detection attempt per physical reflector per full360° revolution, including adjacent-step beam overlap and moving observers/targets.
- Private RNG reproducibility, independent of SPY/SPQ/navigation/weapon RNG; fixed-step equality under1×/8×/16×/64× frame accumulation.
- SNR/Pd worsens with smaller cross-section, greater sea state, and heavier precipitation in representative otherwise-identical geometry.
- Native AIR/ASM returns never produce surface reports; background/terrain do not form fake ships.
- Measurement poison fields do not cross the exact output contract. Covariance is finite/symmetric/SPD and transverse variance grows with range. Plotz does not reveal truth mast height.
- Radar ON marks emission only in airborne flight, radar OFF stops attempts/plots immediately. Rendering and snapshot reads do not advance scan, RNG, attempt counters or simulation state.
- No `configureOffboardSourceC`, `ingestOffboardReportC`, Link16, sensor-onboard perfect truth, remote fire control, weapon, sonar, ESM, FLIR, ISAR, fuel, or air-detection behavior is added at this gate.
