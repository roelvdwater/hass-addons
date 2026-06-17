# Home Assistant app: DSMR to HomeWizard P1 Meter

This Home Assistant app takes DSMR information from a specified Home Assistant instance and exposes it in the format of the HomeWizard V1 API. Currently, it only supports the V1 API.

## About

There are several devices out there which require a HomeWizard P1 Meter to read the energy and/or gas statistics from your house. Many people already have a P1 cable directly connected from their Home Assistant machine to their smart meter and read the data using the official [DSMR Smart Meter](https://www.home-assistant.io/integrations/dsmr/) integration. This app takes the stored DSMR data from a specified Home Assistant instance and exposes it using the HomeWizard P1 Meter V1 API format. This way, you don't need to buy an additional device.

I built this app because I was in that exact situation when I bought my Peblar car charger. It uses the HomeWizard P1 Meter to measure at which rates it can charge. Unfortunately, back then there was no such app, hence I bought the device and created this app.

The app advertises itself on the network using Zeroconf, which allows other devices to automatically discover it. On my Peblar car charger, this was working fine on below firmware version 1.9, however, it stopped working since version 1.9. Luckily, starting from version 1.9, you can manually enter the HomeWizard's IP Address to point to the emulated P1 Meter. So far, my only experience with devices using this emulator, is the Peblar car charger.

> **Note:** The app will return `503 Internal Server Error` when there is no data in the cache or the cache is stale. The cache is considered stale after 12 seconds, because P1 meters usually update every 10 seconds. There's a 2-second margin to give the app a chance to get the latest data from Home Assistant after being signaled to update its cache.

## Installation

The simplest way to install this app is by adding the app repository to your Home Assistant installation.

[![Open your Home Assistant instance and show the add app repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Froelvdwater%2Fhass-addons)

After adding the repository, find the **DSMR to HomeWizard P1 Meter** add-on and select it. Select the **Install** button to install it.

### Configuring the app

After installing the app, it needs a long-lived access token. The documentation on how to create yours can be found in [Home Assistant's official documentation](https://developers.home-assistant.io/docs/auth_api/#long-lived-access-token). Fill it in under `long_lived_access_token`.

You'll also need to configure your Home Assistant URL under `home_assistant_url`. Typically this is the same server's address that the app will be running from. Lastly, you need to fill in a serial number in `serial`. This is the serial number that the emulated P1 Meter will use. It consists of 11 random hexadecimal characters (e.g. 48ff497dd8e).

Once you've configured those settings, you can start the app. The API will be served from port 80 on HTTP (not using SSL), because that's what the official P1 Meter does too. You can try it by navigating to the `/api/v1/data` URL.

If everything's working as expected, you will even see a suggestion from Home Assistant popping up that a new HomeWizard P1 Meter was automatically discovered. You can simply ignore it (unless you want it), as there's no point in adding it because it's data is populated by the same Home Assistance instance.

### Creating an automation and shell command

The app works by retrieving data from Home Assistant on signal. It has a dedicated endpoint (`GET /refresh-data`) that calls the configured Home Assistant instance and stores the result in its cache. To do this automatically, you can create an automation that's triggered when the last update time of your electricity meter is updated, like this:

```
alias: DSMR data refresh
description: ""
triggers:
  - trigger: state
    entity_id:
      - sensor.electricity_meter_tijdstip
conditions: []
actions:
  - action: shell_command.refresh_dsmr_data
    metadata: {}
    data: {}
mode: single
```

You'll need to add the following line under the `shell_command` section of your `configuration.yaml`:

```
shell_command:
  refresh_dsmr_data: 'curl -s http://192.168.178.23/refresh-data'
```

I'm aware that this is not the most ideal way of retrieving and updating data and that there are more modern alternatives (such as using a WebSocket), but this also works (for now).