"""Entrypoint for a client to get a suitable WifiDriver"""

import os
import locale
import ctypes
import platform
from shutil import which
from getpass import getpass
from packaging.version import Version

from pywificli.domain.driver import IWifiDriver
from pywificli.domain.metadata import DriverType, SystemLanguage
from pywificli.drivers.english import (
    EnglishLinuxNmcliLegacy,
    EnglishLinuxWindows,
    EnglishLinuxMacOs,
    EnglishLinuxNmcli,
    EnglishLinuxWpa,
)
from pywificli.exceptions import UnsupportedSystemConfiguration
from pywificli.util import cmdOkOrRaise, cmd


class WifiDriverFactory:
    """Factory to discover and configure a Wifi Driver

    Args:
        sudo_password (str | None, optional): TODO. Defaults to None.
    """

    _driver_map: dict[tuple[SystemLanguage, DriverType], type[IWifiDriver] | None] = {
        (SystemLanguage.ENGLISH, DriverType.LINUX_NMCLI_LEGACY): EnglishLinuxNmcliLegacy,
        (SystemLanguage.ENGLISH, DriverType.LINUX_NMCLI): EnglishLinuxNmcli,
        (SystemLanguage.ENGLISH, DriverType.LINUX_WPA): EnglishLinuxWpa,
        (SystemLanguage.ENGLISH, DriverType.WINDOWS): EnglishLinuxWindows,
        (SystemLanguage.ENGLISH, DriverType.MAC_OS): EnglishLinuxMacOs,
    }

    def __init__(self, sudo_password: str | None = None) -> None:
        self._sudo_password = sudo_password

    async def _sudo_from_stdin(self) -> None:
        """Ask for sudo password input from stdin

        This method prompts the user to enter the sudo password from the command line.
        It validates the password by running a command with sudo and checking if the password is valid.

        Raises:
            RuntimeError: If the password is empty or invalid.
        """
        # Need password for sudo
        if not self._sudo_password:
            self._sudo_password = getpass("Need to run as sudo. Enter password: ")
        if not self._sudo_password:
            raise RuntimeError("Can't use sudo with empty password.")
        # TODO we probably want a non-raise version here
        # Validate password
        result = await cmd(f'echo "{self._sudo_password}" | sudo -S echo "VALID PASSWORD"')
        if not result.is_ok or "VALID PASSWORD" not in result.stdout_or_raise:
            raise RuntimeError("Invalid password")

    # TODO can we assume password is set after this?
    async def _detect_driver_type(self) -> DriverType:
        # Try netsh (Windows).
        if os.name == "nt" and which("netsh"):
            return DriverType.WINDOWS

        # try networksetup (Mac OS 10.10)
        if which("networksetup"):
            return DriverType.MAC_OS

        # Try Linux options.
        # try nmcli (Ubuntu 14.04). Allow for use in Snap Package
        if which("nmcli") or which("nmcli", path="/snap/bin/"):

            ctrl_wifi = await cmdOkOrRaise("nmcli general permissions |grep enable-disable-wifi")
            scan_wifi = await cmdOkOrRaise("nmcli general permissions |grep scan")

            if not "yes" in ctrl_wifi.stdout or not "yes" in scan_wifi.stdout:
                await self._sudo_from_stdin()

            version = (await cmdOkOrRaise("nmcli --version")).stdout.split()[-1]
            # On RHEL based systems, the version is in the form of 1.44.2-1.fc39
            # wich raises an error when trying to compare it with the Version class
            if any(c.isalpha() for c in version):
                version = version.split("-")[0]
            return DriverType.LINUX_NMCLI_LEGACY if Version(version) >= Version("0.9.9.0") else DriverType.LINUX_NMCLI
        # try nmcli (Ubuntu w/o network-manager)
        if which("wpa_supplicant"):
            await self._sudo_from_stdin()
            return DriverType.LINUX_WPA

        raise UnsupportedSystemConfiguration("Unable to find compatible wireless driver.")

    async def _detect_system_language(self) -> SystemLanguage:
        if platform.system().lower() == "windows":
            windll = getattr(ctypes, "windll").kernel32
            language = locale.windows_locale[windll.GetUserDefaultUILanguage()]
        else:
            language = os.environ["LANG"]

        try:
            return SystemLanguage(language)
        except ValueError:
            raise UnsupportedSystemConfiguration(f"Language {language} is not supported.")

    async def get_wifi_driver(self) -> IWifiDriver:
        driver_type = await self._detect_driver_type()
        system_language = await self._detect_system_language()
        if not (driverT := self._driver_map.get((system_language, driver_type))):
            raise UnsupportedSystemConfiguration(f"No supported driver for {driver_type=} {system_language=}")

        # TODO Do sudo stuff
        driver = driverT()
        return driver
