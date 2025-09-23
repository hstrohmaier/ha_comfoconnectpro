from __future__ import annotations

import logging
from typing import Optional, Any

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import callback

from .entity_common import HubBackedEntity, setup_platform_from_types
from .const import BINARYSENSOR_TYPES, MyBinarySensorEntityDescription

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up my binary sensor entities from config entry."""
    return await setup_platform_from_types(
        hass=hass,
        entry=entry,
        async_add_entities=async_add_entities,
        types_dict=BINARYSENSOR_TYPES,
        entity_cls=MyBinarySensor,
    )


class MyBinarySensor(HubBackedEntity, BinarySensorEntity):
    """My binary sensor (read-only switch states)."""

    entity_description: MyBinarySensorEntityDescription
    _attr_is_on: Optional[bool] = None

    # def __init__ nicht erforderlich, verwendet __init__ aus HubBackedEntity, da keine eigenen Attribute zusätzlich angelegt werden müssen

    def _apply_hub_payload(self, payload: Any) -> None:
        """
        Erwartete Payload aus Hub: "on" / "off" (Strings).
        Alles ≠ "off" wird als eingeschaltet interpretiert.
        """
        if payload is None:
            return
        if isinstance(payload, str):
            self._attr_is_on = payload.lower() != "off"
        else:
            # Fallback: truthy -> on
            self._attr_is_on = bool(payload)

    # async def async_set_... entfällt, da r/o
