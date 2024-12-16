"""Support for Premium Bond Checker sensors."""

import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from premium_bond_checker.client import Result

from .const import BOND_PERIODS, CONF_HOLDER_NUMBER, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Premium Bond Checker sensor platform."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    entities: list[BinarySensorEntity] = []

    holder_number = config_entry.data[CONF_HOLDER_NUMBER]

    for bond_period in BOND_PERIODS:
        _LOGGER.debug("Adding sensor for %s - %s", holder_number, bond_period)
        entities.append(
            PremiumBondCheckerSensor(coordinator, holder_number, bond_period)
        )

    async_add_entities(entities)


class PremiumBondCheckerSensor(CoordinatorEntity, BinarySensorEntity):

    _attr_has_entity_name = True
    _attr_translation_key = "premium_bond_checker"

    def __init__(self, coordinator, holder_number: str, bond_period: str):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._data = coordinator
        self._bond_period = bond_period
        self._attr_translation_placeholders = {
            "holder_number": holder_number,
            "bond_period": bond_period,
        }
        self._id = f"premium_bond_checker-{holder_number}-{bond_period}"

    @property
    def is_on(self) -> bool:
        """Return if won"""
        data: Result = self.coordinator.data.results.get(self._bond_period, {})

        _LOGGER.debug(f"Got {data.won} for {data.bond_period}")

        return data.won

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self) -> str:
        return self._id
