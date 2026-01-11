from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorEntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import WarmlinkCoordinator


@dataclass
class WarmlinkBinaryDescription(BinarySensorEntityDescription):
    key_code: str = ""


BINARY_SENSORS: list[WarmlinkBinaryDescription] = [
    WarmlinkBinaryDescription(key="fault", name="Fault", key_code="isFault"),
    WarmlinkBinaryDescription(key="online", name="Online", key_code="status"),
]


class WarmlinkBinarySensor(CoordinatorEntity[WarmlinkCoordinator], BinarySensorEntity):
    entity_description: WarmlinkBinaryDescription

    def __init__(
        self,
        coordinator: WarmlinkCoordinator,
        device_code: str,
        description: WarmlinkBinaryDescription,
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
    def is_on(self) -> bool | None:
        status = self.coordinator.data.get("devices", {}).get(self._device_code, {}).get("status", {})
        if self.entity_description.key == "fault":
            val = status.get("isFault")
            if val is None:
                val = status.get("is_fault")
            return str(val).lower() in ("true", "1", "yes")
        if self.entity_description.key == "online":
            val = status.get("status")
            return str(val).upper() == "ONLINE"
        return None


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    coordinator: WarmlinkCoordinator = hass.data[DOMAIN][entry.entry_id]
    devices = coordinator.data.get("devices", {})
    entities = []
    for device_code in devices:
        for desc in BINARY_SENSORS:
            entities.append(WarmlinkBinarySensor(coordinator, device_code, desc))
    async_add_entities(entities)
