from __future__ import annotations
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN, PLATFORMS, SERVICE_SET_BY_XPATH, SERVICE_SET_RAW_XML,     CONF_IP, CONF_PORT, CONF_SSL, CONF_VERIFY_SSL, CONF_TIMEOUT, CONF_CHANNEL, CONF_USERNAME, CONF_PASSWORD, CONF_AUTH_TYPE
from .api import HikvisionIsapiClient
from .coordinator import HikvisionCoordinator

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    data = entry.data
    client = HikvisionIsapiClient(
        host=data[CONF_IP],
        port=data.get(CONF_PORT, 80),
        use_ssl=data.get(CONF_SSL, False),
        verify_ssl=data.get(CONF_VERIFY_SSL, False),
        timeout=data.get(CONF_TIMEOUT, 8.0),
        channel=data.get(CONF_CHANNEL, 1),
        username=data[CONF_USERNAME],
        password=data[CONF_PASSWORD],
        auth_type=data.get(CONF_AUTH_TYPE, "digest"),
    )
    coord = HikvisionCoordinator(hass, client)
    await coord.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {"client": client, "coordinator": coord}

    async def _svc_set_by_xpath(call: ServiceCall):
        xpath = call.data["xpath"]
        value = str(call.data["value"])
        prefer_sub = call.data.get("prefer_sub")
        wrap = call.data.get("wrap")
        await client.set_by_xpath(xpath, value, prefer_sub=prefer_sub, wrap=wrap)
        await coord.async_request_refresh()

    async def _svc_set_raw_xml(call: ServiceCall):
        path = call.data.get("path", f"/Image/channels/{client.channel}")
        xml = call.data["xml"]
        await client.put_xml(path, xml)
        await coord.async_request_refresh()

    hass.services.async_register(DOMAIN, SERVICE_SET_BY_XPATH, _svc_set_by_xpath)
    hass.services.async_register(DOMAIN, SERVICE_SET_RAW_XML, _svc_set_raw_xml)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    store = hass.data[DOMAIN].pop(entry.entry_id, None)
    if store:
        await store["client"].close()
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
