# DEFENSE_OODA_A decision policy

Status: frozen before Commit C dynamic scenes. All bands are
`SIM_TUNED_GAMEPLAY_NOT_REAL_CIC_SPEC`.

The stable lexicographic tuple (lower is more urgent) is:

1. existing observed A3 authority/threat state (never grants authority);
2. observed TGO band: `<=8`, `<=15`, `<=30`, `>30`, unknown;
3. observed CPA band: `<=300`, `<=1000`, `<=3000`, `>3000`, unknown metres;
4. re-engagement requirement, then live engagement count;
5. observed inbound/closure availability;
6. measurement freshness: `<=0.5`, `<=2`, `<=5`, `>5`, unknown seconds;
7. coast/memory state;
8. covariance sigma band: `<=100`, `<=500`, `<=1500`, `>1500`, unknown metres;
9. owner-local engagement distribution;
10. owner-local integer track ID.

Aging reduces the live-engagement queue component by one at each profile aging
interval but never outranks authority or urgent TGO/CPA. Urgent preemption occurs
only when a waiting row has a strictly more urgent observed TGO band than the
least urgent assigned row; the victim keeps its phase and remaining steps.

The command `score` uses a bounded mixed-radix encoding of the tuple. Sorting is
performed by the tuple itself; the score exists only because the frozen command
schema requires a finite value. Null/NaN/Infinity enters the explicit unknown
worst band or causes capacity HOLD.

Salvo advice first calls the current native H1 result. `DEFENSE_OODA_A` can only
retain or reduce that value, never exceed it or 4. Existing owner-local live
engagements may reduce the advice; `reengageRequired` with zero live rounds may
restore it up to the native result. Downstream reserve, FCS/SPG, Network G and
release gates always run again.
