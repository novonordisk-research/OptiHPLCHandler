from typing import Dict, List, Union

from OptiHPLCHandler import EmpowerHandler, EmpowerInstrumentMethod
from OptiHPLCHandler.applications.empower_implementation.empower_tools import (
    determine_last_high_flow_time,
)
from OptiHPLCHandler.applications.method_generators.add_isocratic_segment import (
    generate_add_isocratic_segment_to_method,
)
from OptiHPLCHandler.applications.method_generators.alter_strong_eluent_pct import (
    generate_altered_strong_eluent_method_pct,
)
from OptiHPLCHandler.applications.method_generators.alter_temperature import (
    generate_altered_temperature_method,
)
from OptiHPLCHandler.applications.method_generators.condense_gradient_table import (
    generate_condense_gradient_table,
)
from OptiHPLCHandler.applications.method_generators.ramp_method import (
    generate_ramp_method,
)
from OptiHPLCHandler.applications.revert_method import revert_method
from OptiHPLCHandler.utils.validate_gradient_table import validate_gradient_table
from OptiHPLCHandler.utils.validate_method_name import (
    make_method_name_string_compatible_with_empower,
)


def _post_and_revert_instrument_methodset_method(
    handler: EmpowerHandler, method: EmpowerInstrumentMethod, original_method_name: str
):
    """
    Post an instrument method and a method set method to Empower not including the
    context manager.
    """
    # Validate method
    validate_gradient_table(method.gradient_table)

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
    settings: dict = None,
):
    if settings is None:
        settings = {
            "temperature_change": 2.5,
            "strong_eluent_change": 1,
            "isocratic_start_times": [15, 30],
            "rampup_time": 10,
            "rampdown_time": 1,
        }

    # own input
    original_method_name = method.method_name

    dict_methods = {}
    dict_methods["input_method"] = {
        "method_name": original_method_name,
        "run_time": method.gradient_table[-1]["Time"],
    }

    with handler:
        # Validate input method
        validate_gradient_table(method.gradient_table)

        # Ramp up method
        generate_ramp_method(
            method=method, ramp_time=settings["rampup_time"], ramp_type="rampup"
        )
        dict_methods["rampup"] = {
            "method_name": method.method_name,
            "run_time": determine_last_high_flow_time(method.gradient_table),
        }

        # post
        _post_and_revert_instrument_methodset_method(
            handler, method, original_method_name
        )

        # Generate scaled gradient condition method
        generate_condense_gradient_table(
            method,
            10,
        )
        dict_methods["scaled"] = {
            "method_name": method.method_name,
            "run_time": determine_last_high_flow_time(method.gradient_table),
        }
        _post_and_revert_instrument_methodset_method(
            handler,
            method,
            original_method_name,
        )

        # Generate altered strong eluent methods
        generate_altered_strong_eluent_method_pct(
            method, settings["strong_eluent_change"]
        )
        dict_methods["plus_strong"] = {
            "method_name": method.method_name,
            "run_time": determine_last_high_flow_time(method.gradient_table),
        }
        _post_and_revert_instrument_methodset_method(
            handler,
            method,
            original_method_name,
        )
        generate_altered_strong_eluent_method_pct(
            method, -settings["strong_eluent_change"]
        )
        dict_methods["minus_strong"] = {
            "method_name": method.method_name,
            "run_time": determine_last_high_flow_time(method.gradient_table),
        }
        _post_and_revert_instrument_methodset_method(
            handler,
            method,
            original_method_name,
        )

        # Generate isocratic start method
        for iteration, isocratic_step in enumerate(
            settings["isocratic_start_times"], start=1
        ):
            generate_add_isocratic_segment_to_method(method, isocratic_step, 0)
            dict_methods[f"iso_start_{iteration}"] = {
                "method_name": method.method_name,
                "run_time": determine_last_high_flow_time(method.gradient_table),
            }
            _post_and_revert_instrument_methodset_method(
                handler,
                method,
                original_method_name,
            )

        # Generate altered temperature method
        generate_altered_temperature_method(method, settings["temperature_change"])
        dict_methods["plus_temp"] = {
            "method_name": method.method_name,
            "run_time": determine_last_high_flow_time(method.gradient_table),
        }
        _post_and_revert_instrument_methodset_method(
            handler,
            method,
            original_method_name,
        )
        generate_altered_temperature_method(method, -settings["temperature_change"])
        dict_methods["minus_temp"] = {
            "method_name": method.method_name,
            "run_time": determine_last_high_flow_time(method.gradient_table),
        }
        _post_and_revert_instrument_methodset_method(
            handler,
            method,
            original_method_name,
        )

        # Generate ramp down method
        generate_ramp_method(
            method=method, ramp_time=settings["rampdown_time"], ramp_type="rampdown"
        )
        dict_methods["rampdown"] = {
            "method_name": method.method_name,
            "run_time": method.gradient_table[-1]["Time"],
        }
        _post_and_revert_instrument_methodset_method(
            handler,
            method,
            original_method_name,
        )

    return dict_methods


