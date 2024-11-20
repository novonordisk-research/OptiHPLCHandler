import logging

from OptiHPLCHandler.applications.empower_implementation.empower_tools import (
    classify_eluents,
)

logger = logging.getLogger(__name__)


def change_gradient_table(  # noqa C901 # NEEDS REVIEW! SRFU
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

    # Determine eluent strength
    classification_input = classify_eluents(input_gradient_table)
    classification_output = classify_eluents(output_gradient_table)

    # Determine that number of compositions in the output method
    output_lines = [
        key for key in output_gradient_table[0].keys() if "Composition" in key
    ]
    input_lines = [
        key for key in input_gradient_table[0].keys() if "Composition" in key
    ]

    logger.debug(f"Classification of eluents in input method: {classification_input}")
    logger.debug(f"Classification of eluents in output method: {classification_output}")

    logger.debug("Determining eluent composition of input and output methods.")
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
        new_gradient_table = []
        for step in input_gradient_table:
            new_step = step.copy()  # Copy to prevent overwiting unread composition
            # Weak eluent composition is as was in output method
            new_step[output_weak_eluent] = step[input_weak_eluent]
            # Strong eluent composition is as was in output method
            new_step[output_strong_composition] = step[input_strong_composition]
            # Set unused solvent lines to 0
            if (
                float(new_step[output_weak_eluent])
                + float(new_step[output_strong_composition])
                != 100
            ):
                raise ValueError(
                    "The sum of the strong and weak eluent in the input method does not equal 100. The gradient is either invalid or another composition has a non zero value which is not supported."  # noqa E501
                )
            for line in unused_output_solvent_lines:
                new_step[line] = 0.0
            new_step["Time"] = step["Time"]
            new_step["Flow"] = step["Flow"]
            new_step["Curve"] = step["Curve"]
            new_gradient_table.append(new_step)

    elif (
        not classification_input["strong_eluents"]
        and not classification_input["weak_eluents"]
    ):
        # Compositions don't change, method is isocratic
        logger.debug("Method is isocratic.")

        # Determine all the composition names in the input method
        non_zero_compositions = set(
            composition
            for step in input_gradient_table
            for composition in step
            if composition not in ["Time", "Flow", "Curve"]
            and float(step[composition]) != 0.0
        )
        logger.debug(f"Non-zero compositions in input method: {non_zero_compositions}")

        # Determine all the composition names in the output method
        unused_output_solvent_lines = [
            key for key in output_gradient_table[0].keys() if "Composition" in key
        ]

        # Remove compositions that have non-zero values in the input method
        unused_output_solvent_lines = [
            line
            for line in unused_output_solvent_lines
            if line not in non_zero_compositions
        ]
        logger.debug(
            f"Unused solvent lines in output method: {unused_output_solvent_lines}"
        )

        # if bsm to bsm, bsm to qsm, qsm to bsm (max two compositions) or qsm to qsm
        # else qsm to bsm (more than two compositions) not possible
        if (
            len(non_zero_compositions) <= 2
        ):  # bsm to bsm, bsm to qsm, qsm to bsm (max two compositions)
            logger.debug(
                f"Number of compositions used in input method is {len(non_zero_compositions)} which is less than or equal to 2. Therefore the transfer is either bsm to bsm, bsm to qsm or qsm to bsm (max two combinations)"  # noqa E501
            )

            logger.debug("Copying over gradient table to output method format.")
            new_gradient_table = []
            for step in input_gradient_table:
                new_step = step.copy()
            for line in unused_output_solvent_lines:
                new_step[line] = "0.0"
            new_step["Time"] = step["Time"]
            new_step["Flow"] = step["Flow"]
            new_step["Curve"] = step["Curve"]
            new_gradient_table.append(new_step)

            if (
                len(output_lines) == 2 and len(input_lines) == 4
            ):  # QSM to BSM (max two compositions)
                logger.debug("QSM to BSM (max two compositions).")

                # if CompositionC or D used. They need to be swapped to A or B
                if "CompositionC" in non_zero_compositions:
                    unused_solvent_line = next(
                        line
                        for line in unused_output_solvent_lines
                        if line not in ["CompositionC", "CompositionD"]
                    )
                    # Solvent line now used
                    unused_output_solvent_lines.remove(unused_solvent_line)
                    unused_output_solvent_lines.append("CompositionC")
                    logger.debug(
                        "CompositionC is used, when target is BSM, swapping..."
                    )
                    logger.debug(f"Swapping CompositionC to {unused_solvent_line}")
                    for step in new_gradient_table:
                        # Find the unused composition
                        new_step[unused_solvent_line] = step.pop("CompositionC")
                if "CompositionD" in non_zero_compositions:
                    unused_solvent_line = next(
                        line
                        for line in unused_output_solvent_lines
                        if line not in ["CompositionC", "CompositionD"]
                    )
                    # Solvent line now used
                    unused_output_solvent_lines.remove(unused_solvent_line)
                    unused_output_solvent_lines.append("CompositionD")
                    logger.debug("CompositionD is used, swapping to CompositionB.")
                    for step in new_gradient_table:
                        step[unused_solvent_line] = step.pop("CompositionD")

        else:  # more than two compositions
            if len(output_lines) == 2:  # QSM to BSM (more than two compositions)
                raise ValueError(
                    "Method has more than two changing compositions and output method is BSM."  # noqa E501
                )
            else:  # QSM to QSM (more than two compositions)
                logger.debug("QSM to QSM (more than two compositions).")
                new_gradient_table = input_gradient_table
    else:
        # Too complicated.
        raise ValueError(
            "Method transfer of gradient tables with multiple strong or weak eluents not supported."  # noqa E501
        )

    # Remove CompositionC and CompositionD if output method is BSM
    if len(output_lines) == 2:  # BSM
        logger.debug("Output method is BSM, removing CompositionC and CompositionD.")
        for step in new_gradient_table:
            step.pop("CompositionC", None)
            step.pop("CompositionD", None)

    return new_gradient_table
