# ESM_A Commit C report

## Status

- IMPLEMENTED: separate anonymous `ESM_RAW` transport, observable-only correlation, cooperative AOA/TDOA/FDOA constraints and deterministic fallback.
- TESTED: DDG/CG, packet validation/order/duplicate/latency/disconnect, fingerprint separation, geometry/clock/reference degradation, unchanged native RF/RNG and SELF/TRACK reports.
- APPROVED: not yet; intermediate checkpoint.
- RELEASE: false.

## Transport

`AEGIS_ESM_RAW_NETWORK_A_1` is not a NETWORK_G observer-track report. It carries only strict ESM raw DTOs and uses the existing authenticated-friendly membership, link availability, radio horizon, latency, queue and coast-time contracts. Packet sequence and observation IDs are deterministic replay protection, not emitter identity. Remote reports enter the same `esmAcceptRawA` path as local reports and never call `observerC`, track association, IFF, identity, ROE or fire-control functions.

Existing NETWORK_G SELF/TRACK report construction and receive functions are byte-identical to merged EMCON_B. EMCON radio policy is unchanged; radar radiation silence does not silently disable the communication link.

## Estimator

Correlation gates measured band/class/family, registered frequency and scan observables with covariance. Receiver-motion Doppler is removed from the frequency fingerprint using the measured receiver velocity and bearing; the predeclared source-motion nuisance prevents false precision. Ambiguous candidates are not force-merged.

TDOA uses arrival-time, clock-bias/drift covariance; FDOA uses receiver frequency-reference and source-motion nuisance covariance. Constraints exceeding the existing 4 km geolocation quality bound are not used. Two-receiver TDOA remains region-valued. Three non-collinear receivers, or valid crossing AOA plus time/frequency constraints, may produce a point only through the same final 95% ellipse gate. Poor timing/reference quality falls back to AOA without inventing precision.

## Gate

`C_GATE.json` is PASS for DDG-119 and CG-52, twice each. It demonstrates:

- native RF detections, bearings and EW RNG remain exact;
- raw packet truth-field audit passes;
- same-source reports combine and a distinct fingerprint remains separate;
- replay, out-of-order, malformed/truth-bearing and disconnected packets fail closed;
- two-receiver TDOA does not create a point; three-receiver TDOA constrains a region;
- moving-receiver FDOA is consumed only with explicit uncertainty;
- clock/frequency degradation widens or removes constraints;
- SELF/TRACK reports and observer-track counts do not change;
- repeated runs are exact.
