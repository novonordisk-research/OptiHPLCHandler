from typing import Any


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
