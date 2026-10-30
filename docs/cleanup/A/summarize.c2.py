"""Strict latest/CLEAN results comparison; expected failures are not excluded."""
from pathlib import Path
import gzip,hashlib,json
H=Path(__file__).resolve().parent;E=H/'evidence/c2'
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
summary={}
for suite in ['release','common','natural']:
 a,b=[read(E/t/(suite+'.json.gz'))for t in ['LATEST','CLEAN']]
 assert len(a['rows'])==len(b['rows'])
 pairs=list(zip(a['rows'],b['rows']));assert all(x['id']==y['id']and x['condition']==y['condition']for x,y in pairs)
 changes=[{'id':x['id'],'condition':x['condition'],'old':x['result'],'new':y['result']}for x,y in pairs if x['result']!=y['result']]
 newfail=[x['id']for x,y in pairs if x['result'].get('success')and not y['result'].get('success')]
 s={'shots':len(pairs),'oldSuccess':sum(bool(x['result'].get('success'))for x,y in pairs),'newSuccess':sum(bool(y['result'].get('success'))for x,y in pairs),'successToFailure':newfail,'exactResultChanges':len(changes),'errors':a.get('errors',[])+b.get('errors',[]),'elapsedS':{'LATEST':a['elapsedS'],'CLEAN':b['elapsedS']},'completeReturnsBitIdentical':not changes}
 summary[suite]=s
 if changes:(E/(suite+'-changes.json')).write_text(json.dumps(changes,indent=2)+'\n')
 assert not newfail and not s['errors']
(H/'evidence/c2-comparison.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary))
