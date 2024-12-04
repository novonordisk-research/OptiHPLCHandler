import logging
from dataclasses import dataclass
from typing import Optional, Union
from xml.etree import ElementTree as ET

from .empower_module_method import EmpowerModuleMethod

logger = logging.getLogger(__name__)


class NoWavelengthError(NotImplementedError):
    pass


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


class Channel:
    def __iter__(self):
        yield "channel_type", self.__class__.__name__
        for attr, value in self.__dict__.items():
            yield attr, value

    def __getitem__(self, item):
        return getattr(self, item)

    def convert(self):
        return self


class Detector(EmpowerModuleMethod):
    @property
    def lamp_enabled(self) -> bool:
        try:
            return self["Lamp"] == "true"
        except KeyError as me:
            raise AttributeError(
                f"Detector method {type(self).__name__} does not have a lamp setting."
            ) from me

    @lamp_enabled.setter
    def lamp_enabled(self, value: bool):
        self["Lamp"] = to_bool(value)

    @property
    def channels(self) -> list[Channel]:
        raise NotImplementedError("Detector method does not have a channel setting.")

    @property
    def wavelengths(self) -> list[str]:
        raise NoWavelengthError("Detector method does not have a wavelength setting.")

    @property
    def spectral_channel(self) -> Optional[Channel]:
        raise NoWavelengthError(
            "Detector method does not have a spectral channel setting."
        )

    @spectral_channel.setter
    def spectral_channel(self, _: Channel):
        raise NoWavelengthError("Spectral channel not settable for this module.")

    @property
    def spectral_wavelengths(self) -> list[dict[str, str]]:
        raise NoWavelengthError(
            "Detector method does not have a spectral wavelength setting."
        )

    @wavelengths.setter
    def wavelengths(self, _: list[str]):
        raise NoWavelengthError("Wavelengths not settable for this module.")

    channel_types: tuple[Channel, ...] = tuple()


@dataclass
class TUVChannel(Channel):
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
        return f"<Wavelength>{self.wavelength}</Wavelength><DataRate>{self.datarate}</DataRate><DataMode>{self.datamode}</DataMode><FilterType>{self.filtertype}</FilterType><TimeConstant>{self.timeconstant}</TimeConstant><RatioMinimum>{self.ratiominimum}</RatioMinimum><AutoZeroWavelength>{self.autozerowavelength}</AutoZeroWavelength><AutoZeroInjectStart>{xml_compatible(self.autozeroinjectstart)}</AutoZeroInjectStart><AutoZeroEventOrKey>{xml_compatible(self.autozeroeventorkey)}</AutoZeroEventOrKey>"  # noqa: E501

    def convert(self):
        return PDAChannel(wavelength1=self.wavelength)


class TUVMethod(Detector):
    channel_names = ["ChannelA", "ChannelB"]
    channel_types = (TUVChannel,)

    @property
    def channels(self) -> list[TUVChannel]:
        channels = []
        for channel_name in self.channel_names:
            channel_xml = self[channel_name]
            channel_xml = "<xml>" + channel_xml + "</xml>"  # give root
            channel = ET.fromstring(channel_xml)
            datamode = channel.find("DataMode").text
            channels.append(
                TUVChannel(
                    wavelength=channel.find("Wavelength").text,
                    datarate=channel.find("DataRate").text,
                    datamode=datamode,
                    filtertype=channel.find("FilterType").text,
                    timeconstant=channel.find("TimeConstant").text,
                    ratiominimum=channel.find("RatioMinimum").text,
                    autozerowavelength=channel.find("AutoZeroWavelength").text,
                    autozeroinjectstart=to_bool(
                        channel.find("AutoZeroInjectStart").text
                    ),
                    autozeroeventorkey=to_bool(channel.find("AutoZeroEventOrKey").text),
                )
            )
            if (
                "SingleMode" in datamode
            ):  # Only load first channel if set to single mode
                break
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
                f"<DataRate>{settings['datarate']}</DataRate>"
                f"<DataMode>{settings['datamode']}</DataMode>"
                f"<TimeConstant>{settings['timeconstant']}</TimeConstant>"
                f"{settings['channel']}"
            )

    @property
    def wavelengths(self) -> list[str]:
        return [channel.wavelength for channel in self.channels]

    @wavelengths.setter
    def wavelengths(self, value: list[str]):
        if not all(isinstance(v, (int, str)) for v in value):
            raise NoWavelengthError(
                "Wavelengths for TUV must be a list of strings or integers."
            )
        self.channels = [TUVChannel(wavelength=str(wavelength)) for wavelength in value]


