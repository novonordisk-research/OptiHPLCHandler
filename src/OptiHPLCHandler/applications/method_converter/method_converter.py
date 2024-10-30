import warnings
from typing import Union

from OptiHPLCHandler import EmpowerInstrumentMethod
from OptiHPLCHandler.applications.empower_implementation.empower_tools import (
    classify_eluents,
)
from OptiHPLCHandler.empower_detector_module_method import PDAMethod, TUVMethod


def transfer_gradient_table(
    input_method: EmpowerInstrumentMethod, output_method: EmpowerInstrumentMethod
) -> None:
    """Transfer the gradient table from one method to another.

    Args:
    input_method (EmpowerInstrumentMethod): The method to transfer the gradient from.
    output_method (EmpowerInstrumentMethod): The method to transfer the gradient to.

    Returns:
    EmpowerInstrumentMethod: The output method gradient table is modified in place.

    Description:
    This function transfers the gradient table from one method to another. The solvent
    selection is conserved based on the eluent strength of the output method.
    """
    # Extract the gradient table from the input_method
    # Pump type of input_method is irrelevant as the gradient table is normalised
    input_gradient_table: list[dict] = input_method.gradient_table
    output_gradient_table: list[dict] = output_method.gradient_table

    # Determine eluent strength
    input_strong_composition = classify_eluents(input_gradient_table)["strong_eluents"][
        0
    ]
    input_weak_eluent = classify_eluents(input_gradient_table)["weak_eluents"][0]
    output_strong_composition = classify_eluents(output_gradient_table)[
        "strong_eluents"
    ][0]
    output_weak_eluent = classify_eluents(output_gradient_table)["weak_eluents"][0]

    # Determine unused solvent lines
    unused_output_solvent_lines = output_method.solvent_handler_method.solvent_lines
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
    new_gradient_table = []
    for step in input_gradient_table:
        new_step = step.copy()  # Copy to prevent overwiting unread composition
        # Weak eluent set to whatever the weak eluent is in output method initially
        new_step[output_weak_eluent] = step[input_weak_eluent]
        # Strong eluent set to whatever the strong eluent was in output method initially
        new_step[output_strong_composition] = step[input_strong_composition]
        # Set unused solvent lines to 0.0
        for line in unused_output_solvent_lines:
            new_step[line] = 0.0
        new_step["Time"] = step["Time"]
        new_step["Flow"] = step["Flow"]
        new_step["Curve"] = step["Curve"]
        new_gradient_table.append(new_step)
    input_gradient_table = new_gradient_table

    # TODO what if QSM to BSM and used solvent lines are different?
    # Remove CompositionC and CompositionD if output method is BSM
    # isinstance(output_method.solvent_handler_method, BSMMethod) didn't work in tests
    # so used __class__.__name__ instead. Probably a better way to mock the classes.
    if output_method.solvent_handler_method.__class__.__name__ == "BSMMethod":
        for step in input_gradient_table:
            step.pop("CompositionC", None)
            step.pop("CompositionD", None)

    # Transfer the gradient table to the output method
    output_method.gradient_table = input_gradient_table


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
    change_dict = {}
    for input_value, (output_key, output_value) in zip(
        input_dict.values(), output_dict.items()
    ):
        input_wavelength = input_value.get("Wavelength1", input_value.get("Wavelength"))

        # Determine the wavelength key name of the output
        # (PDA: Wavelength1, TUV: Wavelength)
        output_key_name = (
            "Wavelength1" if "Wavelength1" in output_value else "Wavelength"
        )
        change_dict[output_key] = {}
        change_dict[output_key][output_key_name] = input_wavelength

        if "Enabled" not in input_value and "Enabled" in output_value:
            # TUV to PDA, set all enabled to True
            # No way of knowing if the input is enabled or not
            change_dict[output_key]["Enabled"] = True

        elif "Enabled" in input_value and "Enabled" in output_value:
            # PDA to PDA, takes enabled key of input and sets it to output
            change_dict[output_key]["Enabled"] = input_value["Enabled"]

    output_dict.update(change_dict)

    return change_dict, output_dict


def transfer_wavelengths(
    input_method: EmpowerInstrumentMethod, output_method: EmpowerInstrumentMethod
) -> None:
    """Transfer the wavelengths from one method to another.

    Args:
    input_method (EmpowerInstrumentMethod): The method to transfer the wavelengths from.
    output_method (EmpowerInstrumentMethod): The method to transfer the wavelengths to.

    Returns:
    EmpowerInstrumentMethod: The output method wavelengths are modified in place.

    Description:


    """
    # Find first detector method that is either PDAMethod or TUVMethod
    # If a method has both a PDA and TUV detector method, the first one is used
    input_detector_method: Union[PDAMethod, TUVMethod] = next(
        (
            detector
            for detector in input_method.detector_method_list
            if detector.__class__.__name__ in ["PDAMethod", "TUVMethod"]
        ),
        None,
    )
    output_detector_method: Union[PDAMethod, TUVMethod] = next(
        (
            detector
            for detector in output_method.detector_method_list
            if detector.__class__.__name__ in ["PDAMethod", "TUVMethod"]
        ),
        None,
    )

    # if value is None, no PDA or TUV detector method found

    if input_detector_method is None:
        raise ValueError("No PDA or TUV detector method found in the input method.")
    if output_detector_method is None:
        raise ValueError("No PDA or TUV detector method found in the output method.")

    # Get the channel_dict
    input_detector_dict = input_detector_method.channel_dict
    output_detector_dict = output_detector_method.channel_dict

    # Transfer the wavelengths
    change_dict, _ = change_wavelengths(input_detector_dict, output_detector_dict)
    print("changed to", change_dict)

    # Set the output detector dictionary
    output_detector_method.channel_dict = change_dict

    # Set defaults
    output_detector_method.lamp_enabled = True  # Ensure lamp is enabled

    # Errors and warnings
    # If PDA method and no channels are enabled, enable the first channel
    if output_detector_method.__class__.__name__ == "PDAMethod" and not any(
        channel["Enabled"] for channel in output_detector_method.channel_dict.values()
    ):
        warnings.warn(
            "No channels enabled in output method. Enabling Channel1.", stacklevel=1
        )
        output_detector_method.channel_dict["Channel1"]["Enabled"] = True

    return output_method
