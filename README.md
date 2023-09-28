
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration) [![Validate](https://github.com/Disane87/spoolman-homeassistant/actions/workflows/validate.yml/badge.svg)](https://github.com/Disane87/spoolman-homeassistant/actions/workflows/validate.yml)


# Spoolman Home Assistant Integration

This integration integrates Spoolman (https://github.com/Donkie/Spoolman/) into Home Assistant. This enables you to observe your filament spools and in example get notified when a spool runs out of filament.

# 🏗️ Installation
Just add this repo to the custom repos in HACS (https://hacs.xyz/docs/faq/custom_repositories/) and you're good to go. You should now see the integration in HACS where you can download the latest version.

# 🛠️ Usage
Just add a new integration for Spoolman and fill in the URL to your Spoolman instance, like this:

![image](https://github.com/Disane87/spoolman-homeassistant/blob/main/resources/images/spoolman-integration-config.png?raw=true)

If you are using an authorization, please fill in your API key provided by spoolman.

You should now see a new integration entry with one device (your spoolman instance) and all non archived spools:

![image](https://github.com/Disane87/spoolman-homeassistant/blob/main/resources/images/spoolman-integration-hass.png?raw=true)

For every spool there is a sensor created with the exact color you've provided. Additionally the integration tracks your curent weight and lenghts.

All other information provides by Spoolman are stored in the attributes of the sensor:

![image](https://github.com/Disane87/spoolman-homeassistant/blob/main/resources/images/spoolman-integration-sensor.png?raw=true)

