import unittest

from OptiHPLCHandler.utils import (
    append_truncate_method_name,
    make_method_name_string_compatible_with_empower,
)
from OptiHPLCHandler.utils.validate_gradient_table import validate_gradient_table


class TestUtils(unittest.TestCase):
    def test_make_method_name_string_compatible_with_empower(self):
        method_name = "Test.Method-Name"
        expected_result = "Test_MethodmName"
        assert (
            make_method_name_string_compatible_with_empower(method_name)
            == expected_result
        )

        method_name = "Another.Method-Name"
        expected_result = "Another_MethodmName"
        assert (
            make_method_name_string_compatible_with_empower(method_name)
            == expected_result
        )

        method_name = "One.More.Method-Name"
        expected_result = "One_More_MethodmName"
        assert (
            make_method_name_string_compatible_with_empower(method_name)
            == expected_result
        )

        method_name = "NoSpecialCharacters"
        expected_result = "NoSpecialCharacters"
        assert (
            make_method_name_string_compatible_with_empower(method_name)
            == expected_result
        )

    def test_truncate_method_name(self):
        method_name = "Test_Method_Name"
        assert (
            append_truncate_method_name(method_name, "_copy") == "Test_Method_Name_copy"
        )
        method_name_long = "Test_Method_Name_That_Is_Longer_Than_30_Characters"
        assert (
            append_truncate_method_name(method_name_long, "_copy")
            == "Test_Method_Name_That_Is__copy"
        )
        assert len(append_truncate_method_name(method_name_long, "_copy")) <= 30

    def test_validate_gradient_table(self):
        gradient_table = [
            {"CompositionA": "10.0", "CompositionB": "90.0"},
            {"CompositionA": "90.0", "CompositionB": "10.0"},
            {"CompositionA": "10.0", "CompositionB": "90.0"},
        ]
        assert validate_gradient_table(gradient_table) is True

        gradient_table = [
            {"CompositionA": "10.0", "CompositionB": "90.0"},
            {"CompositionA": "90.0", "CompositionB": "10.0"},
            {"CompositionA": "10.0", "CompositionB": "80.0"},
        ]
        try:
            validate_gradient_table(gradient_table)
        except ValueError as e:
            assert (
                str(e)
                == "The sum of the compositions in the gradient table row is notequal to 100. The sum is 90.0. The row is {'CompositionA': '10.0', 'CompositionB': '80.0'}"  # noqa: E501
            )

        gradient_table = [
            {
                "Time": "Initial",
            },
            {
                "Time": "10.0",
            },
            {
                "Time": "11.1",
            },
        ]
        assert validate_gradient_table(gradient_table) is True

        gradient_table = [
            {
                "Time": "Initial",
            },
            {
                "Time": "10.0",
            },
            {
                "Time": "9.1",
            },
        ]

        try:
            validate_gradient_table(gradient_table)
        except ValueError as e:
            assert (
                str(e)
                == "The time in the gradient table row is less than the previousrow. The row is 9.1 and the previous rowis 10.0."  # noqa: E501
            )
