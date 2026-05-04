"""
RISC-V Mentorship Coding Challenge
Tier 3 - Unit Tests

Tests import directly from the solution modules to validate the actual
implementation rather than duplicated logic.
"""

import json
import os
import sys
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent

# Ensure the solution directory is on the import path
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from solution_tier1 import group_by_extension
from solution_tier2 import normalize, build_normalized_map, cross_reference


class TestGroupByExtension(unittest.TestCase):
    def _make_instr(self, ext_list):
        return {
            "encoding": "0000000----------000-----0110011",
            "variable_fields": ["rd", "rs1", "rs2"],
            "extension": ext_list,
            "match": "0x33",
            "mask": "0xfe00707f",
        }

    def test_single_extension_grouping(self):
        data = {
            "add": self._make_instr(["rv_i"]),
            "sub": self._make_instr(["rv_i"]),
            "mul": self._make_instr(["rv_m"]),
        }
        ext_map, _ = group_by_extension(data)
        self.assertEqual(len(ext_map["rv_i"]), 2)
        self.assertEqual(len(ext_map["rv_m"]), 1)

    def test_multi_extension_detection(self):
        data = {
            "andn": self._make_instr(["rv_zbb", "rv_zbkb", "rv_zk"]),
            "add": self._make_instr(["rv_i"]),
        }
        _, multi = group_by_extension(data)
        multi_mnemonics = [m for m, _ in multi]
        self.assertIn("ANDN", multi_mnemonics)
        self.assertNotIn("ADD", multi_mnemonics)

    def test_multi_extension_appears_in_each_group(self):
        data = {"andn": self._make_instr(["rv_zbb", "rv_zbkb"])}
        ext_map, _ = group_by_extension(data)
        self.assertIn("ANDN", [m for m, _ in ext_map["rv_zbb"]])
        self.assertIn("ANDN", [m for m, _ in ext_map["rv_zbkb"]])

    def test_empty_dict(self):
        ext_map, multi = group_by_extension({})
        self.assertEqual(len(ext_map), 0)
        self.assertEqual(len(multi), 0)

    def test_mnemonic_uppercased(self):
        data = {"sh1add": self._make_instr(["rv_zba"])}
        ext_map, _ = group_by_extension(data)
        mnemonics = [m for m, _ in ext_map["rv_zba"]]
        self.assertIn("SH1ADD", mnemonics)

    def test_no_extension_field(self):
        data = {
            "weird": {
                "encoding": "0000000----------000-----0110011",
                "variable_fields": [],
                "match": "0x33",
                "mask": "0xfe00707f",
            }
        }
        ext_map, _ = group_by_extension(data)
        self.assertEqual(len(ext_map), 0)

    def test_summary_count(self):
        data = {
            "add": self._make_instr(["rv_i"]),
            "andn": self._make_instr(["rv_zbb", "rv_zbkb"]),
            "mul": self._make_instr(["rv_m"]),
        }
        ext_map, _ = group_by_extension(data)
        total = sum(len(v) for v in ext_map.values())
        self.assertEqual(total, 4)


class TestNormalize(unittest.TestCase):
    def test_rv_prefix_removed(self):
        self.assertEqual(normalize("rv_zba"), "zba")

    def test_rv64_prefix_removed(self):
        self.assertEqual(normalize("rv64_zba"), "zba")

    def test_rv32_prefix_removed(self):
        self.assertEqual(normalize("rv32_zknd"), "zknd")

    def test_capital_z_extension(self):
        self.assertEqual(normalize("Zba"), "zba")

    def test_capital_s_extension(self):
        self.assertEqual(normalize("Smstateen"), "smstateen")

    def test_base_isa_rv32i(self):
        self.assertEqual(normalize("RV32I"), "i")

    def test_base_isa_rv64a(self):
        self.assertEqual(normalize("RV64A"), "a")

    def test_base_isa_rv128i(self):
        self.assertEqual(normalize("RV128I"), "i")

    def test_extension_suffix_removed(self):
        self.assertEqual(normalize("M extension"), "m")

    def test_already_lowercase(self):
        self.assertEqual(normalize("zicsr"), "zicsr")

    def test_quote_stripped(self):
        self.assertEqual(normalize('"A"'), "a")

    def test_whitespace_stripped(self):
        self.assertEqual(normalize("  Zbb  "), "zbb")

    def test_empty_string(self):
        self.assertEqual(normalize(""), "")


