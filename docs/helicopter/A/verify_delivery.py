"""Validate portable GLB scenes and final inspector defaults/touch controls."""
import hashlib, json, struct
from pathlib import Path
from playwright.sync_api import sync_playwright
from browser_support import launch

ROOT = Path(__file__).resolve().parent
raw = (ROOT / 'seahawk-poses-lossless.glb').read_bytes()
n = struct.unpack_from('<I', raw, 12)[0]
doc = json.loads(raw[20:20 + n])
binary = raw[28 + n:]
source = json.loads((ROOT / 'helicopter-options.gltf.json').read_text())
meta = json.loads((ROOT / 'seahawk-render-a1.json').read_text())
checks = {
    'cleanGlbHeaderAndLength': struct.unpack_from('<4sII', raw) == (b'glTF', 2, len(raw)),
    'defaultGlbSceneDeployed': doc['scenes'][doc['scene']]['name'] == 'deployed',
    'sharedGlbBuffersAndMaterialsExact': all(doc[k] == source[k] for k in ['meshes', 'materials', 'accessors', 'bufferViews', 'buffers']) and binary[:source['buffers'][0]['byteLength']] == (ROOT / 'helicopter-options.bin').read_bytes(),
}
def walk(roots):
    seen = set()
    def visit(i):
        if i in seen or not 0 <= i < len(doc['nodes']):
            raise ValueError('Repeated parent or invalid node within scene')
        seen.add(i)
        for child in doc['nodes'][i].get('children', []):
            visit(child)
    for i in roots:
        visit(i)
    return seen
for scene in doc['scenes']:
    walk(scene['nodes'])
    if scene['name'] in meta['poses']:
        checks[scene['name'] + '.sceneMatchesPose'] = [doc['nodes'][i]['extras']['sourceNode'] for i in scene['nodes']] == meta['poses'][scene['name']]
checks['allScenesSingleParentAcyclic'] = True
errors = []; rows = []
with sync_playwright() as pw:
    browser = launch(pw)
    for label, viewport, touch in [('desktop', {'width': 1280, 'height': 800}, False), ('mobile', {'width': 390, 'height': 844}, True)]:
        page = browser.new_page(viewport=viewport, has_touch=touch, is_mobile=touch)
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.route('https://heli.test/**', lambda route: route.fulfill(body=(ROOT / 'AEGIS_HELICOPTER_MODEL_INSPECTOR_v01.html').read_bytes(), content_type='text/html'))
        page.goto('https://heli.test/')
        page.wait_for_function('window.__HELI_VIEW__?.ready || window.__HELI_ERROR__', timeout=60000)
        checks[label + '.defaultDeployed'] = page.evaluate("__HELI_VIEW__.mode === 'deployed' && !window.__HELI_ERROR__")
        for pose in ['folded', 'flight', 'deployed']:
            button = page.locator('[data-mode="' + pose + '"]')
            button.tap() if touch else button.click()
            checks[label + '.' + pose + '.button'] = page.evaluate('p => __HELI_VIEW__.mode === p', pose)
        page.locator('[data-camera="side"]').click()
        # One pointer orbit verifies interaction changes the rendered camera.
        canvas = page.locator('canvas'); box = canvas.bounding_box()
        previous = page.evaluate('__HELI_VIEW__.camera.position.toArray()')
        x, y = box['x'] + box['width'] / 2, box['y'] + box['height'] / 2
        page.mouse.move(x, y); page.mouse.down(); page.mouse.move(x + 25, y + 15, steps=3); page.mouse.up()
        current = page.evaluate('__HELI_VIEW__.camera.position.toArray()')
        checks[label + '.orbit'] = current != previous
        row = page.evaluate('''() => { const v=__HELI_VIEW__,gl=v.renderer.getContext(),r=v.renderer.domElement.getBoundingClientRect();return {mode:v.mode,width:r.width,height:r.height,glError:gl.getError(),pageWidth:document.documentElement.scrollWidth,viewport:innerWidth}; }''')
        checks[label + '.canvasVisible'] = row['width'] >= 200 and row['height'] > 200
        checks[label + '.noHorizontalOverflow'] = row['pageWidth'] <= row['viewport']
        checks[label + '.noGlError'] = row['glError'] == 0
        rows.append({'device': label, **row})
        page.close()
    browser.close()
checks['noPageErrors'] = not errors
out = {'pass': all(checks.values()), 'checks': checks, 'rows': rows, 'errors': errors, 'inspectorSha256': hashlib.sha256((ROOT / 'AEGIS_HELICOPTER_MODEL_INSPECTOR_v01.html').read_bytes()).hexdigest(), 'losslessGlbSha256': hashlib.sha256(raw).hexdigest(), 'limits': 'Viewport/touch emulation on Chromium SwiftShader; not a phone GPU or real-device performance test.'}
(ROOT / 'verification-delivery.json').write_text(json.dumps(out, indent=2) + '\n')
print(json.dumps(out)); raise SystemExit(0 if out['pass'] else 1)
