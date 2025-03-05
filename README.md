
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
- If a Klipper url is configured, the active spool will have an attribute `klipper_active_spool`
- Creation of a service `spoolman.patch_spool` to enable you to change values of a spool from automations

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

> [!IMPORTANT]
> Your spool needs at least a name and a material to get added to Home Assistant.

# Usage in cards
You can use the default `entities` card for this:

![image](./docs/entity-card.png)

Or `auto-entities-card` for getting all entities by this integration dynamically:
https://github.com/thomasloven/lovelace-auto-entities

And a `mushroom-template-card` card for example.
https://github.com/piitaya/lovelace-mushroom/blob/main/docs/cards/template.md

A simple card utilizing `mushroom-template-card` and `auto-entities` to dynamically show all spools could look like this:
```yaml
type: custom:auto-entities
filter:
  include:
    - integration: '*spoolman*'
      sort:
        method: attribute
        attribute: location
        reverse: false
      attributes:
        archived: false
      options:
        type: custom:mushroom-template-card
        vertical: false
        icon_color: '#{{ state_attr(entity, ''filament_color_hex'') }}'
        icon: mdi:printer-3d-nozzle
        badge_icon: |
          {% if state_attr(entity, 'archived') == true %}
            mdi:archive
          {% elif state_attr(entity, 'klipper_active_spool') == true %}
            mdi:check-circle
          {% endif %}
        badge_color: |
          {% if state_attr(entity, 'archived') == true %}
            orange
          {% elif state_attr(entity, 'klipper_active_spool') == true %}
            green
          {% else %}
            default_color
          {% endif %}
        primary: |
          {% set location = state_attr(entity, 'location') %} {% if location %}
            {{ state_attr(entity, 'filament_name') }} ({{ location }})
          {% else %}
            {{ state_attr(entity, 'filament_name') }}
          {% endif %}
        secondary: '{{ (state_attr(entity, ''remaining_weight'') | float)  | round(2) }} g'
        tap_action:
          action: more-info
sort:
  method: attribute
  attribute: klipper_active_spool
  reverse: true
card:
  type: grid
  columns: 2
  square: false
card_param: cards

```
This card does:
- Filtering out all `archived` spools, if not filters all `archived` spools have an orange badge
- Sort by `klipper_active_spool` (only when Klipper url is set in config, active spools is always the first one with green badge)
- Sort by `location` from A-Z
- Shows the `location` after the spool name
- Click on an entity opens the `more_info` dialog

![image](./docs/auto-entities.png)

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
  - service: notify.notify
    data_template:
      title: >-
        {{ trigger.event.data['threshold_name'] | capitalize }}: Spool almost
        empty
      message: >-
        The spool {{ trigger.event.data['spool']['filament']['vendor']['name']
        }} {{ trigger.event.data['spool']['filament']['name'] }} {{
        trigger.event.data['spool']['filament']['material'] }} has reached {{
        trigger.event.data['spool']['used_percentage'] }}% usage
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

# Home Assistant services
This integration creates services to be used in automations:

## `spoolman.patch_spool`
This service is used to change values and properties if a spool. The `data` must match the data for the [Spoolman API](https://donkie.github.io/Spoolman/#tag/spool/operation/Update_spool_spool__spool_id__patch)

> [!IMPORTANT]
> You can't update `remaining_weight` and `used_weight` in one update. You can only set one of them. Spoolmann calculates the missing field by itself.

```yaml
service: spoolman.patch_spool
data:
  id: 45
  first_used: "2019-08-24T14:15:22.000Z"
  last_used: "2019-08-24T14:15:22.000Z"
  price: 20
  initial_weight: 200
  spool_weight: 200
  location: Shelf B
  remaining_weight: 200
  lot_nr: 52342
```

# Extra fields

Spoolman allows the definition of extra fields. You can use these to built your own automations. They are available in the attributes of the spool, with the prefix `extra_`.

You can for example use these to store additional information about the spools, like their humidity measured by a smart home sensor in Home Assistant.
This is an automation example to update a field `humidity`, based on a sensor in Home Assistant, denoted by a custom field `sensor`, for all spools every 15 minutes.

```yaml
alias: Update spoolman
description: ""
mode: single
triggers:
  - trigger: time_pattern
    minutes: /15
conditions: []
actions:
  - repeat:
      for_each: "{{ integration_entities('spoolman') }}"
      sequence:
        - if:
            - condition: template
              value_template: "{{ state_attr(repeat.item, 'extra_sensor') is not none }}"
          then:
            - action: spoolman.patch_spool
              data:
                id: "{{ state_attr(repeat.item, 'id') }}"
                extra:
                  sensor: "{{ state_attr(repeat.item, 'extra_sensor') }}"
                  humidity: >-
                    {{ states("sensor."+state_attr(repeat.item, 'extra_sensor')) }}
```

You can then easily use this information in your cards, for example to show the properties of your spools using the auto-entities card in combination with the multiple-entity-row card:

![List of spools with their attributes](docs/auto-entities-multiple-entity-row.png)


# Contributing
If you're developer and want to contribute to the project, please feel free to do a PR!
But there are some contraints I want to enforce by convention (currently I evaluate the possibility to enforce this by rules. If you have a good hint, please let me know 🎉):

- Please merge your PR to the [dev](https://github.com/Disane87/spoolman-homeassistant/tree/dev) branch. PRs against `main` will be rejected.
- Branch `main` only reflects the `latest` state of the integration
- Branch `dev` reflects the `next` state of the integration
- Please make use of [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/). This ensures the build pipeline works together with [semantic release](https://github.com/semantic-release/semantic-release) and your PRs will start a new release.
- I would recommend using visual studio code (since there is everything working out of the box)


# Cheers 🔥
