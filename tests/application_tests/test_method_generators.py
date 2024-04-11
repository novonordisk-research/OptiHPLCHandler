from types import SimpleNamespace

from applications.method_generators.rampup_method import generate_rampup_method
from applications.method_generators.alter_temperature import (
    generate_altered_temperature_method,
)
from applications.method_generators.alter_strong_eluent_pct import (
    generate_altered_strong_eluent_method_pct,
)
from applications.method_generators.add_isocratic_start import (
    generate_isocratic_start_method,
)
from applications.method_generators.condense_gradient_table import (
    condense_gradient_table,
)


def test_generate_rampup_method():
    # Create a sample full method
    full_method = SimpleNamespace(
        method_name="Test_Method",
        gradient_table=[
            {"Time": 0, "Flow": 0.3, "Curve": 1},
            {"Time": 10, "Flow": 0.2, "Curve": 6},
        ],
    )
    # Generate ramp-up method
    rampup_method = generate_rampup_method(full_method)

    # Assert the generated method has the correct properties
    assert rampup_method.method_name == "Test_Method_ramp"
    assert rampup_method.gradient_table == [
        {"Time": 0, "Flow": 0.05, "Curve": 1},
        {"Time": 10, "Flow": 0.3, "Curve": 6},
    ]
    assert rampup_method.gradient_table[1]["Time"] == 10
    assert rampup_method.gradient_table[1]["Curve"] == 6
    assert rampup_method.gradient_table[1]["Flow"] == 0.3
    assert rampup_method.gradient_table[0]["Flow"] == 0.05


def test_generate_altered_temperature_method():
    # Create a mock instrument method
    mock_method = SimpleNamespace(
        method_name="Test_Method_Name", column_temperature="30.0"
    )
    varied_method = generate_altered_temperature_method(mock_method, 2.5)
    assert varied_method.column_temperature == "32.5"
    assert varied_method.method_name == "Test_Method_Name_2_5C"
    assert len(varied_method.method_name) <= 30

    mock_method = SimpleNamespace(
        method_name="Test_Method_Name", column_temperature="30.0"
    )
    varied_method = generate_altered_temperature_method(mock_method, -2.5)
    assert varied_method.column_temperature == "27.5"
    assert varied_method.method_name == "Test_Method_Name_m2_5C"
    assert len(varied_method.method_name) <= 30


