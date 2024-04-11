from OptiHPLCHandler import EmpowerInstrumentMethod, EmpowerHandler
from empower_implementation.empower_tools import (
    truncate_method_name,
    post_instrument_methodset_method,
    determine_if_isocratic_method,
    validate_gradient_table,
)


def condense_gradient_table(
    method: EmpowerInstrumentMethod,
    handler: EmpowerHandler,
    minutes: int = 10,
    post_method: bool = False,
) -> EmpowerInstrumentMethod:
    """
    Condenses the gradient table of a method into a specified number of minutes
    """

    # Variables
    SUFFIX = f"_cond_{minutes}m"

    # Generate method name
    method_name = truncate_method_name(method.method_name, SUFFIX)
    method.method_name = method_name

    # Gradient variable
    gradient_table = method.gradient_table

    # Validate input method
    validate_gradient_table(gradient_table)

    # Determine if the method is isocratic
    if determine_if_isocratic_method(gradient_table):
        raise ValueError(
            "Method is isocratic. Cannot condense."
        )  # column condition is for gradient methods

    # get list of times in gradient table
    times = [float(x["Time"]) if x["Time"] != "Initial" else 0 for x in gradient_table]

    # scale the times to the new final time
    final_time = times[-1]
    scale_factor = minutes / final_time
    times = [round(x * scale_factor, 2) for x in times]

    # replace 0 with 'Initial'
    times[0] = "Initial"

    # map the times to the gradient table
    for i in range(len(gradient_table)):
        gradient_table[i]["Time"] = str(times[i])

    method.gradient_table = gradient_table

    # Optionally posts the method to Empower
    if post_method:
        post_instrument_methodset_method(handler, method)
    return method
