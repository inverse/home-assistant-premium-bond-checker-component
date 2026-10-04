"""Premium Bond Checker integration."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .const import (
    BOND_PERIOD_CONFIG,
    CONF_HOLDER_NUMBER,
    COORDINATOR_CHECKER,
    COORDINATOR_NEXT_DRAW,
    DOMAIN,
)
from .coordinator import PremiumBondCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.SENSOR]


def _remove_migrated_checker_sensors(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> None:
    """Drop sensor entries left when checkers moved to binary_sensor."""
    entity_registry = er.async_get(hass)
    holder_number = config_entry.data[CONF_HOLDER_NUMBER]
    stale_ids = {
        f"premium_bond_checker-{holder_number}-{period_key}"
        for period_key in BOND_PERIOD_CONFIG
    }
    for entry in er.async_entries_for_config_entry(
        entity_registry, config_entry.entry_id
    ):
        if entry.domain != Platform.SENSOR or entry.unique_id not in stale_ids:
            continue
        entity_registry.async_remove(entry.entity_id)
        _LOGGER.info("Removed migrated sensor entity %s", entry.entity_id)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up Premium Bond Checker from a config entry."""

    _LOGGER.debug(
        "Setting up entry for holder number: %s", config_entry.data[CONF_HOLDER_NUMBER]
    )

    config_entry.async_on_unload(config_entry.add_update_listener(update_listener))
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(config_entry.entry_id, {})
    hass.data[DOMAIN][config_entry.entry_id][
        COORDINATOR_CHECKER
    ] = await create_and_update_coordinator(hass, config_entry)
    hass.data[DOMAIN][config_entry.entry_id][COORDINATOR_NEXT_DRAW] = hass.data[DOMAIN][
        config_entry.entry_id
    ][COORDINATOR_CHECKER]

    _remove_migrated_checker_sensors(hass, config_entry)

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def create_and_update_coordinator(
    hass, entry: ConfigEntry
) -> PremiumBondCoordinator:
    """Create and update a Premium Bond Checker coordinator."""
    _LOGGER.debug(
        "Registering instance for holder number: %s", entry.data[CONF_HOLDER_NUMBER]
    )
    coordinator = PremiumBondCoordinator(hass, entry.data[CONF_HOLDER_NUMBER])
    _LOGGER.debug(
        "Requesting instance update for holder number: %s",
        entry.data[CONF_HOLDER_NUMBER],
    )
    await coordinator.async_config_entry_first_refresh()

    return coordinator


async def update_listener(hass, config_entry):
    """Handle options update."""

    _LOGGER.debug(
        "Handling options change for holder number: %s",
        config_entry.data[CONF_HOLDER_NUMBER],
    )

    await hass.config_entries.async_reload(config_entry.entry_id)
