# HomeAssistant Warmlink Integration 
Warmlink is a custom Home Assistant integration for Warmlink/LinkedGo heat pumps. It logs in to the cloud, reads status and temperatures (Outlet is current temp), lets you set target temperature, and turn heating on/off. Use the main cloud account in HA; the mobile app should use a separate email with a shared Home to avoid single-login kicks. OK!!


# Warmlink CLI

Minimal CLI for diagnostics of Warmlink/LinkedGo cloud endpoints.

## Home Assistant (custom component)

This repo includes a simple HA custom component in `custom_components/warmlink`.

Install:

1) Copy `custom_components/warmlink` into your HA config `custom_components/`.
2) Restart Home Assistant.
3) Add integration: Settings -> Devices & Services -> Add Integration -> Warmlink.

Notes:

- Use the main account where the heat pump was originally added.
- The mobile app should use a different email and a shared "home" invitation to avoid single-login kicks.
- Climate entity uses Outlet temperature (`T02`) as current temperature and `R02` as target.
- Power ON/OFF and temperature set are supported from the climate entity.

## Account requirement (important)

The Warmlink cloud supports a single active login per account. To avoid getting logged out
on the phone when HA logs in:

1) Use the main account (where the heat pump was originally added) for Home Assistant.
2) Use a different email for the mobile app.
3) From the main account, share the "home" with the mobile account and accept the invitation.
