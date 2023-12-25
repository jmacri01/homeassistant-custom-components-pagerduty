"""PagerDuty sensor."""
from __future__ import annotations
import json
import logging
from pdpyras import APISession
from datetime import timedelta
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import CONF_NAME, CONF_SCAN_INTERVAL

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

__version__ = "1.0.0"

COMPONENT_REPO = "TBD"

REQUIREMENTS = ["pdpyras"]

CONF_PAGERDUTY_USER_ID = "pagerduty_user_id"
CONF_API_TOKEN = "api_token"

DEFAULT_SCAN_INTERVAL = timedelta(seconds=15)
DEFAULT_THUMBNAIL = "https://www.home-assistant.io/images/favicon-192x192-full.png"
DEFAULT_TOPN = 9999

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_PAGERDUTY_USER_ID): cv.string,
        vol.Required(CONF_API_TOKEN): cv.string,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.time_period,
    },
)

_LOGGER: logging.Logger = logging.getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_devices: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the PagerDuty sensor."""
    async_add_devices(
        [
            PagerDutySensor(
                pagerduty_user_id=config[CONF_PAGERDUTY_USER_ID],
                name=config[CONF_NAME],
                api_token=config[CONF_API_TOKEN],
                scan_interval=config[CONF_SCAN_INTERVAL],
            ),
        ],
        update_before_add=True,
    )


class PagerDutySensor(SensorEntity):
    """Representation of a PagerDuty sensor."""

    _attr_force_update = True

    def __init__(
        self: PagerDutySensor,
        pagerduty_user_id: str,
        name: str,
        api_token: str,
        scan_interval: timedelta,
    ) -> None:
        """Initialize the PagerDuty sensor."""
        self._pagerduty_user_id = pagerduty_user_id
        self._api_token = api_token
        self._attr_name = name
        self._attr_icon = "mdi:alarm-light"
        self._scan_interval = scan_interval
        self._incidents: list[dict[str, str]] = []
        self._attr_extra_state_attributes = {"incidents": self._incidents}
        self._attr_attribution = "PagerDuty data"
        _LOGGER.debug("PagerDutySensor initialized - %s", self)

    def __repr__(self: PagerDutySensor) -> str:
        """Return the representation."""
        return 'PagerDutySensor(name="{self.name}", pagerduty_user_id="{self._pagerduty_user_id}", scan_interval="{self._scan_interval}"'

    def update(self: PagerDutySensor) -> None:
        """Make call to PagerDuty API and update the state of the sensor."""
        _LOGGER.debug("Polling PagerDuty for user %s", self._pagerduty_user_id)

        session = APISession(self._api_token)
        response = session.rget("/incidents?user_ids[]=" + self._pagerduty_user_id)

        _LOGGER.debug("Received PagerDuty response: %s", response)

        self._incidents.clear()
        for incident in response:
            incident_to_add = {}
            if "service" in incident and "summary" in incident["service"]:
                incident_to_add.update(
                    {"impacted_service": incident["service"]["summary"]}
                )

            if "title" in incident:
                incident_to_add.update({"title": incident["title"]})

            if "description" in incident:
                incident_to_add.update({"description": incident["description"]})

            if "status" in incident:
                incident_to_add.update({"status": incident["status"]})

            self._incidents.append(incident_to_add)

            _LOGGER.debug("Added incident: %s", incident_to_add)
