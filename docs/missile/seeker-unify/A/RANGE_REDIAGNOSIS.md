# Range rediagnosis

IMPLEMENTED: **surface-ship RCS scale only**

TESTED: **1590 identical browser-engine cases**

APPROVED: **directive pre-approval applies only if primary and broad regression gates pass**

UNRESOLVED: **see limitations and managed-radar supplement**

RELEASE: **no release/tag**

## Primary result

**PASS** — false-acquisition increases: 0;
radar-horizon violations: 0; page errors:
baseline 0, product 0.

The RCS values were fixed before this matrix was executed.  No result was fed
back into the RCS constants.

## Terminal cue

| label | shots | baselineTrack | productTrack | baselineHit | productHit |
|---|---|---|---|---|---|
| Kh-32 | 60 | 42 | 60 | 40 | 40 |
| Kh-35U | 60 | 41 | 42 | 41 | 42 |


## Changed ASM target-track cells

| kind | speedKt | altM | rangeKm | shots | baseline | product | delta |
|---|---|---|---|---|---|---|---|
| CG | 0 | 200 | 20 | 5 | 0 | 5 | 5 |
| CG | 0 | 200 | 30 | 5 | 0 | 5 | 5 |
| CG | 0 | 200 | 40 | 5 | 0 | 5 | 5 |
| CG | 0 | 200 | 45 | 5 | 0 | 5 | 5 |
| CG | 15 | 15 | 30 | 5 | 4 | 5 | 1 |
| CG | 15 | 200 | 20 | 5 | 4 | 5 | 1 |
| CG | 15 | 200 | 30 | 5 | 0 | 5 | 5 |
| CG | 15 | 200 | 40 | 5 | 0 | 5 | 5 |
| CG | 15 | 200 | 45 | 5 | 0 | 5 | 5 |
| DDG | 0 | 200 | 20 | 5 | 0 | 5 | 5 |
| DDG | 0 | 200 | 30 | 5 | 0 | 3 | 3 |
| DDG | 15 | 200 | 20 | 5 | 4 | 5 | 1 |
| DDG | 15 | 200 | 30 | 5 | 0 | 5 | 5 |
| HULK | 0 | 200 | 20 | 5 | 0 | 5 | 5 |
| HULK | 0 | 200 | 30 | 5 | 0 | 5 | 5 |
| HULK | 0 | 200 | 40 | 5 | 0 | 5 | 5 |
| HULK | 0 | 200 | 45 | 5 | 0 | 5 | 5 |
| HULK | 15 | 200 | 20 | 5 | 4 | 5 | 1 |
| HULK | 15 | 200 | 30 | 5 | 0 | 5 | 5 |
| HULK | 15 | 200 | 40 | 5 | 0 | 5 | 5 |
| HULK | 15 | 200 | 45 | 5 | 0 | 5 | 5 |
| SOV | 0 | 200 | 30 | 5 | 0 | 5 | 5 |
| SOV | 0 | 200 | 40 | 5 | 0 | 5 | 5 |
| SOV | 0 | 200 | 45 | 5 | 0 | 5 | 5 |
| SOV | 15 | 200 | 30 | 5 | 2 | 5 | 3 |
| SOV | 15 | 200 | 40 | 5 | 0 | 5 | 5 |
| SOV | 15 | 200 | 45 | 5 | 0 | 5 | 5 |


## Product ASM track envelope on the measured grid

| kind | altM | speedKt | furthestAnyTrackKm | furthestAllFiveTrackKm |
|---|---|---|---|---|
| DDG | 15 | 0 | 30 | 30 |
| DDG | 15 | 15 | 30 | 30 |
| DDG | 200 | 0 | 30 | 20 |
| DDG | 200 | 15 | 30 | 30 |
| CG | 15 | 0 | 30 | 30 |
| CG | 15 | 15 | 30 | 30 |
| CG | 200 | 0 | 45 | 45 |
| CG | 200 | 15 | 45 | 45 |
| SOV | 15 | 0 | 30 | 30 |
| SOV | 15 | 15 | 30 | 30 |
| SOV | 200 | 0 | 45 | 45 |
| SOV | 200 | 15 | 45 | 45 |
| HULK | 15 | 0 | 30 | 30 |
| HULK | 15 | 15 | 30 | 30 |
| HULK | 200 | 0 | 45 | 45 |
| HULK | 200 | 15 | 45 | 45 |


