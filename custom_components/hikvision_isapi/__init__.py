from __future__ import annotations

import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.core import HomeAssistant, ServiceCall

from .const import (
    DOMAIN,
    PLATFORMS,
    SERVICE_SET_BY_XPATH,
    SERVICE_SET_RAW_XML,
    CONF_IP,
    CONF_PORT,
    CONF_SSL,
    CONF_VERIFY_SSL,
    CONF_TIMEOUT,
    CONF_CHANNEL,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_AUTH_TYPE,
)
from .api import HikvisionIsapiClient
from .coordinator import HikvisionCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Hikvision ISAPI integration from a config entry."""
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

    # Niet blokkeren tijdens boot: initial refresh met timebox, daarna in background
    async def _initial_refresh() -> None:
        try:
            await asyncio.wait_for(coord.async_config_entry_first_refresh(), timeout=6)
        except asyncio.TimeoutError:
            _LOGGER.warning(
                "Hikvision ISAPI: initial refresh timed out; will continue in background"
            )
            hass.async_create_task(coord.async_request_refresh())
        except Exception as exc:  # noqa: BLE001
            _LOGGER.warning(
                "Hikvision ISAPI: initial refresh failed: %s; will retry later", exc
            )

    hass.async_create_task(_initial_refresh())

    # Sluit HTTP client netjes bij HA stop
    def _on_stop(_event) -> None:
        hass.async_create_task(client.close())

    unsub_stop = hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, _on_stop)

    # Bewaar referenties
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "client": client,
        "coordinator": coord,
        "unsub_stop": unsub_stop,
    }

    # Services
    async def _svc_set_by_xpath(call: ServiceCall) -> None:
        xpath = call.data["xpath"]
        value = str(call.data["value"])
        prefer_sub = call.data.get("prefer_sub")
        wrap = call.data.get("wrap")
        await client.set_by_xpath(xpath, value, prefer_sub=prefer_sub, wrap=wrap)
        await coord.async_request_refresh()

    async def _svc_set_raw_xml(call: ServiceCall) -> None:
        path = call.data.get("path", f"/Image/channels/{client.channel}")
        xml = call.data["xml"]
        await client.put_xml(path, xml)
        await coord.async_request_refresh()

    # NB: services zijn global; alleen één keer registreren is genoeg.
    # Als je meerdere entries verwacht, kun je per entry unieke service-namen maken,
    # maar voor 1 camera is dit prima.
    if not hass.services.has_service(DOMAIN, SERVICE_SET_BY_XPATH):
        hass.services.async_register(DOMAIN, SERVICE_SET_BY_XPATH, _svc_set_by_xpath)
    if not hass.services.has_service(DOMAIN, SERVICE_SET_RAW_XML):
        hass.services.async_register(DOMAIN, SERVICE_SET_RAW_XML, _svc_set_raw_xml)

    # Laad platforms (sensor/number/select/switch)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    store = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    if store:
        # stop-listener opheffen
        unsub = store.get("unsub_stop")
        if unsub:
            try:
                unsub()
            except Exception:  # noqa: BLE001
                pass
        # httpx client sluiten
        try:
            await store["client"].close()
        except Exception:  # noqa: BLE001
            pass

    return ok
