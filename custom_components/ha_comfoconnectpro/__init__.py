"""The Zehnder ComfoConnect PRO integration."""

from __future__ import annotations

import asyncio
import struct
from datetime import timedelta
import threading
from typing import Any, Dict, Iterable, Tuple, Optional


from pymodbus.client import ModbusTcpClient

# from pymodbus.payload import Endian
from pymodbus.exceptions import ConnectionException

# from pymodbus.payload import BinaryPayloadDecoder
import voluptuous as vol

from homeassistant.helpers.entity import Entity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    # CONF_DEVICE,
    Platform,
)
from homeassistant.core import HomeAssistant, callback
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.event import async_track_time_interval

from . import const
from .const import (
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    CONF_HOSTID,
    ENTITIES_DICT,
    BINARYSENSOR_TYPES,
    SENSOR_TYPES,
    SELECT_TYPES,
    CLIMATE_TYPES,
    NUMBER_TYPES,
    BINARY_TYPES,
    get_entity_switch,
    get_entity_type,
    get_entity_select,
    get_entity_factor,
    get_entity_max,
    get_entity_min,
    get_entity_reg,
    get_entity_props,
    is_entity_readonly,
    is_entity_switch,
    is_entity_select,
    is_entity_climate,
    C_MIN_INPUT_REGISTER,
    C_MAX_INPUT_REGISTER,
    C_MIN_HOLDING_REGISTER,
    C_MAX_HOLDING_REGISTER,
    C_MIN_COILS,
    C_MAX_COILS,
    C_MIN_DISCRETE_INPUTS,
    C_MAX_DISCRETE_INPUTS,
)


import logging

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)
_LOGGER.info("ha_comfoconnectpro loaded")

