"""Final-core alignment-only sample: reuse exact same-build OFF8, run ON8 fresh."""
from pathlib import Path
import json,os,subprocess,sys,time
P=Path(__file__).resolve().parent;R=P.parents[3];E=P/'evidence/alignment-final';E.mkdir(parents=True,exist_ok=True);q=json.loads((P/'evidence/final-pairs/results.json').read_text());rows=[r for r in q['rows']if not r['case']['alignment']];assert len(rows)==8
(E/'worker0.json').write_text(json.dumps({'rows':rows,'errors':[],'elapsedS':0,'reuse':{'source':'evidence/final-pairs/results.json','reason':'Same925178b5 build, same inputs/seeds, all5 flagsOFF, identical G2 fixture. No new firing.'}},separators=(',',':'))+'\n');env={**os.environ,'B2_ALIGNMENT_OUT':str(E),'TMPDIR':'/dev/shm','PYTHONDONTWRITEBYTECODE':'1'}
for arg in ['1','--collect']:
 with(E/('worker1.log'if arg=='1'else'collection.log')).open('w')as f:r=subprocess.run([sys.executable,'-u',str(P/'verify_alignment.py'),arg],cwd=R,env=env,stdout=f,stderr=subprocess.STDOUT)
 if r.returncode:raise SystemExit(r.returncode)
