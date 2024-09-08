"""Utility functions"""

import asyncio
import logging
from dataclasses import dataclass
from sys import stdout

from pywificli.exceptions import CommandProcessError

logger = logging.getLogger(__name__)


@dataclass
class CmdResult:
    """All of the information about the result of a command"""

    return_code: int
    stdout: str | None
    stderr: str | None

    @property
    def is_ok(self) -> bool:
        """Was the command successful (its return code is 0)

        Returns:
            bool: True if ok, False otherwise
        """
        return self.return_code == 0

    @property
    def stdout_or_raise(self) -> str:
        if not self.stdout:
            raise ValueError("Stdout is not available")
        return self.stdout


@dataclass
class CmdResultOk(CmdResult):
    stdout: str


async def cmdOkOrRaise(command: str) -> CmdResultOk:
    """Run a command in a subprocess and return its result.

    Args:
        command (str): command to run

    Raises:
        CommandProcessError: Did not receive return code or return code was non-success

    Returns:
        CmdResult: stdout, stderr, and return code
    """
    logger.debug(f"Sending command ==> {command}")
    proc = await asyncio.create_subprocess_shell(
        command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await proc.communicate()

    if (return_code := proc.returncode) is None:
        raise CommandProcessError(command, "Did not receive return code.")
    if return_code == 0:
        logger.debug(f"Exited with {return_code}]")
    else:
        raise CommandProcessError(command, f"exited with non-success return code {return_code}")

    assert stdout
    logger.debug(f"[stdout]\n{stdout.decode()}")
    if stderr:
        logger.warning(f"[stderr]\n{stderr.decode()}")

    return CmdResultOk(
        return_code=return_code,
        stdout=stdout.decode(),
        stderr=stderr.decode() if stderr else None,
    )


async def cmd(command: str) -> CmdResult:
    """Run a command in a subprocess and return its result

    Args:
        command (str): command to run

    Raises:
        CommandProcessError: Did not receive return code

    Returns:
        CmdResult: stdout, stderr, and return code
    """
    logger.debug(f"Sending command ==> {command}")
    proc = await asyncio.create_subprocess_shell(
        command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await proc.communicate()

    if proc.returncode is None:
        raise CommandProcessError(command, "Did not receive return code.")
    if proc.returncode == 0:
        logger.debug(f"Exited with {proc.returncode}]")
    else:
        logger.warning(f"Exited with {proc.returncode}]")

    if stdout:
        logger.debug(f"[stdout]\n{stdout.decode()}")
    if stderr:
        logger.warning(f"[stderr]\n{stderr.decode()}")

    return CmdResult(
        return_code=proc.returncode,
        stdout=stdout.decode() if stdout else None,
        stderr=stderr.decode() if stderr else None,
    )
