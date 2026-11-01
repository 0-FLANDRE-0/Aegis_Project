"""Read-only progress for the A-only corrected 480-case replacement."""
from pathlib import Path
import datetime,json
from zoneinfo import ZoneInfo
B=Path(__file__).resolve().parent;E=B/'evidence';d=E/'a-stop-corrected';rows=[];bad=[]
for p in d.glob('worker*.jsonl'):
 lines=p.read_text().splitlines(keepends=True)
 for i,l in enumerate(lines):
  try:rows.append(json.loads(l))
  except ValueError:
   if i<len(lines)-1 or l.endswith('\n'):bad.append({'file':p.name,'line':i+1})
meta=json.loads((E/'a-stop-start.json').read_text());inactive=[]
for i,pid in enumerate(meta['pids']):
 try:state=Path(f'/proc/{pid}/stat').read_text().split()[2]
 except FileNotFoundError:state='Z'
 if state=='Z'and not(d/f'worker{i}-complete.json').exists():inactive.append(i)
print(json.dumps({'timeKst':datetime.datetime.now(ZoneInfo('Asia/Seoul')).strftime('%H:%M:%S'),'cases':len(rows),'expected':480,'primaryCasesReady':1920+len(rows),'shots':sum(len(r['data']['shots'])for r in rows),'completeWorkers':sum((d/f'worker{i}-complete.json').exists()for i in range(4)),'invalidCompleteLines':bad,'inactiveWorkers':inactive},separators=(',',':')))
