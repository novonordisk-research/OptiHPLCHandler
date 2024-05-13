from typing import Optional

from OptiHPLCHandler import EmpowerInstrumentMethod
from OptiHPLCHandler.utils.validate_method_name import append_truncate_method_name


def generate_ramp_method(
    method: EmpowerInstrumentMethod,
    ramp_time: Optional[float] = None,
    low_flow_rate: float = 0.05,
    flow_curve: int = 6,
    ramp_type: str = "rampup",
    reduce_column_temperature: bool = False,
    suffix: Optional[str] = None,
) -> EmpowerInstrumentMethod:
    """Generate a ramp-up or ramp-down method from an existing method.

    Args:
        method (EmpowerInstrumentMethod): The input method.
        ramp_time (int): The time for the ramp-up or ramp-down.
        low_flow_rate (float): The flow rate for the low flow portion.
        flow_curve (int): The flow curve for the ramp-up or ramp-down.
        ramp_type (str): The type of ramp method to generate. Options are "rampup" or
        "rampdown".

    Returns:
        EmpowerInstrumentMethod: The ramp-up or ramp-down method.

    """

    if ramp_type == "rampup":
        ramp_settings = {
            "suffix": "_ramp",
            "index": 0,
            "ramp_time": 3,
        }
    elif ramp_type == "rampdown":
        ramp_settings = {
            "suffix": "_low",
            "index": 1,
            "ramp_time": 1,
        }
    else:
        raise ValueError(f"Unknown ramp type {ramp_type}")

    if ramp_time is None:
        ramp_time = ramp_settings["ramp_time"]

    if suffix is not None:
        ramp_settings["suffix"] = suffix

    # Validate input
    if not isinstance(low_flow_rate, (int, float)):
        raise TypeError("low_flow_rate must be a number")
    if not isinstance(flow_curve, int):
        raise TypeError("flow_curve must be an integer")
    if not isinstance(ramp_time, (int, float)):
        raise TypeError("ramp_time must be a number")
    if ramp_type not in ["rampup", "rampdown"]:
        raise ValueError(f"Unknown ramp type {ramp_type}")

    # Variables
    suffix = ramp_settings["suffix"]

    # Rename method
    method.method_name = append_truncate_method_name(method.method_name, suffix)

    # Generate a new gradient table for the ramp-up method
    gradient_table = method.gradient_table
    gradient_table = [
        {key: str(value) for key, value in row.items()} for row in gradient_table
    ]  # convert all values to strings

    gradient_table = [
        gradient_table[0],
        {**gradient_table[0], "Time": str(ramp_time), "Curve": str(flow_curve)},
    ]
    gradient_table[ramp_settings["index"]]["Flow"] = str(low_flow_rate)

    # Set method name and gradient table in the full method
    method.gradient_table = gradient_table

    # reduce column temperature
    if reduce_column_temperature:
        method.column_temperature = 20

    return method
