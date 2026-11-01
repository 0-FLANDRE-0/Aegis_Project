# Natural6 baseline fixture qualification

Status: QUALIFIED_BASELINE_FIXTURE. This validates the test setup, not a candidate or expectation update.

| Product | End s | Initial native outcomes | ShipHP after5s aftermath | Actual held plot/track appearances |
|---|---:|---|---:|---:|
| track-a | 45.316667 | {"INTERCEPT_KILL": 5, "NORMAL_HIT": 1} | 9.970806 | 0/0 |
| old-active | 45.316667 | {"INTERCEPT_KILL": 5, "NORMAL_HIT": 1} | 7.674369 | 29/52 |

Both cases start with zero tracks and the unchanged native AUTO/sensor/weapon pipeline. Six Kh-35U at90°,10.8+i×0.08km,10m,280m/s; seed419027 and original90s limit. Native terminal events precede the unchanged5s aftermath. All native/observer faults and drops are zero.

A lacks the B selector: its zero HOLD counters are unavailable diagnostics, not a proof that it resolved every ambiguity. oldB has29 held-plot and52 held-track appearances, with max component7. Peak reported7files is not labeled a duplicate without observed-lineage evidence.

Physical material results differ: AHP9.970806 versus oldB7.674369, despite both5INTERCEPT_KILL+1NORMAL_HIT and one native ship-hit history callback. Full flooding/module/target values and increases are retained in QUALIFICATION.json. They are not approved by lifecycle equality. Long-term flood survival beyond the recorded aftermath is not asserted.

New SHADOW/ACTIVE qualification still requires their own frozen-product runs. No failed pilot was discarded and no AI, inventory, RF, physics, gate or coefficient was changed.
