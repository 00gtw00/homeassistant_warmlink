from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries

from .const import (
    CONF_APP_ID,
    CONF_AREA_CODE,
    CONF_BASE,
    CONF_LANG,
    CONF_LOGIN_SOURCE,
    CONF_TYPE,
    DEFAULT_APP_ID,
    DEFAULT_AREA_CODE,
    DEFAULT_BASE,
    DEFAULT_LANG,
    DEFAULT_LOGIN_SOURCE,
    DEFAULT_TYPE,
    DOMAIN,
)


class WarmlinkConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            return self.async_create_entry(title=user_input["username"], data=user_input)

        schema = vol.Schema(
            {
                vol.Required("username"): str,
                vol.Required("password"): str,
                vol.Optional(CONF_BASE, default=DEFAULT_BASE): str,
                vol.Optional(CONF_LANG, default=DEFAULT_LANG): str,
                vol.Optional(CONF_LOGIN_SOURCE, default=DEFAULT_LOGIN_SOURCE): str,
                vol.Optional(CONF_AREA_CODE, default=DEFAULT_AREA_CODE): str,
                vol.Optional(CONF_APP_ID, default=DEFAULT_APP_ID): str,
                vol.Optional(CONF_TYPE, default=DEFAULT_TYPE): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)
