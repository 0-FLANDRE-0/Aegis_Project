# EMITTER_A implementation plan

Status: IMPLEMENTED (Commit A baseline audit only)

## Pinned baseline

- Remote `main`: `5d0b4ea03f0bb51db1b5d72562f15ce818074b4e`
- Product: `Aegis_SIM_v48_WIP_SEEKER_UNIFY_U3.html`
- Product SHA-256: `243c196a69990e1fba9de0993f7904fb569e3adc5b6e84cf52672d3300638835`
- U3 PR: `#72`, merged with the above merge commit.

## Commit gates

1. Commit A — audit the current hard-coded emitter creation, consumers, mutable
   owners, output order, compatibility power values, and Sovremenny inactive
   registration. No product behavior change.
2. Commit B — add immutable DDG/CG profile emitter registries and a SHADOW
   resolver. The legacy resolver remains tactical authority.
3. Commit C — promote the common resolver to ACTIVE only after exact output,
   order, RNG, receiver/ESM, UI, save/restore, and combat equivalence gates.
4. Commit D — register the existing Sovremenny sensor metadata as explicitly
   inactive/unverified. Physical emission, ESM output, own detection, and attack
   authority remain disabled.
5. Run the broad regression exactly once after the final implementation stage.

## Conflict check before ACTIVE

No contradictory instruction was found. SOV_A says the current Sovremenny hull
has no functional sensors, EW, or emissions. EMITTER_A explicitly permits
declarative registration without enabling physical emission. Commit D therefore
preserves `installed:false`, `active:false`, `emitter:false` and zero physical
emitters.

## Non-goals

- EMCON category UI or doctrine
- new radar/EW physics or retuning
- SPG-62 illumination redesign
- Nulka, aircraft, or missile-emitter migration
- TRACK-D/OODA or NPC tactical doctrine
- save-schema changes

