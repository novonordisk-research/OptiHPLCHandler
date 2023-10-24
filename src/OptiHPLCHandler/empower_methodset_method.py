import logging
from typing import List, Union

from OptiHPLCHandler.data_types import EmpowerMethodSetMethodModel as DataModel
from OptiHPLCHandler.empower_instrument_method import (
    ColumnOvenMethod,
    EmpowerInstrumentMethod,
    SolventManagerMethod,
    instrument_method_factory,
)

logger = logging.getLogger(__name__)


class EmpowerMethodSetMethod:
    """
    A class to handle Empower method set methods.

    : attribute original_method: The original method definition.
    : attribute current_method: The current method definition.
    : attribute column_oven_list: A list of column ovens in the method set method.
    : attribute instrument_method_list: A list of instrument methods in the method set
        method.
    : attribute column_temperature: The column temperature. If multiple column ovens are
        found, the temperature is only returned if all column ovens have the same
        temperature. Otherwise, a ValueError is raised. If no column ovens are found, a
        ValueError is raised. When setting the column temperature, all column ovens
        will be set to the same temperature, regardless of the original temperatures. If
        no column ovens are found, a ValueError is raised.
    """

    def __init__(self, method_definition: Union[dict, list]):
        """
        Initialize the EmpowerInstrumentMethod.

        :param method_definition: A method definition from Empower. If the entire result
            is passed, the method set method definition will be extracted.
        """
        self.column_oven_method_list: list[ColumnOvenMethod] = []
        self.instrument_method_list: list[EmpowerInstrumentMethod] = []
        self.solvent_handler_method = None

        if isinstance(method_definition, dict) and "results" in method_definition:
            # If the entire response from Empower is passed, extract the results
            if len(method_definition["results"]) > 1:
                raise ValueError(
                    f"Multiple method set methods found: {method_definition['results']}"
                )
            method_definition = method_definition["results"][0]
        self.method_name = method_definition["methodName"]
        self.original_method = DataModel(method_definition, mutable=False)
        for instrument_method_definition in method_definition["modules"]:
            instrument_method = instrument_method_factory(instrument_method_definition)
            self.instrument_method_list.append(instrument_method)
            if isinstance(instrument_method, ColumnOvenMethod):
                self.column_oven_method_list.append(instrument_method)
            if isinstance(instrument_method, SolventManagerMethod):
                if self.solvent_handler_method is not None:
                    raise ValueError(
                        "Multiple solvent managers found in method set method."
                    )
                self.solvent_handler_method = instrument_method

    @property
    def current_method(self):
        """
        Return the current method definition.

        :return: The current method definition.
        """
        method = dict(self.original_method)
        method["methodName"] = self.method_name
        method["modules"] = [
            method.current_method for method in self.instrument_method_list
        ]
        return DataModel(method)

    @property
    def column_temperature(self):
        """
        Return the column temperature.

        :return: The column temperature.
        """
        if len(self.column_oven_method_list) == 0:
            raise ValueError("No column oven found in method set method.")
        temperature_set = {
            instrument.column_temperature for instrument in self.column_oven_method_list
        }  # A set, so that duplicated values are collpased into one.
        if len(temperature_set) > 1:
            raise ValueError(f"Multiple column temperatures found: {temperature_set}")
        return temperature_set.pop()

    @column_temperature.setter
    def column_temperature(self, temperature: float):
        if len(self.column_oven_method_list) == 0:
            raise ValueError("No column oven found in method set method.")
        for instrument in self.column_oven_method_list:
            instrument.column_temperature = temperature

    @property
    def gradient_table(self) -> List[dict]:
        """
        Return the gradient table.

        :return: The gradient table.
        """
        if self.solvent_handler_method is None:
            raise ValueError(
                "Can't get gradient table, "
                "no solvent manager found in method set method."
            )
        return self.solvent_handler_method.gradient_table

    @gradient_table.setter
    def gradient_table(self, gradient_table: List[dict]):
        if self.solvent_handler_method is None:
            raise ValueError(
                "Can't set gradient table, "
                "no solvent manager found in method set method."
            )
        self.solvent_handler_method.gradient_table = gradient_table

    @property
    def valve_position(self):
        """
        Return the valve position.

        :return: The valve position.
        """
        if self.solvent_handler_method is None:
            raise ValueError(
                "Can't get valve position, "
                "no solvent manager found in method set method."
            )
        return self.solvent_handler_method.valve_position

    @valve_position.setter
    def valve_position(self, valve_position: str):
        if self.solvent_handler_method is None:
            raise ValueError(
                "Can't set valve position, "
                "no solvent manager found in method set method."
            )
        self.solvent_handler_method.valve_position = valve_position

    def __str__(self):
        return (
            "EmpowerMethodSetMethod with "
            f"{len(self.instrument_method_list)} instrument methods of types "
            ", ".join([type(method).__name__ for method in self.instrument_method_list])
        )
