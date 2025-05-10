"""Support for Premium Bond Checker sensors."""

import logging
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from premium_bond_checker import Result

from . import COORDINATOR_CHECKER, COORDINATOR_NEXT_DRAW
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

    checker_coordinator = hass.data[DOMAIN][config_entry.entry_id][COORDINATOR_CHECKER]

    next_draw_coordinator = hass.data[DOMAIN][config_entry.entry_id][
        COORDINATOR_NEXT_DRAW
    ]

    entities = []

    _LOGGER.debug("Adding sensor for next draw")
    entities.append(
        PremiumBondNextDrawSensor(
            next_draw_coordinator,
            config_entry.data[CONF_HOLDER_NUMBER],
        )
    )

    for period_key, bond_period in BOND_PERIODS.items():
        _LOGGER.debug("Adding sensor for %s", period_key)
        entities.append(
            PremiumBondCheckerSensor(
                checker_coordinator,
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
        self._bond_period = bond_period
        self._name = (
            f"Premium Bond Checker {holder_number} {BOND_PERIODS_TO_NAME[period_key]}"
        )
        self._id = f"premium_bond_checker-{holder_number}-{period_key}"

    @property
    def is_on(self) -> bool:
        """Return if won"""
        _LOGGER.debug(f"Got {self.data.won} for {self.data.bond_period}")

        return self.data.won

    @property
    def data(self) -> Result:
        return self.coordinator.data.results[self._bond_period]

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
        return {
            ATTR_HEADER: self.data.header,
            ATTR_TAGLINE: self.data.tagline,
        }


class PremiumBondNextDrawSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, holder_number: str):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._name = f"Premium Bond Checker {holder_number} Next Draw"
        self._id = f"premium_bond_checker-{holder_number}-next-draw"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self) -> str:
        return self._id

    @property
    def native_value(self):
        """Return the state of the sensor."""

        _LOGGER.debug(f"Got next draw value of {self.coordinator.data}")

        return self.coordinator.data

    @property
    def device_class(self) -> SensorDeviceClass | str | None:
        """Return the device class of the sensor."""
        return SensorDeviceClass.DATE
