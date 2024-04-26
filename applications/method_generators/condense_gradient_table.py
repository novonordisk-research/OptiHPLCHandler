from OptiHPLCHandler import EmpowerInstrumentMethod
from OptiHPLCHandler.utils.validate_method_name import append_truncate_method_name
from OptiHPLCHandler.utils.validate_gradient_table import validate_gradient_table
from empower_implementation.empower_tools import determine_if_isocratic_method


def condense_gradient_table(
    method: EmpowerInstrumentMethod,
    new_method_time: int = 10,
) -> EmpowerInstrumentMethod:
    """
    Condenses the gradient table of a method into a specified number of minutes
    """

    # Variables
    suffix = f"_cond_{new_method_time}m"

    # Generate method name
    method_name = append_truncate_method_name(method.method_name, suffix)
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
    scale_factor = new_method_time / final_time
    times = [x * scale_factor for x in times]

    # replace 0 with 'Initial'
    times[0] = "Initial"

    # map the times to the gradient table
    for i in range(len(gradient_table)):
        gradient_table[i]["Time"] = str(times[i])

    # Validate output method
    validate_gradient_table(gradient_table)

    method.gradient_table = gradient_table

    return method
