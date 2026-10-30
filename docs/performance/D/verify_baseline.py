"""Same-seed PERF_C/PERF_D paired regression; exported ship state and RNG exact."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];SOURCE=ROOT/'docs/multiship/H4/regression_baseline.py'
source=SOURCE.read_text().replace("['performance','ew','network','tactical','maneuver','attack','team']","['performance']")
source=source.replace('AEGIS_MULTI_SHIP_H4_BASELINE_COMPARISON','AEGIS_PERFORMANCE_D_BASELINE_COMPARISON')
source=source.replace('H3/H4','PERF_C/PERF_D').replace('exclude existing EW/network/tactical metadata, new attack settings and profiler','exclude only profiler; EW/network/tactical/maneuver/attack/team state included')
source=source.replace('abs(count_vls(pair[\'baseline\'])-count_vls(pair[\'candidate\']))<=1','count_vls(pair[\'baseline\'])==count_vls(pair[\'candidate\'])')
source=source.replace('Ownship defense/maneuver utility is OFF by default. No allied peers or Harpoon launch in this paired regression; H3-on maneuver and native defense are verified separately.','No intended combat behavior change. No allied peers or Harpoon launch in this paired ownship regression; three-owner parity and native defense are verified separately.')
scope={'__file__':str(SOURCE),'__name__':'_perf_c_baseline'};exec(compile(source,str(SOURCE),'exec'),scope)
if __name__=='__main__':scope['main']()
