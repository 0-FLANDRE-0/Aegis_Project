"""Recover immutable H/I using small modules and unchanged uploaded assets."""
from pathlib import Path
import argparse,hashlib,shutil,subprocess,sys,tempfile
p=argparse.ArgumentParser();p.add_argument('latest');p.add_argument('startup_a');p.add_argument('version',choices=['H','I','J']);p.add_argument('output');p.add_argument('--h-modules');a=p.parse_args()
here=Path(__file__).resolve().parent
reference=here if a.version in ['I','J']else Path(a.h_modules)if a.h_modules else here.parent/'H'
expected={'H':'5aaffab97043a08b43459a374247f559c05e2c104fd8af581d094934078a5dd6','I':'ea7a50cc63d503c20c37a09e6c7853306396d86bf39cce558d6df77791d4177a','J':'05306084448d4b68e25f696276346d3b9b2d4899d01a6b6d5b7ae2be9e2323b6'}[a.version]
if not reference.is_dir():raise SystemExit('EXACT_BASELINE_MODULES_MISSING:'+str(reference))
with tempfile.TemporaryDirectory()as tmp:
    target=Path(tmp)
    for f in reference.iterdir():
        if f.is_file()and(f.suffix in ['.py','.js']or f.name=='assets-manifest.json')and f.name!='candidate-main.js':shutil.copyfile(f,target/f.name)
    if a.version in ['I','J']:
        builder=target/'build_bunker.py';s=builder.read_text();anchor='    from refine_bunker_k import refine_k\n    s=refine_k(s)\n'
        if s.count(anchor)!=1:raise SystemExit('EXACT_J_REBUILD_CONTEXT_MISSING')
        builder.write_text(s.replace(anchor,'').replace('BUNKERHILL_K','BUNKERHILL_J'))
    if a.version=='I':
        builder=target/'build_bunker.py';s=builder.read_text();anchor='    from refine_bunker_j import refine_j\n    s=refine_j(s)\n'
        if s.count(anchor)!=1:raise SystemExit('EXACT_I_REBUILD_CONTEXT_MISSING')
        builder.write_text(s.replace(anchor,'').replace('BUNKERHILL_J','BUNKERHILL_I'))
    subprocess.run([sys.executable,str(target/'extract_embedded_assets.py'),str(Path(a.latest).resolve())],check=True)
    subprocess.run([sys.executable,str(target/'build_bunker.py'),str(Path(a.startup_a).resolve()),str(Path(a.output).resolve())],check=True)
actual=hashlib.sha256(Path(a.output).read_bytes()).hexdigest()
if actual!=expected:raise SystemExit('EXACT_'+a.version+'_BASELINE_REBUILD_MISMATCH:'+actual)
print('EXACT_'+a.version+'_BASELINE_OK:'+actual)
