# Final cost follow-up

Separate from frozen `verify_runtime.py` (`a173e069…5523`); no game, fixture,
coefficient, expected-value or original-result edits. Estimated execution is
about 3–4 minutes after source preparation.

- Hold both shared browser flock leases for the measurement. Before every run,
  verify that no browser main process remains; execute one fresh browser at a time.
- CPU order: A OFF → B OFF → B ON, then B ON → B OFF → A OFF. Reuse the original
  moving-helo setup, 30 simulated seconds of warmup and 2,400 native fixed ticks.
  No association/timing wrapper is installed during CPU measurement. Retain every
  tick cost, median, p95, state/P/private-RNG hash and memory-event observation.
- Allocation order: A OFF → B OFF → B ON. Reuse the original two-owner setup,
  120 warmup ticks and 600 measured native ticks. CDP sampling interval is 32,768
  with both GC-collected-object flags explicitly enabled. No retained-only fallback.
- Save raw heap profiles compressed. Existing candidate wrappers count one actual
  native call and restore before the real async ENV status check. Inclusive nested
  counters are reported separately and are never added together.
- Passive state uses exactly the unchanged A physical/private-RNG/P schema.
  No additional survival, model-preview, geometry, profile or cache getters.
  Preserve any cross-product state differences.
- Previous concurrent-host CPU and retained-only allocation samples stay intact
  and are labelled `NOT_FINAL_FOR_COST_ASSESSMENT`. New results confer no release
  or performance approval automatically.

```sh
TMPDIR=/dev/shm PYTHONDONTWRITEBYTECODE=1 python -u docs/contact/track/B/measure_cost_final.py --run
```
