"""Duplicate holder numbers abort the config flow."""

from unittest.mock import patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.premium_bond_checker.const import CONF_HOLDER_NUMBER, DOMAIN

HOLDER = "123456789"

pytestmark = pytest.mark.asyncio


@pytest.fixture(autouse=True)
def _enable_custom_integrations(enable_custom_integrations: None) -> None:
    return None


async def test_second_holder_aborts_and_stores_unique_id(hass: HomeAssistant) -> None:
    with (
        patch(
            "custom_components.premium_bond_checker.async_setup_entry",
            return_value=True,
        ),
        patch(
            "custom_components.premium_bond_checker.config_flow.Client.is_holder_number_valid",
            return_value=True,
        ),
    ):
        created = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": "user"},
            data={CONF_HOLDER_NUMBER: HOLDER},
        )

    assert created["type"] is FlowResultType.CREATE_ENTRY
    assert hass.config_entries.async_entries(DOMAIN)[0].unique_id == HOLDER

    duplicate = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": "user"},
        data={CONF_HOLDER_NUMBER: HOLDER},
    )
    assert duplicate["type"] is FlowResultType.ABORT
    assert duplicate["reason"] == "already_configured"


async def test_existing_entry_without_unique_id_aborts(hass: HomeAssistant) -> None:
    MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOLDER_NUMBER: HOLDER},
        unique_id=None,
    ).add_to_hass(hass)

    with patch(
        "custom_components.premium_bond_checker.config_flow.Client.is_holder_number_valid",
        return_value=True,
    ) as is_valid:
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": "user"},
            data={CONF_HOLDER_NUMBER: HOLDER},
        )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
    is_valid.assert_not_called()
