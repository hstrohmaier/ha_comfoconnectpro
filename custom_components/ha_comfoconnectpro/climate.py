from __future__ import annotations

import logging

from homeassistant.components.climate import (
    ClimateEntity,
    HVACAction,
    HVACMode,
)
from homeassistant.components.climate.const import (
    PRESET_AWAY,
    PRESET_BOOST,
    PRESET_HOME,
    PRESET_SLEEP,
)
from homeassistant.const import ATTR_TEMPERATURE
from homeassistant.core import callback

from .const import (
    C_EXTERNAL_SETPOINT,
    C_STANDBY,
    C_SUPPLY_HUMIDITY,
    C_SUPPLY_TEMPERATURE,
    C_TEMPERATURE_PROFILE,
    C_TEMPERATURE_PROFILE_MODE,
    C_VENTILATION_PRESET,
    CLIMATE_TYPES,
    MyClimateEntityDescription,
)
from .entity_common import HubBackedEntity, setup_platform_from_types

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up climate entity from config entry."""
    return await setup_platform_from_types(
        hass=hass,
        entry=entry,
        async_add_entities=async_add_entities,
        types_dict=CLIMATE_TYPES,
        entity_cls=MyClimate,
    )


class MyClimate(HubBackedEntity, ClimateEntity):
    """Composite climate entity for the ComfoConnect PRO ventilation unit."""

    entity_description: MyClimateEntityDescription

    _PROFILE_TO_ACTION: dict[str, HVACAction] = {
        "comfort": HVACAction.FAN,
        "cool": HVACAction.COOLING,
        "warm": HVACAction.HEATING,
    }

    # Maps device ventilation preset labels to HA built-in preset names
    _DEVICE_TO_PRESET: dict[str, str] = {
        "away": PRESET_AWAY,
        "low": PRESET_SLEEP,
        "medium": PRESET_HOME,
        "high": PRESET_BOOST,
    }
    _PRESET_TO_DEVICE: dict[str, str] = {v: k for k, v in _DEVICE_TO_PRESET.items()}

    def __init__(self, platform_name, hub, device_info, description):
        super().__init__(platform_name, hub, device_info, description)
        self._attr_hvac_modes = [HVACMode.AUTO]
        self._attr_hvac_mode = HVACMode.AUTO
        self._attr_hvac_action = HVACAction.FAN
        self._attr_temperature_unit = description.temperature_unit
        self._attr_supported_features = description.supported_features
        self._attr_preset_modes = [PRESET_AWAY, PRESET_SLEEP, PRESET_HOME, PRESET_BOOST]
        self._attr_preset_mode = PRESET_HOME
        self._attr_min_temp = 18.0
        self._attr_max_temp = 29.0
        self._attr_target_temperature_step = 0.1

    @callback
    def _on_hub_update(self) -> None:
        supply_temp = self._hub.data.get(C_SUPPLY_TEMPERATURE)
        if supply_temp is not None:
            self._attr_current_temperature = float(supply_temp)

        supply_hum = self._hub.data.get(C_SUPPLY_HUMIDITY)
        if supply_hum is not None:
            self._attr_current_humidity = int(supply_hum)

        if self._hub.data.get(C_STANDBY) == "on":
            self._attr_hvac_action = HVACAction.IDLE
        else:
            profile = self._hub.data.get(C_TEMPERATURE_PROFILE)
            if profile is not None:
                self._attr_hvac_action = self._PROFILE_TO_ACTION.get(
                    profile, HVACAction.FAN
                )

        preset = self._hub.data.get(C_VENTILATION_PRESET)
        if preset is not None:
            self._attr_preset_mode = self._DEVICE_TO_PRESET.get(preset, PRESET_HOME)

        setpoint = self._hub.data.get(C_EXTERNAL_SETPOINT)
        if setpoint is not None:
            self._attr_target_temperature = float(setpoint)

        self.async_write_ha_state()

    async def async_set_temperature(self, **kwargs) -> None:
        """Set target temperature via external setpoint register."""
        temp = kwargs.get(ATTR_TEMPERATURE)
        if temp is None:
            return
        if self._hub.data.get(C_TEMPERATURE_PROFILE_MODE) == "adaptive":
            return
        await self._hub.write_entity_value(C_EXTERNAL_SETPOINT, temp)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set ventilation preset."""
        self._attr_preset_mode = preset_mode
        device_value = self._PRESET_TO_DEVICE.get(preset_mode, "medium")
        await self._hub.write_entity_value(C_VENTILATION_PRESET, device_value)
