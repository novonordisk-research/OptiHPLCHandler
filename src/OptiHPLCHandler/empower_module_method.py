import logging
import re
import warnings
from typing import Dict, List, Mapping, Tuple, Union
from xml.etree import ElementTree as ET

from .utils.data_types import EmpowerModuleMethodModel as DataModel

logger = logging.getLogger(__name__)


class EmpowerModuleMethod:
    """
    Generic module method class that can be used for any Empower module method.
    For specific modules, a subclass should be created that inherits from this class.

    Specific parameters for the method can be set and retrieved using the [] operator,
    e.g `method["ColumnTemperature"] = "50.03"`. This will replace the current value of
    ColumnTemperature with the new value in the underlying xml. The current value can be
    retrieved in the same way. This only works if there is exactly one instance of the
    key in the xml. If there are multiple instances, a ValueError will be raised. If the
    key is not present, a KeyError will be raised. If more than one key is present, use
    the xml key to retrieve the xml and make changes to it through the `replace` method.
    This will replace all instances of the original string with the new string in the
    xml.

    If no xml key is present in the method definition, no changes can be made to the
    method, but the original method definition can still be retrieved.

    :ivar original_method: The original method definition.
    :ivar current_method: The current method definition, including the changes that
        have been made.
    """

    def __init__(self, method_definition: Mapping[str, str]):
        """
        Initialize the EmpowerModuleMethod.

        :param method_definition: The method definition from Empower. Should contain at
            least an xml key. If it is not present, the EmpowerModuleMethod can still be
            created, but no changes can be made to the method, and no values can be
            extracted.
        """
        self.original_method = DataModel(method_definition, mutable=False)
        self._change_list: List[Tuple[str, str]] = []

    def replace(self, original: str, new: str) -> None:
        """
        Replace all instances of a string in the xml of the current method.

        :param original: The string to replace.
        :param new: The string to replace it with.
        """
        if re.search(r"\.\d{8}", new):
            warnings.warn(
                f"The value {new} seems to contain a numerical value with more than 7 "
                "digits after the decimal point. Empower might interpret that wrong."
            )
        self._change_list.append((original, new))

    def undo(self) -> None:
        """Undo the last change made to the method."""
        self._change_list.pop()

    # If this property method is called often, there could be performance issues. In
    # that case, consider cahcing the result with `@functools.lru_cahce(maxsize=1)`. You
    # also need to implement a `__hash__` method and an `__eq__` method for this to
    # work.
    @property
    def current_method(self) -> DataModel:
        """The current method definition, including the changes that have been made."""
        logger.debug(
            "Applying changes to method of type %s to create current method", type(self)
        )
        return self.alter_method(self.original_method, self._change_list)

    def __getitem__(self, key: str) -> str:
        try:
            xml = self.current_method["nativeXml"]
        except KeyError as ex:
            raise KeyError("No xml found in method definition") from ex
        return self.find_value(xml, key)

    def __setitem__(self, key: str, value: str) -> None:
        current_value = self[key]
        self.replace(f"<{key}>{current_value}</{key}>", f"<{key}>{value}</{key}>")

    @staticmethod
    def find_value(xml: str, key: str) -> str:
        """Find the value of a key in an xml from Empower."""
        search_result = re.search(f"<{key}>(.*)</{key}>", xml, re.DOTALL)
        # The re.DOTALL flag ensures that newline charaters are also matched by the dot.
        if not search_result:
            # Consider trying to replace `<` with `&lt` and `>` with `&gt;` and then
            # trying again.
            raise KeyError(f"Could not find key {key}")
        if f"<{key}>" in search_result.groups(1)[0]:
            # Python regex returns the maximum match, so if the key is found multiple
            # times, it will return everything between the first opening tag and the
            # last closing tag. This is not what we want, so we raise an error if this
            # happens.
            raise ValueError(f"Found more than one match for key {key}")
        return search_result.groups(1)[0]

    @staticmethod
    def alter_method(
        original_method: Mapping[str, str], change_list: List[Tuple[str, str]]
    ) -> DataModel:
        """
        Alter the a method definition by applying the changes in the change list.
        """
        method = DataModel(original_method)
        try:
            xml: str = method["nativeXml"]
        except KeyError as ex:
            if len(change_list) > 0:
                raise ValueError(
                    "Cannot apply changes to method, no xml key in method definition."
                ) from ex
            else:
                # If there is no xml key, we can't do anything with the method. But if
                # there are no changes to apply, we can just return the original method.
                return method
        for original, new in change_list:
            num_replaced = xml.count(original)
            if num_replaced == 0:
                warnings.warn(
                    f"Could not find {original} in {method}, no changes made to method."
                )  # Consider trying to replace `<` with `&lt` and `>` with `&gt;` and
                # then trying again.
            else:
                xml = xml.replace(original, new)
                logger.debug(
                    "Replaced %s instances of %s with %s", num_replaced, original, new
                )
        method["nativeXml"] = xml
        return method

    @staticmethod
    def _round(value: Union[str, float], decimal_digits: int = 3) -> str:
        try:
            value = float(value)
        except ValueError:
            logger.debug("Could not convert %s to float, returning as is", value)
            return value
        rounded_value = round(value, decimal_digits)
        if rounded_value != float(value):
            warnings.warn(
                f"Rounding {value} to {rounded_value}, as Empower only "
                f"accepts {decimal_digits} decimal(s)."
            )
        return str(rounded_value)

    def copy(self):
        """Return a copy of the EmpowerModuleMethod."""
        copy = type(self)(self.original_method)
        copy._change_list = self._change_list.copy()
        return copy


