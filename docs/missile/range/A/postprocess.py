"""Sequential local verification after both independent full sweeps. No Git writes."""
import argparse,os,shutil,subprocess
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[3];C=R/'docs/envelope/C';E=H/'evidence'
p=argparse.ArgumentParser();p.add_argument('first',type=Path);p.add_argument('second',type=Path);a=p.parse_args()
def run(*args):
 print('RUN',' '.join(str(x)for x in args),flush=True);subprocess.run([str(x)for x in args],cwd=R,check=True)
run('python',C/'verify_results.py',a.first,a.second,C/'evidence/verification')
for i,f in enumerate([a.first,a.second],1):shutil.copyfile(Path(str(f)+'.receipt.json'),C/f'evidence/run-{i}-receipt.json')
run('python',C/'report.py',a.first,C/'results')
run('python',C/'generate.py')
run('python',H/'build.py')
run('node',H/'verify_static.cjs',R/'Aegis_SIM_v48_WIP_RANGE_A.html',E/'static-final.json')
run('node',H/'verify_candidate_data_only.cjs',R/'Aegis_SIM_v48_WIP_RANGE_A.html',E/'candidate-data-only.json')
run('python',C/'verify_path_all4.py',R/'Aegis_SIM_v48_WIP_RANGE_A.html',C/'evidence/path-final')
run('python',C/'verify_status.py',R/'Aegis_SIM_v48_WIP_RANGE_A.html',C/'evidence/status')
run('python',C/'verify_boundaries.py',R/'Aegis_SIM_v48_WIP_RANGE_A.html',C/'evidence/boundaries')
run('python',C/'report_extra.py',a.first)
run('python',H/'finalize_reports.py')
print('LOCAL_POSTPROCESS_COMPLETE',flush=True)
