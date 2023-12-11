"""Config flow for Premium Bond Checker."""

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from premium_bond_checker.client import Client

from .const import CONF_HOLDER_NUMBER, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({vol.Required(CONF_HOLDER_NUMBER): str})


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> None:
    """Check we can get data for the property."""

    _LOGGER.debug("Validating holder number: %s", data[CONF_HOLDER_NUMBER])

    client = Client()
    is_valid_holder_number = await hass.async_add_executor_job(
        client.is_holder_number_valid, data[CONF_HOLDER_NUMBER]
    )

    if is_valid_holder_number:
        raise InvalidHolderNumber


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):  # type: ignore[call-arg]
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
            _LOGGER.debug(
                "Holder number is invalid: %s", user_input[CONF_HOLDER_NUMBER]
            )

            errors["base"] = "invalid_holder_number"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"

        if not errors:
            return self.async_create_entry(
                title="Premium Bond Checker", data=user_input
            )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class InvalidHolderNumber(HomeAssistantError):
    """Error to indicate the holder number is not recognised."""
