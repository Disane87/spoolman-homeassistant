
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Validate](https://github.com/Disane87/spoolman-homeassistant/actions/workflows/validate.yml/badge.svg)](https://github.com/Disane87/spoolman-homeassistant/actions/workflows/validate.yml)
![GitHub all releases](https://img.shields.io/github/downloads/Disane87/spoolman-homeassistant/total)
![GitHub](https://img.shields.io/github/license/Disane87/spoolman-homeassistant)
![GitHub issues by-label](https://img.shields.io/github/issues/Disane87/spoolman-homeassistant/bug?color=red)
![GitHub contributors](https://img.shields.io/github/contributors/Disane87/spoolman-homeassistant)
[![semantic-release: angular](https://img.shields.io/badge/semantic--release-angular-e10079?logo=semantic-release)](https://github.com/semantic-release/semantic-release)




# Spoolman Home Assistant Integration

This integration integrates Spoolman (https://github.com/Donkie/Spoolman/) into Home Assistant. This enables you to observe your filament spools and in example get notified when a spool runs out of filament.

# ✨ Features
- Locations in Spoolman are created as devices
- Spools are added to the devices
- Monitoring of filament consumption (used and remaining lenght/weight)
- Configurable thresholds for info, warning and critical states. This is useful to trigger notifications in HomeAssistant within an automation
- Enable/disabled archived spools
- Archived spools are grouped into one `Archived` device

> [!NOTE]
> If one of the threshold is exceeded the integration fires an event. The event is named `spoolman.notification_threshold_[threshold name]`. Currently there are three thresholds defined: `info`, `warning` and `critical`.


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

For every spool there is a sensor created with the exact color you've provided. Additionally the integration tracks your current weight and lenghts.

All other information provides by Spoolman are stored in the attributes of the sensor:

![image](resources/images/spoolman-integration-sensor.png?raw=true)

# Cheers 🔥
