# EMCON_B Commit D report — equipment overrides and profile-derived UI

Status: `IMPLEMENTED` / `TESTED` / `APPROVED` (commit-local gate) / `RELEASE=false`

## Implemented

- The existing `uiEmconChipA` and `mapEmconMenuE` are extended; no competing EMCON
  window or duplicate legacy control was created.
- Category rows and equipment rows are generated from the selected owner's immutable
  ShipProfile emitter registry. The UI module contains no DDG/CG profile or equipment IDs.
- The chip separately reports radar master, active radar category count, and ECM
  `TX / REQ / OFF` state.
- Category policy and equipment override commands route through the owner-addressed
  EMCON_B command API. Rendering and the 10 Hz refresh loop are read-only.
- The owner selector follows existing FLEET selection. DDG/CG, mixed-class, and same-class
  ships retain independent policies.
- The `FIRE_CONTROL` contract row is visible but disabled as `등록 장비 없음`; no SPG-62
  RF behavior was added.
- The all-radiation macro stores master/ECM policy per owner, silences radar master and
  ECM physical output, preserves the existing ECM technique request, and restores the
  remembered values exactly.
- The menu states explicitly that communications links remain a separate policy.

## Deterministic gate

Final `D_GATE.json`: `PASS`; page errors 0; console errors 0.

- Category-silent + `FORCE_RADIATE`: operational registered equipment radiates.
- Category-radiate + `FORCE_SILENT`: only the selected equipment is removed.
- SPQ, NAV, and ECM individual isolation: PASS.
- Ship offline defeats `FORCE_RADIATE`: PASS.
- Profile registry IDs equal generated DOM equipment IDs: exact for DDG and CG.
- UI refresh mutation: 0.
- Mixed/same-class owner isolation: PASS.
- All-radiation silence and exact restore: PASS; requests preserved.
- Existing menu/chip node counts: 1 each.

## Responsive measurements

| Viewport | Menu bounds (x, y, w, h px) | Scroll client/content | New control minimum |
|---|---|---|---:|
| 1400×900 | 941, 237, 350, 620 | 618 / 688 | 36 px |
| 832×384 | 399, 61.6, 350, 291.8 | 290 / 684 | 36 px |
| 390×844 | 4, 195.1, 350, 620 | 618 / 684 | 36 px |

All menu bounds stay inside the viewport. Screenshots are under
`docs/electronic/emcon/B/screenshots/`.

## Build

- Baseline SHA-256: `3a5886b4fe0826c834dd237574dd38c21bdd67600553f64c7ce532a7bce1c2be`
- Commit-D candidate SHA-256: `44cc20d1f91c2a9a26c90fe2da4ba0e826828799c160c5a54474b430ec158230`
- Packed-main SHA-256: `513d601e75f1b3cd4044238b2e5c54b331f54b0aa738f5e941cdf7ddffc98d50`

Network lease and save/reset lifecycle authority remain Commit E work. The broad regression
has not been run early.
