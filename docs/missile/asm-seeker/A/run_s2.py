"""Run the S2 fixed matrix, no-target controls and other ASM seeker checks."""
from pathlib import Path
import gzip, hashlib, json, sys, time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
EVIDENCE = HERE / "evidence/s2"
EVIDENCE.mkdir(parents=True, exist_ok=True)
sys.path[:0] = ["/dev/shm/aegis-ciws-dmg-a/docs/pip/B",
                "/dev/shm/aegis-ciws-dmg-a/docs/helicopter/H",
                "/dev/shm/aegis-ciws-dmg-a/docs/multiship/G",
                "/dev/shm/aegis-ciws-dmg-a/docs/bunkerhill/K"]
import browser_backend
browser_backend.install()
from browser_i import launch, load
from playwright.sync_api import sync_playwright


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def compact(row):
    metrics = row["metrics"]
    return {
        "setup": row["setup"],
        "finalMode": row["final"]["seekerMode"],
        "locked": row["final"]["seekerLocked"],
        "firstCandidate": metrics["firstCandidate"],
        "firstTrack": metrics["firstTrack"],
        "searchAcquireReturns": metrics["searchAcquireReturns"],
        "candidateSwitches": metrics["candidateSwitches"],
        "bodyYawReversals": metrics["bodyYawReversals"],
        "acquireSteeringCommands": metrics["acquireSteeringCommands"],
        "faults": row["faults"],
    }


def run_group(page, name, options):
    rows = []
    for opts in options:
        row = page.evaluate("o=>__ASM_SEEKER_A_DIAG__.runCommon(o)", opts)
        if row["faults"]:
            raise RuntimeError(row["faults"])
        rows.append(row)
    blob = gzip.compress(json.dumps(rows, ensure_ascii=False, separators=(",", ":")).encode(), 9, mtime=0)
    path = EVIDENCE / f"{name}.json.gz"
    path.write_bytes(blob)
    return [compact(row) for row in rows], {"path": str(path.relative_to(HERE)), "sha256": hashlib.sha256(blob).hexdigest(), "cases": len(rows)}


