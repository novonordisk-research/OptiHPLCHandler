from OptiHPLCHandler import EmpowerInstrumentMethod, EmpowerHandler
from empower_implementation.empower_tools import (
    truncate_method_name,
    post_instrument_methodset_method,
)


def generate_rampup_method(
    method: EmpowerInstrumentMethod,
    rampup_time: int = 10,
    low_flow_rate: float = 0.05,
    flow_curve: int = 6,
    post_method: bool = False,
    handler: EmpowerHandler = None,
) -> EmpowerInstrumentMethod:
    """
    Generate a ramp-up method based on the given full method.

    Args:
        full_method (EmpowerInstrumentMethod): The full method to generate the ramp-up method from.
        rampup_time (int): The ramp-up time in seconds. Default is 10.
        low_flow_rate (float): The low flow rate in mL/min. Default is 0.05.
        flow_curve (int): The flow curve number. Default is 6.

    Returns:
        EmpowerInstrumentMethod: The generated ramp-up method.
    """

    # Variables
    SUFFIX = "_ramp"

    # Rename method
    method.method_name = truncate_method_name(method.method_name, SUFFIX)

    # Generate a new gradient table for the ramp-up method
    gradient_table = method.gradient_table

    gradient_table = [
        gradient_table[0],
        {**gradient_table[0], "Time": rampup_time, "Curve": flow_curve},
    ]
    gradient_table[0]["Flow"] = low_flow_rate

    # Set method name and gradient table in the full method
    method.gradient_table = gradient_table

    # Optionally posts the method to Empower
    if post_method:
        post_instrument_methodset_method(handler, method)
    return method
