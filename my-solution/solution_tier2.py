"""
RISC-V Mentorship Coding Challenge
Tier 2 - Cross-Reference with the ISA Manual
"""

import json
import os
import re
import sys
import subprocess
from pathlib import Path
from collections import defaultdict

MANUAL_REPO_URL = "https://github.com/riscv/riscv-isa-manual"
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
INSTR_DICT_PATH = REPO_ROOT / "src" / "instr_dict.json"
MANUAL_CLONE_DIR = REPO_ROOT / "riscv-isa-manual"


def load_json_extensions(filepath):
    """Return a set of extension tags found in instr_dict.json."""
    print(f"\n[1] Loading instruction dictionary from: {filepath}")
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: File not found -> {filepath}")
        sys.exit(1)

    raw_tags = set()
    for _, info in data.items():
        for ext in info.get("extension", []):
            raw_tags.add(ext)

    print(f"    Total unique extension tags in JSON : {len(raw_tags)}")
    return raw_tags


def clone_manual(clone_dir, repo_url):
    """Clone the ISA manual repo if not already present."""
    clone_dir = Path(clone_dir)
    print(f"\n[2] Checking ISA manual repo at: {clone_dir}")
    if clone_dir.is_dir():
        print("    Repo already exists, skipping clone.")
        return

    print(f"    Cloning from {repo_url} ...")
    result = subprocess.run(
        ["git", "clone", "--depth=1", repo_url, str(clone_dir)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"ERROR: git clone failed:\n{result.stderr}")
        sys.exit(1)
    print("    Clone complete.")


def scan_manual_extensions(src_dir):
    """Scan all .adoc files under src_dir for extension-like names."""
    print(f"\n[3] Scanning AsciiDoc files in: {src_dir}")

    if not os.path.isdir(src_dir):
        print(f"ERROR: Manual src directory not found -> {src_dir}")
        sys.exit(1)

    patterns = [
        r"\bZ[a-z][a-z0-9]{1,19}\b",
        r"\bS(?:m|s|v)[a-z][a-z0-9]{1,19}\b",
        r"\bRV(?:32|64|128)[IEMAFDZQCVH]\b",
        r"\b[MAFDZQCVH]\s+extension\b",
        r'"[MAFDZQCVH]"\s+extension',
        r'extension\s+"?[MAFDZQCVH]"?\b',
        r"\brv(?:32|64)?_[a-z][a-z0-9_]{1,20}\b",
    ]

    false_positives = {
        "same", "save", "scalar", "scale", "scope", "score", "scratch",
        "search", "second", "section", "secure", "security", "seed",
        "segment", "select", "self", "semantics", "sensitive", "separate",
        "service", "set", "sets", "setting", "setup", "several", "shift",
        "short", "should", "sign", "signal", "signed", "similar", "simple",
        "since", "single", "size", "skip", "slide", "small", "software",
        "some", "source", "special", "spec", "specific", "start", "state",
        "static", "status", "steps", "store", "string", "strong", "subject",
        "subset", "such", "sum", "support", "synonym", "syntax", "system",
        "standard", "stage", "stack", "spike", "scatter", "schedule",
        "scheme", "schmidt", "scott", "see", "send", "serve", "zero",
        "zeros", "zeroes", "swap", "swapping", "zhang", "zabrocki",
        "zandijk", "saarinen", "sarkar", "schwabe", "sewell", "shannon",
        "spinney", "sweeney", "sizhuo", "sail", "shadow", "sample",
        "sampling", "sanitizer", "sigma0", "sigma1", "sum0", "sum1",
        "supervisor", "supplemental", "supplementary", "semihosting",
        "spectre", "synopsis",
    }

    found_raw = set()
    adoc_files = []

    for root, _, files in os.walk(src_dir):
        for fname in files:
            if fname.endswith(".adoc"):
                adoc_files.append(os.path.join(root, fname))

    print(f"    Found {len(adoc_files)} .adoc files to scan")

    for fpath in adoc_files:
        try:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            for pat in patterns:
                for m in re.findall(pat, text):
                    m = m.strip('"').strip()
                    m = re.sub(r"\s+extension$", "", m, flags=re.IGNORECASE).strip()
                    if len(m) < 2:
                        continue
                    if m.lower() in false_positives:
                        continue
                    if " " in m:
                        continue
                    found_raw.add(m)
        except Exception as e:
            print(f"    WARNING: Could not read {fpath}: {e}")

    print(f"    Raw extension mentions found in manual: {len(found_raw)}")
    return found_raw


def normalize(name):
    """Normalize extension name to a common lowercase key."""
    name = name.strip().lower()
    name = re.sub(r"\s+extension$", "", name)
    name = re.sub(r"^extension\s+", "", name)
    name = re.sub(r"^rv(?:32|64|128)?_", "", name)

    base_isa = re.match(r"^rv(?:32|64|128)([a-z]+)$", name)
    if base_isa:
        name = base_isa.group(1)

    name = name.strip('"\'\\`')
    return name.strip()


def build_normalized_map(raw_set):
    """Return dict: normalized_key -> set of original strings."""
    result = defaultdict(set)
    for raw in raw_set:
        key = normalize(raw)
        if key:
            result[key].add(raw)
    return result


def cross_reference(json_tags, manual_tags):
    """Compare normalized extension names from JSON vs manual."""
    json_norm = build_normalized_map(json_tags)
    manual_norm = build_normalized_map(manual_tags)

    json_keys = set(json_norm.keys())
    manual_keys = set(manual_norm.keys())

    matched = json_keys & manual_keys
    json_only = json_keys - manual_keys
    manual_only = manual_keys - json_keys

    return matched, json_only, manual_only, json_norm, manual_norm


def print_report(matched, json_only, manual_only, json_norm, manual_norm):
    """Print final cross-reference report."""
    print("\n" + "=" * 70)
    print("CROSS-REFERENCE REPORT: instr_dict.json  vs  ISA Manual")
    print("=" * 70)

    print(f"\n  {'Matched (in both)':<35} : {len(matched)}")
    print(f"  {'JSON only (not in manual)':<35} : {len(json_only)}")
    print(f"  {'Manual only (not in JSON)':<35} : {len(manual_only)}")
    print(f"  {'TOTAL unique JSON extensions':<35} : {len(matched) + len(json_only)}")

    print("\n" + "-" * 70)
    print("MATCHED EXTENSIONS (present in both sources)")
    print("-" * 70)
    for key in sorted(matched):
        json_originals = ", ".join(sorted(json_norm[key]))
        manual_originals = ", ".join(sorted(manual_norm[key]))
        print(f"  {key:<20} | JSON: {json_originals:<25} | Manual: {manual_originals}")

    print("\n" + "-" * 70)
    print("JSON ONLY (in instr_dict.json but NOT mentioned in ISA manual)")
    print("-" * 70)
    if json_only:
        for key in sorted(json_only):
            originals = ", ".join(sorted(json_norm[key]))
            print(f"  {key:<20} | original tag(s): {originals}")
    else:
        print("  None.")

    print("\n" + "-" * 70)
    print("MANUAL ONLY (in ISA manual but NOT in instr_dict.json)")
    print("-" * 70)
    if manual_only:
        for key in sorted(manual_only):
            originals = ", ".join(sorted(manual_norm[key]))
            print(f"  {key:<20} | found as: {originals}")
    else:
        print("  None.")

    print("\n" + "=" * 70)
    print(
        f"SUMMARY: {len(matched)} matched | "
        f"{len(json_only)} in JSON only | "
        f"{len(manual_only)} in manual only"
    )
    print("=" * 70)


def main():
    instr_path = sys.argv[1] if len(sys.argv) > 1 else str(INSTR_DICT_PATH)
    manual_dir = sys.argv[2] if len(sys.argv) > 2 else str(MANUAL_CLONE_DIR)

    json_tags = load_json_extensions(instr_path)
    clone_manual(manual_dir, MANUAL_REPO_URL)

    manual_src = os.path.join(manual_dir, "src")
    manual_tags = scan_manual_extensions(manual_src)

    matched, json_only, manual_only, json_norm, manual_norm = cross_reference(
        json_tags, manual_tags
    )
    print_report(matched, json_only, manual_only, json_norm, manual_norm)


if __name__ == "__main__":
    main()
