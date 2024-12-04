import json
import os
import unittest

from OptiHPLCHandler.empower_detector_module_method import (
    FLRChannel,
    PDAChannel,
    PDASpectralChannel,
    TUVChannel,
)
from OptiHPLCHandler.empower_instrument_method import EmpowerInstrumentMethod
from OptiHPLCHandler.empower_module_method import SolventManagerMethod


def get_example_file_dict() -> dict:
    """
    Get an example file from the empower_method_examples folder.

    :param file_name: The name of the example file.
    """
    example = {}
    example_folder = os.path.join("tests", "empower_method_examples")
    example_files = os.listdir(example_folder)
    json_file_list = [file for file in example_files if ".json" in file]
    for file in json_file_list:
        file_path = os.path.join(example_folder, file)
        with open(file_path) as f:
            example[file] = json.load(f)
    return example


class TestInstrumentMethod(unittest.TestCase):
    def setUp(self) -> None:
        self.example = get_example_file_dict()
        self.minimal_definition = {
            "methodName": "test_method",
            "modules": [{"name": "test", "nativeXml": "test_name"}],
        }

    def test_initialisation_full_response(self):
        for method_definition in self.example.values():
            method = EmpowerInstrumentMethod(method_definition)
            assert isinstance(method, EmpowerInstrumentMethod)
            assert len(method.module_method_list) == len(
                method_definition["results"][0]["modules"]
            )

    def test_initialisation_method_definition(self):
        for method_definition in self.example.values():
            method = EmpowerInstrumentMethod(method_definition["results"][0])
            assert isinstance(method, EmpowerInstrumentMethod)
            assert len(method.module_method_list) == len(
                method_definition["results"][0]["modules"]
            )

    def test_initialisation_multiple_methods(self):
        method_definition = self.example["response-BSM-PDA-Acq.json"]
        method_definition["results"].append(method_definition["results"][0])
        with self.assertRaises(ValueError):
            EmpowerInstrumentMethod(method_definition)

    def test_initialisation_types(self):
        # Test that the correct types are created
        method_definition = self.example["response-BSM-TUV-CM-Acq.json"]
        method = EmpowerInstrumentMethod(method_definition)
        description = str(method)
        assert "ColumnManagerMethod" in description
        assert "SampleManagerMethod" in description
        assert "BSMMethod" in description
        assert "TUVMethod" in description

    def test_column_oven_method_list(self):
        method_definition = self.example["response-BSM-TUV-CM-Acq.json"]
        method = EmpowerInstrumentMethod(method_definition)
        assert len(method.module_method_list) == 4
        assert len(method.column_oven_method_list) == 1

    def test_detector_method_list(self):
        method_definition = self.example["response-BSM-TUV-CM-Acq.json"]
        method = EmpowerInstrumentMethod(method_definition)
        assert len(method.detector_method_list) == 1

    def test_initialisation_multiple_oven_types(self):
        method_definition = self.example["response-BSM-TUV-CM-Acq.json"]
        method = EmpowerInstrumentMethod(
            method_definition, use_sample_manager_oven=True
        )
        assert len(method.column_oven_method_list) == 2

    def test_sample_manager_method(self):
        method_definition = self.example["response-BSM-TUV-CM-Acq.json"]
        method = EmpowerInstrumentMethod(method_definition)
        assert method.sample_temperature == "20.0"

    def test_sample_temperature_setter(self):
        method_definition = self.example["response-BSM-TUV-CM-Acq.json"]
        method = EmpowerInstrumentMethod(method_definition)
        method.sample_temperature = "50.0"
        assert method.sample_temperature == "50.0"
        assert method.sample_handler_method.sample_temperature == "50.0"

    def test_original_method(self):
        for method_definition in self.example.values():
            method = EmpowerInstrumentMethod(method_definition)
            assert isinstance(method.original_method, dict)
            assert method.original_method == method_definition["results"][0]

    def test_original_method_immutable(self):
        method = EmpowerInstrumentMethod(self.minimal_definition)
        with self.assertRaises(TypeError):
            method.original_method["modules"] = "new"
        with self.assertRaises(TypeError):
            method.original_method["new_key"] = "new_value"

    def test_current_method(self):
        method_definition = self.example["response-BSM-TUV-CM-Acq.json"]
        method = EmpowerInstrumentMethod(method_definition)
        original_column_temperature = method.column_oven_method_list[
            0
        ].column_temperature
        method.column_oven_method_list[0].column_temperature = "50.03"
        assert isinstance(method.current_method, dict)
        assert method.current_method != method_definition["results"][0]
        assert method.current_method["modules"][-1]["nativeXml"].count("50.0") == 1
        assert (
            method.current_method["modules"][-1]["nativeXml"].replace(
                "50.0", original_column_temperature
            )
            == method_definition["results"][0]["modules"][-1]["nativeXml"]
        )
        assert method.original_method == method_definition["results"][0]

    def test_copy(self):
        method = EmpowerInstrumentMethod(self.example["response-BSM-TUV-CM-Acq.json"])
        copy = method.copy()
        assert method is not copy
        assert method.method_name == copy.method_name
        assert method.original_method == copy.original_method
        assert method.current_method == copy.current_method
        assert method.valve_position == copy.valve_position
        assert method.column_temperature == copy.column_temperature
        assert method.gradient_table == copy.gradient_table
        assert method.sample_temperature == copy.sample_temperature

    def test_copy_not_changed(self):
        method = EmpowerInstrumentMethod(self.example["response-BSM-TUV-CM-Acq.json"])
        copy = method.copy()
        method.method_name = "new_name"
        assert method.method_name != copy.method_name
        copy.method_name = "new_name"
        assert method.method_name == copy.method_name
        method.valve_position = "A2"
        assert method.valve_position != copy.valve_position
        assert method.original_method == copy.original_method
        copy.valve_position = "A2"
        assert method.valve_position == copy.valve_position
        method.column_temperature = "50.0"
        assert method.column_temperature != copy.column_temperature
        copy.column_temperature = "50.0"
        assert method.column_temperature == copy.column_temperature
        gradient_table = method.gradient_table
        gradient_table[0]["Flow"] = "0.1"
        method.gradient_table = gradient_table
        assert method.gradient_table != copy.gradient_table
        method.sample_temperature = "50.0"
        assert method.sample_temperature != copy.sample_temperature
        copy.sample_temperature = "50.0"
        assert method.sample_temperature == copy.sample_temperature

    def test_copy_sample_manager_column_oven(self):
        """
        Test that the copy method works when the sample manager column oven is used.

        We need to test this explicitly since we infer the use of the sample manager
        from the presence of the column oven.
        """
        method = EmpowerInstrumentMethod(
            self.example["response-BSM-TUV-CM-Acq.json"],
            use_sample_manager_oven=True,
        )
        two_oven_copy = method.copy()
        assert len(method.column_oven_method_list) == len(
            two_oven_copy.column_oven_method_list
        )
        one_oven_method = EmpowerInstrumentMethod(
            self.example["response-BSM-TUV-CM-Acq.json"]
        )
        assert len(one_oven_method.column_oven_method_list) != len(
            two_oven_copy.column_oven_method_list
        )
        one_oven_copy = one_oven_method.copy()
        assert len(one_oven_copy.column_oven_method_list) != len(
            two_oven_copy.column_oven_method_list
        )

    def test_get_channels_SpectralPDA(self):
        # method.channels duplicates
        method = EmpowerInstrumentMethod(self.example["response-BSM-PDA-CM-Acq.json"])
        self.assertEqual(
            method.channels,
            [
                PDASpectralChannel(
                    start_wavelength="210",
                    end_wavelength="400",
                    resolution="Resolution_12",
                )
            ],
        )

    def test_get_channels_TUV(self):
        method = EmpowerInstrumentMethod(self.example["response-BSM-TUV-CM-Acq.json"])
        self.assertEqual(
            method.channels,
            [
                TUVChannel(
                    wavelength="254",
                    datarate="SingleDataRate_20A",
                    datamode="SingleMode_1A",
                    filtertype="Filter_2",
                    timeconstant="0.1",
                    ratiominimum="0.0001",
                    autozerowavelength="Az_3",
                    autozeroinjectstart=True,
                    autozeroeventorkey=True,
                )
            ],
        )

    def test_get_channels_FLR(self):
        method = EmpowerInstrumentMethod(self.example["response-QSM-FLR-PDA-Acq.json"])
        self.assertEqual(
            method.channels,
            [
                FLRChannel(
                    excitation="280",
                    emission="348",
                    channel_name="AcqFlrChAx280e348",
                    enable=True,
                    datamode="Emission_1F",
                ),
                PDAChannel(
                    wavelength1="214",
                    wavelength2="498",
                    resolution="Resolution_48",
                    datamode="DataModeAbsorbance_0",
                    ratio2dminimumau="0.01",
                ),
            ],
        )

    def test_get_wavelengths_TUV(self):
        method = EmpowerInstrumentMethod(self.example["response-BSM-TUV-CM-Acq.json"])
        self.assertEqual(
            method.wavelengths,
            ["254"],
        )

    def test_get_wavelengths_FLR(self):
        method = EmpowerInstrumentMethod(self.example["response-QSM-FLR-PDA-Acq.json"])
        self.assertEqual(
            method.wavelengths,
            [{"Emission wavelength": "348", "Excitation wavelength": "280"}, "214"],
        )

    def test_get_wavelengths_PDA(self):
        method = EmpowerInstrumentMethod(self.example["response-BSM-PDA-CM-Acq.json"])
        self.assertEqual(
            method.wavelengths,
            [
                {"Start Wavelength": "210", "End Wavelength": "400"},
            ],
        )

    def test_set_wavelengths_TUV(self):
        method = EmpowerInstrumentMethod(self.example["response-BSM-TUV-CM-Acq.json"])
        method.wavelengths = ["669"]
        self.assertEqual(
            method.wavelengths,
            ["669"],
        )

    def test_set_wavelengths_PDA_FLR(self):
        method = EmpowerInstrumentMethod(self.example["response-QSM-FLR-PDA-Acq.json"])
        method.wavelengths = [
            "777",
        ]
        self.assertEqual(
            method.wavelengths,
            [
                {"Emission wavelength": "348", "Excitation wavelength": "280"},
                "777",
            ],
        )

    def test_set_wavelengths_PDA_Spectral(self):
        method = EmpowerInstrumentMethod(self.example["response-BSM-PDA-CM-Acq.json"])
        # Try set the pda, check it raises a not implemented error
        with self.assertRaises(NotImplementedError):
            method.wavelengths = [
                {"Start Wavelength": "210", "End Wavelength": "400"},
            ]