class TestCrossReference(unittest.TestCase):
    def test_exact_match(self):
        json_tags = {"rv_zba", "rv_zbb"}
        manual_tags = {"Zba", "Zbb"}
        matched, _, _, _, _ = cross_reference(json_tags, manual_tags)
        self.assertIn("zba", matched)
        self.assertIn("zbb", matched)

    def test_json_only_detection(self):
        json_tags = {"rv_zba", "rv_zibi"}
        manual_tags = {"Zba"}
        _, json_only, _, _, _ = cross_reference(json_tags, manual_tags)
        self.assertIn("zibi", json_only)

    def test_manual_only_detection(self):
        json_tags = {"rv_zba"}
        manual_tags = {"Zba", "Zdinx", "Zmmul"}
        _, _, manual_only, _, _ = cross_reference(json_tags, manual_tags)
        self.assertIn("zdinx", manual_only)
        self.assertIn("zmmul", manual_only)

    def test_rv64_vs_standard_name(self):
        json_tags = {"rv64_zba"}
        manual_tags = {"Zba"}
        matched, _, _, _, _ = cross_reference(json_tags, manual_tags)
        self.assertIn("zba", matched)

    def test_base_isa_normalization(self):
        json_tags = {"rv_i", "rv64_i"}
        manual_tags = {"RV32I", "RV64I"}
        matched, _, _, _, _ = cross_reference(json_tags, manual_tags)
        self.assertIn("i", matched)

    def test_empty_inputs(self):
        matched, json_only, manual_only, _, _ = cross_reference(set(), set())
        self.assertEqual(len(matched), 0)
        self.assertEqual(len(json_only), 0)
        self.assertEqual(len(manual_only), 0)

    def test_no_overlap(self):
        json_tags = {"rv_zba", "rv_zbb"}
        manual_tags = {"Zdinx", "Zmmul"}
        matched, json_only, manual_only, _, _ = cross_reference(json_tags, manual_tags)
        self.assertEqual(len(matched), 0)
        self.assertEqual(len(json_only), 2)
        self.assertEqual(len(manual_only), 2)

    def test_count_consistency(self):
        json_tags = {"rv_zba", "rv_zbb", "rv_zbc", "rv_zibi"}
        manual_tags = {"Zba", "Zbb", "Zbc", "Zdinx"}
        matched, json_only, _, _, _ = cross_reference(json_tags, manual_tags)
        self.assertEqual(len(matched) + len(json_only), len(json_tags))


class TestRealData(unittest.TestCase):
    INSTR_DICT = REPO_ROOT / "src" / "instr_dict.json"

    def setUp(self):
        if not os.path.exists(self.INSTR_DICT):
            self.skipTest(f"instr_dict.json not found at {self.INSTR_DICT}")
        with open(self.INSTR_DICT) as f:
            self.data = json.load(f)

    def test_total_instructions(self):
        self.assertGreater(len(self.data), 1000)

    def test_known_extension_rv_zba(self):
        ext_map, _ = group_by_extension(self.data)
        mnemonics = {m for m, _ in ext_map.get("rv_zba", [])}
        self.assertIn("SH1ADD", mnemonics)
        self.assertIn("SH2ADD", mnemonics)
        self.assertIn("SH3ADD", mnemonics)
        self.assertEqual(len(mnemonics), 3)

    def test_known_extension_rv_zicsr(self):
        ext_map, _ = group_by_extension(self.data)
        self.assertEqual(len(ext_map.get("rv_zicsr", [])), 6)

    def test_known_extension_rv_m(self):
        ext_map, _ = group_by_extension(self.data)
        self.assertEqual(len(ext_map.get("rv_m", [])), 8)

    def test_andn_is_multi_extension(self):
        _, multi = group_by_extension(self.data)
        multi_dict = {m: exts for m, exts in multi}
        self.assertIn("ANDN", multi_dict)
        self.assertGreater(len(multi_dict["ANDN"]), 1)

    def test_all_instructions_have_encoding(self):
        for mnemonic, info in self.data.items():
            self.assertIn("encoding", info, f"Missing encoding for: {mnemonic}")

    def test_encoding_length(self):
        for mnemonic, info in self.data.items():
            enc = info.get("encoding", "")
            self.assertEqual(len(enc), 32, f"Bad encoding length for {mnemonic}: '{enc}'")

    def test_no_empty_extension_list(self):
        for mnemonic, info in self.data.items():
            exts = info.get("extension", [])
            self.assertGreater(len(exts), 0, f"Empty extension list for: {mnemonic}")


if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestGroupByExtension))
    suite.addTests(loader.loadTestsFromTestCase(TestNormalize))
    suite.addTests(loader.loadTestsFromTestCase(TestCrossReference))
    suite.addTests(loader.loadTestsFromTestCase(TestRealData))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
