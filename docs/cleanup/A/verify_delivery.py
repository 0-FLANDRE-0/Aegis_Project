"""Read-only table integrity and exact fixed-tick latest/CLEAN world comparison."""
from pathlib import Path
import base64,gzip,hashlib,json,re,sys,time
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[2]
sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'))
from browser_tools import launch,load_fleet
build=json.loads((H/'build.json').read_text());raw=(R/build['output']).read_bytes()
base=(R/'Aegis_SIM_v48_WIP_ENV_D_REMEASURE_A.html').read_bytes()
checks={};errors=[];records=[]
def main(data):return gzip.decompress(base64.b64decode(re.search(rb'data-c55-index="13">([^<]+)</script>',data)[1])).decode()
pat=r'// ENV_D_DATA_BEGIN[\s\S]*?// ENV_D_DATA_END'
checks['gameOutsideDataBlockByteExact']=re.sub(pat,'',main(raw))==re.sub(pat,'',main(base))
def shell(data):
 s=data.decode();s=re.sub(r'(data-c55-index="13">)[^<]+',r'\1<MAIN>',s)
 m=re.search(r'const records=(\[.*?\]);',s,re.S);a=json.loads(m[1])
 a[13]={**a[13],'rawBytes':None,'gzipBytes':None,'sha256':None}
 return s[:m.start(1)]+json.dumps(a,separators=(',',':'))+s[m.end(1):]
checks['outerShellAndAssetsByteExact']=shell(raw)==shell(base)
with sync_playwright()as pw:
 b=launch(pw)
 for tag,ship in [('DDG','DDG_119_LATE_FLIGHT_IIA'),('CG','CG_52_LATE_TICONDEROGA')]:
  p=load_fleet(b,raw,own=ship,errors=errors)
  before=p.evaluate('JSON.stringify([__NAVAL_SIM_DIAG__.snapshot(),__HARPOON_DIAG_A__.snapshot().rng])')
  status=p.evaluate('__ENV_D__.status()');table=p.evaluate('__ENV_D__.table()')
  after=p.evaluate('JSON.stringify([__NAVAL_SIM_DIAG__.snapshot(),__HARPOON_DIAG_A__.snapshot().rng])')
  checks[tag+'.statusMatch']=status['match']and not status['recalculationRequired']
  checks[tag+'.schema2']=table['schema']=='AEGIS_ENVELOPE_TABLE_D_2'
  checks[tag+'.rows120']=len(table['rows'])==120
  checks[tag+'.apiIsolation']=before==after
  checks[tag+'.pendingAccurate']=status['pendingEffectiveCells']==build['pendingCells']
  checks[tag+'.core0']=not p.evaluate('__CORE_SELFTEST_FAILURES__')
  records.append({'ship':ship,'status':status});p.close()
 b.close()
original=R/'docs/envelope/D/verify_world120.py';s=original.read_text()
out=H/'evidence/world120';out.mkdir(exist_ok=True)
s=s.replace("E=H/'evidence/reg-k'",'E=Path('+repr(str(out))+')')
a=s.index("FILES={'recovery':");z=s.index("STATE='''",a)
s=s[:a]+"FILES={'recovery':Path("+repr(str(R/'Aegis_SIM_v48_WIP_ENV_D_REMEASURE_A.html'))+"),'current':Path("+repr(str(R/build['output']))+")}\n"+s[z:]
try:exec(compile(s,str(original),'exec'),{'__file__':str(original),'__name__':'__main__'})
except SystemExit as e:assert e.code==0
world=json.loads((out/'world120.json').read_text())
checks['idle120Identical']=world['checks']['idleSameTruthHash']
checks['combat120Identical']=not world['combatHashChanged']
checks['worldCore0']=world['checks']['core0']
checks['pageErrors0']=not errors and not world['errors']
result={'pass':all(checks.values()),'checks':checks,'records':records,'errors':errors,'htmlSha256':hashlib.sha256(raw).hexdigest()}
(H/'evidence/delivery.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result));raise SystemExit(0 if result['pass']else 1)
