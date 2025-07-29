"""Coordinator for Premium Bond Checker integration."""

import dataclasses
import logging
from datetime import date, timedelta

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from premium_bond_checker.client import Client

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

MIN_TIME_BETWEEN_UPDATES = timedelta(days=1)


@dataclasses.dataclass
class NextDrawDataResult:
    next_draw_date: date
    next_draw_reveal_by_date: date


class PremiumBondNextDrawData(DataUpdateCoordinator):
    """Get the latest data and update the states."""

    def __init__(self, hass: HomeAssistant):
        """Init the premium bond checker data object."""

        self.hass = hass

        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=MIN_TIME_BETWEEN_UPDATES
        )

    async def _async_update_data(self):
        """Get the latest data."""
        _LOGGER.debug("Allowing instance update")
        try:
            next_draw_data = await self.hass.async_add_executor_job(
                Client.next_draw,
            )
            next_draw_reveal_by_date = await self.hass.async_add_executor_job(
                Client.next_draw_results_reveal_by,
            )

            return NextDrawDataResult(next_draw_data, next_draw_reveal_by_date)
        except Exception as err:
            _LOGGER.warning("Experienced unexpected error while updating: %s", err)


class PremiumBondCheckerData(DataUpdateCoordinator):
    """Get the latest data and update the states."""

    def __init__(self, hass: HomeAssistant, holder_number: str):
        """Init the premium bond checker data object."""

        self.hass = hass
        self.client = Client()
        self.holder_number = holder_number

        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=MIN_TIME_BETWEEN_UPDATES
        )

    async def _async_update_data(self):
        """Get the latest data."""
        _LOGGER.debug(
            "Allowing instance update for holder number: %s", self.holder_number
        )
        try:
            return await self.hass.async_add_executor_job(
                self.client.check, self.holder_number
            )
        except Exception as err:
            _LOGGER.warning("Experienced unexpected error while updating: %s", err)
