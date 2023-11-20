"""Config flow for Premium Bond Checker."""

import logging
from typing import Any
import voluptuous as vol

from premium_bond_checker.client import Client

from homeassistant.core import HomeAssistant, callback
from homeassistant import config_entries
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, CONF_HOLDER_NUMBER

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({vol.Required(CONF_HOLDER_NUMBER): str})


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Check we can get data for the property."""

    _LOGGER.debug("Validating holder number: %s", data[CONF_HOLDER_NUMBER])

    client = await hass.async_add_executor_job(Client)

    if not client.is_holder_number_valid(data[CONF_HOLDER_NUMBER]):
        raise InvalidHolderNumber


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Premium Bond Checker."""
    
    VERSION = 1
    
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlow:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            await validate_input(self.hass, user_input)
        except InvalidHolderNumber:
            _LOGGER.debug("Holder number is invalid: %s", user_input[CONF_HOLDER_NUMBER])

            errors["base"] = "invalid_holder_number"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"


class InvalidHolderNumber(HomeAssistantError):
    """Error to indicate the holder number is not recognised."""
