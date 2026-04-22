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
- test_solution.py       # Tier 3 - Unit tests
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

## Design Notes

- Tier 2 uses normalization to match naming differences such as rv_zba vs Zba.
- Tier 2 includes conservative filtering to reduce false positive extension mentions from prose text.
- Tier 3 models shared instructions as weighted edges between extension nodes.

## Assumptions

- instr_dict.json is treated as the source of truth for instruction encodings.
- Extension tags in instr_dict.json follow rv, rv32, or rv64 prefix patterns.
- ISA manual clone uses depth=1 for speed.

## Author

Gopi Kishan
