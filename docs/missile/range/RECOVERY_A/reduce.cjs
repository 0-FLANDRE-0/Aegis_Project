// Read-only diagnostic output reduction; no native or simulation writes.
module.exports = function reduce(q) {
  const all = q.diagnosticTicks || [];
  const zero = q.samples?.[0];
  const first = zero?.shelfM != null ? zero : all.find(x => x.shelfM != null) || q.samples?.find(x => x.shelfM != null);
  q.firstShelf = first ? { timeS: first.timeS, shelfM: first.shelfM, cruiseAltM: first.cruiseAltM } : null;
  q.firstShelfSampling = 'FIRST_AVAILABLE_NATIVE_10HZ_SAMPLE_UNLESS_PRESENT_AT_LAUNCH';
  q.firstDescent = all.find((x, i) => i && all[i - 1].vzMps >= 0 && x.vzMps < 0) || null;
  q.phaseTransitions60Hz = all.filter((x, i) => !i || ['mode', 'phase', 'guidance', 'terminalLatched'].some(k => x[k] !== all[i - 1][k]));
  q.diagnosticTicks = all.filter(x => x.timeS >= q.flightTimeS - 10);
  q.telemetryPolicy = 'READ_ONLY_FIRST_SHELF_FIRST_DESCENT_TRANSITIONS_AND_LAST_10S_60HZ';
  return q;
};
