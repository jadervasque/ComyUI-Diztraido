"""Tests for optional lines, JSON templates, and conditional blocks."""

from __future__ import annotations

import json
import unittest

from services.string_format import StringFormatError, format_string


class StringFormatOptionalJsonTests(unittest.TestCase):
    def test_accepts_literal_json_braces_without_escaping(self):
        template = '{\n  "style": "{1}"\n}'
        result = format_string(template, ["photorealistic"])
        self.assertEqual(json.loads(result), {"style": "photorealistic"})

    def test_optional_placeholder_removes_line_for_empty_text_or_none(self):
        template = '''{
  "base": "fixed",
  "style": "{1?}",
  "clothes": "{2?}"
}'''
        result = format_string(template, ["", None])
        self.assertEqual(json.loads(result), {"base": "fixed"})

    def test_optional_placeholder_keeps_zero_and_false(self):
        template = '''{
  "count": "{1?}",
  "enabled": "{2?}"
}'''
        result = format_string(template, [0, False])
        self.assertEqual(
            json.loads(result),
            {"count": "0", "enabled": "false"},
        )

    def test_optional_line_removes_trailing_json_comma(self):
        template = '''{
  "base": "fixed",
  "style": "{1?}"
}'''
        result = format_string(template, [""])
        self.assertEqual(json.loads(result), {"base": "fixed"})

    def test_conditional_block_renders_raw_json_content(self):
        template = '''{
  "base": true,
@if {1}
  "style": "{2}",
@else
  "fallback": "default",
@endif
}'''
        enabled = format_string(template, [True, "anime"])
        disabled = format_string(template, [False, "anime"])
        self.assertEqual(json.loads(enabled), {"base": True, "style": "anime"})
        self.assertEqual(
            json.loads(disabled),
            {"base": True, "fallback": "default"},
        )

    def test_supports_nested_conditional_blocks(self):
        template = '''start
@if {1}
outer
@if {2}
inner
@endif
@endif
end'''
        self.assertEqual(format_string(template, [True, True]), "start\nouter\ninner\nend")
        self.assertEqual(format_string(template, [True, False]), "start\nouter\nend")
        self.assertEqual(format_string(template, [False, True]), "start\nend")

    def test_rejects_unmatched_or_unclosed_block_directives(self):
        with self.assertRaisesRegex(StringFormatError, "matching @if"):
            format_string("@else\ntext", [])
        with self.assertRaisesRegex(StringFormatError, "missing @endif"):
            format_string("@if {1}\ntext", [True])

    def test_user_json_scenario_remains_valid_when_both_inputs_are_empty(self):
        template = '''{
  "image_type": "full-body character reference portrait",
  "style": "{1?}",
  "clothes": "{2?}",
  "reference_usage": {
    "identity_source": "Use the reference image only for identity.",
    "wardrobe_source": "Use {2?} as the exclusive source.",
    "wardrobe_instruction": "Dress the character entirely in {2?}.",
    "priority": "When the reference conflicts with {2?}, follow {2}."
  },
  "aspect_ratio": "1:1",
  "preserve": "Apply {1?} and use {2?}."
}'''
        result = format_string(template, ["", ""])
        self.assertEqual(
            json.loads(result),
            {
                "image_type": "full-body character reference portrait",
                "reference_usage": {
                    "identity_source": "Use the reference image only for identity."
                },
                "aspect_ratio": "1:1",
            },
        )


if __name__ == "__main__":
    unittest.main()
