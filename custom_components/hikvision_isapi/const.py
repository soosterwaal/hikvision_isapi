DOMAIN = "hikvision_isapi"

DEFAULT_PORT = 80
DEFAULT_SSL = False
DEFAULT_VERIFY_SSL = False
DEFAULT_TIMEOUT = 8.0
DEFAULT_CHANNEL = 1
DEFAULT_AUTH_TYPE = "digest"  # or "basic"

CONF_IP = "ip"
CONF_PORT = "port"
CONF_SSL = "ssl"
CONF_VERIFY_SSL = "verify_ssl"
CONF_TIMEOUT = "timeout"
CONF_CHANNEL = "channel"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_AUTH_TYPE = "auth_type"

SERVICE_SET_BY_XPATH = "set_by_xpath"
SERVICE_SET_RAW_XML = "set_raw_xml"

PLATFORMS = ["sensor", "number", "select", "switch"]
