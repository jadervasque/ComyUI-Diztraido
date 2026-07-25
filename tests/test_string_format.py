"""Testes do formatador de strings e de suas condicoes booleanas."""

from __future__ import annotations

import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

import services.string_format as string_format_service
from services.string_format import StringFormatError, format_string


def _load_string_format_node_module():
    root = Path(__file__).resolve().parents[1]
    package_name = "_diztraido_string_format_test"
    module_name = f"{package_name}.nodes.string_format"

    root_package = types.ModuleType(package_name)
    root_package.__path__ = [str(root)]
    nodes_package = types.ModuleType(f"{package_name}.nodes")
    nodes_package.__path__ = [str(root / "nodes")]
    services_package = types.ModuleType(f"{package_name}.services")
    services_package.__path__ = [str(root / "services")]
    modules = {
        package_name: root_package,
        f"{package_name}.nodes": nodes_package,
        f"{package_name}.services": services_package,
        f"{package_name}.services.string_format": string_format_service,
    }

    spec = importlib.util.spec_from_file_location(module_name, root / "nodes" / "string_format.py")
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, modules):
        spec.loader.exec_module(module)
    return module


class StringFormatTests(unittest.TestCase):
    def test_formats_positional_values_preserving_runtime_types(self):
        result = format_string(
            "File_{1}_{2}_{3}_{4}",
            ["test", 12, 3.5, True],
        )
        self.assertEqual(result, "File_test_12_3.5_true")

    def test_selects_ternary_branch_from_single_input(self):
        template = '@{{1}?"Texto A":"Texto B"}'
        self.assertEqual(format_string(template, [True]), "Texto A")
        self.assertEqual(format_string(template, [False]), "Texto B")

    def test_supports_and_or_aliases_with_standard_precedence(self):
        template = '@{{1}|{2}&&{3}?"yes":"no"}'
        self.assertEqual(format_string(template, [False, True, True]), "yes")
        self.assertEqual(format_string(template, [False, True, False]), "no")

        and_template = '@{{1}&{2}?"both":"not both"}'
        self.assertEqual(format_string(and_template, [True, True]), "both")

    def test_supports_negation_parentheses_and_string_booleans(self):
        template = '@{!({1}||{2})?"disabled":"enabled"}'
        self.assertEqual(format_string(template, ["false", 0]), "disabled")
        self.assertEqual(format_string(template, ["true", False]), "enabled")

    def test_formats_placeholders_inside_selected_branch(self):
        template = '@{{1}?"Enabled_{2}":"Disabled_{3}"}'
        self.assertEqual(format_string(template, [True, 7, 9]), "Enabled_7")
        self.assertEqual(format_string(template, [False, 7, 9]), "Disabled_9")

    def test_compares_input_values_for_equality(self):
        template = '@{{1}=={2}?"Sim":"Não"}'
        self.assertEqual(format_string(template, ["A", "A"]), "Sim")
        self.assertEqual(format_string(template, ["A", "B"]), "Não")

    def test_supports_relational_comparisons_and_logical_composition(self):
        cases = [
            ("!=", ["A", "B"], "yes"),
            ("<", [1, 2], "yes"),
            ("<=", [2, 2], "yes"),
            (">", [3.5, 2.0], "yes"),
            (">=", [3, 3], "yes"),
        ]
        for operator, values, expected in cases:
            with self.subTest(operator=operator):
                template = f'@{{{{1}}{operator}{{2}}?"yes":"no"}}'
                self.assertEqual(format_string(template, values), expected)

        combined = '@{{1}=={2}&&{3}>{4}?"match":"no match"}'
        self.assertEqual(format_string(combined, ["A", "A", 5, 2]), "match")
        self.assertEqual(format_string(combined, ["A", "B", 5, 2]), "no match")

    def test_supports_csharp_style_literal_braces(self):
        self.assertEqual(format_string("{{name}}={1}", ["value"]), "{name}=value")

    def test_removes_lines_starting_with_comment_marker(self):
        template = "File_{1}\n# ignored {99}\n  # also ignored\nEnd_{2}"
        self.assertEqual(format_string(template, ["A", "B"]), "File_A\nEnd_B")

    def test_preserves_hash_outside_start_of_line(self):
        template = "Color #1\nValue_{1} # suffix"
        self.assertEqual(format_string(template, [7]), "Color #1\nValue_7 # suffix")

    def test_supports_template_containing_only_comments(self):
        self.assertEqual(format_string("# first\n\t# second", []), "")

    def test_rejects_missing_input_and_invalid_condition(self):
        with self.assertRaisesRegex(StringFormatError, r"Input \{2\}"):
            format_string("{2}", ["only one"])
        with self.assertRaisesRegex(StringFormatError, "Token invalido"):
            format_string('@{{1} + {2}?"yes":"no"}', [True, True])

    def test_rejects_unclosed_ternary(self):
        with self.assertRaisesRegex(StringFormatError, "sem chave de fechamento"):
            format_string('@{{1}?"yes":"no"', [True])

    def test_rejects_relational_comparison_between_incompatible_types(self):
        with self.assertRaisesRegex(StringFormatError, "Valores incompativeis"):
            format_string('@{{1}>{2}?"yes":"no"}', [1, "text"])


class StringFormatNodeTests(unittest.TestCase):
    def test_declares_wildcard_inputs_and_string_output(self):
        module = _load_string_format_node_module()
        schema = module.DiztraidoStringFormat.INPUT_TYPES()

        self.assertEqual(module.DiztraidoStringFormat.RETURN_TYPES, ("STRING",))
        self.assertEqual(len(schema["optional"]), module.MAX_INPUTS)
        self.assertEqual(str(schema["optional"]["input_1"][0]), "*")
        self.assertFalse(schema["optional"]["input_1"][0] != "BOOLEAN")

    def test_builds_string_using_only_inputs_inside_count(self):
        module = _load_string_format_node_module()
        result = module.DiztraidoStringFormat().build_string(
            "{1}_{2}",
            input_count=2,
            input_1="file",
            input_2=10,
            input_3="ignored",
        )
        self.assertEqual(result, ("file_10",))


if __name__ == "__main__":
    unittest.main()