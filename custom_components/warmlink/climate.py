from __future__ import annotations

from typing import Any

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import ClimateEntityFeature, HVACMode
from homeassistant.const import UnitOfTemperature
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import WarmlinkCoordinator


class WarmlinkClimate(CoordinatorEntity[WarmlinkCoordinator], ClimateEntity):
    def __init__(self, coordinator: WarmlinkCoordinator, device_code: str) -> None:
        super().__init__(coordinator)
        self._device_code = device_code
        self._attr_unique_id = f"{device_code}_climate"

    @property
    def name(self) -> str:
        return f"Warmlink {self._device_code}"

    @property
    def device_info(self) -> dict[str, Any]:
        device = self._device_meta
        model = device.get("custModel") if device else None
        return {
            "identifiers": {(DOMAIN, self._device_code)},
            "name": device.get("deviceName") if device else self._device_code,
            "manufacturer": "Warmlink",
            "model": model,
            "configuration_url": "https://github.com/00gtw00/homeassistant_warmlink",
        }

    @property
    def _device_meta(self) -> dict[str, Any]:
        return self.coordinator.data.get("devices", {}).get(self._device_code, {}).get("meta", {})

    @property
    def _device_values(self) -> dict[str, Any]:
        return self.coordinator.data.get("devices", {}).get(self._device_code, {}).get("values", {})

    @property
    def hvac_mode(self) -> HVACMode:
        power = self._device_values.get("Power")
        return HVACMode.HEAT if str(power) == "1" else HVACMode.OFF

    @property
    def hvac_modes(self) -> list[HVACMode]:
        return [HVACMode.HEAT, HVACMode.OFF]

    @property
    def temperature_unit(self) -> str:
        return UnitOfTemperature.CELSIUS

    @property
    def current_temperature(self) -> float | None:
        value = self._device_values.get("T01")
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @property
    def target_temperature(self) -> float | None:
        value = self._device_values.get("R02")
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @property
    def min_temp(self) -> float:
        return 15.0

    @property
    def max_temp(self) -> float:
        return 75.0

    @property
    def supported_features(self) -> ClimateEntityFeature:
        return ClimateEntityFeature.TARGET_TEMPERATURE

    async def async_set_temperature(self, **kwargs: Any) -> None:
        temperature = kwargs.get("temperature")
        if temperature is None:
            return
        await self.coordinator.api.control(self._device_code, "R02", str(temperature))
        await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        if hvac_mode == HVACMode.OFF:
            await self.coordinator.api.control(self._device_code, "Power", "0")
        else:
            await self.coordinator.api.control(self._device_code, "Power", "1")
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self) -> None:
        await self.coordinator.api.control(self._device_code, "Power", "1")
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self) -> None:
        await self.coordinator.api.control(self._device_code, "Power", "0")
        await self.coordinator.async_request_refresh()


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    coordinator: WarmlinkCoordinator = hass.data[DOMAIN][entry.entry_id]
    devices = coordinator.data.get("devices", {})
    entities = [WarmlinkClimate(coordinator, device_code) for device_code in devices]
    async_add_entities(entities)
