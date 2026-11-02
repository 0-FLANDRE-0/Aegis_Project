"""Run the frozen S1 hook-equivalence and Kh-35U two-reflector matrix."""
from pathlib import Path
import gzip,hashlib,json,sys,time

P=Path(__file__).resolve().parent;R=P.parents[3];E=P/'evidence';E.mkdir(exist_ok=True)
sys.path[:0]=['/dev/shm/aegis-ciws-dmg-a/docs/pip/B','/dev/shm/aegis-ciws-dmg-a/docs/helicopter/H','/dev/shm/aegis-ciws-dmg-a/docs/multiship/G','/dev/shm/aegis-ciws-dmg-a/docs/bunkerhill/K']
import browser_backend;browser_backend.install()
from browser_i import launch,load
from playwright.sync_api import sync_playwright

def save(path,data):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def summarize(row):
 m=row['metrics'];return {'seed':row['setup']['seed'],'label':row['setup']['label'],'separationDeg':row['setup']['separationDeg'],'launchRangeKm':row['setup']['launchRangeKm'],'finalMode':row['final']['seekerMode'],'locked':row['final']['seekerLocked'],'searchAcquireReturns':m['searchAcquireReturns'],'candidateSwitches':m['candidateSwitches'],'bodyYawReversals':m['bodyYawReversals'],'acquireSteeringCommands':m['acquireSteeringCommands'],'firstCandidate':m['firstCandidate'],'firstTrack':m['firstTrack'],'faults':len(row['faults'])}

def main():
 html=R/'Aegis_SIM_v48_WIP_ASM_SEEKER_A_DIAG.html';assert sha(html)==json.loads((P/'DIAGNOSTIC_BUILD.json').read_text())['outputSha256']
 errors=[];started=time.monotonic();equivalence=[];matrix=[];raw_receipts=[];harpoon=None
 progress_path=P/'KH35U_REPRODUCTION_PROGRESS.json'
 if progress_path.exists():
  prior=json.loads(progress_path.read_text());matrix=prior.get('cases',[]);raw_receipts=prior.get('raw',[])
 completed={(q['launchRangeKm'],q['separationDeg']) for q in matrix}
 with sync_playwright() as pw:
  body=html.read_bytes();first=True
  for distance in [20,45]:
   for separation in [0,5,10,20,40]:
    if (distance,separation) in completed:continue
    browser=launch(pw);group_errors=[];page=load(browser,body,ship='DDG_119_LATE_FLIGHT_IIA',errors=group_errors);assert page.evaluate('typeof __ASM_SEEKER_A_DIAG__')=='object'
    if first:
     for label,seed in [('Kh-35U',519000),('Kh-35U',519009),('Kh-32',519100)]:
      q=page.evaluate("o=>__ASM_SEEKER_A_DIAG__.equivalence(o)",{'seed':seed,'label':label,'separationDeg':10,'launchRangeKm':20 if label=='Kh-35U' else 45,'maxTimeS':4});equivalence.append(q);assert q['equal'] and not q['onFaults'],q
     harpoon=page.evaluate('__ASM_SEEKER_A_DIAG__.harpoonCoreAudit()');first=False
    page.evaluate("__ASM_SEEKER_A_DIAG__.configure({enabled:true})");group=[]
    for seed in range(519000,519010):
     row=page.evaluate("o=>__ASM_SEEKER_A_DIAG__.runCommon(o)",{'seed':seed,'label':'Kh-35U','separationDeg':separation,'launchRangeKm':distance,'maxTimeS':12,'record':True});assert not row['faults'],row['faults'];group.append(row);matrix.append(summarize(row))
    page.close();browser.close();errors.extend(group_errors);blob=gzip.compress(json.dumps(group,ensure_ascii=False,separators=(',',':')).encode(),9,mtime=0);path=E/f'KH35U_{distance}KM_{separation}DEG_RAW.json.gz';path.write_bytes(blob);raw_receipts.append({'path':str(path.relative_to(P)),'sha256':hashlib.sha256(blob).hexdigest(),'cases':len(group)})
    save(P/'KH35U_REPRODUCTION_PROGRESS.json',{'completed':len(matrix),'planned':100,'elapsedS':time.monotonic()-started,'cases':matrix,'raw':raw_receipts})
 result={'schema':'AEGIS_ASM_SEEKER_A_S1_KH35U_MATRIX_1','status':'PASS' if all(q['locked'] for q in matrix) else 'OBSERVED_UNLOCKED_CASES','inputHtml':html.name,'inputSha256':sha(html),'elapsedS':time.monotonic()-started,'hookEquivalence':equivalence,'pageErrors':errors,'harpoonCoreAudit':harpoon,'cases':matrix,'raw':raw_receipts}
 save(P/'KH35U_REPRODUCTION.json',result)
 return result

if __name__=='__main__':
 r=main();print(json.dumps({'status':r['status'],'cases':len(r['cases']),'elapsedS':r['elapsedS'],'pageErrors':r['pageErrors'],'hookEquivalent':all(q['equal'] for q in r['hookEquivalence']),'locked':sum(q['locked'] for q in r['cases']),'candidateSwitches':sum(q['candidateSwitches'] for q in r['cases']),'searchAcquireReturns':sum(q['searchAcquireReturns'] for q in r['cases']),'acquireSteeringCommands':sum(q['acquireSteeringCommands'] for q in r['cases'])}))
