from OptiHPLCHandler import EmpowerHandler
from typing import List


def generate_rampup_method(
    full_method: EmpowerHandler,
    rampup_time: int = 10,
    low_flow_rate: float = 0.05,
    flow_curve: int = 6,
) -> EmpowerHandler:
    """
    Generate a ramp-up method based on the given full method.

    Args:
        full_method (EmpowerHandler): The full method to generate the ramp-up method from.
        rampup_time (int): The ramp-up time in seconds. Default is 10.
        low_flow_rate (float): The low flow rate in mL/min. Default is 0.05.
        flow_curve (int): The flow curve number. Default is 6.

    Returns:
        EmpowerHandler: The generated ramp-up method.
    """
    # Get the gradient table and method name from the full method
    gradient_table: List[dict] = full_method.gradient_table
    method_name: str = full_method.method_name

    # Truncate the method name if it is too long
    if len(method_name) > 25:
        method_name = method_name[:25]

    method_name = f"{method_name}_ramp"

    # Generate a new gradient table for the ramp-up method
    gradient_table = [
        gradient_table[0],
        {**gradient_table[0], "Time": rampup_time, "Curve": flow_curve},
    ]
    gradient_table[0]["Flow"] = low_flow_rate

    # Set method name and gradient table in the full method
    full_method.gradient_table = gradient_table
    full_method.method_name = method_name

    return full_method
