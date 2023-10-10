import json
import os
import unittest

from OptiHPLCHandler.empower_instrument_method import (
    BSMMethod,
    ColumnHandlerMethod,
    InstrumentMethod,
    instrument_method_factory,
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


class TestInstrumentMethodFactory(unittest.TestCase):
    def setUp(self) -> None:
        self.example = load_example_files()
        self.example_definition = self.example["response-BSM-PDA-Acq.json"]["results"][
            0
        ]["modules"][2]

    def test_column_handler(self):
        minimal_definition = {"name": "rAcquityFTN"}
        instrument_method = instrument_method_factory(minimal_definition)
        assert isinstance(instrument_method, ColumnHandlerMethod)
        example_definition = self.example["response-BSM-PDA-Acq.json"]["results"][0][
            "modules"
        ][0]
        instrument_method = instrument_method_factory(example_definition)
        assert isinstance(instrument_method, ColumnHandlerMethod)

    def test_instrument_method(self):
        minimal_definition = {"name": "none_of_the_above"}
        instrument_method = instrument_method_factory(minimal_definition)
        assert isinstance(instrument_method, InstrumentMethod)
        # This is a PDA, we do not have specific classes for detectors
        instrument_method = instrument_method_factory(self.example_definition)
        assert isinstance(instrument_method, InstrumentMethod)

    def test_unknown(self):
        # Verify that an unknown instrument method will be returned as a generic
        # InstrumentMethod
        minimal_definition = {}
        instrument_method = instrument_method_factory(minimal_definition)
        assert isinstance(instrument_method, InstrumentMethod)


class TestInstrumentMethod(unittest.TestCase):
    def setUp(self) -> None:
        self.example = load_example_files()
        self.example_definition = self.example["response-BSM-PDA-Acq.json"]["results"][
            0
        ]["modules"][2]

    def test_original_method_immutable(self):
        minimal_definition = {"name": "test", "xml": "old"}
        instrument_method = instrument_method_factory(minimal_definition)
        with self.assertRaises(TypeError):
            instrument_method.original_method["xml"] = "new"
        with self.assertRaises(TypeError):
            instrument_method.original_method["new_key"] = "new_value"

    def test_instrument_method_replace(self):
        minimal_definition = {"name": "test", "xml": "old"}
        instrument_method = instrument_method_factory(minimal_definition)
        instrument_method.replace("old", "new")
        assert instrument_method.current_method["xml"] == "new"
        assert instrument_method.original_method["xml"] == "old"

    def test_instrument_method_replace_multiple(self):
        minimal_definition = {"name": "test", "xml": "old"}
        instrument_method = instrument_method_factory(minimal_definition)
        instrument_method.replace("old", "new")
        assert instrument_method.current_method["xml"] == "new"
        instrument_method.replace("new", "newer")
        assert instrument_method.current_method["xml"] == "newer"
        assert instrument_method.original_method["xml"] == "old"

    def test_instrument_method_undo(self):
        minimal_definition = {"name": "test", "xml": "old"}
        instrument_method = instrument_method_factory(minimal_definition)
        instrument_method.replace("old", "new")
        assert instrument_method.current_method["xml"] == "new"
        instrument_method.replace("new", "newer")
        assert instrument_method.current_method["xml"] == "newer"
        instrument_method.undo()
        assert instrument_method.current_method["xml"] == "new"
        instrument_method.undo()
        assert instrument_method.current_method["xml"] == "old"
        with self.assertRaises(IndexError):
            instrument_method.undo()

    def test_instrument_method_replace_no_xml_no_changes(self):
        minimal_definition = {"name": "test"}
        instrument_method = instrument_method_factory(minimal_definition)
        assert instrument_method.original_method == minimal_definition

    def test_instrument_method_replace_no_xml_changes(self):
        minimal_definition = {"name": "test"}
        instrument_method = instrument_method_factory(minimal_definition)
        instrument_method.replace("old", "new")
        with self.assertRaises(ValueError):
            instrument_method.current_method

    def test_instrument_method_getitem(self):
        minimal_definition = {"name": "test", "xml": "<a>value</a>"}
        instrument_method = instrument_method_factory(minimal_definition)
        assert instrument_method["a"] == "value"
        instrument_method = instrument_method_factory(self.example_definition)
        assert instrument_method["StartWavelength"] == "210"

    def test_instrument_method_getitem_no_xml(self):
        minimal_definition = {"name": "test"}
        instrument_method = instrument_method_factory(minimal_definition)
        with self.assertRaises(KeyError):
            instrument_method["a"]

    def test_instrument_method_getitem_no_key(self):
        minimal_definition = {"name": "test", "xml": "<a>value</a>"}
        instrument_method = instrument_method_factory(minimal_definition)
        with self.assertRaises(KeyError):
            instrument_method["b"]
        instrument_method = instrument_method_factory(self.example_definition)
        with self.assertRaises(KeyError):
            instrument_method["not_exisiting_key"]

    def test_instrument_method_getitem_more_occurences(self):
        minimal_definition = {"name": "test", "xml": "<a>value</a><a>value2</a>"}
        instrument_method = instrument_method_factory(minimal_definition)
        with self.assertRaises(ValueError):
            instrument_method["a"]

    def test_instrument_method_setitem(self):
        minimal_definition = {"name": "test", "xml": "<a>value</a>"}
        instrument_method = instrument_method_factory(minimal_definition)
        instrument_method["a"] = "new_value"
        assert instrument_method.current_method["xml"] == "<a>new_value</a>"
        assert instrument_method.original_method["xml"] == "<a>value</a>"
        assert instrument_method["a"] == "new_value"
        instrument_method = instrument_method_factory(self.example_definition)
        instrument_method["StartWavelength"] = "211"
        assert (
            "<StartWavelength>210</StartWavelength>"
            in instrument_method.original_method["xml"]
        )
        assert (
            "<StartWavelength>211</StartWavelength>"
            in instrument_method.current_method["xml"]
        )
        assert instrument_method["StartWavelength"] == "211"


class TestSampleManager(unittest.TestCase):
    def setUp(self) -> None:
        self.example = load_example_files()
        self.example_definition = self.example["response-BSM-PDA-Acq.json"]["results"][
            0
        ]["modules"][0]

    def test_sample_manager_get_temperature(self):
        minimal_definition = {
            "name": "rAcquityFTN",
            "xml": "<ColumnTemperature>43.0</ColumnTemperature>",
        }
        instrument_method: ColumnHandlerMethod = instrument_method_factory(
            minimal_definition
        )
        assert instrument_method.column_temperature == "43.0"
        instrument_method = instrument_method_factory(self.example_definition)
        assert instrument_method.column_temperature == "43.0"

    def test_sample_manager_set_temperature(self):
        minimal_definition = {
            "name": "rAcquityFTN",
            "xml": "<ColumnTemperature>43.0</ColumnTemperature>",
        }
        instrument_method: ColumnHandlerMethod = instrument_method_factory(
            minimal_definition
        )
        instrument_method.column_temperature = "44.0"
        assert (
            instrument_method.original_method["xml"]
            == "<ColumnTemperature>43.0</ColumnTemperature>"
        )
        assert (
            instrument_method.current_method["xml"]
            == "<ColumnTemperature>44.0</ColumnTemperature>"
        )
        assert instrument_method.column_temperature == "44.0"
        instrument_method = instrument_method_factory(self.example_definition)
        instrument_method.column_temperature = "44.0"
        assert (
            "<ColumnTemperature>43.0</ColumnTemperature>"
            in instrument_method.original_method["xml"]
        )
        assert (
            "<ColumnTemperature>44.0</ColumnTemperature>"
            in instrument_method.current_method["xml"]
        )
        assert instrument_method.column_temperature == "44.0"


class testBSMMethod(unittest.TestCase):
    def setUp(self) -> None:
        bsm_method_list = [
            definition["results"][0]["modules"]
            for name, definition in load_example_files().items()
            if "BSM" in name
        ]  # Finding all BSM methodset method definitions
        for i, bsm_method in enumerate(bsm_method_list):
            bsm_method_list[i] = [
                module for module in bsm_method if module["name"] == "AcquityBSM"
            ][0]
        # Finding the BSM instrument method in the methodset method definition
        self.bsm_method_list = bsm_method_list
        self.minimal_definition = {
            "name": "AcquityBSM",
            "xml": (
                "<FlowSourceA>1</FlowSourceA><FlowSourceB>1</FlowSourceB>"
                "<GradientTable><GradientRow><Time>0.00</Time><Flow>0.600</Flow>"
                "<CompositionA>100.0</CompositionA><CompositionB>0.0</CompositionB>"
                "<Curve>6</Curve></GradientRow></GradientTable>"
            ),
        }
        self.medium_definition = {
            "name": "AcquityBSM",
            "xml": (
                "<FlowSourceA>2</FlowSourceA><FlowSourceB>1</FlowSourceB>"
                "<GradientTable>"
                "<GradientRow>"
                "<Time>0.00</Time><Flow>0.300</Flow>"
                "<CompositionA>90.0</CompositionA>"
                "<CompositionB>10.0</CompositionB>"
                "<Curve>6</Curve>"
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
        instrument_method = instrument_method_factory(self.minimal_definition)
        assert isinstance(instrument_method, BSMMethod)

        instrument_method = instrument_method_factory(self.medium_definition)
        assert isinstance(instrument_method, BSMMethod)

        for bsm_method in self.bsm_method_list:
            bsm = instrument_method_factory(bsm_method)
            assert isinstance(bsm, BSMMethod)

    def test_valve_position(self):
        instrument_method = BSMMethod(self.minimal_definition)
        assert instrument_method.valve_position == ["A1", "B1"]
        assert "A1" in str(instrument_method)
        assert "B1" in str(instrument_method)
        instrument_method = BSMMethod(self.medium_definition)
        assert instrument_method.valve_position == ["A2", "B1"]
        assert "A2" in str(instrument_method)
        assert "B1" in str(instrument_method)
        for bsm_method in self.bsm_method_list:
            bsm = BSMMethod(bsm_method)
            assert bsm.valve_position == ["A1", "B1"]  # All examples us A1 and B1

    def test_valve_position_setter(self):
        instrument_method = BSMMethod(self.minimal_definition)
        instrument_method.valve_position = ["A2", "B2"]
        assert instrument_method.valve_position == ["A2", "B2"]
        assert "A2" in str(instrument_method)
        assert "B2" in str(instrument_method)
        assert "<FlowSourceA>2</FlowSourceA>" in instrument_method.current_method["xml"]
        assert "<FlowSourceB>2</FlowSourceB>" in instrument_method.current_method["xml"]
        instrument_method.valve_position = "A1"
        assert instrument_method.valve_position == ["A1", "B2"]
        assert "A1" in str(instrument_method)
        assert "B2" in str(instrument_method)
        assert "<FlowSourceA>1</FlowSourceA>" in instrument_method.current_method["xml"]
        assert "<FlowSourceB>2</FlowSourceB>" in instrument_method.current_method["xml"]

    def test_gradient_data(self):
        instrument_method = BSMMethod(self.minimal_definition)
        assert len(instrument_method.gradient_data) == 1
        assert instrument_method.gradient_data[0].time == "0.00"
        assert instrument_method.gradient_data[0].flow == "0.600"
        assert instrument_method.gradient_data[0].composition == ["100.0", "0.0"]
        assert str(instrument_method.gradient_data[0].curve) == "6"
        instrument_method = BSMMethod(self.medium_definition)
        assert len(instrument_method.gradient_data) == 2
        assert instrument_method.gradient_data[0].time == "0.00"
        assert instrument_method.gradient_data[0].flow == "0.300"
        assert instrument_method.gradient_data[0].composition == ["90.0", "10.0"]
        assert str(instrument_method.gradient_data[0].curve) == "6"
        assert instrument_method.gradient_data[1].time == "10.00"
        assert instrument_method.gradient_data[1].flow == "0.500"
        assert instrument_method.gradient_data[1].composition == ["10.0", "90.0"]
        assert str(instrument_method.gradient_data[1].curve) == "6"

    def test_gradient_table(self):
        instrument_method = BSMMethod(self.minimal_definition)
        assert len(instrument_method.gradient_table) == 1
        assert instrument_method.gradient_table[0]["Time"] == "0.00"
        assert instrument_method.gradient_table[0]["Flow"] == "0.600"
        assert instrument_method.gradient_table[0]["CompositionA"] == "100.0"
        assert instrument_method.gradient_table[0]["CompositionB"] == "0.0"
        assert str(instrument_method.gradient_table[0]["Curve"]) == "6"
        instrument_method = BSMMethod(self.medium_definition)
        assert len(instrument_method.gradient_table) == 2
        assert instrument_method.gradient_table[0]["Time"] == "0.00"
        assert instrument_method.gradient_table[0]["Flow"] == "0.300"
        assert instrument_method.gradient_table[0]["CompositionA"] == "90.0"
        assert instrument_method.gradient_table[0]["CompositionB"] == "10.0"
        assert str(instrument_method.gradient_table[0]["Curve"]) == "6"
        assert instrument_method.gradient_table[1]["Time"] == "10.00"
        assert instrument_method.gradient_table[1]["Flow"] == "0.500"
        assert instrument_method.gradient_table[1]["CompositionA"] == "10.0"
        assert instrument_method.gradient_table[1]["CompositionB"] == "90.0"
        assert str(instrument_method.gradient_table[1]["Curve"]) == "6"

    def test_gradient_table_setter(self):
        instrument_method = BSMMethod(self.minimal_definition)
        instrument_method.gradient_table = [
            {
                "Time": "0.00",
                "Flow": "0.500",
                "CompositionA": "50.0",
                "CompositionB": "50.0",
                "Curve": "11",
            }
        ]
        assert len(instrument_method.gradient_table) == 1
        assert instrument_method.gradient_table[0]["Time"] == "0.00"
        assert instrument_method.gradient_table[0]["Flow"] == "0.500"
        assert instrument_method.gradient_table[0]["CompositionA"] == "50.0"
        assert instrument_method.gradient_table[0]["CompositionB"] == "50.0"
        assert str(instrument_method.gradient_table[0]["Curve"]) == "11"

    def test_gradient_table_setter_default(self):
        instrument_method = BSMMethod(self.minimal_definition)
        instrument_method.gradient_table = [
            {
                "Time": "0.00",
                "Flow": "1",
                "CompositionA": "50.0",
                "CompositionB": "50.0",
            }
        ]
        assert str(instrument_method.gradient_table[0]["Curve"]) == "6"

    def test_gradient_table_setter_multiple(self):
        instrument_method = BSMMethod(self.minimal_definition)
        instrument_method.gradient_table = [
            {
                "Time": "0.00",
                "Flow": "0.500",
                "CompositionA": "70.0",
                "CompositionB": "30.0",
                "Curve": "11",
            },
            {
                "Time": "10.00",
                "Flow": "0.600",
                "CompositionA": "20.0",
                "CompositionB": "80.0",
                "Curve": "10",
            },
        ]
        assert len(instrument_method.gradient_table) == 2
        assert instrument_method.gradient_table[0]["Time"] == "0.00"
        assert instrument_method.gradient_table[0]["Flow"] == "0.500"
        assert instrument_method.gradient_table[0]["CompositionA"] == "70.0"
        assert instrument_method.gradient_table[0]["CompositionB"] == "30.0"
        assert str(instrument_method.gradient_table[0]["Curve"]) == "11"
        assert instrument_method.gradient_table[1]["Time"] == "10.00"
        assert instrument_method.gradient_table[1]["Flow"] == "0.600"
        assert instrument_method.gradient_table[1]["CompositionA"] == "20.0"
        assert instrument_method.gradient_table[1]["CompositionB"] == "80.0"
        assert str(instrument_method.gradient_table[1]["Curve"]) == "10"

    def test_gradient_xml(self):
        instrument_method = BSMMethod(self.minimal_definition)
        assert instrument_method.gradient_xml in self.minimal_definition["xml"]
        assert instrument_method["GradientTable"] in instrument_method.gradient_xml
        instrument_method = BSMMethod(self.medium_definition)
        assert instrument_method.gradient_xml in self.medium_definition["xml"]
        assert instrument_method["GradientTable"] in instrument_method.gradient_xml

        def strip(x: str) -> str:
            return x.replace("\r\n", "").replace(" ", "")

        # Removes the whitespaces and newlines from the xml from Waters
        for bsm_method in self.bsm_method_list:
            bsm = BSMMethod(bsm_method)
            assert bsm.gradient_xml in strip(bsm_method["xml"])
            assert strip(bsm["GradientTable"]) in bsm.gradient_xml

    def test_gradient_xml_setter(self):
        instrument_method = BSMMethod(self.minimal_definition)
        instrument_method.gradient_table = [
            {
                "Time": "0.00",
                "Flow": "0.500",
                "CompositionA": "70.0",
                "CompositionB": "30.0",
                "Curve": "11",
            },
            {
                "Time": "10.00",
                "Flow": "0.600",
                "CompositionA": "20.0",
                "CompositionB": "80.0",
                "Curve": "10",
            },
        ]
        assert instrument_method.gradient_xml in instrument_method.current_method["xml"]
