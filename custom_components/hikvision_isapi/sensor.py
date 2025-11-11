from __future__ import annotations
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN
from .coordinator import HikvisionCoordinator
from .utils import stable_uid

def _display_name_from_path(path: str) -> str:
    last = path.rsplit('/', 1)[-1]
    if '[' in last:
        last = last.split('[', 1)[0]
    return last or "parameter"

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    store = hass.data[DOMAIN][entry.entry_id]
    coord: HikvisionCoordinator = store["coordinator"]

    entities = []
    entry_id = entry.entry_id
    for path_key in sorted(coord.data.keys()):
        entities.append(HikvisionParamSensor(coord, path_key, entry_id))
    if entities:
        async_add_entities(entities)

class HikvisionParamSensor(CoordinatorEntity[HikvisionCoordinator], SensorEntity):
    _attr_icon = "mdi:cog"
    _attr_has_entity_name = True

    def __init__(self, coordinator: HikvisionCoordinator, path_key: str, entry_id: str):
        super().__init__(coordinator)
        self._path_key = path_key
        self._entry_id = entry_id
        self._attr_unique_id = f"hik_param_{stable_uid(entry_id, path_key)}"
        self._attr_name = _display_name_from_path(path_key)

    @property
    def native_value(self):
        return self.coordinator.data.get(self._path_key)

    async def async_update(self):
        await self.coordinator.async_request_refresh()
