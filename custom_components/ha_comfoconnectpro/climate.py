# custom_components/ha_comfoconnectpro/climate.py
# neu
from __future__ import annotations

import logging
from typing import Optional, Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.core import callback

from .entity_common import HubBackedEntity, setup_platform_from_types
from .const import CLIMATE_TYPES, HaComfoConnectPROClimateEntityDescription

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Zehnder ComfoConnect PRO climate entities from config entry."""
    return await setup_platform_from_types(
        hass=hass,
        entry=entry,
        async_add_entities=async_add_entities,
        types_dict=CLIMATE_TYPES,
        entity_cls=ComfoConnectPROClimate,
    )


class ComfoConnectPROClimate(HubBackedEntity, ClimateEntity):
    """Zehnder ComfoConnect PRO Modbus Climate (reiner Sollwert-Steller)."""

    entity_description: HaComfoConnectPROClimateEntityDescription

    def __init__(self, platform_name, hub, device_info, description):
        super().__init__(platform_name, hub, device_info, description)
        # Nur AUTO anzeigen, damit kein manueller HVAC-Mode erwartet wird
        self._attr_hvac_modes = [HVACMode.AUTO]
        self._attr_hvac_mode = HVACMode.AUTO

        # Statische Eigenschaften aus der Description
        self._attr_temperature_unit = description.temperature_unit
        self._attr_min_temp = description.min_value
        self._attr_max_temp = description.max_value
        self._attr_target_temperature_low = description.min_value
        self._attr_target_temperature_high = description.max_value
        self._attr_target_temperature_step = description.step
        self._attr_supported_features = (
            description.supported_features or ClimateEntityFeature.TARGET_TEMPERATURE
        )

    def _apply_hub_payload(self, payload: Any) -> None:
        """
        Erwartet ein Dict wie:
          {"temperature": float,
           "target_temp_low": float | None,
           "target_temp_high": float | None}
        """
        if not isinstance(payload, dict):
            return

        temp = payload.get("temperature")
        if temp is not None:
            self._attr_current_temperature = float(temp)
            self._attr_target_temperature = float(temp)

        lo = payload.get("target_temp_low")
        if lo is not None:
            self._attr_target_temperature_low = float(lo)

        hi = payload.get("target_temp_high")
        if hi is not None:
            self._attr_target_temperature_high = float(hi)

    def set_temperature(self, **kwargs) -> None:
        """
        Von HA aufgerufen. Reicht die gewünschten Werte an den Hub weiter.
        Wir delegieren synchron an den Hub via create_task.
        """
        # Attribute lokal vorab setzen (optimiertes UI-Feedback)
        if "temperature" in kwargs:
            t = float(kwargs["temperature"])
            self._attr_current_temperature = t
            self._attr_target_temperature = t
        if "target_temp_low" in kwargs:
            self._attr_target_temperature_low = float(kwargs["target_temp_low"])
        if "target_temp_high" in kwargs:
            self._attr_target_temperature_high = float(kwargs["target_temp_high"])

        # Tatsächliches Schreiben an den Hub
        self.hass.add_job(self._hub.setter_function_callback(self, kwargs))

    async def async_set_temperature(self, **kwargs) -> None:
        """
        Async-Variante (einige Frontends/Automationen nutzen diese).
        Spiegelt die Logik von set_temperature.
        """
        if "temperature" in kwargs:
            t = float(kwargs["temperature"])
            self._attr_current_temperature = t
            self._attr_target_temperature = t
        if "target_temp_low" in kwargs:
            self._attr_target_temperature_low = float(kwargs["target_temp_low"])
        if "target_temp_high" in kwargs:
            self._attr_target_temperature_high = float(kwargs["target_temp_high"])

        await self._hub.setter_function_callback(self, kwargs)