class TestColumnTemperature(unittest.TestCase):
    def setUp(self) -> None:
        self.example = get_example_file_dict()
        self.column_manager_example = self.example["response-BSM-TUV-CM-Acq.json"]

    def test_get(self):
        method = EmpowerInstrumentMethod(self.column_manager_example)
        assert method.column_temperature == "HeaterOff_-1"

    def test_get_none(self):
        method_definition = self.column_manager_example["results"][0]
        method_definition["modules"] = method_definition["modules"][0:-1]
        method = EmpowerInstrumentMethod(method_definition)
        with self.assertRaises(ValueError):
            method.column_temperature

    def test_get_multiple(self):
        method_definition = self.column_manager_example["results"][0]
        method_definition["modules"].append(method_definition["modules"][-1])
        method = EmpowerInstrumentMethod(method_definition)
        assert method.column_temperature == "HeaterOff_-1"

    def test_get_multiple_mismatching(self):
        method_definition = self.column_manager_example["results"][0]
        method_definition["modules"].append(method_definition["modules"][-1])
        method = EmpowerInstrumentMethod(method_definition)
        method.column_oven_method_list[0].column_temperature = "50.03"
        with self.assertRaises(ValueError):
            method.column_temperature

    def test_set(self):
        method_definition = self.column_manager_example
        method = EmpowerInstrumentMethod(method_definition)
        new_temperature = "50.0"
        method.column_temperature = new_temperature
        assert method.column_temperature == new_temperature
        assert method.column_oven_method_list[0].column_temperature == new_temperature

    def test_set_multiple(self):
        method_definition = self.column_manager_example["results"][0]
        method_definition["modules"].append(method_definition["modules"][-1])
        method = EmpowerInstrumentMethod(method_definition)
        method.column_oven_method_list[0].column_temperature = "5"
        method.column_temperature = "50.0"
        assert method.column_temperature == "50.0"

    def test_set_none(self):
        method_definition = self.column_manager_example["results"][0]
        method_definition["modules"] = method_definition["modules"][0:-1]
        method = EmpowerInstrumentMethod(method_definition)
        with self.assertRaises(ValueError):
            method.column_temperature = "50.03"

    def test_only_setting_one_temperature(self):
        minimal_definition = {
            "methodName": "test_method",
            "modules": [
                {
                    "name": "rAcquityFTN",
                    "nativeXml": "<ColumnTemperature>43.0</ColumnTemperature>",
                },
                {
                    "name": "ACQ-CM",
                    "nativeXml": "<SetColumnTemperature>45.0</SetColumnTemperature>",
                },
            ],
        }
        method = EmpowerInstrumentMethod(minimal_definition)
        assert method.column_temperature == "45.0"
        method.column_temperature = "50.03"
        assert method.column_temperature == "50.0"
        assert method.module_method_list[0].column_temperature == "43.0"
        assert method.module_method_list[1].column_temperature == "50.0"

    def test_setting_multiple(self):
        minimal_definition = {
            "methodName": "test_method",
            "modules": [
                {
                    "name": "rAcquityFTN",
                    "nativeXml": "<ColumnTemperature>43.0</ColumnTemperature>",
                },
                {
                    "name": "ACQ-CM",
                    "nativeXml": "<SetColumnTemperature>45.0</SetColumnTemperature>",
                },
            ],
        }
        method = EmpowerInstrumentMethod(
            minimal_definition, use_sample_manager_oven=True
        )
        with self.assertRaises(ValueError):
            method.column_temperature
        method.column_temperature = "50.03"
        assert method.column_temperature == "50.0"
        assert method.module_method_list[0].column_temperature == "50.0"
        assert method.module_method_list[1].column_temperature == "50.0"

    def test_copy(self):
        method = EmpowerInstrumentMethod(self.column_manager_example)
        copy = method.copy()
        assert method.column_temperature == copy.column_temperature
        method.column_temperature = "50.0"
        assert method.column_temperature != copy.column_temperature
        copy = method.copy()
        assert method.column_temperature == copy.column_temperature


