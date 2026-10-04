"""Home Assistant test plugin."""

from pathlib import Path

import pytest

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture
def hass_config_dir() -> str:
    return str(Path(__file__).parent.parent)
