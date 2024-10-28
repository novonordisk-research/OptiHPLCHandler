from dataclasses import dataclass
from enum import Enum
from typing import Any


@dataclass
class Sample:
    name: str
    sample_position: str
    injection_volume: float


@dataclass
class ColumnOptions:
    name: str
    equilibration_time: float
    cleaning_time: float

    def __init__(
        self,
        length: float = 150,
        diameter: float = 2.1,
        flow_rate: float = 0.3,
        # porosity: float = 0.5,  # needed?
        name: str = "",
    ):
        self.name = name
        self._equilibration_column_volumes = 4.2
        self._cleaning_column_volumes = 1.2
        self._column_info_table = [
            {
                "column_diameter_mm": 1.0,
                "column_length_mm": 30,
                "column_volume_ml": None,
            },
            {
                "column_diameter_mm": 2.1,
                "column_length_mm": 30,
                "column_volume_ml": 0.1,
            },
            {
                "column_diameter_mm": 3.0,
                "column_length_mm": 30,
                "column_volume_ml": 0.2,
            },
            {
                "column_diameter_mm": 1.0,
                "column_length_mm": 50,
                "column_volume_ml": 0.04,
            },
            {
                "column_diameter_mm": 2.1,
                "column_length_mm": 50,
                "column_volume_ml": 0.2,
            },
            {
                "column_diameter_mm": 3.0,
                "column_length_mm": 50,
                "column_volume_ml": 0.4,
            },
            {
                "column_diameter_mm": 1.0,
                "column_length_mm": 100,
                "column_volume_ml": 0.08,
            },
            {
                "column_diameter_mm": 2.1,
                "column_length_mm": 100,
                "column_volume_ml": 0.4,
            },
            {
                "column_diameter_mm": 3.0,
                "column_length_mm": 100,
                "column_volume_ml": 0.8,
            },
            {
                "column_diameter_mm": 1.0,
                "column_length_mm": 150,
                "column_volume_ml": 0.12,
            },
            {
                "column_diameter_mm": 2.1,
                "column_length_mm": 150,
                "column_volume_ml": 0.5,
            },
            {
                "column_diameter_mm": 3.0,
                "column_length_mm": 150,
                "column_volume_ml": 1.0,
            },
        ]
        # calculate equilibration and cleaning times
        self._column_volume_ml = [
            x["column_volume_ml"]
            for x in self._column_info_table
            if x["column_diameter_mm"] == diameter and x["column_length_mm"] == length
        ][0]
        self.equilibration_time = round(
            float(
                self._column_volume_ml * self._equilibration_column_volumes / flow_rate
            ),
            2,
        )
        self.cleaning_time = round(
            float(self._column_volume_ml * self._cleaning_column_volumes / flow_rate), 2
        )


class SampleType(Enum):
    """Class for sample type"""

    UNKNOWN = "Unknown"
    STANDARD = "Standard"
    BROADSTANDARD = "Broad Standard"
    BROADUNKNOWN = "Broad Unknown"
    NARROWSTANDARD = "Narrow Standard"
    NARROWUNKNOWN = "Narrow Unknown"
    CONTROL = "Control"
    RFINTERNALSTANDARD = "RF Internal Standard"


class OptiDict(dict):
    """Data class for OptiHPLC data types"""

    def __init__(self, *args, mutable: bool = True, **kwargs):
        """
        Initialize a data clas object.

        :param mutable: Whether the object is mutable. If False, an error will be raised
            when trying to modify the object.
        """
        super().__init__(*args, **kwargs)
        self.mutable = mutable

    def __setitem__(self, __key: Any, __value: Any) -> None:
        if getattr(self, "mutable", True):
            # un-pickling does not call __init__, so mutable is not set when unpickling
            # Therefore, we need to allow for mutable not being set
            return super().__setitem__(__key, __value)
        raise TypeError("Object is immutable")


class EmpowerModuleMethodModel(OptiDict):
    pass


class EmpowerInstrumentMethodModel(OptiDict):
    pass
