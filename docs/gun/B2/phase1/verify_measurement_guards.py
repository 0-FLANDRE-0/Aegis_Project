"""Negative build tests on private files; never mutate the product/table/constants."""
from pathlib import Path
import hashlib,json,subprocess,sys,tempfile,shutil
P=Path(__file__).resolve().parent;R=P.parents[3];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();root=R/'Aegis_SIM_v48_WIP_GUN_B2.html';before=sha(root);rows=[]
for name in ['runtime','dispersion','compiled-spec','native-function']:
 with tempfile.TemporaryDirectory(prefix='b2-guard-',dir='/dev/shm')as d:
  T=Path(d)
  for f in ['runtime.js','dispersion-constants.json','range-table.json','ring.js']:shutil.copyfile(P/f,T/f)
  if name=='runtime':(T/'runtime.js').write_text((T/'runtime.js').read_text()+'\n// PRIVATE NEGATIVE MUTATION\n')
  elif name=='dispersion':(T/'dispersion-constants.json').write_text((T/'dispersion-constants.json').read_text()+' ')
  else:
   q=json.loads((T/'range-table.json').read_text())
   if name=='compiled-spec':q['compiledGunSpecSha256']='0'*64
   else:q['nativeSourceHashes']['gunB2ShellEvent']='0'*64
   (T/'range-table.json').write_text(json.dumps(q))
  text=(P/'build.py').read_text().replace("P=Path(__file__).resolve().parent;R=P.parents[3]","P=Path("+repr(str(T))+");R=Path("+repr(str(R))+")",1).replace("OUT=R/'Aegis_SIM_v48_WIP_GUN_B2.html'","OUT=P/'private-output.html'",1)
  script=T/'guard-build.py';script.write_text(text);q=subprocess.run([sys.executable,str(script),'--stage','all'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
  rows.append({'name':name,'rejected':q.returncode!=0 and 'GUN_B2_RANGE_REMEASUREMENT_REQUIRED:'in q.stdout,'noOutput':not(T/'private-output.html').exists(),'log':q.stdout})
checks={'allFourRejectedBeforeWrite':all(r['rejected']and r['noOutput']for r in rows),'productUnchanged':sha(root)==before};out={'pass':all(checks.values()),'checks':checks,'rows':rows,'htmlSha256':before};(P/'evidence/measurement-guards.json').write_text(json.dumps(out,indent=2)+'\n');print(checks);raise SystemExit(not out['pass'])
