# homeassistant-custom-components-pagerduty
Adds a PagerDuty sensor to home assistant.
Sensor state is the number of assigned incidents.
Sensor contains incidents attribute which contains a list of assigned incidents.
Queries PagerDuty API for all incidents assigned to a user.

## Support
[![coffee](https://www.buymeacoffee.com/assets/img/custom_images/black_img.png)](https://www.buymeacoffee.com/jmacri)

## Getting Started

### Install component
Copy `/custom_components/pagerduty/` to the following directory in Home Assistant:
`<config directory>/custom_components/pagerduty/`

### Define sensor
Add the following to `<config directory>/configuration.yaml`
**Example configuration.yaml:**

```yaml
sensor:
  platform: pagerduty
  name: Pager Duty
  pagerduty_user_id: 'YOUR_PAGERDUTY_USER_ID'
  api_token: 'YOUR_PAGER_DUTY_API_TOKEN'
  scan_interval:
    seconds: 15
```

**Configuration variables:**

key | description
:--- | :---
**platform (Required)** | The platform name
**name (Required)** | Name your feed
**pagerduty_user_id (Required)** | Your PagerDuty User ID (see section below)
**api_token (Required)** | Your PagerDuty API Token (see section below)
**scan_interval (Optional)** | Update interval. Defaults to 15 seconds

***

#### Getting User ID and API Token from PagerDuty
Your pager duty User ID can be found by going to your profile page.
The URL should be of the format `https://your_org_name.pagerduty.com/users/USER_ID`. Copy the value of USER_ID to the pagerduty_user_id sensor variable.

You can create an API Token by going to Integrations -> API Access Keys.