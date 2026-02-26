from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass

from .entity_common import HubBackedEntity, setup_platform_from_types
from .const import SENSOR_TYPES, MySensorEntityDescription

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    return await setup_platform_from_types(
        hass=hass,
        entry=entry,
        async_add_entities=async_add_entities,
        types_dict=SENSOR_TYPES,
        entity_cls=MySensor,
    )


class MySensor(HubBackedEntity, SensorEntity):
    entity_description: MySensorEntityDescription

    def _apply_hub_payload(self, payload: Any) -> None:
        """Map hub payload to native_value.

        Für ENUM-Sensoren muss native_value der slug/key sein (z.B. 'normal_operation'),
        damit entity_component.sensor.state.<translation_key> greift.
        """
        if payload is None:
            self._attr_native_value = None
            return

        # ENUM: int -> slug mappen (falls Mapping vorhanden), str bleibt str
        if self.entity_description.device_class == SensorDeviceClass.ENUM:
            if isinstance(payload, str):
                self._attr_native_value = payload
                return

            # optionales Mapping (falls du es in der Description hinterlegt hast)
            value_map = (
                getattr(self.entity_description, "values_map", None)
                or getattr(self.entity_description, "value_map", None)
                or getattr(self.entity_description, "values", None)
            )
            if isinstance(value_map, dict):
                self._attr_native_value = value_map.get(payload, str(payload))
                return

            # fallback: wenn options vorhanden und payload ein Index ist
            opts = getattr(self.entity_description, "options", None)
            if isinstance(payload, int) and isinstance(opts, (list, tuple)) and 0 <= payload < len(opts):
                self._attr_native_value = opts[payload]
                return

        # Standard: direkt übernehmen
        self._attr_native_value = payload
