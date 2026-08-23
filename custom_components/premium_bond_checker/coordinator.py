"""Coordinator for Premium Bond Checker integration."""

import dataclasses
import logging
from datetime import date, timedelta

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from premium_bond_checker.client import Client

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

MIN_TIME_BETWEEN_UPDATES = timedelta(days=1)


@dataclasses.dataclass
class NextDrawDataResult:
    next_draw_date: date
    next_draw_reveal_by_date: date


@dataclasses.dataclass
class PremiumBondData:
    """Data object for the coordinator."""

    checker_data: dict
    next_draw_data: NextDrawDataResult


class PremiumBondCoordinator(DataUpdateCoordinator):
    """Unified coordinator for Premium Bond Checker."""

    def __init__(self, hass: HomeAssistant, holder_number: str):
        """Init the premium bond checker data object."""
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
            return await self.hass.async_add_executor_job(self._fetch_all_data)
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    def _fetch_all_data(self) -> PremiumBondData:
        """Fetch all data synchronously."""
        checker_data = self.client.check(self.holder_number)
        next_draw_date = Client.next_draw()
        next_draw_reveal_by_date = Client.next_draw_results_reveal_by()

        return PremiumBondData(
            checker_data=checker_data,
            next_draw_data=NextDrawDataResult(next_draw_date, next_draw_reveal_by_date),
        )
