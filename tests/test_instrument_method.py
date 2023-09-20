import json
import os
import unittest

from OptiHPLCHandler.empower_instrument_method import (
    instrument_method_factory,
    ColumnHandler,
    InstrumentMethod,
)


class TestInstrumentMethod(unittest.TestCase):
    def setUp(self) -> None:
        self.example = {}
        example_folder = "tests\empower_method_examples"
        example_files = os.listdir(example_folder)
        for file in example_files:
            file_path = os.path.join(example_folder, file)
            with open(file_path) as f:
                self.example[file] = json.load(f)

    def test_instrument_method_factory_column_handler(self):
        minimal_definition = {"name": "rAcquityFTN"}
        instrument_method = instrument_method_factory(minimal_definition)
        assert isinstance(instrument_method, ColumnHandler)
        example_definition = self.example["response-BSM-PDA-Acq.json"]["results"][0][
            "modules"
        ][0]
        instrument_method = instrument_method_factory(example_definition)
        assert isinstance(instrument_method, ColumnHandler)

    def test_instrument_method_factory_instrument_method(self):
        minimal_definition = {"name": "none_of_the_above"}
        instrument_method = instrument_method_factory(minimal_definition)
        assert isinstance(instrument_method, InstrumentMethod)
        example_definition = self.example["response-BSM-PDA-Acq.json"]["results"][0][
            "modules"
        ][2]
        # This is a PDA, we do not have specific classes for detectors
        instrument_method = instrument_method_factory(example_definition)
        assert isinstance(instrument_method, InstrumentMethod)

    def test_instrument_method_factory_unknown(self):
        # Verify that an unknown instrument method will be returned as a generic
        # InstrumentMethod
        minimal_definition = {}
        instrument_method = instrument_method_factory(minimal_definition)
        assert isinstance(instrument_method, InstrumentMethod)

    def test_instrument_method_replace(self):
        minimal_definition = {"name": "test", "xml": "old"}
        instrument_method = instrument_method_factory(minimal_definition)
        instrument_method.replace("old", "new")
        assert instrument_method.original_method["xml"] == "old"
        assert instrument_method.current_method["xml"] == "new"

    def test_instrument_method_replace_multiple(self):
        minimal_definition = {"name": "test", "xml": "old"}
        instrument_method = instrument_method_factory(minimal_definition)
        instrument_method.replace("old", "new")
        instrument_method.replace("new", "newer")
        assert instrument_method.original_method["xml"] == "old"
        assert instrument_method.current_method["xml"] == "newer"

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
        example_definition = self.example["response-BSM-PDA-Acq.json"]["results"][0][
            "modules"
        ][2]
        instrument_method = instrument_method_factory(example_definition)
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
        example_definition = self.example["response-BSM-PDA-Acq.json"]["results"][0][
            "modules"
        ][2]
        instrument_method = instrument_method_factory(example_definition)
        with self.assertRaises(KeyError):
            instrument_method["not_exisiting_key"]

    def test_instrument_method_getitem_more_occurences(self):
        minimal_definition = {"name": "test", "xml": "<a>value</a><a>value2</a>"}
        instrument_method = instrument_method_factory(minimal_definition)
        with self.assertRaises(ValueError):
            instrument_method["a"]

    def test_sample_manager_get_temperature(self):
        minimal_definition = {
            "name": "rAcquityFTN",
            "xml": "<ColumnTemperature>43.0</ColumnTemperature>",
        }
        instrument_method = instrument_method_factory(minimal_definition)
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
        instrument_method = instrument_method_factory(minimal_definition)
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
