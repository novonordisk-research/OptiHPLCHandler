from typing import List, Optional

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


def determine_if_isocratic_method(gradient_table: List[dict]) -> bool:
    """
    Determines if the method is isocratic based on the gradient table.

    Args:
        gradient_table (List[dict]): The gradient table to determine if the method is isocratic.

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
    gradient_table: List[dict], composition: str
) -> float:
    """
    Determines the maximum value in the gradient table.

    Args:
        gradient_table (List[dict]): The gradient table to determine the maximum value.
        composition (str): The name of the composition entry to determine the maximum value.

    Returns:
        float: The maximum value in the gradient table.
    """

    # Determine the index of the composition with the maximum value
    return max([float(step[composition]) for step in gradient_table])


def determine_last_high_flow_time(gradient_table: List[dict]) -> float:
    """
    Determine the time at which the last high flow rate occurs in a gradient table.

    Parameters
    ----------
    gradient_table : List[dict]

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


def determine_strong_eluent(gradient_table: List[dict]) -> Optional[str]:
    """
    Determines the strong eluent from a given gradient table.

    Args:
        gradient_table (List[dict]): A list of dictionaries representing the gradient table.

    Returns:
        Tuple[str, List[str]]: A tuple containing the strong eluent and a list of weak eluents.
    """
    # Get the compositions
    compositions = [key for key in gradient_table[0].keys() if "Composition" in key]

    # Check if isocratic method
    if determine_if_isocratic_method(gradient_table):
        raise ValueError("Cannot determine strong eluent for isocratic method.")

    # find the composition with the maximum value
    list_weak_eluents = []
    for composition in compositions:
        max_value = determine_max_compositon_value(gradient_table, composition)

        # Determine the strong and weak eluents
        if float(gradient_table[0][composition]) < float(max_value):
            strong_eluent = composition
        else:
            list_weak_eluents.append(composition)

    return strong_eluent, list_weak_eluents
