from __future__ import annotations
from homeassistant import config_entries
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.data_entry_flow import FlowResult
import voluptuous as vol
import logging
from .const import DOMAIN, CONF_IP, CONF_PORT, CONF_SSL, CONF_VERIFY_SSL, CONF_TIMEOUT, CONF_CHANNEL, CONF_AUTH_TYPE

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_IP): str,
    vol.Optional(CONF_PORT, default=80): int,
    vol.Optional(CONF_SSL, default=False): bool,
    vol.Required(CONF_USERNAME): str,
    vol.Required(CONF_PASSWORD): str,
    vol.Optional(CONF_VERIFY_SSL, default=False): bool,
    vol.Optional(CONF_TIMEOUT, default=8.0): vol.Coerce(float),
    vol.Optional(CONF_CHANNEL, default=1): int,
    vol.Optional(CONF_AUTH_TYPE, default="digest"): vol.In(["digest","basic"]),
})

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        try:
            if user_input is None:
                return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA)
            await self.async_set_unique_id(f"{user_input['ip']}:{user_input.get('port',80)}:{user_input.get('channel',1)}")
            self._abort_if_unique_id_configured()
            title = f"Hikvision ({user_input['ip']})"
            return self.async_create_entry(title=title, data=user_input)
        except Exception as exc:
            _LOGGER.exception("Config flow error: %s", exc)
            return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA, errors={"base": "unknown"})
