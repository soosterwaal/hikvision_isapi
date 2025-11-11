from __future__ import annotations
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from .coordinator import HikvisionCoordinator
from .entity_map import TYPED_SUFFIX_PARAMS
from .utils import stable_uid, path_to_xpath

def _matches(coord: HikvisionCoordinator, suffix: str):
    for path in coord.data.keys():
        if path.endswith(suffix):
            yield path

def _truthy(val: str, on_list: list[str]) -> bool:
    if val is None:
        return False
    return str(val).strip().lower() in [x.lower() for x in on_list]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    store = hass.data[DOMAIN][entry.entry_id]
    coord: HikvisionCoordinator = store["coordinator"]
    entry_id = entry.entry_id

    entities = []
    for item in TYPED_SUFFIX_PARAMS:
        if item.get("platform") != "switch":
            continue
        suffix = item["suffix"]
        for path in _matches(coord, suffix):
            entities.append(HikvisionSwitch(coord, path, item, entry_id))
    if entities:
        async_add_entities(entities)

class HikvisionSwitch(CoordinatorEntity[HikvisionCoordinator], SwitchEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, path: str, meta: dict, entry_id: str):
        super().__init__(coordinator)
        self._path = path
        self._meta = meta
        self._entry_id = entry_id
        self._attr_unique_id = f"hik_swi_{stable_uid(entry_id, path)}"
        self._attr_name = meta.get("name") or path.rsplit('/',1)[-1]
        self._sub = path.rsplit('/')[2]
        self._on_vals = meta.get("on", ["true","1","on","enabled"])
        self._off_vals = meta.get("off", ["false","0","off","disabled"])

    @property
    def is_on(self):
        val = self.coordinator.data.get(self._path)
        return _truthy(val, self._on_vals)

    async def async_turn_on(self, **kwargs):
        await self.coordinator.client.set_by_xpath(path_to_xpath(self._path), self._on_vals[0], prefix_subpath=self._sub)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        await self.coordinator.client.set_by_xpath(path_to_xpath(self._path), self._off_vals[0], prefix_subpath=self._sub)
        await self.coordinator.async_request_refresh()
