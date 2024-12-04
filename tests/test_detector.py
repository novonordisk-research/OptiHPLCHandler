import os
import unittest

from OptiHPLCHandler.empower_detector_module_method import (
    Detector,
    FLRChannel,
    FLRMethod,
    PDAChannel,
    PDAMethod,
    PDASpectralChannel,
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
        # Check xml
        xml_content = self.method.current_method["nativeXml"]
        self.assertIn("<Wavelength>400</Wavelength>", xml_content)
        self.assertIn("<Wavelength>500</Wavelength>", xml_content)
        self.assertIn("<DataMode>DualModeA_1B</DataMode>", xml_content)
        self.assertIn("<DataMode>DualModeB_2C</DataMode>", xml_content)
        self.assertIn("<DataRate>DualDataRate_1B</DataRate>", xml_content)
        self.assertIn("<DataRate>DualDataRate_1B</DataRate>", xml_content)
        self.assertIn("<TimeConstant>2.0000</TimeConstant>", xml_content)
        self.assertIn("<TimeConstant>2.0000</TimeConstant>", xml_content)

    def test_get_wavelengths(self):
        self.assertEqual(self.method.wavelengths, ["214"])

    def test_set_wavelengths(self):
        self.assertEqual(self.method.wavelengths, ["214"])
        self.method.wavelengths = ["222", "400"]
        self.assertEqual(self.method.wavelengths, ["222", "400"])
        # Check xml
        xml_content = self.method.current_method["nativeXml"]
        self.assertIn("<Wavelength>222</Wavelength>", xml_content)
        self.assertIn("<Wavelength>400</Wavelength>", xml_content)


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
        # Check xml
        xml_content = self.method.current_method["nativeXml"]
        self.assertIn("<Wavelength1>400</Wavelength1>", xml_content)

    def test_get_wavelengths(self):
        self.assertEqual(self.method.wavelengths, ["214", "280"])

    def test_set_wavelengths(self):
        self.assertEqual(self.method.wavelengths, ["214", "280"])
        self.method.wavelengths = ["222", "400"]
        self.assertEqual(self.method.wavelengths, ["222", "400"])
        # Check xml
        xml_content = self.method.current_method["nativeXml"]
        self.assertIn("<Wavelength1>222</Wavelength1>", xml_content)
        self.assertIn("<Wavelength1>400</Wavelength1>", xml_content)
        self.assertIn("<Enable>true</Enable>", xml_content)

    def test_get_spectral_channel(self):
        self.assertEqual(self.method.spectral_channel, None)

    def test_set_spectral_channel(self):
        self.assertEqual(self.method.spectral_channel, None)
        self.method.spectral_channel = PDASpectralChannel(
            start_wavelength="200", end_wavelength="300"
        )
        self.assertIsInstance(self.method.spectral_channel, PDASpectralChannel)
        self.assertEqual(self.method.spectral_channel.start_wavelength, "200")
        self.assertEqual(self.method.spectral_channel.end_wavelength, "300")
        # Check xml
        xml_content = self.method.current_method["nativeXml"]
        self.assertIn("<StartWavelength>200</StartWavelength>", xml_content)
        self.assertIn("<EndWavelength>300</EndWavelength>", xml_content)

    def test_get_spectral_wavelengths(self):
        self.assertEqual(self.method.spectral_wavelengths, [])

    def test_set_spectral_wavelengths(self):
        self.assertEqual(self.method.spectral_wavelengths, [])
        self.method.spectral_wavelengths = [
            {"Start Wavelength": "200", "End Wavelength": "300"}
        ]
        self.assertEqual(
            self.method.spectral_wavelengths,
            [{"Start Wavelength": "200", "End Wavelength": "300"}],
        )
        # Check xml
        xml_content = self.method.current_method["nativeXml"]
        self.assertIn("<StartWavelength>200</StartWavelength>", xml_content)
        self.assertIn("<EndWavelength>300</EndWavelength>", xml_content)


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
        self.assertEqual(channels[0].datamode, "Emission_1F")
        self.assertEqual(channels[0].channel_name, "AcqFlrChAx280e348")

    def test_set_channels(self):
        self.assertEqual(self.method.channels[0].excitation, "280")
        self.assertEqual(self.method.channels[0].emission, "348")
        self.assertEqual(self.method.channels[0].datamode, "Emission_1F")
        self.assertEqual(self.method.channels[0].channel_name, "AcqFlrChAx280e348")
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
        self.assertEqual(channels[0].channel_name, "AcqFlrChAx400e500")
        self.assertEqual(channels[1].channel_name, "AcqFlrChBx500e600")
        # Check xml
        xml_content = self.method.current_method["nativeXml"]
        self.assertIn("<Excitation>400</Excitation>", xml_content)
        self.assertIn("<Emission>500</Emission>", xml_content)
        self.assertIn("<Excitation>500</Excitation>", xml_content)
        self.assertIn("<Emission>600</Emission>", xml_content)
        self.assertIn("<Name>AcqFlrChAx400e500</Name>", xml_content)

    def test_get_wavelengths(self):
        self.assertEqual(
            self.method.wavelengths,
            [{"Emission wavelength": "348", "Excitation wavelength": "280"}],
        )
        self.assertEqual(self.method.channels[0].channel_name, "AcqFlrChAx280e348")

    def test_set_wavelengths(self):
        new_wavelengths = [
            {"Emission wavelength": "400", "Excitation wavelength": "500"},
            {"Emission wavelength": "500", "Excitation wavelength": "600"},
            {"Emission wavelength": "600", "Excitation wavelength": "700"},
            {"Emission wavelength": "700", "Excitation wavelength": "800"},
        ]
        self.method.wavelengths = new_wavelengths
        self.assertEqual(self.method.wavelengths, new_wavelengths)
        self.assertEqual(self.method.channels[0].channel_name, "AcqFlrChAx500e400")
        self.assertEqual(self.method.channels[1].channel_name, "AcqFlrChBx600e500")
        self.assertEqual(self.method.channels[2].channel_name, "AcqFlrChCx700e600")
        self.assertEqual(self.method.channels[3].channel_name, "AcqFlrChDx800e700")
        # Check xml
        xml_content = self.method.current_method["nativeXml"]
        self.assertIn("<Excitation>500</Excitation>", xml_content)
        self.assertIn("<Emission>400</Emission>", xml_content)
        self.assertIn("<Excitation>600</Excitation>", xml_content)
        self.assertIn("<Emission>500</Emission>", xml_content)
        self.assertIn("<Name>AcqFlrChAx500e400</Name>", xml_content)
        self.assertIn("<Name>AcqFlrChBx600e500</Name>", xml_content)
        self.assertIn("<Name>AcqFlrChCx700e600</Name>", xml_content)
        self.assertIn("<Name>AcqFlrChDx800e700</Name>", xml_content)
