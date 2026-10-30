"""Run one bounded release-regression slice in a fresh verification process."""
from pathlib import Path
import argparse,json,subprocess,tempfile
H=Path(__file__).resolve().parent;R=H.parents[3];mapping={'normal':'normal','dual':'dual','fault':'fault','battery':'battery','request':'release-request'}
p=argparse.ArgumentParser();p.add_argument('--kind',choices=mapping,required=True);p.add_argument('--start',type=int,required=True);p.add_argument('--end',type=int,required=True);a=p.parse_args();cases=json.loads((R/'docs/missile/termination/A/cases'/f'{mapping[a.kind]}.json').read_text());assert 0<=a.start<a.end<=len(cases)
parts=H/'release/parts';parts.mkdir(parents=True,exist_ok=True);case_file=Path('/dev/shm')/f'aegis-nv-{a.kind}-{a.start}-{a.end}.json';case_file.write_text(json.dumps(cases[a.start:a.end],separators=(',',':')));out=parts/f'{a.kind}-{a.start}-{a.end-1}.json';log=parts/f'{a.kind}-{a.start}-{a.end-1}.log';build=json.loads((H/'build.json').read_text());cmd=['python','docs/missile/termination/A/verify_live.py',build['variants']['FINAL']['file'],str(out),'--cases',str(case_file),'--batch','8']
with log.open('w')as stream:result=subprocess.run(cmd,cwd=R,stdout=stream,stderr=subprocess.STDOUT)
case_file.unlink(missing_ok=True);print(json.dumps({'kind':a.kind,'start':a.start,'end':a.end,'exitCode':result.returncode,'results':len(json.loads(out.read_text())['results'])if out.exists()else 0}));raise SystemExit(result.returncode)