@dataclass
class PDAChannel(Channel):
    # Wrapper of channel name and enable handled on module method level
    # enable handled in module level
    wavelength1: str  # abs wavelength
    wavelength2: str = "254"  # Used in difference/sum etc
    resolution: str = "Resolution_48"  # used in Absorbance etc
    datamode: str = "DataModeAbsorbance_0"  # default to Absorbance
    ratio2dminimumau: str = "0.01"  # used in Ratio

    def to_xml(self) -> str:
        return f"<DataMode>{self.datamode}</DataMode><Wavelength1>{self.wavelength1}</Wavelength1><Wavelength2>{self.wavelength2}</Wavelength2><Resolution>{self.resolution}</Resolution><Ratio2DMinimumAU>{self.ratio2dminimumau}</Ratio2DMinimumAU>"  # noqa: E501

    def convert(self):
        return TUVChannel(wavelength=self.wavelength1)


@dataclass
class PDASpectralChannel(Channel):
    start_wavelength: str
    end_wavelength: str
    resolution: str = "Resolution_12"

    def to_xml(self) -> str:
        return f"<Enable>true</Enable> <StartWavelength>{self.start_wavelength}</StartWavelength><EndWavelength>{self.end_wavelength}</EndWavelength>    <Resolution>{self.resolution}</Resolution>"  # noqa: E501


class PDAMethod(Detector):
    channel_names = [
        "Channel1",
        "Channel2",
        "Channel3",
        "Channel4",
        "Channel5",
        "Channel6",
        "Channel7",
        "Channel8",
    ]
    channel_types = (PDAChannel, PDASpectralChannel)

    @property
    def channels(self) -> list[PDAChannel]:
        channels = []
        for channel_name in self.channel_names:
            channel_xml = self[channel_name]
            channel_xml = "<xml>" + channel_xml + "</xml>"
            channel = ET.fromstring(channel_xml)
            if not channel.find("Enable").text == "true":
                continue
            channels.append(
                PDAChannel(
                    datamode=channel.find("DataMode").text,
                    wavelength1=channel.find("Wavelength1").text,
                    wavelength2=channel.find("Wavelength2").text,
                    resolution=channel.find("Resolution").text,
                    ratio2dminimumau=channel.find("Ratio2DMinimumAU").text,
                )
            )
        return channels

    @channels.setter
    def channels(self, value: list[PDAChannel]):
        if len(value) > 8:
            raise ValueError("Too many channels")
        for channel_index in range(8):
            try:
                channel_xml = f"<Enable>true</Enable>{value[channel_index].to_xml()}"
            except IndexError:
                default_pda_channel = PDAChannel(wavelength1="254")
                channel_xml = f"<Enable>false</Enable>{default_pda_channel.to_xml()}"

            self[self.channel_names[channel_index]] = channel_xml

    @property
    def wavelengths(self) -> list[str]:
        single_wavelengths = [channel.wavelength1 for channel in self.channels]
        return single_wavelengths

    @wavelengths.setter
    def wavelengths(self, value: list[str]):  # Deal with numbers
        if not all(isinstance(v, (int, str)) for v in value):
            raise NoWavelengthError(
                "Wavelengths for PDA must be a list of strings or integers."
            )
        self.channels = [
            PDAChannel(wavelength1=str(wavelength)) for wavelength in value
        ]

    @property
    def spectral_channel(self) -> Optional[PDASpectralChannel]:
        spectral_channel_xml = self["SpectralChannel"]
        spectral_channel_xml = "<xml>" + spectral_channel_xml + "</xml>"  # give root
        spectral_channel = ET.fromstring(spectral_channel_xml)
        if spectral_channel.find("Enable").text == "true":
            return PDASpectralChannel(
                start_wavelength=spectral_channel.find("StartWavelength").text,
                end_wavelength=spectral_channel.find("EndWavelength").text,
                resolution=spectral_channel.find("Resolution").text,
            )
        return None

    @spectral_channel.setter
    def spectral_channel(self, value: PDASpectralChannel):
        self["SpectralChannel"] = value.to_xml()

    @property
    def spectral_wavelengths(self) -> list[dict[str, str]]:
        if self.spectral_channel is None:
            return []
        return [
            {
                "Start Wavelength": self.spectral_channel.start_wavelength,
                "End Wavelength": self.spectral_channel.end_wavelength,
            },
        ]

    @spectral_wavelengths.setter
    def spectral_wavelengths(self, value: list[dict[str:str]]):
        if len(value) != 1:
            raise ValueError("Invalid number of scans. Should only be one.")
        value = value[0]

        if value == {}:
            self.spectral_channel = None
        self.spectral_channel = PDASpectralChannel(
            start_wavelength=value["Start Wavelength"],
            end_wavelength=value["End Wavelength"],
        )


