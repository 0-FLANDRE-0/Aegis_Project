"""Direct original-file suites; historical H4A evidence is not counted."""
import runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
SUITES={k:('docs/multiship/'+v[0],v[1])for k,v in runpy.run_path(str(ROOT/'docs/multiship/H4A/suite_catalog.py'))['SUITES'].items()}
SUITES['baseline']=('docs/performance/D/verify_baseline.py','baseline-comparison.json')
SUITES['semantics']=('docs/performance/D/verify_semantics.py','semantics.json')
SUITES['resources']=('docs/performance/D/verify_resources.py','resources.json')
SUITES['planner']=('docs/performance/D/verify_planner.py','planner.json')
SUITES['radar']=('docs/performance/D/verify_radar.py','radar.json')

SUITES['damage']=('docs/performance/D/verify_damage.py','damage.json')
SUITES['envelope']=('docs/performance/D/verify_envelope.py','envelope.json')
