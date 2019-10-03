"""Threatify Core Package."""

import logging
import logging.config
import os.path

from .app_objects import App, app  # pylint: disable=E


def init(**custom_settings):
    """Initialize application configuration."""
    configure_logging = custom_settings.get("configure_logging", True)

    config_path = os.path.join(
        os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ),
        "config.ini",
    )
    # print(config_path)
    App(config_path, configure_logging=configure_logging)

    log = logging.getLogger("record_keeper")
    log.debug("Initialized!")
