"""Coordinator for Premium Bond Checker integration."""

import dataclasses
import logging
from datetime import date, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from premium_bond_checker.client import Client

from .const import CONF_HOLDER_NUMBER, DOMAIN

_LOGGER = logging.getLogger(__name__)

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

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        """Init the premium bond checker data object."""
        self.client = Client()
        self.holder_number = config_entry.data[CONF_HOLDER_NUMBER]
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=MIN_TIME_BETWEEN_UPDATES,
            config_entry=config_entry,
        )

    async def _async_update_data(self):
        """Get the latest data."""
        _LOGGER.debug(
            "Allowing instance update for holder number: %s", self.holder_number
        )
        try:
            return await self.hass.async_add_executor_job(self._fetch_all_data)
        except Exception as err:
            raise UpdateFailed(
                f"Error communicating with API: {err}", retry_after=60
            ) from err

    def _fetch_all_data(self) -> PremiumBondData:
        """Fetch all data synchronously."""
        checker_data = self.client.check(self.holder_number)
        next_draw_date = Client.next_draw()
        next_draw_reveal_by_date = Client.next_draw_results_reveal_by()

        return PremiumBondData(
            checker_data=checker_data,
            next_draw_data=NextDrawDataResult(next_draw_date, next_draw_reveal_by_date),
        )
