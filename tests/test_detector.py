import os
import unittest

from OptiHPLCHandler.factories import module_method_factory
from OptiHPLCHandler.empower_detector_module_method import Detector, FLRMethod


def load_example_file(example_name: str) -> str:
    with open(os.path.join("tests", "empower_method_examples", f"{example_name}.xml")) as f:
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
        self.method.channel_dict = {
            "Channel1": {"Excitation": "400", "Emission": "38"}
        }
        assert self.method.channel_dict["Channel1"]["Excitation"] == "400"
        assert self.method.channel_dict["Channel1"]["Emission"] == "38"
        assert self.method.channel_dict["Channel1"]["Name"] == "AcqFlrChAx400e38"

    def test_set_wavelenghts_int(self):
        self.method.channel_dict = {
            "Channel1": {"Excitation": 400, "Emission": 38}
        }
        assert self.method.channel_dict["Channel1"]["Excitation"] == "400"
        assert self.method.channel_dict["Channel1"]["Emission"] == "38"
        assert self.method.channel_dict["Channel1"]["Name"] == "AcqFlrChAx400e38"