The 15 m rows stop between the 30 and 40 km samples consistently with the
low-altitude radar horizon. At 200 m, the non-low-observable CG/Project 956/hulk
reach the 45 km sample and stop at 50 km; the 15 dB-reduced DDG reaches 30 km.
This is compatible with the public Kh-35 family 20/50 km context without using
those distances to tune the RCS constants.

## False-acquisition controls

| control | altM | rangeKm | shots | baseline | product | delta |
|---|---|---|---|---|---|---|
| CHAFF | 15 | 10 | 5 | 5 | 5 | 0 |
| CHAFF | 15 | 20 | 5 | 5 | 5 | 0 |
| CHAFF | 15 | 30 | 5 | 5 | 5 | 0 |
| CHAFF | 15 | 40 | 5 | 0 | 0 | 0 |
| CHAFF | 15 | 45 | 5 | 0 | 0 | 0 |
| CHAFF | 15 | 50 | 5 | 0 | 0 | 0 |
| CHAFF | 200 | 10 | 5 | 5 | 5 | 0 |
| CHAFF | 200 | 20 | 5 | 0 | 0 | 0 |
| CHAFF | 200 | 30 | 5 | 0 | 0 | 0 |
| CHAFF | 200 | 40 | 5 | 0 | 0 | 0 |
| CHAFF | 200 | 45 | 5 | 0 | 0 | 0 |
| CHAFF | 200 | 50 | 5 | 0 | 0 | 0 |
| NO_TARGET | 15 | 10 | 5 | 0 | 0 | 0 |
| NO_TARGET | 15 | 20 | 5 | 0 | 0 | 0 |
| NO_TARGET | 15 | 30 | 5 | 0 | 0 | 0 |
| NO_TARGET | 15 | 40 | 5 | 0 | 0 | 0 |
| NO_TARGET | 15 | 45 | 5 | 0 | 0 | 0 |
| NO_TARGET | 15 | 50 | 5 | 0 | 0 | 0 |
| NO_TARGET | 200 | 10 | 5 | 0 | 0 | 0 |
| NO_TARGET | 200 | 20 | 5 | 0 | 0 | 0 |
| NO_TARGET | 200 | 30 | 5 | 0 | 0 | 0 |
| NO_TARGET | 200 | 40 | 5 | 0 | 0 | 0 |
| NO_TARGET | 200 | 45 | 5 | 0 | 0 | 0 |
| NO_TARGET | 200 | 50 | 5 | 0 | 0 | 0 |
| SEA_CLUTTER | 15 | 10 | 5 | 0 | 0 | 0 |
| SEA_CLUTTER | 15 | 20 | 5 | 0 | 0 | 0 |
| SEA_CLUTTER | 15 | 30 | 5 | 0 | 0 | 0 |
| SEA_CLUTTER | 15 | 40 | 5 | 0 | 0 | 0 |
| SEA_CLUTTER | 15 | 45 | 5 | 0 | 0 | 0 |
| SEA_CLUTTER | 15 | 50 | 5 | 0 | 0 | 0 |
| SEA_CLUTTER | 200 | 10 | 5 | 0 | 0 | 0 |
| SEA_CLUTTER | 200 | 20 | 5 | 0 | 0 | 0 |
| SEA_CLUTTER | 200 | 30 | 5 | 0 | 0 | 0 |
| SEA_CLUTTER | 200 | 40 | 5 | 0 | 0 | 0 |
| SEA_CLUTTER | 200 | 45 | 5 | 0 | 0 | 0 |
| SEA_CLUTTER | 200 | 50 | 5 | 0 | 0 | 0 |


## ESSM B2 / SM-6 air, ASM, sea-clutter and chaff no-increase gate

