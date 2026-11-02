"""Build ASM_SEEKER_A from the pinned TRACK_C product with one association fix."""
from pathlib import Path
import base64, difflib, gzip, hashlib, json, re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = ROOT / "Aegis_SIM_v48_WIP_TRACK_C.html"
OUT = ROOT / "Aegis_SIM_v48_WIP_ASM_SEEKER_A.html"
BASE_SHA = "3f2af4c1e18ef30ce4b8dfe4cc2b28f2b91cf96c62306e8f9c55df4a8c508c81"
BASE_MAIN_SHA = "b036ce98279685c884896b918f9fc05f26b2980811c05e3eed39b25016d5827f"


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


OLD = """s.lastValidatedCandidateCount++;const rangeErr=Math.abs(m.rangeM-cueRange),azErr=Math.abs(angNorm(m.azRad-cueAz)),elErr=Math.abs(angNorm(m.elRad-cueEl)),score=5*Math.log1p(Math.max(0,m.snr))+18*(evidence-.5)-4*clamp(rangeErr/Math.max(1200,cueRange*.12),0,4)-5*clamp(azErr/deg(5),0,4)-3*clamp(elErr/deg(4),0,4);scored.push({m,score,stats:null,rangeErr,azErr,elErr,dopErr:0});"""

NEW = """s.lastValidatedCandidateCount++;const rangeErr=Math.abs(m.rangeM-cueRange),azErr=Math.abs(angNorm(m.azRad-cueAz)),elErr=Math.abs(angNorm(m.elRad-cueEl)),cueRangeScaleM=Math.max(1200,cueRange*.12),cueAzScaleRad=deg(5),cueElScaleRad=deg(4);
        // ASM_SEEKER_A: before an EKF exists, the launch cue is an acquisition
        // basket, not merely a soft score. Reuse the existing residual scales;
        // no RF/Pd/noise/beam/gimbal or guidance coefficient changes.
        if(rangeErr>cueRangeScaleM||azErr>cueAzScaleRad||elErr>cueElScaleRad)continue;
        const score=5*Math.log1p(Math.max(0,m.snr))+18*(evidence-.5)-4*clamp(rangeErr/cueRangeScaleM,0,4)-5*clamp(azErr/cueAzScaleRad,0,4)-3*clamp(elErr/cueElScaleRad,0,4);scored.push({m,score,stats:null,rangeErr,azErr,elErr,dopErr:0});"""


def main():
    raw = BASE.read_bytes()
    assert sha(raw) == BASE_SHA
    source, match = unpack(raw)
    assert sha(source.encode()) == BASE_MAIN_SHA
    assert source.count(OLD) == 1
    candidate = source.replace(OLD, NEW, 1)
    assert candidate.count(NEW) == 1 and candidate.replace(NEW, OLD, 1) == source
    output = pack(raw, candidate, match)
    check, _ = unpack(output)
    assert check == candidate
    OUT.write_bytes(output)
    diff = "".join(difflib.unified_diff(
        source.splitlines(True), candidate.splitlines(True),
        fromfile="Aegis_SIM_v48_WIP_TRACK_C/main.js",
        tofile="Aegis_SIM_v48_WIP_ASM_SEEKER_A/main.js",
    ))
    (HERE / "changes.diff").write_text(diff)
    receipt = {
        "schema": "AEGIS_ASM_SEEKER_A_PRODUCT_BUILD_1",
        "base": BASE.name,
        "baseSha256": sha(raw),
        "baseMainSha256": sha(source.encode()),
        "output": OUT.name,
        "outputSha256": sha(output),
        "outputMainSha256": sha(candidate.encode()),
        "changedOccurrences": 1,
        "changedFunction": "asmSeekerAssociateMeasurements",
        "behaviorChange": "Initial no-EKF acquisition rejects evidence outside the pre-existing launch-cue residual scales.",
        "unchanged": ["RF/Pd", "noise", "RCS", "beam", "gimbal", "guidance", "propulsion", "damage"],
    }
    (HERE / "PRODUCT_BUILD.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
