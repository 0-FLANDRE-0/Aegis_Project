"""Freeze the pre-implementation GUN_B2B game-model derivation.

This is an offline deterministic calculator.  It does not import or execute the game.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
from pathlib import Path

P = Path(__file__).resolve().parent

CASE_KG = 25.0                 # SIM_TUNED, documented 24--26 kg range
EXPLOSIVE_KG = 3.7             # user-selected Mk 80 game load; source disagreement documented
OUTER_DIAMETER_M = 0.127       # PUBLIC_SPEC, nominal 5-inch bore
STEEL_DENSITY_KG_M3 = 7800.0   # SIM_TUNED mild-steel surrogate
COMP_B_SPECIFIC_WEIGHT_LB_IN3 = 0.0621  # SAND94-2255 table 5
GURNEY_FPS = 9100.0            # SAND94-2255 table 5
MOTT_B = 0.0554                # SAND94-2255 table 6, lb^1/2 in^-7/6
REFERENCE_FRAGMENT_KG = 0.0011 # NIJ 0117.01 table 8, nominal .22 FSP mass
TARGETS = {
    "Kh-35U": {"vitalAreaM2": 0.55, "v50Mps": 1450.0, "widthMps": 210.0},
    "Kh-32": {"vitalAreaM2": 1.0, "v50Mps": 1900.0, "widthMps": 230.0},
}
BIN_EDGES_KG = [0.0, 1e-5, 10**-4.5, 1e-4, 10**-3.5, 1e-3,
                10**-2.5, 1e-2, 10**-1.5, 0.1, math.inf]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


rho_comp_b = COMP_B_SPECIFIC_WEIGHT_LB_IN3 * 0.45359237 / 0.0254**3
case_volume = CASE_KG / STEEL_DENSITY_KG_M3
charge_volume = EXPLOSIVE_KG / rho_comp_b
equivalent_length = 4 * (case_volume + charge_volume) / (math.pi * OUTER_DIAMETER_M**2)
inner_diameter = OUTER_DIAMETER_M * math.sqrt(charge_volume / (case_volume + charge_volume))
wall_thickness = (OUTER_DIAMETER_M - inner_diameter) / 2
t_in = wall_thickness / 0.0254
di_in = inner_diameter / 0.0254
ma_sqrt_lb = MOTT_B * t_in**(5/6) * di_in**(1/3) * (1 + t_in / di_in)
mu_kg = ma_sqrt_lb**2 * 0.45359237
n0 = CASE_KG / (2 * mu_kg)
gurney_mps = GURNEY_FPS * 0.3048
fragment_speed_mps = gurney_mps / math.sqrt(CASE_KG / EXPLOSIVE_KG + 0.5)


def tail_count(x: float) -> float:
    return n0 * math.exp(-x)


def tail_mass(x: float) -> float:
    if math.isinf(x):
        return 0.0
    return n0 * mu_kg * (x*x + 2*x + 2) * math.exp(-x)


bins = []
for index, (lo, hi) in enumerate(zip(BIN_EDGES_KG, BIN_EDGES_KG[1:]), 1):
    a = math.sqrt(lo / mu_kg)
    b = math.inf if math.isinf(hi) else math.sqrt(hi / mu_kg)
    count = tail_count(a) - (0.0 if math.isinf(b) else tail_count(b))
    mass = tail_mass(a) - tail_mass(b)
    bins.append({
        "index": index,
        "loKg": lo,
        "hiKg": None if math.isinf(hi) else hi,
        "count": count,
        "massKg": mass,
        "representativeMassKg": mass / count,
    })

burst_speeds = []
g7_path = P.parent / "phase1a" / "evidence" / "g7" / "trials.jsonl"
for line in g7_path.read_text().splitlines():
    row = json.loads(line)
    for burst in row.get("burstVelocities", []):
        speed = burst.get("speedMps") if isinstance(burst, dict) else None
        if isinstance(speed, (int, float)) and math.isfinite(speed):
            burst_speeds.append(float(speed))
burst_median = statistics.median(burst_speeds)
target_speed = 280.0
pass_distance = 12.5
delay = 0.002
center_deg = math.degrees(math.atan2(
    pass_distance,
    (burst_median + target_speed) * (delay + pass_distance / fragment_speed_mps),
))


def arrival(theta_deg: float, projectile_speed: float) -> dict[str, float]:
    x = pass_distance / math.tan(math.radians(theta_deg)) - (projectile_speed + target_speed) * delay
    w = -(projectile_speed + target_speed)
    aa = w*w - fragment_speed_mps**2
    bb = 2*x*w
    cc = x*x + pass_distance**2
    disc = bb*bb - 4*aa*cc
    roots = [(-bb - math.sqrt(disc))/(2*aa), (-bb + math.sqrt(disc))/(2*aa)]
    time_s = min(root for root in roots if root > 0)
    return {
        "bodyPolarDeg": math.degrees(math.atan2(pass_distance, x + w*time_s)),
        "fragmentTimeS": time_s,
    }


old_matching = json.loads((P.parent / "phase1a" / "matching.json").read_text())
design_rows = []
for old in old_matching["preImplementationRangeComparison"]:
    speed = old["phase1ActualBurstSpeedMps"]
    design_rows.append({
        "rangeKm": old["rangeKm"],
        "representativeBurstSpeedMps": speed,
        "newFixedDesign": arrival(center_deg, speed),
    })

solid_angle = 4 * math.pi * math.sin(math.radians(20))
unit_rows = []
for target, tp in TARGETS.items():
    for distance in (5, 10, 15, 20, 25):
        area = distance**2 * solid_angle
        expected = 0.0
        bin_rows = []
        for item in bins:
            m = item["representativeMassKg"]
            v50 = tp["v50Mps"] * (REFERENCE_FRAGMENT_KG / m)**(1/3)
            impact = math.hypot(fragment_speed_mps, target_speed)
            ppen = 1 / (1 + math.exp(-(impact - v50) / tp["widthMps"]))
            density = item["count"] / area
            contribution = density * tp["vitalAreaM2"] * ppen
            expected += contribution
            bin_rows.append({
                "bin": item["index"], "densityM2": density, "v50Mps": v50,
                "penetrationProbability": ppen, "expectedLethalHits": contribution,
            })
        unit_rows.append({
            "target": target, "distanceM": distance, "impactSpeedMps": impact,
            "expectedLethalHits": expected, "pk": -math.expm1(-expected), "bins": bin_rows,
        })

model = {
    "schema": "AEGIS_GUN_B2B_MOTT_1",
    "provenance": "PUBLIC_REF_PLUS_SIM_TUNED_EQUIVALENT_CYLINDER",
    "input": {
        "caseMassKg": CASE_KG, "caseMassRangeKg": [24, 26], "explosiveMassKg": EXPLOSIVE_KG,
        "outerDiameterM": OUTER_DIAMETER_M, "steelDensityKgM3": STEEL_DENSITY_KG_M3,
        "compBSpecificWeightLbIn3": COMP_B_SPECIFIC_WEIGHT_LB_IN3,
        "compBDensityKgM3": rho_comp_b, "gurneyFps": GURNEY_FPS,
        "gurneyMps": gurney_mps, "mottB": MOTT_B,
        "referenceFragmentMassKg": REFERENCE_FRAGMENT_KG,
    },
    "equivalentCylinder": {
        "innerDiameterM": inner_diameter, "wallThicknessM": wall_thickness,
        "effectiveLengthM": equivalent_length, "caseVolumeM3": case_volume,
        "chargeVolumeM3": charge_volume,
    },
    "mott": {
        "maSqrtLb": ma_sqrt_lb, "muKg": mu_kg, "n0": n0,
        "massBinEdgesKg": [None if math.isinf(x) else x for x in BIN_EDGES_KG],
        "bins": bins, "countSum": sum(x["count"] for x in bins),
        "massSumKg": sum(x["massKg"] for x in bins),
        "countError": sum(x["count"] for x in bins) - n0,
        "massErrorKg": sum(x["massKg"] for x in bins) - CASE_KG,
    },
    "fragmentSpeedMps": fragment_speed_mps,
    "fuzeMatching": {
        "g7Source": str(g7_path.relative_to(P.parents[3])), "g7Sha256": sha(g7_path),
        "burstCount": len(burst_speeds), "burstSpeedMedianMps": burst_median,
        "targetSpeedMps": target_speed, "passDistanceM": pass_distance,
        "processingDelayS": delay, "fixedPolarCenterDeg": center_deg,
        "within20to80": 20 <= center_deg <= 80, "designRows": design_rows,
    },
    "unitRows": unit_rows,
}

assert abs(model["mott"]["countError"]) < 1e-9
assert abs(model["mott"]["massErrorKg"]) < 1e-10
assert model["fuzeMatching"]["within20to80"]
(P / "model-parameters.json").write_text(json.dumps(model, indent=2) + "\n")

with (P / "mott-bins.csv").open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=bins[0].keys(), lineterminator="\n")
    writer.writeheader(); writer.writerows(bins)
with (P / "unit-pk.csv").open("w", newline="") as f:
    fields = ["target", "distanceM", "impactSpeedMps", "expectedLethalHits", "pk"]
    writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
    writer.writeheader(); writer.writerows({k: row[k] for k in fields} for row in unit_rows)
with (P / "unit-pk-bins.csv").open("w", newline="") as f:
    fields = ["target", "distanceM", "bin", "densityM2", "v50Mps",
              "penetrationProbability", "expectedLethalHits"]
    writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for row in unit_rows:
        for item in row["bins"]:
            writer.writerow({"target":row["target"],"distanceM":row["distanceM"],**item})

print(json.dumps({
    "fragmentSpeedMps": fragment_speed_mps, "muKg": mu_kg, "n0": n0,
    "countSum": model["mott"]["countSum"], "massSumKg": model["mott"]["massSumKg"],
    "burstCount": len(burst_speeds), "burstMedianMps": burst_median,
    "centerDeg": center_deg, "within20to80": 20 <= center_deg <= 80,
}, indent=2))
