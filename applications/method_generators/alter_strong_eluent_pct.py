from OptiHPLCHandler import EmpowerInstrumentMethod, EmpowerHandler
from empower_implementation.empower_tools import (
    truncate_method_name,
    post_instrument_methodset_method,
    determine_if_isocratic_method,
    determine_index_of_max_compositon_value,
    determine_strong_eluent,
    validate_gradient_table,
)


def generate_altered_strong_eluent_method_pct(
    method: EmpowerInstrumentMethod,
    handler: EmpowerHandler,
    strong_eluent_delta: float = 1,
    post_method: bool = False,
    maintain_wash_pct: bool = True,
):
    """
    Alter the strong eluent composition in a gradient method by a specified percentage.
    """

    # Variables
    SUFFIX = "_{:.1f}pct".format(strong_eluent_delta)

    # generate method name
    method.method_name = truncate_method_name(method.method_name, SUFFIX)
    # gradient table variable
    gradient_table = method.gradient_table

    # Validate the gradient table rows to ensure the sum of compositions in each row is 100 prior to changes
    validate_gradient_table(gradient_table)

    # determine if isocratic method
    if determine_if_isocratic_method(gradient_table):
        raise ValueError("Cannot generate varied gradient method for isocratic method.")
        # could do for BSM but not for a QSM without knowing more about the method

    # determine strong eluent
    strong_eluent, list_weak_eluents = determine_strong_eluent(gradient_table)

    # determine max composition value
    _, max_value = determine_index_of_max_compositon_value(
        gradient_table, strong_eluent
    )

    # change the strong eluent composition
    for iteration, value in enumerate(gradient_table):
        iter_strong_eluent_delta = strong_eluent_delta

        # For the case where the gradient slopes to the wash strong eluent composition
        if not maintain_wash_pct:
            # if wash composition is 100%, then the strong eluent composition cannot
            # be increased without changing the gradient slope
            if float(value[strong_eluent]) >= 100:
                raise ValueError(
                    "Strong eluent composition is already at 100%. Cannot increase further while retaining gradient slope."
                )

        if maintain_wash_pct:
            if value[strong_eluent] == max_value:
                iter_strong_eluent_delta = 0

        # Add strong eluent delta to the strong eluent composition in all rows
        gradient_table[iteration][strong_eluent] = str(
            float(gradient_table[iteration][strong_eluent]) + iter_strong_eluent_delta
        )

        # determine used weak eluents in row (i.e. not 0)
        list_weak_eluents_with_non_zero_composition = [
            weak_eluent
            for weak_eluent in list_weak_eluents
            if float(gradient_table[iteration][weak_eluent]) != 0.0
        ]

        # correct weak eluent composition
        for weak_eluent in list_weak_eluents:
            if float(gradient_table[iteration][weak_eluent]) != 0.0:
                weak_eluent_delta = iter_strong_eluent_delta / len(
                    list_weak_eluents_with_non_zero_composition
                )
                new_value = (
                    float(gradient_table[iteration][weak_eluent]) - weak_eluent_delta
                )

                if new_value < 0:
                    raise ValueError(
                        "Weak eluent composition cannot be negative, try a smaller strong eluent delta."
                    )

                gradient_table[iteration][weak_eluent] = str(new_value)

        # Validate the gradient table rows to ensure the sum of compositions in each row is 100 after the changes
        validate_gradient_table(gradient_table)

    method.gradient_table = gradient_table

    # Optionally posts the method to Empower
    if post_method:
        post_instrument_methodset_method(handler, method)
    return method
