"""PERF_F/HELI_A six cases; exclude only profiler and the new aircraft schema."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];SOURCE=ROOT/'docs/multiship/H4/regression_baseline.py'
source=SOURCE.read_text().replace("['performance','ew','network','tactical','maneuver','attack','team']","['performance','aviation']")
source=source.replace('AEGIS_MULTI_SHIP_H4_BASELINE_COMPARISON','AEGIS_HELO_A_BASELINE_COMPARISON').replace('H3/H4','PERF_F/HELI_A')
source=source.replace("abs(count_vls(pair['baseline'])-count_vls(pair['candidate']))<=1","count_vls(pair['baseline'])==count_vls(pair['candidate'])")
source=source.replace('exclude existing EW/network/tactical metadata, new attack settings and profiler','exclude only profiler and new aircraft operational schema; EW/network/tactical/maneuver/attack/team included')
source=source.replace('Ownship defense/maneuver utility is OFF by default. No allied peers or Harpoon launch in this paired regression; H3-on maneuver and native defense are verified separately.','Cold helicopters, defense/maneuver utility OFF. No allied peers or Harpoon launch in this six-case paired regression. Native aviation is verified by the HELI_A native suite; no claim to repeat historical H3/H4 suites.')
scope={'__file__':str(SOURCE),'__name__':'_helo_baseline'};exec(compile(source,str(SOURCE),'exec'),scope)
if __name__=='__main__':scope['main']()
