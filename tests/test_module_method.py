import json
import os
import unittest
import warnings

from OptiHPLCHandler.empower_module_method import (
    BSMMethod,
    ColumnManagerMethod,
    ColumnOvenMethod,
    EmpowerModuleMethod,
    QSMMethod,
    SampleManagerMethod,
    module_method_factory,
)


def load_example_files() -> dict:
    example = {}
    example_folder = os.path.join("tests", "empower_method_examples")
    example_files = os.listdir(example_folder)
    for file in example_files:
        file_path = os.path.join(example_folder, file)
        with open(file_path) as f:
            example[file] = json.load(f)
    return example


class TestModuleMethodFactory(unittest.TestCase):
    def setUp(self) -> None:
        self.example = load_example_files()
        self.example_definition = self.example["response-BSM-PDA-Acq.json"]["results"][
            0
        ]["modules"][2]

    def test_sample_manager(self):
        minimal_definition = {"name": "rAcquityFTN"}
        module_method = module_method_factory(minimal_definition)
        assert isinstance(module_method, SampleManagerMethod)
        example_definition = self.example["response-BSM-PDA-Acq.json"]["results"][0][
            "modules"
        ][0]
        module_method = module_method_factory(example_definition)
        assert isinstance(module_method, SampleManagerMethod)

    def test_column_manager(self):
        minimal_definition = {"name": "ACQ-CM"}
        module_method = module_method_factory(minimal_definition)
        assert isinstance(module_method, ColumnManagerMethod)
        example_definition = self.example["response-BSM-TUV-CM-Acq.json"]["results"][0][
            "modules"
        ][3]
        module_method = module_method_factory(example_definition)
        assert isinstance(module_method, ColumnManagerMethod)

    def test_module_method(self):
        minimal_definition = {"name": "none_of_the_above"}
        module_method = module_method_factory(minimal_definition)
        assert isinstance(module_method, EmpowerModuleMethod)
        # This is a PDA, we do not have specific classes for detectors
        module_method = module_method_factory(self.example_definition)
        assert isinstance(module_method, EmpowerModuleMethod)

    def test_unknown(self):
        # Verify that an unknown module method will be returned as a generic
        # EmpowerModuleMethod
        minimal_definition = {}
        module_method = module_method_factory(minimal_definition)
        assert isinstance(module_method, EmpowerModuleMethod)


class TestModuleMethod(unittest.TestCase):
    def setUp(self) -> None:
        self.example = load_example_files()
        self.example_definition = self.example["response-BSM-PDA-Acq.json"]["results"][
            0
        ]["modules"][2]

    def test_original_method_immutable(self):
        minimal_definition = {"name": "test", "nativeXml": "old"}
        module_method = module_method_factory(minimal_definition)
        with self.assertRaises(TypeError):
            module_method.original_method["nativeXml"] = "new"
        with self.assertRaises(TypeError):
            module_method.original_method["new_key"] = "new_value"

    def test_module_method_replace(self):
        minimal_definition = {"name": "test", "nativeXml": "old"}
        module_method = module_method_factory(minimal_definition)
        module_method.replace("old", "new")
        assert module_method.current_method["nativeXml"] == "new"
        assert module_method.original_method["nativeXml"] == "old"

    def test_module_method_replace_multiple(self):
        minimal_definition = {"name": "test", "nativeXml": "old"}
        module_method = module_method_factory(minimal_definition)
        module_method.replace("old", "new")
        assert module_method.current_method["nativeXml"] == "new"
        module_method.replace("new", "newer")
        assert module_method.current_method["nativeXml"] == "newer"
        assert module_method.original_method["nativeXml"] == "old"

    def test_module_method_undo(self):
        minimal_definition = {"name": "test", "nativeXml": "old"}
        module_method = module_method_factory(minimal_definition)
        module_method.replace("old", "new")
        assert module_method.current_method["nativeXml"] == "new"
        module_method.replace("new", "newer")
        assert module_method.current_method["nativeXml"] == "newer"
        module_method.undo()
        assert module_method.current_method["nativeXml"] == "new"
        module_method.undo()
        assert module_method.current_method["nativeXml"] == "old"
        with self.assertRaises(IndexError):
            module_method.undo()

    def test_module_method_replace_no_xml_no_changes(self):
        minimal_definition = {"name": "test"}
        module_method = module_method_factory(minimal_definition)
        assert module_method.original_method == minimal_definition

    def test_module_method_replace_no_xml_changes(self):
        minimal_definition = {"name": "test"}
        module_method = module_method_factory(minimal_definition)
        module_method.replace("old", "new")
        with self.assertRaises(ValueError):
            module_method.current_method

    def test_module_method_getitem(self):
        minimal_definition = {"name": "test", "nativeXml": "<a>value</a>"}
        module_method = module_method_factory(minimal_definition)
        assert module_method["a"] == "value"
        module_method = module_method_factory(self.example_definition)
        assert module_method["StartWavelength"] == "210"

    def test_module_method_getitem_no_xml(self):
        minimal_definition = {"name": "test"}
        module_method = module_method_factory(minimal_definition)
        with self.assertRaises(KeyError):
            module_method["a"]

    def test_module_method_getitem_no_key(self):
        minimal_definition = {"name": "test", "nativeXml": "<a>value</a>"}
        module_method = module_method_factory(minimal_definition)
        with self.assertRaises(KeyError):
            module_method["b"]
        module_method = module_method_factory(self.example_definition)
        with self.assertRaises(KeyError):
            module_method["not_exisiting_key"]

    def test_module_method_getitem_more_occurences(self):
        minimal_definition = {"name": "test", "nativeXml": "<a>value</a><a>value2</a>"}
        module_method = module_method_factory(minimal_definition)
        with self.assertRaises(ValueError):
            module_method["a"]

    def test_module_method_setitem(self):
        minimal_definition = {"name": "test", "nativeXml": "<a>value</a>"}
        module_method = module_method_factory(minimal_definition)
        module_method["a"] = "new_value"
        assert module_method.current_method["nativeXml"] == "<a>new_value</a>"
        assert module_method.original_method["nativeXml"] == "<a>value</a>"
        assert module_method["a"] == "new_value"
        module_method = module_method_factory(self.example_definition)
        module_method["StartWavelength"] = "211"
        assert (
            "<StartWavelength>210</StartWavelength>"
            in module_method.original_method["nativeXml"]
        )
        assert (
            "<StartWavelength>211</StartWavelength>"
            in module_method.current_method["nativeXml"]
        )
        assert module_method["StartWavelength"] == "211"

    def test_warning_too_many_decimals(self):
        # Empower sometimes gives the wrong values is more than 10 decimals are given.
        minimal_definition = {"name": "test", "nativeXml": "<a>value</a>"}
        module_method = module_method_factory(minimal_definition)
        with self.assertWarns(UserWarning):
            module_method["a"] = "0.123456789101112"
        with self.assertWarns(UserWarning):
            module_method["a"] = 0.123456789101112
        # Assert that mno warning is raised with 6 decimals
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            module_method["a"] = 0.123456
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            module_method["a"] = "0.123456"


