from OptiHPLCHandler import EmpowerInstrumentMethod, EmpowerHandler
from empower_implementation.empower_tools import (
    truncate_method_name,
    post_instrument_methodset_method,
)


def generate_altered_temperature_method(
    method: EmpowerInstrumentMethod,
    handler: EmpowerHandler = None,
    temperature_delta: float = 2.5,
    post_method: bool = False,
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
    SUFFIX = "_{:.1f}C".format(temperature_delta)

    # generate method name
    method.method_name = truncate_method_name(method.method_name, SUFFIX)

    # change the column temperature
    method.column_temperature = str(
        float(method.column_temperature) + temperature_delta
    )

    # Optionally posts the method to Empower
    if post_method:
        post_instrument_methodset_method(handler, method)

    return method
