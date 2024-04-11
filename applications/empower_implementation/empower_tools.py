from typing import List, Optional

from OptiHPLCHandler import EmpowerHandler, EmpowerInstrumentMethod


def make_method_name_string_compatible_with_empower(method_name: str) -> str:
    """
    Replaces special characters in empower method names.

    Args:
        method_name (str): The original method name.

    Returns:
        str: The method name with special characters replaced.
    """

    new_method_name = method_name.replace(".", "_")
    new_method_name = new_method_name.replace("-", "m")  # assuming minus
    return new_method_name


def truncate_method_name(method_name: str, suffix: str) -> str:
    """
    Truncates the given method name and appends the provided suffix.
    Also replaces characters that are not allowed in Empower method names.

    Args:
        method_name (str): The original method name.
        suffix (str): The suffix to be appended.

    Returns:
        str: The truncated method name with the suffix.
    """

    # Truncate
    if len(method_name) > 30 - len(suffix):
        new_method_name = method_name[: 30 - len(suffix)] + suffix
    else:
        new_method_name = method_name + suffix

    # Replace special characters
    new_method_name = make_method_name_string_compatible_with_empower(new_method_name)

    return new_method_name


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
    with handler:
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
    # Check if the compostions are the same for all rows (using composition A as reference)
    for row in gradient_table:
        if float(row["CompositionA"]) != float(gradient_table[0]["CompositionA"]):
            return False
    return True


def determine_index_of_max_compositon_value(
    gradient_table: List[dict], composition: str
) -> tuple[int, str]:
    """
    Determines the index of the composition with the maximum value in the gradient table.

    Args:
        gradient_table (List[dict]): A list of dictionaries representing the gradient table.
        composition (str): The composition string to search for.

    Returns:
        int: The index of the composition with the maximum value and the maximum value.

    Raises:
        ValueError: If the composition string is not valid.

    Example:
        gradient_table = [
            {"CompositionA": "10.0", "CompositionB": "20.0"},
            {"CompositionA": "15.0", "CompositionB": "25.0"},
            {"CompositionA": "5.0", "CompositionB": "15.0"}
        ]
        composition = "CompositionB"
        determine_index_of_max_compositon_value(gradient_table, composition)
        # Output: (2, 25)
    """

    # Check composition string is valid
    list_allowed_compositions = (
        "CompositionA",
        "CompositionB",
        "CompositionC",
        "CompositionD",
    )
    if composition not in list_allowed_compositions:
        raise ValueError("Invalid composition string.")

    # Determine the index of the composition with the maximum value
    max_index = max(
        range(len(gradient_table)), key=lambda i: float(gradient_table[i][composition])
    )
    max_value = gradient_table[max_index][composition]
    return max_index, str(max_value)


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
        _, max_value = determine_index_of_max_compositon_value(
            gradient_table, composition
        )

        # Determine the strong and weak eluents
        if float(gradient_table[0][composition]) < float(max_value):
            strong_eluent = composition
        else:
            list_weak_eluents.append(composition)

    return strong_eluent, list_weak_eluents


def validate_gradient_table(gradient_table: List[dict]) -> bool:
    """
    Validates the gradient table to ensure the sum of compositions in each row is 100.

    Args:
        gradient_table (List[dict]): The gradient table to validate.

    Returns:
        bool: True if the gradient table is valid, False otherwise.
    """
    previous_time = None
    for row in gradient_table:
        list_keys = row.keys()
        if any("Composition" in key for key in list_keys):
            # Test sum of compositions is 100
            sum_compositions = sum(
                float(value) for key, value in row.items() if "Composition" in key
            )
            if sum_compositions != 100:
                raise ValueError(
                    f"""
                    The sum of the compositions in the gradient table row is not equal to 
                    100. The sum is {sum_compositions}. The row is {row}"""
                )

        # Test time is greater than previous time
        if "Time" in row:
            if row["Time"] == "Initial":
                current_time = 0
            else:
                current_time = float(row["Time"])
            if previous_time is not None:
                if current_time < previous_time:
                    raise ValueError(
                        f"The time in the gradient table row is less than the previous row. The row is {row['Time']} and the previous row is {previous_time}."
                    )
            previous_time = current_time

    return True
