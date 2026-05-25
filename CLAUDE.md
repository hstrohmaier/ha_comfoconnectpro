# ha_comfoconnectpro

Home Assistant custom integration for the Zehnder ComfoConnect PRO ventilation unit via Modbus TCP.

## Architecture

All Modbus registers are declared once in `ENTITIES_DICT` in `const.py`. The `init()` function (called at import time) classifies each entry into typed dicts — `SENSOR_TYPES`, `SELECT_TYPES`, `BINARY_TYPES`, `NUMBER_TYPES`, etc. — based on register type and data shape. Each platform file (`sensor.py`, `select.py`, etc.) calls `setup_platform_from_types()` from `entity_common.py`, which instantiates the appropriate `HubBackedEntity` subclass for every entry in its dict.

The climate entity is an exception: it is a composite entity not backed by a single register. It is created manually in `climate.py:async_setup_entry` using `get_hub_and_device_info()` from `entity_common.py`.

## Adding or Modifying an Entity

1. Add or edit the entry in `ENTITIES_DICT` in `const.py`.
2. Register fields: `RT` (register type), `REG` (0-based address), `NAME`, `DT` (data type), and optionally `UNIT`, `FAKTOR`, `MIN`, `MAX`, `VALUES` (for selects/enums), `PF` (platform override).
3. Add translation strings to `translations/en.json` and `translations/de.json` under the matching platform key.
4. No platform code changes needed unless adding a new platform.

**Register types:**
- `C_REG_TYPE_INPUT_REGISTERS` → read-only sensor
- `C_REG_TYPE_HOLDING_REGISTERS` → read-write (number/select/climate)
- `C_REG_TYPE_DISCRETE_INPUTS` → read-only binary sensor
- `C_REG_TYPE_COILS` → read-write switch

**Platform override:** Add `"PF": Platform.NUMBER` (or other platform) to force classification regardless of register type.

## Hub (`MyModbusHub` in `__init__.py`)

- Polls all registers every N seconds (default 15) via `async_refresh_modbus_data()`.
- Decoded values are stored in `hub.data[entity_key]` as Python-native types (str for selects/enums, float for numerics, bool for switches).
- Write via `hub.write_entity_value(entity_key, value)` — handles encoding and triggers a refresh.
- Entity callbacks are registered via `hub.async_add_my_modbus_sensor(callback)`.

## Entity Update Flow

`HubBackedEntity._on_hub_update()` (in `entity_common.py`) is called on every poll. For single-register entities it calls `_apply_hub_payload(hub.data[description.key])`. Override `_on_hub_update` directly (as the climate entity does) when aggregating multiple registers.

## Linting

```
ruff check .
ruff format .
```

## CI

GitHub Actions run `hassfest` (HA manifest validation) and `hacs` validation on every push. No unit tests.
