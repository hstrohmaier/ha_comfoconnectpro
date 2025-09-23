# custom_components/ha_comfoconnectpro/switch.py
from __future__ import annotations

import logging
from typing import Optional, Any

from homeassistant.components.switch import SwitchEntity

from .entity_common import HubBackedEntity, setup_platform_from_types
from .const import BINARY_TYPES, HaComfoConnectPROBinaryEntityDescription

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up ComfoConnectPRO switch entities from config entry."""
    return await setup_platform_from_types(
        hass=hass,
        entry=entry,
        async_add_entities=async_add_entities,
        types_dict=BINARY_TYPES,
        entity_cls=ComfoConnectPROSwitch,
    )

class ComfoConnectPROSwitch(HubBackedEntity, SwitchEntity):
    """ComfoConnectPRO Modbus switch (r/w)."""

    entity_description: HaComfoConnectPROBinaryEntityDescription

    # def __init__ nicht erforderlich, verwendet __init__ aus HubBackedEntity, da keine eigenen Attribute zusätzlich angelegt werden müssen

    def _apply_hub_payload(self, payload: Any) -> None:
        """Map hub payload to on/off."""
        self._attr_is_on = self._to_bool(payload)

    @staticmethod
    def _to_bool(v: Any) -> bool:
        if isinstance(v, str):
            return not v.strip().lower() in {"off", "0", "false", "no", "aus"}
        try:
            return bool(int(v))
        except Exception:
            return bool(v)

    async def async_turn_on(self, **kwargs) -> None:
        self._attr_is_on = True
        await self._hub.setter_function_callback(self, True)

    async def async_turn_off(self, **kwargs) -> None:
        self._attr_is_on = False
        await self._hub.setter_function_callback(self, False)

    
