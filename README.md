# Hikvision ISAPI (Universal) — Home Assistant Integration

Universal Hikvision ISAPI integration for Home Assistant.

- Discovers leaf parameters under `/ISAPI/Image/channels/<n>` and exposes them as sensors.
- Typed entities for common parameters (numbers/selects/switches).
- Universal `set_by_xpath` service to change any parameter.
- Digest or Basic authentication.

## Install (HACS)
1. Make this repository public.
2. Add it in HACS as a custom repository (category: Integration) OR publish a GitHub release (e.g. `v0.2.2`) and submit to the HACS default index.
3. Install via HACS and restart Home Assistant.

## Manual Install
Copy `custom_components/hikvision_isapi/` to your HA config and restart.

## Services
- `hikvision_isapi.set_by_xpath` with fields: `xpath`, `value`, optional `prefer_sub`, `wrap`.
- `hikvision_isapi.set_raw_xml` to PUT raw XML to a path.

## Versioning
Version uses SemVer (e.g., `0.2.2`) for compatibility with AwesomeVersion.
