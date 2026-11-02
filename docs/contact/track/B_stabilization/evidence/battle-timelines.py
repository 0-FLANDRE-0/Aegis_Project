"""Standalone SVG reporting from recorded native events only; no simulation."""
from pathlib import Path
import gzip,json,html

P=Path(__file__).resolve().parents[1];E=P/'evidence/battle-analysis'
def main():
 data=json.loads(gzip.decompress((E/'DETAILS.json.gz').read_bytes()))['rows']
 order={'track-a':0,'old-shadow':1,'old-active':2,'candidate-shadow':3,'candidate-active':4}
 cases=['DDG_CONVERGING_2','CG_MULTIPLE_3','DDG_BEARING_CROSSING_2','NATURAL_SATURATION_13']
 out=['<svg xmlns="http://www.w3.org/2000/svg" width="1260" height="1160" viewBox="0 0 1260 1160">','<rect width="1260" height="1160" fill="#111923"/>','<style>text{font:13px monospace;fill:#dae3ed}.title{font:bold 18px sans-serif}</style>','<text x="20" y="28" class="title">Natural battle native timelines — frozen evidence, no coefficient changes</text>','<text x="20" y="50">Blue: first recorded sensor update · purple: release · green: effect · red: damaging hit · orange: actual HOLD interval</text>']
 y=80;x0=240;w=960
 for case in cases:
  rows=sorted((r for r in data if r['case']==case),key=lambda r:order[r['version']]);limit=90 if case=='NATURAL_SATURATION_13'else 30
  out.append(f'<text x="20" y="{y}" class="title">{case} (0–{limit}s)</text>');y+=26
  for r in rows:
   X=lambda t:x0+w*t/limit
   out.append(f'<text x="20" y="{y+4}">{html.escape(r["version"])}</text><line x1="{x0}" y1="{y}" x2="{x0+w}" y2="{y}" stroke="#405067"/>')
   for hold in r.get('holdDurations',[]):out.append(f'<rect x="{X(hold["startStep"]/60):.2f}" y="{y-8}" width="{max(.3,w*hold["durationS"]/limit):.2f}" height="16" fill="#d38a2d" opacity=".2"/>')
   for event in r['nativeEffectPairs']:out.append(f'<circle cx="{X(event["timeS"]):.2f}" cy="{y}" r="3" fill="#56c78b"/>')
   for key,color in [('firstRecordedSensorUpdateS','#51bbef'),('firstWeaponLaunchS','#c690ff'),('firstDamagingShipHitS','#f07878')]:
    t=r['times'].get(key)
    if t is not None:out.append(f'<line x1="{X(t):.2f}" y1="{y-10}" x2="{X(t):.2f}" y2="{y+10}" stroke="{color}" stroke-width="3"/>')
   t=r['end']['timeS'];color='#f07878'if r['status']!='QUALIFYING_COMPLETED_BATTLE'else'#e2e9ef'
   out.append(f'<circle cx="{X(t):.2f}" cy="{y}" r="5" fill="{color}"/><text x="{x0}" y="{y+19}">end {t:.2f}s · HP {r["hp"]} · remaining {r["end"]["remainingInitialThreats"]} · applied HOLD plots {r["counts"].get("actualHeldPlotAppearances",0)}</text>');y+=45
  for t in range(0,limit+1,10):out.append(f'<text x="{x0+w*t/limit:.2f}" y="{y-6}">{t}</text>')
  y+=20
 out+=['<text x="20" y="1140">19 captured pages:15 completed main battles;4 saturation lifecycle-incomplete. New saturation regression remains unapproved.</text>','</svg>'];(E/'battle-native-timelines.svg').write_text('\n'.join(out)+'\n')

if __name__=='__main__':main()
