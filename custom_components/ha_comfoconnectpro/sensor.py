from __future__ import annotations

import logging
import math
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.core import callback

from .entity_common import HubBackedEntity, get_hub_and_device_info, setup_platform_from_types
from .const import (
    SENSOR_TYPES,
    MySensorEntityDescription,
    DerivedSensorSpec,
    DEW_POINT_SENSOR_TYPES,
    ABSOLUTE_HUMIDITY_SENSOR_TYPES,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    await setup_platform_from_types(
        hass=hass,
        entry=entry,
        async_add_entities=async_add_entities,
        types_dict=SENSOR_TYPES,
        entity_cls=MySensor,
    )

    hub_name, hub, device_info = get_hub_and_device_info(hass, entry)
    derived = [
        DewPointSensor(hub_name, hub, device_info, spec)
        for spec in DEW_POINT_SENSOR_TYPES.values()
    ] + [
        AbsoluteHumiditySensor(hub_name, hub, device_info, spec)
        for spec in ABSOLUTE_HUMIDITY_SENSOR_TYPES.values()
    ]
    async_add_entities(derived)
    return True


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
            if (
                isinstance(payload, int)
                and isinstance(opts, (list, tuple))
                and 0 <= payload < len(opts)
            ):
                self._attr_native_value = opts[payload]
                return

        # Standard: direkt übernehmen
        self._attr_native_value = payload


class _DerivedSensorBase(HubBackedEntity, SensorEntity):
    """Base for sensors computed from a temperature + relative humidity pair."""

    def __init__(self, platform_name: str, hub, device_info: dict, spec: DerivedSensorSpec):
        super().__init__(platform_name, hub, device_info, spec.description)
        self._temp_key = spec.temp_key
        self._humidity_key = spec.humidity_key

    @callback
    def _on_hub_update(self) -> None:
        T = self._hub.data.get(self._temp_key)
        RH = self._hub.data.get(self._humidity_key)
        if T is None or RH is None or not (0 < RH <= 100):
            self._attr_native_value = None
        else:
            try:
                self._attr_native_value = round(self._compute(T, RH), 1)
            except Exception:
                self._attr_native_value = None
        self.async_write_ha_state()

    def _compute(self, T: float, RH: float) -> float:
        raise NotImplementedError


class DewPointSensor(_DerivedSensorBase):
    """Dew point via Magnus formula (August-Roche-Magnus approximation)."""

    _A = 17.625
    _B = 243.04  # °C

    def _compute(self, T: float, RH: float) -> float:
        gamma = (self._A * T) / (self._B + T) + math.log(RH / 100.0)
        return self._B * gamma / (self._A - gamma)


class AbsoluteHumiditySensor(_DerivedSensorBase):
    """Absolute humidity in g/m³."""

    def _compute(self, T: float, RH: float) -> float:
        return (6.112 * math.exp((17.67 * T) / (T + 243.5)) * RH * 2.1674) / (273.15 + T)
