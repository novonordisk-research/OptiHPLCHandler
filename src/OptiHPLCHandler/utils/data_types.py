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
        if self.mutable:
            return super().__setitem__(__key, __value)
        raise TypeError("Object is immutable")


class EmpowerModuleMethodModel(OptiDict):
    pass


class EmpowerInstrumentMethodModel(OptiDict):
    pass
