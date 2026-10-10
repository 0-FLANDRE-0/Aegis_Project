"""Retain C sensor/offboard tests with E's active measured authorization contract.

C expected every foreign file UNKNOWN/WITHHELD before any AI existed. E retains
that protection for unknown/surface files and separately validates measured
hostile-intent authorization. Historical C source is unchanged; no controller
or sensor is disabled, and no target truth is read.
"""
import importlib.util,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;C=HERE.parent/'C';sys.path.insert(0,str(C))
def main():
 spec=importlib.util.spec_from_file_location('retained_c_observers_e',C/'verify_observers.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 old="checks.foreignAuthorityWithheld=foreign.tracks.every(t=>t.identity==='UNKNOWN'&&t.engagementAuthority==='WITHHELD');"
 new="""checks.foreignSurfaceProtected=near(foreign,ownNav.positionWorld.x/.0038,ownNav.positionWorld.y/.0038).every(t=>t.identity==='UNKNOWN'&&t.engagementAuthority==='WITHHELD');
 checks.foreignUnknownProtected=foreign.tracks.filter(t=>['UNKNOWN','FRIEND','NEUTRAL'].includes(t.identity)).every(t=>t.engagementAuthority==='WITHHELD');
 const files=window.__AEGIS_ENGAGEMENT_RUNTIME__.ships.get(id).combatSystem.trackManager.tracks;
 checks.foreignMeasuredAuthority=foreign.tracks.filter(t=>t.engagementAuthority==='AUTO_AUTHORIZED').every(t=>{const f=files.get(t.trackId);return t.identity==='ASSUMED_HOSTILE'&&t.threatStatus==='THREAT'&&t.classification==='ASM'&&t.confirmed&&t.sensorAgeS<=2&&f.classificationConfidence>=.58&&f.sensorHits>=2;});"""
 assert m.FIXTURE.count(old)==1;m.FIXTURE=m.FIXTURE.replace(old,new);m.main()
if __name__=='__main__':main()
