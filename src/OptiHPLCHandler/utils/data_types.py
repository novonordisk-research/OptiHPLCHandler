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
        porosity: float = 0.5,
        name: str = "",
    ):
        self.name = name

        # find equilibration time and cleaning time from column length, diameter, and porosity # noqa E501
        # assign


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
