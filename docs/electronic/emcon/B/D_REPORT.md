# EMCON_B Commit D / correction-2 UI report

Status: `IMPLEMENTED` / `TESTED` / `APPROVED` (limited gate) / `RELEASE=false`.

- The existing EMCON chip is menu-only. The menu has one top `전파방사통제` button and registry-generated category/equipment controls; the former separate radar-master button is removed.
- UI code contains no DDG/CG profile or equipment IDs. `FIRE_CONTROL` is disabled as `등록 장비 없음`; no SPG-62 RF model was added.
- The top control reads only ShipRuntime `allRadiationSilent`. Child text, color, and ARIA read effective equipment decisions.
- During global silence, operational children remain selectable and display OFF. Selecting SPY/SPQ/NAV/ECM atomically clears global/master silence and enables only that selection.
- ECM displays permission (`ARMED · 대기`) separately from physical `TX`.
- Non-friendly/inactive SOV owners and damaged/offline equipment are fail-closed.

`D_STATIC.json` and `D_GATE.json` pass. Chromium coverage includes DDG/CG, mixed and same-class owner routing, menu-only mutation 0, registry/DOM exactness, equipment/category breakout, and page/console errors 0.

| Viewport | Menu bounds (x, y, w, h px) | New-control minimum |
|---|---|---:|
| 1400×900 | 941, 237, 350, 620 | 36 px |
| 832×384 | 399, 61.6, 350, 291.8 | 36 px |
| 390×844 | 4, 195.1, 350, 620 | 36 px |

Evidence screenshots are under `docs/electronic/emcon/B/screenshots/`.
