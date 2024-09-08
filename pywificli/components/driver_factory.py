"""Entrypoint for a client to get a suitable WifiDriver"""

from pywificli.domain.driver import IWifiDriver

# TODO should this be async?


class WifiDriverFactory:
    """Factory to discover and configure a Wifi Driver

    Args:
        sudo_password (str | None, optional): TODO. Defaults to None.
    """

    def __init__(self, sudo_password: str | None = None) -> None:
        self._sudo_password = sudo_password

    # def get_wifi_driver(self) -> IWifiDriver:
    #     # Detect OS
    #     # Detect system language
    #     # Get Wifi Driver
    #     # Do sudo stuff if needed
    #     ...
