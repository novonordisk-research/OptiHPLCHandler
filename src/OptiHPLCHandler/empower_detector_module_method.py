import logging
import re
from typing import Union
from xml.etree import ElementTree as ET
from dataclasses import dataclass

from .empower_module_method import EmpowerModuleMethod

logger = logging.getLogger(__name__)

# TUV
# Single <DataRate>SingleDataRate_20A</DataRate>\r\n    <DataMode>SingleMode_1A</DataMode>\r\n
# <DataRate>DualDataRate_1B</DataRate>\r\n    <DataMode>DualModeB_2C</DataMode>\r\n

# Dual <DataRate>DualDataRate_1B</DataRate>\r\n    <DataMode>DualModeA_1B</DataMode>\r\n
# <DataRate>DualDataRate_1B</DataRate>\r\n    <DataMode>DualModeB_2C</DataMode>\r\n


def to_bool(bool_string: Union[str, bool]) -> bool:
    if bool_string == "true" or bool_string is True:
        return True
    elif bool_string == "false" or bool_string is False:
        return False
    else:
        raise ValueError(f"Invalid bool string: {bool_string}")


def xml_compatible(value: Union[str, bool]) -> str:
    if value is True:
        value = "true"
    elif value is False:
        value = "false"
    return str(value)


class Detector(EmpowerModuleMethod):
    def simplified_channel_name(self, channel_name: str) -> str:
        # Convert "ChannelA" to "Channel1" and "ChannelB" to "Channel2"
        channel_number = ord(channel_name[-1]) - 64
        # ord converts a character into an integer, so ord("A") = 65, ord("B") = 66, ...
        if channel_number < 1:
            return channel_name
        return f"Channel{channel_number}"

    def empower_channel_name(self, channel_name: str) -> str:
        if not channel_name.startswith("Channel"):
            # For things like spectral channel
            return channel_name
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

    def create_channel_text(self, channel_name: str, change_dict: dict) -> str:
        channel_name = self.empower_channel_name(channel_name)
        old_xml = f"<{channel_name}>{self[channel_name]}</{channel_name}>"
        old_channel = ET.fromstring(old_xml)
        for setting_name, setting_value in change_dict.items():
            if setting_name != "XML":
                if old_channel.find(setting_name) is None:
                    raise KeyError(
                        f"Setting {setting_name} to {setting_value} failed. Key '{setting_name}' not found in '{channel_name}'"  # noqa: E501
                    )
                old_channel.find(setting_name).text = xml_compatible(setting_value)
        channel_str = ET.tostring(old_channel).decode()
        channel_str = channel_str.replace(f"<{channel_name}>", "")
        channel_str = channel_str.replace(f"</{channel_name}>", "")
        return channel_str


@dataclass
class TUVChannel:
    # Description ignored and just placed in xml
    wavelength: str
    datarate: str = "SingleDataRate_20A"  # DualDataRate_1B # DEAL IN MODULE
    datamode: str = "SingleMode_1A"  # DualModeA_1B / DualModeB_2C # DEAL IN MODULE
    filtertype: str = "Filter_2"
    timeconstant: str = "0.1000"  # 2.0000 # DEAL IN MODULE
    ratiominimum: str = "0.0001"
    autozerowavelength: str = "Az_3"
    autozeroinjectstart: bool = True
    autozeroeventorkey: bool = True

    def to_xml(self):
        return f"<Wavelength>{self.wavelength}</Wavelength>\r\n    <DataRate>{self.datarate}</DataRate>\r\n    <DataMode>{self.datamode}</DataMode>\r\n    <FilterType>{self.filtertype}</FilterType>\r\n    <TimeConstant>{self.timeconstant}</TimeConstant>\r\n    <RatioMinimum>{self.ratiominimum}</RatioMinimum>\r\n    <AutoZeroWavelength>{self.autozerowavelength}</AutoZeroWavelength>\r\n    <AutoZeroInjectStart>{xml_compatible(self.autozeroinjectstart)}</AutoZeroInjectStart>\r\n    <AutoZeroEventOrKey>{xml_compatible(self.autozeroeventorkey)}</AutoZeroEventOrKey>"  # noqa: E501


