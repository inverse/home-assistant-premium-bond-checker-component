"""Support for Premium Bond Checker sensors."""

import logging
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from premium_bond_checker.client import Result

from .const import (
    ATTR_HEADER,
    ATTR_TAGLINE,
    BOND_PERIODS,
    BOND_PERIODS_TO_NAME,
    CONF_HOLDER_NUMBER,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Premium Bond Checker sensor platform."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    entities: list[BinarySensorEntity] = []

    for period_key, bond_period in BOND_PERIODS.items():
        _LOGGER.debug("Adding sensor for %s", period_key)
        entities.append(
            PremiumBondCheckerSensor(
                coordinator,
                config_entry.data[CONF_HOLDER_NUMBER],
                period_key,
                bond_period,
            )
        )

    async_add_entities(entities)


class PremiumBondCheckerSensor(CoordinatorEntity, BinarySensorEntity):
    def __init__(
        self, coordinator, holder_number: str, period_key: str, bond_period: str
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._data = coordinator
        self._bond_period = bond_period
        self._name = (
            f"Premium Bond Checker {holder_number} {BOND_PERIODS_TO_NAME[period_key]}"
        )
        self._id = f"premium_bond_checker-{holder_number}-{period_key}"

    @property
    def is_on(self) -> bool:
        """Return if won"""
        data: Result = self.coordinator.data.results[self._bond_period]

        _LOGGER.debug(f"Got {data.won} for {data.bond_period}")

        return data.won

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self) -> str:
        return self._id

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return state attributes."""
        data: Result = self.coordinator.data.results[self._bond_period]

        return {
            ATTR_HEADER: data.header,
            ATTR_TAGLINE: data.tagline,
        }
