"""Security and privacy tests for Premium Bond Checker."""

import logging
from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from premium_bond_checker.client import BondPeriod
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.premium_bond_checker import (
    migrate_entity_unique_ids,
    migrate_entry_title,
)
from custom_components.premium_bond_checker.config_flow import (
    ConfigFlow,
    InvalidHolderNumber,
    validate_input,
)
from custom_components.premium_bond_checker.const import (
    ATTR_HEADER,
    ATTR_TAGLINE,
    CONF_HOLDER_NUMBER,
    DOMAIN,
    INTEGRATION_TITLE,
    build_entity_unique_id,
)
from custom_components.premium_bond_checker.coordinator import (
    NextDrawDataResult,
    PremiumBondCheckerData,
    PremiumBondNextDrawData,
)
from custom_components.premium_bond_checker.sensor import (
    PremiumBondCheckerSensor,
    PremiumBondNextDrawDaysRemainingSensor,
    PremiumBondNextDrawSensor,
)

HOLDER_NUMBER = "holder-number-sentinel"
ENTRY_ID = "entry-id-sentinel"


def _config_entry(
    title: str = HOLDER_NUMBER, entry_id: str = ENTRY_ID
) -> MockConfigEntry:
    return MockConfigEntry(
        domain=DOMAIN,
        entry_id=entry_id,
        title=title,
        data={CONF_HOLDER_NUMBER: HOLDER_NUMBER},
    )


def test_new_unique_ids_are_stable_and_holder_free() -> None:
    """New entity unique IDs use the config entry ID, not the holder number."""
    this_month = build_entity_unique_id(ENTRY_ID, "this_month")

    assert this_month == build_entity_unique_id(ENTRY_ID, "this_month")
    assert this_month != build_entity_unique_id("different-entry", "this_month")
    assert HOLDER_NUMBER not in this_month


def test_entity_names_and_attributes_do_not_expose_holder_number(hass) -> None:
    """Entity presentation data never includes the holder number."""
    checker_coordinator = DataUpdateCoordinator(
        hass, logging.getLogger(__name__), name="test"
    )
    checker_coordinator.data = SimpleNamespace(
        results={
            BondPeriod.THIS_MONTH: SimpleNamespace(
                won=True,
                bond_period=BondPeriod.THIS_MONTH,
                header="Prize information",
                tagline="Results available",
            )
        }
    )
    next_draw_coordinator = PremiumBondNextDrawData(hass)
    next_draw_coordinator.data = NextDrawDataResult(date(2030, 1, 1), date(2030, 1, 4))

    entities = (
        PremiumBondCheckerSensor(
            checker_coordinator, ENTRY_ID, "this_month", BondPeriod.THIS_MONTH
        ),
        PremiumBondNextDrawSensor(next_draw_coordinator, ENTRY_ID),
        PremiumBondNextDrawDaysRemainingSensor(next_draw_coordinator, ENTRY_ID),
    )

    assert all(HOLDER_NUMBER not in entity.name for entity in entities)
    assert all(HOLDER_NUMBER not in entity.unique_id for entity in entities)
    assert HOLDER_NUMBER not in str(entities[0].extra_state_attributes)
    assert entities[0].extra_state_attributes == {
        ATTR_HEADER: "Prize information",
        ATTR_TAGLINE: "Results available",
    }


@pytest.mark.asyncio
async def test_validation_and_update_errors_do_not_log_holder_number(
    hass, caplog
) -> None:
    """Unexpected validation and update failures keep the holder out of logs."""
    with patch("custom_components.premium_bond_checker.config_flow.Client") as client:
        client.return_value.is_holder_number_valid.return_value = False
        with caplog.at_level(logging.DEBUG):
            with pytest.raises(InvalidHolderNumber):
                await validate_input(hass, {CONF_HOLDER_NUMBER: HOLDER_NUMBER})

    coordinator = PremiumBondCheckerData(hass, HOLDER_NUMBER)
    coordinator.client.check = Mock(side_effect=RuntimeError(HOLDER_NUMBER))
    with caplog.at_level(logging.DEBUG):
        await coordinator._async_update_data()

    assert HOLDER_NUMBER not in caplog.text


@pytest.mark.asyncio
async def test_whitespace_only_holder_number_is_rejected(hass) -> None:
    """Whitespace-only holder numbers are rejected before any network request."""
    flow = ConfigFlow()
    flow.hass = hass

    with patch(
        "custom_components.premium_bond_checker.config_flow.validate_input",
        new_callable=AsyncMock,
    ) as validate:
        result = await flow.async_step_user({CONF_HOLDER_NUMBER: "   "})

    assert result["errors"] == {"base": "invalid_holder_number"}
    validate.assert_not_awaited()


@pytest.mark.asyncio
async def test_new_config_entry_uses_generic_title(hass) -> None:
    """New config entries do not use the holder number as their title."""
    flow = ConfigFlow()
    flow.hass = hass

    with patch(
        "custom_components.premium_bond_checker.config_flow.validate_input",
        new_callable=AsyncMock,
    ):
        result = await flow.async_step_user(
            {CONF_HOLDER_NUMBER: f"  {HOLDER_NUMBER}  "}
        )

    assert result["title"] == INTEGRATION_TITLE
    assert result["data"] == {CONF_HOLDER_NUMBER: HOLDER_NUMBER}


def test_legacy_title_migrates_but_user_title_is_preserved(hass) -> None:
    """Only titles that equal the stored holder number are replaced."""
    legacy_entry = _config_entry()
    legacy_entry.add_to_hass(hass)
    migrate_entry_title(hass, legacy_entry)

    custom_entry = _config_entry("My household Premium Bonds", "custom-entry-id")
    custom_entry.add_to_hass(hass)
    migrate_entry_title(hass, custom_entry)

    assert legacy_entry.title == INTEGRATION_TITLE
    assert custom_entry.title == "My household Premium Bonds"


def test_legacy_unique_id_migrates_without_renaming_entity_id(hass) -> None:
    """Legacy entities retain their entity ID while receiving an opaque unique ID."""
    config_entry = _config_entry()
    config_entry.add_to_hass(hass)
    entity_registry = er.async_get(hass)
    legacy_unique_id = f"{DOMAIN}-{HOLDER_NUMBER}-this_month"
    registry_entry = entity_registry.async_get_or_create(
        "binary_sensor",
        DOMAIN,
        legacy_unique_id,
        suggested_object_id="legacy_premium_bonds",
        config_entry=config_entry,
    )

    migrate_entity_unique_ids(hass, config_entry)

    migrated_entry = entity_registry.async_get(registry_entry.entity_id)
    assert migrated_entry is not None
    assert migrated_entry.entity_id == registry_entry.entity_id
    assert migrated_entry.unique_id == build_entity_unique_id(ENTRY_ID, "this_month")
