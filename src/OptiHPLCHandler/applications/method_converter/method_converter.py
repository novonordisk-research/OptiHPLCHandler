import logging
import warnings
from typing import Union

from OptiHPLCHandler import EmpowerInstrumentMethod
from OptiHPLCHandler.applications.empower_implementation.empower_tools import (
    classify_eluents,
)
from OptiHPLCHandler.empower_detector_module_method import PDAMethod, TUVMethod
from OptiHPLCHandler.empower_module_method import BSMMethod
from OptiHPLCHandler.utils.validate_method_name import append_truncate_method_name

logger = logging.getLogger(__name__)

# make function that extracts the parts


def change_gradient_table(
    input_gradient_table: dict, output_gradient_table: dict, output_lines: list[str]
) -> dict:
    logger.debug(f"Input gradient table: {input_gradient_table}")
    logger.debug(f"Initial output gradient table: {output_gradient_table}")

    # Determine eluent strength
    classification_input = classify_eluents(input_gradient_table)
    classification_output = classify_eluents(output_gradient_table)

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

    elif (  # remove this elif when above done
        not classification_input["strong_eluents"]
        and not classification_input["weak_eluents"]
    ):
        # Compositions don't change, method is isocratic
        # TODO: Implement isocratic method transfer
        # if qsm to bsm, only two lines can have values
        raise NotImplementedError("Method transfer of isocratic methods not supported.")

    else:
        # Too complicated.
        raise ValueError(
            "Method transfer of gradient tables with multiple strong or weak eluents not supported."  # noqa E501
        )

    # Determine unused solvent lines
    unused_output_solvent_lines = output_lines
    # Remove valve number and add Composition to the solvent lines
    unused_output_solvent_lines = unused_output_solvent_lines = [
        f"Composition{line[:-1]}" if line[-1].isdigit() else f"Composition{line}"
        for line in unused_output_solvent_lines
    ]
    # remove used solvent lines
    unused_output_solvent_lines.remove(output_strong_composition)
    unused_output_solvent_lines.remove(output_weak_eluent)

    # Ensure strong eluent is composition B and weak eluent is composition A
    # Doesn't check if already in correct format
    logger.debug("Transferring gradient table to output method.")
    new_gradient_table = []
    for step in input_gradient_table:
        new_step = step.copy()  # Copy to prevent overwiting unread composition
        # Weak eluent set to whatever the weak eluent is in output method initially
        new_step[output_weak_eluent] = step[input_weak_eluent]
        # Strong eluent set to whatever the strong eluent was in output method initially
        new_step[output_strong_composition] = step[input_strong_composition]
        # Set unused solvent lines to 0.0 (This needs changing for isocratic methods)
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

    return new_gradient_table


def transfer_gradient_table(
    input_method: EmpowerInstrumentMethod, output_method: EmpowerInstrumentMethod
) -> None:
    """Transfer the gradient table from one method to another.

    Args:
    input_method (EmpowerInstrumentMethod): The method to transfer the gradient from.
    output_method (EmpowerInstrumentMethod): The method to transfer the gradient to.

    Returns:
    None: The output method gradient table is modified in place.

    Description:
    This function transfers the gradient table from one method to another. The solvent
    selection is conserved based on the eluent strength of the output method.

    Note:
    The gradient table composition set and valve positions are set to how they were
    defined in the output method.
    """
    logger.debug("Transferring gradient table from input method to output method.")
    input_gradient_type = type(input_method.solvent_handler_method)
    output_gradient_type = type(output_method.solvent_handler_method)
    logger.debug(f"Input gradient type: {input_gradient_type}")
    logger.debug(f"Output gradient type: {output_gradient_type}")

    # Extract the gradient table from the input_method
    # Pump type of input_method is irrelevant as the gradient table is normalised
    input_gradient_table: list[dict] = input_method.gradient_table
    output_gradient_table: list[dict] = output_method.gradient_table

    input_gradient_table = change_gradient_table(
        input_gradient_table,
        output_gradient_table,
        output_method.solvent_handler_method.solvent_lines,
    )

    # Remove CompositionC and CompositionD if output method is BSM
    if isinstance(output_method.solvent_handler_method, BSMMethod):
        for step in input_gradient_table:
            step.pop("CompositionC", None)
            step.pop("CompositionD", None)

    # Transfer the gradient table to the output method
    output_method.gradient_table = input_gradient_table

    logger.info(
        f"Gradient table of output method changed to : {output_method.gradient_table}"
    )