class TUVMethod(Detector):
    channel_names = [f"Channel{letter}" for letter in ["A", "B"]]

    @property
    def channels(self) -> list[TUVChannel]:
        channels = []
        for channel_name in self.channel_names:
            channel_xml = self[channel_name]
            channel = ET.fromstring(channel_xml)
            if not channel.Enable:
                continue
            channels.append(
                TUVChannel(
                    wavelength=channel.Wavelength,
                    datarate=channel.DataRate,
                    datamode=channel.DataMode,
                    filtertype=channel.FilterType,
                    timeconstant=channel.TimeConstant,
                    ratiominimum=channel.RatioMinimum,
                    autozerowavelength=channel.AutoZeroWavelength,
                    autozeroinjectstart=to_bool(channel.AutoZeroInjectStart),
                    autozeroeventorkey=to_bool(channel.AutoZeroEventOrKey),
                )
            )
        return channels

    @channels.setter
    def channels(self, value: list[TUVChannel]):
        if len(value) not in [1, 2]:
            raise ValueError("Invalid number of channels entered. Expected 1 or 2.")

        channel_settings = [
            {
                "datamode": "SingleMode_1A" if len(value) == 1 else "DualModeA_1B",
                "datarate": (
                    "SingleDataRate_20A" if len(value) == 1 else "DualDataRate_1B"
                ),
                "timeconstant": "0.1000" if len(value) == 1 else "2.0000",
                "channel": value[0].to_xml(),
            },
            {
                "datamode": "DualModeB_2C",
                "datarate": "DualDataRate_1B",
                "timeconstant": "2.0000",
                "channel": value[0].to_xml() if len(value) == 1 else value[1].to_xml(),
            },
        ]

        for i, settings in enumerate(channel_settings):
            self[f"Channel{chr(65 + i)}"] = (
                f"<DataRate>{settings['datarate']}</DataRate>\r\n"
                f"<DataMode>{settings['datamode']}</DataMode>\r\n"
                f"<TimeConstant>{settings['timeconstant']}</TimeConstant>\r\n"
                f"{settings['channel']}"
            )

    @property
    def wavelengths(self) -> list[str]:
        return [channel.wavelength for channel in self.channels]

    @wavelengths.setter
    def wavelengths(self, value: list[str]):
        if isinstance(value, (int, str)):
            value = [str(value)]
            self.channels = [TUVChannel(wavelength=wavelength) for wavelength in value]
        else:
            raise ValueError("Wavelengths must be a list of strings or integers.")


@dataclass
class PDAChannel:
    # Wrapper of channel name and enable handled on module method level
    # enable handled in module level
    wavelength1: str  # abs wavelength
    datamode: str = "DataModeAbsorbance_0"  # default to Absorbance
    wavelength2: str = "254"  # Used in difference/sum etc
    resolution: str = "Resolution_48"  # used in Absorbance etc
    ratio2dminimumau: str = "0.01"  # used in Ratio

    def to_xml(self) -> str:
        return f"<DataMode>{self.datamode}</DataMode>\r\n    <Wavelength1>{self.wavelength1}</Wavelength1>\r\n    <Wavelength2>{self.wavelength2}</Wavelength2>\r\n    <Resolution>{self.resolution}</Resolution>\r\n    <Ratio2DMinimumAU>{self.ratio2dminimumau}</Ratio2DMinimumAU>"


@dataclass
class PDASpectralChannel:
    start_wavelength: str
    end_wavelength: str
    enable: bool = False
    resolution: str = "Resolution_12"

    def to_xml(self) -> str:
        return f"<Enable>{xml_compatible(self.enable)}</Enable>\r\n <StartWavelength>{self.start_wavelength}</StartWavelength>\r\n    <EndWavelength>{self.end_wavelength}</EndWavelength>\r\n    <Resolution>{self.resolution}</Resolution>"