class TestColumnOvens(unittest.TestCase):
    def setUp(self) -> None:
        self.example = load_example_files()
        self.example_definition = self.example["response-BSM-PDA-Acq.json"]["results"][
            0
        ]["modules"][0]

    def test_sample_manager_get_temperature(self):
        minimal_definition = {
            "name": "rAcquityFTN",
            "nativeXml": "<ColumnTemperature>43.0</ColumnTemperature>",
        }
        module_method: ColumnOvenMethod = module_method_factory(minimal_definition)
        assert isinstance(module_method, ColumnOvenMethod)
        assert module_method.column_temperature == "43.0"
        module_method = module_method_factory(self.example_definition)
        assert module_method.column_temperature == "43.0"

    def test_sample_manager_set_temperature(self):
        minimal_definition = {
            "name": "rAcquityFTN",
            "nativeXml": "<ColumnTemperature>43.0</ColumnTemperature>",
        }
        module_method: ColumnOvenMethod = module_method_factory(minimal_definition)
        module_method.column_temperature = "44.0"
        assert (
            module_method.original_method["nativeXml"]
            == "<ColumnTemperature>43.0</ColumnTemperature>"
        )
        assert (
            module_method.current_method["nativeXml"]
            == "<ColumnTemperature>44.0</ColumnTemperature>"
        )
        assert module_method.column_temperature == "44.0"
        module_method = module_method_factory(self.example_definition)
        module_method.column_temperature = "44.0"
        assert (
            "<ColumnTemperature>43.0</ColumnTemperature>"
            in module_method.original_method["nativeXml"]
        )
        assert (
            "<ColumnTemperature>44.0</ColumnTemperature>"
            in module_method.current_method["nativeXml"]
        )
        assert module_method.column_temperature == "44.0"

    def test_column_manager_get_temperature(self):
        minimal_definition = {
            "name": "ACQ-CM",
            "nativeXml": "<SetColumnTemperature>43.0</SetColumnTemperature>",
        }
        module_method: ColumnOvenMethod = module_method_factory(minimal_definition)
        assert isinstance(module_method, ColumnOvenMethod)
        assert module_method.column_temperature == "43.0"

    def test_column_manager_set_temperature(self):
        minimal_definition = {
            "name": "ACQ-CM",
            "nativeXml": "<SetColumnTemperature>43.0</SetColumnTemperature>",
        }
        module_method: ColumnOvenMethod = module_method_factory(minimal_definition)
        module_method.column_temperature = "44.0"
        assert (
            module_method.original_method["nativeXml"]
            == "<SetColumnTemperature>43.0</SetColumnTemperature>"
        )
        assert (
            module_method.current_method["nativeXml"]
            == "<SetColumnTemperature>44.0</SetColumnTemperature>"
        )
        assert module_method.column_temperature == "44.0"

    def test_rounding(self):
        minimal_definition = {
            "name": "ACQ-CM",
            "nativeXml": "<SetColumnTemperature>43.0</SetColumnTemperature>",
        }
        module_method: ColumnOvenMethod = module_method_factory(minimal_definition)
        module_method.column_temperature = 100 / 3
        assert (
            module_method.current_method["nativeXml"]
            == "<SetColumnTemperature>33.3</SetColumnTemperature>"
        )
        assert module_method.column_temperature == "33.3"
        module_method.column_temperature = 40.06
        assert module_method.column_temperature == "40.1"
        # Rounding, not concatenating