def change_wavelengths(input_dict: dict, output_dict: dict) -> tuple[dict, dict]:
    """Change the wavelengths of the output dictionary to match the input dictionary.

    Args:
    input_dict (dict): The dictionary containing the input wavelengths.
    output_dict (dict): The dictionary containing the output wavelengths.

    Returns:
    tuple[dict, dict]: The dictionary containing the changes made and the output
    dictionary.

    output_dict is modified in place. changes_dict contains only the changes made.

    Description:
    The function iterates over the lists, finishing at the end of the shorter list. It
    finds the wavelength of the input (whether the key be Wavelength1 or Wavelength) and
    sets the output wavelength to the input wavelength (keeping the key name the same).
    If the input does not contain the enabled key, and the output does, the enabled key
    is set to True. The function is designed to work with the following combinations:

    TUV to PDA, set all enabled to True
    PDA to TUV, takes the first two wavelengths and TUV doesn't have the enabled key
    PDA to PDA, takes the enabled key of the input and sets it to the output
    TUV to TUV, takes the first two wavelengths of the input and sets it to the output

    """
    logger.debug("Changing wavelengths of the output dictionary to match the input.")
    change_dict = {}
    for (input_key, input_value), (output_key, output_value) in zip(
        input_dict.items(), output_dict.items()
    ):
        input_wavelength = input_value.get("Wavelength1", input_value.get("Wavelength"))

        # Skip the spectral channel key
        if input_key == "SpectralChannel" or output_key == "SpectralChannel":
            # Skip the spectral channel key
            logger.debug("Skipping spectral channel key.")
            continue

        # Determine the wavelength key name of the output
        # (PDA: Wavelength1, TUV: Wavelength)
        output_key_name = (
            "Wavelength1" if "Wavelength1" in output_value else "Wavelength"
        )
        change_dict[output_key] = {}
        change_dict[output_key][output_key_name] = input_wavelength

        if "Enable" not in input_value and "Enable" in output_value:
            # TUV to PDA, set all enabled to True
            # No way of knowing if the input is enabled or not
            logger.debug("TUV to PDA, setting all enabled to True.")
            change_dict[output_key]["Enable"] = True

        elif "Enable" in input_value and "Enable" in output_value:
            # PDA to PDA, takes enabled key of input and sets it to output
            logger.debug("PDA to PDA, setting enabled key of input to output.")
            change_dict[output_key]["Enable"] = input_value["Enable"]

    output_dict.update(change_dict)
    logger.debug(f"Output dictionary changed to: {output_dict}")
    logger.debug(f"Changes made: {change_dict}")

    return change_dict, output_dict


def transfer_wavelengths(
    input_method: EmpowerInstrumentMethod, output_method: EmpowerInstrumentMethod
) -> None:
    """Transfer the wavelengths from one method to another.

    Args:
    input_method (EmpowerInstrumentMethod): The method to transfer the wavelengths from.
    output_method (EmpowerInstrumentMethod): The method to transfer the wavelengths to.

    Returns:
    None: The output method wavelengths are modified in place.

    Description:


    """
    logger.debug("Transferring wavelengths from input method to output method.")
    # Find first detector method that is either PDAMethod or TUVMethod
    # If a method has both a PDA and TUV detector method, the first one is used
    input_detector_method: Union[PDAMethod, TUVMethod] = next(
        (
            detector
            for detector in input_method.detector_method_list
            if isinstance(detector, (PDAMethod, TUVMethod))
        ),
        None,
    )
    output_detector_method: Union[PDAMethod, TUVMethod] = next(
        (
            detector
            for detector in output_method.detector_method_list
            if isinstance(detector, (PDAMethod, TUVMethod))
        ),
        None,
    )

    logger.debug(f"Input detector method type: {type(input_detector_method)}")
    logger.debug(f"Output detector method type: {type(output_detector_method)}")
    # if value is None, no PDA or TUV detector method found

    if input_detector_method is None:
        raise ValueError("No PDA or TUV detector method found in the input method.")
    if output_detector_method is None:
        raise ValueError("No PDA or TUV detector method found in the output method.")

    # Get the channel_dict
    input_detector_dict = input_detector_method.channel_dict
    output_detector_dict = output_detector_method.channel_dict

    logger.debug(f"Input detector dictionary: {input_detector_dict}")
    logger.debug(f"Output detector dictionary: {output_detector_dict}")

    # Transfer the wavelengths
    change_dict, _ = change_wavelengths(input_detector_dict, output_detector_dict)
    logger.debug(
        f"The following changes will be applied to {output_method.method_name} from {input_method.method_name}: {change_dict}"  # noqa E501
    )

    # Set the output detector dictionary
    output_detector_method.channel_dict = change_dict

    # Set defaults
    if output_detector_method.lamp_enabled is False:
        output_detector_method.lamp_enabled = True  # Ensure lamp is enabled
        logger.debug(f"Enabling lamp for {output_method.method_name}.")

    # Errors and warnings
    # If PDA method and no channels are enabled, enable the first channel
    if isinstance(output_detector_method, PDAMethod) and not any(
        channel["Enable"] for channel in output_detector_method.channel_dict.values()
    ):
        warning_str = "No channels enabled in output method. Enabling Channel1."
        warnings.warn(warning_str)
        output_detector_method.channel_dict["Channel1"]["Enable"] = True


