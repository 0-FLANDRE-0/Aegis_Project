"""Resolve exact repository fixtures and record the browser used by each CI job."""
from pathlib import Path
import argparse, hashlib, importlib.metadata, json, os, sys

p = argparse.ArgumentParser()
p.add_argument('--browser', action='store_true')
a = p.parse_args()
out = Path(os.environ.get('AEGIS_EVIDENCE_DIR', 'artifacts/bunkerhill'))
out.mkdir(parents=True, exist_ok=True)
variables = {}
fixtures = {}
for key, name, folder, expected in [
    ('AEGIS_BUILD_BASELINE', 'Aegis_SIM_v48_WIP_STARTUP_A.html', 'WIP_STARTUP_A', '94f5e9321fe1f04c5b43c4d8dca5b0762014c1cffe358ad92a81b8ffe70e7c92'),
    ('AEGIS_SAVE_BASELINE', 'Aegis_SIM_v48_WIP16B.html', 'WIP16B', '7b63a62bb1cad123b7d7eb17c1fbe26452194c3ff2c637c09b4c48a2a6c8d76d'),
]:
    choices = [Path(name), Path('archive/v48') / folder / name]
    match = next((q for q in choices if q.is_file() and hashlib.sha256(q.read_bytes()).hexdigest() == expected), None)
    if match is None:
        raise SystemExit('EXACT_BASELINE_MISSING:' + name)
    variables[key] = str(match)
    fixtures[key] = {'path': str(match), 'sha256': expected}
candidate = Path('Aegis_SIM_v48_WIP_BUNKERHILL_K.html')
sha = hashlib.sha256(candidate.read_bytes()).hexdigest()
if sha != 'efe1a0994f172da878733023826e9383ed0aed3c8c9601d10177a5d9faf287df':
    raise SystemExit('UPLOADED_K_SHA_MISMATCH')
record = {'pythonVersion': sys.version, 'candidateSha256': sha, 'fixtures': fixtures}
if a.browser:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser_path = pw.chromium.executable_path
        if not Path(browser_path).is_file():
            raise SystemExit('PINNED_CHROMIUM_MISSING')
        variables['AEGIS_CHROMIUM_EXECUTABLE'] = browser_path
        browser = pw.chromium.launch(executable_path=browser_path, headless=True, args=['--no-sandbox'])
        record.update(browserVersion=browser.version, executablePath=browser_path,
                      playwrightVersion=importlib.metadata.version('playwright'),
                      baselineAndCandidateUseSameBrowser=True)
        browser.close()
with Path(os.environ['GITHUB_ENV']).open('a') as target:
    for key, value in variables.items():
        target.write(key + '=' + value + '\n')
(out / 'environment.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps(record), flush=True)
