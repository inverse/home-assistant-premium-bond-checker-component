"""Premium Bond Checker integration."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from premium_bond_checker.exceptions import PremiumBondCheckerException

from .const import (
    CONF_HOLDER_NUMBER,
    COORDINATOR_CHECKER,
    COORDINATOR_NEXT_DRAW,
    DOMAIN,
    INTEGRATION_TITLE,
    build_entity_unique_id,
)
from .coordinator import PremiumBondCheckerData, PremiumBondNextDrawData

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

_LEGACY_ENTITY_UNIQUE_ID_MIGRATIONS = (
    (Platform.BINARY_SENSOR, "this_month", "this_month"),
    (Platform.BINARY_SENSOR, "last_six_months", "last_six_months"),
    (Platform.BINARY_SENSOR, "unclaimed", "unclaimed"),
    (Platform.SENSOR, "next-draw", "next_draw"),
    (Platform.SENSOR, "next-draw-days-remaining", "next_draw_days_remaining"),
)


def migrate_entry_title(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Replace a holder-number-derived config entry title."""
    if config_entry.title == config_entry.data[CONF_HOLDER_NUMBER]:
        hass.config_entries.async_update_entry(config_entry, title=INTEGRATION_TITLE)


def migrate_entity_unique_ids(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Migrate legacy entity unique IDs without renaming entity IDs."""
    entity_registry = er.async_get(hass)
    holder_number = config_entry.data[CONF_HOLDER_NUMBER]

    for entity_domain, legacy_suffix, new_key in _LEGACY_ENTITY_UNIQUE_ID_MIGRATIONS:
        legacy_unique_id = f"{DOMAIN}-{holder_number}-{legacy_suffix}"
        entity_id = entity_registry.async_get_entity_id(
            entity_domain, DOMAIN, legacy_unique_id
        )
        if entity_id is None:
            continue

        registry_entry = entity_registry.async_get(entity_id)
        if (
            registry_entry is None
            or registry_entry.config_entry_id != config_entry.entry_id
        ):
            continue

        new_unique_id = build_entity_unique_id(config_entry.entry_id, new_key)
        existing_entity_id = entity_registry.async_get_entity_id(
            entity_domain, DOMAIN, new_unique_id
        )
        if existing_entity_id is not None and existing_entity_id != entity_id:
            _LOGGER.warning("Unable to migrate a Premium Bond entity unique ID")
            continue

        try:
            entity_registry.async_update_entity(entity_id, new_unique_id=new_unique_id)
        except ValueError:
            _LOGGER.warning("Unable to migrate a Premium Bond entity unique ID")


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up Premium Bond Checker from a config entry."""

    _LOGGER.debug("Setting up Premium Bond Checker entry")

    config_entry.async_on_unload(config_entry.add_update_listener(update_listener))
    migrate_entry_title(hass, config_entry)
    migrate_entity_unique_ids(hass, config_entry)
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN].setdefault(config_entry.entry_id, {})
    hass.data[DOMAIN][config_entry.entry_id][
        COORDINATOR_CHECKER
    ] = await create_and_update_checker_coordinator(hass, config_entry)
    hass.data[DOMAIN][config_entry.entry_id][
        COORDINATOR_NEXT_DRAW
    ] = await create_and_update_next_draw_coordinator(hass, config_entry)

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def create_and_update_checker_coordinator(
    hass, entry: ConfigEntry
) -> PremiumBondCheckerData:
    """Create and update a Premium Bond Checker coordinator."""
    _LOGGER.debug("Registering Premium Bond Checker instance")
    coordinator = PremiumBondCheckerData(hass, entry.data[CONF_HOLDER_NUMBER])
    _LOGGER.debug("Requesting Premium Bond results update")
    await coordinator.async_config_entry_first_refresh()

    return coordinator


async def create_and_update_next_draw_coordinator(
    hass, entry: ConfigEntry
) -> PremiumBondNextDrawData:
    """Create and update a Premium Bond Next Draw coordinator."""
    coordinator = PremiumBondNextDrawData(hass)
    _LOGGER.debug("Requesting instance update")
    try:
        await coordinator.async_config_entry_first_refresh()
    except PremiumBondCheckerException:
        _LOGGER.error("Failed to fetch next draw date")

    return coordinator


async def update_listener(hass, config_entry):
    """Handle options update."""

    _LOGGER.debug("Handling Premium Bond Checker options change")

    await hass.config_entries.async_reload(config_entry.entry_id)
