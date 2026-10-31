"""Read-only long-run progress. Safe while JSONL writers are active."""
from pathlib import Path
import collections,datetime,json,os
from zoneinfo import ZoneInfo
B=Path(__file__).resolve().parent;E=B/'evidence';rows=[];bad=[]
for p in(E/'trials').glob('worker*.jsonl'):
 lines=p.read_text().splitlines(keepends=True)
 for i,line in enumerate(lines):
  try:rows.append(json.loads(line))
  except ValueError:
   if i<len(lines)-1 or line.endswith('\n'):bad.append({'file':p.name,'line':i+1})
g=collections.Counter((r['ship'],r['bearing'],r['count'],r['experiment'])for r in rows);inactive=[];meta=json.loads((E/'execution-start.json').read_text())
for i,pid in enumerate(meta['pids']):
 try:
  state=Path(f'/proc/{pid}/stat').read_text().split()[2]
  if state=='Z'and not(E/'trials'/f'worker{i}-complete.json').exists():inactive.append(i)
 except FileNotFoundError:
  if not(E/'trials'/f'worker{i}-complete.json').exists():inactive.append(i)
print(json.dumps({'timeKst':datetime.datetime.now(ZoneInfo('Asia/Seoul')).strftime('%H:%M:%S'),'cases':len(rows),'expected':2400,'shots':sum(len(r['data']['shots'])for r in rows),'conditions':len(g),'minTrialsPerCondition':min(g.values())if len(g)==80 else 0,'maxTrialsPerCondition':max(g.values(),default=0),'completeWorkers':sum((E/'trials'/f'worker{i}-complete.json').exists()for i in range(4)),'invalidCompleteLines':bad,'inactiveWorkers':inactive},separators=(',',':')))
