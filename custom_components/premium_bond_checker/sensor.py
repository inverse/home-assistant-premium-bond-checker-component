"""Support for Premium Bond Checker sensors."""

import logging
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt

from . import COORDINATOR, PremiumBondCoordinator
from .const import ATTR_HEADER, ATTR_REVEAL_BY, ATTR_TAGLINE, BOND_PERIOD_CONFIG, DOMAIN
from .entity import PremiumBondCheckerEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Premium Bond Checker sensor platform."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR]

    entities = []

    _LOGGER.debug("Adding sensor for next draw")
    entities.append(PremiumBondNextDrawSensor(coordinator))
    _LOGGER.debug("Adding sensor for next draw days remaining")
    entities.append(PremiumBondNextDrawDaysRemainingSensor(coordinator))

    for period_key, (bond_period, name) in BOND_PERIOD_CONFIG.items():
        _LOGGER.debug("Adding prize value sensor for %s", period_key)
        entities.append(
            PremiumBondPrizeValueSensor(
                coordinator,
                period_key,
                bond_period,
                name,
            )
        )

    async_add_entities(entities)


class PremiumBondPrizeValueSensor(PremiumBondCheckerEntity, SensorEntity):
    """Total prize value won for a bond period."""

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_native_unit_of_measurement = "GBP"
    _attr_suggested_display_precision = 0

    def __init__(
        self,
        coordinator: PremiumBondCoordinator,
        period_key: str,
        bond_period: str,
        name: str,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._bond_period = bond_period
        self._attr_name = f"{name} Prize"
        self._attr_unique_id = (
            f"premium_bond_checker-{coordinator.holder_number}-{period_key}-prize"
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


class PremiumBondNextDrawSensor(PremiumBondCheckerEntity, SensorEntity):
    _attr_translation_key = "next_draw"
    _attr_device_class = SensorDeviceClass.DATE

    def __init__(self, coordinator: PremiumBondCoordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Next Draw"
        self._attr_unique_id = (
            f"premium_bond_checker-{coordinator.holder_number}-next-draw"
        )

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


class PremiumBondNextDrawDaysRemainingSensor(PremiumBondCheckerEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.DAYS

    def __init__(self, coordinator: PremiumBondCoordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Next Draw Days Remaining"
        self._attr_unique_id = (
            f"premium_bond_checker-{coordinator.holder_number}-next-draw-days-remaining"
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return (
            self.coordinator.data.next_draw_data.next_draw_date - dt.now().date()
        ).days
