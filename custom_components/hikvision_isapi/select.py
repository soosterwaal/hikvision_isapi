from __future__ import annotations
from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from .coordinator import HikvisionCoordinator
from .entity_map import TYPED_SUFFIX_PARAMS
from .utils import stable_uid, path_to_xpath  # path_to_xpath from your earlier fix

def _matches(coord: HikvisionCoordinator, suffix: str):
    for path in coord.data.keys():
        if path.endswith(suffix):
            yield path

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    store = hass.data[DOMAIN][entry.entry_id]
    coord: HikvisionCoordinator = store["coordinator"]
    entry_id = entry.entry_id

    entities = []
    for item in TYPED_SUFFIX_PARAMS:
        if item.get("platform") != "select":
            continue
        suffix = item["suffix"]
        for path in _matches(coord, suffix):
            entities.append(HikvisionSelect(coord, path, item, entry_id))
    if entities:
        async_add_entities(entities)

class HikvisionSelect(CoordinatorEntity[HikvisionCoordinator], SelectEntity):
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
