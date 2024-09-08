"""Simple entrypoint demo"""

import asyncio

# from pywificli.components.driver_factory import WifiDriverFactory


async def main() -> None:
    print("Hello!!")
    # factory = WifiDriverFactory()
    # wifi_driver = factory.get_wifi_driver()
    # interface = list(await wifi_driver.get_available_interfaces())[0]
    # scan_results = await wifi_driver.scan(interface, 10.0)
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
