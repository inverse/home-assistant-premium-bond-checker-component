import logging
import time
from datetime import timedelta
from typing import Any, Dict

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator


from .const import DOMAIN, DEFAULT_SCAN_INTERVAL_WEEKS

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["binary"]


def setup_platform(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    
    username: str = entry.data[CONF_USERNAME]

    coordinator = PremiumBondCheckerDataUpdateCoordinator(
        hass
    )
    
    hass.data[DOMAIN][entry.entry_id] = coordinator
    hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    return True

    

class PremiumBondCheckerDataUpdateCoordinator(DataUpdateCoordinator[Dict[str, Any]]):
    def __init__(
        self,
        hass: HomeAssistant,
    ):
        self.hass = hass
        update_interval = timedelta(weeks=DEFAULT_SCAN_INTERVAL_WEEKS)
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=update_interval)

    async def _async_update_data(self) -> dict[str, Any]:
        client = Client()
        return client.check(premium_bond_number)
