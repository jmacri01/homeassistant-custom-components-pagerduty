"""PagerDuty sensor."""
from __future__ import annotations
import json
import logging
from pdpyras import APISession
from datetime import timedelta
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.const import CONF_NAME, CONF_SCAN_INTERVAL

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType, StateType

from homeassistant.util import dt as dt_util

__version__ = "1.0.2"

COMPONENT_REPO = "https://github.com/jmacri01/homeassistant-custom-components-pagerduty"

REQUIREMENTS = ["pdpyras"]

CONF_PAGERDUTY_USER_ID = "pagerduty_user_id"
CONF_API_TOKEN = "api_token"
CONF_TYPE = "type"

DEFAULT_INCIDENTS_SCAN_INTERVAL = timedelta(seconds=15)
DEFAULT_ONCALL_SCAN_INTERVAL = timedelta(minutes=5)
DEFAULT_THUMBNAIL = "https://www.home-assistant.io/images/favicon-192x192-full.png"
DEFAULT_TOPN = 9999

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Required(CONF_PAGERDUTY_USER_ID): cv.string,
        vol.Required(CONF_API_TOKEN): cv.string,
        vol.Required(CONF_TYPE): cv.string,
        vol.Optional(CONF_SCAN_INTERVAL): cv.time_period,
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
    if config[CONF_TYPE] == "incidents":
        scan_interval = DEFAULT_INCIDENTS_SCAN_INTERVAL
        if CONF_SCAN_INTERVAL in config:
            scan_interval = config[CONF_SCAN_INTERVAL]
        async_add_devices(
            [
                PagerDutyIncidentsSensor(
                    pagerduty_user_id=config[CONF_PAGERDUTY_USER_ID],
                    name=config[CONF_NAME],
                    api_token=config[CONF_API_TOKEN],
                    scan_interval=scan_interval,
                ),
            ],
            update_before_add=True,
        )
    elif config[CONF_TYPE] == "oncallschedules":
        scan_interval = DEFAULT_ONCALL_SCAN_INTERVAL
        if CONF_SCAN_INTERVAL in config:
            scan_interval = config[CONF_SCAN_INTERVAL]
        async_add_devices(
            [
                PagerDutyOnCallSensor(
                    pagerduty_user_id=config[CONF_PAGERDUTY_USER_ID],
                    name=config[CONF_NAME],
                    api_token=config[CONF_API_TOKEN],
                    scan_interval=scan_interval,
                ),
            ],
            update_before_add=True,
        )
    else:
        _LOGGER.error(
            "Sensor type %s is not recognized. Valid types: incidents, oncallschedules",
            config[CONF_TYPE],
        )


class PagerDutyIncidentsSensor(SensorEntity):
    """Representation of a PagerDutyIncidents sensor."""

    _attr_force_update = True

    def __init__(
        self: PagerDutyIncidentsSensor,
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
        _LOGGER.debug("PagerDutyIncidentsSensor initialized - %s", self)

    def __repr__(self: PagerDutyIncidentsSensor) -> str:
        """Return the representation."""
        return 'PagerDutyIncidentsSensor(name="{self.name}", pagerduty_user_id="{self._pagerduty_user_id}", scan_interval="{self._scan_interval}"'

    def update(self: PagerDutyIncidentsSensor) -> None:
        """Make call to PagerDuty API and update the state of the sensor."""
        _LOGGER.debug("Polling PagerDuty for user %s", self._pagerduty_user_id)

        session = APISession(self._api_token)
        response = session.rget("/incidents?user_ids[]=" + self._pagerduty_user_id)

        _LOGGER.debug("Received PagerDuty response: %s", response)

        self._incidents.clear()
        for incident in response:
            incident_to_add = {}
            if (
                "service" in incident
                and incident["service"] is not None
                and "summary" in incident["service"]
            ):
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

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        state = "none"
        for incident in self._incidents:
            if "status" in incident:
                if incident["status"] == "triggered":
                    return "triggered"
                if incident["status"] == "acknowledged":
                    state = "acknowledged"
        return state


class PagerDutyOnCallSensor(BinarySensorEntity):
    """Representation of a PagerDutyOnCall sensor."""

    _attr_force_update = True

    def __init__(
        self: PagerDutyOnCallSensor,
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
        self._oncallschedules: list[dict[str, str]] = []
        self._attr_extra_state_attributes = {"oncalls": self._oncallschedules}
        _LOGGER.debug("PagerDutyOnCallSensor initialized - %s", self)

    def __repr__(self: PagerDutyOnCallSensor) -> str:
        """Return the representation."""
        return 'PagerDutyOnCallSensor(name="{self.name}", pagerduty_user_id="{self._pagerduty_user_id}", scan_interval="{self._scan_interval}"'

    def update(self: PagerDutyOnCallSensor) -> None:
        """Make call to PagerDuty API and update the state of the sensor."""
        _LOGGER.debug("Polling PagerDuty for user %s", self._pagerduty_user_id)

        session = APISession(self._api_token)
        response = session.rget("/oncalls?user_ids[]=" + self._pagerduty_user_id)

        _LOGGER.debug("Received PagerDuty response: %s", response)

        self._oncallschedules.clear()
        for oncallschedule in response:
            oncallschedule_to_add = {}
            if (
                "schedule" in oncallschedule
                and oncallschedule["schedule"] is not None
                and "summary" in oncallschedule["schedule"]
            ):
                oncallschedule_to_add.update(
                    {"oncall_schedule": oncallschedule["schedule"]["summary"]}
                )
            else:
                continue
            if "start" in oncallschedule:
                oncallschedule_to_add.update(
                    {
                        "start": dt_util.as_local(
                            dt_util.parse_datetime(oncallschedule["start"])
                        )
                    }
                )

            if "end" in oncallschedule:
                oncallschedule_to_add.update(
                    {
                        "end": dt_util.as_local(
                            dt_util.parse_datetime(oncallschedule["end"])
                        )
                    }
                )

            self._oncallschedules.append(oncallschedule_to_add)

            _LOGGER.debug("Added oncall schedule: %s", oncallschedule_to_add)

    @property
    def is_on(self) -> StateType:
        """Return the state of the sensor."""
        for oncallschedule in self._oncallschedules:
            if (
                oncallschedule["end"] is not None
                and oncallschedule["start"] is not None
                and dt_util.now() <= oncallschedule["end"]
                and dt_util.now() >= oncallschedule["start"]
            ):
                return True

        return False
