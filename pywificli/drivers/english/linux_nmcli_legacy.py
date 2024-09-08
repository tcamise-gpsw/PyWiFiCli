"""Linux NMCLI Legacy driver for English System Language"""

from pywificli.domain.driver import ConnectionState, IWifiDriver, ScanResult, ScanState
from pywificli.domain.metadata import DriverType, SystemLanguage


class EnglishLinuxNmcliLegacy(IWifiDriver):
    @property
    def _driver_type(self) -> DriverType:
        raise NotImplementedError

    @property
    def _system_language(self) -> SystemLanguage:
        raise NotImplementedError

    async def get_available_interfaces(self) -> set[str]:
        raise NotImplementedError

    async def is_enabled(self, interface: str) -> bool:
        raise NotImplementedError

    async def scan(self, interface: str, timeout: float) -> list[ScanResult]:
        raise NotImplementedError

    async def connect(self, interface: str, ssid: str, password: str, timeout: float) -> bool:
        raise NotImplementedError

    async def disconnect(self, interface: str) -> bool:
        raise NotImplementedError

    async def get_connection_state(self, interface: str) -> tuple[ConnectionState, str]:
        raise NotImplementedError

    async def get_scan_state(self, interface: str) -> ScanState:
        raise NotImplementedError

    async def enable(self, interface: str, enable: bool) -> bool:
        raise NotImplementedError
