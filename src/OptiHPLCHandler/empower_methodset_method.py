import logging
from typing import Union

from .empower_instrument_method import (
    instrument_method_factory,
    InstrumentMethod,
    ColumnHandler,
)

logger = logging.getLogger(__name__)


class EmpowerMethodSetMethod:
    def __init__(self, method_definition: Union[dict, list]):
        """
        Initialize the EmpowerInstrumentMethod.

        :param method_definition: A method definition from Empower. If the entire result
            is passed, the method set method definition will be extracted.
        """
        self.column_oven_list: list[ColumnHandler] = []
        self.instrument_method_list: list[InstrumentMethod] = []

        if isinstance(method_definition, dict):
            # If the entire response from Empower is passed, extract the results
            method_definition = method_definition["results"]
        for instrument_method_definition in method_definition:
            instrument_method = instrument_method_factory(instrument_method_definition)
            self.instrument_method_list.append(instrument_method)
            if isinstance(instrument_method, ColumnHandler):
                self.column_oven_list.append(instrument_method)

    @property
    def original_method(self):
        """
        Return the original method definition.

        :return: The original method definition.
        """
        return [method.original_method for method in self.instrument_method_list]

    @property
    def current_method(self):
        """
        Return the current method definition.

        :return: The current method definition.
        """
        return [method.current_method for method in self.instrument_method_list]

    @property
    def column_temperature(self):
        """
        Return the column temperature.

        :return: The column temperature.
        """
        if len(self.column_oven_list) == 0:
            raise ValueError("No column oven found in method set method.")
        temperature_set = {
            instrument.column_temperature for instrument in self.column_oven_list
        }
        if len(temperature_set) > 1:
            raise ValueError(f"Multiple column temperatures found: {temperature_set}")
        return temperature_set.pop()

    @column_temperature.setter
    def column_temperature(self, temperature: float):
        """
        Set the column temperature.

        :param temperature: The column temperature.
        """
        for instrument in self.column_oven_list:
            instrument.column_temperature = temperature
