from datetime import datetime
from enum import Enum
from typing import Any, List, NamedTuple


class Eluent(NamedTuple):
    """Class for eluent"""

    Position: str
    """Position of the eluent (A,B,C,D,A1,A2,B1,B2,D1,D2,D3,D4,D5,D6)"""
    Name: str
    """Name of the eluent"""


class HPLCSetup(NamedTuple):
    """Class for HPLC setup"""

    name: str
    """Name of the HPLC setup"""
    ColumnList: List[str]
    """List of columns"""
    EluentList: List[Eluent]
    """List of eluents"""
    PlateTypeList: List[str]
    """List of plate types"""
    FlowCell: str
    """The installed flow cell"""


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


class Sample(NamedTuple):
    """Class for one Sample"""

    Method: str
    """ Name of the method to use """
    SamplePos: str
    """Position of the sample"""
    SampleName: str
    """Name of the sample"""
    SampleType: SampleType
    """Type of the sample"""
    InjectionVolume: float
    """Volume of the injection"""
    OtherFields: List[NamedTuple]
    """Other fields to be set for the Sample, e.g. dilution factor, or custom fields"""


class HplcResult(NamedTuple):
    """Class for result of one Sample"""

    StartTime: datetime
    """When the Sample is expected to be or was started"""
    EndTime: datetime
    """When the Sample is expected to be or was ended"""
    PerformedExperiment: Sample
    """The Sample that was performed"""
    Data: str
    """Reference to where the sdata can be found"""


class DataField(NamedTuple):
    """Class for data field"""

    Name: str
    """Name of the data field"""
    Value: str
    """Value of the data field"""


class OptiDict(dict):
    """Class for Empower instrument method"""

    def __init__(self, *args, mutable: bool = True, **kwargs):
        """
        Initialize the EmpowerInstrumentMethod.

        :param mutable: Whether the object is mutable. If False, an error will be raised
            when trying to modify the object.
        """
        super().__init__(*args, **kwargs)
        self.mutable = mutable

    def __setitem__(self, __key: Any, __value: Any) -> None:
        if self.mutable:
            return super().__setitem__(__key, __value)
        raise TypeError("Object is immutable")


class EmpowerInstrumentMethodModel(OptiDict):
    pass


class EmpowerMethodSetMethodModel(OptiDict):
    pass


class EmpowerGradientCurve(Enum):
    ONE = "1"
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    ELEVEN = "11"

    def __str__(self):
        return self.value
        # This allows for smooth use in f strings


class EmpowerGradientRowModel(NamedTuple):
    time: str
    flow: str
    composition: List[str]
    curve: EmpowerGradientCurve
