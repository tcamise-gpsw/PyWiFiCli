"""Windows driver for English System Language"""

import enum
import asyncio
import os
import re
import html
import tempfile
import logging

from pywificli.domain.driver import ConnectionState, IWifiDriver, ScanResult, ScanState
from pywificli.domain.metadata import DriverType, SystemLanguage
from pywificli.util import cmdOkOrRaise

logger = logging.getLogger(__name__)


class EnglishLinuxWindows(IWifiDriver):
    # Used to build profile
    _template = r"""<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{ssid}</name>
    <SSIDConfig>
        <SSID>
            <name>{ssid}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>manual</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>{auth}</authentication>
                <encryption>{encrypt}</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>{passwd}</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
    <MacRandomization xmlns="http://www.microsoft.com/networking/WLAN/profile/v3">
        <enableRandomization>false</enableRandomization>
    </MacRandomization>
</WLANProfile>"""

    @property
    def driver_type(self) -> DriverType:
        return DriverType.LINUX_NMCLI_LEGACY

    @property
    def system_language(self) -> SystemLanguage:
        return SystemLanguage.ENGLISH

    # TODO move parsing out of here
    async def get_available_interfaces(self) -> set[str]:
        """Discover all available interfaces.

        # We're parsing, for example, the following line to find "Wi-Fi":
        # Name                   : Wi-Fi

        Returns:
            list[str]: List of interfaces
        """
        response = await cmdOkOrRaise("netsh wlan show interfaces")
        interfaces = set()

        # Look behind to find field, then match (non-greedy) any chars until CRLF
        match = "(?<={}).+?(?=\\r\\n)"
        for interface in re.findall(match.format("Name"), response.stdout):
            # Strip leading whitespace and then the first two chars of remaining (i.e. " :")
            interfaces.add(interface.strip()[2:])

        return interfaces

    # TODO is this global or per interface?
    async def is_enabled(self, interface: str) -> bool:
        response = await cmdOkOrRaise("netsh wlan show interfaces")
        # Is there at least one interfaces enabled?
        return "no wireless interface" not in response.stdout.lower()

    async def scan(self, interface: str, timeout: float) -> list[ScanResult]:
        response = await cmdOkOrRaise("netsh wlan show networks")
        # TODO this won't work if there are >9 ssids
        ssids = re.findall(r"(?<=^SSID\s(\d)\s:\s)(.*)$", response.stdout, flags=re.MULTILINE)
        return [ScanResult(ssid, 0) for ssid in ssids]

    async def connect(self, interface: str, ssid: str, password: str, timeout: float) -> bool:
        logger.info(f"Attempting to establish Wifi connection to {ssid}...")
        # Replace xml tokens (&, <, >, etc.)
        password = html.escape(password)
        ssid = html.escape(ssid)
        # Start fresh each time.
        await self._clean(ssid)

        # Create new profile
        output = self._template.format(ssid=ssid, auth="WPA2PSK", encrypt="AES", passwd=password)
        logger.debug(f"Using template {output}")

        # Need ugly low level mkstemp and os here because standard tempfile can't be accessed by a subprocess in Windows :(
        fd, filename = tempfile.mkstemp()
        os.write(fd, output.encode("utf-8"))
        os.close(fd)
        response = await cmdOkOrRaise(f"netsh wlan add profile filename={filename}")
        if "is added on interface" not in response.stdout:
            raise RuntimeError(response)
        os.remove(filename)

        async def wait_for_connection_state(status: ConnectionState, ssid: str) -> None:
            while (await self.get_connection_state(interface)) != (status, ssid):
                await asyncio.sleep(1)

        # TODO should we configure attempts. Or move to above layer?
        for _ in range(5):
            # Try to connect
            response = await cmdOkOrRaise(f'netsh wlan connect ssid="{ssid}" name="{ssid}" interface="{interface}"')
            if "was completed successfully" not in response.stdout:
                raise RuntimeError(response)

            wait_for_ssid_connected = asyncio.create_task(
                coro=wait_for_connection_state(ConnectionState.CONNECTED, ssid), name="wait_for_ssid_connected"
            )
            wait_for_timeout = asyncio.create_task(coro=asyncio.sleep(timeout), name="wait_for_timeout")
            finished, _ = await asyncio.wait(
                [wait_for_ssid_connected, wait_for_timeout],
                return_when=asyncio.FIRST_COMPLETED,
            )
            if ["wait_for_ssid_connected" in task.get_name() for task in finished]:
                return True
        return False

    async def disconnect(self, interface: str) -> bool:
        response = await cmdOkOrRaise(f'netsh wlan disconnect interface="{interface}"')
        return bool("completed successfully" in response.stdout.lower())

    # TODO move the parsing out of here
    async def get_connection_state(self, interface: str) -> tuple[ConnectionState, str]:
        """Get the current network SSID and state.

        # Here is an example of what we are parsing (i.e. to find FunHouse SSID):
        # Name                   : Wi-Fi
        # Description            : TP-Link Wireless USB Adapter
        # GUID                   : 093d8022-33cb-4400-8362-275eaf24cb86
        # Physical address       : 98:48:27:88:cb:18
        # State                  : connected
        # SSID                   : FunHouse

        Returns:
            tuple[Optional[str], SsidState]: Tuple of (ssid, network_state)
        """

        class ParseState(enum.Enum):
            """Current state of interface parsing"""

            PARSE_INTERFACE = enum.auto()
            PARSE_SSID = enum.auto()
            PARSE_STATE = enum.auto()

        response = await cmdOkOrRaise("netsh wlan show interfaces")
        parse_state = ParseState.PARSE_INTERFACE
        ssid: str | None = None
        network_state: str | None = None
        for field in response.stdout.split("\r\n"):
            if parse_state is ParseState.PARSE_INTERFACE:
                if "Name" in field and interface in field:
                    parse_state = ParseState.PARSE_STATE
            elif parse_state is ParseState.PARSE_STATE:
                if "State" in field:
                    network_state = field.split(":")[1].strip().lower()
                    parse_state = ParseState.PARSE_SSID
            elif parse_state is ParseState.PARSE_SSID:
                if "SSID" in field:
                    ssid = field.split(":")[1].strip()
                    break

        if network_state == "connected":
            state = ConnectionState.CONNECTED
        elif network_state == "disconnected":
            state = ConnectionState.DISCONNECTED
        else:
            state = ConnectionState.CONNECTING
        assert ssid
        return (state, ssid)

    async def get_scan_state(self, interface: str) -> ScanState:
        raise NotImplementedError

    async def enable(self, interface: str, enable: bool) -> bool:
        arg = "enable" if enable else "disable"
        response = await cmdOkOrRaise(f'netsh interface set interface "{interface}" "{arg}"')
        return "not exist" not in response.stdout

    @staticmethod
    async def _clean(ssid: str | None) -> None:
        """Disconnect and delete SSID profile.

        Args:
            ssid (str | None): name of SSID
        """
        await cmdOkOrRaise("netsh wlan disconnect")
        if ssid:
            await cmdOkOrRaise(f'netsh wlan delete profile name="{ssid}"')
