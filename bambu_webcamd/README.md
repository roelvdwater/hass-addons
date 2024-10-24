# Home Assistant Add-on: Bambu Lab webcamd server

This Home Assistant add-on allows you to stream Bambu Lab printers through HTTP. This add-on is essentially a wrapper for [this](https://github.com/synman/webcamd/tree/bambu) webcamd python server, which offers support for Bambu Lab printers.

## Installation

The simplest way to install this add-on is by adding the add-on repository to your Home Assistant installation.

[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Froelvdwater%2Fhass-addons)

After adding the repository, find the **Bambu Lab webcamd server** add-on and select it. Select the **INSTALL** button to install it.

Make sure to set the hostname of your Bambu Lab printer and its access code in the configuration before starting the add-on.

When following the steps above, you're all set and you can start the add-on. You can then navigate to the web interface by selecting the **OPEN WEB-UI** button. From there, you'll have several options to watch the camera's feed.

The underlying webcamd server supports watching a livestream. However, the add-on only supports getting snapshots at the moment. Support for watching the livestream will potentially be added in the future.
