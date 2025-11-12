from __future__ import annotations
import httpx
from typing import Optional, Tuple
from lxml import etree as ET
import logging
_LOGGER = logging.getLogger(__name__)

class HikIsapiError(Exception):
    pass

class HikvisionIsapiClient:
    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        port: int = 80,
        use_ssl: bool = False,
        verify_ssl: bool = False,
        timeout: float = 8.0,
        channel: int = 1,
        auth_type: str = "digest",  # "digest" | "basic"
    ) -> None:
        self.scheme = "https" if use_ssl else "http"
        self.base = f"{self.scheme}://{host}:{port}/ISAPI"
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.channel = channel
        self._digest = (auth_type == "digest")

        auth = httpx.DigestAuth(username, password) if self._digest else (username, password)
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(connect=3.0, read=5.0, write=5.0, pool=5.0),
            limits=httpx.Limits(max_keepalive_connections=0, max_connections=10),
            verify=verify_ssl,
            auth=auth
        )

    async def close(self):
        await self._client.aclose()

    def _url(self, path: str) -> str:
        return f"{self.base}{path}"

    async def get_xml(self, path: str) -> str:
        r = await self._client.get(self._url(path))
        r.raise_for_status()
        return r.text

    async def has_endpoint(self, path: str) -> bool:
        try:
            await self.get_xml(path)
            return True
        except httpx.HTTPStatusError as e:
            if e.response.status_code in (404, 405):
                return False
            raise
        except Exception:
            return False

    async def put_xml(self, path: str, xml: str) -> str:
        r = await self._client.put(self._url(path), content=xml, headers={"Content-Type": "application/xml"})
        r.raise_for_status()
        return r.text if r.text else "OK"

    # -------- Universal read (Image Channel) --------
    async def read_image_channel(self) -> str:
        return await self.get_xml(f"/Image/channels/{self.channel}")
    
    def _nsmap_for(self, root):
        # geef default namespace een prefix 'ns'
        nsmap = {}
        for k, v in (root.nsmap or {}).items():
            if not v:
                continue
            nsmap[k or "ns"] = v
        return nsmap

    def _ns_agnostic(self, xpath: str) -> str:
        # //A/B/C -> //*[local-name()='A']/*[local-name()='B']/*[local-name()='C']
        if not xpath or not xpath.startswith("//"):
            return xpath
        parts = [p for p in xpath[2:].split("/") if p]
        out = []
        for p in parts:
            if "[" in p or "(" in p or p == "*":
                out.append(p)
            else:
                out.append(f"*[(local-name()='{p}')]")
        return "//" + "/".join(out)

    async def read_sub_or_main(self, sub: str) -> Tuple[str, str]:
        """Return (path_used, xml) for either /.../<sub> or main."""
        sub_path = f"/Image/channels/{self.channel}/{sub}"
        _LOGGER.warning("Trying sub-endpoint: %s", sub_path)
        if await self.has_endpoint(sub_path):
            return sub_path, await self.get_xml(sub_path)
        
        _LOGGER.warning("Falling back to main channel for sub-endpoint: %s", sub_path)
        main_path = f"/Image/channels/{self.channel}"
        return main_path, await self.get_xml(main_path)

    # -------- Universal write by XPath --------
    async def set_by_xpath(
        self,
        xpath: str,
        value: str,
        prefer_sub: Optional[str] = None,
        wrap: Optional[str] = None,
    ) -> str:
        """
        xpath: e.g. //Shutter/ShutterTime  or  //DayNight/DayNightFilterType
        prefer_sub: try sub-endpoint like "shutter" or "dayNight" first
        wrap: override wrapper root element when PUTting on main channel (default 'ImageChannel')
        """
        # 1) Pick source XML (sub-endpoint if possible)
        if prefer_sub:
            _LOGGER.warning("Using prefer_sub=%s for xpath=%s", prefer_sub, xpath)
            path, xml_text = await self.read_sub_or_main(prefer_sub)
        else:
            path = f"/Image/channels/{self.channel}"
            xml_text = await self.read_image_channel()

        _LOGGER.warning("Using path=%s and xml_text=%s", path, xml_text)
        root = ET.fromstring(xml_text.encode("utf-8"))

        xpath = self._ns_agnostic(xpath)
        ns = self._nsmap_for(root)
        nodes = root.xpath(xpath, namespaces=ns) if ns else root.xpath(xpath)

        if not nodes:
            # If we read sub xml and failed, try main as fallback for node presence
            if prefer_sub and path.endswith(prefer_sub):
                path = f"/Image/channels/{self.channel}"
                xml_text = await self.read_image_channel()
                root = ET.fromstring(xml_text.encode("utf-8"))
                nodes = root.xpath(xpath, namespaces=ns) if ns else root.xpath(xpath)
        if not nodes:
            raise HikIsapiError(f"XPath not found: {xpath} {xml_text}")

        # 2) Set text on all matched nodes (usually 1)
        changed = False
        for node in nodes:
            if getattr(node, "text", None) != value:
                node.text = value
                changed = True
        if not changed:
            return "No change"

        # 3) Build minimal payload:
        if prefer_sub and path.endswith(prefer_sub):
            payload = ET.tostring(root, encoding="utf-8", xml_declaration=False).decode()
            return await self.put_xml(path, payload)

        top = wrap or "ImageChannel"
        # Find the nearest ancestor under ImageChannel for the first node
        first = nodes[0]
        ancestor = first
        while ancestor.getparent() is not None and ancestor.getparent().tag != top:
            ancestor = ancestor.getparent()
        # Build payload with that container to be reasonably minimal
        container = ET.Element(top)
        container.append(ancestor)
        payload = ET.tostring(container, encoding="utf-8", xml_declaration=False).decode()
        return await self.put_xml(f"/Image/channels/{self.channel}", payload)

    # Convenience setters (typed)
    async def set_shutter(self, value: str):
        return await self.set_by_xpath("//Shutter/ShutterTime", value, prefer_sub="shutter")

    async def set_daynight(self, mode: str):
        return await self.set_by_xpath("//DayNight/DayNightFilterType", mode, prefer_sub="dayNight")

    async def set_mixed_light(self, mode: str):
        # Try common locations; fall back if first fails
        try:
            return await self.set_by_xpath("//MixedLight/mixedLightBrightnessRegulatMode", mode, prefer_sub="mixedLight")
        except Exception:
            return await self.set_by_xpath("//ImageEnhancement/mixedLightBrightnessRegulatMode", mode, prefer_sub=None)
