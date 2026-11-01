"""Run the existing B1 exact EW-difference attribution on B2 raw reports.
No game expectation or original assertion is changed.
"""
from pathlib import Path
import json,sys
P=Path(__file__).resolve().parent;R=P.parents[3];f=R/'docs/gun/B1/verify_ew_inventory_delta.py';original=f.read_text();rows=[]
for mode in ['OFF','ON']:
 base=P/'evidence/regression'/mode
 if not(base/'map/E/evidence/ew-h3/summary.json').exists():continue
 source=original.replace("H/'evidence'",repr(str(base)))
 # Use a Path expression to preserve the original exact authorization predicate.
 source=original.replace("E=H/'evidence'","E=Path("+repr(str(base))+")")
 source=source.replace("E/('regression/map/E/evidence/ew-h3/ew-'","E/('map/E/evidence/ew-h3/ew-'")
 try:exec(compile(source,str(f)+'::B2_EXACT_INPUT','exec'),{'__file__':str(f),'__name__':'__main__'})
 except SystemExit as e:
  q=json.loads((base/'ew-inventory-differences.json').read_text());rows.append({'mode':mode,**q})
  if e.code:raise
(P/'evidence/ew-reconciliation.json').write_text(json.dumps({'pass':bool(rows)and all(r['pass']for r in rows),'rows':rows,'existingPredicateSource':str(f.relative_to(R))},indent=2)+'\n')
