"""Original 29 assertions, with actual WebGL on both ON and OFF flights.

The old harness opened 3D for only four ON flights. REG_K explicitly requests
eight real WebGL flights, so enable the same presentation path for controls too.
No target, clock, command, sensor, fuze or acceptance assertion is modified.
"""
from pathlib import Path
import hashlib,json,sys
H=Path(__file__).resolve().parent;R=H.parents[2]
p=R/'docs/missile/termination/A/verify_observed_world.py'
s=p.read_text();changes=[]
for needle in ["   if enabled:\n    page.evaluate('async()=>",'   if enabled:\n    old=page.evaluate']:
 assert s.count(needle)==1
 s=s.replace(needle,needle.replace('if enabled:','if True:'),1);changes.append(needle.splitlines()[-1].strip())
out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
(out/'harness-presentation-adaptation.json').write_text(json.dumps({'source':str(p.relative_to(R)),'sourceSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'changes':changes,'assertionChanges':0,'expectedNativeFlights':8,'expectedActualWebglFlights':8},indent=2)+'\n')
sys.path.insert(0,str(p.parent));sys.argv[0]=str(p)
exec(compile(s,str(p),'exec'),{'__name__':'__main__','__file__':str(p)})