@dataclass
class FLRChannel(Channel):
    # name: str # Emission and excitation constructed here and channel name is constructed in module level # noqa: E501
    # description hardcoded to blank
    excitation: str
    emission: str
    channel_name: str = ""  # handled on module level
    enable: bool = True  # handled on module level
    datamode: str = "Emission_1F"  # Done on module level

    @property
    def name(self) -> str:
        return f"AcqFlrCh{self.channel_name[-1]}x{self.excitation}e{self.emission}"

    def to_xml(self) -> str:
        return f"<Name>{self.name}</Name><Enable>{xml_compatible(self.enable)}</Enable><Excitation>{self.excitation}</Excitation><Emission>{self.emission}</Emission><DataMode>{self.datamode}</DataMode>"  # noqa: E501


class FLRMethod(Detector):
    channel_names = ["ChannelA", "ChannelB", "ChannelC", "ChannelD"]
    channel_types = (FLRChannel,)

    @property
    def channels(self) -> list[FLRChannel]:
        channels = []
        for channel_name in self.channel_names:
            channel_xml = self[channel_name]
            channel_xml = "<xml>" + channel_xml + "</xml>"  # give root
            channel = ET.fromstring(channel_xml)
            if channel.find("Enable").text != "true":
                continue
            # Correct channel name to include ChA, ChB, ChC, ChD
            channel_name = channel.find("Name").text
            channels.append(
                FLRChannel(
                    excitation=channel.find("Excitation").text,
                    emission=channel.find("Emission").text,
                    datamode=channel.find("DataMode").text,
                    channel_name=channel_name,
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
                # Always enable if it is in the list
                value[channel_index].channel_name = self.channel_names[channel_index]
                value[channel_index].enable = True
                # Ensure datamode is set to the correct enum
                value[channel_index].datamode = dict_modes[channel_index + 1]
                channel_xml = value[channel_index].to_xml()
            except IndexError:
                default_flr_channel = FLRChannel(
                    excitation="350",
                    emission="397",
                    enable=False,
                    datamode=dict_modes[channel_index + 1],
                    channel_name=self.channel_names[channel_index],
                )
                channel_xml = default_flr_channel.to_xml()

            self[self.channel_names[channel_index]] = channel_xml

    @property
    def wavelengths(self) -> list[dict[str, str]]:
        return [
            {
                "Excitation wavelength": channel.excitation,
                "Emission wavelength": channel.emission,
            }
            for channel in self.channels
        ]

    @wavelengths.setter
    def wavelengths(self, value: list[dict[str, str]]):
        if not all(isinstance(v, dict) for v in value):
            raise NoWavelengthError(
                "Wavelengths for FLR must be a list of dictionaries."
            )
        if len(value) not in [1, 2, 3, 4]:
            raise ValueError(
                f"Invalid number of wavelengths entered. Expected 1 to 4. Got {len(value)}"  # noqa: E501
            )
        self.channels = [
            FLRChannel(
                excitation=int(value[i]["Excitation wavelength"]),
                emission=int(value[i]["Emission wavelength"]),
            )
            for i in range(len(value))
        ]
