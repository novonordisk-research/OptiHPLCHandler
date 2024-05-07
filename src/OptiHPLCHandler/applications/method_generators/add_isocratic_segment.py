from typing import Optional

from OptiHPLCHandler import EmpowerInstrumentMethod
from OptiHPLCHandler.utils.validate_method_name import append_truncate_method_name


def generate_add_isocratic_segment_to_method(
    method: EmpowerInstrumentMethod,
    isocratic_duration: float,
    index_of_isocratic_segment: int,
    suffix: Optional[str] = None,
):
    """
    Add an isocratic segment to an existing gradient method.

    Parameters
    ----------
    method : EmpowerInstrumentMethod
        The method to add the isocratic segment to.
    isocratic_duration : float
        The duration of the isocratic segment in minutes.
    index_of_isocratic_segment : int
        The index of the segment to add the isocratic segment after.

    Returns
    -------
    EmpowerInstrumentMethod
        The method with the isocratic segment added.
    """
    # grab the gradient table
    gradient_table = method.gradient_table
    gradient_table = [
        {key: str(value) for key, value in row.items()} for row in gradient_table
    ]  # convert all values to strings

    # If last segment, correct to index
    if index_of_isocratic_segment == -1:
        index_of_isocratic_segment = len(gradient_table) - 1

    # Variables
    if suffix is None:
        suffix = f"_iso_{isocratic_duration}m_{index_of_isocratic_segment}"

    # generate method name
    method.method_name = append_truncate_method_name(method.method_name, suffix)

    # obtain the row of the index_of_isocratic_segment
    row_after_isocratic_segment = gradient_table[index_of_isocratic_segment].copy()

    # add to the gradient table a row in position index_of_isocratic_segment +1 with
    # the same composition as the row after the index_of_isocratic_segment but a time
    # of isocratic_duration
    gradient_table.insert(index_of_isocratic_segment + 1, row_after_isocratic_segment)

    if "Curve" in gradient_table[index_of_isocratic_segment + 1]:
        gradient_table[index_of_isocratic_segment + 1]["Curve"] = "6"

    # add isocratic duration to all times in the gradient table after the
    # index_of_isocratic_segment
    for row in gradient_table[index_of_isocratic_segment + 1 :]:
        if row["Time"] == "Initial":
            row["Time"] = "0"
        row["Time"] = str(float(row["Time"]) + float(isocratic_duration))

    # update the gradient table
    method.gradient_table = gradient_table

    return method
