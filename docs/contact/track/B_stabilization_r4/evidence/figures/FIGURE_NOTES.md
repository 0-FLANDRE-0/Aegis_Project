# Offline battle figure notes

- `moderate6_ship_state`: legacy shipHP and recorded water, not a sink-state or physical identity metric. All four initial threat totals are 5 INTERCEPT_KILL + 1 NORMAL_HIT. End times differ. TRACK-A numerical water residue is preserved in CSV and shown approximately zero.
- `moderate6_event_timeline`: two explicitly different x-axis ranges. Native event chronology is not a complete causal decomposition. MFF sequence mismatches are not proved to be the same gun round. Three wreck callbacks are not three additional initial-threat hits.
- `hold_episode_scope`: closed episodes end at the next accepted native update; open elapsed is right-censored at the recorded endpoint, not continuous sensor outage. No physical-target continuity is inferred.
- No browser, simulation, source coefficient, expectation, original capture, existing report or table was changed. Figures are offline static plots, not phone FPS measurements.
- Every CSV row includes its source JSON path, SHA-256 and pointer. Figure provenance pins all source inputs, script, and outputs.