class TestSolventManager(unittest.TestCase):
    def setUp(self) -> None:
        self.example = get_example_file_dict()
        self.bsm_example = self.example["response-BSM-PDA-Acq.json"]
        self.method = EmpowerInstrumentMethod(self.bsm_example)

    def test_init(self):
        assert self.method.solvent_handler_method is not None
        assert isinstance(self.method.solvent_handler_method, SolventManagerMethod)

    def test_init_none(self):
        method_definition = self.bsm_example["results"][0]
        method_definition["modules"] = [method_definition["modules"][0]]
        method = EmpowerInstrumentMethod(method_definition)
        assert method.solvent_handler_method is None

    def test_multiple(self):
        method_definition = self.bsm_example["results"][0]
        method_definition["modules"].append(method_definition["modules"][1])
        method = EmpowerInstrumentMethod(method_definition)
        with self.assertRaises(ValueError):
            method.solvent_handler_method

    def test_get_gradient_table(self):
        gradient_table = self.method.gradient_table
        assert isinstance(gradient_table, list)
        assert isinstance(gradient_table[0], dict)

    def test_get_gradient_table_none(self):
        method_definition = self.bsm_example["results"][0]
        method_definition["modules"] = [method_definition["modules"][0]]
        method = EmpowerInstrumentMethod(method_definition)
        with self.assertRaises(ValueError):
            method.gradient_table

    def test_set_gradient_table(self):
        gradient_table = self.method.gradient_table
        assert gradient_table[0]["Flow"] != "0.1"
        assert (
            "<Flow>0.1</Flow>"
            not in self.method.current_method["modules"][1]["nativeXml"]
        )
        gradient_table[0]["Flow"] = "0.1"
        self.method.gradient_table = gradient_table
        assert self.method.gradient_table[0]["Flow"] == "0.1"
        assert (
            "<Flow>0.1</Flow>" in self.method.current_method["modules"][1]["nativeXml"]
        )

    def test_set_gradient_table_none(self):
        method_definition = self.bsm_example["results"][0]
        method_definition["modules"] = [method_definition["modules"][0]]
        method = EmpowerInstrumentMethod(method_definition)
        with self.assertRaises(ValueError):
            method.gradient_table = [{"Flow": "0.1"}]

    def test_copy(self):
        gradient_table = self.method.gradient_table
        gradient_table[0]["Flow"] = "0.1"
        self.method.gradient_table = gradient_table
        copy = self.method.copy()
        assert self.method.gradient_table == copy.gradient_table


