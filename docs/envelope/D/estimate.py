"""Conservative preflight estimate, using measured native CPU costs and old C search sizes."""
from pathlib import Path
import datetime,json,statistics
H=Path(__file__).resolve().parent;R=H.parents[2]
p=json.loads((H/'evidence/pilot.json').read_text());old=json.loads((R/'docs/envelope/C/ENVELOPE_TABLE_C.json').read_text())['rows']
cpu={w:statistics.mean(s['cpuS']for r in p['records']if r['weapon']==w for s in r['shots'])for w in ['SM2','SM2ER','SM6','ESSM']}
# Binary/coarse + all farther integer km + conservative full inner 5km grid.
# Historical C supplies a planning estimate, never a current ENV_D measurement.
shots={w:0 for w in cpu}
for r in old:shots[r['weapon']]+=min(496,500-r['maxRangeKm']+25+min(100,int(r['maxRangeKm']/5)))*5
# Additional CROSS motion adds 25% relative to the old four-motion grid.
main={w:round(n*1.25)for w,n in shots.items()}
aux=round(sum(main.values())*6/120)
repeat=126*4*5
trajectory=156+30
cpuSeconds=sum(main[w]*cpu[w]for w in cpu)+(aux+repeat+trajectory)*statistics.mean(cpu.values())
fullHours=cpuSeconds/4/3600*1.25
reducedHours=fullHours*(4/6)*.5
result={'schema':'AEGIS_ENV_D_PRE_EXECUTION_COST_1','timestampUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pilotShots':80,'pilotMeanCpuS':statistics.mean(cpu.values()),'pilotByWeaponCpuS':cpu,'workers':4,'coresQuota':4,'cpuReserveFactor':1.25,'planningSource':'HISTORICAL ENV_C upper-search sizes; not current performance values','expectedMainShotsByWeapon':main,'expectedMainShots':sum(main.values()),'expectedAuxiliaryShots':aux,'maximumBoundaryReplayShots':repeat,'trajectoryAndReplaySlots':trajectory,'expectedShotsTotal':sum(main.values())+aux+repeat+trajectory,'expectedHours':fullHours,'reducedExpectedShots':round((sum(main.values())+aux)*(4/6)*.5)+repeat+trajectory,'reducedExpectedHours':reducedHours,'reducedScope':'exclude 1km/10km altitude, outer resolution2km; not selected','sixHourRule':'FULL_ALLOWED_BY_EXPECTED_COST'if fullHours<=6 else'DO_NOT_START_FULL','reuseFlightAcrossSeeds':False,'exhaustiveAbsoluteUpperBoundShots':126*496*5+repeat+trajectory,'uncertainty':'New Kappa + real ASM damage + seed-dependent flights can alter search work. Upper bound is not the expected work. Full run is resumable per cell and is not automatically repeated.'}
(H/'COST_ESTIMATE.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
