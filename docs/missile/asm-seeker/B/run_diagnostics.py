"""Run pinned ASM_SEEKER_B baseline matrices in the real browser engine."""
from pathlib import Path
import hashlib,json,sys,time
P=Path(__file__).resolve().parent;HTML=Path('/dev/shm/Aegis_SIM_v48_WIP_ASM_SEEKER_B_DIAG.html')
sys.path[:0]=['/dev/shm/aegis-ciws-dmg-a/docs/pip/B','/dev/shm/aegis-ciws-dmg-a/docs/helicopter/H','/dev/shm/aegis-ciws-dmg-a/docs/multiship/G','/dev/shm/aegis-ciws-dmg-a/docs/bunkerhill/K']
import browser_backend;browser_backend.install()
from browser_i import launch,load
from playwright.sync_api import sync_playwright
def save(name,obj):(P/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def main():
 started=time.monotonic();errors=[];body=HTML.read_bytes();rows=[];sam=[];cue=[]
 with sync_playwright() as pw:
  br=launch(pw);page=load(br,body,ship='DDG_119_LATE_FLIGHT_IIA',errors=errors);audit=page.evaluate('__ASM_SEEKER_B_DIAG__.audit()')
  for kind in ['DDG','CG','SOV','HULK']:
   for speed in [0,15]:
    for alt in [15,200]:
     for dist in [10,20,30,40,45,50]:
      opts=[{'seed':s,'kind':kind,'rangeKm':dist,'altM':alt,'speedKt':speed,'control':'TARGET'} for s in range(629300,629305)]
      rows.extend(page.evaluate('a=>a.map(o=>__ASM_SEEKER_B_DIAG__.runRangeCase(o))',opts));save('RANGE_PROGRESS.json',{'cases':len(rows),'elapsedS':time.monotonic()-started,'rows':rows})
  for control in ['SEA_CLUTTER','CHAFF','NO_TARGET']:
   c='CHAFF' if control=='CHAFF' else control
   for alt in [15,200]:
    for dist in [10,20,30,40,45,50]:
     opts=[{'seed':s,'kind':'DDG','rangeKm':dist,'altM':alt,'speedKt':0,'control':c} for s in range(629300,629305)]
     rows.extend(page.evaluate('a=>a.map(o=>__ASM_SEEKER_B_DIAG__.runRangeCase(o))',opts));save('RANGE_PROGRESS.json',{'cases':len(rows),'elapsedS':time.monotonic()-started,'rows':rows})
  for path in ['ESSM_BLOCK2_AIR','SM6_BLOCK_IA_AIR','SM6_BLOCK_IA_SURFACE']:
   for target in ['AIRCRAFT','ASM','SEA_CLUTTER','CHAFF']:
    for dist in [10,20,30,40,45,50]:
     opts=[{'seed':s+200000,'path':path,'targetKind':target,'rangeKm':dist} for s in range(629300,629305)]
     sam.extend(page.evaluate('a=>a.map(o=>__ASM_SEEKER_B_DIAG__.runSamArhCase(o))',opts))
  for label in ['Kh-32','Kh-35U']:
   for dist in [60,100,130]:
    for speed,turn in [(15,0),(30,0),(30,30),(30,90)]:
     opts=[{'seed':s,'label':label,'rangeKm':dist,'speedKt':speed,'turnDeg':turn} for s in range(729300,729305)]
     cue.extend(page.evaluate('a=>a.map(o=>__ASM_SEEKER_B_DIAG__.runCueCase(o))',opts));save('CUE_PROGRESS.json',{'cases':len(cue),'elapsedS':time.monotonic()-started,'rows':cue})
  br.close()
 result={'schema':'AEGIS_ASM_SEEKER_B_BASELINE_DIAGNOSTICS_1','input':str(HTML),'inputSha256':hashlib.sha256(body).hexdigest(),'elapsedS':time.monotonic()-started,'audit':audit,'pageErrors':errors,'rangeCases':rows,'samArhCases':sam,'cueCases':cue}
 save('BASELINE_DIAGNOSTICS.json',result);print(json.dumps({'range':len(rows),'sam':len(sam),'cue':len(cue),'elapsedS':result['elapsedS'],'errors':errors}));return result
if __name__=='__main__':main()