| path | targetKind | rangeKm | shots | baseline | product | delta |
|---|---|---|---|---|---|---|
| ESSM_BLOCK2_AIR | AIRCRAFT | 10 | 5 | 5 | 5 | 0 |
| ESSM_BLOCK2_AIR | AIRCRAFT | 20 | 5 | 5 | 5 | 0 |
| ESSM_BLOCK2_AIR | AIRCRAFT | 30 | 5 | 5 | 5 | 0 |
| ESSM_BLOCK2_AIR | AIRCRAFT | 40 | 5 | 5 | 5 | 0 |
| ESSM_BLOCK2_AIR | AIRCRAFT | 45 | 5 | 5 | 5 | 0 |
| ESSM_BLOCK2_AIR | AIRCRAFT | 50 | 5 | 5 | 5 | 0 |
| ESSM_BLOCK2_AIR | ASM | 10 | 5 | 5 | 5 | 0 |
| ESSM_BLOCK2_AIR | ASM | 20 | 5 | 5 | 5 | 0 |
| ESSM_BLOCK2_AIR | ASM | 30 | 5 | 5 | 5 | 0 |
| ESSM_BLOCK2_AIR | ASM | 40 | 5 | 5 | 5 | 0 |
| ESSM_BLOCK2_AIR | ASM | 45 | 5 | 5 | 5 | 0 |
| ESSM_BLOCK2_AIR | ASM | 50 | 5 | 5 | 5 | 0 |
| ESSM_BLOCK2_AIR | CHAFF | 10 | 5 | 5 | 5 | 0 |
| ESSM_BLOCK2_AIR | CHAFF | 20 | 5 | 5 | 5 | 0 |
| ESSM_BLOCK2_AIR | CHAFF | 30 | 5 | 5 | 5 | 0 |
| ESSM_BLOCK2_AIR | CHAFF | 40 | 5 | 5 | 5 | 0 |
| ESSM_BLOCK2_AIR | CHAFF | 45 | 5 | 5 | 5 | 0 |
| ESSM_BLOCK2_AIR | CHAFF | 50 | 5 | 5 | 5 | 0 |
| ESSM_BLOCK2_AIR | SEA_CLUTTER | 10 | 5 | 0 | 0 | 0 |
| ESSM_BLOCK2_AIR | SEA_CLUTTER | 20 | 5 | 0 | 0 | 0 |
| ESSM_BLOCK2_AIR | SEA_CLUTTER | 30 | 5 | 0 | 0 | 0 |
| ESSM_BLOCK2_AIR | SEA_CLUTTER | 40 | 5 | 0 | 0 | 0 |
| ESSM_BLOCK2_AIR | SEA_CLUTTER | 45 | 5 | 0 | 0 | 0 |
| ESSM_BLOCK2_AIR | SEA_CLUTTER | 50 | 5 | 0 | 0 | 0 |
| SM6_BLOCK_IA_AIR | AIRCRAFT | 10 | 5 | 5 | 5 | 0 |
| SM6_BLOCK_IA_AIR | AIRCRAFT | 20 | 5 | 5 | 5 | 0 |
| SM6_BLOCK_IA_AIR | AIRCRAFT | 30 | 5 | 5 | 5 | 0 |
| SM6_BLOCK_IA_AIR | AIRCRAFT | 40 | 5 | 5 | 5 | 0 |
| SM6_BLOCK_IA_AIR | AIRCRAFT | 45 | 5 | 5 | 5 | 0 |
| SM6_BLOCK_IA_AIR | AIRCRAFT | 50 | 5 | 5 | 5 | 0 |
| SM6_BLOCK_IA_AIR | ASM | 10 | 5 | 5 | 5 | 0 |
| SM6_BLOCK_IA_AIR | ASM | 20 | 5 | 5 | 5 | 0 |
| SM6_BLOCK_IA_AIR | ASM | 30 | 5 | 5 | 5 | 0 |
| SM6_BLOCK_IA_AIR | ASM | 40 | 5 | 5 | 5 | 0 |
| SM6_BLOCK_IA_AIR | ASM | 45 | 5 | 5 | 5 | 0 |
| SM6_BLOCK_IA_AIR | ASM | 50 | 5 | 5 | 5 | 0 |
| SM6_BLOCK_IA_AIR | CHAFF | 10 | 5 | 5 | 5 | 0 |
| SM6_BLOCK_IA_AIR | CHAFF | 20 | 5 | 5 | 5 | 0 |
| SM6_BLOCK_IA_AIR | CHAFF | 30 | 5 | 5 | 5 | 0 |
| SM6_BLOCK_IA_AIR | CHAFF | 40 | 5 | 5 | 5 | 0 |
| SM6_BLOCK_IA_AIR | CHAFF | 45 | 5 | 5 | 5 | 0 |
| SM6_BLOCK_IA_AIR | CHAFF | 50 | 5 | 5 | 5 | 0 |
| SM6_BLOCK_IA_AIR | SEA_CLUTTER | 10 | 5 | 0 | 0 | 0 |
| SM6_BLOCK_IA_AIR | SEA_CLUTTER | 20 | 5 | 0 | 0 | 0 |
| SM6_BLOCK_IA_AIR | SEA_CLUTTER | 30 | 5 | 0 | 0 | 0 |
| SM6_BLOCK_IA_AIR | SEA_CLUTTER | 40 | 5 | 0 | 0 | 0 |
| SM6_BLOCK_IA_AIR | SEA_CLUTTER | 45 | 5 | 0 | 0 | 0 |
| SM6_BLOCK_IA_AIR | SEA_CLUTTER | 50 | 5 | 0 | 0 | 0 |
| SM6_BLOCK_IA_SURFACE | AIRCRAFT | 10 | 5 | 5 | 5 | 0 |
| SM6_BLOCK_IA_SURFACE | AIRCRAFT | 20 | 5 | 5 | 5 | 0 |
| SM6_BLOCK_IA_SURFACE | AIRCRAFT | 30 | 5 | 5 | 5 | 0 |
| SM6_BLOCK_IA_SURFACE | AIRCRAFT | 40 | 5 | 5 | 5 | 0 |
| SM6_BLOCK_IA_SURFACE | AIRCRAFT | 45 | 5 | 5 | 5 | 0 |
| SM6_BLOCK_IA_SURFACE | AIRCRAFT | 50 | 5 | 5 | 5 | 0 |
| SM6_BLOCK_IA_SURFACE | ASM | 10 | 5 | 5 | 5 | 0 |
| SM6_BLOCK_IA_SURFACE | ASM | 20 | 5 | 5 | 5 | 0 |
| SM6_BLOCK_IA_SURFACE | ASM | 30 | 5 | 5 | 5 | 0 |
| SM6_BLOCK_IA_SURFACE | ASM | 40 | 5 | 5 | 5 | 0 |
| SM6_BLOCK_IA_SURFACE | ASM | 45 | 5 | 5 | 5 | 0 |
| SM6_BLOCK_IA_SURFACE | ASM | 50 | 5 | 5 | 5 | 0 |
| SM6_BLOCK_IA_SURFACE | CHAFF | 10 | 5 | 5 | 5 | 0 |
| SM6_BLOCK_IA_SURFACE | CHAFF | 20 | 5 | 5 | 5 | 0 |
| SM6_BLOCK_IA_SURFACE | CHAFF | 30 | 5 | 5 | 5 | 0 |
| SM6_BLOCK_IA_SURFACE | CHAFF | 40 | 5 | 5 | 5 | 0 |
| SM6_BLOCK_IA_SURFACE | CHAFF | 45 | 5 | 5 | 5 | 0 |
| SM6_BLOCK_IA_SURFACE | CHAFF | 50 | 5 | 5 | 5 | 0 |
| SM6_BLOCK_IA_SURFACE | SEA_CLUTTER | 10 | 5 | 0 | 0 | 0 |
| SM6_BLOCK_IA_SURFACE | SEA_CLUTTER | 20 | 5 | 0 | 0 | 0 |
| SM6_BLOCK_IA_SURFACE | SEA_CLUTTER | 30 | 5 | 0 | 0 | 0 |
| SM6_BLOCK_IA_SURFACE | SEA_CLUTTER | 40 | 5 | 0 | 0 | 0 |
| SM6_BLOCK_IA_SURFACE | SEA_CLUTTER | 45 | 5 | 0 | 0 | 0 |
| SM6_BLOCK_IA_SURFACE | SEA_CLUTTER | 50 | 5 | 0 | 0 | 0 |


## Changed ship-radar plot-eligible cells

No changed cells.


## Interpretation

`detected + trackEligible` means the production common RF echo field generated
an echo and the production anonymous surface-domain evidence admitted it.  The
separate managed-radar supplement drives the actual SPY/SPQ/BridgeMaster plot
acceptors and reports TrackStore creation.  All detections are checked against
the same target-height radar horizon.
