# R4 moderate-six physical regression — not approved

R3 HP 7.404279277316576; R4 HP 0. R4 flooding is 0.2429106334538965 m³ at the original checkpoint. Native initial terminal kinds match5KILL+1NORMAL_HIT; material result worsens.

firstCapturedAssociationReturnDifferenceIncludingNis:
```json
{
  "index": 3000,
  "R3": {
    "step": 1888,
    "timeS": 31.466666666666665,
    "route": "OWN_SPY_GLOBAL",
    "observerShip": "SHIP_DDG119_OWN",
    "actualHeldPlots": [],
    "actualHeldTracks": [],
    "actualSelectedPairs": [
      {
        "i": 1,
        "id": 300000007,
        "nis": 9.392787456197391
      }
    ]
  },
  "R4": {
    "step": 1888,
    "timeS": 31.466666666666665,
    "route": "OWN_SPY_GLOBAL",
    "observerShip": "SHIP_DDG119_OWN",
    "actualHeldPlots": [],
    "actualHeldTracks": [],
    "actualSelectedPairs": [
      {
        "i": 1,
        "id": 300000007,
        "nis": 9.410279191482674
      }
    ]
  }
}
```

firstCapturedAssociationChoiceOrHoldDifference:
```json
{
  "index": 3011,
  "R3": {
    "step": 1900,
    "timeS": 31.666666666666668,
    "route": "OWN_SPY_GLOBAL",
    "observerShip": "SHIP_DDG119_OWN",
    "actualHeldPlots": [],
    "actualHeldTracks": [],
    "actualSelectedPairs": [
      {
        "i": 1,
        "id": 300000006
      },
      {
        "i": 2,
        "id": 300000007
      }
    ]
  },
  "R4": {
    "step": 1900,
    "timeS": 31.666666666666668,
    "route": "OWN_SPY_GLOBAL",
    "observerShip": "SHIP_DDG119_OWN",
    "actualHeldPlots": [],
    "actualHeldTracks": [],
    "actualSelectedPairs": [
      {
        "i": 0,
        "id": 300000007
      }
    ]
  }
}
```

firstSampledStateDifference:
```json
{
  "index": 32,
  "R3Step": 1920,
  "R4Step": 1920,
  "R3TimeS": 32,
  "R4TimeS": 32,
  "differentTopLevelFields": [
    "tracks"
  ]
}
```

firstNativeLaunchDifference:
```json
{
  "index": 18,
  "R3": {
    "step": 2256,
    "timeS": 37.6,
    "kind": "NATIVE_WEAPON_LAUNCH",
    "type": "SAM",
    "id": 14,
    "assignedTargetId": 300000004,
    "life": 0
  },
  "R4": {
    "step": 2268,
    "timeS": 37.8,
    "kind": "NATIVE_WEAPON_LAUNCH",
    "type": "SAM",
    "id": 14,
    "assignedTargetId": 300000005,
    "life": 0
  }
}
```

firstNativeEffectDifference:
```json
{
  "index": 14,
  "R3": {
    "step": 2266,
    "timeS": 37.766666666666666,
    "kind": "NATIVE_INTERCEPT_RESULT",
    "result": "MISS",
    "weapon": "5in MFF",
    "trackId": 300000005,
    "target": {
      "id": 8,
      "label": "Kh-35U",
      "alive": true,
      "life": 37.766666666665806,
      "_warheadState": "NORMAL",
      "retirement": {},
      "systems": {
        "seeker": 0,
        "guidance": 0,
        "fuze": 0,
        "warhead": 0,
        "fuel": 0,
        "engine": 0,
        "fins": 0
      },
      "behavior": {
        "seekerFailed": false,
        "guidanceMode": "NORMAL",
        "engineStopped": false,
        "fuelEngineStopped": false,
        "finsScale": 1,
        "availableG": 12
      }
    }
  },
  "R4": {
    "step": 2248,
    "timeS": 37.46666666666667,
    "kind": "NATIVE_INTERCEPT_RESULT",
    "result": "MISS",
    "weapon": "5in MFF",
    "trackId": 300000006,
    "target": {
      "id": 8,
      "label": "Kh-35U",
      "alive": true,
      "life": 37.46666666666582,
      "_warheadState": "NORMAL",
      "retirement": {},
      "systems": {
        "seeker": 0,
        "guidance": 0,
        "fuze": 0,
        "warhead": 0,
        "fuel": 0,
        "engine": 0,
        "fins": 0
      },
      "behavior": {
        "seekerFailed": false,
        "guidanceMode": "NORMAL",
        "engineStopped": false,
        "fuelEngineStopped": false,
        "finsScale": 1,
        "availableG": 12
      }
    }
  }
}
```

The first logged native return differs at NIS before a subsequent different selection/launch/hit geometry. A changed scalar does not identify the earliest causative hidden lifecycle metadata write.
Observed focused foreign finalizer denominator is zero in both six-target runs;12–26s on003/004 does not cover the later recipient/time that may be affected. Do not use zero here to prove the guard never executed anywhere.
R4 has one initial NORMAL_HIT plus three later native wreck hit callbacks; these are not four unique initial surviving missiles.
The all-initial-terminal+5s criterion is unchanged; R4 still has one native SAM alive at that checkpoint.
No global RNG trace at first divergence is available here. Protected source equality does not prove identical consumed RNG branches; do not attribute this damage change solely to RNG.
No automatic coefficient adjustment or baseline approval is performed.