class testQSMMethod(unittest.TestCase):
    def setUp(self) -> None:
        qsm_method_list = [
            definition["results"][0]["modules"]
            for name, definition in load_example_files().items()
            if "QSM" in name
        ]  # Finding all instrument method definitions that controls a QSM
        for i, qsm_method in enumerate(qsm_method_list):
            qsm_method_list[i] = [
                module for module in qsm_method if module["name"] == "rAcquityQSM"
            ][0]
        # Finding the QSM module method in the instrument method definition
        self.qsm_method_list = qsm_method_list
        self.minimal_definition = {
            "name": "rAcquityQSM",
            "nativeXml": (
                "<SolventSelectionValveAPosition>0</SolventSelectionValveAPosition>"
                "<SolventSelectionValveBPosition>0</SolventSelectionValveBPosition>"
                "<SolventSelectionValveCPosition>0</SolventSelectionValveCPosition>"
                "<SolventSelectionValveDPosition>5</SolventSelectionValveDPosition>"
                "<GradientTable>"
                "<GradientRow>"
                "<Time>Initial</Time><Flow>1.5</Flow>"
                "<CompositionA>25.0</CompositionA>"
                "<CompositionB>25.0</CompositionB>"
                "<CompositionC>25.0</CompositionC>"
                "<CompositionD>25.0</CompositionD>"
                "<Curve>Initial</Curve>"
                "</GradientRow>"
                "</GradientTable>"
            ),
        }
        self.medium_definition = {
            "name": "rAcquityQSM",
            "nativeXml": (
                "<SolventSelectionValveAPosition>0</SolventSelectionValveAPosition>"
                "<SolventSelectionValveBPosition>0</SolventSelectionValveBPosition>"
                "<SolventSelectionValveCPosition>0</SolventSelectionValveCPosition>"
                "<SolventSelectionValveDPosition>5</SolventSelectionValveDPosition>"
                "<GradientTable>"
                "<GradientRow>"
                "<Time>Initial</Time><Flow>1.5</Flow>"
                "<CompositionA>25.0</CompositionA>"
                "<CompositionB>25.0</CompositionB>"
                "<CompositionC>25.0</CompositionC>"
                "<CompositionD>25.0</CompositionD>"
                "<Curve>Initial</Curve>"
                "</GradientRow>"
                "<GradientRow>"
                "<Time>69</Time><Flow>0.69</Flow>"
                "<CompositionA>10.0</CompositionA>"
                "<CompositionB>10.0</CompositionB>"
                "<CompositionC>10.0</CompositionC>"
                "<CompositionD>70.0</CompositionD>"
                "<Curve>6</Curve>"
                "</GradientRow>"
                "</GradientTable>"
            ),
        }

    def test_factory(self):
        module_method = module_method_factory(self.minimal_definition)
        assert isinstance(module_method, QSMMethod)

        module_method = module_method_factory(self.medium_definition)
        assert isinstance(module_method, QSMMethod)

        for qsm_method in self.qsm_method_list:
            qsm = module_method_factory(qsm_method)
            assert isinstance(qsm, QSMMethod)

    def test_valve_position(self):
        module_method = QSMMethod(self.minimal_definition)
        assert module_method.valve_position == ["A0", "B0", "C0", "D5"]
        assert "A0" in str(module_method)
        assert "B0" in str(module_method)
        assert "C0" in str(module_method)
        assert "D5" in str(module_method)
        module_method = QSMMethod(self.medium_definition)
        assert module_method.valve_position == ["A0", "B0", "C0", "D5"]
        assert "A0" in str(module_method)
        assert "B0" in str(module_method)
        assert "C0" in str(module_method)
        assert "D5" in str(module_method)
        for qsm_method in self.qsm_method_list:
            qsm = QSMMethod(qsm_method)
            assert qsm.valve_position == ["A0", "B0", "C0", "D0"]
            # All examples us A0, B0, C0 and D0

    def test_valve_position_setter(self):
        module_method = QSMMethod(self.minimal_definition)
        module_method.valve_position = ["A0", "B0", "C0", "D2"]
        assert module_method.valve_position == ["A0", "B0", "C0", "D2"]
        assert "A0" in str(module_method)
        assert "B0" in str(module_method)
        assert "C0" in str(module_method)
        assert "D2" in str(module_method)
        assert (
            "<SolventSelectionValveAPosition>0</SolventSelectionValveAPosition>"
            in module_method.current_method["nativeXml"]
        )
        assert (
            "<SolventSelectionValveBPosition>0</SolventSelectionValveBPosition>"
            in module_method.current_method["nativeXml"]
        )
        assert (
            "<SolventSelectionValveCPosition>0</SolventSelectionValveCPosition>"
            in module_method.current_method["nativeXml"]
        )
        assert (
            "<SolventSelectionValveDPosition>2</SolventSelectionValveDPosition>"
            in module_method.current_method["nativeXml"]
        )
        module_method.valve_position = "D1"
        assert module_method.valve_position == ["A0", "B0", "C0", "D1"]
        assert "A0" in str(module_method)
        assert "B0" in str(module_method)
        assert "C0" in str(module_method)
        assert "D1" in str(module_method)
        assert (
            "<SolventSelectionValveAPosition>0</SolventSelectionValveAPosition>"
            in module_method.current_method["nativeXml"]
        )
        assert (
            "<SolventSelectionValveBPosition>0</SolventSelectionValveBPosition>"
            in module_method.current_method["nativeXml"]
        )
        assert (
            "<SolventSelectionValveCPosition>0</SolventSelectionValveCPosition>"
            in module_method.current_method["nativeXml"]
        )
        assert (
            "<SolventSelectionValveDPosition>1</SolventSelectionValveDPosition>"
            in module_method.current_method["nativeXml"]
        )

    def test_gradient_table(self):
        module_method = QSMMethod(self.minimal_definition)
        assert len(module_method.gradient_table) == 1
        assert module_method.gradient_table[0]["Time"] == "Initial"
        assert module_method.gradient_table[0]["Flow"] == "1.5"
        assert module_method.gradient_table[0]["CompositionA"] == "25.0"
        assert module_method.gradient_table[0]["CompositionB"] == "25.0"
        assert module_method.gradient_table[0]["CompositionC"] == "25.0"
        assert module_method.gradient_table[0]["CompositionD"] == "25.0"
        assert str(module_method.gradient_table[0]["Curve"]) == "Initial"
        module_method = QSMMethod(self.medium_definition)
        assert len(module_method.gradient_table) == 2
        assert module_method.gradient_table[0]["Time"] == "Initial"
        assert module_method.gradient_table[0]["Flow"] == "1.5"
        assert module_method.gradient_table[0]["CompositionA"] == "25.0"
        assert module_method.gradient_table[0]["CompositionB"] == "25.0"
        assert module_method.gradient_table[0]["CompositionC"] == "25.0"
        assert module_method.gradient_table[0]["CompositionD"] == "25.0"
        assert str(module_method.gradient_table[0]["Curve"]) == "Initial"
        assert module_method.gradient_table[1]["Time"] == "69"
        assert module_method.gradient_table[1]["Flow"] == "0.69"
        assert module_method.gradient_table[1]["CompositionA"] == "10.0"
        assert module_method.gradient_table[1]["CompositionB"] == "10.0"
        assert module_method.gradient_table[1]["CompositionC"] == "10.0"
        assert module_method.gradient_table[1]["CompositionD"] == "70.0"
        assert str(module_method.gradient_table[1]["Curve"]) == "6"

    def test_gradient_table_setter(self):
        module_method = QSMMethod(self.minimal_definition)
        module_method.gradient_table = [
            {
                "Time": "Initial",
                "Flow": "3.3",
                "CompositionA": "33.0",
                "CompositionB": "33.0",
                "CompositionC": "33.0",
                "CompositionD": "1.0",
                "Curve": "Initial",
            }
        ]
        assert len(module_method.gradient_table) == 1
        assert module_method.gradient_table[0]["Time"] == "Initial"
        assert module_method.gradient_table[0]["Flow"] == "3.3"
        assert module_method.gradient_table[0]["CompositionA"] == "33.0"
        assert module_method.gradient_table[0]["CompositionB"] == "33.0"
        assert module_method.gradient_table[0]["CompositionC"] == "33.0"
        assert module_method.gradient_table[0]["CompositionD"] == "1.0"
        assert str(module_method.gradient_table[0]["Curve"]) == "Initial"

    def test_gradient_table_setter_default(self):
        module_method = QSMMethod(self.minimal_definition)
        module_method.gradient_table = [
            {
                "Time": "0.0",
                "Flow": "3.3",
                "CompositionA": "33.0",
                "CompositionB": "33.0",
                "CompositionC": "33.0",
                "CompositionD": "1.0",
            },
            {
                "Time": "0.0",
                "Flow": "3.3",
                "CompositionA": "33.0",
                "CompositionB": "33.0",
                "CompositionC": "33.0",
                "CompositionD": "1.0",
            },
        ]
        assert str(module_method.gradient_table[0]["Curve"]) == "Initial"
        assert str(module_method.gradient_table[1]["Curve"]) == "6"

    def test_gradient_table_setter_multiple(self):
        module_method = QSMMethod(self.minimal_definition)
        module_method.gradient_table = [
            {
                "Time": "Initial",
                "Flow": "0.500",
                "CompositionA": "70.0",
                "CompositionB": "10.0",
                "CompositionC": "10.0",
                "CompositionD": "10.0",
                "Curve": "Initial",
            },
            {
                "Time": "10.00",
                "Flow": "0.600",
                "CompositionA": "10.0",
                "CompositionB": "80.0",
                "CompositionC": "0.0",
                "CompositionD": "10.0",
                "Curve": "10",
            },
        ]
        assert len(module_method.gradient_table) == 2
        assert module_method.gradient_table[0]["Time"] == "Initial"
        assert module_method.gradient_table[0]["Flow"] == "0.500"
        assert module_method.gradient_table[0]["CompositionA"] == "70.0"
        assert module_method.gradient_table[0]["CompositionB"] == "10.0"
        assert module_method.gradient_table[0]["CompositionC"] == "10.0"
        assert module_method.gradient_table[0]["CompositionD"] == "10.0"
        assert str(module_method.gradient_table[0]["Curve"]) == "Initial"
        assert module_method.gradient_table[1]["Time"] == "10.00"
        assert module_method.gradient_table[1]["Flow"] == "0.600"
        assert module_method.gradient_table[1]["CompositionA"] == "10.0"
        assert module_method.gradient_table[1]["CompositionB"] == "80.0"
        assert module_method.gradient_table[1]["CompositionC"] == "0.0"
        assert module_method.gradient_table[1]["CompositionD"] == "10.0"
        assert str(module_method.gradient_table[1]["Curve"]) == "10"

    def test_gradient_xml_setter(self):
        module_method = QSMMethod(self.minimal_definition)
        module_method.gradient_table = [
            {
                "Time": "Initial",
                "Flow": "0.500",
                "CompositionA": "70.0",
                "CompositionB": "10.0",
                "CompositionC": "10.0",
                "CompositionD": "10.0",
                "Curve": "Initial",
            },
            {
                "Time": "10.00",
                "Flow": "0.600",
                "CompositionA": "80.0",
                "CompositionB": "0.0",
                "CompositionC": "10.0",
                "CompositionD": "10.0",
                "Curve": "10",
            },
        ]
        new_method = QSMMethod(module_method.current_method)
        assert new_method.gradient_table == module_method.gradient_table

    def test_floats_and_strings(self):
        module_method = QSMMethod(self.minimal_definition)
        module_method.gradient_table = [
            {
                "Time": "Initial",
                "Flow": 1,
                "CompositionA": 40,
                "CompositionB": 40,
                "CompositionC": 10,
                "CompositionD": 10,
                "Curve": "Initial",
            },
        ]
        assert float(module_method.gradient_table[0]["Flow"]) == 1.0
        assert float(module_method.gradient_table[0]["CompositionA"]) == 40.0
        assert float(module_method.gradient_table[0]["CompositionB"]) == 40.0
        assert float(module_method.gradient_table[0]["CompositionC"]) == 10.0
        assert float(module_method.gradient_table[0]["CompositionD"]) == 10.0
        module_method.gradient_table = [
            {
                "Time": "Initial",
                "Flow": "0.5",
                "CompositionA": "30.0",
                "CompositionB": "30.0",
                "CompositionC": "30.0",
                "CompositionD": "10.0",
                "Curve": "Initial",
            },
        ]
        assert module_method.gradient_table[0]["Flow"] == "0.5"
        assert module_method.gradient_table[0]["CompositionA"] == "30.0"
        assert module_method.gradient_table[0]["CompositionB"] == "30.0"
        assert module_method.gradient_table[0]["CompositionC"] == "30.0"
        assert module_method.gradient_table[0]["CompositionD"] == "10.0"

    def test_rounding_floats(self):
        # Empower gives the wrong numbers if more than 10 decimals are given for
        # parameters in the gradient table. This test checks that the numbers are
        # rounded to 3 decimals before being sent to Empower.
        # Consider adding test for 3*1/3 = 1
        module_method = QSMMethod(self.minimal_definition)
        module_method.gradient_table = [
            {
                "Time": "Initial",
                "Flow": 1 / 3,
                "CompositionA": 2 / 3,
                "CompositionB": 0,
                "CompositionC": 1 / 3,
                "CompositionD": 0,
                "Curve": "Initial",
            },
            {
                "Time": 1 / 3,
                "Flow": 1 / 3,
                "CompositionA": 1 / 3,
                "CompositionB": 0,
                "CompositionC": 0,
                "CompositionD": 2 / 3,
                "Curve": 6,
            },
        ]
        assert module_method.gradient_table[0]["Flow"] == "0.333"
        assert module_method.gradient_table[0]["CompositionA"] == "0.667"
        assert module_method.gradient_table[0]["CompositionB"] == "0"
        assert module_method.gradient_table[0]["CompositionC"] == "0.333"
        assert module_method.gradient_table[0]["CompositionD"] == "0"
        assert module_method.gradient_table[1]["Time"] == "0.333"
        assert module_method.gradient_table[1]["Flow"] == "0.333"
        assert module_method.gradient_table[1]["CompositionA"] == "0.333"
        assert module_method.gradient_table[1]["CompositionB"] == "0"
        assert module_method.gradient_table[1]["CompositionC"] == "0"
        assert module_method.gradient_table[1]["CompositionD"] == "0.667"
        assert (
            "0.3333" not in module_method.current_method
        )  # If values are given as strings, EmpowerHandler should not round them
        module_method = QSMMethod(self.minimal_definition)
        with self.assertWarns(UserWarning):
            module_method.gradient_table = [
                {
                    "Time": "Initial",
                    "Flow": "0.33333",  # No rounding, since this is a string
                    "CompositionA": 0.66667,  # Rounding, since this is a float
                    "CompositionB": "0",
                    "CompositionC": "0",
                    "CompositionD": "0.33333",
                    "Curve": "Initial",
                },
                {
                    "Time": "0.33333333",  # 8 decimals should give a warning
                    "Flow": "0.33333",
                    "CompositionA": "0.33333",
                    "CompositionB": "0",
                    "CompositionC": "0.66667",
                    "CompositionD": "0",
                    "Curve": 6,
                },
            ]
        assert module_method.gradient_table[0]["Flow"] == "0.33333"
        assert module_method.gradient_table[0]["CompositionA"] == "0.667"
        assert module_method.gradient_table[0]["CompositionB"] == "0"
        assert module_method.gradient_table[0]["CompositionC"] == "0"
        assert module_method.gradient_table[0]["CompositionD"] == "0.33333"
        assert module_method.gradient_table[1]["Time"] == "0.33333333"
        assert module_method.gradient_table[1]["Flow"] == "0.33333"
        assert module_method.gradient_table[1]["CompositionA"] == "0.33333"
        assert module_method.gradient_table[1]["CompositionB"] == "0"
        assert module_method.gradient_table[1]["CompositionC"] == "0.66667"
        assert module_method.gradient_table[1]["CompositionD"] == "0"
        assert "0.3333" in module_method.current_method["nativeXml"]

    def test_manually_than_gradient_table_changed(self):
        # Checks that manual changes in the gradient table does not proclude the use
        # of the gradient_table setter.
        module_method = QSMMethod(self.minimal_definition)
        module_method.replace("<Flow>0.600</Flow>", "<Flow>0.010</Flow>")
        new_gradient_table = [
            {
                "Time": "Initial",
                "Flow": "0.500",
                "CompositionA": "50.0",
                "CompositionB": "0.0",
                "CompositionC": "50.0",
                "CompositionD": "0.0",
                "Curve": "Initial",
            },
        ]
        module_method.gradient_table = new_gradient_table
        assert module_method.gradient_table == new_gradient_table

    def test_gradient_table_then_manual(self):
        module_method = QSMMethod(self.minimal_definition)
        new_gradient_table = [
            {
                "Time": "Initial",
                "Flow": "0.500",
                "CompositionA": "50.0",
                "CompositionB": "0.0",
                "CompositionC": "50.0",
                "CompositionD": "0.0",
                "Curve": "Initial",
            },
        ]
        module_method.gradient_table = new_gradient_table
        module_method.replace("<Flow>0.500</Flow>", "<Flow>0.010</Flow>")
        assert module_method.gradient_table[0]["Flow"] == "0.010"

    def test_gradient_table_float(self):
        module_method = QSMMethod(self.minimal_definition)
        new_gradient_table = [
            {
                "Time": "Initial",
                "Flow": 0.500,
                "CompositionA": 50.0,
                "CompositionB": 0.0,
                "CompositionC": 50.0,
                "CompositionD": 0.0,
                "Curve": "Initial",
            },
            {
                "Time": 10,
                "Flow": 0.500,
                "CompositionA": 50.0,
                "CompositionB": 0.0,
                "CompositionC": 0.0,
                "CompositionD": 50.0,
                "Curve": 6,
            },
        ]
        module_method.gradient_table = new_gradient_table
        assert float(module_method.gradient_table[0]["Flow"]) == 0.5

    def test_initial(self):
        module_method = QSMMethod(self.minimal_definition)
        new_gradient_table = [
            {
                "Time": 0,
                "Flow": 0.500,
                "CompositionA": 50.0,
                "CompositionB": 0.0,
                "CompositionC": 50.0,
                "CompositionD": 0.0,
                "Curve": 6,
            },
            {
                "Time": 10,
                "Flow": 0.500,
                "CompositionA": 50.0,
                "CompositionB": 0.0,
                "CompositionC": 0.0,
                "CompositionD": 50.0,
                "Curve": 6,
            },
        ]
        module_method.gradient_table = new_gradient_table
        assert module_method.gradient_table[0]["Time"] == "Initial"
        assert module_method.gradient_table[0]["Curve"] == "Initial"
        assert module_method.gradient_table[1]["Time"] != "Initial"
        assert module_method.gradient_table[1]["Curve"] != "Initial"

    def test_initial_error(self):
        module_method = QSMMethod(self.minimal_definition)
        with self.assertRaises(ValueError):
            module_method.gradient_table = [
                {
                    "Time": 10,
                    "Flow": 0.500,
                    "CompositionA": 30.0,
                    "CompositionB": 30.0,
                    "CompositionC": 30.0,
                    "CompositionD": 10.0,
                    "Curve": "Initial",
                }
            ]

    def test_error_if_late_initial(self):
        module_method = QSMMethod(self.minimal_definition)
        with self.assertRaises(ValueError):
            module_method.gradient_table = [
                {
                    "Time": "Initial",
                    "Flow": 0.500,
                    "CompositionA": 10.0,
                    "CompositionB": 10.0,
                    "CompositionC": 10.0,
                    "CompositionD": 70.0,
                    "Curve": "Initial",
                },
                {
                    "Time": 10,
                    "Flow": 0.500,
                    "CompositionA": 10.0,
                    "CompositionB": 10.0,
                    "CompositionC": 10.0,
                    "CompositionD": 70.0,
                    "Curve": "Initial",
                },
            ]
        with self.assertRaises(ValueError):
            module_method.gradient_table = [
                {
                    "Time": "Initial",
                    "Flow": 0.500,
                    "CompositionA": 10.0,
                    "CompositionB": 10.0,
                    "CompositionC": 10.0,
                    "CompositionD": 70.0,
                    "Curve": "Initial",
                },
                {
                    "Time": "Initial",
                    "Flow": 0.500,
                    "CompositionA": 10.0,
                    "CompositionB": 10.0,
                    "CompositionC": 10.0,
                    "CompositionD": 70.0,
                    "Curve": "Initial",
                },
            ]


