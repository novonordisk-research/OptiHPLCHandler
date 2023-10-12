import logging
import re
from typing import Dict, List, Mapping, Tuple, Union
from warnings import warn
from xml.etree import ElementTree as ET

from OptiHPLCHandler.data_types import EmpowerGradientCurve, EmpowerGradientRowModel
from OptiHPLCHandler.data_types import EmpowerInstrumentMethodModel as DataModel

logger = logging.getLogger(__name__)


class InstrumentMethod:
    """
    Generic instrument method class that can be used for any Empower instrument method.
    For specific instrument methods, a subclass should be created that inherits from
    this class.

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

    :attribute original_method: The original method definition.
    :attribute current_method: The current method definition, including the changes that
        have been made.
    """

    def __init__(self, method_definition: Mapping[str, str]):
        """
        Initialize the InstrumentMethod.

        :param method_definition: The method definition from Empower. Should contain at
            least an xml key. If it is not present, the InstrumentMethod can still be
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
        logger.debug("Applying changes to create current method")
        return self.alter_method(self.original_method, self._change_list)

    def __getitem__(self, key: str) -> str:
        try:
            xml = self.current_method["xml"]
        except KeyError as ex:
            raise KeyError("No xml found in method definition") from ex
        return self.find_value(xml, key)

    def __setitem__(self, key: str, value: str) -> None:
        current_value = self[key]
        self.replace(f"<{key}>{current_value}</{key}>", f"<{key}>{value}</{key}>")

    @staticmethod
    def find_value(xml: str, key: str):
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
            xml: str = method["xml"]
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
            logger.debug("Replacing %s with %s", original, new)
            num_replaced = xml.count(original)
            if num_replaced == 0:
                logger.warning(
                    f"Could not find {original} in {method}, no changes made to method."
                )  # Consider trying to replace `<` with `&lt` aand `>` with `&gt;` and
                # then trying again.
            else:
                xml = xml.replace(original, new)
                logger.debug(
                    "Replaced %s instances of %s with %s", num_replaced, original, new
                )
        method["xml"] = xml
        return method


class ColumnOvenMethod(InstrumentMethod):
    """
    Class for instrument methods that have a column temperature.

    :attribute column_temperature: The column temperature.
    """

    TEMPERATURE_KEY: str

    @property
    def column_temperature(self):
        """The column temperature."""
        return self[self.TEMPERATURE_KEY]

    @column_temperature.setter
    def column_temperature(self, value: str) -> None:
        self[self.TEMPERATURE_KEY] = value


class SampleManagerMethod(ColumnOvenMethod):
    """Class for instrument methods that control a sample manager."""

    TEMPERATURE_KEY = "ColumnTemperature"


class SolventManagerMethod(InstrumentMethod):
    """
    Parent class for instrument methods that control a solvent manager.

    Attributes in addition to the ones from InstrumentMethod:
    :attribute valve_position: The current valve position for each solvent line.
    :attribute gradient_table: The gradient table for the method.
    """

    valve_tag_prefix: str
    valve_tag_suffix: str
    solvent_lines: List[str]

    def __init__(self, method_definition: Mapping[str, str]):
        super().__init__(method_definition)
        _gradient_xml = self.find_value(self.original_method["xml"], "GradientTable")
        self.gradient_data = self.interpret_gradient_table(_gradient_xml)

    @property
    def current_method(self) -> DataModel:
        """The current method definition, including the changes that have been made."""
        method = super().current_method
        original_gradient_xml = (
            "<GradientTable>"
            + self.find_value(method["xml"], "GradientTable")
            + "</GradientTable>"
        )
        if original_gradient_xml not in self.original_method["xml"]:
            warn(
                "Gradient table not found in original method, probably because it is "
                "has been manually changed. These changes will be overwritten, and the "
                "gradient table will be set to the one set through the gradient_table "
                "property, or the original, if that has not been changed."
            )
        return self.alter_method(method, [(original_gradient_xml, self.gradient_xml)])

    @property
    def valve_position(self) -> List[str]:
        """The current valve position for each solvent line."""
        valve_position_tags = [
            self.valve_tag_prefix + solvent + self.valve_tag_suffix
            for solvent in self.solvent_lines
        ]
        valve_positions = [
            solvent + self[tag]
            for solvent, tag in zip(self.solvent_lines, valve_position_tags)
        ]
        # Consider removing the ones that have position 0,
        # to make QSM methods easier to read.
        return valve_positions

    def __str__(self):
        return f"{type(self).__name__} with valve positions {self.valve_position}"

    @valve_position.setter
    def valve_position(self, value: Union[str, List[str]]) -> None:
        if isinstance(value, str):
            value = [value]
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
        - Time: The time in minutes.
        - Flow: The flow in mL/min.
        - CompositionX: The composition of solvent line X (A, B, C, D) in %.
        - Curve: The curve type (1-11, 6 is linear and default).
        """
        gradient_table = []
        for row in self.gradient_data:
            row_dict = {"Time": row.time, "Flow": row.flow}
            for solvent, composition in zip(self.solvent_lines, row.composition):
                row_dict[f"Composition{solvent}"] = composition
            row_dict["Curve"] = row.curve.value
            gradient_table.append(row_dict)
        return gradient_table

    @gradient_table.setter
    def gradient_table(self, value: List[Dict[str, str]]) -> None:
        gradient_rows = []
        for row in value:
            curve = row.get("Curve", "6")
            # "6" is linear, which covers 90% of the use cases
            composition = []
            for line in self.solvent_lines:
                composition.append(row[f"Composition{line}"])
            gradient_rows.append(
                EmpowerGradientRowModel(
                    time=row["Time"],
                    flow=row["Flow"],
                    composition=composition,
                    curve=EmpowerGradientCurve(curve),
                )
            )
        self.gradient_data = gradient_rows

    @property
    def gradient_xml(self) -> str:
        """The gradient table as xml for use with Empower API"""
        xml = ET.Element("GradientTable")
        for row in self.gradient_table:
            row_xml = ET.SubElement(xml, "GradientRow")
            for key, value in row.items():
                ET.SubElement(row_xml, key).text = value
        return ET.tostring(xml, encoding="unicode")

    @classmethod
    def interpret_gradient_table(cls, xml: str) -> List[EmpowerGradientRowModel]:
        """Create the internal representation of the gradient table from the xml."""
        gradient_row_list = []
        e_tree = ET.fromstring(f"<root>{xml}</root>")
        for gradient_row in e_tree:
            if gradient_row.tag != "GradientRow":
                raise ValueError(
                    f"Expected GradientRow, got {gradient_row.tag} instead."
                )
            gradient_row_dict = {}
            for field in gradient_row:
                gradient_row_dict[field.tag] = field.text
            composition = []
            for line in cls.solvent_lines:
                composition.append(gradient_row_dict[f"Composition{line}"])
            gradient_row_list.append(
                EmpowerGradientRowModel(
                    time=gradient_row_dict["Time"],
                    flow=gradient_row_dict["Flow"],
                    composition=composition,
                    curve=EmpowerGradientCurve(gradient_row_dict["Curve"]),
                )
            )
        return gradient_row_list


