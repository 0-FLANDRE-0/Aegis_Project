# Legacy EMCON UI14 retirement and current coverage

Authority: TRACK_C directive §4 explicitly retires the 14 assertions whose DOM precondition is the removed `#lockBtn`. Original source `docs/helicopter/K/verify_ui.py` is preserved byte-for-byte. These are **RETIRED**, not failed-current assertions and not 14 newly passed tests. No hidden/detached legacy controls were recreated.

The original suite had seven assertions at each of 390×1000 and1100×800. The current UI213 path (`docs/contact/friendly/A/cpu2d_ui.py` → `docs/gun/B1/run_test_migrations.py` → `docs/map/E/verify_d_ui.py`) covers current general interactions but does not supply the old passive LOCK action. The extra current-DOM suite is `C/emcon_ui.py`, both sizes × DDG/CG,36 checks, raw model/state records and four screenshots in `evidence/current-emcon-ui/`. Native EMCON policy is separately covered by the unchanged27-check `emcon-native` domain suite.

| Old assertion (×2 sizes =14) | Current UI213 relationship | Current replacement / disposition |
|---|---|---|
| passivePointer | Old passive LOCK button no longer exists after approved MAP_E. Nonradiating manual designation UI remains explicitly deferred by the earlier user instruction. | Retire old UI action; do not resurrect. Native EMCON designation policy retained in27-check native suite. Current radar chip→quiet mode verified with0 physical SPY emitters and no PD. |
| labelFits | Text/button belonged to removed LOCK control. | Retire obsolete text assertion. Current EMCON menu's bounds tested at both widths. |
| autoControlsStillBlocked | Old external AUTO LOCK widget removed; current engagement chip selects AUTO. | Current DOM AUTO selection while quiet preserves0 SPY emitters and pdTracking=false. Existing automatic EMCON block unchanged. |
| vlsButtonsStillBlocked | Old fireBtn/external3DFireBtn removed. General MAP UI213 interactions alone are insufficient EMCON-specific proof. | Current weapon chip→salvo→track→`#mapFireB` is disabled with existing EMCON rejection; DOM click produces no interceptor release. |
| releaseTimeNotRequestTime | Harpoon/current release route still exists; general UI213 covers interface, not this timing case. | Current CG Harpoon plan queued quiet; actual release after radar re-enabled; native journal `launchEmcon=false` at actual release. Both sizes. |
| offRestoresNormalPrecision | Old paired LOCK-button sequence unavailable. | Current radar restoration tested via actual chip/menu; normal precision handoff remains native27-check coverage. No assertion that a removed UI action was executed. |
| core | Core failure array remains meaningful. | Current36 checks require core failure count0 in all four real DOM sessions; also covered in other native/current UI suites. |

`evidence/current-emcon-ui/RESULTS.json`:36/36, browser page errors0. Its original action/state records show DDG and CG quiet physical emitters0, original SAM rejection unchanged, CG Harpoon launch journal time policy unchanged. This retirement changes neither game code nor tolerances. Final UI213 and native27 outcomes are linked separately in `VALIDATION.json` rather than assumed from this table.