def transfer_method(
    input_method: EmpowerInstrumentMethod, output_method: EmpowerInstrumentMethod
) -> None:
    """Transfers the following from the input method to the output method:
    - Gradient Table
    - Wavelengths
    - Sample Temperature
    - Column Temperature

    Args:
        input_method (EmpowerInstrumentMethod): The method to transfer from
        output_method (EmpowerInstrumentMethod): The method to transfer to

    Returns:
        None - The output_method is modified in place

    Note:
    The gradient table composition set and valve positions are set to how they were
    defined in the output method.

    Column position is set in the sample set method and not in the method itself.
    """
    transfer_gradient_table(input_method, output_method)
    transfer_wavelengths(input_method, output_method)
    logger.debug(
        f"Transferring sample temperature from {output_method.sample_temperature} to {input_method.sample_temperature}."  # noqa E501
    )
    output_method.sample_temperature = input_method.sample_temperature
    logger.debug(
        f"Transferring column temperature from {output_method.column_temperature} to {input_method.column_temperature}."  # noqa E501
    )
    output_method.column_temperature = input_method.column_temperature

    # New output method name is input method name + "_transfer" and is truncated to 32
    # characters if necessary
    logger.debug("Constructing method name for output method.")
    new_method_name = append_truncate_method_name(input_method.method_name, "_transfer")
    output_method.method_name = new_method_name

    logger.info(f"Method transfer complete. Output method name: {new_method_name}")


def change_method(
    method: EmpowerInstrumentMethod,
    gradient_table: list[dict],
    channel_dict: dict,
    sample_temperature: float,
    column_temperature: float,
):
    """Applies the following changes to the method:
    - Gradient Table
    - Wavelengths
    - Sample Temperature
    - Column Temperature

    Args:
    method (EmpowerInstrumentMethod): The method to change
    gradient_table (list[dict]): The gradient table to change to
    channel_dict (dict): The channel dictionary to change to
    sample_temperature (float): The sample temperature to change to
    column_temperature (float): The column temperature to change to

    Returns:
    None - The method is modified in place
    """

    # Generate gradient table based on format of output method
    output_gradient_table: list[dict] = change_gradient_table(
        gradient_table,
        method.gradient_table,
        method.solvent_handler_method.solvent_lines,
    )

    # Remove CompositionC and CompositionD if output method is BSM
    if isinstance(method.solvent_handler_method, BSMMethod):
        for step in output_gradient_table:
            step.pop("CompositionC", None)
            step.pop("CompositionD", None)

    # Transfer the gradient table to the output method
    method.gradient_table = output_gradient_table

    # Generate channel_dict based on format of output method
    change_dict, _ = change_wavelengths(
        channel_dict, method.detector_method_list[0].channel_dict
    )
    method.detector_method_list[0].channel_dict = change_dict
    # HCECK DETECTOR!

    # Set defaults
    # if method.detector_method.lamp_enabled is False:
    #    method.detector_method.lamp_enabled = True

    # Errors and warnings
    # If PDA method and no channels are enabled, enable the first channel
    # if isinstance(method.detector_method, PDAMethod) and not any(
    #    channel["Enable"] for channel in method.detector_method.channel_dict.values()
    # ):
    #    warning_str = "No channels enabled in output method. Enabling Channel1."
    #    warnings.warn(warning_str)

    # Set sample and column temperature
    method.sample_temperature = sample_temperature
    method.column_temperature = column_temperature

    logger.info("Method change complete.")