class TestValvePosition(unittest.TestCase):
    def setUp(self) -> None:
        self.example = get_example_file_dict()
        self.bsm_example = self.example["response-BSM-PDA-Acq.json"]
        self.method = EmpowerInstrumentMethod(self.bsm_example)

    def test_get(self):
        assert self.method.valve_position == ["A1", "B1"]

    def test_get_none(self):
        method_definition = self.bsm_example["results"][0]
        method_definition["modules"] = [method_definition["modules"][0]]
        method = EmpowerInstrumentMethod(method_definition)
        with self.assertRaises(ValueError):
            method.valve_position

    def test_set_list_one(self):
        self.method.valve_position = ["A2"]
        assert self.method.valve_position == ["A2", "B1"]
        assert (
            "<FlowSourceA>2</FlowSourceA>"
            in self.method.current_method["modules"][1]["nativeXml"]
        )
        assert (
            "<FlowSourceB>1</FlowSourceB>"
            in self.method.current_method["modules"][1]["nativeXml"]
        )

    def test_set_list_multiple(self):
        self.method.valve_position = ["A7", "B5"]
        assert self.method.valve_position == ["A7", "B5"]
        assert (
            "<FlowSourceA>7</FlowSourceA>"
            in self.method.current_method["modules"][1]["nativeXml"]
        )
        assert (
            "<FlowSourceB>5</FlowSourceB>"
            in self.method.current_method["modules"][1]["nativeXml"]
        )

    def test_set_str_single(self):
        self.method.valve_position = "A2"
        assert self.method.valve_position == ["A2", "B1"]
        assert (
            "<FlowSourceA>2</FlowSourceA>"
            in self.method.current_method["modules"][1]["nativeXml"]
        )
        assert (
            "<FlowSourceB>1</FlowSourceB>"
            in self.method.current_method["modules"][1]["nativeXml"]
        )

    def test_set_str_multiple(self):
        self.method.valve_position = "A2, B3"
        assert self.method.valve_position == ["A2", "B3"]
        assert (
            "<FlowSourceA>2</FlowSourceA>"
            in self.method.current_method["modules"][1]["nativeXml"]
        )
        assert (
            "<FlowSourceB>3</FlowSourceB>"
            in self.method.current_method["modules"][1]["nativeXml"]
        )

    def test_set_none(self):
        method_definition = self.bsm_example["results"][0]
        method_definition["modules"] = [method_definition["modules"][0]]
        method = EmpowerInstrumentMethod(method_definition)
        with self.assertRaises(ValueError):
            method.valve_position = "A2"
        with self.assertRaises(ValueError):
            method.valve_position = ["A2", "B1"]

    def test_method_name(self):
        assert self.method.method_name == "AcquityBSMPDA"
        self.method.method_name = "new_name"
        assert self.method.method_name == "new_name"
        assert self.method.current_method["methodName"] == "new_name"

    def test_copy(self):
        copy = self.method.copy()
        assert self.method.valve_position == copy.valve_position
        self.method.valve_position = "A2"
        assert self.method.valve_position != copy.valve_position
        copy = self.method.copy()
        assert self.method.valve_position == copy.valve_position


