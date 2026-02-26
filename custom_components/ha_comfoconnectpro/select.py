from __future__ import annotations

import logging
import inspect
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
        self._attr_options = list(description.options or [])
        self._attr_current_option = description.default_select_option
        self._setter_function = description.setter_function

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        # option ist der Key/Slug aus self.options
        self._attr_current_option = option

        # Schreiben über bereitgestellte Setter-Funktion (falls vorhanden)
        if callable(self._setter_function):
            result = self._setter_function(self._hub, option)
            if inspect.isawaitable(result):
                await result
            return

        # Fallback: kompatibel zu bestehender Hub-API
        if hasattr(self._hub, "setter_function_callback"):
            await self._hub.setter_function_callback(self, option)
            return

        _LOGGER.debug(
            "No setter configured for select %s (%s)",
            self.entity_description.key,
            type(self).__name__,
        )

    def _apply_hub_payload(self, payload: Any) -> None:
        """Map hub payload to current_option.

        Erwartet bevorzugt den Options-Key (str). Toleriert auch Index (int).
        """
        if isinstance(payload, str):
            self._attr_current_option = payload
            return

        if isinstance(payload, int):
            opts = list(self.options or [])
            if 0 <= payload < len(opts):
                self._attr_current_option = opts[payload]
            else:
                _LOGGER.debug(
                    "Select %s: Index-Payload %r außerhalb options (%s)",
                    self.entity_description.key,
                    payload,
                    len(opts),
                )
            return

        if payload is not None:
            _LOGGER.debug(
                "Select %s: unerwartete Payload %r – ignoriere",
                self.entity_description.key,
                payload,
            )
