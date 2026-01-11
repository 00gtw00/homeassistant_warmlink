from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import WarmlinkApi
from .const import DEFAULT_CODES, DEFAULT_UPDATE_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class WarmlinkCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(
        self, hass: HomeAssistant, api: WarmlinkApi, update_interval: int = DEFAULT_UPDATE_INTERVAL
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval),
        )
        self.api = api

    async def _async_update_data(self) -> dict[str, Any]:
        if not self.api.token:
            token = await self.api.login()
            if not token:
                raise UpdateFailed("Login failed")

        devices = await self.api.device_list()
        result: dict[str, Any] = {"devices": {}}
        for device in devices:
            code = (
                device.get("deviceCode")
                or device.get("deviceName")
                or device.get("device_code")
                or device.get("device_name")
            )
            if not code:
                continue
            status = await self.api.get_device_status(code)
            values = await self.api.get_data_by_code(code, DEFAULT_CODES)
            result["devices"][code] = {
                "meta": device,
                "status": status,
                "values": values,
            }
        return result
