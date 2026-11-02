"""Add the unchanged test-only S1 observer to the ASM_SEEKER_A product."""
from pathlib import Path
import base64, gzip, hashlib, json, re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = ROOT / "Aegis_SIM_v48_WIP_ASM_SEEKER_A.html"
OUT = ROOT / "Aegis_SIM_v48_WIP_ASM_SEEKER_A_TEST.html"


def sha(value):
    return hashlib.sha256(value).hexdigest()


def unpack(raw):
    match = re.search(rb'data-c55-index="13">([^<]+)', raw)
    assert match
    return gzip.decompress(base64.b64decode(match[1])).decode(), match


def pack(raw, source, match):
    compressed = gzip.compress(source.encode(), 9, mtime=0)
    encoded = base64.b64encode(compressed)
    out = raw[:match.start(1)] + encoded + raw[match.end(1):]
    meta = re.search(rb'const records=(\[.*?\]);', out, re.S)
    assert meta
    rows = json.loads(meta[1])
    rows[13].update(rawBytes=len(source.encode()), gzipBytes=len(compressed), sha256=sha(source.encode()))
    if "encodedBytes" in rows[13]:
        rows[13]["encodedBytes"] = len(encoded)
    return out[:meta.start(1)] + json.dumps(rows, separators=(",", ":")).encode() + out[meta.end(1):]


def main():
    receipt = json.loads((HERE / "PRODUCT_BUILD.json").read_text())
    raw = BASE.read_bytes()
    assert sha(raw) == receipt["outputSha256"]
    source, match = unpack(raw)
    assert sha(source.encode()) == receipt["outputMainSha256"]
    observer = (HERE / "diagnostic.js").read_text()
    anchor = "  window.__NAVAL_SIM_DIAG__ = {"
    assert source.count(anchor) == 1
    candidate = source.replace(anchor, observer + "\n" + anchor, 1)
    assert candidate.replace(observer + "\n", "", 1) == source
    output = pack(raw, candidate, match)
    check, _ = unpack(output)
    assert check == candidate
    OUT.write_bytes(output)
    result = {
        "schema": "AEGIS_ASM_SEEKER_A_PRODUCT_DIAGNOSTIC_BUILD_1",
        "base": BASE.name,
        "baseSha256": sha(raw),
        "baseMainSha256": sha(source.encode()),
        "output": OUT.name,
        "outputSha256": sha(output),
        "outputMainSha256": sha(candidate.encode()),
        "observerSha256": sha(observer.encode()),
        "inverseByteExact": True,
        "testOnlyInstrumentation": True,
    }
    (HERE / "PRODUCT_DIAGNOSTIC_BUILD.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
