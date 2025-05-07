# Premium Bond Checker for Home Assistant

[![hacs][hacs-badge]][hacs-url]
[![release][release-badge]][release-url]
![downloads][downloads-badge]
![build][build-badge]

A [Home Assistant][home-assistant] component for creating sensors for checking if your holder number(s) have won on the premium bonds.

It fetches data from [Nsandi], leveraging the [premium-bond-checker][premium-bond-checker-package] package.

## What it provides

- Binary sensors for each holder number you configure including metadata around the result for:
  - This month
  - Last 6 months
  - Unclaimed
- Sensor for the next draw date

## Installation

It's available via [HACS][hacs] through the standard process for custom repositories Follow their [official guide][hacs-custom-repo-guide] for adding a custom repository.

Repo: `https://github.com/inverse/home-assistant-premium-bond-checker-component`

## Example usage

<img src="https://github.com/user-attachments/assets/3f7394c1-cd96-4cbf-bc52-9ff41282eac2" width="400" />

_Illustrative, when you really have won it will display the prize information._

### Automation

```yaml
alias: Premium Bond Win
triggers:
  - trigger: state
    entity_id:
      - sensor.premium_bond_checker_<your_holder_number>_this_month
    from: "off"
    to: "on"
actions:
  - action: notify.<your_notifier>
    data:
      title: "Premium Bond Win!"
      message: >
        {{ sensor.premium_bond_checker_<your_holder_number>_this_month', 'header') }}

        {{ sensor.premium_bond_checker_<your_holder_number>_this_month', 'tagline') }}
```

<!-- Badges -->

[hacs-url]: https://github.com/hacs/integration
[hacs-badge]: https://img.shields.io/badge/hacs-default-orange.svg?style=flat-square
[release-badge]: https://img.shields.io/github/v/release/inverse/home-assistant-premium-bond-checker-component?style=flat-square
[downloads-badge]: https://img.shields.io/github/downloads/inverse/home-assistant-premium-bond-checker-component/total?style=flat-square
[build-badge]: https://img.shields.io/github/actions/workflow/status/inverse/home-assistant-premium-bond-checker-component/main.yml?branch=master&style=flat-square

<!-- Other -->

[premium-bond-checker-package]: https://github.com/inverse/python-premium-bond-checker
[home-assistant]: https://www.home-assistant.io/
[hacs]: https://hacs.xyz
[hacs-custom-repo-guide]: https://hacs.xyz/docs/faq/custom_repositories
[nsandi]: https://www.nsandi.com/
[release-url]: https://github.com/inverse/home-assistant-premium-bond-checker-component/releases
