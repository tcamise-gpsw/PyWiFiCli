"""Driver functionality domain entities and interfaces"""

import enum
from abc import ABC, abstractmethod
from dataclasses import dataclass

from pywificli.domain.metadata import DriverType, SystemLanguage


@dataclass
class ScanResult:
    """An SSID Scan Result"""

    ssid: str
    rssi: str
    # TODO what else?


class ConnectionState(enum.Enum):
    """An interface's current connection state"""

    DISCONNECTED = enum.auto()
    CONNECTING = enum.auto()
    CONNECTED = enum.auto()


class ScanState(enum.Enum):
    """An interface's current scanning state"""

    IDLE = enum.auto()
    SCANNING = enum.auto()


# TODO onDisconnect callback?
class IWifiDriver(ABC):
    """Wifi Driver Interface.

    A WiFi driver can manage all of its interfaces simultaneously.
    """

    @property
    @abstractmethod
    def driver_type(self) -> DriverType:
        """The driver type that this driver implements

        Returns:
            DriverType: Wifi Driver Type
        """

    @property
    @abstractmethod
    def language(self) -> SystemLanguage:
        """The system language of this driver

        Returns:
            SystemLanguage: Driver System Language
        """

    @property
    @abstractmethod
    def available_interfaces(self) -> set[str]:
        """Get all of the currently available WiFi interfaces

        Returns:
            set[str]: list of available interfaces
        """

    @abstractmethod
    def is_adapter_enabled(self, interface: str) -> bool:
        """Is the Wifi Adapter currently enabled?

        Args:
            interface (str): interface to use

        Returns:
            bool: True if enabled, False otherwise
        """

    @abstractmethod
    async def scan(self, interface: str, timeout: int) -> list[ScanResult]:
        """Scan for SSIDs on a given interface

        Args:
            interface (str): interface to use
            timeout (int): how long to scan for

        Returns:
            list[ScanResult]: list of available SSIDs
        """

    # TODO retries here? or above?
    @abstractmethod
    async def connect(self, interface: str, ssid: str, password: str, timeout: int) -> bool:
        """Connect to a given SSID

        Args:
            interface (str): interface to use
            ssid (str): target SSID to connect to
            password (str): password of SSID
            timeout (int): how long to attempt to connect before giving up

        Returns:
            bool: True if the connection was established, False otherwise
        """

    @abstractmethod
    async def disconnect(self, interface: str) -> bool:
        """Disconnect from the currently connected SSID on a given interface

        Args:
            interface (str): interface to disconnect

        Returns:
            bool: True if disconnection was successful, False otherwise
        """

    @abstractmethod
    def get_connection_state(self, interface: str) -> tuple[ConnectionState, str]:
        """Get the connection state of a given interface

        Args:
            interface (str): interface to query

        Returns:
            tuple[ConnectionState, str]: (ConnectionState, ssid)
        """

    @abstractmethod
    def get_scan_state(self, interface: str) -> ScanState:
        """Get the scan state of a given interface

        Args:
            interface (str): interface to query

        Returns:
            ScanState: scan state
        """

    @abstractmethod
    async def enable(self, interface: str, enable: bool) -> bool:
        """Enable or disable a given interface

        Args:
            interface (str): interface to configure
            enable (bool): True to enable, False to disable

        Returns:
            bool: True if the request was successful, False otherwise
        """
