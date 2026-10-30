"""Run from the existing AEGIS Codex checkout. No product files are modified."""
from __future__ import annotations
import argparse, gzip, hashlib, importlib.util, json, math, sys
from pathlib import Path

EXPECTED = {
    "DZT": "edc159fa347d721d61d80228e2512665f22da0adb4f02fdf4e2dbe82789e0c9c",
    "HANDOFF": "e42a2e05b8ff2096dfb334e7b9427cd2cd6da46d567083f06620ffdf35729ed7",
}
MODES = ["NATIVE", "IDEAL_ARH_VALUES_REAL_VALIDITY", "WITHHOLD_ARH_AUTHORITY"]

def clean(value):
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {k: clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    return value

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, default=Path("/tmp/aegis-sm6-240km-rf-causal"))
    parser.add_argument("--native-only", action="store_true")
    args = parser.parse_args()
    repo, out = args.repo.resolve(), args.output.resolve()
    helper_dir = repo / "docs/missile/fuze-zem/A"
    if not (helper_dir / "browser_tools.py").is_file():
        raise SystemExit("--repo must point at the original Aegis_Project checkout.")
    if out.exists() and any(out.iterdir()):
        raise SystemExit("Output is nonempty; choose a new --output. Existing evidence is preserved.")
    baseline = repo / "Aegis_SIM_v48_WIP_FUZE_ZEM_A.html"
    if not baseline.exists():
        baseline = repo / "archive/v48/WIP_FUZE_ZEM_A" / baseline.name
    files = {"DZT": baseline, "HANDOFF": repo / "Aegis_SIM_v48_WIP_LAUNCH_HANDOFF_A.html"}
    for name, file in files.items():
        actual = hashlib.sha256(file.read_bytes()).hexdigest()
        if actual != EXPECTED[name]:
            raise SystemExit(f"{name}: selected HTML differs from pinned investigation input: {actual}")
    cases = json.loads((repo / "docs/missile/termination/A/cases/normal.json").read_text())
    case = cases[152]
    expected_case = {"weapon": "SM6", "seed": 12001, "rangeKm": 240, "altM": 5000, "enabled": False}
    if not all(case.get(k) == v for k, v in expected_case.items()):
        raise SystemExit("Original case 152 changed; inspect it before proceeding.")
    if case.get("targetSpeedMps", 250) != 250:
        raise SystemExit("Original target speed changed.")
    fixture = (repo / "docs/missile/termination/A/live-fixture.js").read_text()
    observer = Path(__file__).with_name("observer.js").read_text()
    sys.path.insert(0, str(helper_dir))
    spec = importlib.util.spec_from_file_location("sm6_causal_browser_tools", helper_dir / "browser_tools.py")
    if spec is None or spec.loader is None:
        raise SystemExit("Cannot load the checkout's browser_tools.py.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    from playwright.sync_api import sync_playwright
    reference_paths = {
        "DZT": repo / "docs/missile/fuze-zem/A/evidence/release-DZT/normals.json",
        "HANDOFF": repo / "docs/missile/launch-handoff/A/final-evidence/release-HANDOFF/normals.json",
    }
    references = {name: json.loads(path.read_text())["results"][152] for name, path in reference_paths.items()}
    modes = MODES[:1] if args.native_only else MODES
    out.mkdir(parents=True, exist_ok=True)
    errors, summary = [], []
    with sync_playwright() as pw:
        browser = module.launch(pw)
        try:
            for variant, file in files.items():
                instrumented = module.instrument(file.read_bytes(), fixture + "\n" + observer)
                page = module.load_fleet(browser, instrumented, own="DDG_119_LATE_FLIGHT_IIA", errors=errors)
                page.set_default_timeout(240000)
                try:
                    for mode in modes:
                        page.evaluate("mode => __SM6_RF_CAUSAL_DIAG__.configure(mode)", mode)
                        result = page.evaluate("c => __TERM_LIVE_TEST__.run(c)", case)
                        rows = page.evaluate("__SM6_RF_CAUSAL_DIAG__.read()")
                        metadata = page.evaluate("__SM6_RF_CAUSAL_DIAG__.metadata()")
                        exact = result == references[variant] if mode == "NATIVE" else None
                        payload = clean({"variant": variant, "condition": case, "mode": mode,
                            "selectedHtmlSha256": EXPECTED[variant],
                            "observerSha256": hashlib.sha256(observer.encode()).hexdigest(),
                            "nativeObserverPreservesEntireOriginalReturn": exact,
                            "metadata": metadata, "result": result, "rows": rows})
                        target = out / f"{variant}-{mode}.json.gz"
                        target.write_bytes(gzip.compress(json.dumps(payload, ensure_ascii=False, allow_nan=False,
                            separators=(",", ":")).encode(), compresslevel=9, mtime=0))
                        entry = {"variant": variant, "mode": mode, "success": result.get("success"),
                            "closestM": result.get("closestM"), "flightTimeS": result.get("flightTimeS"),
                            "finalSpeedMps": result.get("final", {}).get("speedMps"),
                            "nativeObserverExact": exact, "rows": len(rows), "output": target.name}
                        summary.append(entry)
                        print(json.dumps(entry, ensure_ascii=False), flush=True)
                        del rows, payload
                        if mode == "NATIVE" and not exact:
                            raise RuntimeError("Observer changed the original native return; discard causal conclusions.")
                finally:
                    page.close()
        finally:
            browser.close()
    if errors:
        raise RuntimeError("Browser errors: " + repr(errors))
    (out / "summary.json").write_text(json.dumps({"summary": summary, "errors": errors,
        "counterfactualsAreNotProductChanges": True}, indent=2, ensure_ascii=False))
    print("Saved diagnostic evidence to", out)

if __name__ == "__main__":
    main()

