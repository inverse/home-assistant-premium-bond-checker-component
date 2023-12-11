""" Premium Bond Checker integration."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_HOLDER_NUMBER, DOMAIN
from .coordinator import PremiumBondCheckerData

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Premium Bond Checker from a config entry."""

    _LOGGER.debug(
        "Setting up entry for holder number: %s", entry.data[CONF_HOLDER_NUMBER]
    )

    instance = await create_and_update_instance(hass, entry)
    hass.data.setdefault(DOMAIN, {})

    hass.data[DOMAIN][entry.entry_id] = instance
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def create_and_update_instance(
    hass, entry: ConfigEntry
) -> PremiumBondCheckerData:
    """Create and update a Premium Bond Checker instance."""
    _LOGGER.debug(
        "Registering instance for holder number: %s", entry.data[CONF_HOLDER_NUMBER]
    )
    instance = PremiumBondCheckerData(hass, entry.data[CONF_HOLDER_NUMBER])
    _LOGGER.debug(
        "Requesting instance update for holder number: %s",
        entry.data[CONF_HOLDER_NUMBER],
    )
    await instance.async_config_entry_first_refresh()

    return instance
