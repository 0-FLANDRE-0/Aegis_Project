# EMITTER_A Commit D — Sovremenny inactive registration report

## Status

- IMPLEMENTED: existing SOV_A sensor registration metadata is exposed through the common equipment registry as eleven inactive records.
- TESTED: enemy and neutral deployment, zero physical emission/ESM source, zero own receiver/detection, inactive attack runtime, unchanged DDG/CG behavior and RNG.
- APPROVED: metadata registration only; no SOV electronic capability is activated.
- UNRESOLVED: SOV radar/EW implementation and verified RF values remain future work, outside EMITTER_A.
- RELEASE: no release/tag; branch checkpoint and final candidate product only.

No power, frequency, beam, RPM, Pd or detection value was invented. Every SOV
row retains the existing model-registration system, NATO name, role, position,
confidence and provenance while explicitly setting `installed=false`,
`active=false`, `physicalEmission=false`, and
`outputKind=REGISTERED_INACTIVE`.

See `D_GATE.json`, `SCOPE_D.json`, and `changes-D-active.diff`.
