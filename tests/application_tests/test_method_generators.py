from types import SimpleNamespace

from applications.method_generators.ramp_method import generate_ramp_method
from applications.method_generators.alter_temperature import (
    generate_altered_temperature_method,
)
from applications.method_generators.alter_strong_eluent_pct import (
    generate_altered_strong_eluent_method_pct,
)
from applications.method_generators.add_isocratic_segment import (
    add_isocratic_segment_to_method,
)
from applications.method_generators.condense_gradient_table import (
    condense_gradient_table,
)


def test_generate_ramp_method():
    method = SimpleNamespace(
        gradient_table=[
            {
                "Time": "Initial",
                "Flow": 1,
                "CompositionA": 95,
                "CompositionB": 5,
                "Curve": "Initial",
            },
            {"Time": 10, "Flow": 1, "CompositionA": 10, "CompositionB": 90, "Curve": 6},
            {"Time": 20, "Flow": 1, "CompositionA": 95, "CompositionB": 5, "Curve": 6},
            {"Time": 30, "Flow": 1, "CompositionA": 95, "CompositionB": 5, "Curve": 6},
        ],
        column_temperature=30,
        method_name="test",
    )

    method = generate_ramp_method(
        method, low_flow_rate=0.05, flow_curve=6, ramp_type="rampup"
    )
    print(method.gradient_table)
    assert method.gradient_table == [
        {
            "Time": "Initial",
            "Flow": 0.05,
            "CompositionA": 95,
            "CompositionB": 5,
            "Curve": "Initial",
        },
        {"Time": 10, "Flow": 1, "CompositionA": 95, "CompositionB": 5, "Curve": 6},
    ]
    assert method.column_temperature == 30
    assert method.method_name == "test_ramp"

    method = SimpleNamespace(
        gradient_table=[
            {
                "Time": "Initial",
                "Flow": 1,
                "CompositionA": 95,
                "CompositionB": 5,
                "Curve": "Initial",
            },
            {"Time": 10, "Flow": 1, "CompositionA": 10, "CompositionB": 90, "Curve": 6},
            {"Time": 20, "Flow": 1, "CompositionA": 95, "CompositionB": 5, "Curve": 6},
            {"Time": 30, "Flow": 1, "CompositionA": 95, "CompositionB": 5, "Curve": 6},
        ],
        method_name="test",
        column_temperature=30,
    )

    method = generate_ramp_method(
        method,
        low_flow_rate=0.05,
        flow_curve=6,
        ramp_type="rampdown",
        reduce_column_temperature=True,
    )
    print(method.gradient_table)
    assert method.gradient_table == [
        {
            "Time": "Initial",
            "Flow": 1,
            "CompositionA": 95,
            "CompositionB": 5,
            "Curve": "Initial",
        },
        {"Time": 1, "Flow": 0.05, "CompositionA": 95, "CompositionB": 5, "Curve": 6},
    ]
    assert method.column_temperature == 20
    assert method.method_name == "test_low"


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
        method=mock_method_bsm, strong_eluent_delta=1
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
        method=mock_method_bsm, strong_eluent_delta=1
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
            method=mock_method_bsm, strong_eluent_delta=100
        )
    except ValueError as e:
        assert (
            str(e)
            == "The composition in the gradient table row is greater than 100 or less than 0. The composition is -10.0. The row is {'Time': 'Initial', 'Flow': '0.3', 'CompositionA': '-10.0', 'CompositionB': '110.0', 'Curve': 'Initial'}"
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
            method=mock_method_bsm, strong_eluent_delta=1
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
        method=mock_method_qsm, strong_eluent_delta=1
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


def test_add_isocratic_segment_method():
    index_0 = [
        {"CompositionA": 95, "CompositionB": 5, "Flow": 0.3, "Time": 0},
        {"CompositionA": 95, "CompositionB": 5, "Flow": 0.3, "Time": 10},
        {"CompositionA": 50, "CompositionB": 50, "Flow": 0.3, "Time": 20},
        {"CompositionA": 40, "CompositionB": 60, "Flow": 0.03, "Time": 30},
    ]

    index_1 = [
        {"CompositionA": 95, "CompositionB": 5, "Flow": 0.3, "Time": 0},
        {"CompositionA": 50, "CompositionB": 50, "Flow": 0.3, "Time": 10},
        {"CompositionA": 50, "CompositionB": 50, "Flow": 0.3, "Time": 20},
        {"CompositionA": 40, "CompositionB": 60, "Flow": 0.03, "Time": 30},
    ]

    index_2 = [
        {"CompositionA": 95, "CompositionB": 5, "Flow": 0.3, "Time": 0},
        {"CompositionA": 50, "CompositionB": 50, "Flow": 0.3, "Time": 10},
        {"CompositionA": 40, "CompositionB": 60, "Flow": 0.03, "Time": 20},
        {"CompositionA": 40, "CompositionB": 60, "Flow": 0.03, "Time": 30},
    ]

    list_results = [index_0, index_1, index_2, index_2]
    list_indices = [0, 1, 2, -1]

    for index, value in enumerate(list_indices):
        method = SimpleNamespace(
            gradient_table=[
                {"CompositionA": 95, "CompositionB": 5, "Flow": 0.3, "Time": 0},
                {"CompositionA": 50, "CompositionB": 50, "Flow": 0.3, "Time": 10},
                {"CompositionA": 40, "CompositionB": 60, "Flow": 0.03, "Time": 20},
            ],
            method_name="Test Method",
        )

        method_result = add_isocratic_segment_to_method(method, 10, value)
        print(method_result.method_name)

        assert method_result.gradient_table == list_results[index]
        assert (
            method_result.method_name == f"Test Method_iso_10m_{value}"
            if value != -1
            else f"Test Method_iso_10m_{len(method_result.gradient_table)}"
        )


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
