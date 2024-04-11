from OptiHPLCHandler import EmpowerInstrumentMethod, EmpowerHandler
from empower_implementation.empower_tools import (
    truncate_method_name,
    validate_gradient_table,
    post_instrument_methodset_method,
)


def generate_isocratic_start_method(
    method: EmpowerInstrumentMethod,
    handler: EmpowerHandler = None,
    isocratic_duration: float = 2.5,
    post_method: bool = False,
):
    """
    Add an isocratic hold at the start of a gradient method.
    """
    # Variables
    SUFFIX = "_iso_{:.1f}m".format(isocratic_duration)

    # generate method name
    method.method_name = truncate_method_name(method.method_name, SUFFIX)

    # grab the gradient table
    gradient_table = method.gradient_table
    validate_gradient_table(gradient_table)

    # obtain first row
    first_row = gradient_table[0].copy()

    # add to the gradient table a row in position 1 with the same composition as the first row but a time of isocratic_duration
    gradient_table.insert(1, first_row)
    gradient_table[1]["Time"] = "{:.1f}".format(isocratic_duration)

    if "Curve" in gradient_table[1]:
        gradient_table[1]["Curve"] = "6"

    # add isocratic duration to all times in the gradient table after the first row
    for row in gradient_table[2:]:
        row["Time"] = "{:.1f}".format(float(row["Time"]) + isocratic_duration)

    # update the gradient table
    method.gradient_table = gradient_table

    # Optionally posts the method to Empower
    if post_method:
        post_instrument_methodset_method(handler, method)
    return method
