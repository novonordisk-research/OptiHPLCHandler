from typing import Optional

from src.OptiHPLCHandler import EmpowerHandler, EmpowerInstrumentMethod
from src.OptiHPLCHandler.utils.data_types import ColumnOptions, Sample


class ConditionSet:
    def __init__(
        self,
        column_position: str,
        column_options: ColumnOptions,
        valve: dict,  # dataclass? {"strong": "D4", "weak":"A"}
        samples: list[Sample],
        plate_type: str,
        instrument_method: EmpowerInstrumentMethod,
        # add optional things that default as None here
        column_temperature: Optional[float] = None,
    ):
        # self.name = name? construct with conditions
        self.column_position = column_position
        self.column_options = column_options
        self.valve = valve
        self.samples = samples
        self.plate_type = plate_type
        self.instrument_method = instrument_method
        self.column_temperature = column_temperature

    def get_rampup_method(self, valve):
        pass

    def get_shutdown_method(self, valve):
        pass

    def get_cleaning_method(self, valve):
        pass

    def post_instrument_methods(
        self, handler: EmpowerHandler, include_extra: bool = False
    ):
        # posts instrument and method set methods (of the same name)
        pass

    @property
    def initialise_column_sample_set(self) -> list[dict]:
        # ramp up and preclean
        # use the get_rampup_method and get_cleaning_method methods
        pass

    @property
    def condition_set_sample_injections(self) -> list[dict]:
        # sets up injections for each sample
        pass

    @property
    def post_run_column_clean_sample_set(self) -> list[dict]:
        # cleans each column position
        pass

    @property
    def shutdown_column_sample_set(self) -> list[dict]:
        # shuts down lamp and temp on all columns (one line in sample set at end)
        pass
