import json
import os
import unittest

from OptiHPLCHandler.empower_methodset_method import EmpowerMethodSetMethod


class TestMethodSetMethod(unittest.TestCase):
    def setUp(self) -> None:
        self.example = {}
        example_folder = os.path.join("tests", "empower_method_examples")
        example_files = os.listdir(example_folder)
        for file in example_files:
            file_path = os.path.join(example_folder, file)
            with open(file_path) as f:
                self.example[file] = json.load(f)
        self.minimal_definition = {"modules": [{"name": "test", "xml": "test_name"}]}

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

    def test_original_method(self):
        for method_definition in self.example.values():
            method = EmpowerMethodSetMethod(method_definition)
            assert isinstance(method.original_method, dict)
            assert method.original_method == method_definition["results"][0]

    def test_current_method(self):
        method_definition = self.example["response-BSM-PDA-Acq.json"]
        method = EmpowerMethodSetMethod(method_definition)
        original_column_temperature = method.column_oven_list[0].column_temperature
        method.column_oven_list[0].column_temperature = "50.03"
        assert isinstance(method.current_method, dict)
        assert method.current_method != method_definition["results"][0]
        assert method.current_method["modules"][0]["xml"].count("50.03") == 1
        assert (
            method.current_method["modules"][0]["xml"].replace(
                "50.03", original_column_temperature
            )
            == method_definition["results"][0]["modules"][0]["xml"]
        )
        assert method.original_method == method_definition["results"][0]

    def test_get_column_temperature(self):
        method_definition = self.example["response-BSM-PDA-Acq.json"]
        method = EmpowerMethodSetMethod(method_definition)
        assert method.column_temperature == "43.0"

    def test_get_column_temperature_none(self):
        method_definition = self.example["response-BSM-PDA-Acq.json"]["results"][0]
        method_definition["modules"] = method_definition["modules"][1:]
        method = EmpowerMethodSetMethod(method_definition)
        with self.assertRaises(ValueError):
            method.column_temperature

    def test_get_column_temperature_multiple(self):
        method_definition = self.example["response-BSM-PDA-Acq.json"]["results"][0]
        method_definition["modules"].append(method_definition["modules"][0])
        method = EmpowerMethodSetMethod(method_definition)
        assert method.column_temperature == "43.0"

    def test_get_column_temperature_multiple_mismatching(self):
        method_definition = self.example["response-BSM-PDA-Acq.json"]["results"][0]
        method_definition["modules"].append(method_definition["modules"][0])
        method = EmpowerMethodSetMethod(method_definition)
        method.column_oven_list[0].column_temperature = "50.03"
        with self.assertRaises(ValueError):
            method.column_temperature

    def test_set_column_temperature(self):
        method_definition = self.example["response-BSM-PDA-Acq.json"]
        method = EmpowerMethodSetMethod(method_definition)
        new_temperature = method.column_temperature + "1"
        method.column_temperature = new_temperature
        assert method.column_temperature == new_temperature
        assert method.column_oven_list[0].column_temperature == new_temperature

    def test_set_column_temperature_multiple(self):
        method_definition = self.example["response-BSM-PDA-Acq.json"]["results"][0]
        method_definition["modules"].append(method_definition["modules"][0])
        method = EmpowerMethodSetMethod(method_definition)
        method.column_oven_list[0].column_temperature = "5"
        method.column_temperature = "50.03"
        assert method.column_temperature == "50.03"

    def test_set_column_temperature_none(self):
        method_definition = self.example["response-BSM-PDA-Acq.json"]["results"][0]
        method_definition["modules"] = method_definition["modules"][1:]
        method = EmpowerMethodSetMethod(method_definition)
        with self.assertRaises(ValueError):
            method.column_temperature = "50.03"
