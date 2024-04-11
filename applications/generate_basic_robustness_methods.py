from OptiHPLCHandler import EmpowerHandler, EmpowerInstrumentMethod
from method_generators.rampup_method import generate_rampup_method
from method_generators.alter_strong_eluent_pct import (
    generate_altered_strong_eluent_method_pct,
)
from method_generators.alter_temperature import generate_altered_temperature_method
from method_generators.add_isocratic_start import generate_isocratic_start_method
from method_generators.condense_gradient_table import condense_gradient_table
from revert_method import revert_method


def _post_instrument_methodset_method(
    handler: EmpowerHandler, method: EmpowerInstrumentMethod, original_method_name: str
):
    """
    Post an instrument method and a method set method to Empower not including the context manager.
    """
    handler.PostInstrumentMethod(method)
    method_set_method = {
        "name": method.method_name,
        "instrumentMethod": method.method_name,
    }
    handler.PostMethodSetMethod(method_set_method)

    method = revert_method(method, original_method_name)

    return method


def generate_basic_robustness_instrument_methods(
    handler: EmpowerHandler,
    method: EmpowerInstrumentMethod,
    maintain_wash_pct: bool = True,
):

    TEMPERATURE_CHANGE = 2.5
    STRONG_ELUENT_CHANGE = 1
    ISOCRATIC_START_TIMES = [30, 60]
    RAMPUP_TIME = 10
    ORIGINAL_METHOD_NAME = method.method_name

    dict_methods = {}
    dict_methods["input_method"] = {
        "method_name": ORIGINAL_METHOD_NAME,
        "run_time": method.gradient_table[-1]["Time"],
    }

    with handler:

        # Ramp up method
        generate_rampup_method(method=method, rampup_time=RAMPUP_TIME)
        dict_methods["rampup"] = {
            "method_name": method.method_name,
            "run_time": method.gradient_table[-1]["Time"],
        }
        _post_instrument_methodset_method(handler, method, ORIGINAL_METHOD_NAME)

        # Generate scaled gradient condition method
        condense_gradient_table(method, None, 10, False)
        dict_methods["scaled"] = {
            "method_name": method.method_name,
            "run_time": method.gradient_table[-1]["Time"],
        }
        _post_instrument_methodset_method(
            handler,
            method,
            ORIGINAL_METHOD_NAME,
        )

        # Generate altered strong eluent methods
        generate_altered_strong_eluent_method_pct(
            method, None, STRONG_ELUENT_CHANGE, False, maintain_wash_pct
        )
        dict_methods["plus_strong"] = {
            "method_name": method.method_name,
            "run_time": method.gradient_table[-1]["Time"],
        }
        _post_instrument_methodset_method(
            handler,
            method,
            ORIGINAL_METHOD_NAME,
        )
        generate_altered_strong_eluent_method_pct(
            method, None, -STRONG_ELUENT_CHANGE, False, maintain_wash_pct
        )
        dict_methods["minus_strong"] = {
            "method_name": method.method_name,
            "run_time": method.gradient_table[-1]["Time"],
        }
        _post_instrument_methodset_method(
            handler,
            method,
            ORIGINAL_METHOD_NAME,
        )

        # Generate isocratic start method
        generate_isocratic_start_method(method, None, ISOCRATIC_START_TIMES[0], False)
        dict_methods["iso_start_1"] = {
            "method_name": method.method_name,
            "run_time": method.gradient_table[-1]["Time"],
        }
        _post_instrument_methodset_method(
            handler,
            method,
            ORIGINAL_METHOD_NAME,
        )
        generate_isocratic_start_method(method, None, ISOCRATIC_START_TIMES[1], False)
        dict_methods["iso_start_2"] = {
            "method_name": method.method_name,
            "run_time": method.gradient_table[-1]["Time"],
        }
        _post_instrument_methodset_method(
            handler,
            method,
            ORIGINAL_METHOD_NAME,
        )

        # Generate altered temperature method
        generate_altered_temperature_method(method, None, TEMPERATURE_CHANGE, False)
        dict_methods["plus_temp"] = {
            "method_name": method.method_name,
            "run_time": method.gradient_table[-1]["Time"],
        }
        _post_instrument_methodset_method(
            handler,
            method,
            ORIGINAL_METHOD_NAME,
        )
        generate_altered_temperature_method(method, None, -TEMPERATURE_CHANGE, False)
        dict_methods["minus_temp"] = {
            "method_name": method.method_name,
            "run_time": method.gradient_table[-1]["Time"],
        }
        _post_instrument_methodset_method(
            handler,
            method,
            ORIGINAL_METHOD_NAME,
        )
    return dict_methods
