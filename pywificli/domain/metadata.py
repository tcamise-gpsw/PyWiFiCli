"""Domain interfaces and entities describing Wifi drivers"""

import enum


class SystemLanguage(enum.Enum):
    """System language for a given Wifi Driver"""

    ENGLISH = enum.auto()  # TODO we'll probably want a value here.


class DriverType(enum.Enum):
    """The type of a given Wifi Driver"""

    LINUX_NMCLI = enum.auto()
    LINUX_NMCLI_LEGACY = enum.auto()
    LINUX_WPA = enum.auto()
    MAC_OS = enum.auto()
    WINDOWS = enum.auto()
