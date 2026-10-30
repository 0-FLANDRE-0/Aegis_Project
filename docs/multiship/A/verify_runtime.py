"""Real browser checks of detached state, predeparture choices and atomic import."""
import argparse,hashlib,json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'docs/bunkerhill/K'))
from browser_i import launch,load
def main():
    p=argparse.ArgumentParser();p.add_argument('html',type=Path);p.add_argument('out',type=Path);args=p.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    errors=[];rows=[]
    with sync_playwright() as pw:
        browser=launch(pw)
        for own in ['DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']:
            page=load(browser,args.html.read_bytes(),ship=own,errors=errors)
            result=page.evaluate('''()=>{
              const d=window.__NAVAL_SIM_DIAG__,checks={},snap=()=>d.multiShipSnapshotA(),fp=()=>JSON.stringify(d.operationalImportMutationFingerprintV48Wip11B());
              const isolation=d.multiShipIsolationAuditA();checks.isolation=isolation.pass;checks.coreZero=window.__CORE_SELFTEST_FAILURES__.length===0;checks.ownership=d.runtimeOwnershipAuditV48Wip11A().pass;
              const cases=[];
              for(const target of ['NONE','HULK'])for(const enemy of [null,'DDG_119_LATE_FLIGHT_IIA','CG_52_LATE_TICONDEROGA']){
                window.__WIP125_DIAG__.forcePreSail();
                const ui=document.querySelector('#wip125LoadoutOverlay [data-deployment-a]'),tp=ui.querySelector('[data-target-choice]'),ep=ui.querySelector('[data-enemy-choice]');
                tp.value=target;ep.value=enemy??'NONE';ep.dispatchEvent(new Event('change',{bubbles:true}));
                document.getElementById('wip125DepartBtn').click();const s=snap(),exp=d.exportOperationalStateV48Wip11A(),counts=d.profilerSnapshotV48Wip11A().entityCounts??d.runtimeEntityCountsV48Wip11A?.();
                const row={target,enemy,snapshot:s,counts};cases.push(row);
                checks[target+'.'+enemy+'.registered']=s.registered===(enemy?2:1)&&s.simulated===1&&s.ships[0].profileId===exp.profileId;
                checks[target+'.'+enemy+'.target']=exp.deployment.targetShip===target&&d.operationalImportMutationFingerprintV48Wip11B().world.surfaceIds.length===(target==='HULK'?1:0);
                checks[target+'.'+enemy+'.locked']=window.__AEGIS_DEPLOYMENT_A__.setDraft({...exp.deployment,targetShip:target==='NONE'?'HULK':'NONE'}).errors.includes('DEPLOYMENT_LOCKED_AFTER_DEPARTURE');
                if(enemy){const e=s.ships.find(r=>r.role==='ENEMY');checks[target+'.'+enemy+'.bound']=Object.values(e.bound).every(Boolean)&&e.execution==='STATE_BOUND_INACTIVE'&&e.vlsCells===(enemy.startsWith('DDG')?96:122)&&e.closeInTypes.join(',')===(enemy.startsWith('DDG')?'GUN,RAM':'GUN,GUN');}
                const validation=d.validateOperationalStateV48Wip11A(exp);checks[target+'.'+enemy+'.saveValid']=validation.ok;
                const imported=d.importOperationalStateV48Wip11A(exp);checks[target+'.'+enemy+'.import']=imported.validation.ok&&snap().registered===s.registered;
                d.resetEntireSessionV48Wip11A();checks[target+'.'+enemy+'.reset']=snap().registered===s.registered&&snap().deployment.committed.enemyProfileId===enemy;
              }
              const valid=d.exportOperationalStateV48Wip11A(),invalids=[null,{}, {...valid.deployment,targetShip:'BAD'}, {...valid.deployment,enemyProfileId:'BAD'}, {...valid.deployment,enemyProfileId:false}, {...valid.deployment,truthRef:{}}];
              for(let i=0;i<invalids.length;i++){const bad=structuredClone(valid);bad.deployment=invalids[i];const before=fp();let rejected=false;try{rejected=!d.importOperationalStateV48Wip11A(bad).ok;}catch(e){rejected=String(e.message).startsWith('Operational state rejected:');}checks['invalid.'+i]=rejected&&fp()===before;}
              const legacy=structuredClone(valid);delete legacy.deployment;const lv=d.validateOperationalStateV48Wip11A(legacy);checks.legacyMigration=lv.ok&&lv.migrations.some(q=>q.id==='LEGACY_DEPLOYMENT_MULTI_SHIP_A');
              for(const role of ['PLAYER','INVALID']){const before=fp();let rejected=false;try{d.spawnShipRuntimeV48Wip11A(valid.profileId,{entityId:'DIAG_INVALID_ROLE',role});}catch(e){rejected=String(e.message)==='PREPARED_SHIP_ROLE_INVALID';}checks['reservedRole.'+role]=rejected&&fp()===before;}
              checks.faultsZero=!window.__WIP125_DIAG__.wip150RuntimeFault()&&!window.__WIP125_DIAG__.wip150PresentationFault();
              return {checks,isolation,cases,pass:Object.values(checks).every(Boolean)};
            }''')
            result['own']=own;rows.append(result);page.close();print(json.dumps({'own':own,'pass':result['pass'],'failed':[k for k,v in result['checks'].items() if not v]}),flush=True)
        browser.close()
    report={'sha256':hashlib.sha256(args.html.read_bytes()).hexdigest(),'cases':rows,'errors':errors,'pass':all(r['pass'] for r in rows) and not errors};(args.out/'runtime.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');raise SystemExit(0 if report['pass'] else 1)
if __name__=='__main__':main()
