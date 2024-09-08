import logging
from pathlib import Path

import pytest

from pywificli.logging import set_logging_level, setup_logging

##############################################################################################################
#                                             Log Management
##############################################################################################################

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session", autouse=True)
def configure_logging():
    global logger
    logger = setup_logging(logger)
    set_logging_level(logging.ERROR)


@pytest.fixture(scope="module", autouse=True)
def manage_logs(request):
    top_dir_stripped = Path(*Path(request.node.name).parts[1:])
    extension_changed = Path(str(top_dir_stripped).strip(".py") + ".log")
    request.config.pluginmanager.get_plugin("logging-plugin").set_log_path(
        Path(".reports") / "logs" / extension_changed
    )


@pytest.fixture(scope="function", autouse=True)
def test_log(request):
    logging.debug("################################################################################")
    logging.debug("Test '{}' STARTED".format(request.node.nodeid))
    logging.debug("################################################################################")
