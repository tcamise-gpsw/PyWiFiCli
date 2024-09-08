import pytest
from pywificli.components.driver_factory import WifiDriverFactory
from pywificli.domain.metadata import DriverType, SystemLanguage


@pytest.mark.asyncio
async def test_system_language_is_detected_correctly():
    # GIVEN
    factory = WifiDriverFactory()

    # WHEN
    language = await factory._detect_system_language()

    # THEN
    assert language is SystemLanguage.ENGLISH


# TODO
# @pytest.mark.asyncio
# async def test_system_language_raises_on_failure_to_detect():
#     # GIVEN
#     factory = WifiDriverFactory()

#     # WHEN
#     language = await factory._detect_system_language()

#     # THEN
#     assert language is SystemLanguage.ENGLISH


@pytest.mark.asyncio
async def test_driver_type_is_detected_correctly():
    # GIVEN
    factory = WifiDriverFactory()

    # WHEN
    driver_type = await factory._detect_driver_type()

    # THEN
    assert driver_type is DriverType.WINDOWS
