# RISC-V Instruction Set Explorer

LFX Mentorship Coding Challenge - Summer 2026
Mentor: Rafael Sene (RISC-V International)

## Overview

This project implements the three-tier RISC-V Instruction Set Explorer coding challenge. It parses, cross-references, and visualizes the RISC-V ISA extension ecosystem using data from the riscv-extensions-landscape and riscv-isa-manual repositories.

## Project Structure

my-solution/
- solution_tier1.py      # Tier 1 - Instruction set parsing
- solution_tier2.py      # Tier 2 - Cross-reference with ISA manual
- graph_extensions.py    # Tier 3 - Extension sharing graph
- test_solution.py       # Tier 3 - Unit tests (imports from solution modules)
- graph.html             # Generated visual graph (after running Tier 3)
- README.md              # This file

## Requirements

- Python 3.8+
- Git (for auto-cloning the ISA manual in Tier 2)
- A modern browser (for Tier 3 HTML graph)

No external Python packages are required.

## Usage

### Tier 1 - Instruction Set Parsing

Reads ../src/instr_dict.json, groups instructions by extension, and reports a summary table plus multi-extension instructions.

```bash
python3 solution_tier1.py
```

### Tier 2 - Cross-Reference with ISA Manual

Clones/reuses ../riscv-isa-manual, scans AsciiDoc files under src/, and cross-references extension names against instr_dict.json.

```bash
python3 solution_tier2.py
```

### Tier 3 - Extension Sharing Graph

Generates both text graph output and an interactive HTML visualization.

```bash
python3 graph_extensions.py
```

This creates graph.html in the current directory.

### Run Unit Tests

```bash
python3 test_solution.py
```

## Sample Output

### Tier 1 (abbreviated)

```text
Total instructions loaded: 1188

=================================================================
EXTENSION TAG                    COUNT   EXAMPLE MNEMONIC
=================================================================
rv32_c                               1 instructions | e.g. C_JAL
rv32_c_f                             4 instructions | e.g. C_FLW
rv64_a                              11 instructions | e.g. AMOADD_D
rv64_i                              15 instructions | e.g. ADDIW
rv_a                                11 instructions | e.g. AMOADD_W
rv_i                                37 instructions | e.g. ADD
rv_m                                 8 instructions | e.g. DIV
rv_v                               627 instructions | e.g. VAADD_VV
rv_zba                               3 instructions | e.g. SH1ADD
rv_zbb                              17 instructions | e.g. ANDN
rv_zicsr                             6 instructions | e.g. CSRRC
...
=================================================================

Total extensions found : 114
Total instruction tags : 1343  (some counted in multiple extensions)

INSTRUCTIONS BELONGING TO MORE THAN ONE EXTENSION (73 total):
  ANDN                      rv_zbb, rv_zkn, rv_zks, rv_zk, rv_zbkb
  CLMUL                     rv_zbc, rv_zkn, rv_zks, rv_zk, rv_zbkc
  SH1ADD belongs only to rv_zba (single extension)
  ...
```

> **Note:** The coding challenge example shows `rv_zba | 4 instructions` as an illustrative sample. The actual data in instr_dict.json contains 3 instructions for rv_zba (SH1ADD, SH2ADD, SH3ADD), which our output correctly reflects.

### Tier 2

```text
SUMMARY: 53 matched | 32 in JSON only | 101 in manual only

Examples of matched extensions:
  zba                  | JSON: rv64_zba, rv_zba          | Manual: Zba
  zbb                  | JSON: rv64_zbb, rv_zbb          | Manual: Zbb
  zicsr                | JSON: rv_zicsr                   | Manual: Zicsr

Examples of JSON-only (not in manual):
  v                    | original tag(s): rv_v
  zibi                 | original tag(s): rv_zibi
  zicbo                | original tag(s): rv_zicbo

Examples of manual-only (not in JSON):
  zfa                  | found as: Zfa
  zmmul                | found as: Zmmul
  zvfh                 | found as: Zvfh
```

### Tier 3

```text
Total extensions (nodes) : 114
Total sharing pairs (edges) : 57

  EXTENSION A               EXTENSION B               SHARED COUNT  EXAMPLE
  rv64_zk                   rv64_zkn                     16  e.g. AES64DS
  rv_zk                     rv_zkn                       15  e.g. ANDN
  rv_zvkn                   rv_zvkned                    11  e.g. VAESDF_VS
  ...

HTML graph saved to: graph.html
```

### Tests

```text
Ran 36 tests in 0.058s
OK
```

## Design Notes

- **Normalization:** Tier 2 uses normalization to match naming differences such as rv_zba vs Zba. Prefixes (rv_, rv32_, rv64_) are stripped, base ISA forms like RV32I are reduced to the letter (i), and quotes/suffixes are cleaned.
- **False-positive filtering:** Tier 2 includes a curated blocklist of common English words (e.g., "save", "system", "zero") that would otherwise match extension-like regex patterns in the ISA manual prose.
- **Extension sharing graph:** Tier 3 models shared instructions as weighted edges between extension nodes. The interactive HTML graph uses D3.js with force layout, color-coded groups (vector, crypto, Z-extensions, RV64, RV32, base), zoom/drag, and tooltips.
- **Tests import real modules:** Unit tests import directly from solution_tier1.py and solution_tier2.py rather than duplicating logic, ensuring the actual implementation is validated.

## Assumptions

- instr_dict.json is treated as the source of truth for instruction encodings.
- Extension tags in instr_dict.json follow rv, rv32, or rv64 prefix patterns.
- ISA manual clone uses depth=1 for speed.

## Author

Gopi Kishan
