"""Config flow for Premium Bond Checker."""

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from premium_bond_checker.client import Client

from .const import CONF_HOLDER_NUMBER, DOMAIN, INTEGRATION_TITLE

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({vol.Required(CONF_HOLDER_NUMBER): str})


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> None:
    """Check we can get data for the property."""

    _LOGGER.debug("Validating Premium Bond holder number")

    client = Client()
    is_valid_holder_number = await hass.async_add_executor_job(
        client.is_holder_number_valid, data[CONF_HOLDER_NUMBER]
    )

    if not is_valid_holder_number:
        raise InvalidHolderNumber


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):  # type: ignore[call-arg]
    """Handle a config flow for Premium Bond Checker."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlow:
        """Handle the initial step."""
        if user_input is None:
            _LOGGER.debug("Showing empty form for holder number.")
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}
        user_input = {
            **user_input,
            CONF_HOLDER_NUMBER: user_input[CONF_HOLDER_NUMBER].strip(),
        }

        try:
            if not user_input[CONF_HOLDER_NUMBER]:
                raise InvalidHolderNumber

            await validate_input(self.hass, user_input)
        except InvalidHolderNumber:
            _LOGGER.debug("Premium Bond holder number is invalid")

            errors["base"] = "invalid_holder_number"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.warning(
                "Unexpected error while validating Premium Bond holder number"
            )
            errors["base"] = "unknown"

        if not errors:
            return self.async_create_entry(title=INTEGRATION_TITLE, data=user_input)

        _LOGGER.debug("Showing form with errors.")

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class InvalidHolderNumber(HomeAssistantError):
    """Error to indicate the holder number is not recognised."""