def sample_set_namer(method_name: str) -> str:
    return f"{method_name}_robustness"


def get_name_and_run_time(dict_methods_method: dict) -> Union[str, str]:
    return dict_methods_method["method_name"], dict_methods_method["run_time"]


def condition_or_equilibrate_column_sampleset_line(
    column_position: int, dict_methods_method: dict, function: str, runtime: str = None
) -> dict:
    if function not in ["Condition Column", "Equilibrate"]:
        raise ValueError("Function must be 'Condition Column' or 'Equilibrate'")

    dict_output = {
        "Function": function,
        "ColumnPosition": column_position,
    }
    dict_output["Method"], dict_output["RunTime"] = get_name_and_run_time(
        dict_methods_method
    )

    if runtime:
        dict_output["RunTime"] = runtime

    return dict_output


def injection_sampleset_line(
    column_position: str,
    vial_position: str,
    sample_name: str,
    dict_methods_method: dict,
    injection_volume: int,
) -> dict:
    dict_output = {
        "ColumnPosition": column_position,
        "SamplePos": vial_position,
        "InjectionVolume": injection_volume,
        "SampleName": sample_name,
    }
    dict_output["Method"], dict_output["RunTime"] = get_name_and_run_time(
        dict_methods_method
    )

    dict_output["RunTime"] = make_method_name_string_compatible_with_empower(
        dict_output["RunTime"]
    )

    if len(dict_output["SampleName"]) > 30:
        raise ValueError("Sample name too long")

    return dict_output


def post_and_run_experiment(
    handler: EmpowerHandler,
    sample_set_method_name: str,
    sample_list: List[Dict[str, str]],
    plates: Dict[str, str],
    system: str,
    node: str,
    post: bool = False,
    run: bool = False,
) -> None:
    print("Logging in to Empower...")
    with handler:
        print("Log in successful.")

        if post:
            print(f"Posting SampleSet Method {sample_set_method_name}...")
            handler.PostExperiment(
                sample_set_method_name=sample_set_method_name,
                sample_list=sample_list,
                plates=plates,
                audit_trail_message=None,
            )
            print(f"Sample Set Method {sample_set_method_name} posted.")

        else:
            print(f"Sample Set Method {sample_set_method_name} not posted.")

        if run:
            print(f"Running SampleSet Method {sample_set_method_name}...")
            handler.RunExperiment(
                sample_set_method=sample_set_method_name,
                sample_set_name=sample_set_method_name,
                system=system,
                node=node,
            )
            print(f"Sample Set Method {sample_set_method_name} running/queued.")

        else:
            print(f"Sample Set Method {sample_set_method_name} not run.")


