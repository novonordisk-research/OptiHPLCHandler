from typing import Optional

from OptiHPLCHandler import EmpowerHandler, EmpowerInstrumentMethod


def post_instrument_methodset_method(
    handler: EmpowerHandler,
    method: EmpowerInstrumentMethod,
    post_method_set_method: bool = True,
):
    """
    Posts an instrument method and optionally posts a method set method.

    Args:
        handler: The handler object used to interact with the instrument.
        method: The instrument method to be posted.
        post_method_set_method: A boolean indicating whether to post a method set
        method.
                                Default is True.

    Returns:
        None
    """
    handler.PostInstrumentMethod(method)
    if post_method_set_method:
        method_set_method = {
            "name": method.method_name,
            "instrumentMethod": method.method_name,
        }
        handler.PostMethodSetMethod(method_set_method)


def determine_if_isocratic_method(gradient_table: list[dict]) -> bool:
    """
    Determines if the method is isocratic based on the gradient table.

    Args:
        gradient_table (list[dict]): The gradient table to determine if the method is
        isocratic.

    Returns:
        bool: True if the method is isocratic, False otherwise.
    """
    composition_table = []
    for row in gradient_table:
        composition_table.append(
            {
                key: float(value)
                for key, value in row.items()
                if key.startswith("Composition")
            }
        )

    composition_set = [dict(t) for t in {tuple(d.items()) for d in composition_table}]

    if len(composition_set) != 1:
        return False
    return True


def determine_max_compositon_value(
    gradient_table: list[dict], composition: str
) -> float:
    """
    Determines the maximum value in the gradient table.

    Args:
        gradient_table (list[dict]): The gradient table to determine the maximum value.
        composition (str): The name of the composition entry to determine the maximum
        value.

    Returns:
        float: The maximum value in the gradient table.
    """

    # Determine the index of the composition with the maximum value
    return max([float(step[composition]) for step in gradient_table])


def determine_last_high_flow_time(gradient_table: list[dict]) -> float:
    """
    Determine the time at which the last high flow rate occurs in a gradient table.

    Parameters
    ----------
    gradient_table : list[dict]

    Returns
    -------
    float
    """
    # return max flow rate accross list of dict gradient
    max_flow_rate = max([step["Flow"] for step in gradient_table])
    last_high_flow_time = 0
    for step in gradient_table:
        if step["Flow"] == max_flow_rate:
            last_high_flow_time = step["Time"]
    return last_high_flow_time


def determine_strong_eluent(gradient_table: list[dict]) -> Optional[str]:
    """
    Determine the strong eluent in the gradient table. Assuming there is only one
    strong eluent. Deprecated in favor of classify_eluents.
    """
    classified_eluents_dict = classify_eluents(gradient_table)
    list_strong_eluent = classified_eluents_dict["strong_eluents"]
    list_weak_eluents = classified_eluents_dict["weak_eluents"]
    list_constant = classified_eluents_dict["constant_composition_eluents"]
    return list_strong_eluent[0], [*list_weak_eluents, *list_constant]


def determine_decreasing_weak_eluents(gradient_table: list[dict]) -> list[str]:
    """
    Determine the weak eluents in the gradient table. Deprecated in favor of
    classify_eluents.
    """
    classified_eluents_dict = classify_eluents(gradient_table)
    list_weak_eluents = classified_eluents_dict["weak_eluents"]

    return list_weak_eluents


def classify_eluents(
    gradient_table: list[dict],
) -> dict[str, list[str]]:
    """
    Classify the eluents in the gradient table as strong, weak, or constant composition.
    Strong eluents are the eluting eluents and thus have increasing composition values
    over the gradient table.
    Weak eluents have decreasing composition values over the gradient table.
    Constant composition eluents have the same composition value over the gradient
    table.
    """

    # Get the compositions
    compositions = [key for key in gradient_table[0].keys() if "Composition" in key]

    # Determine the eluents
    list_weak_eluents = []
    list_strong_eluents = []
    list_constant_composition_eluents = []

    for composition in compositions:
        # Get eluents max value in the gradient table
        max_value = max([float(step[composition]) for step in gradient_table])
        # Determine if increasing and thus strong
        if float(gradient_table[0][composition]) < float(max_value):
            list_strong_eluents.append(composition)

        else:
            # Determine if constant composition
            if all([float(step[composition]) == max_value for step in gradient_table]):
                list_constant_composition_eluents.append(composition)
            else:
                # Is decreasing and thus weak
                list_weak_eluents.append(composition)

    return {
        "strong_eluents": list_strong_eluents,
        "weak_eluents": list_weak_eluents,
        "constant_composition_eluents": list_constant_composition_eluents,
    }
