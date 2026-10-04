"""Support for Premium Bond Checker sensors."""

import logging
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt

from . import COORDINATOR_CHECKER, COORDINATOR_NEXT_DRAW, PremiumBondCoordinator
from .const import (
    ATTR_HEADER,
    ATTR_REVEAL_BY,
    ATTR_TAGLINE,
    BOND_PERIOD_CONFIG,
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

    checker_coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR_CHECKER]

    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR_NEXT_DRAW]

    entities = []

    _LOGGER.debug("Adding sensor for next draw")
    entities.append(
        PremiumBondNextDrawSensor(
            coordinator,
            config_entry.data[CONF_HOLDER_NUMBER],
        )
    )
    _LOGGER.debug("Adding sensor for next draw days remaining")
    entities.append(
        PremiumBondNextDrawDaysRemainingSensor(
            coordinator,
            config_entry.data[CONF_HOLDER_NUMBER],
        )
    )

    for period_key, (bond_period, name) in BOND_PERIOD_CONFIG.items():
        _LOGGER.debug("Adding prize value sensor for %s", period_key)
        entities.append(
            PremiumBondPrizeValueSensor(
                checker_coordinator,
                config_entry.data[CONF_HOLDER_NUMBER],
                period_key,
                bond_period,
                name,
            )
        )

    async_add_entities(entities)


class PremiumBondPrizeValueSensor(CoordinatorEntity, SensorEntity):
    """Total prize value won for a bond period."""

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_native_unit_of_measurement = "GBP"
    _attr_suggested_display_precision = 0

    def __init__(
        self,
        coordinator: PremiumBondCoordinator,
        holder_number: str,
        period_key: str,
        bond_period: str,
        name: str,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._bond_period = bond_period
        self._attr_name = f"Premium Bond Checker {holder_number} {name} Prize"
        self._attr_unique_id = (
            f"premium_bond_checker-{holder_number}-{period_key}-prize"
        )

    @property
    def _result(self):
        return self.coordinator.data.checker_data.results[self._bond_period]

    @property
    def native_value(self) -> int:
        """Return the total prize value for this bond period."""
        return self._result.total_prize()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return state attributes."""
        return {
            ATTR_HEADER: self._result.header,
            ATTR_TAGLINE: self._result.tagline,
        }


class PremiumBondNextDrawSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "next_draw"
    _attr_device_class = SensorDeviceClass.DATE

    def __init__(self, coordinator: PremiumBondCoordinator, holder_number: str):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = f"Premium Bond Checker {holder_number} Next Draw"
        self._attr_unique_id = f"premium_bond_checker-{holder_number}-next-draw"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        _LOGGER.debug(f"Got next draw value of {self.coordinator.data}")

        return self.coordinator.data.next_draw_data.next_draw_date

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return state attributes."""
        return {
            ATTR_REVEAL_BY: self.coordinator.data.next_draw_data.next_draw_reveal_by_date,
        }


class PremiumBondNextDrawDaysRemainingSensor(CoordinatorEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.DAYS

    def __init__(self, coordinator: PremiumBondCoordinator, holder_number: str):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = (
            f"Premium Bond Checker {holder_number} Next Draw Days Remaining"
        )
        self._attr_unique_id = (
            f"premium_bond_checker-{holder_number}-next-draw-days-remaining"
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return (
            self.coordinator.data.next_draw_data.next_draw_date - dt.now().date()
        ).days
