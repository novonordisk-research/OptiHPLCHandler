import logging
import re
from typing import List, Optional, Union

from .empower_detector_module_method import Channel, Detector, NoWavelengthError
from .empower_module_method import (
    ColumnManagerMethod,
    ColumnOvenMethod,
    EmpowerModuleMethod,
    SampleManagerMethod,
    SolventManagerMethod,
)
from .factories import module_method_factory
from .utils.data_types import EmpowerInstrumentMethodModel as DataModel

logger = logging.getLogger(__name__)


class EmpowerInstrumentMethod:
    """
    A class to handle Empower instrument methods.

    :ivar original_method: The original method definition.
    :ivar current_method: The current method definition.
    :ivar column_oven_list: A list of column ovens in the instrument method.
    :ivar module_method_list: A list of module methods in the instrument
        method.
    :ivar solvent_handler_method: The solvent manager module method.
    :ivar column_temperature: The column temperature. If multiple column ovens are
        found, the temperature is only returned if all column ovens have the same
        temperature. Otherwise, a ValueError is raised. If no column ovens are found, a
        ValueError is raised. When setting the column temperature, all column ovens
        will be set to the same temperature, regardless of the original temperatures. If
        no column ovens are found, a ValueError is raised.
    :ivar gradient_table: The gradient table. If no solvent manager is found, a
        ValueError is raised. When setting the gradient table, the gradient table of the
        solvent manager will be set to the provided gradient table. If no solvent
        manager is found, a ValueError is raised.
    :ivar valve_position: The valve position. If no solvent manager is found, a
        ValueError is raised. When setting the valve position, the valve position of the
        solvent manager will be set to the provided valve position. If no solvent
        manager is found, a ValueError is raised.
    """

    def __init__(
        self,
        method_definition: Union[dict, list],
        use_sample_manager_oven: bool = False,
    ):
        """
        Initialize the EmpowerInstrumentMethod.

        :param method_definition: A method definition from Empower. If the entire result
            is passed, the instrument method definition will be extracted.
        :param use_sample_manager_oven: If True, both sample manager oven and column
            manager oven will be used. If False, only column manager oven will be used.
        """
        self.module_method_list: list[EmpowerModuleMethod] = []

        if isinstance(method_definition, dict) and "results" in method_definition:
            # If the entire response from Empower is passed, extract the results
            if len(method_definition["results"]) > 1:
                raise ValueError(
                    f"Multiple instrument methods found: {method_definition['results']}"
                )
            method_definition = method_definition["results"][0]
        self.method_name = method_definition["methodName"]
        self.original_method = DataModel(method_definition, mutable=False)
        for module_method_definition in method_definition["modules"]:
            module_method = module_method_factory(module_method_definition)
            self.module_method_list.append(module_method)
        self.use_sample_manager_oven = use_sample_manager_oven

    @property
    def detector_method_list(self) -> list[Detector]:
        """A list of detector module methods in the instrument method."""
        return [
            module for module in self.module_method_list if isinstance(module, Detector)
        ]

    @property
    def sample_handler_method(self) -> Optional[SampleManagerMethod]:
        """The sample manager module method."""
        sample_handler_method = [
            module
            for module in self.module_method_list
            if isinstance(module, SampleManagerMethod)
        ]
        if len(sample_handler_method) == 0:
            return None
        if len(sample_handler_method) > 1:
            raise ValueError("Multiple sample managers found in instrument method.")
        return sample_handler_method[0]

    @property
    def solvent_handler_method(self) -> Optional[SolventManagerMethod]:
        """The sample manager module method."""
        solvent_handler_method = [
            module
            for module in self.module_method_list
            if isinstance(module, SolventManagerMethod)
        ]
        if len(solvent_handler_method) == 0:
            return None
        if len(solvent_handler_method) > 1:
            raise ValueError("Multiple solvent managers found in instrument method.")
        return solvent_handler_method[0]

    @property
    def column_oven_method_list(self) -> List[ColumnOvenMethod]:
        """A list of column ovens in the instrument method."""
        if self.use_sample_manager_oven:
            oven_type_tuple = (ColumnManagerMethod, SampleManagerMethod)
        else:
            oven_type_tuple = (ColumnManagerMethod,)
        return [
            module
            for module in self.module_method_list
            if isinstance(module, oven_type_tuple)
        ]

    @property
    def current_method(self):
        """The current method definition."""
        method = dict(self.original_method)
        method["methodName"] = self.method_name
        method["modules"] = [
            method.current_method for method in self.module_method_list
        ]
        return DataModel(method)

    @property
    def column_temperature(self):
        """The column temperature for the relevant column oven(s) if any are present."""
        if len(self.column_oven_method_list) == 0:
            raise ValueError("No column oven found in instrument method.")
        temperature_set = {
            module.column_temperature for module in self.column_oven_method_list
        }  # A set, so that duplicated values are collpased into one.
        if len(temperature_set) > 1:
            raise ValueError(f"Multiple column temperatures found: {temperature_set}")
        return temperature_set.pop()

    @column_temperature.setter
    def column_temperature(self, temperature: float):
        if len(self.column_oven_method_list) == 0:
            raise ValueError("No column oven found in instrument method.")
        for module in self.column_oven_method_list:
            module.column_temperature = temperature

    @property
    def sample_temperature(self):
        """The sample temperature for the relevant sample oven(s) if any are present."""
        if self.sample_handler_method is None:
            raise ValueError("No sample manager found in instrument method.")
        return self.sample_handler_method.sample_temperature

    @sample_temperature.setter
    def sample_temperature(self, temperature: float):
        if self.sample_handler_method is None:
            raise ValueError("No sample manager found in instrument method.")
        self.sample_handler_method.sample_temperature = temperature

    @property
    def gradient_table(self) -> List[dict]:
        """The gradient table, if a solvent manager module method is present."""
        if self.solvent_handler_method is None:
            raise ValueError(
                "Can't get gradient table, "
                "no solvent manager found in instrument method."
            )
        return self.solvent_handler_method.gradient_table

    @gradient_table.setter
    def gradient_table(self, gradient_table: List[dict]):
        if self.solvent_handler_method is None:
            raise ValueError(
                "Can't set gradient table, "
                "no solvent manager found in instrument method."
            )
        self.solvent_handler_method.gradient_table = gradient_table

    @property
    def valve_position(self):
        """
        The valve position for the solvent manager, if a solvent manager module method
        is present. When setting, can be a list of valve positions (e.g. ["A1", "B2"]),
        or a string containing one or more valve positions, (e.g. "A1, B2").
        """
        if self.solvent_handler_method is None:
            raise ValueError(
                "Can't get valve position, "
                "no solvent manager found in instrument method."
            )
        return self.solvent_handler_method.valve_position

    @valve_position.setter
    def valve_position(self, valve_position: Union[str, List[str]]):
        if self.solvent_handler_method is None:
            raise ValueError(
                "Can't set valve position, "
                "no solvent manager found in instrument method."
            )
        if isinstance(valve_position, str):
            valve_position = [i[0] for i in re.finditer(r"[A-D]\d", valve_position)]
            # Make a list of every instance of XY in the string, where X is A, B, C
            # or D, and Y is a digit (0-9). These are presumed to be valve positions.
            if len(valve_position) == 0:
                raise ValueError(
                    f"Found nothing that could be a valve position in {valve_position}"
                )
        self.solvent_handler_method.valve_position = valve_position

    @property
    def channels(self):
        """The channels for the relevant detector(s) if any are present."""
        channels = []
        for module in self.detector_method_list:
            channels.extend(module.channels)
            try:
                # get attr with default value None raises NoWavelengthError if not found
                spectral_channel = module.spectral_channel
            except NoWavelengthError:
                # No spectral channel found for this detector, so set it to None
                spectral_channel = None
            if spectral_channel is not None:
                channels.append(spectral_channel)
        return channels

    @channels.setter
    def channels(self, channels: list[Channel]):
        detector_channel_pairing = [
            (detector, []) for detector in self.detector_method_list
        ]
        # Finding all the viable channel types in the output method
        all_channel_types: tuple[Channel, ...] = tuple()
        for detector in self.detector_method_list:
            all_channel_types = all_channel_types + detector.channel_types
        # For each input channel, assign it to a detector in the output method
        for channel in channels:
            # For each input channel, check whether it is a viable channel type in the
            # output method. If not, convert it to something else.
            original_channel_type = type(channel)
            if not isinstance(channel, all_channel_types):
                channel = channel.convert()
                if not isinstance(channel, all_channel_types):
                    raise ValueError(
                        f"Channel type {original_channel_type} is not compatible with the output method, nor can it beconverted to any detector in the output method."  # noqa E501
                    )
            for detector, detector_channels in detector_channel_pairing:
                # For each output detector, check whether the channel is viable. If it
                # is, pair it with that detector and stop. If not, continue to the next
                # detector
                if isinstance(channel, detector.channel_types):
                    detector_channels.append(channel)
                    break
                else:
                    raise ValueError(
                        f"Channel type {original_channel_type} does not match any detector in the output method."  # noqa E501
                    )
        for detector, detector_channels in detector_channel_pairing:
            if len(detector_channels) > 0:
                detector.channels = detector_channels

    @property
    def wavelengths(self):
        """The wavelengths for the relevant detector(s) if any are present."""
        wavelengths = []
        for module in self.detector_method_list:
            try:
                wavelengths.extend(module.wavelengths)
            except NoWavelengthError:
                pass  # No wavelengths found for this detector
            try:
                wavelengths.extend(module.spectral_wavelengths)
            except NoWavelengthError:
                pass  # No spectral wavelengths found for this detector
        return wavelengths

    @wavelengths.setter
    def wavelengths(self, wavelengths: list[str]):
        if len(set(type(wavelength) for wavelength in wavelengths)) > 1:
            raise ValueError("Only one type of wavelength can be set at a time.")
        if not all(isinstance(wavelength, (str, int)) for wavelength in wavelengths):
            raise NotImplementedError("Only single wavelength channels are settable.")
        for module in self.detector_method_list:
            try:
                module.wavelengths = wavelengths
                return  # Stops after finding the first detector with wavelengths
            except NoWavelengthError:
                pass
        raise NoWavelengthError(
            "No detector with appropriate channel definitions found."
        )

    @property
    def channels_serialisable(self):
        return [dict(channel) for channel in self.channels]

    def __str__(self):
        return (
            f"{type(self).__name__} with "
            f"{len(self.module_method_list)} module methods of types "
            + (", ".join([type(method).__name__ for method in self.module_method_list]))
        )

    def copy(self):
        if any(
            isinstance(module, SampleManagerMethod)
            for module in self.column_oven_method_list
        ):
            use_sample_manager_oven = True
        else:
            use_sample_manager_oven = False
        copy = EmpowerInstrumentMethod(
            self.original_method, use_sample_manager_oven=use_sample_manager_oven
        )
        copy.method_name = self.method_name
        copy.module_method_list = [module.copy() for module in self.module_method_list]
        return copy
