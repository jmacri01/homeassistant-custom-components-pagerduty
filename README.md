# homeassistant-custom-components-pagerduty
This is being abandoned in favor of https://github.com/jdrozdnovak/ha_pagerduty
Adds a PagerDuty incidents sensor and PagerDuty on call schedules binary sensor to home assistant.
## Incidents Sensor
State is the highest level status across all incidents (triggered, acknowledged, none).
Attributes contain a list of assigned incidents.

## On Call Schedules Binary Sensor
State is on when configured user is on call for any schedule.
Attributes contain a list of assigned schedules.

## Support
[![coffee](https://www.buymeacoffee.com/assets/img/custom_images/black_img.png)](https://www.buymeacoffee.com/jmacri)

## Getting Started

### Install component
Add as a custom HACS repository
OR
Copy `/custom_components/pagerduty/` to the following directory in Home Assistant:
`<config directory>/custom_components/pagerduty/`

### Define sensor
Add the following to `<config directory>/configuration.yaml`
**Example configuration.yaml:**

```yaml
sensor:
- platform: pagerduty
  name: Pager Duty Incidents
  type: incidents
  pagerduty_user_id: 'YOUR_PAGERDUTY_USER_ID'
  api_token: 'YOUR_PAGER_DUTY_API_TOKEN'
  scan_interval:
    seconds: 15
- platform: pagerduty
  name: Pager Duty On Call Schedules
  type: oncallschedules
  pagerduty_user_id: 'YOUR_PAGERDUTY_USER_ID'
  api_token: 'YOUR_PAGER_DUTY_API_TOKEN'
  scan_interval:
    minutes: 5	
```

**Configuration variables:**

key | description
:--- | :---
**platform (Required)** | The platform name
**name (Required)** | Name your feed
**type (Required)** | incidents or oncallschedules
**pagerduty_user_id (Required)** | Your PagerDuty User ID (see section below)
**api_token (Required)** | Your PagerDuty API Token (see section below)
**scan_interval (Optional)** | Update interval. Defaults to 15 seconds for incidents and 5 minutes for oncallschedules

***

#### Getting User ID and API Token from PagerDuty
Your pager duty User ID can be found by going to your profile page.
The URL should be of the format `https://your_org_name.pagerduty.com/users/USER_ID`. Copy the value of USER_ID to the pagerduty_user_id sensor variable.

You can create an API Token by going to Integrations -> API Access Keys.
