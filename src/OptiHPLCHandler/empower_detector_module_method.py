from xml.etree import ElementTree as ET

from .empower_module_method import EmpowerModuleMethod


def bool_from_string(bool_string: str) -> str:
    if bool_string == "true":
        return True
    elif bool_string == "false":
        return False
    else:
        raise ValueError(f"Invalid bool string: {bool_string}")


def string_from_bool(bool_value: bool) -> str:
    if bool_value == True:
        return "true"
    elif bool_value == False:
        return "false"
    else:
        raise ValueError(f"Invalid bool value: {bool_value}")


class Detector(EmpowerModuleMethod):
    pass


class TUVMethod(Detector):
    wavelength_name = "Wavelength"

    @property
    def lamp_enabled(self) -> bool:
        return self["Lamp"] == "true"

    @lamp_enabled.setter
    def lamp_enabled(self, value: bool):
        self["Lamp"] = "true" if value else "false"

    @property
    def channel_dict(self) -> dict[str, dict]:
        # Wavelength Name in the XML

        list_of_channel_names = ["ChannelA", "ChannelB"]
        channel_dict = {}
        for channel_name in list_of_channel_names:
            channel_xml = f"<{channel_name}>{self[channel_name]}</{channel_name}>"
            channel = ET.fromstring(channel_xml)
            wavelength = channel.find(self.wavelength_name).text
            data_mode = channel.find("DataMode").text
            channel_dict[channel_name] = {
                self.wavelength_name: wavelength,
                "Enabled": True,
                "DataMode": data_mode,
                "XML": channel_xml,
            }  # enabled True is a bit of a lie, but this brings consistency with the PDA method
        return channel_dict

    @channel_dict.setter
    def channel_dict(self, value: dict[str, dict]):
        for channel_name, channel in value.items():
            old_xml = f"<{channel_name}>{self[channel_name]}</{channel_name}>"
            old_channel = ET.fromstring(old_xml)
            for setting_name, setting_value in channel.items():
                if setting_name != "XML":
                    if setting_value == True:
                        setting_value = "true"
                    elif setting_value == False:
                        setting_value = "false"
                    old_channel.find(setting_name).text = str(setting_value)
            channel_str = ET.tostring(old_channel).decode()
            channel_str = channel_str.replace(f"<{channel_name}> ", "")
            channel_str = channel_str.replace(f" </{channel_name}>", "")
            self[channel_name] = channel_str

    # setting channel_dict by {"ChannelA": {"Wavelength": 666}}


class PDAMethod(Detector):
    wavelength_name = "Wavelength1"

    @property
    def lamp_enabled(self) -> bool:
        return self["Lamp"] == "true"

    @lamp_enabled.setter
    def lamp_enabled(self, value: bool):
        self["Lamp"] = "true" if value else "false"

    @property
    def channel_dict(self) -> dict[str, dict]:

        # Single wavelength channels
        list_of_channel_names = [f"Channel{num}" for num in range(1, 9)]
        channel_dict = {}
        for channel_name in list_of_channel_names:
            channel_xml = f"<{channel_name}>{self[channel_name]}</{channel_name}>"
            channel = ET.fromstring(channel_xml)
            wavelength = channel.find(self.wavelength_name).text
            enabled = bool_from_string(channel.find("Enable").text)
            data_mode = channel.find("DataMode").text
            channel_dict[channel_name] = {
                self.wavelength_name: wavelength,
                "Enabled": enabled,
                "DataMode": data_mode,
                "XML": channel_xml,
            }

        # Spectral channels
        # deal with that mess here
        return channel_dict


class FLRMethod(Detector):
    @property
    def channel_dict(self) -> list[dict]:
        pass


class RIMethod(Detector):
    @property
    def channel_dict(self) -> list[dict]:
        pass