class BSMMethod(SolventManagerMethod):
    """Class for instrument methods that control a binary solvent manager (BSM)."""

    valve_tag_prefix = "FlowSource"
    valve_tag_suffix = ""
    solvent_lines = ["A", "B"]


class QSMMethod(SolventManagerMethod):
    """Class for instrument methods that control a quaternary solvent manager (QSM)."""

    valve_tag_prefix = "SolventSelectionValve"
    valve_tag_suffix = "Position"
    solvent_lines = ["A", "B", "C", "D"]


def instrument_method_factory(method_definition: Mapping[str, str]) -> InstrumentMethod:
    """
    Factory function for creating an InstrumentMethod from a method definition. The
    method definition should contain at least a name key, which is used to determine
    which subclass of InstrumentMethod should be created. If the name key is not present
    or the name is not recognized, a generic InstrumentMethod will be created.
    """
    try:
        if method_definition["name"] in ["rAcquityFTN"]:
            logger.debug("Creating SampleManager")
            return SampleManagerMethod(method_definition)
        elif method_definition["name"] in ["AcquityBSM"]:
            logger.debug("Creating BSM")
            return BSMMethod(method_definition)
        # Add more cases as they are coded
        else:
            logger.debug(
                "Unknown instrument method: %s, creating a generic InstrumentMethod",
                method_definition["name"],
            )  # The error is always caught, so we use the debug level here.
            raise ValueError(f"Unknown instrument method: {method_definition['name']}")
    except (KeyError, ValueError) as e:
        if isinstance(e, KeyError):
            # If the name key is not present, we don't know what to do with it, but we
            # can still create a generic InstrumentMethod and just return that.
            logger.debug("KeyError: %s, creating a generic InstrumentMethod", e)
        return InstrumentMethod(method_definition)
