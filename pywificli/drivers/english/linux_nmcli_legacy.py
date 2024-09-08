"""Linux NMCLI Legacy driver for English System Language"""

from pywificli.domain.driver import ConnectionState, IWifiDriver, ScanResult, ScanState
from pywificli.domain.metadata import DriverType, SystemLanguage


class EnglishLinuxNmcliLegacy(IWifiDriver):
    @property
    def driver_type(self) -> DriverType:
        return DriverType.LINUX_NMCLI_LEGACY

    @property
    def system_language(self) -> SystemLanguage:
        return SystemLanguage.ENGLISH

    async def get_available_interfaces(self) -> set[str]:
        return await super().get_available_interfaces()

    async def is_enabled(self, interface: str) -> bool:
        return await super().is_enabled(interface)

    async def scan(self, interface: str, timeout: float) -> list[ScanResult]:
        return await super().scan(interface, timeout)

    async def connect(self, interface: str, ssid: str, password: str, timeout: float) -> bool:
        return await super().connect(interface, ssid, password, timeout)

    async def disconnect(self, interface: str) -> bool:
        return await super().disconnect(interface)

    async def get_connection_state(self, interface: str) -> tuple[ConnectionState, str]:
        return super().get_connection_state(interface)

    async def get_scan_state(self, interface: str) -> ScanState:
        return super().get_scan_state(interface)

    async def enable(self, interface: str, enable: bool) -> bool:
        return await super().enable(interface, enable)
