"""Untouched delivered HTML: schema/status plus native 120-second world hashes."""
from pathlib import Path
import base64,gzip,hashlib,json,re,sys
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(R/'docs/missile/fuze-zem/A'))
from browser_tools import launch,load_fleet
build=json.loads((H/'build.json').read_text());raw=(R/build['output']).read_bytes();base=(R/'Aegis_SIM_v48_WIP_CLEAN_A.html').read_bytes();checks={};errors=[];records=[]
def main(b):return gzip.decompress(base64.b64decode(re.search(rb'data-c55-index="13">([^<]+)',b)[1]))
pattern=rb'// ENV_D_DATA_BEGIN[\s\S]*?// ENV_D_DATA_END';checks['gameCodeByteExact']=re.sub(pattern,b'',main(raw))==re.sub(pattern,b'',main(base))
def shell(b):
 s=re.sub(rb'(data-c55-index="13">)[^<]+',rb'\1<MAIN>',b);m=re.search(rb'const records=(\[.*?\]);',s,re.S);rs=json.loads(m[1]);rs[13]={**rs[13],'rawBytes':None,'gzipBytes':None,'sha256':None};return s[:m.start(1)]+json.dumps(rs,separators=(',',':')).encode()+s[m.end(1):]
checks['shellUIAssetsByteExact']=shell(raw)==shell(base)
with sync_playwright()as pw:
 b=launch(pw)
 for tag,ship in [('DDG','DDG_119_LATE_FLIGHT_IIA'),('CG','CG_52_LATE_TICONDEROGA')]:
  p=load_fleet(b,raw,own=ship,errors=errors);before=p.evaluate('JSON.stringify([__NAVAL_SIM_DIAG__.snapshot(),__HARPOON_DIAG_A__.snapshot().rng])');status=p.evaluate('__ENV_D__.status()');summary=p.evaluate('()=>{const t=__ENV_D__.table();return{schema:t.schema,rows:t.rows.length,present:t.rows.every(r=>Number.isFinite(r.effectiveMinKm)&&Number.isFinite(r.effectiveMaxKm)&&r.effectiveMinKm<=r.effectiveMaxKm&&Array.isArray(r.otherRuns)&&Array.isArray(r.deadZones))}}');after=p.evaluate('JSON.stringify([__NAVAL_SIM_DIAG__.snapshot(),__HARPOON_DIAG_A__.snapshot().rng])');checks[tag+'.statusMatch']=status['match']and not status['recalculationRequired'];checks[tag+'.complete']=status['effectiveIntervalsComplete']and status['pendingEffectiveCells']==0 and not status['additionalMeasurementsRequired'];checks[tag+'.schema3']=summary['schema']=='AEGIS_ENVELOPE_TABLE_D_3'and summary['rows']==120 and summary['present'];checks[tag+'.readOnly']=before==after;checks[tag+'.core0']=not p.evaluate('__CORE_SELFTEST_FAILURES__');records.append({'ship':ship,'status':status,'tableSummary':summary});p.close()
 b.close()
original=R/'docs/envelope/D/verify_world120.py';s=original.read_text();out=H/'evidence/world120';out.mkdir(exist_ok=True)
s=s.replace("E=H/'evidence/reg-k'",'E=Path('+repr(str(out))+')');a=s.index("FILES={'recovery':");z=s.index("STATE='''",a);s=s[:a]+"FILES={'recovery':Path("+repr(str(R/'Aegis_SIM_v48_WIP_CLEAN_A.html'))+"),'current':Path("+repr(str(R/build['output']))+")}\n"+s[z:]
try:exec(compile(s,str(original),'exec'),{'__file__':str(original),'__name__':'__main__'})
except SystemExit as e:assert e.code==0
w=json.loads((out/'world120.json').read_text());checks['idle120Exact']=w['checks']['idleSameTruthHash'];checks['combat120Exact']=not w['combatHashChanged'];checks['worldCore0']=w['checks']['core0'];checks['pageErrors0']=not errors and not w['errors'];result={'pass':all(checks.values()),'checks':checks,'records':records,'errors':errors,'htmlSha256':hashlib.sha256(raw).hexdigest()};(H/'evidence/delivery.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));assert result['pass']
