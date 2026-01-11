from __future__ import annotations

import logging

from aiohttp import ClientSession
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .api import WarmlinkApi
from .const import DOMAIN
from .coordinator import WarmlinkCoordinator

PLATFORMS = ["climate", "sensor", "binary_sensor"]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    session: ClientSession = async_create_clientsession(hass)
    api = WarmlinkApi(
        session=session,
        username=entry.data["username"],
        password=entry.data["password"],
        base=entry.data["base"],
        lang=entry.data["lang"],
        login_source=entry.data["login_source"],
        area_code=entry.data["area_code"],
        app_id=entry.data["app_id"],
        typ=entry.data["type"],
    )
    coordinator = WarmlinkCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok and DOMAIN in hass.data:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
