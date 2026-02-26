from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Type, TypeVar, Callable

from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers.entity import Entity

from .const import (
    DOMAIN,
    DEFAULT_NAME,
    ATTR_MANUFACTURER,
)

import sys
import logging
from homeassistant.components.sensor import SensorDeviceClass

thismodule = sys.modules[__name__]
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)
_LOGGER.info(f"{thismodule} loaded.")


T = TypeVar("T", bound=Entity)

class HubBackedEntity(Entity):
    """Gemeinsame Basis: hält Hub-Referenz, Device-Info, Name/ID, Update-Hook."""


    # Beschreibungstyp ist je Plattform unterschiedlich (kommt aus const.py)
    entity_description: Any
    _attr_has_entity_name = True

    def __init__(self, platform_name: str, hub, device_info: dict, description: Any):
        self._platform_name = platform_name
        self._hub = hub
        self._attr_device_info = device_info
        self.entity_description = description

        # entry_id aus identifiers ziehen: {(DOMAIN, entry.entry_id)}
        entry_id = None
        identifiers = device_info.get("identifiers") or set()
        for dom, ident in identifiers:
            if dom == DOMAIN:
                entry_id = ident
                break
        self._entry_id = entry_id or platform_name  # Fallback

        self._attr_unique_id = f"{self._entry_id}-{description.key}"
        base = f"{description.key}"
        self._attr_suggested_object_id = base

    async def async_added_to_hass(self) -> None:
        self._hub.async_add_my_modbus_sensor(self._on_hub_update)

    async def async_will_remove_from_hass(self) -> None:
        self._hub.async_remove_my_modbus_sensor(self._on_hub_update)

    @callback
    def _on_hub_update(self) -> None:
        payload = self._hub.data.get(self.entity_description.key)

        try:
            self._apply_hub_payload(payload)
        except Exception as exc:
            _LOGGER.debug(
                "Apply payload failed for %s (%s): %r",
                self.entity_description.key,
                type(self).__name__,
                exc,
            )

        self.async_write_ha_state()

    # Von Subklassen überschreiben, um Hub-Daten in Entity-Attribute zu mappen
    def _apply_hub_payload(self, payload: Any) -> None:
        pass

    #@property
    #def name(self) -> str:
    #    return f"{self.entity_description.name}"

    @property
    def unique_id(self) -> Optional[str]:
        return f"{self._entry_id}_{self.entity_description.key}"


async def setup_platform_from_types(
    hass,
    entry,
    async_add_entities,
    types_dict: Dict[str, Any],
    entity_cls: Type[T],
) -> bool:
    """Einheitlicher Setup-Helper für alle Plattformen."""
    hub_name = entry.options.get(CONF_NAME, entry.data[CONF_NAME])
    hub = hass.data[DOMAIN][hub_name]["hub"]

    device_info = {
        "identifiers": {(DOMAIN, entry.entry_id)},
        "name": DEFAULT_NAME,
        "manufacturer": ATTR_MANUFACTURER,
    }

    entities: List[T] = [
        entity_cls(hub_name, hub, device_info, desc) for desc in types_dict.values()
    ]
    if not entities:
        _LOGGER.debug("No entities for %s on hub %s", entity_cls.__name__, hub_name)

    async_add_entities(entities)
    return True
