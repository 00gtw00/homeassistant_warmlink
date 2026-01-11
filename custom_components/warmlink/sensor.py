from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.const import UnitOfElectricCurrent, UnitOfTemperature, UnitOfVolumeFlowRate
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import WarmlinkCoordinator


@dataclass
class WarmlinkSensorDescription(SensorEntityDescription):
    code: str = ""


SENSORS: list[WarmlinkSensorDescription] = [
    WarmlinkSensorDescription(key="outside", name="Outside", code="T04", native_unit_of_measurement=UnitOfTemperature.CELSIUS),
    WarmlinkSensorDescription(key="inlet", name="Inlet", code="T01", native_unit_of_measurement=UnitOfTemperature.CELSIUS),
    WarmlinkSensorDescription(key="outlet", name="Outlet", code="T02", native_unit_of_measurement=UnitOfTemperature.CELSIUS),
    WarmlinkSensorDescription(
        key="flow",
        name="Flow",
        code="T39",
        native_unit_of_measurement=UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
        icon="mdi:water-pump",
    ),
    WarmlinkSensorDescription(key="current", name="Current", code="InputCurrent1", native_unit_of_measurement=UnitOfElectricCurrent.AMPERE),
    WarmlinkSensorDescription(key="curve_slope", name="Curve slope", code="compensate_slope"),
    WarmlinkSensorDescription(key="curve_offset", name="Curve offset", code="compensate_offset"),
    WarmlinkSensorDescription(key="mode", name="Mode", code="Mode"),
    WarmlinkSensorDescription(key="silent", name="Silent", code="Manual-mute"),
]


class WarmlinkSensor(CoordinatorEntity[WarmlinkCoordinator], SensorEntity):
    entity_description: WarmlinkSensorDescription

    def __init__(
        self,
        coordinator: WarmlinkCoordinator,
        device_code: str,
        description: WarmlinkSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._device_code = device_code
        self._attr_unique_id = f"{device_code}_{description.key}"

    @property
    def name(self) -> str:
        return f"Warmlink {self._device_code} {self.entity_description.name}"

    @property
    def device_info(self) -> dict[str, Any]:
        device = self.coordinator.data.get("devices", {}).get(self._device_code, {}).get("meta", {})
        model = device.get("custModel") if device else None
        return {
            "identifiers": {(DOMAIN, self._device_code)},
            "name": device.get("deviceName") if device else self._device_code,
            "manufacturer": "Warmlink",
            "model": model,
            "configuration_url": "https://github.com/00gtw00/homeassistant_warmlink",
        }

    @property
    def native_value(self) -> str | float | None:
        values = self.coordinator.data.get("devices", {}).get(self._device_code, {}).get("values", {})
        value = values.get(self.entity_description.code)
        if value is None or value == "":
            return None
        if self.entity_description.native_unit_of_measurement:
            try:
                return float(value)
            except (TypeError, ValueError):
                return None
        return str(value)


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    coordinator: WarmlinkCoordinator = hass.data[DOMAIN][entry.entry_id]
    devices = coordinator.data.get("devices", {})
    entities = []
    for device_code in devices:
        for desc in SENSORS:
            entities.append(WarmlinkSensor(coordinator, device_code, desc))
    async_add_entities(entities)
