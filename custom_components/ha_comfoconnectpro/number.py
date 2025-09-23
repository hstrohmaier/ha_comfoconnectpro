# custom_components/ha_comfoconnectpro/number.py
# neu
from __future__ import annotations

import logging
from typing import Optional, Any

from homeassistant.components.number import NumberEntity

from .entity_common import HubBackedEntity, setup_platform_from_types
from .const import NUMBER_TYPES, HaComfoConnectPRONumberEntityDescription

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up ComfoConnectPRO number entities from config entry."""
    return await setup_platform_from_types(
        hass=hass,
        entry=entry,
        async_add_entities=async_add_entities,
        types_dict=NUMBER_TYPES,
        entity_cls=ComfoConnectPRONumber,
    )


class ComfoConnectPRONumber(HubBackedEntity, NumberEntity):
    """ComfoConnectPRO Modbus number entity (rw)."""

    entity_description: HaComfoConnectPRONumberEntityDescription

    def __init__(self, platform_name, hub, device_info, description):
        super().__init__(platform_name, hub, device_info, description)
        # Mode (slider/box)
        self._attr_mode = description.mode

    def _apply_hub_payload(self, payload: Any) -> None:
        """Map hub payload to native_value."""
        self._attr_native_value = payload

    async def async_set_native_value(self, value: float) -> None:
        """Write new value via hub."""
        self._attr_native_value = value
        # Einheitliches Schreiben wie bei select/climate:
        await self._hub.setter_function_callback(self, value)

    @property
    def native_unit_of_measurement(self) -> str | None:
        return getattr(self.entity_description, "unit_of_measurement", None)

    @property
    def native_min_value(self) -> float | None:
        return getattr(self.entity_description, "min_value", None)

    @property
    def native_max_value(self) -> float | None:
        return getattr(self.entity_description, "max_value", None)

    @property
    def native_step(self) -> float | None:
        return getattr(self.entity_description, "step", None)
