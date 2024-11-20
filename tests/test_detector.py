import os
import unittest

from OptiHPLCHandler.empower_detector_module_method import (
    Detector,
    FLRChannel,
    FLRMethod,
    PDAChannel,
    PDAMethod,
    TUVChannel,
    TUVMethod,
)
from OptiHPLCHandler.factories import module_method_factory


def load_example_file(example_name: str) -> str:
    with open(
        os.path.join("tests", "empower_method_examples", f"{example_name}.xml")
    ) as f:
        return f.read()


class TestDetector(unittest.TestCase):
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
        channels = self.method.channels
        self.assertEqual(len(channels), 1)
        self.assertEqual(channels[0].wavelength, "214")

    def test_set_channels(self):
        self.method.channels = [TUVChannel(wavelength="400")]
        channels = self.method.channels
        self.assertEqual(len(channels), 1)
        self.assertEqual(channels[0].wavelength, "400")

    def test_set_channels_add(self):
        self.assertEqual(self.method.channels[0].datamode, "SingleMode_1A")
        self.assertEqual(self.method.channels[0].datarate, "SingleDataRate_20A")
        self.assertEqual(self.method.channels[0].timeconstant, "0.1")
        self.method.channels = [
            TUVChannel(wavelength="400"),
            TUVChannel(wavelength="500"),
        ]
        channels = self.method.channels
        self.assertEqual(len(channels), 2)
        self.assertEqual(channels[0].wavelength, "400")
        self.assertEqual(channels[1].wavelength, "500")
        self.assertEqual(channels[0].datamode, "DualModeA_1B")
        self.assertEqual(channels[1].datamode, "DualModeB_2C")
        self.assertEqual(channels[0].datarate, "DualDataRate_1B")
        self.assertEqual(channels[1].datarate, "DualDataRate_1B")
        self.assertEqual(channels[0].timeconstant, "2.0000")
        self.assertEqual(channels[1].timeconstant, "2.0000")

    def test_get_wavelengths(self):
        self.assertEqual(self.method.wavelengths, ["214"])

    def test_set_wavelengths(self):
        self.assertEqual(self.method.wavelengths, ["214"])
        self.method.wavelengths = ["222", "400"]
        self.assertEqual(self.method.wavelengths, ["222", "400"])

    def test_set_channel_from_tuv(self):
        pda_channels = PDAChannel(wavelength1="999")
        self.method.channels[0] = pda_channels
        self.assertIsInstance(self.method.channels[0], TUVChannel)

    def test_set_channel_from_tuv_list(self):
        # Fails when trying to set a list of channels
        pda_channels = [PDAChannel(wavelength1="999")]
        self.method.channels = pda_channels
        self.assertIsInstance(self.method.channels[0], TUVChannel)


class TestPDA(unittest.TestCase):
    def setUp(self) -> None:
        pda_example = load_example_file("PDA_example")
        pda_example = {"nativeXml": pda_example}
        self.method: PDAMethod = module_method_factory(pda_example)

    def test_instantiation(self):
        self.assertIsInstance(self.method, PDAMethod)

    def test_get_channels(self):
        channels = self.method.channels
        self.assertEqual(len(channels), 2)
        self.assertEqual(channels[0].wavelength1, "214")
        self.assertEqual(channels[1].wavelength1, "280")

    def test_set_channels(self):
        self.method.channels = [PDAChannel(wavelength1="400")]
        channels = self.method.channels
        self.assertEqual(len(channels), 1)
        self.assertEqual(channels[0].wavelength1, "400")

    def test_get_wavelengths(self):
        self.assertEqual(self.method.wavelengths, ["214", "280"])

    def test_set_wavelengths(self):
        self.assertEqual(self.method.wavelengths, ["214", "280"])
        self.method.wavelengths = ["222", "400"]
        self.assertEqual(self.method.wavelengths, ["222", "400"])

    def test_set_channel_from_pda(self):
        tuv_channels = TUVChannel(wavelength="999")
        self.method.channels[0] = tuv_channels
        self.assertIsInstance(self.method.channels[0], PDAChannel)

    def test_set_channel_from_pda_list(self):
        # Fails when trying to set a list of channels
        tuv_channels = [TUVChannel(wavelength="999")]
        self.method.channels = tuv_channels
        self.assertIsInstance(self.method.channels[0], PDAChannel)


class TestFLR(unittest.TestCase):
    def setUp(self) -> None:
        flr_example = load_example_file("FLR_example")
        flr_example = {"nativeXml": flr_example}
        self.method: FLRMethod = module_method_factory(flr_example)

    def test_instantiation(self):
        self.assertIsInstance(self.method, FLRMethod)

    def test_get_channels(self):
        channels = self.method.channels
        self.assertEqual(len(channels), 1)
        self.assertEqual(channels[0].excitation, "280")
        self.assertEqual(channels[0].emission, "348")

    def test_set_channels(self):
        self.assertEqual(self.method.channels[0].excitation, "280")
        self.assertEqual(self.method.channels[0].emission, "348")
        self.assertEqual(self.method.channels[0].datamode, "Emission_1F")
        self.method.channels = [
            FLRChannel(excitation="400", emission="500"),
            FLRChannel(excitation="500", emission="600"),
        ]
        channels = self.method.channels
        self.assertEqual(len(channels), 2)
        self.assertEqual(channels[0].excitation, "400")
        self.assertEqual(channels[0].emission, "500")
        self.assertEqual(self.method.channels[0].datamode, "Emission_1F")
        self.assertEqual(channels[1].excitation, "500")
        self.assertEqual(channels[1].emission, "600")
        self.assertEqual(channels[1].datamode, "Emission_2B")