class PDAMethod(Detector):
    channel_names = [f"Channel{num}" for num in range(1, 9)]

    @property
    def channels(self) -> list[PDAChannel]:
        channels = []
        for channel_name in self.channel_names:
            channel_xml = self[channel_name]
            channel = ET.fromstring(channel_xml)
            if not channel.Enable:
                continue
            channels.append(
                PDAChannel(
                    datamode=channel.DataMode,
                    wavelength1=channel.Wavelength1,
                    wavelength2=channel.Wavelength2,
                    resolution=channel.Resolution,
                    ratio2dminimumau=channel.Ratio2DMinimumAU,
                )
            )
        return channels

    @channels.setter
    def channels(self, value: list[PDAChannel]):
        if len(value) > 8:
            raise ValueError("Too many channels")
        for channel_index in range(8):
            try:
                channel_xml = (
                    f"<Enable>true</Enable>\r\n{value[channel_index].to_xml()}"
                )
            except IndexError:
                default_pda_channel = PDAChannel(wavelength1="254")
                channel_xml = (
                    f"<Enable>false</Enable>\r\n{default_pda_channel.to_xml()}"
                )

            self[self.channel_names(channel_index)] = channel_xml

    @property
    def wavelengths(self) -> list[str]:
        return [channel.wavelength1 for channel in self.channels]

    @wavelengths.setter
    def wavelengths(self, value: list[str]):  # Deal with numbers
        if isinstance(value, (int, str)):
            value = [str(value)]
            self.channels = [PDAChannel(wavelength1=wavelength) for wavelength in value]
        else:
            raise ValueError("Wavelengths must be a list of strings or integers.")

    @property
    def spectral_channel(self) -> PDASpectralChannel:
        spectral_channel_xml = self["SpectralChannel"]
        spectral_channel = ET.fromstring(spectral_channel_xml)
        return PDASpectralChannel(
            enable=spectral_channel.Enable,
            start_wavelength=spectral_channel.StartWavelength,
            end_wavelength=spectral_channel.EndWavelength,
            resolution=spectral_channel.Resolution,
        )

    @spectral_channel.setter
    def spectral_channel(self, value: PDASpectralChannel):
        self["SpectralChannel"] = value.to_xml()

    @property
    def spectral_wavelengths(self) -> list[str]:
        return [
            self.spectral_channel.start_wavelength,
            self.spectral_channel.end_wavelength,
        ]

    @spectral_wavelengths.setter
    def spectral_wavelengths(self, value: list[str]):
        if len(value) != 2:
            raise ValueError("Invalid number of wavelengths entered. Expected 2.")
        self.spectral_channel = PDASpectralChannel(
            enable=True,
            start_wavelength=value[0],
            end_wavelength=value[1],
        )


@dataclass
class FLRChannel:
    # name: str # Emission and excitation constructed here and channel name is constructed in module level
    # description hardcoded to blank
    excitation: str
    emission: str
    enable: bool = True  # handled on module level
    datamode: str = "Emission_1F"  # Done on module level

    @property
    def name(self) -> str:
        return (
            f"AcqFlr$Ch$x{self.excitation}e{self.emission}"  # $$ to name channel after
        )

    def to_xml(self) -> str:
        return f"<Name>{self.name}</Name>\r\n <Description />\r\n    <Excitation>{self.excitation}</Excitation>\r\n    <Emission>{self.emission}</Emission>\r\n"  # noqa: E501


class FLRMethod(Detector):
    channel_names = [f"Channel{letter}" for letter in ["A", "B", "C", "D"]]

    @property
    def channels(self) -> list[FLRChannel]:
        channels = []
        for channel_name in self.channel_names:
            channel_xml = self[channel_name]
            channel = ET.fromstring(channel_xml)
            if not channel.Enable:
                continue
            channels.append(
                FLRChannel(
                    name=channel.Name,
                    excitation=channel.Excitation,
                    emission=channel.Emission,
                    enable=channel.Enable,
                    datamode=channel.DataMode,
                )
            )
        return channels

    @channels.setter
    def channels(self, value: list[FLRChannel]):
        if not 1 <= len(value) <= 4:
            raise ValueError("Invalid number of channels entered. Expected 1 to 4.")
        dict_modes = {
            1: "Emission_1F",  # ? why tho
            2: "Emission_2B",
            3: "Emission_3C",
            4: "Emission_4D",
        }
        for channel_index in range(4):
            try:
                # Correct channel name to include ChA, ChB, ChC, ChD
                name = value[channel_index].name
                name = re.sub(r"\$Ch\$", f"Ch{chr(65 + channel_index)}", name)
                value[channel_index].name = name
                # Always enable if it is in the list
                value[channel_index].enable = True
                # Ensure datamode is set to the correct enum
                value[channel_index].datamode = dict_modes[channel_index]
                channel_xml = value[channel_index].to_xml()
            except IndexError:
                default_flr_channel = FLRChannel(
                    excitation="350",
                    emission="397",
                    enable=False,
                    datamode=dict_modes[channel_index],
                )
                channel_xml = default_flr_channel.to_xml()

            self[self.channel_names(channel_index)] = channel_xml

    @property
    def wavelengths(self) -> list[tuple[str, str]]:
        return [(channel.excitation, channel.emission) for channel in self.channels]

    @wavelengths.setter
    def wavelengths(self, value: list[tuple[str, str]]):
        self.channels = [
            FLRChannel(excitation=excitation, emission=emission)
            for excitation, emission in value
        ]


class RIMethod(Detector):
    @property
    def channel_dict(self) -> dict[str, dict]:
        return {"RIChannel": {}}
