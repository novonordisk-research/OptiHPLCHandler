from typing import Optional

from OptiHPLCHandler import EmpowerInstrumentMethod
from OptiHPLCHandler.applications.empower_implementation.empower_tools import (
    determine_if_isocratic_method,
    determine_max_compositon_value,
    determine_strong_eluent,
)
from OptiHPLCHandler.utils.validate_method_name import append_truncate_method_name


def generate_altered_strong_eluent_method_pct(
    method: EmpowerInstrumentMethod,
    strong_eluent_delta: float = 1,
    maintain_wash_pct: bool = True,
    suffix: Optional[str] = None,
) -> EmpowerInstrumentMethod:
    """
    Alter the strong eluent composition in a gradient method by a specified percentage.

    Parameters
    ----------
    method : EmpowerInstrumentMethod

    strong_eluent_delta : float, optional
        The percentage change to the strong eluent composition, by default 1

    maintain_wash_step : bool, optional
        If True, the wash step strong eluent composition will not be changed,
        by default True
        This should be set to False if the wash step is also part of the gradient,
        otherwise the slope would be altered
    """

    # Variables
    if suffix is None:
        suffix = "_{:.1f}pct".format(strong_eluent_delta)

    # generate method name
    method.method_name = append_truncate_method_name(method.method_name, suffix)
    # gradient table variable
    gradient_table = method.gradient_table
    gradient_table = [
        {key: str(value) for key, value in row.items()} for row in gradient_table
    ]  # convert all values to strings

    # determine if isocratic method
    if determine_if_isocratic_method(gradient_table):
        raise ValueError("Cannot generate varied gradient method for isocratic method.")
        # could do for BSM but not for a QSM without knowing more about the method

    # determine strong eluent
    strong_eluent, list_weak_eluents = determine_strong_eluent(gradient_table)

    # determine max composition value
    max_value = determine_max_compositon_value(gradient_table, strong_eluent)

    # change the strong eluent composition
    for step in gradient_table:
        step[strong_eluent] = float(step[strong_eluent])

        # if maintain wash step, do not change the strong eluent composition in
        # the wash step
        if maintain_wash_pct:
            if step[strong_eluent] == float(max_value):
                step[strong_eluent] = str(step[strong_eluent])  # make strings
                for weak_eluent in list_weak_eluents:
                    step[weak_eluent] = str(step[weak_eluent])  # make strings
                continue

        # Add strong eluent delta to the strong eluent composition in all rows
        step[strong_eluent] = str(step[strong_eluent] + strong_eluent_delta)

        # correct weak eluent composition
        sum_weak_eluents = sum(
            float(step[weak_eluent]) for weak_eluent in list_weak_eluents
        )
        for weak_eluent in list_weak_eluents:
            step[weak_eluent] = float(step[weak_eluent])
            weak_eluent_delta = (
                strong_eluent_delta * step[weak_eluent] / sum_weak_eluents
            )
            new_value = step[weak_eluent] - weak_eluent_delta

            step[weak_eluent] = str(new_value)

    method.gradient_table = gradient_table

    return method