def generate_basic_robustness_sampleset(
    dict_methods: dict, input_settings: dict = None
) -> List[dict]:
    # Initialise settings
    if input_settings is None:
        settings = {
            "column_position": ["Position 1"],
            "blank_vial_position": "1:A,1",
            "sample_vial_position": "1:A,2",
            "sample_name": "Sample",
            "injection_volume": 3,
            "linearity_volumes": [0.7, 1, 3, 5, 7, 10],
            "equilibration_time": "10.0",
            "repeat_injections_number": 5,
        }
    else:
        for setting in input_settings:
            settings[setting] = input_settings[setting]

    # Initialisation
    sample_list = []
    column_positions = settings["column_position"]
    blank_vial_position = settings["blank_vial_position"]
    sample_vial_position = settings["sample_vial_position"]
    sample_name = settings["sample_name"]
    injection_volume = settings["injection_volume"]
    linearity_volumes = settings["linearity_volumes"]
    equilibration_time = settings["equilibration_time"]
    repeat_injections_number = settings["repeat_injections_number"]

    for column_position in column_positions:
        # Startup
        sample_list.append(
            condition_or_equilibrate_column_sampleset_line(
                column_position, dict_methods["rampup"], "Condition Column"
            )
        )
        sample_list.append(
            condition_or_equilibrate_column_sampleset_line(
                column_position, dict_methods["scaled"], "Condition Column"
            )
        )
        sample_list.append(
            condition_or_equilibrate_column_sampleset_line(
                column_position,
                dict_methods["input_method"],
                "Equilibrate",
                equilibration_time,
            )
        )

        # Carryover
        sample_list.append(
            injection_sampleset_line(
                column_position,
                blank_vial_position,
                "Pre co blank",
                dict_methods["input_method"],
                injection_volume,
            )
        )
        sample_list.append(
            injection_sampleset_line(
                column_position,
                sample_vial_position,
                sample_name,
                dict_methods["input_method"],
                injection_volume,
            )
        )
        sample_list.append(
            injection_sampleset_line(
                column_position,
                blank_vial_position,
                "Post co blank",
                dict_methods["input_method"],
                injection_volume,
            )
        )

        # Repeat injections
        for i in range(repeat_injections_number):
            sample_list.append(
                injection_sampleset_line(
                    column_position,
                    sample_vial_position,
                    f"{sample_name}_rep{i+1}",
                    dict_methods["input_method"],
                    injection_volume,
                )
            )

        # Linearity
        for volume in linearity_volumes:
            sample_list.append(
                injection_sampleset_line(
                    column_position,
                    sample_vial_position,
                    f"{sample_name}_{volume}uL",
                    dict_methods["input_method"],
                    volume,
                )
            )

        sample_list.append(
            injection_sampleset_line(
                column_position,
                blank_vial_position,
                "Post rep lin blank",
                dict_methods["input_method"],
                injection_volume,
            )
        )

        # +/- strong eluent
        dict_plus_strong_equilibrate = condition_or_equilibrate_column_sampleset_line(
            column_position,
            dict_methods["plus_strong"],
            "Equilibrate",
            equilibration_time,
        )
        sample_list.append(dict_plus_strong_equilibrate)
        dict_plus_strong_injection = injection_sampleset_line(
            column_position,
            sample_vial_position,
            f"{sample_name}_p_str",
            dict_methods["plus_strong"],
            injection_volume,
        )
        sample_list.append(dict_plus_strong_injection)

        dict_minus_strong_equilibrate = condition_or_equilibrate_column_sampleset_line(
            column_position,
            dict_methods["minus_strong"],
            "Equilibrate",
            equilibration_time,
        )
        sample_list.append(dict_minus_strong_equilibrate)
        dict_minus_strong_injection = injection_sampleset_line(
            column_position,
            sample_vial_position,
            f"{sample_name}_m_str",
            dict_methods["minus_strong"],
            injection_volume,
        )
        sample_list.append(dict_minus_strong_injection)

        # Isocratic start
        dict_iso_start_1_equilibrate = condition_or_equilibrate_column_sampleset_line(
            column_position,
            dict_methods["iso_start_1"],
            "Equilibrate",
            equilibration_time,
        )
        sample_list.append(dict_iso_start_1_equilibrate)
        dict_iso_start_1_injection = injection_sampleset_line(
            column_position,
            sample_vial_position,
            f"{sample_name}_iso1",
            dict_methods["iso_start_1"],
            injection_volume,
        )
        sample_list.append(dict_iso_start_1_injection)

        dict_iso_start_2_injection = injection_sampleset_line(
            column_position,
            sample_vial_position,
            f"{sample_name}_iso2",
            dict_methods["iso_start_2"],
            injection_volume,
        )
        sample_list.append(dict_iso_start_2_injection)

        # +/- temperature
        dict_plus_temp_equilibrate = condition_or_equilibrate_column_sampleset_line(
            column_position,
            dict_methods["plus_temp"],
            "Equilibrate",
            equilibration_time,
        )
        sample_list.append(dict_plus_temp_equilibrate)
        dict_plus_temp_injection = injection_sampleset_line(
            column_position,
            sample_vial_position,
            f"{sample_name}_p_temp",
            dict_methods["plus_temp"],
            injection_volume,
        )
        sample_list.append(dict_plus_temp_injection)

        dict_minus_temp_equilibrate = condition_or_equilibrate_column_sampleset_line(
            column_position,
            dict_methods["minus_temp"],
            "Equilibrate",
            equilibration_time,
        )
        sample_list.append(dict_minus_temp_equilibrate)
        dict_minus_temp_injection = injection_sampleset_line(
            column_position,
            sample_vial_position,
            f"{sample_name}_m_temp",
            dict_methods["minus_temp"],
            injection_volume,
        )
        sample_list.append(dict_minus_temp_injection)

        # Rampdown
        dict_rampdown_condition = condition_or_equilibrate_column_sampleset_line(
            column_position, dict_methods["rampdown"], "Condition Column"
        )
        sample_list.append(dict_rampdown_condition)

    return sample_list


def post_run_basic_robustness_test(
    handler, input_method, plates, system, node, post=True, run=False
):
    # generate methods
    dict_methods = generate_basic_robustness_instrument_methods(handler, input_method)

    # generate sample set method
    sample_list = generate_basic_robustness_sampleset(dict_methods)
    sample_set_method_name = sample_set_namer(input_method.method_name)

    # post and run experiment
    post_and_run_experiment(
        handler=handler,
        sample_set_method_name=sample_set_method_name,
        sample_list=sample_list,
        plates=plates,
        system=system,
        node=node,
        post=post,
        run=run,
    )
