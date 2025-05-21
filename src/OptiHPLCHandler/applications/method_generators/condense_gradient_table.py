from typing import Optional

from OptiHPLCHandler import EmpowerInstrumentMethod
from OptiHPLCHandler.utils.validate_method_name import append_truncate_method_name


def generate_condense_gradient_table(
    method: EmpowerInstrumentMethod,
    new_method_time: int = 10,
    suffix: Optional[str] = None,
) -> EmpowerInstrumentMethod:
    """
    Condenses the gradient table of a method into a specified number of minutes
    """

    # Variables
    if suffix is None:
        suffix = f"_cond_{new_method_time}m"

    # Generate method name
    method_name = append_truncate_method_name(method.method_name, suffix)
    method.method_name = method_name

    # Gradient variable
    gradient_table = method.gradient_table
    gradient_table = [
        {key: str(value) for key, value in row.items()} for row in gradient_table
    ]  # convert all values to strings

    # if method is isocratic, add new_method_time to the list
    if len(gradient_table) == 1:
        # make new row in gradient with new_method_time so run time can be determined
        row = gradient_table[0].copy()
        row["Time"] = str(new_method_time)
        row["Curve"] = 6  # Curve numebr doesn't matter in this context as only 2 points
        gradient_table.append(row)

    # get list of times in gradient table
    times = [float(x["Time"]) if x["Time"] != "Initial" else 0 for x in gradient_table]

    final_time = times[-1]
    scale_factor = new_method_time / final_time
    times = [x * scale_factor for x in times]

    # replace 0 with 'Initial'
    times[0] = "Initial"

    # map the times to the gradient table
    for i in range(len(gradient_table)):
        gradient_table[i]["Time"] = str(times[i])

    method.gradient_table = gradient_table

    return method
