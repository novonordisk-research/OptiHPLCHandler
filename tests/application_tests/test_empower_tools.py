import unittest
from applications import (
    make_method_name_string_compatible_with_empower,
    truncate_method_name,
    determine_if_isocratic_method,
    determine_index_of_max_compositon_value,
    determine_strong_eluent,
    validate_gradient_table,
    determine_last_high_flow_time,
)


class TestMakeMethodNameStringCompatibleWithEmpower(unittest.TestCase):

    def test_make_method_name_string_compatible_with_empower():
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

    def test_truncate_method_name():
        method_name = "Test_Method_Name"
        assert truncate_method_name(method_name, "_copy") == "Test_Method_Name_copy"
        method_name_long = "Test_Method_Name_That_Is_Longer_Than_30_Characters"
        assert (
            truncate_method_name(method_name_long, "_copy")
            == "Test_Method_Name_That_Is__copy"
        )
        assert len(truncate_method_name(method_name_long, "_copy")) <= 30

    def test_determine_if_isocratic_method():
        # Create a sample gradient table
        gradient_table = [
            {
                "Time": "Initial",
                "Flow": "0.3",
                "CompositionA": "90",
                "CompositionB": "90",
                "Curve": "Initial",
            },
            {
                "Time": "10.0",
                "Flow": "0.3",
                "CompositionA": "90",
                "CompositionB": "90",
                "Curve": "6",
            },
            {
                "Time": "10.1",
                "Flow": "0.3",
                "CompositionA": "90",
                "CompositionB": "90",
                "Curve": "6",
            },
        ]
        # Assert the method is isocratic
        assert determine_if_isocratic_method(gradient_table) == True

        # Assess float correctly handled
        gradient_table = [
            {
                "Time": "Initial",
                "Flow": "0.3",
                "CompositionA": "90.0",
                "CompositionB": "90",
                "Curve": "Initial",
            },
            {
                "Time": "10.0",
                "Flow": "0.3",
                "CompositionA": "90",
                "CompositionB": "90",
                "Curve": "6",
            },
            {
                "Time": "10.1",
                "Flow": "0.3",
                "CompositionA": "90",
                "CompositionB": "90",
                "Curve": "6",
            },
        ]
        # Assert the method is isocratic
        assert determine_if_isocratic_method(gradient_table) == True

        # Create a sample gradient table
        gradient_table = [
            {
                "Time": "Initial",
                "Flow": "0.3",
                "CompositionA": "90",
                "CompositionB": "10",
                "Curve": "Initial",
            },
            {
                "Time": "10.0",
                "Flow": "0.3",
                "CompositionA": "80",
                "CompositionB": "20",
                "Curve": "6",
            },
            {
                "Time": "10.1",
                "Flow": "0.3",
                "CompositionA": "70",
                "CompositionB": "30",
                "Curve": "6",
            },
        ]
        # Assert the method is not isocratic
        assert determine_if_isocratic_method(gradient_table) == False


def test_determine_index_of_max_compositon_value():
    gradient_table = [
        {"CompositionA": "10.0", "CompositionB": "20.0"},
        {"CompositionA": "15.0", "CompositionB": "25.0"},
        {"CompositionA": "5.0", "CompositionB": "15.0"},
    ]
    composition = "CompositionB"
    assert determine_index_of_max_compositon_value(gradient_table, composition) == (
        1,
        "25.0",
    )

    composition = "CompositionA"
    assert determine_index_of_max_compositon_value(gradient_table, composition) == (
        1,
        "15.0",
    )

    gradient_table = [
        {"CompositionZ": "10.0", "CompositionB": "20.0"},
    ]
    try:
        determine_index_of_max_compositon_value(gradient_table, "CompositionZ")
    except ValueError as e:
        assert str(e) == "Invalid composition string."


def test_determine_strong_eluent():
    gradient_table = [
        {"CompositionA": "10.0", "CompositionB": "90.0"},
        {"CompositionA": "90.0", "CompositionB": "10.0"},
        {"CompositionA": "10.0", "CompositionB": "90.0"},
    ]
    assert determine_strong_eluent(gradient_table) == ("CompositionA", ["CompositionB"])

    gradient_table = [
        {"CompositionB": "10.0", "CompositionA": "90.0"},
        {"CompositionB": "90.0", "CompositionA": "10.0"},
        {"CompositionB": "10.0", "CompositionA": "90.0"},
    ]
    assert determine_strong_eluent(gradient_table) == ("CompositionB", ["CompositionA"])

    gradient_table = [
        {"CompositionA": "90.0", "CompositionB": "10.0"},
    ]
    try:
        determine_strong_eluent(gradient_table)
    except ValueError as e:
        assert str(e) == "Cannot determine strong eluent for isocratic method."


def test_validate_gradient_table():
    gradient_table = [
        {"CompositionA": "10.0", "CompositionB": "90.0"},
        {"CompositionA": "90.0", "CompositionB": "10.0"},
        {"CompositionA": "10.0", "CompositionB": "90.0"},
    ]
    assert validate_gradient_table(gradient_table) == True

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
            == "The sum of the compositions in the gradient table row is not equal to 100. The sum is 90.0. The row is {'CompositionA': '10.0', 'CompositionB': '80.0'}"
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
    assert validate_gradient_table(gradient_table) == True

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
            == "The time in the gradient table row is less than the previous row. The row is 9.1 and the previous row is 10.0."
        )


def test_determine_last_high_flow_time():
    gradient_table = [
        {"Time": 0, "Flow": 0.5},
        {"Time": 10, "Flow": 1},
        {"Time": 20, "Flow": 1},
        {"Time": 30, "Flow": 0.1},
    ]
    assert determine_last_high_flow_time(gradient_table) == 20
