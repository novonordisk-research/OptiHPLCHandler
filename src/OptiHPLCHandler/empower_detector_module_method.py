import logging
from xml.etree import ElementTree as ET
from typing import Union

from .empower_module_method import EmpowerModuleMethod


logger = logging.getLogger(__name__)


def to_bool(bool_string: Union[str, bool]) -> bool:
    if bool_string == "true" or bool_string is True:
        return True
    elif bool_string == "false" or bool_string is False:
        return False
    else:
        raise ValueError(f"Invalid bool string: {bool_string}")


def to_string(bool_value: Union[str, bool]) -> str:
    if bool_value is True or bool_value == "true":
        return "true"
    elif bool_value is False or bool_value == "false":
        return "false"
    else:
        raise ValueError(f"Invalid bool value: {bool_value}")


class Detector(EmpowerModuleMethod):
    def simplified_channel_name(self, channel_name: str) -> str:
        # Convert "ChannelA" to "Channel1" and "ChannelB" to "Channel2"
        channel_number = ord(channel_name[-1]) - 64
        # ord converts a character into an integer, so ord("A") = 65, ord("B") = 66, etc.
        if channel_number < 1:
            return channel_name
        return f"Channel{channel_number}"

    def empower_channel_name(self, channel_name: str) -> str:
        if ord(channel_name[-1]) < 65:
            channel_number = int(channel_name[-1])
        else:
            channel_number = ord(channel_name[-1]) - 64
        try:
            self["ChannelA"]
            # If there is a ChannelA, the channels are designated alphabetically
            return f"Channel{chr(channel_number+64)}"
        except KeyError:
            # If there is no ChannelA, the channels are designated numerically
            return f"Channel{channel_number}"

    @property
    def lamp_enabled(self) -> bool:
        try:
            return self["Lamp"] == "true"
        except KeyError as me:
            raise AttributeError(
                f"Dector method {type(self).__name__} does not have a lamp setting."
            ) from me

    @lamp_enabled.setter
    def lamp_enabled(self, value: bool):
        self["Lamp"] = to_bool(value)


class TUVMethod(Detector):
    wavelength_name = "Wavelength"

    @property
    def wavelength_mode(self) -> str:
        # Not settable as would have to change "DataMode" which is hell
        if self["WavelengthMode"] == "1":
            return "Single"
        elif self["WavelengthMode"] == "2":
            return "Dual"
        else:
            raise ValueError(f"Invalid WavelengthMode: {self['WavelengthMode']}")

    @property
    def channel_dict(self) -> dict[str, dict]:
        list_of_channel_names = ["ChannelA", "ChannelB"]
        channel_dict = {}
        for channel_name in list_of_channel_names:
            channel_xml = f"<{channel_name}>{self[channel_name]}</{channel_name}>"
            channel = ET.fromstring(channel_xml)
            wavelength = channel.find(self.wavelength_name).text
            channel_dict[self.simplified_channel_name(channel_name)] = {
                self.wavelength_name: wavelength,
                "Type": "Single",
                "XML": channel_xml,
            }
        return channel_dict

    @channel_dict.setter
    def channel_dict(self, value: dict[str, dict]):
        for channel_name, channel in value.items():
            channel_name = self.empower_channel_name(channel_name)
            old_xml = f"<{channel_name}>{self[channel_name]}</{channel_name}>"
            old_channel = ET.fromstring(old_xml)
            for setting_name, setting_value in channel.items():
                if setting_name != "XML":
                    old_channel.find(setting_name).text = str(setting_value)
            channel_str = ET.tostring(old_channel).decode()
            channel_str = channel_str.replace(f"<{channel_name}>", "")
            channel_str = channel_str.replace(f"</{channel_name}>", "")
            self[channel_name] = channel_str


