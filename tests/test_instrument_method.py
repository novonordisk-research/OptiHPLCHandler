import json
import os
import unittest

from OptiHPLCHandler.empower_instrument_method import (
    ColumnHandlerMethod,
    InstrumentMethod,
    instrument_method_factory,
)


class TestInstrumentMethod(unittest.TestCase):
    def setUp(self) -> None:
        self.example = {}
        example_folder = os.path.join("tests", "empower_method_examples")
        example_files = os.listdir(example_folder)
        for file in example_files:
            file_path = os.path.join(example_folder, file)
            with open(file_path) as f:
                self.example[file] = json.load(f)
        self.example_definition = self.example["response-BSM-PDA-Acq.json"]["results"][
            0
        ]["modules"][2]

    def test_instrument_method_factory_column_handler(self):
        minimal_definition = {"name": "rAcquityFTN"}
        instrument_method = instrument_method_factory(minimal_definition)
        assert isinstance(instrument_method, ColumnHandlerMethod)
        example_definition = self.example["response-BSM-PDA-Acq.json"]["results"][0][
            "modules"
        ][0]
        instrument_method = instrument_method_factory(example_definition)
        assert isinstance(instrument_method, ColumnHandlerMethod)

    def test_instrument_method_factory_instrument_method(self):
        minimal_definition = {"name": "none_of_the_above"}
        instrument_method = instrument_method_factory(minimal_definition)
        assert isinstance(instrument_method, InstrumentMethod)
        # This is a PDA, we do not have specific classes for detectors
        instrument_method = instrument_method_factory(self.example_definition)
        assert isinstance(instrument_method, InstrumentMethod)

    def test_instrument_method_factory_unknown(self):
        # Verify that an unknown instrument method will be returned as a generic
        # InstrumentMethod
        minimal_definition = {}
        instrument_method = instrument_method_factory(minimal_definition)
        assert isinstance(instrument_method, InstrumentMethod)

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

    def test_sample_manager_get_temperature(self):
        minimal_definition = {
            "name": "rAcquityFTN",
            "xml": "<ColumnTemperature>43.0</ColumnTemperature>",
        }
        instrument_method: ColumnHandlerMethod = instrument_method_factory(
            minimal_definition
        )
        assert instrument_method.column_temperature == "43.0"
        example_definition = self.example["response-BSM-PDA-Acq.json"]["results"][0][
            "modules"
        ][0]
        instrument_method = instrument_method_factory(example_definition)
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
        example_definition = self.example["response-BSM-PDA-Acq.json"]["results"][0][
            "modules"
        ][0]
        instrument_method = instrument_method_factory(example_definition)
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
