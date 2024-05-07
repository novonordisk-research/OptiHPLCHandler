from typing import Optional

from OptiHPLCHandler import EmpowerInstrumentMethod
from OptiHPLCHandler.utils.validate_method_name import append_truncate_method_name


def generate_altered_temperature_method(
    method: EmpowerInstrumentMethod,
    temperature_delta: float = 2.5,
    suffix: Optional[str] = None,
):
    """
    Generates varied temperature methods based on the given method.

    Args:
        method (EmpowerInstrumentMethod): The base method to generate varied temperature
        methods from.
        temperature_delta (float, optional): The temperature difference to apply to the
        column temperature. Defaults to 2.5.
        post_method (bool, optional): Flag indicating whether to post the generated
        method to Empower. Defaults to False.

    Returns:
        EmpowerInstrumentMethod: The generated method with the updated column
        temperature.

    Raises:
        None
    """

    # Variables
    if suffix is None:
        suffix = "_{:.1f}C".format(temperature_delta)

    # generate method name
    method.method_name = append_truncate_method_name(method.method_name, suffix)

    # change the column temperature
    method.column_temperature = str(
        float(method.column_temperature) + temperature_delta
    )

    return method
