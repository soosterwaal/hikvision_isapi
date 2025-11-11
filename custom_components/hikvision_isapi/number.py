from __future__ import annotations
from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from .coordinator import HikvisionCoordinator
from .entity_map import TYPED_SUFFIX_PARAMS
from .utils import path_to_xpath

def _matches(coord: HikvisionCoordinator, suffix: str):
    for path in coord.data.keys():
        if path.endswith(suffix):
            yield path

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    store = hass.data[DOMAIN][entry.entry_id]
    coord: HikvisionCoordinator = store["coordinator"]

    entities = []
    for item in TYPED_SUFFIX_PARAMS:
        if item.get("platform") != "number":
            continue
        suffix = item["suffix"]
        for path in _matches(coord, suffix):
            entities.append(HikvisionNumber(coord, path, item))
    if entities:
        async_add_entities(entities)

class HikvisionNumber(CoordinatorEntity[HikvisionCoordinator], NumberEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, path: str, meta: dict):
        super().__init__(coordinator)
        self._path = path
        self._meta = meta
        self._attr_unique_id = f"hik_num_{abs(hash(path))}"
        self._attr_name = meta.get("name") or path.rsplit('/',1)[-1]
        self._attr_native_min_value = float(meta.get("min", 0))
        self._attr_native_max_value = float(meta.get("max", 100))
        self._attr_native_step = float(meta.get("step", 1))

    @property
    def native_value(self):
        val = self.coordinator.data.get(self._path)
        try:
            return float(val)
        except (TypeError, ValueError):
            return None

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.client.set_by_xpath(path_to_xpath(self._path), str(int(value)))
        await self.coordinator.async_request_refresh()
