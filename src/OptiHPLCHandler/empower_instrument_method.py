import logging
from typing import List, Optional, Union

from OptiHPLCHandler.data_types import EmpowerInstrumentMethodModel as DataModel
from OptiHPLCHandler.empower_module_method import (
    ColumnManagerMethod,
    ColumnOvenMethod,
    EmpowerModuleMethod,
    SampleManagerMethod,
    SolventManagerMethod,
    module_method_factory,
)

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
        self.column_oven_method_list: list[ColumnOvenMethod] = []
        self.module_method_list: list[EmpowerModuleMethod] = []
        self.solvent_handler_method: Optional[SolventManagerMethod] = None

        if use_sample_manager_oven:
            oven_type_tuple = (ColumnManagerMethod, SampleManagerMethod)
        else:
            oven_type_tuple = (ColumnManagerMethod,)

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
            if isinstance(module_method, oven_type_tuple):
                self.column_oven_method_list.append(module_method)
            if isinstance(module_method, SolventManagerMethod):
                if self.solvent_handler_method is not None:
                    raise ValueError(
                        "Multiple solvent managers found in instrument method."
                    )
                self.solvent_handler_method = module_method

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
        is present.
        """
        if self.solvent_handler_method is None:
            raise ValueError(
                "Can't get valve position, "
                "no solvent manager found in instrument method."
            )
        return self.solvent_handler_method.valve_position

    @valve_position.setter
    def valve_position(self, valve_position: str):
        if self.solvent_handler_method is None:
            raise ValueError(
                "Can't set valve position, "
                "no solvent manager found in instrument method."
            )
        self.solvent_handler_method.valve_position = valve_position

    def __str__(self):
        return (
            f"{type(self).__name__} with "
            f"{len(self.module_method_list)} module methods of types "
            + (", ".join([type(method).__name__ for method in self.module_method_list]))
        )