def test_generate_varied_gradient_method():

    # BSM method where the strong eluent is CompositionB
    mock_method_bsm = SimpleNamespace(
        method_name="mock_method_bsm_basic",
        gradient_table=[
            {
                "Time": "Initial",
                "Flow": "0.3",
                "CompositionA": "90.0",
                "CompositionB": "10.0",
                "Curve": "Initial",
            },
            {
                "Time": "10.0",
                "Flow": "0.3",
                "CompositionA": "20.0",
                "CompositionB": "80.0",
                "Curve": 6,
            },
            {
                "Time": "10.1",
                "Flow": "0.3",
                "CompositionA": "10.0",
                "CompositionB": "90.0",
                "Curve": 6,
            },
            {
                "Time": "12.1",
                "Flow": "0.3",
                "CompositionA": "10.0",
                "CompositionB": "90.0",
                "Curve": 6,
            },
            {
                "Time": "12.2",
                "Flow": "0.3",
                "CompositionA": "90.0",
                "CompositionB": "10.0",
                "Curve": 6,
            },
            {
                "Time": "20.0",
                "Flow": "0.3",
                "CompositionA": "90.0",
                "CompositionB": "10.0",
                "Curve": 6,
            },
        ],
    )
    varied_method = generate_altered_strong_eluent_method_pct(
        method=mock_method_bsm, handler=None, strong_eluent_delta=1
    )
    assert varied_method.gradient_table == [
        {
            "Time": "Initial",
            "Flow": "0.3",
            "CompositionA": "89.0",
            "CompositionB": "11.0",
            "Curve": "Initial",
        },
        {
            "Time": "10.0",
            "Flow": "0.3",
            "CompositionA": "19.0",
            "CompositionB": "81.0",
            "Curve": 6,
        },
        {
            "Time": "10.1",
            "Flow": "0.3",
            "CompositionA": "10.0",
            "CompositionB": "90.0",
            "Curve": 6,
        },
        {
            "Time": "12.1",
            "Flow": "0.3",
            "CompositionA": "10.0",
            "CompositionB": "90.0",
            "Curve": 6,
        },
        {
            "Time": "12.2",
            "Flow": "0.3",
            "CompositionA": "89.0",
            "CompositionB": "11.0",
            "Curve": 6,
        },
        {
            "Time": "20.0",
            "Flow": "0.3",
            "CompositionA": "89.0",
            "CompositionB": "11.0",
            "Curve": 6,
        },
    ]

    # BSM method where the strong eluent is CompositionA
    mock_method_bsm = SimpleNamespace(
        method_name="mock_method_bsm_comp_a",
        gradient_table=[
            {
                "Time": "Initial",
                "Flow": "0.3",
                "CompositionB": "90.0",
                "CompositionA": "10.0",
                "Curve": "Initial",
            },
            {
                "Time": "10.0",
                "Flow": "0.3",
                "CompositionB": "20.0",
                "CompositionA": "80.0",
                "Curve": 6,
            },
            {
                "Time": "10.1",
                "Flow": "0.3",
                "CompositionB": "10.0",
                "CompositionA": "90.0",
                "Curve": 6,
            },
            {
                "Time": "12.1",
                "Flow": "0.3",
                "CompositionB": "10.0",
                "CompositionA": "90.0",
                "Curve": 6,
            },
            {
                "Time": "12.2",
                "Flow": "0.3",
                "CompositionB": "90.0",
                "CompositionA": "10.0",
                "Curve": 6,
            },
            {
                "Time": "20.0",
                "Flow": "0.3",
                "CompositionB": "90.0",
                "CompositionA": "10.0",
                "Curve": 6,
            },
        ],
    )
    varied_method = generate_altered_strong_eluent_method_pct(
        method=mock_method_bsm, handler=None, strong_eluent_delta=1
    )
    assert varied_method.gradient_table == [
        {
            "Time": "Initial",
            "Flow": "0.3",
            "CompositionB": "89.0",
            "CompositionA": "11.0",
            "Curve": "Initial",
        },
        {
            "Time": "10.0",
            "Flow": "0.3",
            "CompositionB": "19.0",
            "CompositionA": "81.0",
            "Curve": 6,
        },
        {
            "Time": "10.1",
            "Flow": "0.3",
            "CompositionB": "10.0",
            "CompositionA": "90.0",
            "Curve": 6,
        },
        {
            "Time": "12.1",
            "Flow": "0.3",
            "CompositionB": "10.0",
            "CompositionA": "90.0",
            "Curve": 6,
        },
        {
            "Time": "12.2",
            "Flow": "0.3",
            "CompositionB": "89.0",
            "CompositionA": "11.0",
            "Curve": 6,
        },
        {
            "Time": "20.0",
            "Flow": "0.3",
            "CompositionB": "89.0",
            "CompositionA": "11.0",
            "Curve": 6,
        },
    ]

    # BSM method where the strong eluent delta is too high
    mock_method_bsm = SimpleNamespace(
        method_name="mock_method_bsm_high_delta",
        gradient_table=[
            {
                "Time": "Initial",
                "Flow": "0.3",
                "CompositionA": "90.0",
                "CompositionB": "10.0",
                "Curve": "Initial",
            },
            {
                "Time": "10.0",
                "Flow": "0.3",
                "CompositionA": "20.0",
                "CompositionB": "80.0",
                "Curve": 6,
            },
            {
                "Time": "10.1",
                "Flow": "0.3",
                "CompositionA": "10.0",
                "CompositionB": "90.0",
                "Curve": 6,
            },
            {
                "Time": "12.1",
                "Flow": "0.3",
                "CompositionA": "10.0",
                "CompositionB": "90.0",
                "Curve": 6,
            },
            {
                "Time": "12.2",
                "Flow": "0.3",
                "CompositionA": "90.0",
                "CompositionB": "10.0",
                "Curve": 6,
            },
            {
                "Time": "20.0",
                "Flow": "0.3",
                "CompositionA": "90.0",
                "CompositionB": "10.0",
                "Curve": 6,
            },
        ],
    )
    try:
        varied_method = generate_altered_strong_eluent_method_pct(
            method=mock_method_bsm, handler=None, strong_eluent_delta=100
        )
    except ValueError as e:
        assert (
            str(e)
            == "Weak eluent composition cannot be negative, try a smaller strong eluent delta."
        )

    # BSM method where the gradient table is isocratic
    mock_method_bsm = SimpleNamespace(
        method_name="mock_method_bsm_isocratic",
        gradient_table=[
            {
                "Time": "Initial",
                "Flow": "0.3",
                "CompositionA": "90.0",
                "CompositionB": "10.0",
                "Curve": "Initial",
            },
        ],
    )
    try:
        varied_method = generate_altered_strong_eluent_method_pct(
            method=mock_method_bsm, handler=None, strong_eluent_delta=1
        )
    except ValueError as e:
        assert str(e) == "Cannot generate varied gradient method for isocratic method."

    # BSM method where the wash percentage is not maintained
    mock_method_bsm = SimpleNamespace(
        method_name="mock_method_bsm_basic",
        gradient_table=[
            {
                "Time": "Initial",
                "Flow": "0.3",
                "CompositionA": "90.0",
                "CompositionB": "10.0",
                "Curve": "Initial",
            },
            {
                "Time": "10.0",
                "Flow": "0.3",
                "CompositionA": "20.0",
                "CompositionB": "80.0",
                "Curve": 6,
            },
            {
                "Time": "10.1",
                "Flow": "0.3",
                "CompositionA": "10.0",
                "CompositionB": "90.0",
                "Curve": 6,
            },
            {
                "Time": "12.1",
                "Flow": "0.3",
                "CompositionA": "10.0",
                "CompositionB": "90.0",
                "Curve": 6,
            },
            {
                "Time": "12.2",
                "Flow": "0.3",
                "CompositionA": "90.0",
                "CompositionB": "10.0",
                "Curve": 6,
            },
            {
                "Time": "20.0",
                "Flow": "0.3",
                "CompositionA": "90.0",
                "CompositionB": "10.0",
                "Curve": 6,
            },
        ],
    )
    varied_method = generate_altered_strong_eluent_method_pct(
        method=mock_method_bsm,
        handler=None,
        strong_eluent_delta=1,
        maintain_wash_pct=False,
    )
    assert varied_method.gradient_table == [
        {
            "Time": "Initial",
            "Flow": "0.3",
            "CompositionA": "89.0",
            "CompositionB": "11.0",
            "Curve": "Initial",
        },
        {
            "Time": "10.0",
            "Flow": "0.3",
            "CompositionA": "19.0",
            "CompositionB": "81.0",
            "Curve": 6,
        },
        {
            "Time": "10.1",
            "Flow": "0.3",
            "CompositionA": "9.0",
            "CompositionB": "91.0",
            "Curve": 6,
        },
        {
            "Time": "12.1",
            "Flow": "0.3",
            "CompositionA": "9.0",
            "CompositionB": "91.0",
            "Curve": 6,
        },
        {
            "Time": "12.2",
            "Flow": "0.3",
            "CompositionA": "89.0",
            "CompositionB": "11.0",
            "Curve": 6,
        },
        {
            "Time": "20.0",
            "Flow": "0.3",
            "CompositionA": "89.0",
            "CompositionB": "11.0",
            "Curve": 6,
        },
    ]

    # Basic QSM method
    mock_method_qsm = SimpleNamespace(
        method_name="mock_method_qsm",
        gradient_table=[
            {
                "Time": "Initial",
                "Flow": "0.3",
                "CompositionA": "90.0",
                "CompositionB": "10.0",
                "CompositionC": "0.0",
                "CompositionD": "0.0",
                "Curve": "Initial",
            },
            {
                "Time": "10.0",
                "Flow": "0.3",
                "CompositionA": "20.0",
                "CompositionB": "80.0",
                "CompositionC": "0.0",
                "CompositionD": "0.0",
                "Curve": 6,
            },
            {
                "Time": "10.1",
                "Flow": "0.3",
                "CompositionA": "10.0",
                "CompositionB": "90.0",
                "CompositionC": "0.0",
                "CompositionD": "0.0",
                "Curve": 6,
            },
            {
                "Time": "12.1",
                "Flow": "0.3",
                "CompositionA": "10.0",
                "CompositionB": "90.0",
                "CompositionC": "0.0",
                "CompositionD": "0.0",
                "Curve": 6,
            },
            {
                "Time": "12.2",
                "Flow": "0.3",
                "CompositionA": "90.0",
                "CompositionB": "10.0",
                "CompositionC": "0.0",
                "CompositionD": "0.0",
                "Curve": 6,
            },
            {
                "Time": "20.0",
                "Flow": "0.3",
                "CompositionA": "90.0",
                "CompositionB": "10.0",
                "CompositionC": "0.0",
                "CompositionD": "0.0",
                "Curve": 6,
            },
        ],
    )

    varied_method = generate_altered_strong_eluent_method_pct(
        method=mock_method_qsm, handler=None, strong_eluent_delta=1
    )
    assert varied_method.gradient_table == [
        {
            "Time": "Initial",
            "Flow": "0.3",
            "CompositionA": "89.0",
            "CompositionB": "11.0",
            "CompositionC": "0.0",
            "CompositionD": "0.0",
            "Curve": "Initial",
        },
        {
            "Time": "10.0",
            "Flow": "0.3",
            "CompositionA": "19.0",
            "CompositionB": "81.0",
            "CompositionC": "0.0",
            "CompositionD": "0.0",
            "Curve": 6,
        },
        {
            "Time": "10.1",
            "Flow": "0.3",
            "CompositionA": "10.0",
            "CompositionB": "90.0",
            "CompositionC": "0.0",
            "CompositionD": "0.0",
            "Curve": 6,
        },
        {
            "Time": "12.1",
            "Flow": "0.3",
            "CompositionA": "10.0",
            "CompositionB": "90.0",
            "CompositionC": "0.0",
            "CompositionD": "0.0",
            "Curve": 6,
        },
        {
            "Time": "12.2",
            "Flow": "0.3",
            "CompositionA": "89.0",
            "CompositionB": "11.0",
            "CompositionC": "0.0",
            "CompositionD": "0.0",
            "Curve": 6,
        },
        {
            "Time": "20.0",
            "Flow": "0.3",
            "CompositionA": "89.0",
            "CompositionB": "11.0",
            "CompositionC": "0.0",
            "CompositionD": "0.0",
            "Curve": 6,
        },
    ]


