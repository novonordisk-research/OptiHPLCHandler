import logging

from OptiHPLCHandler.applications.empower_implementation.empower_tools import (
    classify_eluents,
)

logger = logging.getLogger(__name__)


def change_gradient_table(
    input_gradient_table: list[dict],
    output_gradient_table: list[dict],
) -> dict:
    """Change the gradient table of the output method to match the input method.

    Args:
    input_gradient_table (dict): The gradient table of the input method
    output_gradient_table (dict): The gradient table of the output method
    output_lines (list[str]): The solvent lines of the output method

    Returns:
    dict: The new gradient table of the output method

    Description:
    This function first classifies the eluents in the input and output methods.

    If the input and output methods are simple, two component gradients, the function
    will transfer the input gradient table to the output gradient table.

    If the input method is isocratic, the function will transfer the input gradient
    table to the output gradient table. Here are the possible combinations:

    - BSM to BSM, BSM to QSM, QSM to BSM (max two compositions)
    - QSM to QSM

    QSM to BSM (more than two compositions) is not possible.

    Where BSM is binary solvent manager and QSM is quaternary solvent manager.

    If the input method gradient table has more than two changing compositions, the
    function will raise a ValueError.

    """
    logger.debug(f"Input gradient table: {input_gradient_table}")
    logger.debug(f"Initial output gradient table: {output_gradient_table}")
    input_lines = [
        key for key in input_gradient_table[0].keys() if "Composition" in key
    ]
    output_lines = [
        key for key in output_gradient_table[0].keys() if "Composition" in key
    ]
    if set(input_lines) == set(output_lines):
        logger.debug(
            "Like to like method transfer, returning gradient table unchanged."
        )
        return input_gradient_table

    # Determine eluent strength
    classification_input = classify_eluents(input_gradient_table)
    classification_output = classify_eluents(output_gradient_table)

    logger.debug(f"Classification of eluents in input method: {classification_input}")
    logger.debug(f"Classification of eluents in output method: {classification_output}")

    logger.debug("Determining eluent composition of input and output methods.")
    new_gradient_table = []
    if (
        len(classification_input["strong_eluents"]) == 1
        and len(classification_input["weak_eluents"]) == 1
    ):
        logger.debug("Both gradient tables are simple, two component gradients.")
        # Only two eluents in the method, w/ gradient
        input_strong_composition = classification_input["strong_eluents"][0]
        input_weak_eluent = classification_input["weak_eluents"][0]
        output_strong_composition = classification_output["strong_eluents"][0]
        output_weak_eluent = classification_output["weak_eluents"][0]

        # Determine unused solvent lines
        compositions_in_output = [
            key for key in output_gradient_table[0].keys() if "Composition" in key
        ]
        unused_output_solvent_lines = compositions_in_output

        # remove used solvent lines
        unused_output_solvent_lines.remove(output_strong_composition)
        unused_output_solvent_lines.remove(output_weak_eluent)

        # Ensure strong eluent is composition B and weak eluent is composition A
        # Doesn't check if already in correct format
        logger.debug("Transferring gradient table to output method.")

        for step in input_gradient_table:
            new_step = {
                output_weak_eluent: step[input_weak_eluent],
                output_strong_composition: step[input_strong_composition],
                "Time": step["Time"],
                "Flow": step["Flow"],
                "Curve": step["Curve"],
            }
            for line in unused_output_solvent_lines:
                new_step[line] = 0.0
            new_gradient_table.append(new_step)

    elif (
        not classification_input["strong_eluents"]
        and not classification_input["weak_eluents"]
    ):
        # Compositions don't change, method is isocratic
        logger.debug("Method is isocratic.")

        # Determine all the composition names in the input method
        non_zero_compositions = [
            composition
            for composition in input_gradient_table[0].keys()
            if composition not in ["Time", "Flow", "Curve"]
            and float(input_gradient_table[0][composition]) != 0.0
        ]
        logger.debug(f"Non-zero compositions in input method: {non_zero_compositions}")
        if len(non_zero_compositions) > len(output_lines):
            raise ValueError(
                "Method uses more compositions than output method. Cannot transfer gradient table."  # noqa E501
            )
        for step in input_gradient_table:
            unused_output_solvent_lines = output_lines.copy()
            new_step = {line: "0.0" for line in output_lines}
            for composition in non_zero_compositions:
                new_step[unused_output_solvent_lines.pop(0)] = step[composition]
            new_step["Time"] = step["Time"]
            new_step["Flow"] = step["Flow"]
            new_step["Curve"] = step["Curve"]
            new_gradient_table.append(new_step)
    else:
        # Too complicated.
        raise ValueError(
            "Method transfer of gradient tables with multiple strong or weak eluents not supported."  # noqa E501
        )

    return new_gradient_table
