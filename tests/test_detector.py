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


class TestFLR(unittest.TestCase):
    def setUp(self) -> None:
        flr_example = load_example_file("FLR_example")
        flr_example = {"nativeXml": flr_example}
        self.method: FLRMethod = module_method_factory(flr_example)

    def test_instantiation(self):
        self.assertIsInstance(self.method, FLRMethod)

    def test_channels(self):
        channel_dict = self.method.channel_dict
        assert len(channel_dict) == 2
