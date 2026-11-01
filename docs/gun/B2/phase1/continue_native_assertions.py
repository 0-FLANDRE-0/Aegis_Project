"""Continue legacy ON assertions after new beam correctly returns no event.
A missing event evaluates FALSE, never PASS. Original crash/log is preserved.
No game threshold, expected value or original test file is changed.
"""
from pathlib import Path
import hashlib,json,sys
P=Path(__file__).resolve().parent;R=P.parents[3];f=R/'docs/gun/B1/verify_native.py';source=f.read_text();replacements={"R/'Aegis_SIM_v48_WIP_GUN_B1.html'":"R/'Aegis_SIM_v48_WIP_GUN_B2.html'","q['event']['reason']=='MFF_PROXIMITY'and abs(q['event']['t']-.5)<1e-12":"q['event'] is not None and q['event']['reason']=='MFF_PROXIMITY'and abs(q['event']['t']-.5)<1e-12",'__GB_TEST__.shellProbe({kind:"SAM"}).event.triggerKind':'__GB_TEST__.shellProbe({kind:"SAM"}).event?.triggerKind'}
for old,new in replacements.items():assert old in source;source=source.replace(old,new)
# Isolate evidence from the preserved unmodified test's partial failure.
source=source.replace("E=H/'evidence/native'","E=H/'evidence/native-continuation'")
q={'originalFile':str(f.relative_to(R)),'originalSourceSha256':hashlib.sha256(f.read_bytes()).hexdigest(),'privateReplacementDiff':replacements,'assertionMeaning':'Absent event remains failure; no expectation/tolerance relaxed. Reaches remaining CG and burst assertions after original null dereference.'};d=P/'evidence/gun-regression';d.mkdir(parents=True,exist_ok=True);(d/'continuation-policy.json').write_text(json.dumps(q,indent=2)+'\n');sys.argv=[str(f)];exec(compile(source,str(f)+'::NULL_SAFE_RECORD_FALSE','exec'),{'__file__':str(f),'__name__':'__main__'})
