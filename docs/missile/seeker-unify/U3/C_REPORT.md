# SEEKER_UNIFY_U3 Commit C report

## Status

| State | Result |
|---|---|
| IMPLEMENTED | Existing ASM HOJ angular tracking is behind a common port; Harpoon has a missile-owned terminal HOJ state and threat-mode capability gate. |
| TESTED | ASM SHADOW/ACTIVE state and RNG equivalence, Harpoon MAX_THREAT/CONFIRMED_ONLY feature scenes, deterministic repeats, six non-jamming natural scenes, and static scope/provenance audit. |
| APPROVED | C gate passed. Existing ASM behavior is equivalent and Harpoon policy matches the user decision. |
| UNRESOLVED | Harpoon HOJ real-world capability remains unconfirmed by design. `CONFIRMED_ONLY` performance is `UNVERIFIED`; only feature-off behavior was checked. |
| RELEASE | Not released. Branch checkpoint only. |

## Capability and parameter provenance

`RGM-84D / terminalHoj` is recorded as `ASSUMED_THREAT`:

- enabled in `MAX_THREAT`;
- disabled before signal synthesis in `CONFIRMED_ONLY`;
- no claim of real Harpoon HOJ capability;
- no new tuned performance values and no result-fitting.

The game effect reuses the already-existing Kh-35U HOJ receiver/filter
abstraction and labels that fact as
`SIM_TUNED_REUSE_EXISTING_GAME_ABSTRACTION`. It does not add a Harpoon
midcourse passive-RF mode.

## Common state ownership

The common updater owns only an angular HOJ track state. Ports supply the
emitter signal and RNG:

- existing ASM: unchanged global simulation RNG and existing emitter adapter;
- Harpoon: its own missile RNG (`harpoonRandomA` / `harpoonNoiseA`) and an
  independent `m.seeker.hoj` state;
- no ASM/Harpoon state object is shared;
- termination/reset follows each missile's existing lifetime; no new save
  inventory schema is introduced.

Harpoon updates this state only after its terminal seeker is active. If a firm
ARH track exists, ARH retains guidance authority. HOJ guides only when its
angular track is valid and firm ARH is unavailable.

## Gate results

| Check | Result |
|---|---:|
| ASM SHADOW comparisons | 90 |
| State mismatches | 0 |
| RNG mismatches | 0 |
| SHADOW repeat deterministic | yes |
| ACTIVE repeat deterministic | yes |
| MAX_THREAT Harpoon HOJ | TRACK, guidance active |
| CONFIRMED_ONLY Harpoon HOJ | OFF, RNG consumption 0 |
| ASM/Harpoon state object sharing | none |
| B vs C non-jamming natural scenes | 6/6 bit equal |
| Page errors | 0 |

The legacy `asmUpdateHojTrack` body is preserved byte-for-byte under the
SHADOW reference name. Fifteen unrelated functions, including emitter physics,
passive RF, launch gates, damage, and save inventory functions, remained byte
equal.

## Evidence

- `C_GATE.json`
- `C_SCOPE.json`
- `BUILD_C_SHADOW.json`
- `BUILD_C_ACTIVE.json`
- `changes-C.diff`
- `changes-through-C.diff`
- `hoj_common_c.js`
- `harpoon_hoj_c.js`
- `run_c_contract.py`
- `verify_c_scope.py`

