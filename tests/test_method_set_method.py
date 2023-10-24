import json
import os
import unittest

from OptiHPLCHandler.empower_instrument_method import SolventManagerMethod
from OptiHPLCHandler.empower_methodset_method import EmpowerMethodSetMethod


def get_example_file_dict() -> dict:
    """
    Get an example file from the empower_method_examples folder.

    :param file_name: The name of the example file.
    """
    example = {}
    example_folder = os.path.join("tests", "empower_method_examples")
    example_files = os.listdir(example_folder)
    for file in example_files:
        file_path = os.path.join(example_folder, file)
        with open(file_path) as f:
            example[file] = json.load(f)
    return example


class TestMethodSetMethod(unittest.TestCase):
    def setUp(self) -> None:
        self.example = get_example_file_dict()
        self.minimal_definition = {
            "methodName": "test_method",
            "modules": [{"name": "test", "nativeXml": "test_name"}],
        }

    def test_initialisation_full_response(self):
        for method_definition in self.example.values():
            method = EmpowerMethodSetMethod(method_definition)
            assert isinstance(method, EmpowerMethodSetMethod)
            assert len(method.instrument_method_list) == len(
                method_definition["results"][0]["modules"]
            )

    def test_initialisation_method_definition(self):
        for method_definition in self.example.values():
            method = EmpowerMethodSetMethod(method_definition["results"][0])
            assert isinstance(method, EmpowerMethodSetMethod)
            assert len(method.instrument_method_list) == len(
                method_definition["results"][0]["modules"]
            )

    def test_initialisation_multiple_methods(self):
        method_definition = self.example["response-BSM-PDA-Acq.json"]
        method_definition["results"].append(method_definition["results"][0])
        with self.assertRaises(ValueError):
            EmpowerMethodSetMethod(method_definition)

    def test_original_method(self):
        for method_definition in self.example.values():
            method = EmpowerMethodSetMethod(method_definition)
            assert isinstance(method.original_method, dict)
            assert method.original_method == method_definition["results"][0]

    def test_original_method_immutable(self):
        method = EmpowerMethodSetMethod(self.minimal_definition)
        with self.assertRaises(TypeError):
            method.original_method["modules"] = "new"
        with self.assertRaises(TypeError):
            method.original_method["new_key"] = "new_value"

    def test_current_method(self):
        method_definition = self.example["response-BSM-PDA-Acq.json"]
        method = EmpowerMethodSetMethod(method_definition)
        original_column_temperature = method.column_oven_method_list[
            0
        ].column_temperature
        method.column_oven_method_list[0].column_temperature = "50.03"
        assert isinstance(method.current_method, dict)
        assert method.current_method != method_definition["results"][0]
        assert method.current_method["modules"][0]["nativeXml"].count("50.03") == 1
        assert (
            method.current_method["modules"][0]["nativeXml"].replace(
                "50.03", original_column_temperature
            )
            == method_definition["results"][0]["modules"][0]["nativeXml"]
        )
        assert method.original_method == method_definition["results"][0]


class TestColumnTemperature(unittest.TestCase):
    def setUp(self) -> None:
        self.example = get_example_file_dict()

    def test_get(self):
        method_definition = self.example["response-BSM-PDA-Acq.json"]
        method = EmpowerMethodSetMethod(method_definition)
        assert method.column_temperature == "43.0"

    def test_get_none(self):
        method_definition = self.example["response-BSM-PDA-Acq.json"]["results"][0]
        method_definition["modules"] = method_definition["modules"][1:]
        method = EmpowerMethodSetMethod(method_definition)
        with self.assertRaises(ValueError):
            method.column_temperature

    def test_get_multiple(self):
        method_definition = self.example["response-BSM-PDA-Acq.json"]["results"][0]
        method_definition["modules"].append(method_definition["modules"][0])
        method = EmpowerMethodSetMethod(method_definition)
        assert method.column_temperature == "43.0"

    def test_get_multiple_mismatching(self):
        method_definition = self.example["response-BSM-PDA-Acq.json"]["results"][0]
        method_definition["modules"].append(method_definition["modules"][0])
        method = EmpowerMethodSetMethod(method_definition)
        method.column_oven_method_list[0].column_temperature = "50.03"
        with self.assertRaises(ValueError):
            method.column_temperature

    def test_set(self):
        method_definition = self.example["response-BSM-PDA-Acq.json"]
        method = EmpowerMethodSetMethod(method_definition)
        new_temperature = method.column_temperature + "1"
        method.column_temperature = new_temperature
        assert method.column_temperature == new_temperature
        assert method.column_oven_method_list[0].column_temperature == new_temperature

    def test_set_multiple(self):
        method_definition = self.example["response-BSM-PDA-Acq.json"]["results"][0]
        method_definition["modules"].append(method_definition["modules"][0])
        method = EmpowerMethodSetMethod(method_definition)
        method.column_oven_method_list[0].column_temperature = "5"
        method.column_temperature = "50.03"
        assert method.column_temperature == "50.03"

    def test_set_none(self):
        method_definition = self.example["response-BSM-PDA-Acq.json"]["results"][0]
        method_definition["modules"] = method_definition["modules"][1:]
        method = EmpowerMethodSetMethod(method_definition)
        with self.assertRaises(ValueError):
            method.column_temperature = "50.03"


