"""Shared offline browser setup; main override is explicitly experimental."""
from pathlib import Path
import base64,gzip,hashlib,json,os,re,shutil
def served_bytes(html,main_override=None):
    data=Path(html).read_bytes()
    if not main_override:return data
    html=data.decode();raw=Path(main_override).read_bytes();gz=gzip.compress(raw,9,mtime=0)
    m=re.search(r'<script type="application/octet-stream" data-c55-index="13">(.*?)</script>',html,re.S)
    html=html[:m.start(1)]+base64.b64encode(gz).decode()+html[m.end(1):]
    m=re.search(r'const records=(\[.*?\]);',html,re.S);rows=json.loads(m[1]);rows[13].update(rawBytes=len(raw),gzipBytes=len(gz),sha256=hashlib.sha256(raw).hexdigest())
    return (html[:m.start(1)]+json.dumps(rows,separators=(',',':'))+html[m.end(1):]).encode()
def launch(pw,webgl=False):
    args=['--no-sandbox','--disable-dev-shm-usage']
    args+=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']if webgl else ['--disable-gpu']
    return pw.chromium.launch(executable_path=os.environ.get('AEGIS_CHROMIUM_EXECUTABLE')or shutil.which('chromium'),headless=True,args=args)
def load(browser,body,ship='CG_52_LATE_TICONDEROGA',webgl=False,seed=0x6d2b79f5,errors=None):
    page=browser.new_page(viewport={'width':640,'height':480}if webgl else {'width':1000,'height':760})
    page.on('pageerror',lambda e:errors.append(str(e))if errors is not None else None)
    page.add_init_script(f'window.__NAVAL_SIM_SEED__={seed};')
    page.route('https://aegis.test/**',lambda r:r.fulfill(body=body,content_type='text/html'))
    page.goto('https://aegis.test/candidate?view3d='+('1'if webgl else '0'),wait_until='load',timeout=90000)
    page.wait_for_selector('#aegisShipConfirmBtn',timeout=90000);page.locator('#aegisShipSelect').select_option(ship);page.locator('#aegisShipConfirmBtn').click()
    page.wait_for_function('window.C55Packaging?.ready&&window.__WIP125_DIAG__'+('&&(window.__WIP148_3D_VIEW__?.ready||window.__WIP148_3D_VIEW__?._loadError)'if webgl else ''),timeout=120000)
    if webgl:
        error=page.evaluate("String(window.__WIP148_3D_VIEW__._loadError??'')")
        if error:raise RuntimeError(error)
    page.evaluate("()=>{document.getElementById('wip125DepartBtn').click();window.__NAVAL_SIM_DIAG__.ciwsB1Closure.setPaused(true);}")
    if webgl:page.evaluate("window.__WIP148_3D_VIEW__.c12ApplyPreset('LOW')")
    return page
