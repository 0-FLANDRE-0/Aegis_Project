"""Derive a shared, articulated Harpoon asset from the user's standalone viewer.

No live mesh reads enter the simulator. Uniform source textures are baked into
linear material colours; wings and tail fins are separate authored rigid parts.
"""
import argparse, base64, gzip, hashlib, io, json, re
from pathlib import Path
import numpy as np
from PIL import Image

SOURCE = Path('/tmp/codex-remote-attachments/01a1001f-c12a-71b9-84a1-aa605987d0ab/b4ab3894-f0ec-4dfb-badc-504f8bf5e9cf/1-RGM-84D_Harpoon_Viewer_v1.html')
OUT = Path(__file__).resolve().parent

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,default=SOURCE)
    ap.add_argument('--out',type=Path,default=OUT)
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    raw = args.source.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == 'b8b7ab4707c81e759998c0a1f1a7b33d0c814bf0026ecbec59a7092c7afb9a42'
    html = raw.decode()
    meta = json.loads(re.search(r'<script[^>]*id="meta"[^>]*>(.*?)</script>', html, re.S)[1])
    buf = base64.b64decode(re.search(r'<script[^>]*id="geo"[^>]*>(.*?)</script>', html, re.S)[1])
    materials = []
    linear = lambda v: v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4
    for m in meta['materials']:
        c = np.array(m['color'][:3], dtype=float)
        if m['tex'] is not None:
            png = base64.b64decode(meta['textures'][m['tex']].split(',', 1)[1])
            im = Image.open(io.BytesIO(png)).convert('RGB')
            lo, hi = zip(*im.getextrema())
            assert lo == hi, 'Nonuniform texture requires preservation'
            c *= [linear(v / 255) for v in lo]
        materials.append(dict(color=c.tolist(), roughness=max(.35, m['rough']), metalness=min(.3, m['metal'])))
    binary = bytearray()
    meshes = []
    def append(a):
        while len(binary) % 4: binary.append(0)
        offset = len(binary)
        binary.extend(a.tobytes())
        return [offset, a.size]
    for i, m in enumerate(meta['meshes']):
        read = lambda name, dtype: np.frombuffer(buf, dtype, count=m[name][1], offset=m[name][0]).copy()
        p, n, ix = read('pos', '<f4').reshape(-1, 3), read('nor', '<f4').reshape(-1, 3), read('idx', '<u4').reshape(-1, 3)
        roles = [('BOOSTER' if m['booster'] else 'BODY', ix)]
        if i in [47, 51, 53, 54]:
            is_tail = p[ix, 0].mean(axis=1) < -1
            roles = [('WING', ix[~is_tail]), ('TAIL', ix[is_tail])]
        for role, triangles in roles:
            used, inv = np.unique(triangles, return_inverse=True)
            pos, normal = p[used].copy(), n[used].copy()
            pivot, radial = None, None
            if role in ['WING', 'TAIL']:
                yz = pos[:, 1:]
                radial = yz.mean(axis=0); radial /= np.linalg.norm(radial)
                root = .1715
                if role == 'WING':
                    # Correct opposite tip span from 0.9814 m to the public 0.914 m.
                    r = np.linalg.norm(yz, axis=1)
                    new_r = root + (r - root) * ((.914 / 2 - root) / (.9814168305 / 2 - root))
                    pos[:, 1:] *= (new_r / np.maximum(r, 1e-8))[:, None]
                pivot = [float(pos[:, 0].min()), float(radial[0]*root), float(radial[1]*root)]
                pos -= np.array(pivot)
                radial = [0, float(radial[0]), float(radial[1])]
            assert np.isfinite(pos).all() and np.isfinite(normal).all()
            meshes.append(dict(sourceMesh=i, role=role, material=m['mat'], pivot=pivot, radial=radial,
                               pos=append(pos.astype('<f4')), nor=append(normal.astype('<f4')),
                               idx=append(inv.astype('<u4'))))
    result = dict(schema='HARPOON_RENDER_ASSET_A1', axis='NOSE_PLUS_X_Y_UP_Z_LATERAL', lengthM=4.63,
                  bodyLengthM=3.84, diameterM=.343, wingSpanM=.914, boosterCenterXM=-1.92,
                  meshes=meshes, materials=materials, sourceHtmlSha256=hashlib.sha256(raw).hexdigest(),
                  attribution=dict(author='Civorsky', title='Missiles', license='CC BY 4.0',
                      url='https://sketchfab.com/3d-models/missiles-37899978144a45d0bd03c3538957b145',
                      licenseUrl='https://creativecommons.org/licenses/by/4.0/',
                      modifications='Articulated wings/tails, corrected main-wing span, baked uniform texture colours'))
    (args.out/'model-meta.json').write_text(json.dumps(result, separators=(',', ':')))
    (args.out/'model-geo.gz').write_bytes(gzip.compress(binary, 9, mtime=0))
    print(json.dumps(dict(meshes=len(meshes), triangles=sum(m['idx'][1]//3 for m in meshes), bytes=len(binary), gzipBytes=(args.out/'model-geo.gz').stat().st_size)))

if __name__ == '__main__': main()
