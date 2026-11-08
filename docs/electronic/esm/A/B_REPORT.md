# ESM_A Commit B report

## Status

- IMPLEMENTED: strict anonymous raw DTO, historical receiver state, bounded history, deterministic AOA likelihood, coast/lost lifecycle.
- TESTED: DDG-119 and CG-52 native detection/bearing/RNG equivalence; strict validation; localizer geometry; real receiver-to-contact path.
- APPROVED: not yet; this is an intermediate branch checkpoint.
- RELEASE: false.

## Boundary

The native RF hit decision and its calls to `observerRandomC` / `observerNormalC` are byte-for-byte the predecessor calculation and execute in the same order. A stateless hash supplies only the new clock/frequency measurement perturbations; it does not advance game, observer or EW RNG.

The strict DTO carries the receiving friendly platform/receiver, its measured pose/velocity and covariance, angular measurement/covariance, optional actual registered frequency/scan observable, explicit clock/frequency-reference uncertainty and RF quality. It rejects unknown fields, non-finite values, future epochs and non-SPD covariance. It never carries an emitting entity/target ID, truth position/velocity, faction, identity or object reference.

Single and poorly conditioned bearings remain ray/region-valued. A point estimate is promoted only after a 500 m baseline, 12° crossing angle, forward-ray consistency, the 200 km bounded game hypothesis and a 95% ellipse major axis no larger than 4 km. These constants were fixed in `PLAN.md` before tests.

## Gate

`B_GATE.json` is PASS. Both real player profiles produced exactly the same legacy detection rows and final EW RNG state as merged EMCON_B over 30 native receiver trials. The deterministic fixture additionally proves:

- one bearing produces no point;
- the observation origin remains fixed after movement;
- crossing AOA shrinks the region;
- parallel geometry is not promoted;
- coast uncertainty grows and the inherited 12 s hold expires the contact;
- invalid DTOs fail closed;
- the real raw→validator→contact path creates no observer track or engagement authority.

No RF sensitivity, Pd, noise, beam, LOS, weather, radar, ECM, EMCON, seeker or network coefficient changed.