class TestSolventManager(unittest.TestCase):
    def setUp(self) -> None:
        self.example = get_example_file_dict()
        self.bsm_example = self.example["response-BSM-PDA-Acq.json"]

    def test_init(self):
        method = EmpowerMethodSetMethod(self.bsm_example)
        assert method.solvent_handler_method is not None
        assert isinstance(method.solvent_handler_method, SolventManagerMethod)

    def test_init_none(self):
        method_definition = self.bsm_example["results"][0]
        method_definition["modules"] = [method_definition["modules"][0]]
        method = EmpowerMethodSetMethod(method_definition)
        assert method.solvent_handler_method is None

    def test_init_multiple(self):
        method_definition = self.bsm_example["results"][0]
        method_definition["modules"].append(method_definition["modules"][1])
        with self.assertRaises(ValueError):
            EmpowerMethodSetMethod(method_definition)

    def test_get_gradient_table(self):
        method = EmpowerMethodSetMethod(self.bsm_example)
        gradient_table = method.gradient_table
        assert isinstance(gradient_table, list)
        assert isinstance(gradient_table[0], dict)

    def test_get_gradient_table_none(self):
        method_definition = self.bsm_example["results"][0]
        method_definition["modules"] = [method_definition["modules"][0]]
        method = EmpowerMethodSetMethod(method_definition)
        with self.assertRaises(ValueError):
            method.gradient_table

    def test_set_gradient_table(self):
        method = EmpowerMethodSetMethod(self.bsm_example)
        gradient_table = method.gradient_table
        assert gradient_table[0]["Flow"] != "0.1"
        assert (
            "<Flow>0.1</Flow>" not in method.current_method["modules"][1]["nativeXml"]
        )
        gradient_table[0]["Flow"] = "0.1"
        method.gradient_table = gradient_table
        assert method.gradient_table[0]["Flow"] == "0.1"
        assert "<Flow>0.1</Flow>" in method.current_method["modules"][1]["nativeXml"]

    def test_set_gradient_table_none(self):
        method_definition = self.bsm_example["results"][0]
        method_definition["modules"] = [method_definition["modules"][0]]
        method = EmpowerMethodSetMethod(method_definition)
        with self.assertRaises(ValueError):
            method.gradient_table = [{"Flow": "0.1"}]


class TestValvePosition(unittest.TestCase):
    def setUp(self) -> None:
        self.example = get_example_file_dict()
        self.bsm_example = self.example["response-BSM-PDA-Acq.json"]

    def test_get(self):
        method = EmpowerMethodSetMethod(self.bsm_example)
        assert method.valve_position == ["A1", "B1"]

    def test_get_none(self):
        method_definition = self.bsm_example["results"][0]
        method_definition["modules"] = [method_definition["modules"][0]]
        method = EmpowerMethodSetMethod(method_definition)
        with self.assertRaises(ValueError):
            method.valve_position

    def test_set(self):
        method = EmpowerMethodSetMethod(self.bsm_example)
        method.valve_position = "A2"
        assert method.valve_position == ["A2", "B1"]
        assert (
            "<FlowSourceA>2</FlowSourceA>"
            in method.current_method["modules"][1]["nativeXml"]
        )
        assert (
            "<FlowSourceB>1</FlowSourceB>"
            in method.current_method["modules"][1]["nativeXml"]
        )
        method.valve_position = ["A7", "B5"]
        assert method.valve_position == ["A7", "B5"]
        assert (
            "<FlowSourceA>7</FlowSourceA>"
            in method.current_method["modules"][1]["nativeXml"]
        )
        assert (
            "<FlowSourceB>5</FlowSourceB>"
            in method.current_method["modules"][1]["nativeXml"]
        )

    def test_set_none(self):
        method_definition = self.bsm_example["results"][0]
        method_definition["modules"] = [method_definition["modules"][0]]
        method = EmpowerMethodSetMethod(method_definition)
        with self.assertRaises(ValueError):
            method.valve_position = "A2"
        with self.assertRaises(ValueError):
            method.valve_position = ["A2", "B1"]

    def test_method_name(self):
        method = EmpowerMethodSetMethod(self.bsm_example)
        assert method.method_name == "AcquityBSMPDA"
        method.method_name = "new_name"
        assert method.method_name == "new_name"
        assert method.current_method["methodName"] == "new_name"