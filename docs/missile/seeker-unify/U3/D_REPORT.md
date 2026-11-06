# SEEKER_UNIFY_U3 Commit D report

## Status

| State | Result |
|---|---|
| IMPLEMENTED | Existing Mahalanobis-gated passive-RF candidates are ranked by `d² + ln(det(S))`; deterministic ties use observable measurement fields only. |
| TESTED | Static scope/gate audit, synthetic ranking and tie cases, 12 equipment scenes, four natural ASM scenes, four `CONFIRMED_ONLY` scenes, SHADOW equivalence, ACTIVE deterministic repeat. |
| APPROVED | D gate passed. SHADOW is equivalent to Commit C and all ACTIVE differences originate in the approved candidate policy. |
| UNRESOLVED | General emitter registration remains deferred to `EMITTER_A`. `CONFIRMED_ONLY` performance remains `UNVERIFIED`; only limited feature-state scenes ran. |
| RELEASE | Not released. Branch checkpoint only. |

## Selection contract

`asmPassiveRfMeasurementB2` retains its existing family, band, geometry, LOS,
sensitivity, and Mahalanobis gates. Only candidates which have already passed
those gates reach the new selector. In this producer the angular innovation
covariance is diagonal, therefore:

```text
det(S) = Sa × Se
score  = d² + ln(det(S))
```

The lowest score wins. Exact-score ties use, in order, the candidate's measured
`d²`, covariance determinant, frequency, bearing, elevation, angular sigmas,
SNR/power and observable classification strings. Source IDs, platform IDs,
emitter coordinates and truth positions are not selector inputs. Candidates
that are observationally identical produce the same tactical measurement.

The selector consumes no RNG. It preserves the pre-existing deterministic
measurement-noise hash after a candidate has been selected.

## SHADOW → ACTIVE gate

| Check | Result |
|---|---:|
| Representative scenes per branch | 20 |
| SHADOW real-candidate comparisons | 857 total (synthetic + real) |
| SHADOW legacy/new ranking differences | 467 |
| SHADOW equipment output vs Commit C | 12/12 exact |
| SHADOW natural ASM output vs Commit C | 4/4 exact |
| SHADOW `CONFIRMED_ONLY` output vs Commit C | 4/4 exact |
| ACTIVE equipment scenes changed | 6/12 |
| ACTIVE natural ASM scenes changed | 3/4 |
| ACTIVE `CONFIRMED_ONLY` scenes changed | 0/4 |
| ACTIVE repeated equipment input | exact |
| Browser errors | 0 |

The representative difference was an S-band `SHIP SEARCH RADAR` candidate
with lower `d²` versus an IJ-band `SURFACE SEARCH RADAR` candidate with a much
smaller innovation covariance. The legacy selector chose the former; the new
score correctly chose the latter. This is the intended policy change.

All four natural scenes retained their final outcome: two ship hits, one
pre-existing Kh-32 pass/miss at 60 km, and one unchanged fourth scene. Three
scenes changed acquisition timing or closest approach. Consequently downstream
physical RF/RNG call order also changed in ACTIVE. The selector itself consumed
zero RNG; SHADOW retained Commit C RNG and tactical output exactly.

## Scope preservation

- Mahalanobis gate expression: byte-identical before/after.
- 17 protected functions or source segments: byte-identical, including emitter
  registration, RF gain/frequency physics, CUE update, HOJ, Harpoon seeker,
  launch gates, and save/restore.
- New distance/range constants: none.
- Save schema change: none.
- Emitter registry generalization: not performed (`EMITTER_A`).

## Evidence

- `D_GATE.json`
- `D_SCOPE.json`
- `BUILD_D_SHADOW.json`
- `BUILD_D_ACTIVE.json`
- `DIAG_D_BASELINE.json`
- `DIAG_D_SHADOW.json`
- `DIAG_D_ACTIVE.json`
- `changes-D.diff`
- `changes-through-D.diff`
- `passive_rf_d.js`
- `run_d_contract.py`
- `verify_d_scope.py`

