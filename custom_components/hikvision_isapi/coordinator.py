from __future__ import annotations
from datetime import timedelta
import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

try:
    from lxml import etree as ET
except Exception as e:
    ET = None
    _LOGGER.error("lxml is not available: %s", e)

def _localname(tag: str) -> str:
    if tag and '}' in tag:
        return tag.split('}', 1)[1]
    return tag or ""

def _friendly_path(node) -> str:
    parts = []
    cur = node
    while cur is not None and hasattr(cur, "tag"):
        if isinstance(cur.tag, str):
            parts.append(_localname(cur.tag))
        cur = cur.getparent()
    parts = [p for p in reversed(parts) if p]
    if parts and parts[0] != "ImageChannel":
        parts.insert(0, "ImageChannel")
    return "/" + "/".join(parts)

def flatten_xml(xml: str) -> dict[str, str]:
    if ET is None:
        return {"//rawXml": xml}
    try:
        root = ET.fromstring(xml.encode("utf-8"))
        out = {}
        for node in root.xpath(".//*"):
            if len(node) == 0 and (node.text is not None):
                path = _friendly_path(node)
                key = path
                idx = 1
                while key in out:
                    idx += 1
                    key = f"{path}[{idx}]"
                out[key] = node.text.strip()
        return out
    except Exception as exc:
        _LOGGER.exception("Failed to parse XML: %s", exc)
        return {"//error": str(exc)}

class HikvisionCoordinator(DataUpdateCoordinator[dict]):
    def __init__(self, hass: HomeAssistant, client):
        super().__init__(
            hass,
            _LOGGER,
            name="hikvision_isapi",
            update_interval=timedelta(seconds=60),
        )
        self._client = client

    async def _async_update_data(self) -> dict:
        xml = await self._client.read_image_channel()
        return flatten_xml(xml)

    @property
    def client(self):
        return self._client
