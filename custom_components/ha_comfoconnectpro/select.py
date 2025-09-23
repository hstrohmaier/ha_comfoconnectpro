from __future__ import annotations

import logging
from typing import Optional, Any

from homeassistant.components.select import SelectEntity
from homeassistant.core import callback

from .entity_common import HubBackedEntity, setup_platform_from_types
from .const import SELECT_TYPES, MySelectEntityDescription

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up my select entities from config entry."""
    return await setup_platform_from_types(
        hass=hass,
        entry=entry,
        async_add_entities=async_add_entities,
        types_dict=SELECT_TYPES,
        entity_cls=MySelect,
    )


class MySelect(HubBackedEntity, SelectEntity):
    """My select entity."""

    entity_description: MySelectEntityDescription
    _attr_current_option: Optional[str]
    _setter_function: Optional[Any]

    def __init__(
        self,
        platform_name,
        hub,
        device_info,
        description: MySelectEntityDescription,
    ):
        super().__init__(platform_name, hub, device_info, description)
        # Optionen & Default aus der Description übernehmen
        self._attr_options = description.select_options or []
        self._attr_current_option = description.default_select_option
        self._setter_function = description.setter_function

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        self._attr_current_option = option
        # Einheitlich über Hub schreiben (bleibt kompatibel mit deiner bisherigen Logik)
        await self._hub.setter_function_callback(self, option)

    def _apply_hub_payload(self, payload: Any) -> None:
        # Erwartet String (das aktuell ausgewählte Label); toleranter Fallback auf None
        if isinstance(payload, str):
            self._attr_current_option = payload
        elif payload is not None:
            _LOGGER.debug(
                "Select %s: unerwartete Payload %r – ignoriere",
                self.entity_description.key,
                payload,
            )
