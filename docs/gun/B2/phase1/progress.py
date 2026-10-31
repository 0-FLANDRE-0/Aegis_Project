from pathlib import Path
import argparse,json,time,datetime
P=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--wait',type=int,default=0);a=ap.parse_args();assert 0<=a.wait<=50
time.sleep(a.wait)
g7=sum(sum(1 for _ in p.open())for p in(P/'evidence/g7').glob('*.jsonl'));curve=sum(sum(1 for _ in p.open())for p in(P/'evidence/range-intercept').glob('*.jsonl'))
r=sorted((P/'evidence/regression').glob('*.done.json'),key=lambda p:p.stat().st_mtime);last=json.loads(r[-1].read_text())if r else None
out={'UTC':datetime.datetime.now(datetime.timezone.utc).strftime('%H:%M:%S'),'G7':f'{g7}/960','거리시도':f'{curve}/1440','회귀작업처리':{'실행완료':sum(json.loads(p.read_text()).get('exit')is not None and json.loads(p.read_text()).get('exit')!=-15 for p in r),'중복중단':sum(json.loads(p.read_text()).get('exit')==-15 for p in r),'근거재사용':sum(json.loads(p.read_text()).get('exit')is None for p in r)},'최근회귀':last,'물리후속완료':(P/'evidence/v2-checks-execution.json').exists(),'기존회귀전체완료':(P/'evidence/regression/execution.json').exists()and(P/'evidence/canonical-on-ui-execution.json').exists()and json.loads((P/'evidence/canonical-on-ui-execution.json').read_text())['exit']==0,'함포회귀전체완료':(P/'evidence/gun-regression/execution.json').exists()}
gun=sorted((P/'evidence/gun-regression').glob('*.done.json'),key=lambda p:p.stat().st_mtime)
if gun:out['함포최근작업']=json.loads(gun[-1].read_text())
for mode in ['OFF','ON']:
 f=P/f'evidence/regression/{mode}/map/E/evidence/ui-execution.json'
 if f.exists():out['UI_'+mode]=json.loads(f.read_text())['rows'][-1]
print(json.dumps(out,ensure_ascii=False))