def test_generate_isocratic_start_method():
    mock_method = SimpleNamespace(
        gradient_table=[
            {"Time": "Initial", "CompositionA": 0, "CompositionB": 100},
            {"Time": 1, "CompositionA": 0, "CompositionB": 100},
            {"Time": 2, "CompositionA": 100, "CompositionB": 0},
        ],
        method_name="Test Method",
    )

    gradient_table = generate_isocratic_start_method(
        mock_method, handler=None, isocratic_duration=2.5, post_method=False
    ).gradient_table

    time_list = [entry["Time"] for entry in gradient_table]
    assert time_list == ["Initial", "2.5", "3.5", "4.5"]


def test_condense_gradient_table():
    method = SimpleNamespace(
        gradient_table=[
            {
                "Time": "Initial",
                "Flow": "0.300",
                "CompositionA": "50.0",
                "CompositionB": "50.0",
                "Curve": "Initial",
            },
            {
                "Time": "30.00",
                "Flow": "0.300",
                "CompositionA": "10.0",
                "CompositionB": "90.0",
                "Curve": "6",
            },
            {
                "Time": "32.00",
                "Flow": "0.300",
                "CompositionA": "10.0",
                "CompositionB": "90.0",
                "Curve": "6",
            },
            {
                "Time": "32.10",
                "Flow": "0.300",
                "CompositionA": "50.0",
                "CompositionB": "50.0",
                "Curve": "6",
            },
            {
                "Time": "40.00",
                "Flow": "0.300",
                "CompositionA": "50.0",
                "CompositionB": "50.0",
                "Curve": "6",
            },
        ],
        method_name="test_method",
    )
    resulting_gradient_table = [
        {
            "Time": "Initial",
            "Flow": "0.300",
            "CompositionA": "50.0",
            "CompositionB": "50.0",
            "Curve": "Initial",
        },
        {
            "Time": "7.5",
            "Flow": "0.300",
            "CompositionA": "10.0",
            "CompositionB": "90.0",
            "Curve": "6",
        },
        {
            "Time": "8.0",
            "Flow": "0.300",
            "CompositionA": "10.0",
            "CompositionB": "90.0",
            "Curve": "6",
        },
        {
            "Time": "8.03",
            "Flow": "0.300",
            "CompositionA": "50.0",
            "CompositionB": "50.0",
            "Curve": "6",
        },
        {
            "Time": "10.0",
            "Flow": "0.300",
            "CompositionA": "50.0",
            "CompositionB": "50.0",
            "Curve": "6",
        },
    ]

    condense_gradient_table(method, 10).gradient_table
    assert method.gradient_table == resulting_gradient_table
    assert method.method_name == "test_method_cond_10m"
