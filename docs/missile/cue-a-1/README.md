# CUE_A-1

Current PR candidate: `Aegis_SIM_v48_WIP_CUE_A_1.html`<br>
SHA-256: `0449d3192cc4cafbda3686669e3738a36b7a7d8aeda205b5cbd3e614061b814a`

This increment restores the ASM-only 0.5 km floor, replaces tick-coupled cue noise with an exact-discrete Singer model, bounds unknown-velocity uncertainty, and limits midcourse passive RF to observed ship-radar families with band and swept-beam handling.

- Start with `REPORT.md` for the reviewed outcome.
- Use `REGRESSION_RESULTS.json` for final disposition and `REGRESSION_RESULTS_RAW.json` for the immutable one-time broad output.
- Detailed Stage 1 and Stage 2 evidence is in `CUE_FILTER_SINGER.*` and `PASSIVE_RF_EMITTER_BAND.*`.
- `CONFIRMED_ONLY` performance is UNVERIFIED. Inherited debts are not waived.
- Delivery policy: PR only; no merge/release/tag.