class PDAMethod(Detector):
    wavelength_name = "Wavelength1"

    @property
    def channel_dict(self) -> dict[str, dict]:

        # Single wavelength channels
        list_of_channel_names = [f"Channel{num}" for num in range(1, 9)]
        channel_dict = {}
        for channel_name in list_of_channel_names:
            channel_xml = f"<{channel_name}>{self[channel_name]}</{channel_name}>"
            channel = ET.fromstring(channel_xml)
            wavelength = channel.find(self.wavelength_name).text
            enabled = to_bool(channel.find("Enable").text)
            channel_dict[channel_name] = {
                self.wavelength_name: wavelength,
                "Enable": enabled,
                "Type": "Single",
                "XML": channel_xml,
            }

        spectral_channel_xml = (
            f"<SpectralChannel>{self['SpectralChannel']}</SpectralChannel>"
        )
        spectral_channel = ET.fromstring(spectral_channel_xml)
        start_wavelength = spectral_channel.find("StartWavelength").text
        end_wavelength = spectral_channel.find("EndWavelength").text
        enabled = to_bool(spectral_channel.find("Enable").text)
        channel_dict["SpectralChannel"] = {
            "StartWavelength": start_wavelength,
            "EndWavelength": end_wavelength,
            "Enable": enabled,
            "Type": "Spectral",
            "XML": spectral_channel_xml,
        }

        return channel_dict

    @channel_dict.setter
    def channel_dict(self, value: dict[str, dict]):
        for channel_name, channel in value.items():
            old_xml = f"<{channel_name}>{self[channel_name]}</{channel_name}>"
            old_channel = ET.fromstring(old_xml)
            if channel_name.startswith("Channel"):
                for setting_name, setting_value in channel.items():
                    if setting_name != "XML":
                        if setting_name == "Enable":
                            setting_value = to_string(setting_value)
                        old_channel.find(setting_name).text = str(setting_value)
                channel_str = ET.tostring(old_channel).decode()
                channel_str = channel_str.replace(f"<{channel_name}> ", "")
                channel_str = channel_str.replace(f" </{channel_name}>", "")
                self[channel_name] = channel_str
            elif channel_name == "SpectralChannel":
                for setting_name, setting_value in channel.items():
                    if setting_name != "XML":
                        if setting_name == "Enable":
                            setting_value = to_string(setting_value)
                        old_channel.find(setting_name).text = str(setting_value)
                channel_str = ET.tostring(old_channel).decode()
                channel_str = channel_str.replace(f"<{channel_name}> ", "")
                channel_str = channel_str.replace(f" </{channel_name}>", "")
                self[channel_name] = channel_str
            else:
                raise ValueError(f"Invalid channel type: {old_channel.get('Type')}")


class FLRMethod(Detector):
    @property
    def channel_dict(self) -> list[dict]:
        channel_dict = {}
        channel_name_list = [
            self.empower_channel_name(f"Channel{num}") for num in range(1, 5)
        ]
        for channel_name in channel_name_list:
            try:
                channel_xml = f"<{channel_name}>{self[channel_name]}</{channel_name}>"
            except KeyError:
                logger.debug(f"No channel named {channel_name}")
                continue
            channel = ET.fromstring(channel_xml)
            enabled = to_bool(channel.find("Enable").text)
            excitiation_wavelength = channel.find("Excitation").text
            emmision_wavelength = channel.find("Emission").text
            name = channel.find("Name").text
            channel_dict[self.simplified_channel_name(channel_name)] = {
                "Enable": enabled,
                "Type": "Single",
                "Name": name,
                "Excitation": excitiation_wavelength,
                "Emission": emmision_wavelength,
                "XML": channel_xml,
            }
        return channel_dict

    @channel_dict.setter
    def channel_dict(self, value: dict[str, dict]):
        for channel_name, channel in value.items():
            channel_name = self.empower_channel_name(channel_name)
            old_xml = f"<{channel_name}>{self[channel_name]}</{channel_name}>"
            old_channel = ET.fromstring(old_xml)
            if channel_name.startswith("Channel"):
                for setting_name, setting_value in channel.items():
                    if setting_name != "XML":
                        if setting_name == "Enable":
                            setting_value = to_string(setting_value)
                        old_channel.find(setting_name).text = str(setting_value)
                excitation = old_channel.find("Excitation").text
                emission = old_channel.find("Emission").text
                name = f"AcqFlrCh{channel_name[-1]}x{excitation}e{emission}"
                old_channel.find("Name").text = name
                channel_str = ET.tostring(old_channel).decode()
                channel_str = channel_str.replace(f"<{channel_name}> ", "")
                channel_str = channel_str.replace(f" </{channel_name}>", "")
                self[channel_name] = channel_str


class RIMethod(Detector):
    @property
    def channel_dict(self) -> dict[str, dict]:
        pass
