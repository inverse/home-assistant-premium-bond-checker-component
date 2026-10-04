"""Support for Premium Bond Checker binary sensors."""

import logging
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from premium_bond_checker.models import Result

from . import COORDINATOR_CHECKER, PremiumBondCoordinator
from .const import ATTR_HEADER, ATTR_TAGLINE, BOND_PERIOD_CONFIG, DOMAIN
from .entity import PremiumBondCheckerEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Premium Bond Checker binary sensor platform."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR_CHECKER]

    entities = []
    for period_key, (bond_period, name) in BOND_PERIOD_CONFIG.items():
        _LOGGER.debug("Adding binary sensor for %s", period_key)
        entities.append(
            PremiumBondCheckerSensor(
                coordinator,
                period_key,
                bond_period,
                name,
            )
        )

    async_add_entities(entities)


class PremiumBondCheckerSensor(PremiumBondCheckerEntity, BinarySensorEntity):
    def __init__(
        self,
        coordinator: PremiumBondCoordinator,
        period_key: str,
        bond_period: str,
        name: str,
    ):
        super().__init__(coordinator)
        self._bond_period = bond_period
        self._attr_name = name
        self._attr_unique_id = (
            f"premium_bond_checker-{coordinator.holder_number}-{period_key}"
        )

    @property
    def is_on(self) -> bool:
        """Return if won"""
        _LOGGER.debug(f"Got {self.data.won} for {self.data.bond_period}")

        return self.data.won

    @property
    def data(self) -> Result:
        return self.coordinator.data.checker_data.results[self._bond_period]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return state attributes."""
        return {
            ATTR_HEADER: self.data.header,
            ATTR_TAGLINE: self.data.tagline,
        }