class ColumnOvenMethod(EmpowerModuleMethod):
    """
    Class for module methods that have a column temperature.

    Attributes in addition to the ones from EmpowerModuleMethod:

    :ivar column_temperature: The column temperature.

    :meta private:
    """

    column_temperature_key: str

    @property
    def column_temperature(self) -> str:
        """
        The column temperature. If a float is given, it will be rounded to 1 decimal.
        """
        return self[self.column_temperature_key]

    @column_temperature.setter
    def column_temperature(self, value: Union[str, float]) -> None:
        self[self.column_temperature_key] = self._round(value, decimal_digits=1)


class SampleManagerMethod(ColumnOvenMethod):
    """Class for module methods that control a sample manager."""

    column_temperature_key = "ColumnTemperature"

    sample_temperature_key = "SampleTemperature"

    @property
    def sample_temperature(self) -> str:
        """The sample temperature."""
        return self[self.sample_temperature_key]

    @sample_temperature.setter
    def sample_temperature(self, value: Union[str, float]) -> None:
        self[self.sample_temperature_key] = self._round(value, decimal_digits=1)


class ColumnManagerMethod(ColumnOvenMethod):
    """Class for module methods that control a column manager."""

    column_temperature_key = "SetColumnTemperature"


class SolventManagerMethod(EmpowerModuleMethod):
    """
    Parent class for module methods that control a solvent manager. Specific instrument
    types should subclass this class and set the following class attributes:
    valve_tag_prefix, valve_tag_suffix, and solvent_lines.

    Attributes in addition to the ones from EmpowerModuleMethod:
    :ivar valve_position: The current valve position for each solvent line.
    :ivar gradient_table: The gradient table for the method.

    :meta private:
    """

    valve_tag_prefix: str
    valve_tag_suffix: str
    solvent_lines: List[str]

    @property
    def valve_position(self) -> List[str]:
        """
        The current valve position for each solvent line. When setting, the value can be
        a list of strings. Each string should should be of the form `XY`, where `X`
        is the solvent line (A, B, C, D) and `Y` is the position (0-6).
        """
        valve_position_list = [
            line + self[self.valve_tag_prefix + line + self.valve_tag_suffix]
            for line in self.solvent_lines
        ]
        # Consider removing the ones that have position 0,
        # to make QSM methods easier to read.
        return valve_position_list

    def __str__(self):
        return f"{type(self).__name__} with valve positions {self.valve_position}"

    @valve_position.setter
    def valve_position(self, value: List[str]) -> None:
        for position in value:
            if position[0] not in self.solvent_lines:
                raise ValueError(
                    f"Invalid valve position {position}, "
                    f"must start with one of {self.solvent_lines}"
                )
            self[
                self.valve_tag_prefix + position[0] + self.valve_tag_suffix
            ] = position[1:]

    @property
    def gradient_table(self) -> List[Dict[str, str]]:
        """
        The gradient table for the method. It is a list of dicts, one for each row.

        The dicts have the following keys:
          - Time: The time in minutes (or Initial).
          - Flow: The flow in mL/min.
          - CompositionX: The composition of solvent line X (A, B, C, D) in %.
          - Curve: The curve type (Initial, or 1-11, 6 is linear and default).

        When setting, values can be strings or numbers. Floats will be rounded to 3
        decimals, as Empower has problems with too many decimals. The exception is
        value(s) for 'Curve', which is assumed to be integers and will not be rounded.
        """
        gradient_table = []
        e_tree = ET.fromstring(f"<root>{self['GradientTable']}</root>")
        for gradient_row in e_tree:
            if gradient_row.tag != "GradientRow":
                raise ValueError(
                    f"Expected GradientRow, got {gradient_row.tag} instead."
                )
            row_dict = {}
            for field in gradient_row:
                row_dict[field.tag] = field.text
            gradient_table.append(row_dict)
        return gradient_table

    @gradient_table.setter
    def gradient_table(
        self, new_gradient_table: List[Dict[str, Union[str, float, int]]]
    ) -> None:
        for i, gradient_row in enumerate(new_gradient_table[1:]):
            if gradient_row["Time"] == "Initial":
                raise ValueError(
                    f"Time cannot be 'Initial' for row {i+2} of gradient table, "
                    "only for the first row."
                )
            if "Curve" in gradient_row and gradient_row["Curve"] == "Initial":
                raise ValueError(
                    f"Curve cannot be 'Initial' for row {i+2} of gradient table, "
                    "only for the first row."
                )
        if new_gradient_table[0]["Time"] != "Initial":
            if float(new_gradient_table[0]["Time"]) == 0.0:
                logger.debug(
                    "Initial time for gradient table given os %s, changed to 'Initial'",
                    new_gradient_table[0]["Time"],
                )
                new_gradient_table[0]["Time"] = "Initial"
            else:
                raise ValueError(
                    "Initial time should be 'Initial' or 0, "
                    f"got {new_gradient_table[0]['Time']}."
                )
        new_gradient_table[0]["Curve"] = "Initial"
        xml = ET.Element("GradientTable")
        for row in new_gradient_table:
            row_xml = ET.SubElement(xml, "GradientRow")
            curve = row.get("Curve", "6")
            # "6" is linear, which covers 90% of the use cases
            ET.SubElement(row_xml, "Time").text = self._round(row["Time"])
            ET.SubElement(row_xml, "Flow").text = self._round(row["Flow"])
            for line in self.solvent_lines:
                line_name = f"Composition{line}"
                ET.SubElement(row_xml, line_name).text = self._round(row[line_name])
            ET.SubElement(row_xml, "Curve").text = str(curve)
            # Consider validating curve (1-11)
        gradient_xml = ET.tostring(xml, encoding="unicode")
        gradient_xml = gradient_xml.replace("<GradientTable>", "").replace(
            "</GradientTable>", ""
        )  # Stripping root tag, as it is set by __setitem__()
        self["GradientTable"] = gradient_xml


class BSMMethod(SolventManagerMethod):
    """Class for module methods that control a binary solvent manager (BSM)."""

    valve_tag_prefix = "FlowSource"
    valve_tag_suffix = ""
    solvent_lines = ["A", "B"]


class QSMMethod(SolventManagerMethod):
    """Class for module methods that control a quaternary solvent manager (QSM)."""

    valve_tag_prefix = "SolventSelectionValve"
    valve_tag_suffix = "Position"
    solvent_lines = ["A", "B", "C", "D"]