class TestSampleTemperature(unittest.TestCase):
    def setUp(self) -> None:
        self.example = get_example_file_dict()
        self.bsm_example = self.example["response-BSM-PDA-Acq.json"]
        self.method = EmpowerInstrumentMethod(self.bsm_example)

    def test_get(self):
        assert self.method.sample_temperature == "20.0"

    def test_get_none(self):
        method_definition = self.bsm_example["results"][0]
        method_definition["modules"] = [method_definition["modules"][1]]
        method = EmpowerInstrumentMethod(method_definition)
        with self.assertRaises(ValueError):
            method.sample_temperature

    def test_set(self):
        self.method.sample_temperature = "50.0"
        assert self.method.sample_temperature == "50.0"
        assert (
            "<SampleTemperature>50.0</SampleTemperature>"
            in self.method.current_method["modules"][0]["nativeXml"]
        )

    def test_set_none(self):
        method_definition = self.bsm_example["results"][0]
        method_definition["modules"] = [method_definition["modules"][1]]
        method = EmpowerInstrumentMethod(method_definition)
        with self.assertRaises(ValueError):
            method.sample_temperature = "50.03"

    def test_copy(self):
        copy = self.method.copy()
        assert self.method.sample_temperature == copy.sample_temperature
        self.method.sample_temperature = "50.0"
        assert self.method.sample_temperature != copy.sample_temperature
        copy = self.method.copy()
        assert self.method.sample_temperature == copy.sample_temperature
