import os
import unittest

from OptiHPLCHandler.empower_detector_module_method import (
    Detector,
    FLRMethod,
    PDAMethod,
    TUVMethod,
)
from OptiHPLCHandler.factories import module_method_factory


def load_example_file(example_name: str) -> str:
    with open(
        os.path.join("tests", "empower_method_examples", f"{example_name}.xml")
    ) as f:
        return f.read()


class TestDetector(unittest.TestCase):
    def test_simplified_channel_name(self):
        method = Detector({"nativeXml": "test"})
        assert method.simplified_channel_name("ChannelA") == "Channel1"
        assert method.simplified_channel_name("Channel2") == "Channel2"

    def test_empower_channel_name(self):
        alphabetic_method = Detector({"nativeXml": "<ChannelA>test</ChannelA>"})
        assert alphabetic_method.empower_channel_name("Channel1") == "ChannelA"
        assert alphabetic_method.empower_channel_name("ChannelB") == "ChannelB"
        numeric_method = Detector({"nativeXml": "<Channel1>test</Channel1>"})
        assert numeric_method.empower_channel_name("Channel1") == "Channel1"
        assert numeric_method.empower_channel_name("ChannelB") == "Channel2"

    def test_lamp_enabled(self):
        method = Detector({"nativeXml": "<Lamp>true</Lamp>"})
        assert method.lamp_enabled is True
        method.lamp_enabled = False
        assert method.lamp_enabled is False

    def test_no_lamp(self):
        method = Detector({"nativeXml": "<test/>"})
        with self.assertRaises(AttributeError):
            method.lamp_enabled


class TestTUV(unittest.TestCase):
    def setUp(self) -> None:
        tuv_example = load_example_file("TUV_example")
        tuv_example = {"nativeXml": tuv_example}
        self.method: TUVMethod = module_method_factory(tuv_example)

    def test_instantiation(self):
        self.assertIsInstance(self.method, TUVMethod)

    def test_get_channels(self):
        channel_dict = self.method.channel_dict
        self.assertEqual(len(channel_dict), 2)
        self.assertEqual(channel_dict["Channel1"]["Type"], "Single")
        self.assertEqual(channel_dict["Channel1"]["Wavelength"], "214")

    def test_set_wavelengths(self):
        self.method.channel_dict = {"Channel1": {"Wavelength": "400"}}
        self.assertEqual(self.method.channel_dict["Channel1"]["Wavelength"], "400")

        self.method.channel_dict = {"ChannelA": {"Wavelength": "400"}}
        self.assertEqual(self.method.channel_dict["Channel1"]["Wavelength"], "400")

        self.method.channel_dict = {"Channel1": {"Wavelength": 400}}
        self.assertEqual(self.method.channel_dict["Channel1"]["Wavelength"], "400")


