# Zehnder ComfoConnect PRO - Component
![Zehnder logo](/zehnder.png)

## Build Status

[![hassfest](https://github.com/hstrohmaier/ha_comfoconnectpro/actions/workflows/hassfest.yaml/badge.svg?branch=main)](https://github.com/hstrohmaier/ha_comfoconnectpro/actions/workflows/hassfest.yaml)
[![HACS](https://github.com/hstrohmaier/ha_comfoconnectpro/actions/workflows/hacs.yaml/badge.svg?branch=main)](https://github.com/hstrohmaier/ha_comfoconnectpro/actions/workflows/hacs.yaml)
[![Release checks](https://github.com/hstrohmaier/ha_comfoconnectpro/actions/workflows/release.yaml/badge.svg?branch=main)](https://github.com/hstrohmaier/ha_comfoconnectpro/actions/workflows/release.yaml)


[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)
![Version](https://img.shields.io/github/v/release/hstrohmaier/ha_comfoconnectpro?style=plastic)
![Downloads](https://img.shields.io/github/downloads/hstrohmaier/ha_comfoconnectpro/total)

Home Assistant Custom Component for Zehnder Zehnder ComfoConnect PRO interface. 

![Example screenshot of dashboard](/Screenshot.png)

## Installation

### HACS

This component is easiest installed using [HACS](https://github.com/custom-components/hacs).

To download the component, [the repository URL must be added as custom repository to HACS](https://hacs.xyz/docs/faq/custom_repositories/).

Use the URL: https://github.com/hstrohmaier/ha_comfoconnectpro

### Manual installation

Copy all files from custom_components/ha_comfoconnectpro/ to custom_components/ha_comfoconnectpro/ inside your config Home Assistant directory.

### Prerequisites
- Ownership of a Zehnder ComfoConnect PRO interface and ComfoAir Q 350 series
- Network connection to the Zehnder ComfoConnect PRO interface (Modbus-TCP)

## Configuration via UI
When adding the component to the Home Assistant intance, the config dialog will ask for Name, Host/IP-Address and Slave ID of the interface and the port number (usually 502 for Modbus over TCP)

## Entities

The integration creates multiple entities for recieving that states of the ventilation and for controlling mode.

## Activating Modbus-TCP using Zehnder ComfoConnect PRO Webinterface
- Go to the default web page of your Zehnder ComfoConnect PRO. (Served on port 80 of Interface-IP address)
- Login as admin
- Press 'Protocols and Services'
- Select 3rd Party Protocols, choose 'ModBus TCP'
- Leave the default settings (Slave ID: 1, TCP Port: 502)
- Press "Save"
- Done (take a minute to reboot)

If you have setup the interface already the data should be getting in at this point
Disclaimer: Use at own risk. As admin user you can do quite some settings that should not be done if you do not know what you are doing. In other words: Don't change any settings unless you have been instructed to by a Zehnder expert as admin.
