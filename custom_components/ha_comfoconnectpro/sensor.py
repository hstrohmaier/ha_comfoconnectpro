# custom_components/ha_comfoconnectpro/sensor.py
# neu
from __future__ import annotations

import logging
from typing import Optional, Any

from homeassistant.components.sensor import SensorEntity

from .entity_common import HubBackedEntity, setup_platform_from_types
from .const import SENSOR_TYPES, HaComfoConnectPROSensorEntityDescription

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Zehnder ComfoConnect PRO sensor entities from config entry."""
    return await setup_platform_from_types(
        hass=hass,
        entry=entry,
        async_add_entities=async_add_entities,
        types_dict=SENSOR_TYPES,
        entity_cls=ComfoConnectPROSensor,
    )


class ComfoConnectPROSensor(HubBackedEntity, SensorEntity):
    """Zehnder ComfoConnect PRO Modbus sensor entity."""

    entity_description: HaComfoConnectPROSensorEntityDescription

    # def __init__ nicht erforderlich, verwendet __init__ aus HubBackedEntity, da keine eigenen Attribute zusätzlich angelegt werden müssen

    def _apply_hub_payload(self, payload: Any) -> None:
        """Map hub payload to native_value."""
        self._attr_native_value = payload

    # async def async_set_... entfällt, da r/o
