# SEEKER_UNIFY_A — surface-ship RCS normalization and seeker unification design

IMPLEMENTED: **YES — surface-ship RCS supply/provenance only**

TESTED: **YES — primary 1,590-case matrix, managed/NPC radar, native 364, UI 213, WebGL 29, reference battles 60**

APPROVED: **YES — directive automatic merge gate; RCS-path exact-state deltas recorded without tolerance changes**

UNRESOLVED: **No public class-specific absolute RCS measurements; DDG reduction remains explicit SIM_TUNED. Common seeker layer is design-only.**

RELEASE: **main merge permitted; no release/tag**

## Outcome

Validation is **PASS**. The product changes only the surface-ship RCS providers and explicit S/X/IJ band plumbing. The 19 protected seeker, radar-equation, guidance, propulsion, fuze and damage functions are byte-identical to the baseline.

## RCS basis

The absolute beam scale uses Skolnik's 1974 grazing-incidence formula `52*sqrt(f_MHz)*D_kt^(3/2)`. Public full-load displacement is used for DDG-119, CG-52 and Project 956. Existing section locations and bow/quarter/beam/stern/top curves are retained. DDG uses a clearly tagged 15 dB SIM_TUNED reduction based on public qualitative shaping evidence; CG and Project 956 use the unreduced formula because no defensible class-specific reduction was found.

## Primary matrix

- Identical browser-engine conditions: 1590
- False-acquisition increases: 0
- Radar-horizon violations: 0
- Kh-32 terminal TRACK: 42 → 60 / 60; hits 40 → 40
- Kh-35U terminal TRACK: 41 → 42 / 60; hits 41 → 42
- ESSM Block 2 and SM-6 Block IA air/surface aircraft/ASM/sea-clutter/chaff acceptance increases: 0

## Ship radar paths

- Production SPY-1D(V)/SPQ-9B/BridgeMaster acceptors: 255 tracks in 420 cases; baseline/product changed conditions 0.
- NPC DDG/CG observers: 24 tracks in 60 cases; changed conditions 0.
- Truth-reference exposure in both TrackStores: 0.

## Broad regression

- native13: 364/364
- UI: 213/213
- observed WebGL: 29/29
- Paired DDG/CG: 36 raw equal + 6 pre-approved RCS-path deltas = 42/42 effective. Physical state, damage, inventory bounds and faults are unchanged.
- Existing retired EMCON UI 14-check debt remains explicitly incomplete; current EMCON native 27/27 passes.

## 60-battle reference (not a merge gate)

- Completed: 60/60
- Product totals: kills 301, leakers 17, egress 1, other 1
- Historical TRACK-C totals: kills 264, leakers 15, egress 37, other 4

These statistics are reported as requested and are not used to fit the RCS values or to pass/fail the work.

## Part 2

`UNIFY_AUDIT.md` inventories WIP22 ASM, Harpoon, SAM SARH/dual-mode ARH and RAM from reflector collection through guidance input. `UNIFY_DESIGN.md` defines a future common measurement/validation/association contract, while `PROFILE_MIGRATION_TABLE.json` records field and unit migration. No common seeker implementation is included in this product.
