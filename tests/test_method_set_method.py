import json
import os
import unittest

from OptiHPLCHandler.empower_methodset_method import EmpowerMethodSetMethod


class TestMethodSetMethod(unittest.TestCase):
    def setUp(self) -> None:
        self.example = {}
        example_folder = "tests\empower_method_examples"
        example_files = os.listdir(example_folder)
        for file in example_files:
            file_path = os.path.join(example_folder, file)
            with open(file_path) as f:
                self.example[file] = json.load(f)

    def test_initialisation_full_response(self):
        for method_definition in self.example.values():
            method = EmpowerMethodSetMethod(method_definition)
            assert isinstance(method, EmpowerMethodSetMethod)

    def test_initialisation_method_definition(self):
        for method_definition in self.example.values():
            method = EmpowerMethodSetMethod(method_definition["results"])
            assert isinstance(method, EmpowerMethodSetMethod)

    def test_original_method(self):
        for method_definition in self.example.values():
            method = EmpowerMethodSetMethod(method_definition)
            assert isinstance(method.original_method, list)
            assert isinstance(method.original_method[0], dict)
            assert method.original_method == method_definition["results"]

    def test_current_method(self):
        method_definition = self.example["response-BSM-PDA-Acq.json"]
        method = EmpowerMethodSetMethod(method_definition)
        original_column_temperature = method.column_oven_list[0].column_temperature
        method.column_oven_list[0].column_temperature = "50.03"
        assert isinstance(method.current_method, list)
        assert isinstance(method.current_method[0], dict)
        assert method.current_method != method_definition["results"]
        assert method.current_method[0]["xml"].count("50.03") == 1
        assert (
            method.current_method[0]["xml"].replace(
                "50.03", original_column_temperature
            )
            == method_definition["results"][0]["modules"][0]["xml"]
        )
