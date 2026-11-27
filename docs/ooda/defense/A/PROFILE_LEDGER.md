# DEFENSE_OODA_A profile ledger

Status: `FROZEN_BEFORE_DYNAMIC_COMBAT_TESTS`

Source tag for every value below: `SIM_TUNED_GAMEPLAY_NOT_REAL_CIC_SPEC`.

These are game pacing values. They are not claims about real Aegis CIC staffing,
throughput, modernization, reaction time, or combat performance.

| ShipProfile | base slots | OBSERVE steps | ORIENT steps | DECIDE steps | modernization | minimum capacity | queue limit | aging interval | urgent TGO bands (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `DDG_119_LATE_FLIGHT_IIA` | 4 | 12 | 24 | 12 | 1.00 | 0.20 | 64 | 300 | 8 / 15 / 30 |
| `CG_52_LATE_TICONDEROGA` | 4 | 18 | 30 | 18 | 0.80 | 0.20 | 64 | 300 | 8 / 15 / 30 |

The two profiles use one common engine. No OODA function branches on a DDG/CG
name. Sovremenny has no active defensive sensor/weapon suite and intentionally
has no OODA profile in this stage.

## Capacity formula

- `crewBottleneck = min(COMBAT.availability, OPERATIONS.availability)`.
- `damageFactor = ship.damage.combatEff`.
- Because crew availability and combat-efficiency can describe overlapping
  consequences of one casualty, they are not multiplied:
  `operationalFactor = min(crewBottleneck, damageFactor)`.
- `capacity = clamp(operationalFactor * modernizationFactor, 0, 1)`.
- Mission/equipment/combat unavailable, invalid inputs, or capacity below the
  profile minimum produce capacity 0 and advisory HOLD.
- `slots = capacity == 0 ? 0 : max(1, floor(baseSlots * capacity))`.
- Each phase service time is
  `ceil(basePhaseSteps / max(minimumOperationalCapacity, capacity))`.

Rounding is deliberately conservative: slots round down and time rounds up.
Radar power, VLS power, SPG condition, probability of kill, missile performance,
and sensor performance do not receive a modernization multiplier.

## Freeze rule

The values in this ledger are frozen before any dynamic combat result is
observed. A later change needs an explicit user decision and a new recorded
reason; regression results may not be used as after-the-fact tuning targets.
