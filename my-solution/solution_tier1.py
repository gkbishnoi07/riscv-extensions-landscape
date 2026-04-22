"""
RISC-V Mentorship Coding Challenge
Tier 1 - Instruction Set Parsing
"""

import json
import sys
from collections import defaultdict


def load_instr_dict(filepath):
    """Load and return the instruction dictionary JSON file."""
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: File not found -> {filepath}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON -> {e}")
        sys.exit(1)


def group_by_extension(instr_dict):
    """
    Group instructions by their extension tag(s).

    Returns:
        ext_map  -> { extension_tag: [ (mnemonic, data), ... ] }
        multi    -> [ (mnemonic, [ext1, ext2, ...]) ]  instructions in >1 extension
    """
    ext_map = defaultdict(list)
    multi = []

    for mnemonic, data in instr_dict.items():
        extensions = data.get("extension", [])

        if len(extensions) > 1:
            multi.append((mnemonic.upper(), extensions))

        for ext in extensions:
            ext_map[ext].append((mnemonic.upper(), data))

    return ext_map, multi


def print_summary_table(ext_map):
    """Print a formatted summary table of extensions."""

    print("\n" + "=" * 65)
    print(f"{'EXTENSION TAG':<30} {'COUNT':>7}   {'EXAMPLE MNEMONIC'}")
    print("=" * 65)

    for ext in sorted(ext_map.keys()):
        instructions = ext_map[ext]
        count = len(instructions)
        example = instructions[0][0]
        print(f"{ext:<30} {count:>7} instructions | e.g. {example}")

    print("=" * 65)
    print(f"\nTotal extensions found : {len(ext_map)}")
    total_instr = sum(len(v) for v in ext_map.values())
    print(f"Total instruction tags : {total_instr}  (some counted in multiple extensions)")


def print_multi_extension_instructions(multi):
    """Print instructions that belong to more than one extension."""

    print("\n" + "=" * 65)
    print("INSTRUCTIONS BELONGING TO MORE THAN ONE EXTENSION")
    print("=" * 65)

    if not multi:
        print("  None found.")
    else:
        print(f"  {'MNEMONIC':<25} EXTENSIONS")
        print("  " + "-" * 55)
        for mnemonic, exts in sorted(multi):
            exts_str = ", ".join(exts)
            print(f"  {mnemonic:<25} {exts_str}")

    print("=" * 65)
    print(f"\nTotal multi-extension instructions: {len(multi)}")


def main():
    filepath = "../src/instr_dict.json"

    if len(sys.argv) > 1:
        filepath = sys.argv[1]

    print(f"\nLoading instruction dictionary from: {filepath}")
    instr_dict = load_instr_dict(filepath)
    print(f"Total instructions loaded: {len(instr_dict)}")

    ext_map, multi = group_by_extension(instr_dict)
    print_summary_table(ext_map)
    print_multi_extension_instructions(multi)


if __name__ == "__main__":
    main()