class TestPDA(unittest.TestCase):
    def setUp(self) -> None:
        pda_example = load_example_file("PDA_example")
        pda_example = {"nativeXml": pda_example}
        self.method: PDAMethod = module_method_factory(pda_example)

    def test_instantiation(self):
        self.assertIsInstance(self.method, PDAMethod)

    def test_get_channels(self):
        channel_dict = self.method.channel_dict
        self.assertEqual(len(channel_dict), 9)
        self.assertEqual(channel_dict["Channel1"]["Enable"], True)
        self.assertEqual(channel_dict["Channel1"]["Type"], "Single")
        self.assertEqual(channel_dict["Channel1"]["Wavelength1"], "214")

    def test_set_enable_channels_bool(self):
        self.assertEqual(self.method.channel_dict["Channel1"]["Enable"], True)
        self.method.channel_dict = {"Channel1": {"Enable": False}}
        self.assertEqual(self.method.channel_dict["Channel1"]["Enable"], False)

    def test_set_enable_channels_str(self):
        self.assertEqual(self.method.channel_dict["Channel1"]["Enable"], True)
        self.method.channel_dict = {"Channel1": {"Enable": "false"}}
        self.assertEqual(self.method.channel_dict["Channel1"]["Enable"], False)

    def test_set_wavelength_str(self):
        self.method.channel_dict = {"Channel1": {"Wavelength1": "400"}}
        self.assertEqual(self.method.channel_dict["Channel1"]["Wavelength1"], "400")

    def test_set_wavelength_int(self):
        self.method.channel_dict = {"Channel1": {"Wavelength1": 400}}
        self.assertEqual(self.method.channel_dict["Channel1"]["Wavelength1"], "400")

    def test_set_wavelength_twice(self):
        # Get the initial value
        self.assertEqual(self.method.channel_dict["Channel1"]["Wavelength1"], "214")
        # Set the value to 400
        self.method.channel_dict = {"Channel1": {"Wavelength1": 400}}
        self.assertEqual(self.method.channel_dict["Channel1"]["Wavelength1"], "400")
        # Set the value to 500
        self.method.channel_dict = {"Channel1": {"Wavelength1": 500}}
        self.assertEqual(self.method.channel_dict["Channel1"]["Wavelength1"], "500")

    def test_get_spectral_channel(self):
        channel_dict = self.method.channel_dict
        self.assertEqual(channel_dict["SpectralChannel"]["StartWavelength"], "210")
        self.assertEqual(channel_dict["SpectralChannel"]["EndWavelength"], "400")
        self.assertEqual(channel_dict["SpectralChannel"]["Enable"], False)

    def test_set_spectral_channel(self):
        self.method.channel_dict = {
            "SpectralChannel": {
                "StartWavelength": 200,
                "EndWavelength": 300,
                "Enable": True,
            }
        }
        channel_dict = self.method.channel_dict
        self.assertEqual(channel_dict["SpectralChannel"]["StartWavelength"], "200")
        self.assertEqual(channel_dict["SpectralChannel"]["EndWavelength"], "300")
        self.assertEqual(channel_dict["SpectralChannel"]["Enable"], True)


class TestFLR(unittest.TestCase):
    def setUp(self) -> None:
        flr_example = load_example_file("FLR_example")
        flr_example = {"nativeXml": flr_example}
        self.method: FLRMethod = module_method_factory(flr_example)

    def test_instantiation(self):
        self.assertIsInstance(self.method, FLRMethod)

    def test_get_channels(self):
        channel_dict = self.method.channel_dict
        assert len(channel_dict) == 4
        assert channel_dict["Channel1"]["Enable"] is True
        assert channel_dict["Channel1"]["Type"] == "Single"
        assert channel_dict["Channel1"]["Excitation"] == "280"
        assert channel_dict["Channel1"]["Emission"] == "348"
        assert channel_dict["Channel1"]["Name"] == "AcqFlrChAx280e348"

    def test_set_enable_channels_bool(self):
        assert self.method.channel_dict["Channel1"]["Enable"] is True
        self.method.channel_dict = {"Channel1": {"Enable": False}}
        assert self.method.channel_dict["Channel1"]["Enable"] is False

    def test_set_enable_channels_str(self):
        assert self.method.channel_dict["Channel1"]["Enable"] is True
        self.method.channel_dict = {"Channel1": {"Enable": "false"}}
        assert self.method.channel_dict["Channel1"]["Enable"] is False

    def test_set_wavelenghts_str(self):
        self.method.channel_dict = {"Channel1": {"Excitation": "400", "Emission": "38"}}
        assert self.method.channel_dict["Channel1"]["Excitation"] == "400"
        assert self.method.channel_dict["Channel1"]["Emission"] == "38"
        assert self.method.channel_dict["Channel1"]["Name"] == "AcqFlrChAx400e38"

    def test_set_wavelenghts_int(self):
        self.method.channel_dict = {"Channel1": {"Excitation": 400, "Emission": 38}}
        assert self.method.channel_dict["Channel1"]["Excitation"] == "400"
        assert self.method.channel_dict["Channel1"]["Emission"] == "38"
        assert self.method.channel_dict["Channel1"]["Name"] == "AcqFlrChAx400e38"
