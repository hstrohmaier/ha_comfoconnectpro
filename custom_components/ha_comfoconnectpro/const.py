"""Constants for the integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any

import sys

from homeassistant.components.climate import (
    ClimateEntityDescription,
    ClimateEntityFeature,
)
from homeassistant.components.sensor import *
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberDeviceClass,
)
from homeassistant.const import (
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfEnergy,
    UnitOfPower,
    CONF_NAME,
    Platform,
)

from pymodbus.client import ModbusTcpClient

import logging

thismodule = sys.modules[__name__]
_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)
_LOGGER.info(f"{thismodule}.const loaded")



DOMAIN = "ha_comfoconnectpro"
DEFAULT_NAME = "ComfoConnect PRO"
DEFAULT_SCAN_INTERVAL = 15
DEFAULT_PORT = 502
DEFAULT_HOSTID = 1
CONF_HOSTID = "hostid"
CONF_HUB = "hacomfoconnectpro_hub"
ATTR_MANUFACTURER = "Zehnder"



# ------------------------------------------------------------
# 1) Error-Konstanten (C_<NAME> = "<error_num>")
#    >> Diese Konstanten dienen als Keys im ERROR_DICT.
# ------------------------------------------------------------
C_NO_ERR = 0
C_HRU_T_FIRE_ERR = 21
C_T_HRU_ERR = 22
C_T_11_ERR = 23
C_T_11_LIMIT_ERR = 24
C_T_12_ERR = 25
C_T_12_LIMIT_ERR = 26
C_T_20_ERR = 27
C_T_20_LIMIT_ERR = 28
C_T_21_ERR = 29
C_T_21_LIMIT_ERR = 30
C_T_22_ERR = 31
C_T_22_LIMIT_ERR = 32
C_HRU_INIT_ERR = 33
C_HRU_FRONT_OPEN_ERR = 34
C_H_21_RELEASE_ERR = 35
C_H_21_P_ERR = 37
C_H_21_P_RATIO_ERR = 38
C_PHI_11_ERR = 39
C_PHI_12_ERR = 41
C_PHI_20_ERR = 43
C_PHI_21_ERR = 45
C_PHI_22_ERR = 47
C_P_12_ERR = 49
C_P_22_ERR = 50
C_F_12_S_ERR = 51
C_F_22_S_ERR = 52
C_PTOT_12_S_ERR = 53
C_PTOT_22_S_ERR = 54
C_F_12_S_SET_ERR = 55
C_F_22_S_SET_ERR = 56
C_QM_12_SET_ERR = 57
C_QM_22_SET_ERR = 58
C_T_21_SET_ERR = 59
C_T_22_SET_ERR = 60
C_T_22_FROST_ERR = 61
C_UNBALANCE_ERR = 62
C_PRESENT_RF_ERR = 66
C_PRESENT_IO_ERR = 67
C_PRESENT_H_21_ERR = 68
C_PRESENT_H_23_ERR = 69
C_PRESENT_HOOD_ERR = 74
C_PRESENT_CCOOL_ERR = 75
C_PRESENT_G_ERR = 76
C_FILTER_ALARM_FLAG = 77
C_FILTER_EXT_ERR = 78
C_FILTER_WARNING_FLAG = 79
C_STANDBY_ERR = 80
C_H_21_COMM_ERR = 81
C_T_22_MANUAL_ERR = 89
C_CC_OVERHEAT_ERR = 90
C_CC_COMP_ERR = 91
C_CC_T_10_ERR = 92
C_CC_T_13_ERR = 93
C_CC_T_23_ERR = 94
C_T_HOOD_ERR = 95
C_IO_HOOD_DUTY_ERR = 96
C_QM_CONSTRAINT_MIN_ERR = 97
C_H_21_QM_MIN_ERR = 98
C_CONFIG_ERR = 99
C_ANALYSIS_BUSY_WARNING = 100
C_COMFONET_ERR = 101
C_CO2_SENS_COUNT_ERR = 102
C_CO2_SENS_TOO_MANY_ERR = 103
C_CO2_SENS_GENERAL_ERR = 104

# Dictionary mit Beschreibungen
ERROR_DICT: Dict[str, Any] = {
    C_NO_ERR: "Normalbetrieb",
    C_HRU_T_FIRE_ERR: "Zwei oder mehr Temperatursensoren sind außerhalb der Grenzen",
    C_T_HRU_ERR: "Temperatur zu hoch für HRU",
    C_T_11_ERR: "Wert des Temperatursensors T11 hat den Grenzwert zu oft überschritten",
    C_T_11_LIMIT_ERR: "Wert des Temperatursensors T11 überschreitet den Grenzwert",
    C_T_12_ERR: "Wert des Temperatursensors T12 hat den Grenzwert zu oft überschritten",
    C_T_12_LIMIT_ERR: "Wert des Temperatursensors T12 überschreitet den Grenzwert",
    C_T_20_ERR: "Wert des Temperatursensors T20 hat den Grenzwert zu oft überschritten",
    C_T_20_LIMIT_ERR: "Wert des Temperatursensors T20 überschreitet den Grenzwert",
    C_T_21_ERR: "Wert des Temperatursensors T21 hat den Grenzwert zu oft überschritten",
    C_T_21_LIMIT_ERR: "Wert des Temperatursensors T21 überschreitet den Grenzwert",
    C_T_22_ERR: "Wert des Temperatursensors T22 hat den Grenzwert zu oft überschritten",
    C_T_22_LIMIT_ERR: "Wert des Temperatursensors T22 überschreitet den Grenzwert",
    C_HRU_INIT_ERR: "HRU ist nicht initialisiert worden",
    C_HRU_FRONT_OPEN_ERR: "Die Vordertür ist offen",
    C_H_21_RELEASE_ERR: "Vorwärmer ist vorhanden, aber seine Position (links/rechts) stimmt nicht mit der Ausrichtung von HRU überein",
    C_H_21_P_ERR: "Vorwärmer liefert nicht die gewünschte Leistung",
    C_H_21_P_RATIO_ERR: "Vorwärmer liefert nicht die gewünschte Leistung im erforderlichen Verhältnis",
    C_PHI_11_ERR: "Wert des Feuchtigkeitssensors ϕ11 hat den Grenzwert zu oft überschritten",
    C_PHI_12_ERR: "Wert des Feuchtigkeitssensors ϕ12 hat den Grenzwert zu oft überschritten",
    C_PHI_20_ERR: "Wert des Feuchtigkeitssensors ϕ20 hat den Grenzwert zu oft überschritten",
    C_PHI_21_ERR: "Wert des Feuchtigkeitssensors ϕ21 hat den Grenzwert zu oft überschritten",
    C_PHI_22_ERR: "Wert des Feuchtigkeitssensors ϕ22 hat den Grenzwert zu oft überschritten",
    C_P_12_ERR: "Wert des Drucksensors P12 hat den Grenzwert zu oft überschritten",
    C_P_22_ERR: "Wert des Drucksensors P22 hat den Grenzwert zu oft überschritten",
    C_F_12_S_ERR: "Drehzahl des F12-Lüfters hat den Grenzwert zu oft überschritten",
    C_F_22_S_ERR: "Drehzahl des F22-Lüfters hat den Grenzwert zu oft überschritten",
    C_PTOT_12_S_ERR: "Statischer Druck des Sensors P12 hat den Grenzwert zu oft überschritten",
    C_PTOT_22_S_ERR: "Statischer Druck des Sensors P22 hat den Grenzwert zu oft überschritten",
    C_F_12_S_SET_ERR: "Erforderliche F12-Lüfterdrehzahl wurde zu oft nicht erreicht",
    C_F_22_S_SET_ERR: "Erforderliche F22-Lüfterdrehzahl wurde zu oft nicht erreicht",
    C_QM_12_SET_ERR: "Erforderlicher Massenstrom für F12-Lüfter wurde zu oft nicht erreicht",
    C_QM_22_SET_ERR: "Erforderlicher Massenstrom für F22-Lüfter wurde zu oft nicht erreicht",
    C_T_21_SET_ERR: "Erforderliche Temperatur für die Außenluft nach dem Vorwärmer wurde zu oft nicht erreicht",
    C_T_22_SET_ERR: "Erforderliche Temperatur für die Zuluft wurde zu oft nicht erreicht",
    C_T_22_FROST_ERR: "Zulufttemperatur (Sensor T22) ist zu oft zu niedrig",
    C_UNBALANCE_ERR: "Unwucht lag im vergangenen Zeitraum zu oft außerhalb der Toleranzwerte",
    C_PRESENT_RF_ERR: "RF-Kommunikationshardware war vorhanden, wird aber nicht mehr erkannt",
    C_PRESENT_IO_ERR: "Optionskarte war vorhanden, wird aber nicht mehr erkannt",
    C_PRESENT_H_21_ERR: "Vorwärmer war vorhanden, wird aber nicht mehr erkannt",
    C_PRESENT_H_23_ERR: "Nacherhitzer war vorhanden, wird aber nicht mehr erkannt",
    C_PRESENT_HOOD_ERR: "Abzugshaube war vorhanden, wird aber nicht mehr erkannt",
    C_PRESENT_CCOOL_ERR: "Comfo Cool war vorhanden, wird aber nicht mehr erkannt",
    C_PRESENT_G_ERR: "ComfoFond war vorhanden, wird aber nicht mehr erkannt",
    C_FILTER_ALARM_FLAG: "Filter müssen jetzt ausgetauscht werden",
    C_FILTER_EXT_ERR: "Der Eingang des externen Filters ist hoch",
    C_FILTER_WARNING_FLAG: "Die Filter müssen jetzt bestellt werden, da die verbleibende Lebensdauer der Filter begrenzt ist",
    C_STANDBY_ERR: "Standby ist aktiv",
    C_H_21_COMM_ERR: "Vorwärmer kommuniziert nicht zuverlässig",
    C_T_22_MANUAL_ERR: "Bypass wird manuell verwendet.",
    C_CC_OVERHEAT_ERR: "ComfoCool ist überhitzt",
    C_CC_COMP_ERR: "ComfoCool Kompressorfehler",
    C_CC_T_10_ERR: "ComfoCool Raumtemperatur außerhalb der Grenzen",
    C_CC_T_13_ERR: "ComfoCool Kompressortemperatur außerhalb der Grenzen",
    C_CC_T_23_ERR: "ComfoCool Vorlauftemperatur außerhalb der Grenzen",
    C_T_HOOD_ERR: "Haubentemperatur ist zu hoch",
    C_IO_HOOD_DUTY_ERR: "Haube ist aktiviert",
    C_QM_CONSTRAINT_MIN_ERR: "STATUS-FLAG",
    C_H_21_QM_MIN_ERR: "Strom zu niedrig für Vorwärmer",
    C_CONFIG_ERR: "Konfigurationsfehler",
    C_ANALYSIS_BUSY_WARNING: "Warnung, dass eine Fehleranalyse ausgeführt wird",
    C_COMFONET_ERR: "Fehler auf dem ComfoNet-Bus",
    C_CO2_SENS_COUNT_ERR: "Die Anzahl der CO2-Sensoren an einem Controller hat sich verringert - ein oder mehrere Sensoren werden nicht mehr erkannt",
    C_CO2_SENS_TOO_MANY_ERR: "Mehr als 8 Sensoren werden in einer Zone erkannt",
    C_CO2_SENS_GENERAL_ERR: "Allgemeiner CO2-Sensor-Fehler",
}

# --- Konstanten ---

# Datentyp für coils oder discrete_inputs
C_DT_BITS = ModbusTcpClient.DATATYPE.BITS  # "bit"     # 1 Bit

# Datentypen für input_registers or holding_registers
C_DT_INT16 = ModbusTcpClient.DATATYPE.INT16  # "INT16"     # 1 Register
C_DT_UINT16 = ModbusTcpClient.DATATYPE.UINT16  # "UINT16"   # 1 Register
C_DT_INT32 = ModbusTcpClient.DATATYPE.INT32  # "INT32"   # 2 Register
C_DT_UINT32 = ModbusTcpClient.DATATYPE.UINT32  # "UINT32"   # 2 Register

C_MIN_INPUT_REGISTER = sys.maxsize
C_MAX_INPUT_REGISTER = -1
C_MIN_HOLDING_REGISTER = sys.maxsize
C_MAX_HOLDING_REGISTER = -1
C_MIN_COILS = sys.maxsize
C_MAX_COILS = -1
C_MIN_DISCRETE_INPUTS = sys.maxsize
C_MAX_DISCRETE_INPUTS = -1

# Konstanten zur Definition der Registerart
C_REG_TYPE_UNKNOWN = 0
C_REG_TYPE_COILS = 1
C_REG_TYPE_DISCRETE_INPUTS = 2
C_REG_TYPE_HOLDING_REGISTERS = 3
C_REG_TYPE_INPUT_REGISTERS = 4

# ------------------------------------------------------------
# 2) Entity-Konstanten (C_<NAME> = "<entity_key>")
#    >> Diese Konstanten dienen als Keys im ENTITIES_DICT.
# ------------------------------------------------------------
C_CONNECTION_STATE = "connection_state"
C_ACTIVEERROR1 = "activeerror1"
C_ACTIVEERROR2 = "activeerror2"
C_ACTIVEERROR3 = "activeerror3"
C_ACTIVEERROR4 = "activeerror4"
C_ACTIVEERROR5 = "activeerror5"
C_AIRFLOW = "airflow"
C_ROOM_TEMPERATURE = "room_temperature"
C_EXTRACT_TEMPERATURE = "extract_temperature"
C_EXHAUST_TEMPERATURE = "exhaust_temperature"
C_OUTDOOR_TEMPERATURE = "outdoor_temperature"
C_SUPPLY_TEMPERATURE = "supply_temperature"
C_ROOM_HUMIDITY = "room_humidity"
C_EXTRACT_HUMIDITY = "extract_humidity"
C_EXHAUST_HUMIDITY = "exhaust_humidity"
C_OUTDOOR_HUMIDITY = "outdoor_humidity"
C_SUPPLY_HUMIDITY = "supply_humidity"
C_CO2_SENSOR_ZONE_1 = "co2_sensor_zone_1"
C_CO2_SENSOR_ZONE_2 = "co2_sensor_zone_2"
C_CO2_SENSOR_ZONE_3 = "co2_sensor_zone_3"
C_CO2_SENSOR_ZONE_4 = "co2_sensor_zone_4"
C_CO2_SENSOR_ZONE_5 = "co2_sensor_zone_5"
C_CO2_SENSOR_ZONE_6 = "co2_sensor_zone_6"
C_CO2_SENSOR_ZONE_7 = "co2_sensor_zone_7"
C_CO2_SENSOR_ZONE_8 = "co2_sensor_zone_8"
C_FILTER_DAYS_REMAINING = "filter_days_remaining"

C_ERROR_FLAG = "error_flag"
C_STANDBY = "standby"
C_COMFOHOOD = "comfohood"
C_FILTER_DIRTY = "filter_dirty"

C_VENTILATION_PRESET = "ventilation_preset"
C_TEMPERATURE_PROFILE = "temperature_profile"
C_TEMPERATURE_PROFILE_MODE = "temperature_profile_mode"
C_EXTERNAL_SETPOINT = "external_setpoint"
C_BOOST_TIME = "boost_time"

C_RESET_ERRORS = "reset_errors"
C_VENTILATION_PRESET_AWAY = "ventilation_preset_away"
C_VENTILATIONPRESET1 = "ventilationpreset1"
C_VENTILATIONPRESET2 = "ventilationpreset2"
C_VENTILATIONPRESET3 = "ventilationpreset3"
C_AUTO_MODE = "auto_mode"
C_BOOST = "boost"
C_AWAY_FUNCTION = "away_function"
C_COMFOCOOL = "comfocool"


# --------------------------------------------------------------------------------------------
# 2) ENTITIES_DICT DICT, neue Register müssen nur hier zugefügt werden.
#    Sofern zusätzliche Register keine neue Logik erfordern, ist der restliche Code schon darauf vorbereitet
# --------------------------------------------------------------------------------------------
#    ENTITIES_DICT: Dict[str, Dict[str, Any]]
#    *Key = passende C_<...>-Konstante = HASS sensor_id
#    *NAME: Angezeigter Name
#    *REG: Modbus-Register (Zero-Based)
#    *RT: Register Typ (derzeit 1..4): Holding-Register, Coils (read-write) oder Input-Register, Discrete-Inputs (read-only)
#    *DT: Datentyp (derzeit nur BITS, INT16, UINT16), Hinweis: BITS für Coils und Discrete-Inputs (Angabe optional). Schalter immer mit 0 oder 1
#    RW: Read/Write für Coils und Holding-Register unterbinden mit "RW":0
#    FAKTOR: Multiplikator für Anzeige im HA (derzeit: 1, 0.1)
#    UNIT: Einheit der Entität (°C, W, kW, Wh, kWh, bar, ppm, m³/h...)
#    STEP: Steuert die Darstellung in der Anzeige im HA, Schrittweite der Einstellung (z.B. 5.0, 1.0, 0.5, 0.1)
#    MIN: Erlaubter Mindestwert der Entität
#    MAX: Erlaubter Höchstwert der Entität
#    VALUES: Gültige Auswahlwerte; dict[id,AngezeigterName] mit optionalem Bestandteil: "default":<defaultwert>
#    INC: 1, wenn Entität stetig steigende Werte liefert.
#    SWITCH: Werte für "aus" und optional für "ein". Wenn "ein" nicht angegeben ist, sind alle anderen ganzahligen Werte "ein" gültig
#    PF: Anzeige-Variante in HA übersteuern. "PF":Platform.NUMBER v=> Temperaturwert wird nicht als CLIMATE, sondern als NUMBER behandelt.
#
#    *: Obligatorischer Wert
# --------------------------------------------------------------------------------------------

# Modbus-Register gemäß Zehnder_CSY_ComfoConnect-Pro_INM_DE-de.pdf vom 24.09.2024
# Achtung: Register sind in der Dokumentation mit 1 beginnend nummeriert und es wird darauf verwiesen,
# dass in der PDU Register mit Null beginnend adressiert werden (1-16 -> 0-15). Daher ist beim REG-Wert immer den Wert aus der Doku um eins reduzieren.
# Getestet mit Zehnder ComfoConnect PRO  RCG 2.0.0.10

# --- ENTITIES_DICT ---
ENTITIES_DICT: Dict[str, Dict[str, Any]] = {
    # INPUT_REGISTERS
    C_CONNECTION_STATE: {
        "RT": C_REG_TYPE_INPUT_REGISTERS,
        "REG": 0,
        "NAME": "Verbindungsstatus",
        "VALUES": {
            0: "ok",
            30: "die erkannte Lüftungseinheit ist kein CAQ",
            40: "CAQ-Version nicht kompatibel",
            50: "keine Lüftungseinheit erkannt",
        },
        "DT": C_DT_UINT16,
    },
    C_ACTIVEERROR1: {
        "RT": C_REG_TYPE_INPUT_REGISTERS,
        "REG": 1,
        "NAME": "Fehler 1",
        "VALUES": ERROR_DICT,
        "DT": C_DT_UINT16,
    },
    C_ACTIVEERROR2: {
        "RT": C_REG_TYPE_INPUT_REGISTERS,
        "REG": 2,
        "NAME": "Fehler 2",
        "VALUES": ERROR_DICT,
        "DT": C_DT_UINT16,
    },
    C_ACTIVEERROR3: {
        "RT": C_REG_TYPE_INPUT_REGISTERS,
        "REG": 3,
        "NAME": "Fehler 3",
        "VALUES": ERROR_DICT,
        "DT": C_DT_UINT16,
    },
    C_ACTIVEERROR4: {
        "RT": C_REG_TYPE_INPUT_REGISTERS,
        "REG": 4,
        "NAME": "Fehler 4",
        "VALUES": ERROR_DICT,
        "DT": C_DT_UINT16,
    },
    C_ACTIVEERROR5: {
        "RT": C_REG_TYPE_INPUT_REGISTERS,
        "REG": 5,
        "NAME": "Fehler 5",
        "VALUES": ERROR_DICT,
        "DT": C_DT_UINT16,
    },
    C_AIRFLOW: {
        "RT": C_REG_TYPE_INPUT_REGISTERS,
        "REG": 6,
        "NAME": "Zuluft Ventilator-Volumen ",
        "UNIT": "m³",
        "DT": C_DT_UINT16,
    },
    C_ROOM_TEMPERATURE: {
        "RT": C_REG_TYPE_INPUT_REGISTERS,
        "REG": 7,
        "NAME": "Raumlufttemperatur",
        "FAKTOR": 0.1,
        "UNIT": "°C",
        "DT": C_DT_INT16,
    },
    C_EXTRACT_TEMPERATURE: {
        "RT": C_REG_TYPE_INPUT_REGISTERS,
        "REG": 8,
        "NAME": "Fortlufttemperatur",
        "FAKTOR": 0.1,
        "UNIT": "°C",
        "DT": C_DT_INT16,
    },
    C_EXHAUST_TEMPERATURE: {
        "RT": C_REG_TYPE_INPUT_REGISTERS,
        "REG": 9,
        "NAME": "Ablufttemperatur",
        "FAKTOR": 0.1,
        "UNIT": "°C",
        "DT": C_DT_INT16,
    },
    C_OUTDOOR_TEMPERATURE: {
        "RT": C_REG_TYPE_INPUT_REGISTERS,
        "REG": 10,
        "NAME": "Außenlufttemperatur",
        "FAKTOR": 0.1,
        "UNIT": "°C",
        "DT": C_DT_INT16,
    },
    C_SUPPLY_TEMPERATURE: {
        "RT": C_REG_TYPE_INPUT_REGISTERS,
        "REG": 11,
        "NAME": "Zulufttemperatur",
        "FAKTOR": 0.1,
        "UNIT": "°C",
        "DT": C_DT_INT16,
    },
    C_ROOM_HUMIDITY: {
        "RT": C_REG_TYPE_INPUT_REGISTERS,
        "REG": 12,
        "NAME": "Raumluftfeuchtigkeit",
        "UNIT": "%",
        "DT": C_DT_UINT16,
    },
    C_EXTRACT_HUMIDITY: {
        "RT": C_REG_TYPE_INPUT_REGISTERS,
        "REG": 13,
        "NAME": "Fortluftfeuchtigkeit",
        "UNIT": "%",
        "DT": C_DT_UINT16,
    },
    C_EXHAUST_HUMIDITY: {
        "RT": C_REG_TYPE_INPUT_REGISTERS,
        "REG": 14,
        "NAME": "Abluftfeuchtigkeit",
        "UNIT": "%",
        "DT": C_DT_UINT16,
    },
    C_OUTDOOR_HUMIDITY: {
        "RT": C_REG_TYPE_INPUT_REGISTERS,
        "REG": 15,
        "NAME": "Außenluftfeuchtigkeit",
        "UNIT": "%",
        "DT": C_DT_UINT16,
    },
    C_SUPPLY_HUMIDITY: {
        "RT": C_REG_TYPE_INPUT_REGISTERS,
        "REG": 16,
        "NAME": "Zuluftfeuchtigkeit",
        "UNIT": "%",
        "DT": C_DT_UINT16,
    },
    C_CO2_SENSOR_ZONE_1: {
        "RT": C_REG_TYPE_INPUT_REGISTERS,
        "REG": 17,
        "NAME": "CO2 Sensor Zone 1",
        "UNIT": "ppm",
        "DT": C_DT_UINT16,
    },
    C_CO2_SENSOR_ZONE_2: {
        "RT": C_REG_TYPE_INPUT_REGISTERS,
        "REG": 18,
        "NAME": "CO2 Sensor Zone 2",
        "UNIT": "ppm",
        "DT": C_DT_UINT16,
    },
    C_CO2_SENSOR_ZONE_3: {
        "RT": C_REG_TYPE_INPUT_REGISTERS,
        "REG": 19,
        "NAME": "CO2 Sensor Zone 3",
        "UNIT": "ppm",
        "DT": C_DT_UINT16,
    },
    C_CO2_SENSOR_ZONE_4: {
        "RT": C_REG_TYPE_INPUT_REGISTERS,
        "REG": 20,
        "NAME": "CO2 Sensor Zone 4",
        "UNIT": "ppm",
        "DT": C_DT_UINT16,
    },
    C_CO2_SENSOR_ZONE_5: {
        "RT": C_REG_TYPE_INPUT_REGISTERS,
        "REG": 21,
        "NAME": "CO2 Sensor Zone 5",
        "UNIT": "ppm",
        "DT": C_DT_UINT16,
    },
    C_CO2_SENSOR_ZONE_6: {
        "RT": C_REG_TYPE_INPUT_REGISTERS,
        "REG": 22,
        "NAME": "CO2 Sensor Zone 6",
        "UNIT": "ppm",
        "DT": C_DT_UINT16,
    },
    C_CO2_SENSOR_ZONE_7: {
        "RT": C_REG_TYPE_INPUT_REGISTERS,
        "REG": 23,
        "NAME": "CO2 Sensor Zone 7",
        "UNIT": "ppm",
        "DT": C_DT_UINT16,
    },
    C_CO2_SENSOR_ZONE_8: {
        "RT": C_REG_TYPE_INPUT_REGISTERS,
        "REG": 24,
        "NAME": "CO2 Sensor Zone 8",
        "UNIT": "ppm",
        "DT": C_DT_UINT16,
    },
    C_FILTER_DAYS_REMAINING: {
        "RT": C_REG_TYPE_INPUT_REGISTERS,
        "REG": 25,
        "NAME": "Filter ersetzen in",
        "UNIT": "d",
        "DT": C_DT_UINT16,
    },
    # DISCRETE_INPUTS
    C_ERROR_FLAG: {"RT": C_REG_TYPE_DISCRETE_INPUTS, "REG": 0, "NAME": "Fehler aktiv?"},
    C_STANDBY: {"RT": C_REG_TYPE_DISCRETE_INPUTS, "REG": 1, "NAME": "Standby"},
    C_COMFOHOOD: {"RT": C_REG_TYPE_DISCRETE_INPUTS, "REG": 2, "NAME": "ComfoHood"},
    C_FILTER_DIRTY: {
        "RT": C_REG_TYPE_DISCRETE_INPUTS,
        "REG": 3,
        "NAME": "Filter wechseln",
    },
    # HOLDING_REGISTERS
    C_VENTILATION_PRESET: {
        "RT": C_REG_TYPE_HOLDING_REGISTERS,
        "REG": 0,
        "NAME": "Lüftungsstufe",
        "DT": C_DT_UINT16,  # byte -> in 16 Bit Register
        "VALUES": {
            0: "Außer Haus",
            1: "Voreinstellung 1",
            2: "Voreinstellung 2",
            3: "Voreinstellung 3",
            "default": 2,
        },
    },
    C_TEMPERATURE_PROFILE: {
        "RT": C_REG_TYPE_HOLDING_REGISTERS,
        "REG": 1,
        "NAME": "Temperaturprofil",
        "DT": C_DT_UINT16,  # byte -> in 16 Bit Register
        "VALUES": {0: "Komfort", 1: "Eco", 2: "Warm", "default": 0},
        # Hinweis: funktioniert nur im Modus 0 oder 1
    },
    C_TEMPERATURE_PROFILE_MODE: {
        "RT": C_REG_TYPE_HOLDING_REGISTERS,
        "REG": 2,
        "NAME": "Temperaturprofil Modus",
        "DT": C_DT_UINT16,  # byte -> in 16 Bit Register
        "VALUES": {0: "Adaptiv", 1: "Fest", 2: "gemäß ext. Sollwert", "default": 0},
    },
    C_EXTERNAL_SETPOINT: {
        "RT": C_REG_TYPE_HOLDING_REGISTERS,
        "REG": 3,
        "NAME": "Externer Sollwert",
        "FAKTOR": 0.1,
        "MIN": 5.0,
        "MAX": 35.0,
        "UNIT": "°C",
        "DT": C_DT_UINT16,
        # Hinweis: funktioniert nur im Modus 2
    },
    C_BOOST_TIME: {
        "RT": C_REG_TYPE_HOLDING_REGISTERS,
        "REG": 4,
        "NAME": "Boost-Zeit [min.]",
        "FAKTOR": 0.016666666667,  # Sekunden: 1.0, im Register stehen Sekunden, Umrechnung in Minuten
        "UNIT": "min",
        "STEP": 1,  # Sekunden: 60,
        "MIN": 0,
        "MAX": 1092,  # Sekunden: 65535,
        "DT": C_DT_UINT16,
        # Hinweis: 65535 (18h12m15s)wird als 24 Stunden betrachtet
    },
    # COILS
    C_RESET_ERRORS: {
        "RT": C_REG_TYPE_COILS,
        "REG": 0,
        "NAME": "Fehler quittieren",
        # selbstrücksetzende Coil, der Wert False wird ignoriert
    },
    # # Wird schon über C_VENTILATION_PRESET gesetzt
    # C_VENTILATION_PRESET_AWAY: {
    #     "RT": C_REG_TYPE_COILS, "REG": 1, "NAME": "Ventilation Preset Away"
    #     # der Wert False wird ignoriert
    # },
    # C_VENTILATIONPRESET1: {
    #     "RT": C_REG_TYPE_COILS, "REG": 2, "NAME": "VentilationPreset1"
    #     # der Wert False wird ignoriert
    # },
    # C_VENTILATIONPRESET2: {
    #     "RT": C_REG_TYPE_COILS, "REG": 3, "NAME": "VentilationPreset2"
    #     # der Wert False wird ignoriert
    # },
    # C_VENTILATIONPRESET3: {
    #    "RT": C_REG_TYPE_COILS, "REG": 4, "NAME": "VentilationPreset3"
    #    # der Wert False wird ignoriert
    # },
    C_AUTO_MODE: {"RT": C_REG_TYPE_COILS, "REG": 5, "NAME": "Auto Mode"},
    C_BOOST: {"RT": C_REG_TYPE_COILS, "REG": 6, "NAME": "Boost"},
    C_AWAY_FUNCTION: {"RT": C_REG_TYPE_COILS, "REG": 7, "NAME": "Away function"},
    C_COMFOCOOL: {"RT": C_REG_TYPE_COILS, "REG": 8, "NAME": "ComfoCool"},
}


# ------------------------------------------------------------
# Klassendefinitionen für die unterschiedlichen Entitätstypen
# ------------------------------------------------------------


@dataclass
class MyBinarySensorEntityDescription(BinarySensorEntityDescription):
    """A class that describes Modbus binarysensor entities."""


@dataclass
class MySensorEntityDescription(SensorEntityDescription):
    """A class that describes Modbus sensor entities."""


@dataclass
class MyBinaryEntityDescription(BinarySensorEntityDescription):
    """A class that describes Modbus binary entities."""

    # Hinweis: Falls echte Schalter-Entities verwendet werden, ggf. SwitchEntityDescription verwenden.


@dataclass
class MySelectEntityDescription(SensorEntityDescription):
    """A class that describes Modbus select sensor entities."""

    select_options: list[str] = None
    default_select_option: str = None
    setter_function = None


@dataclass
class MyClimateEntityDescription(ClimateEntityDescription):
    """A class that describes Modbus climate sensor entities."""

    min_value: float = None
    max_value: float = None
    step: float = None
    hvac_modes: list[str] = None
    temperature_unit: str = "°C"
    supported_features: ClimateEntityFeature = ClimateEntityFeature.TARGET_TEMPERATURE


@dataclass
class MyNumberEntityDescription(NumberEntityDescription):
    """A class that describes Modbus number entities."""

    mode: str = "slider"
    initial: float = None
    editable: bool = True


BINARYSENSOR_TYPES: dict[str, MyBinarySensorEntityDescription] = {}
SENSOR_TYPES: dict[str, MySensorEntityDescription] = {}
SELECT_TYPES: dict[str, MySelectEntityDescription] = {}
CLIMATE_TYPES: dict[str, MyClimateEntityDescription] = {}
NUMBER_TYPES: dict[str, MyNumberEntityDescription] = {}
BINARY_TYPES: dict[str, MyBinaryEntityDescription] = {}


# --------------------------------------------------------------------
# Hilfsfunktionen zur Klassifizierung der Eintitäten aus ENTITIES_DICT
# --------------------------------------------------------------------

TEMP_UNITS = {"°C", "K"}


def is_entity_readonly(props: Dict[str, Any]) -> bool:
    """Input-Register oder Discrete-Inputs oder Read-Only: RW=0)"""
    reg_type = get_entity_type(props)
    return reg_type in [C_REG_TYPE_INPUT_REGISTERS, C_REG_TYPE_DISCRETE_INPUTS] or (props.get("RW") == 0)


def is_entity_readwrite(props: Dict[str, Any]) -> bool:
    """Beschreibbar, Read-Only: Beschreibbar (WR=None)"""
    reg_type = get_entity_type(props)
    return reg_type in [C_REG_TYPE_HOLDING_REGISTERS, C_REG_TYPE_COILS]


def is_entity_switch(props: Dict[str, Any]) -> bool:
    reg_type = get_entity_type(props)
    return (reg_type in [C_REG_TYPE_DISCRETE_INPUTS, C_REG_TYPE_COILS]) or (
        get_entity_switch(props) is not None
    )


def is_entity_select(props: Dict[str, Any]) -> bool:
    return props.get("VALUES") not in (None, {})


def is_entity_climate(props: Dict[str, Any]) -> bool:
    return get_entity_unit(props) in TEMP_UNITS and get_entity_platform(props) in {
        None,
        Platform.CLIMATE,
    }


def is_entity_number(props: Dict[str, Any]) -> bool:
    return get_entity_platform(props) == Platform.NUMBER or not (
        is_entity_switch(props) or is_entity_select(props) or is_entity_climate(props)
    )


# -------------------------------------------------
# Hilfsfunktionen zum Lesen der Daten einer Entität
# -------------------------------------------------


def get_entity_type(props: Dict[str, Any]) -> int | None:
    return props.get("RT")


def get_entity_name(props: Dict[str, Any], default: str = None) -> str | None:
    return props.get("NAME", default)


def get_entity_unit(props: Dict[str, Any], default: str = None) -> str | None:
    return props.get("UNIT", default)


def get_entity_platform(props: Dict[str, Any], default: str = None) -> str | None:
    return props.get("PF", default)


def get_entity_min(props: Dict[str, Any]) -> float | None:
    return props.get("MIN", 0)


def get_entity_max(props: Dict[str, Any]) -> float | None:
    return props.get("MAX", 50.0)


def get_entity_step(props: Dict[str, Any]) -> float | None:
    return props.get("STEP", 0.1)


def get_entity_hvac_modes(
    props: Dict[str, Any], default: str = None
) -> list[str] | None:
    return props.get("HVAC_MODES") or default


def get_entity_switch(props: Dict[str, Any]) -> dict[str, int] | None:
    return props.get("SWITCH")


def get_entity_select(props: Dict[str, Any]) -> dict[Any, Any] | None:
    return props.get("VALUES")


def get_entity_select_values_and_default(
    props: dict[str, Any],
) -> tuple[list[str], str] | None:
    values = get_entity_select(props)
    default_index = values.get("default")
    select_map = {k: v for k, v in values.items() if k != "default"}
    return list(select_map.values()), select_map.get(default_index)


def get_entity_reg(
    props: Dict[str, Any],
) -> tuple[int | None, ModbusTcpClient.DATATYPE | None]:
    reg_type = get_entity_type(props)
    if reg_type in [C_REG_TYPE_COILS, C_REG_TYPE_DISCRETE_INPUTS]:
        dt = C_DT_BITS
    else:
        dt = props.get("DT")
    return props.get("REG"), dt


def get_entity_props(entity: str) -> dict:
    return ENTITIES_DICT[entity]


def get_entity_factor(props: Dict[str, Any]) -> float:
    return props.get("FAKTOR", 1.0)


# --------------------------------------------------------------------------------
# Hilfsfunktionen zur Erstellen der aus ENTITIES_DICT abgeleiteten Datenstrukturen
# --------------------------------------------------------------------------------


def _classify_register(props: Dict[str, Any]) -> int | None:
    global \
        C_MIN_INPUT_REGISTER, \
        C_MAX_INPUT_REGISTER, \
        C_MIN_HOLDING_REGISTER, \
        C_MAX_HOLDING_REGISTER, \
        C_MIN_COILS, \
        C_MAX_COILS, \
        C_MIN_DISCRETE_INPUTS, \
        C_MAX_DISCRETE_INPUTS

    reg_type = get_entity_type(props)
    reg_from, dt = get_entity_reg(props)
    if reg_from is None or dt is None:
        return None
    if dt == ModbusTcpClient.DATATYPE.BITS:
        sizeofdt = 1
    else:
        sizeofdt = dt.value[1]
    reg_to = reg_from + sizeofdt - 1

    match reg_type:
        case thismodule.C_REG_TYPE_DISCRETE_INPUTS:
            C_MIN_DISCRETE_INPUTS = min(reg_from, C_MIN_DISCRETE_INPUTS)
            C_MAX_DISCRETE_INPUTS = max(reg_to, C_MAX_DISCRETE_INPUTS)
        case thismodule.C_REG_TYPE_COILS:
            C_MIN_COILS = min(reg_from, C_MIN_COILS)
            C_MAX_COILS = max(reg_to, C_MAX_COILS)
        case thismodule.C_REG_TYPE_INPUT_REGISTERS:
            C_MIN_INPUT_REGISTER = min(reg_from, C_MIN_INPUT_REGISTER)
            C_MAX_INPUT_REGISTER = max(reg_to, C_MAX_INPUT_REGISTER)
        case thismodule.C_REG_TYPE_HOLDING_REGISTERS:
            C_MIN_HOLDING_REGISTER = min(reg_from, C_MIN_HOLDING_REGISTER)
            C_MAX_HOLDING_REGISTER = max(reg_to, C_MAX_HOLDING_REGISTER)

    if is_entity_readonly(props):
        if is_entity_switch(props):
            """Nicht beschreibbar, Schalter (SWITCH!=None)."""
            return MyBinarySensorEntityDescription  # C_REGISTERCLASS_BINARY_SENSOR
        elif is_entity_select(props):
            """Nicht beschreibbar, Auswahl (VALUES enthält mindestens ein Element)."""
            return MySensorEntityDescription  # C_REGISTERCLASS_SELECT_ENTITY
        else:
            """Nicht beschreibbar, kein Schalter (SWITCH=None)."""
            return MySensorEntityDescription  # C_REGISTERCLASS_SENSOR
    else:
        if is_entity_switch(props):
            """Beschreibbar, Schalter (SWITCH!=None)."""
            return MyBinaryEntityDescription  # C_REGISTERCLASS_BINARY_ENTITY
        elif is_entity_select(props):
            """Beschreibbar, Auswahl (VALUES enthält mindestens ein Element)."""
            return MySelectEntityDescription  # C_REGISTERCLASS_SELECT_ENTITY
        elif is_entity_climate(props):
            """Beschreibbar, Nur Temperatureinheiten (°C oder K) zulassen"""
            return MyClimateEntityDescription  # C_REGISTERCLASS_CLIMATE_ENTITY
        else:
            """Beschreibbar, kein Schalter (SWITCH=None), keine Auswahl (VALUES ist None), Einheit optional, aber nicht °C oder K."""
            return MyNumberEntityDescription  # C_REGISTERCLASS_NUMBER_ENTITY


def _unit_mapping(
    unit: Optional[str],
) -> tuple[Optional[str], Optional[SensorDeviceClass], Optional[SensorStateClass]]:
    """
    Mappt unsere Einheit (UNIT) auf Home-Assistant native_unit_of_measurement + device_class + state_class.
    Für unbekannte Einheiten bleiben Klassen leer.
    """
    if unit is None:
        return None, None, None

    u = unit.strip()
    # Temperatur
    if u == "°C":
        return (
            UnitOfTemperature.CELSIUS,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
        )
    if u == "K":
        # Selten als absolute Temperatur; hier i. d. R. Offsets -> als °C nicht sinnvoll.
        return (
            UnitOfTemperature.KELVIN,
            SensorDeviceClass.TEMPERATURE,
            SensorStateClass.MEASUREMENT,
        )

    # Druck
    if u.lower() in {"bar"}:
        return (
            UnitOfPressure.BAR,
            SensorDeviceClass.PRESSURE,
            SensorStateClass.MEASUREMENT,
        )

    # Energie & Leistung
    if u.lower() in {"kwh", "kW/h".lower()}:  # akzeptiere beide Schreibweisen
        return (
            UnitOfEnergy.KILO_WATT_HOUR,
            SensorDeviceClass.ENERGY,
            SensorStateClass.TOTAL_INCREASING,
        )
    if u.lower() in {"w"}:
        return UnitOfPower.WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT
    if u.lower() in {"kw"}:
        return (
            UnitOfPower.KILO_WATT,
            SensorDeviceClass.POWER,
            SensorStateClass.MEASUREMENT,
        )

    # Volumenstrom
    if u.lower() in {"l/min", "l/Min", "l pro min"}:
        return "l/min", None, SensorStateClass.MEASUREMENT
    if u.lower() in {"m³/h"}:
        return "m³/h", None, SensorStateClass.MEASUREMENT

    # Drehzahl / Stellgrad
    if u == "‰":
        return "‰", None, SensorStateClass.MEASUREMENT
    if u == "%":
        return "%", None, SensorStateClass.MEASUREMENT

    # PPM, Anteil
    if u == "ppm":
        return "ppm", None, SensorStateClass.MEASUREMENT

    # Zeit/Dauer
    if u.lower() in {"h", "std"}:
        return "h", SensorDeviceClass.DURATION, SensorStateClass.TOTAL_INCREASING
    if u.lower() in {"min"}:
        return "min", SensorDeviceClass.DURATION, SensorStateClass.MEASUREMENT
    if u.lower() in {"s", "sek", "sec"}:
        return "s", SensorDeviceClass.DURATION, SensorStateClass.MEASUREMENT

    # Restdauer
    if u.lower() in {"d", "days"}:
        return "d", SensorDeviceClass.DURATION, SensorStateClass.MEASUREMENT

    # Fallback: nutze Roh-Einheit ohne Device-Class
    return u, None, SensorStateClass.MEASUREMENT


_initialized = False


def init():
    global \
        _initialized, \
        BINARYSENSOR_TYPES, \
        SENSOR_TYPES, \
        SELECT_TYPES, \
        CLIMATE_TYPES, \
        NUMBER_TYPES, \
        BINARY_TYPES
    if _initialized:
        return
    _LOGGER.info(
        "****************************************  initalizing ***************************************"
    )

    thismodule.BINARYSENSOR_TYPES = {}
    thismodule.SENSOR_TYPES = {}
    thismodule.SELECT_TYPES = {}
    thismodule.CLIMATE_TYPES = {}
    thismodule.NUMBER_TYPES = {}
    thismodule.BINARY_TYPES = {}

    for c_key, props in ENTITIES_DICT.items():
        entity_key: str = c_key
        name: str = get_entity_name(props, entity_key)
        registerclass = _classify_register(props)

        match registerclass:
            case thismodule.MySensorEntityDescription:
                unit, device_class, state_class = _unit_mapping(get_entity_unit(props))
                _LOGGER.debug(f"Sensor {entity_key}: {name}, Einheit {unit}")
                SENSOR_TYPES[entity_key] = registerclass(
                    name=name,
                    key=entity_key,
                    native_unit_of_measurement=unit,
                    device_class=device_class,
                    state_class=state_class,
                )

            case thismodule.MyBinarySensorEntityDescription:
                _LOGGER.debug(f"Binär-Sensor {entity_key}: {name}")
                BINARYSENSOR_TYPES[entity_key] = registerclass(
                    name=name,
                    key=entity_key,
                )

            case thismodule.MyClimateEntityDescription:
                # key = f"{C_PREFIX_CLIMATE}_{entity_key}"
                min_value = get_entity_min(props)
                max_value = get_entity_max(props)
                step = get_entity_step(props)
                hvac_modes = get_entity_hvac_modes(props)
                temperature_unit = get_entity_unit(props)
                _LOGGER.debug(
                    f"Temperatur-Stellwert {entity_key}: {name}, {min_value}-{max_value}{temperature_unit} in {step}-er Schritten"
                )
                CLIMATE_TYPES[entity_key] = registerclass(
                    name=name,
                    key=entity_key,
                    min_value=min_value,
                    max_value=max_value,
                    step=step,
                    hvac_modes=hvac_modes,
                    temperature_unit=temperature_unit,
                    supported_features=props.get(
                        "FEATURES", ClimateEntityFeature.TARGET_TEMPERATURE
                    ),
                )

            case thismodule.MyNumberEntityDescription:
                # key = f"{C_PREFIX_NUMBER}_{entity_key}"
                min_value = get_entity_min(props)
                max_value = get_entity_max(props)
                step = get_entity_step(props)
                unit_of_measurement = get_entity_unit(props)
                _LOGGER.debug(
                    f"Numerischer Stellwert {entity_key}: {name}, {min_value}-{max_value}{unit_of_measurement} in {step}-er Schritten"
                )
                NUMBER_TYPES[entity_key] = registerclass(
                    name=name,
                    key=entity_key,
                    min_value=min_value,
                    max_value=max_value,
                    step=step,
                    unit_of_measurement=unit_of_measurement,
                    editable=is_entity_readwrite(props),
                    mode="box",
                )

            case thismodule.MyBinaryEntityDescription:
                # key = f"{C_PREFIX_SWITCH}_{entity_key}"
                _LOGGER.debug(f"Schalter {entity_key}: {name}")
                BINARY_TYPES[entity_key] = registerclass(
                    name=name,
                    key=entity_key,
                )

            case thismodule.MySelectEntityDescription:
                # key = f"{C_PREFIX_SELECT}_{entity_key}"
                values, default = get_entity_select_values_and_default(props)
                _LOGGER.debug(
                    f"Auswahl-Entität {entity_key}: {name}, Werte-Bereich: {values}, Default: {default}"
                )
                SELECT_TYPES[entity_key] = registerclass(
                    name=name,
                    key=entity_key,
                    select_options=values,
                    default_select_option=default,
                )

            case _:
                _LOGGER.warning(f"Unbekannter Entitätstyp {entity_key}: {props}")
                print(f"Sensor konnte nicht zugeordnet werden: {entity_key}/{name}")

    _initialized = True
    _LOGGER.debug(
        f"Status-Register (r/o) von {C_MIN_INPUT_REGISTER} bis {C_MAX_INPUT_REGISTER}"
    )
    _LOGGER.debug(
        f"Discrete Inputs-Register (r/o) von {C_MIN_DISCRETE_INPUTS} bis {C_MAX_DISCRETE_INPUTS}"
    )
    _LOGGER.debug(f"- {len(SENSOR_TYPES)} Sensoren")
    _LOGGER.debug(f"- {len(BINARYSENSOR_TYPES)} Binär-Sensoren")
    _LOGGER.debug(
        f"Holding-Register (r/w) von {C_MIN_HOLDING_REGISTER} bis {C_MAX_HOLDING_REGISTER}"
    )
    _LOGGER.debug(f"Coils (r/w) von {C_MIN_COILS} bis {C_MAX_COILS}")
    _LOGGER.debug(f"- {len(SELECT_TYPES)} Auswahl-Entitäten")
    _LOGGER.debug(f"- {len(BINARY_TYPES)} Schalter")
    _LOGGER.debug(f"- {len(CLIMATE_TYPES)} Temperatur-Stellwerte")
    _LOGGER.debug(f"- {len(NUMBER_TYPES)} Numerische Stellwerte")
    _LOGGER.info(
        "****************************************  initalized ****************************************"
    )


init()
