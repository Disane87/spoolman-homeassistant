
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Validate](https://github.com/Disane87/spoolman-homeassistant/actions/workflows/validate.yml/badge.svg)](https://github.com/Disane87/spoolman-homeassistant/actions/workflows/validate.yml)
![GitHub all releases](https://img.shields.io/github/downloads/Disane87/spoolman-homeassistant/total)
![GitHub](https://img.shields.io/github/license/Disane87/spoolman-homeassistant)
![GitHub issues by-label](https://img.shields.io/github/issues/Disane87/spoolman-homeassistant/bug?color=red)
![GitHub contributors](https://img.shields.io/github/contributors/Disane87/spoolman-homeassistant)
[![semantic-release: angular](https://img.shields.io/badge/semantic--release-conventionalcommits-e10079?logo=semantic-release)](https://github.com/semantic-release/semantic-release)


# Spoolman Home Assistant Integration

This integration integrates Spoolman (https://github.com/Donkie/Spoolman/) into Home Assistant. This enables you to observe your filament spools and in example get notified when a spool runs out of filament.

# ✨ Features
- Locations in Spoolman are created as devices
- Spools are added to the devices
- Monitoring of filament consumption (used and remaining length/weight)
- Configurable thresholds for info, warning and critical states. This is useful to trigger notifications in HomeAssistant within an automation (see the [automation example](#automation-example))
- Enable/disabled archived spools
- Archived spools are grouped into one `Archived` device

> [!NOTE]
> If one of the threshold is exceeded the integration fires an event. The event is named `spoolman_spool_threshold_exceeded`. Currently there are three thresholds defined: `info`, `warning` and `critical`.


> [!IMPORTANT]
> If one of the threshold is exceeded, there is no other event for that particular threshold and spool until restart of HomeAssistant.

# 🏗️ Installation
Just add this repo to the custom repos in HACS (https://hacs.xyz/docs/faq/custom_repositories/) and you're good to go. You should now see the integration in HACS where you can download the latest version.

# 🛠️ Usage
Just add a new integration for Spoolman and fill in the URL to your Spoolman instance, like this:

![image](resources/images/spoolman-integration-config.png?raw=true)

You should now see a new integration entry with one device per location (your spoolman instance) and all archived spools grouped in an own device:

![image](resources/images/spoolman-integration-devices.png?raw=true)

![image](resources/images/spoolman-integration-hass.png?raw=true)

For every spool there is a sensor created with the exact color you've provided. Additionally the integration tracks your current weight and lengths.

All other information provides by Spoolman are stored in the attributes of the sensor:

![image](resources/images/spoolman-integration-sensor.png?raw=true)

# Automation example
An automation in Homeassistant could be something like this:
```yaml
alias: Filament almost empty
description: ""
trigger:
  - platform: event
    event_type: spoolman_spool_threshold_exceeded
condition: []
action:
  - service: notify.mobile_app_iphone_marco
    data_template:
      title: "{{ trigger.event.data.threshold_name }}: Spool almost empty"
      message: >-
        The spool {{ trigger.event.data.spool.filament.vendor.name }} {{
        trigger.event.data.spool.filament.filament.name }} {{
        trigger.event.data.spool.filament.filament.material }} has reached {{
        trigger.event.data.spool.used_percentage }}% usage
mode: restart
```

You can use the following data within your templates:
```json
{
    "entity_id": self.entity_id,
    "spool": spool,
    "threshold_name": threshold_name,
    "threshold_value": config_threshold,
    "used_percentage": used_percentage,
}
```

A spool has this structure (according to the [OpenAPI description](https://donkie.github.io/Spoolman/) of Spoolman):

```json
{
    "id": 1,
    "registered": "2023-09-22T19:52:36Z",
    "first_used": "2023-09-23T04:22:26.975000Z",
    "last_used": "2023-09-30T04:09:34.242017Z",
    "filament": {
        "id": 1,
        "registered": "2023-09-22T19:52:07Z",
        "name": "Black",
        "vendor": {
            "id": 1,
            "registered": "2023-09-22T19:43:26Z",
            "name": "Jayo"
        },
        "material": "PLA+",
        "price": 15.99,
        "density": 1.24,
        "diameter": 1.75,
        "weight": 1100,
        "article_number": "B0BJ1FR86Y",
        "comment": "",
        "settings_extruder_temp": 210,
        "settings_bed_temp": 60,
        "color_hex": "000000"
    },
    "remaining_weight": 4.468290721106769,
    "used_weight": 1095.5317092788932,
    "remaining_length": 1498.1446855790216,
    "used_length": 367313.8366728618,
    "location": "Lager",
    "lot_nr": "1704306141A",
    "archived": false
}
```

# Cheers 🔥
