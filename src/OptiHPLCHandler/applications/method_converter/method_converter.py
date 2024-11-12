import logging
import warnings
from dataclasses import dataclass
from typing import Union

from OptiHPLCHandler import EmpowerInstrumentMethod
from OptiHPLCHandler.applications.empower_implementation.empower_tools import (
    classify_eluents,
)
from OptiHPLCHandler.empower_detector_module_method import (
    PDAMethod,
    TUVMethod,
    FLRMethod,
)
from OptiHPLCHandler.utils.validate_method_name import append_truncate_method_name

logger = logging.getLogger(__name__)


@dataclass
class MethodParts:
    """Dataclass to store the parts of an EmpowerInstrumentMethod."""

    gradient_table: list[dict]
    channels: list[dict]
    sample_temperature: float
    column_temperature: float
    solvent_lines: list[str]
    original_method_name: str
    _original_method: EmpowerInstrumentMethod

    def __init__(self, method: EmpowerInstrumentMethod):
        self.gradient_table = method.gradient_table
        if not self.gradient_table:
            raise ValueError("No gradient table found in the method.")

        # If detectors other than PDA or TUV are used, raise a warning
        other_detectors = [
            detector
            for detector in method.detector_method_list
            if not isinstance(detector, (PDAMethod, TUVMethod, FLRMethod))
        ]
        if other_detectors:
            warnings.warn(
                f"Detectors other than PDA,TUV or FLR are present in the method: {other_detectors}. These detectors will not be transferred."  # noqa E501
            )

        # If both PDA and TUV detectors are used, raise a warning
        allowed_detectors = [
            detector
            for detector in method.detector_method_list
            if isinstance(detector, (PDAMethod, TUVMethod))
        ]
        # If no PDA, FLR or TUV detectors are found, raise a ValueError
        if not allowed_detectors:
            raise ValueError("No PDA, FLR or TUV detector method found in the method.")

        detectors: list[Union[PDAMethod, TUVMethod, FLRMethod]] = allowed_detectors

        self.channels = [detector.channel_dict for detector in detectors]
        if not self.channel_dict:
            raise ValueError("No channel dictionary found in the detector method.")

        self.sample_temperature = method.sample_temperature
        self.column_temperature = method.column_temperature
        self.solvent_lines = method.solvent_handler_method.solvent_lines

        # Save the original method and method name
        self.original_method_name = method.method_name
        self._original_method = method


def change_gradient_table(  # noqa C901
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


def change_gradient_table_from_method_parts(
    input_parts: MethodParts, output_method: EmpowerInstrumentMethod
) -> list[dict]:
    """Change the gradient table of the output method to match the input method.

    Args:
    input_parts (MethodParts): The parts of the input method
    output_method (EmpowerInstrumentMethod): The output method

    Returns:
    list[dict]: The new gradient table of the output method

    Description:
    The function is a wrapper for change_gradient_table. See change_gradient_table for
    more information.
    """
    return change_gradient_table(
        input_parts.gradient_table,
        output_method.gradient_table,
    )


@dataclass
class PDAAbsorbanceChannel:
    """Dataclass to store the channels in PDA Method."""

    absorbance_wavelength: float
    enable: bool
    type: str = "Single"  # Hardcode


@dataclass
class PDASpectralChannel:
    """Dataclass to store the sepctral channel in a PDA Method."""

    start_wavelength: float
    end_wavelength: float
    enable: bool
    type: str = "Spectral"  # Hardcode


@dataclass
class TUVChannel:
    """Dataclass to store the channels in TUV Method."""

    absorbance_wavelength: float
    type: str


def change_channels(input_list_dict: dict, output_list_dict: dict) -> list[dict]:
    """Takes a list of channel_dicts (from detector methods), identifies the module and
    changes the output to match the input."""
    # if input only contains PDA and output contains TUV, it will change
    # if input contains TUV and PDA and output contains TUV, it will assume its the TUV
    # you would want to change
    # if input contains TUV and PDA and output contains TUV and PDA, it will change both

    # identify the module
    # PDA has 8 channels and a spectral channel, has wavelength1 as the key (enable key)
    # TUV has two and the key is wavelength (no enable key)
    # FLR has 4 channels and two different wavelength keys, Excitation and Emission
    # enable key is present
    # RI not support
    pass


# minimum input, requires channel_dict for both input and output
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


def change_wavelengths_from_method_parts(
    input_parts: MethodParts, output_method: EmpowerInstrumentMethod
) -> tuple[dict, dict]:
    # Requires output method parts to determine the detector type
    output_method_parts = MethodParts(output_method)
    return change_wavelengths(
        input_parts.channel_dict, output_method_parts.channel_dict
    )


def transfer_method_from_method_parts(
    input_parts: MethodParts, output_method: EmpowerInstrumentMethod
) -> None:
    """Transfer the method parts from the input method to the output method.

    Args:
    input_parts (MethodParts): The parts of the input method
    output_method (EmpowerInstrumentMethod): The output method

    Description:
    The function transfers the gradient table, wavelengths, sample temperature, column
    temperature and method name from the input method to the output method.
    """

    logger.debug("Transferring gradient table from input to output method.")
    new_gradient_table = change_gradient_table_from_method_parts(
        input_parts, output_method
    )
    output_method.gradient_table = new_gradient_table

    logger.debug("Transferring wavelengths from input to output method.")
    change_dict, _ = change_wavelengths_from_method_parts(input_parts, output_method)

    # find the first TUV or PDA detector in output method
    # This is done in the extract_method_parts function for the input method
    output_detector: Union[PDAMethod, TUVMethod] = next(
        (
            detector
            for detector in output_method.detector_method_list
            if isinstance(detector, (PDAMethod, TUVMethod))
        ),
        None,
    )
    if output_detector is None:
        raise ValueError("No PDA or TUV detector method found in the output method.")

    output_detector.channel_dict = change_dict

    logger.debug(
        f"Transferring sample temperature from {input_parts.sample_temperature} to {output_method.sample_temperature}."  # noqa E501
    )
    output_method.sample_temperature = input_parts.sample_temperature

    logger.debug(
        f"Transferring column temperature from {input_parts.column_temperature} to {output_method.column_temperature}."  # noqa E501
    )
    output_method.column_temperature = input_parts.column_temperature

    # New output method name is input method name + "_transfer" and is truncated to 32
    # characters if necessary
    logger.debug("Constructing method name for output method.")
    new_method_name = append_truncate_method_name(
        input_parts.original_method_name, "_transfer"
    )
    output_method.method_name = new_method_name

    logger.info(f"Method transfer complete. Output method name: {new_method_name}")


def transfer_method(
    input_method: EmpowerInstrumentMethod, output_method: EmpowerInstrumentMethod
) -> None:
    input_parts = MethodParts(input_method)
    logger.debug(f"Extracted input method parts: {input_parts}")

    transfer_method_from_method_parts(input_parts, output_method)

    logger.info(
        f"Method transfer complete. Output method name: {output_method.method_name}"
    )
