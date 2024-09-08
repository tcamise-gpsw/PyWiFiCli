"""Simple entrypoint demo"""

import asyncio
from pathlib import Path

from pywificli.components.driver_factory import WifiDriverFactory, WifiInterfaceControllerFactory
from pywificli.logging import set_file_logging_level, set_logging_level, setup_logging


async def main() -> None:
    setup_logging("__name__", Path("scan_ssids.log"))

    wifi = await WifiInterfaceControllerFactory().get_first_interface_controller()
    scan_results = await wifi.scan(10.0)
    print(scan_results)
    # if await wifi_driver.connect(interface, scan_results[0].ssid, "password", 10.0):
    #     print("Connected whoohoo!")
    # else:
    #     print("Failed to connect")
    # await asyncio.sleep(10)
    # await wifi_driver.disconnect(interface)


# Needed for poetry scripts defined in pyproject.toml
def entrypoint() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    entrypoint()
