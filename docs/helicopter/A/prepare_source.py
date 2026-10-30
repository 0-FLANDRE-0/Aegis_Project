"""Read the supplied model as data; retain only known GLB chunks. No extractall."""
import argparse, base64, gzip, hashlib, json, os, re, struct, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE_SHA = '69b83b51a9d3d9a50d5a5accba84c113ecd827e7e7e66af72fe1eaa55ade7013'
BASELINE_SHA = '4571ed015469a48a0cc3ab96b4ee4e3d72c05257d2943a88fdd39272292583d5'

def baseline_path():
    supplied = os.environ.get('AEGIS_SIM_BASELINE')
    if supplied:
        return Path(supplied)
    for parent in ROOT.parents:
        candidate = parent / 'Aegis_SIM_v48_WIP_PERF_F.html'
        if candidate.is_file():
            return candidate
    raise FileNotFoundError('Set AEGIS_SIM_BASELINE to the verified PERF_F HTML')

def prepare(source, baseline):
    source = Path(source)
    if zipfile.is_zipfile(source):
        with zipfile.ZipFile(source) as z:
            entries = [i for i in z.infolist() if Path(i.filename).name == 'uss_daniel_inouye_ddg-118.glb' and not i.is_dir()]
            if len(entries) != 1 or entries[0].file_size > 64 * 1024 * 1024:
                raise ValueError('Expected one DDG-118 GLB below 64 MiB')
            raw = z.read(entries[0])
    else:
        if source.stat().st_size > 64 * 1024 * 1024:
            raise ValueError('Source exceeds expected size')
        raw = source.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA:
        raise ValueError('Different source: audit must be repeated before selecting these nodes')
    magic, version, length = struct.unpack_from('<4sII', raw)
    if magic != b'glTF' or version != 2 or length != len(raw):
        raise ValueError('Invalid GLB header')
    chunks = {}; offset = 12
    while offset < length:
        size, kind = struct.unpack_from('<II', raw, offset); offset += 8
        if size % 4 or offset + size > length or kind in chunks:
            raise ValueError('Invalid GLB chunk')
        chunks[kind] = raw[offset:offset + size]; offset += size
    doc = json.loads(chunks[0x4E4F534A]); binary = chunks[0x004E4942]
    game = Path(baseline).read_bytes()
    if hashlib.sha256(game).hexdigest() != BASELINE_SHA:
        raise ValueError('Expected the verified PERF_F baseline')
    found = re.search(rb'<script type="application/octet-stream" data-c55-index="0">(.*?)</script>', game, re.S)
    if not found:
        raise ValueError('Existing Three engine not found')
    three = gzip.decompress(base64.b64decode(found[1]))
    (ROOT / 'source.glb').write_bytes(raw)
    (ROOT / 'source.gltf.json').write_text(json.dumps(doc, indent=2) + '\n')
    (ROOT / 'source.bin').write_bytes(binary[:doc['buffers'][0]['byteLength']])
    (ROOT / 'packed0.js').write_bytes(three)
    print(json.dumps({'sourceBytes': len(raw), 'sourceSha256': SOURCE_SHA, 'existingEngineBytes': len(three), 'baselineSha256': BASELINE_SHA}))

if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('source'); p.add_argument('--baseline', type=Path)
    a = p.parse_args(); prepare(a.source, a.baseline or baseline_path())