def main():
    html = ROOT / "Aegis_SIM_v48_WIP_ASM_SEEKER_A_TEST.html"
    receipt = json.loads((HERE / "PRODUCT_DIAGNOSTIC_BUILD.json").read_text())
    assert sha(html) == receipt["outputSha256"]
    errors, matrix, controls, other, raw = [], [], [], [], []
    equivalence, harpoon_core = [], None
    started = time.monotonic()
    with sync_playwright() as pw:
        for distance in (20, 45):
            for separation in (0, 5, 10, 20, 40):
                browser = launch(pw)
                group_errors = []
                page = load(browser, html.read_bytes(), ship="DDG_119_LATE_FLIGHT_IIA", errors=group_errors)
                page.evaluate("__ASM_SEEKER_A_DIAG__.configure({enabled:true})")
                if not equivalence:
                    for label, seed in (("Kh-35U", 519000), ("Kh-32", 519100)):
                        row = page.evaluate("o=>__ASM_SEEKER_A_DIAG__.equivalence(o)", {
                            "seed": seed, "label": label, "separationDeg": 10,
                            "launchRangeKm": 20, "maxTimeS": 4,
                        })
                        assert row["equal"] and not row["onFaults"]
                        equivalence.append(row)
                    harpoon_core = page.evaluate("__ASM_SEEKER_A_DIAG__.harpoonCoreAudit()")
                options = [{"seed": seed, "label": "Kh-35U", "separationDeg": separation,
                            "launchRangeKm": distance, "maxTimeS": 12, "record": True}
                           for seed in range(519000, 519010)]
                rows, entry = run_group(page, f"KH35U_{distance}KM_{separation}DEG", options)
                matrix.extend(rows); raw.append(entry); errors.extend(group_errors)
                browser.close()

        browser = launch(pw)
        page = load(browser, html.read_bytes(), ship="DDG_119_LATE_FLIGHT_IIA", errors=errors)
        page.evaluate("__ASM_SEEKER_A_DIAG__.configure({enabled:true})")
        control_options = []
        for label in ("Kh-35U", "Kh-32"):
            for seed in range(519200, 519210):
                control_options.append({"seed": seed, "label": label, "targetMode": "NO_TARGET",
                                        "separationDeg": 20, "launchRangeKm": 20,
                                        "maxTimeS": 12, "record": True})
        rows, entry = run_group(page, "NO_TARGET_CONTROLS", control_options)
        controls.extend(rows); raw.append(entry)

        for mode in ("SINGLE_OWN_SHIP", "OWN_PLUS_TARGET"):
            options = [{"seed": seed, "label": "Kh-32", "targetMode": mode,
                        "separationDeg": 5, "launchRangeKm": 20,
                        "maxTimeS": 12, "record": True}
                       for seed in range(519100, 519110)]
            rows, entry = run_group(page, f"KH32_{mode}", options)
            other.extend(rows); raw.append(entry)
            harpoon_rows = []
            for seed in range(519100, 519110):
                row = page.evaluate("o=>__ASM_SEEKER_A_DIAG__.runHarpoonPhysical(o)",
                                    {"seed": seed, "targetMode": mode})
                if row["faults"]:
                    raise RuntimeError(row["faults"])
                harpoon_rows.append(row)
            blob = gzip.compress(json.dumps(harpoon_rows, ensure_ascii=False, separators=(",", ":")).encode(), 9, mtime=0)
            path = EVIDENCE / f"HARPOON_{mode}.json.gz"
            path.write_bytes(blob)
            raw.append({"path": str(path.relative_to(HERE)), "sha256": hashlib.sha256(blob).hexdigest(), "cases": len(harpoon_rows)})
            other.extend(harpoon_rows)
        browser.close()

    baseline = json.loads((HERE / "KH35U_REPRODUCTION.json").read_text())["cases"]
    key = lambda row: (row.get("setup", row)["launchRangeKm"], row.get("setup", row)["separationDeg"], row.get("setup", row)["seed"])
    before = {key(row): row for row in baseline}
    changes = []
    for row in matrix:
        prior = before[key(row)]
        changes.append({
            "key": key(row),
            "before": {"locked": prior["locked"], "firstCandidate": prior["firstCandidate"], "firstTrack": prior["firstTrack"]},
            "after": {"locked": row["locked"], "firstCandidate": row["firstCandidate"], "firstTrack": row["firstTrack"]},
        })
    result = {
        "schema": "AEGIS_ASM_SEEKER_A_S2_RESULTS_1",
        "status": "PASS" if not errors and all(row["acquireSteeringCommands"] == 0 for row in matrix)
                  and not any(row["locked"] for row in controls)
                  and harpoon_core["pass"] else "FAIL",
        "inputHtml": html.name,
        "inputSha256": sha(html),
        "productSha256": receipt["baseSha256"],
        "elapsedS": time.monotonic() - started,
        "hookEquivalence": equivalence,
        "harpoonCoreAudit": harpoon_core,
        "pageErrors": errors,
        "matrix": matrix,
        "noTargetControls": controls,
        "otherSeekers": other,
        "beforeAfter": changes,
        "raw": raw,
    }
    save(HERE / "S2_RESULTS.json", result)
    print(json.dumps({
        "status": result["status"], "elapsedS": result["elapsedS"],
        "matrixLocked": sum(row["locked"] for row in matrix),
        "noTargetLocked": sum(row["locked"] for row in controls),
        "kh32Locked": sum(row.get("locked", False) for row in other if row.get("setup", {}).get("label") == "Kh-32"),
        "harpoonLocked": sum(row.get("final", {}).get("locked", False) for row in other if row.get("schema") == "AEGIS_ASM_SEEKER_A_HARPOON_PHYSICAL_1"),
        "pageErrors": errors,
    }, indent=2))


if __name__ == "__main__":
    main()
