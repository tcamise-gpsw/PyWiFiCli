import pytest

from pywificli.util import cmd


@pytest.mark.asyncio
async def test_echo_cli():
    # WHEN
    response = await cmd("ls")

    # THEN
    assert response.is_ok
    assert response.stderr is None
    assert response.stdout is not None
    assert len(response.stdout) > 1