PLATFORMS = [
    Platform.BINARY_SENSOR,  # BINARYSENSOR_TYPES (r/o)
    Platform.SENSOR,  # SENSOR_TYPES (r/o)
    Platform.SELECT,  # SELECT_TYPES (r/w)
    Platform.SWITCH,  # BINARY_TYPES (r/w)
    Platform.CLIMATE,  # CLIMATE_TYPES (r/w)
    Platform.NUMBER,  # NUMBER_TYPES (r/w)
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up a Zehnder ComfoConnect PRO modbus."""
    _LOGGER.info(entry)
    hass.data.setdefault(DOMAIN, {})

    host = entry.data.get(CONF_HOST)
    name = entry.data.get(CONF_NAME)
    port = entry.data.get(CONF_PORT)
    scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    if scan_interval < 5:
        scan_interval = DEFAULT_SCAN_INTERVAL
    hostid = entry.data.get(CONF_HOSTID)

    _LOGGER.info("Setup %s.%s", DOMAIN, name)

    hub = HaComfoConnectPROModbusHub(hass, name, host, port, scan_interval, hostid)
    # """Register the hub."""
    hass.data[DOMAIN][name] = {"hub": hub}

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass, entry):
    """Unload Zehnder ComfoConnect PRO modbus entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if not unload_ok:
        return False

    hass.data[DOMAIN].pop(entry.data["name"])
    return True


class HaComfoConnectPROModbusHub:
    """Thread safe wrapper class for pymodbus."""

    def __init__(
        self,
        hass: HomeAssistant,
        name,
        host,
        port,
        scan_interval,
        hostid,
    ):
        """Initialize the Modbus hub."""
        self._hass = hass
        self._client = ModbusTcpClient(host=host, port=port, timeout=3, retries=3)
        self._lock = threading.Lock()
        self._name = name
        self._scan_interval = timedelta(seconds=scan_interval)
        self._hostid = hostid
        self._unsub_interval_method = None
        self._sensors = []
        self.data: Dict[str, Any] = {}

    @callback
    def async_add_hacomfoconnectpro_modbus_sensor(self, update_callback):
        """Listen for data updates."""
        # This is the first sensor, set up interval.
        if not self._sensors:
            self.connect()
            self._unsub_interval_method = async_track_time_interval(
                self._hass, self.async_refresh_modbus_data, self._scan_interval
            )

        self._sensors.append(update_callback)

    @callback
    def async_remove_hacomfoconnectpro_modbus_sensor(self, update_callback):
        """Remove data update."""
        self._sensors.remove(update_callback)

        if not self._sensors:
            # """stop the interval timer upon removal of last sensor"""
            self._unsub_interval_method()
            self._unsub_interval_method = None
            self.close()

    async def async_refresh_modbus_data(self, _now: Optional[int] = None) -> None:
        """Time to update."""
        if not self._sensors:
            return

        update_result = self.read_modbus_registers()

        if update_result:
            for update_callback in self._sensors:
                update_callback()

    @property
    def name(self):
        """Return the name of this hub."""
        return self._name

    def close(self):
        """Disconnect client."""
        with self._lock:
            self._client.close()

    def connect(self):
        """Connect client."""
        with self._lock:
            self._client.connect()

    # ---- Helper ----------------------------------------------------------

    # ---- Switches ----------------------------------------------------------
    def _encode_switch(self, v: Any) -> int:
        if isinstance(v, str):
            v = v.strip().lower()
            return 0 if v in {"off", "aus", "false", "0", "nein", "no"} else 1
        else:
            return 1 if bool(v) else 0

    def _decode_switch(self, props: Dict[str, Any], raw: int) -> str:
        """
        SWITCH-Mapping -> 'off'/'on'.
        Erlaubt {"off": 0}  oder {"off": 0, "on": 1}.
        """
        m: Dict[str, int] = get_entity_switch(props) or {}
        off_v = m.get("off", 0)
        return "off" if raw == off_v else "on"

    # ---- Numerische Werte ----------------------------------------------------------
    def _encode_numeric(
        self, value: float, faktor: float, min_v: float | None, max_v: float | None
    ) -> int:
        """
        Skaliert den Wert mit FAKTOR und gibt eine ganzzahlige Registerdarstellung zurück.
        Begrenzung erfolgt auf MIN und MAX (ebenfalls skaliert).
        """
        if min_v is not None and value < min_v:
            raise ValueError("VALUE darf nicht < MIN sein.")
        if max_v is not None and value > max_v:
            raise ValueError("VALUE darf nicht > MAX sein.")
        if faktor == 0:
            raise ValueError("FAKTOR darf nicht 0 sein.")

        return round(value / faktor)

    def _decode_numeric(self, props: Dict[str, Any], raw: int) -> float:
        """Rohwert -> physikalischer Wert mittels FAKTOR (raw * faktor)."""
        # Sentinel für 'ungültig': -500
        if raw == -500:
            return None
        faktor = get_entity_factor(props) or 1.0
        value = raw * faktor
        return float(value)

    def _decode_climate(self, props: Dict[str, Any], raw: int) -> dict:
        value = self._decode_numeric(props, raw)
        min_value = get_entity_min(props)
        max_value = get_entity_max(props)

        return {
            "temperature": value,
            "target_temp_low": min_value,
            "target_temp_high": max_value,
        }

    # ---- Select Werte ----------------------------------------------------------
    def _encode_select(self, props: Dict[str, Any], value: Any) -> int:
        """Ermittle den zu schreibenden Integer aus VALUES-Mapping (Label oder Index erlaubt)."""
        values = props["VALUES"]
        # label -> index
        if isinstance(value, str):
            inv = {str(v): k for k, v in values.items() if k != "default"}
            if value in inv:
                return int(inv[value])
            # tolerant gegen unterschiedliche Groß-/Kleinschreibung
            for k, v in inv.items():
                if k.lower() == value.lower():
                    return int(v)
            raise ValueError(
                f"Unbekannte Option '{value}'. Zulässig: {list(inv.keys())}"
            )
        # index (int) direkt
        try:
            iv = int(value)
        except Exception as e:
            raise ValueError(f"Ungültiger Select-Wert: {value!r}") from e
        if iv not in {k for k in values.keys() if isinstance(k, int)}:
            raise ValueError(
                f"Index {iv} nicht in VALUES: {sorted(k for k in values.keys() if isinstance(k, int))}"
            )
        return iv

    def _decode_select(self, props: Dict[str, Any], raw: int) -> str | None:
        """
        Invertiere VALUES (Index->Text) zu Text
        Unbekannte Indizes -> None.
        """
        values: Dict[Any, Any] = get_entity_select(props) or {}
        return values.get(raw, f"Ungültiger Wert: {raw}")

    # ***************************************** SCHREIBEN **************************************************************

    async def write_entity_value(self, entity_key: str, value: Any) -> None:
        """
        Generisches Schreiben für alle beschreibbaren Entitäten.
        - SWITCH: akzeptiert bool / 'on'/'off'/0/1
        - SELECT (VALUES): akzeptiert Label (String) oder Index (int)
        - NUMBER/CLIMATE: beachtet FAKTOR, MIN/MAX
        - UINT32: wird Big-Endian in zwei Registern geschrieben (REG, REG+1)
        - HA (Hand-Aktiv): falls vorhanden und activate_hand=True -> 1 schreiben
        """

        _LOGGER.info(f"Schreibe Entität {entity_key} -> {value}")
        print(f"write_entity_value: {entity_key} -> {value}")

        # Props finden
        props = get_entity_props(entity_key)
        if not props:
            raise ValueError(
                f"Ungültige Entität {entity_key}. Definition in ENTITIES_DICT nicht gefunden."
            )
        if is_entity_readonly(props):
            raise PermissionError(f"Register {entity_key} ist read-only.")

        reg, dt = get_entity_reg(props)
        if reg is None or dt is None:
            raise ValueError(f"Fehlende Registerdefinition für {entity_key}.")

        # 1) Wert in Roh-Registerwert(e) umwandeln
        reg_words: Tuple[int, ...] | list[int]

        if is_entity_switch(props):
            raw = self._encode_switch(value)
        elif is_entity_select(props):
            raw = self._encode_select(props, value)
        elif is_entity_climate(props):
            raw = self._encode_numeric(
                float(value["temperature"]),
                get_entity_factor(props),
                get_entity_min(props),
                get_entity_max(props),
            )
        else:
            # numerisch
            raw = self._encode_numeric(
                float(value),
                get_entity_factor(props),
                get_entity_min(props),
                get_entity_max(props),
            )

        if dt == ModbusTcpClient.DATATYPE.BITS:
            reg_words = (bool(raw),)
        else:
            reg_words = self._client.convert_to_registers(value=raw, data_type=dt)

        # 2) Schreiben
        await self._write_modbus_registers(reg, reg_words, dt)

        # 3) Daten neu lesen
        _LOGGER.info("Schreibvorgang abgeschlossen. Löse Refresh-Zyklus aus.")
        await self.async_refresh_modbus_data()

    async def setter_function_callback(self, entity: Entity, option):
        await self.write_entity_value(entity.entity_description.key, option)

    # ***************************************** LESEN **************************************************************

    def read_entity_value(
        self, buf: list[int | bool], idx: int, dt: ModbusTcpClient.DATATYPE
    ):
        if buf:
            if dt == ModbusTcpClient.DATATYPE.BITS:
                dtlen = 1
            else:
                dtlen = dt.value[1]
            buflen = len(buf)
            out_of_bounds = (idx < 0) or (idx + dtlen > buflen)
            if out_of_bounds:
                raise ValueError(
                    "Puffer hat nur {buflen} Elemente und ist damit zu klein zum Lesen von {dtlen} Elementen ab Index {idx}!!"
                )
            else:
                if dt == ModbusTcpClient.DATATYPE.BITS:
                    return buf[idx]
                else:
                    return self._client.convert_from_registers(
                        registers=buf[idx : idx + dtlen], data_type=dt
                    )
        else:
            raise ValueError(
                "Puffer hat keine Elemente. Fehler in Definition const.ENTITIES_DICT!!"
            )

    def read_modbus_registers(self):
        """Read from modbus registers"""

        if C_MAX_INPUT_REGISTER >= C_MIN_INPUT_REGISTER:
            _LOGGER.debug(
                f"Lese Input-Register {C_MIN_INPUT_REGISTER} bis {C_MAX_INPUT_REGISTER}..."
            )
            with self._lock:
                modbusdata_input = self._client.read_input_registers(
                    address=C_MIN_INPUT_REGISTER,
                    count=C_MAX_INPUT_REGISTER - C_MIN_INPUT_REGISTER + 1,
                    device_id=self._hostid,
                )
                if modbusdata_input is None or not hasattr(
                    modbusdata_input, "registers"
                ):
                    _LOGGER.error("Fehler beim Lesen der Input-Register.")
                    return False
                _LOGGER.debug(
                    f"{len(modbusdata_input.registers)} Input-Register: {modbusdata_input.registers}"
                )
                input_regs = modbusdata_input.registers
        else:
            _LOGGER.error("Keine Input-Register definiert.")
            input_regs = None

        if C_MAX_HOLDING_REGISTER >= C_MIN_HOLDING_REGISTER:
            _LOGGER.debug(
                f"Lese Holding-Register {C_MIN_HOLDING_REGISTER} bis {C_MAX_HOLDING_REGISTER}..."
            )
            with self._lock:
                modbusdata_holding = self._client.read_holding_registers(
                    address=C_MIN_HOLDING_REGISTER,
                    count=C_MAX_HOLDING_REGISTER - C_MIN_HOLDING_REGISTER + 1,
                    device_id=self._hostid,
                )
                if modbusdata_holding is None or not hasattr(
                    modbusdata_holding, "registers"
                ):
                    _LOGGER.error("Fehler beim Lesen der Holding-Register.")
                    return False
                _LOGGER.debug(
                    f"{len(modbusdata_holding.registers)} Holding-Register: {modbusdata_holding.registers}"
                )
                holding_regs = modbusdata_holding.registers
        else:
            _LOGGER.error("Keine Holding-Register definiert.")
            holding_regs = None

        if C_MAX_COILS >= C_MIN_COILS:
            _LOGGER.debug(f"Lese Coils {C_MIN_COILS} bis {C_MAX_COILS}...")
            with self._lock:
                modbusdata_coils = self._client.read_coils(
                    address=C_MIN_COILS,
                    count=C_MAX_COILS - C_MIN_COILS + 1,
                    device_id=self._hostid,
                )
                if modbusdata_coils is None or not hasattr(modbusdata_coils, "bits"):
                    _LOGGER.error("Fehler beim Lesen der Coils.")
                    return False
                _LOGGER.debug(
                    f"{len(modbusdata_coils.bits)} Coils: {modbusdata_coils.bits}"
                )
                coils = modbusdata_coils.bits
        else:
            _LOGGER.error("Keine Coils definiert.")
            coils = None

        if C_MAX_DISCRETE_INPUTS >= C_MIN_DISCRETE_INPUTS:
            _LOGGER.debug(
                f"Lese Discrete Inputs {C_MIN_DISCRETE_INPUTS} bis {C_MAX_DISCRETE_INPUTS} ..."
            )
            with self._lock:
                modbusdata_discrete = self._client.read_discrete_inputs(
                    address=C_MIN_DISCRETE_INPUTS,
                    count=C_MAX_DISCRETE_INPUTS - C_MIN_DISCRETE_INPUTS + 1,
                    device_id=self._hostid,
                )
                if modbusdata_discrete is None or not hasattr(
                    modbusdata_discrete, "bits"
                ):
                    _LOGGER.error("Fehler beim Lesen der Discrete Inputs.")
                    return False
                _LOGGER.debug(
                    f"{len(modbusdata_discrete.bits)} Discrete Inputs: {modbusdata_discrete.bits}"
                )
                discrete = modbusdata_discrete.bits
        else:
            _LOGGER.error("Keine Discrete Inputs definiert.")
            discrete = None

        for entity_key, props in ENTITIES_DICT.items():
            reg_type = get_entity_type(props)
            reg, dt = get_entity_reg(props)
            if reg is None:
                continue  # defensiv
            _LOGGER.debug(f"Lese Entität '{entity_key}'.")
            match reg_type:
                case const.C_REG_TYPE_COILS:
                    raw = self.read_entity_value(coils, reg - C_MIN_COILS, dt)
                case const.C_REG_TYPE_DISCRETE_INPUTS:
                    raw = self.read_entity_value(
                        discrete, reg - C_MIN_DISCRETE_INPUTS, dt
                    )
                case const.C_REG_TYPE_INPUT_REGISTERS:
                    raw = self.read_entity_value(
                        input_regs, reg - C_MIN_INPUT_REGISTER, dt
                    )
                case const.C_REG_TYPE_HOLDING_REGISTERS:
                    raw = self.read_entity_value(
                        holding_regs, reg - C_MIN_HOLDING_REGISTER, dt
                    )

            if is_entity_switch(props):
                value = self._decode_switch(props, raw)
            elif is_entity_select(props):
                value = self._decode_select(props, raw)
            elif is_entity_climate(props):
                if is_entity_readonly(props):
                    value = self._decode_numeric(props, raw)
                else:
                    value = self._decode_climate(props, raw)
            else:
                value = self._decode_numeric(props, raw)

            self.data[entity_key] = value

        _LOGGER.info("Lesen der Register erfolgreich abgeschlossen.")
        return True

    # ***************************************** SCHREIBEN **************************************************************

    async def _write_modbus_registers(
        self, base_reg: int, reg_values: Iterable[int], dt: ModbusTcpClient.DATATYPE
    ):
        """
        Schreibt eine Sequenz 16-bit Registerwerte ab base_reg.

        Mit int(word) & 0xFFFF: sicherstellen, dass der Wert in den gültigen Bereich passt.
        Beispiel: 70000 & 0xFFFF → 4464
                  -1 & 0xFFFF → 65535
        """
        _LOGGER.info(f"Schreibzugriff auf Register {base_reg}: {reg_values}")
        for offset, word in enumerate(reg_values):
            if dt == ModbusTcpClient.DATATYPE.BITS:
                self._client.write_coil(
                    address=base_reg + offset, value=bool(word), device_id=self._hostid
                )
            else:
                self._client.write_register(
                    address=base_reg + offset,
                    value=int(word) & 0xFFFF,
                    device_id=self._hostid,
                )
