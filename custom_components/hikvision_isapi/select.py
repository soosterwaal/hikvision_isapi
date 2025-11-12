from __future__ import annotations
import asyncio
from typing import Optional

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import HikvisionCoordinator
from .entity_map import TYPED_SUFFIX_PARAMS
from .utils import stable_uid, path_to_xpath  # als je utils met deze helpers al hebt

BLC_OPTIONS = ["off", "UP", "DOWN", "LEFT", "RIGHT", "CENTER", "AUTO"]

def _matches(coord: HikvisionCoordinator, suffix: str):
    for path in (coord.data or {}).keys():
        if path.endswith(suffix):
            yield path

def _truthy(val: Optional[str]) -> bool:
    if val is None:
        return False
    return str(val).strip().lower() in ("true", "1", "on", "enabled")

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    store = hass.data[DOMAIN][entry.entry_id]
    coord: HikvisionCoordinator = store["coordinator"]
    entry_id = entry.entry_id

    # Wacht heel even op eerste data (niet blokkerend voor boot)
    if not coord.data:
        try:
            await asyncio.wait_for(coord.async_request_refresh(), timeout=3)
        except Exception:
            pass

    entities: list[SelectEntity] = []

    # --- 2a) bestaande typed selects uit de suffix-map
    for item in TYPED_SUFFIX_PARAMS:
        if item.get("platform") != "select":
            continue
        suffix = item["suffix"]
        for path in _matches(coord, suffix):
            entities.append(_GenericHikvisionSelect(coord, path, item, entry_id))

    # --- 2b) onze custom BLC select ---
    # We maken 'm als we in de data /BLC/enabled of /BLC/BLCMode tegenkomen.
    has_blc = any(
        p.endswith("/BLC/enabled") or p.endswith("/BLC/BLCMode")
        for p in (coord.data or {}).keys()
    )
    if has_blc:
        entities.append(HikvisionBLCSelect(coord, entry_id))

    if entities:
        async_add_entities(entities)

class _GenericHikvisionSelect(CoordinatorEntity[HikvisionCoordinator], SelectEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, path: str, meta: dict, entry_id: str):
        super().__init__(coordinator)
        self._path = path
        self._meta = meta
        self._entry_id = entry_id
        self._attr_unique_id = f"hik_sel_{stable_uid(entry_id, path)}"
        self._attr_name = meta.get("name") or path.rsplit('/',1)[-1]
        self._attr_options = list(meta.get("options", []))

    @property
    def current_option(self):
        return self.coordinator.data.get(self._path)

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.client.set_by_xpath(path_to_xpath(self._path), option)
        await self.coordinator.async_request_refresh()

class HikvisionBLCSelect(CoordinatorEntity[HikvisionCoordinator], SelectEntity):
    """Select with options off/up/down/left/right/center that writes full BLC payload."""

    _attr_has_entity_name = True
    _attr_options = BLC_OPTIONS
    _attr_icon = "mdi:focus-field"

    def __init__(self, coordinator: HikvisionCoordinator, entry_id: str):
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_unique_id = f"hik_blc_{entry_id}"
        self._attr_name = "Backlight Compensation"

    # Helpers to read current BLC state from flattened XML
    def _get(self, suffix: str) -> Optional[str]:
        # keys like /ImageChannel/.../BLC/enabled or /BLC/BLCMode
        for k, v in (self.coordinator.data or {}).items():
            if k.endswith(suffix):
                return v
        return None

    @property
    def current_option(self) -> Optional[str]:
        enabled = _truthy(self._get("/BLC/enabled"))
        mode = (self._get("/BLC/BLCMode") or "").strip().lower()
        if not enabled:
            return "off"
        # normalize camera values to our options
        m = mode or "center"
        if m not in BLC_OPTIONS:
            # camera gebruikt CAPs: UP/DOWN/LEFT/RIGHT/CENTER
            m = m.lower()
            if m not in BLC_OPTIONS:
                m = "center"
        return m

    async def async_select_option(self, option: str) -> None:
        option = option.strip().lower()
        if option not in BLC_OPTIONS:
            raise ValueError(f"Unsupported BLC option: {option}")

        # Build full BLC payload (namespace + version verplicht)
        if option == "off":
            enabled = "false"
            # behoud vorige mode als die bekend is, anders CENTER
            prev_mode = (self._get("/BLC/BLCMode") or "CENTER").upper()
            mode = prev_mode if prev_mode in ("UP","DOWN","LEFT","RIGHT","CENTER") else "CENTER"
        else:
            enabled = "true"
            mode = option.upper()

        payload = (
            "<BLC xmlns='http://www.hikvision.com/ver20/XMLSchema' version='2.0'>"
            f"<enabled>{enabled}</enabled>"
            f"<BLCMode>{mode}</BLCMode>"
            "</BLC>"
        )

        # write to sub-endpoint if available; otherwise main channel
        path = f"/Image/channels/{self.coordinator.client.channel}/BLC"
        try:
            if await self.coordinator.client.has_endpoint(path):
                await self.coordinator.client.put_xml(path, payload)
            else:
                # some models accept BLC on main channel wrapper
                await self.coordinator.client.put_xml(
                    f"/Image/channels/{self.coordinator.client.channel}", payload
                )
        finally:
            await self.coordinator.async_request_refresh()