class testBSMMethod(unittest.TestCase):
    def setUp(self) -> None:
        bsm_method_list = [
            definition["results"][0]["modules"]
            for name, definition in load_example_files().items()
            if "BSM" in name
        ]  # Finding all instrument method definitions that controls a BSM
        for i, bsm_method in enumerate(bsm_method_list):
            bsm_method_list[i] = [
                module for module in bsm_method if module["name"] == "AcquityBSM"
            ][0]
        # Finding the BSM module method in the instrument method definition
        self.bsm_method_list = bsm_method_list
        self.minimal_definition = {
            "name": "AcquityBSM",
            "nativeXml": (
                "<FlowSourceA>1</FlowSourceA><FlowSourceB>1</FlowSourceB>"
                "<GradientTable><GradientRow><Time>Initial</Time><Flow>0.600</Flow>"
                "<CompositionA>100.0</CompositionA><CompositionB>0.0</CompositionB>"
                "<Curve>Initial</Curve></GradientRow></GradientTable>"
            ),
        }
        self.medium_definition = {
            "name": "AcquityBSM",
            "nativeXml": (
                "<FlowSourceA>2</FlowSourceA><FlowSourceB>1</FlowSourceB>"
                "<GradientTable>"
                "<GradientRow>"
                "<Time>Initial</Time><Flow>0.300</Flow>"
                "<CompositionA>90.0</CompositionA>"
                "<CompositionB>10.0</CompositionB>"
                "<Curve>Initial</Curve>"
                "</GradientRow>"
                "<GradientRow>"
                "<Time>10.00</Time>"
                "<Flow>0.500</Flow>"
                "<CompositionA>10.0</CompositionA>"
                "<CompositionB>90.0</CompositionB>"
                "<Curve>6</Curve>"
                "</GradientRow>"
                "</GradientTable>"
            ),
        }

    def test_factory(self):
        module_method = module_method_factory(self.minimal_definition)
        assert isinstance(module_method, BSMMethod)

        module_method = module_method_factory(self.medium_definition)
        assert isinstance(module_method, BSMMethod)

        for bsm_method in self.bsm_method_list:
            bsm = module_method_factory(bsm_method)
            assert isinstance(bsm, BSMMethod)

    def test_valve_position(self):
        module_method = BSMMethod(self.minimal_definition)
        assert module_method.valve_position == ["A1", "B1"]
        assert "A1" in str(module_method)
        assert "B1" in str(module_method)
        module_method = BSMMethod(self.medium_definition)
        assert module_method.valve_position == ["A2", "B1"]
        assert "A2" in str(module_method)
        assert "B1" in str(module_method)
        for bsm_method in self.bsm_method_list:
            bsm = BSMMethod(bsm_method)
            assert bsm.valve_position == ["A1", "B1"]  # All examples us A1 and B1

    def test_valve_position_setter(self):
        module_method = BSMMethod(self.minimal_definition)
        module_method.valve_position = ["A2", "B2"]
        assert module_method.valve_position == ["A2", "B2"]
        assert "A2" in str(module_method)
        assert "B2" in str(module_method)
        assert (
            "<FlowSourceA>2</FlowSourceA>" in module_method.current_method["nativeXml"]
        )
        assert (
            "<FlowSourceB>2</FlowSourceB>" in module_method.current_method["nativeXml"]
        )
        module_method.valve_position = "A1"
        assert module_method.valve_position == ["A1", "B2"]
        assert "A1" in str(module_method)
        assert "B2" in str(module_method)
        assert (
            "<FlowSourceA>1</FlowSourceA>" in module_method.current_method["nativeXml"]
        )
        assert (
            "<FlowSourceB>2</FlowSourceB>" in module_method.current_method["nativeXml"]
        )

    def test_gradient_table(self):
        module_method = BSMMethod(self.minimal_definition)
        assert len(module_method.gradient_table) == 1
        assert module_method.gradient_table[0]["Time"] == "Initial"
        assert module_method.gradient_table[0]["Flow"] == "0.600"
        assert module_method.gradient_table[0]["CompositionA"] == "100.0"
        assert module_method.gradient_table[0]["CompositionB"] == "0.0"
        assert str(module_method.gradient_table[0]["Curve"]) == "Initial"
        module_method = BSMMethod(self.medium_definition)
        assert len(module_method.gradient_table) == 2
        assert module_method.gradient_table[0]["Time"] == "Initial"
        assert module_method.gradient_table[0]["Flow"] == "0.300"
        assert module_method.gradient_table[0]["CompositionA"] == "90.0"
        assert module_method.gradient_table[0]["CompositionB"] == "10.0"
        assert str(module_method.gradient_table[0]["Curve"]) == "Initial"
        assert module_method.gradient_table[1]["Time"] == "10.00"
        assert module_method.gradient_table[1]["Flow"] == "0.500"
        assert module_method.gradient_table[1]["CompositionA"] == "10.0"
        assert module_method.gradient_table[1]["CompositionB"] == "90.0"
        assert str(module_method.gradient_table[1]["Curve"]) == "6"

    def test_gradient_table_setter(self):
        module_method = BSMMethod(self.minimal_definition)
        module_method.gradient_table = [
            {
                "Time": "Initial",
                "Flow": "0.500",
                "CompositionA": "50.0",
                "CompositionB": "50.0",
                "Curve": "Initial",
            }
        ]
        assert len(module_method.gradient_table) == 1
        assert module_method.gradient_table[0]["Time"] == "Initial"
        assert module_method.gradient_table[0]["Flow"] == "0.500"
        assert module_method.gradient_table[0]["CompositionA"] == "50.0"
        assert module_method.gradient_table[0]["CompositionB"] == "50.0"
        assert str(module_method.gradient_table[0]["Curve"]) == "Initial"

    def test_gradient_table_setter_default(self):
        module_method = BSMMethod(self.minimal_definition)
        module_method.gradient_table = [
            {
                "Time": "0.00",
                "Flow": "1",
                "CompositionA": "50.0",
                "CompositionB": "50.0",
            },
            {
                "Time": "0.00",
                "Flow": "1",
                "CompositionA": "50.0",
                "CompositionB": "50.0",
            },
        ]
        assert str(module_method.gradient_table[0]["Curve"]) == "Initial"
        assert str(module_method.gradient_table[1]["Curve"]) == "6"

    def test_gradient_table_setter_multiple(self):
        module_method = BSMMethod(self.minimal_definition)
        module_method.gradient_table = [
            {
                "Time": "Initial",
                "Flow": "0.500",
                "CompositionA": "70.0",
                "CompositionB": "30.0",
                "Curve": "Initial",
            },
            {
                "Time": "10.00",
                "Flow": "0.600",
                "CompositionA": "20.0",
                "CompositionB": "80.0",
                "Curve": "10",
            },
        ]
        assert len(module_method.gradient_table) == 2
        assert module_method.gradient_table[0]["Time"] == "Initial"
        assert module_method.gradient_table[0]["Flow"] == "0.500"
        assert module_method.gradient_table[0]["CompositionA"] == "70.0"
        assert module_method.gradient_table[0]["CompositionB"] == "30.0"
        assert str(module_method.gradient_table[0]["Curve"]) == "Initial"
        assert module_method.gradient_table[1]["Time"] == "10.00"
        assert module_method.gradient_table[1]["Flow"] == "0.600"
        assert module_method.gradient_table[1]["CompositionA"] == "20.0"
        assert module_method.gradient_table[1]["CompositionB"] == "80.0"
        assert str(module_method.gradient_table[1]["Curve"]) == "10"

    def test_gradient_xml_setter(self):
        module_method = BSMMethod(self.minimal_definition)
        module_method.gradient_table = [
            {
                "Time": "Initial",
                "Flow": "0.500",
                "CompositionA": "70.0",
                "CompositionB": "30.0",
                "Curve": "Initial",
            },
            {
                "Time": "10.00",
                "Flow": "0.600",
                "CompositionA": "20.0",
                "CompositionB": "80.0",
                "Curve": "10",
            },
        ]
        new_method = BSMMethod(module_method.current_method)
        assert new_method.gradient_table == module_method.gradient_table

    def test_floats_and_strings(self):
        module_method = BSMMethod(self.minimal_definition)
        module_method.gradient_table = [
            {
                "Time": "Initial",
                "Flow": 1,
                "CompositionA": 50,
                "CompositionB": 50,
                "Curve": "Initial",
            },
        ]
        assert float(module_method.gradient_table[0]["Flow"]) == 1.0
        assert float(module_method.gradient_table[0]["CompositionA"]) == 50.0
        assert float(module_method.gradient_table[0]["CompositionB"]) == 50.0
        module_method.gradient_table = [
            {
                "Time": "Initial",
                "Flow": "0.5",
                "CompositionA": "50.0",
                "CompositionB": "50.0",
                "Curve": "Initial",
            },
        ]
        assert module_method.gradient_table[0]["Flow"] == "0.5"
        assert module_method.gradient_table[0]["CompositionA"] == "50.0"
        assert module_method.gradient_table[0]["CompositionB"] == "50.0"

    def test_rounding_floats(self):
        # Empower gives the wrong numbers if more than 10 decimals are given for
        # parameters in the gradient table. This test checks that the numbers are
        # rounded to 3 decimals before being sent to Empower.
        module_method = BSMMethod(self.minimal_definition)
        module_method.gradient_table = [
            {
                "Time": "Initial",
                "Flow": 1 / 3,
                "CompositionA": 2 / 3,
                "CompositionB": 1 / 3,
                "Curve": "Initial",
            },
            {
                "Time": 1 / 3,
                "Flow": 1 / 3,
                "CompositionA": 1 / 3,
                "CompositionB": 2 / 3,
                "Curve": 6,
            },
        ]
        assert module_method.gradient_table[0]["Flow"] == "0.333"
        assert module_method.gradient_table[0]["CompositionA"] == "0.667"
        assert module_method.gradient_table[0]["CompositionB"] == "0.333"
        assert module_method.gradient_table[1]["Time"] == "0.333"
        assert module_method.gradient_table[1]["Flow"] == "0.333"
        assert module_method.gradient_table[1]["CompositionA"] == "0.333"
        assert module_method.gradient_table[1]["CompositionB"] == "0.667"
        assert (
            "0.3333" not in module_method.current_method
        )  # If values are given as strings, EmpowerHandler should not round them
        module_method = BSMMethod(self.minimal_definition)
        with self.assertWarns(UserWarning):
            module_method.gradient_table = [
                {
                    "Time": "Initial",
                    "Flow": "0.33333",  # No rounding, since this is a string
                    "CompositionA": 0.66667,  # Rounding, since this is a float
                    "CompositionB": "0.33333",
                    "Curve": "Initial",
                },
                {
                    "Time": "0.33333333",  # 8 decimals should give a warning
                    "Flow": "0.33333",
                    "CompositionA": "0.33333",
                    "CompositionB": "0.66667",
                    "Curve": 6,
                },
            ]
        assert module_method.gradient_table[0]["Flow"] == "0.33333"
        assert module_method.gradient_table[0]["CompositionA"] == "0.667"
        assert module_method.gradient_table[0]["CompositionB"] == "0.33333"
        assert module_method.gradient_table[1]["Time"] == "0.33333333"
        assert module_method.gradient_table[1]["Flow"] == "0.33333"
        assert module_method.gradient_table[1]["CompositionA"] == "0.33333"
        assert module_method.gradient_table[1]["CompositionB"] == "0.66667"
        assert "0.3333" in module_method.current_method["nativeXml"]

    def test_manually_than_gradient_table_changed(self):
        # Checks that manual changes in the gradient table does not proclude the use
        # of the gradient_table setter.
        module_method = BSMMethod(self.minimal_definition)
        module_method.replace("<Flow>0.600</Flow>", "<Flow>0.010</Flow>")
        new_gradient_table = [
            {
                "Time": "Initial",
                "Flow": "0.500",
                "CompositionA": "50.0",
                "CompositionB": "50.0",
                "Curve": "Initial",
            },
        ]
        module_method.gradient_table = new_gradient_table
        assert module_method.gradient_table == new_gradient_table

    def test_gradient_table_then_manual(self):
        module_method = BSMMethod(self.minimal_definition)
        new_gradient_table = [
            {
                "Time": "Initial",
                "Flow": "0.500",
                "CompositionA": "50.0",
                "CompositionB": "50.0",
                "Curve": "Initial",
            },
        ]
        module_method.gradient_table = new_gradient_table
        module_method.replace("<Flow>0.500</Flow>", "<Flow>0.010</Flow>")
        assert module_method.gradient_table[0]["Flow"] == "0.010"

    def test_gradient_table_float(self):
        module_method = BSMMethod(self.minimal_definition)
        new_gradient_table = [
            {
                "Time": "Initial",
                "Flow": 0.500,
                "CompositionA": 50.0,
                "CompositionB": 50.0,
                "Curve": "Initial",
            },
            {
                "Time": 10,
                "Flow": 0.500,
                "CompositionA": 50.0,
                "CompositionB": 50.0,
                "Curve": 6,
            },
        ]
        module_method.gradient_table = new_gradient_table
        assert float(module_method.gradient_table[0]["Flow"]) == 0.5

    def test_initial(self):
        module_method = BSMMethod(self.minimal_definition)
        new_gradient_table = [
            {
                "Time": 0,
                "Flow": 0.500,
                "CompositionA": 50.0,
                "CompositionB": 50.0,
                "Curve": 6,
            },
            {
                "Time": 10,
                "Flow": 0.500,
                "CompositionA": 50.0,
                "CompositionB": 50.0,
                "Curve": 6,
            },
        ]
        module_method.gradient_table = new_gradient_table
        assert module_method.gradient_table[0]["Time"] == "Initial"
        assert module_method.gradient_table[0]["Curve"] == "Initial"
        assert module_method.gradient_table[1]["Time"] != "Initial"
        assert module_method.gradient_table[1]["Curve"] != "Initial"

    def test_initial_error(self):
        module_method = BSMMethod(self.minimal_definition)
        with self.assertRaises(ValueError):
            module_method.gradient_table = [
                {
                    "Time": 10,
                    "Flow": 0.500,
                    "CompositionA": 50.0,
                    "CompositionB": 50.0,
                    "Curve": "Initial",
                }
            ]

    def test_error_if_late_initial(self):
        module_method = BSMMethod(self.minimal_definition)
        with self.assertRaises(ValueError):
            module_method.gradient_table = [
                {
                    "Time": "Initial",
                    "Flow": 0.500,
                    "CompositionA": 50.0,
                    "CompositionB": 50.0,
                    "Curve": "Initial",
                },
                {
                    "Time": 10,
                    "Flow": 0.500,
                    "CompositionA": 50.0,
                    "CompositionB": 50.0,
                    "Curve": "Initial",
                },
            ]
        with self.assertRaises(ValueError):
            module_method.gradient_table = [
                {
                    "Time": "Initial",
                    "Flow": 0.500,
                    "CompositionA": 50.0,
                    "CompositionB": 50.0,
                    "Curve": "Initial",
                },
                {
                    "Time": "Initial",
                    "Flow": 0.500,
                    "CompositionA": 50.0,
                    "CompositionB": 50.0,
                    "Curve": "6",
                },
            ]
