# Premium Bond Checker for Home Assistant

[![hacs][hacs-badge]][hacs-url]
[![release][release-badge]][release-url]
![build][build-badge]
![ruff][ruff-badge]

A [Home Assistant][home-assistant] component for creating sensors for checking if your holder number(s) have won on the premium bonds.

It fetches data from [NS&I][nsandi], leveraging the [premium-bond-checker][premium-bond-checker-package] package.

## What it provides

- Binary sensors for each holder number you configure including metadata around the result for:
  - This month
  - Last six months (`last_six_months`)
  - Unclaimed
- Prize value sensors with the total prize amount for each of those periods
- Sensor for the next draw date

## Installation

It's available via [HACS][hacs] through the standard process for custom repositories. Follow their [official guide][hacs-custom-repo-guide] for adding a custom repository.

Repo: `https://github.com/inverse/home-assistant-premium-bond-checker-component`

## Configuration

This integration is configured from the UI; there is no YAML configuration.

1. Go to **Settings > Devices & Services > Add Integration**.
2. Search for **Premium Bond Checker**.
3. Enter your holder number and submit.

Add one integration entry per holder number. Each entry creates its own set of entities, named `Premium Bond Checker <holder number> <period>` - for example `binary_sensor.premium_bond_checker_12345678_this_month`.

## Example usage

<img src="https://github.com/user-attachments/assets/3f7394c1-cd96-4cbf-bc52-9ff41282eac2" width="400" />

_Illustrative, when you really have won it will display the prize information._

### Automation

```yaml
alias: Premium Bond Win
triggers:
  - trigger: state
    entity_id:
      - binary_sensor.premium_bond_checker_<your_holder_number>_this_month
    attribute: tagline
conditions:
  - condition: state
    entity_id: binary_sensor.premium_bond_checker_<your_holder_number>_this_month
    state:
      - "on"
actions:
  - action: notify.<your_notifier>
    data:
      title: Premium Bond Win!
      message: >-
        {{ state_attr('binary_sensor.premium_bond_checker_<your_holder_number>_this_month', 'header') }}
        {{ state_attr('binary_sensor.premium_bond_checker_<your_holder_number>_this_month',
        'tagline') }}
```

## License

MIT - see [LICENSE](LICENSE).

## Contributing

Issues and pull requests are welcome at
[the repository](https://github.com/inverse/home-assistant-premium-bond-checker-component).

<!-- Badges -->

[hacs-url]: https://github.com/hacs/integration
[hacs-badge]: https://img.shields.io/badge/hacs-default-orange.svg?style=flat-square
[release-badge]: https://img.shields.io/github/v/release/inverse/home-assistant-premium-bond-checker-component?style=flat-square
[build-badge]: https://img.shields.io/github/actions/workflow/status/inverse/home-assistant-premium-bond-checker-component/main.yml?branch=master&style=flat-square
[ruff-badge]: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v0.json

<!-- Other -->

[premium-bond-checker-package]: https://github.com/inverse/python-premium-bond-checker
[home-assistant]: https://www.home-assistant.io/
[hacs]: https://hacs.xyz
[hacs-custom-repo-guide]: https://hacs.xyz/docs/faq/custom_repositories
[nsandi]: https://www.nsandi.com/
[release-url]: https://github.com/inverse/home-assistant-premium-bond-checker-component/releases
[ruff]: https://github.com/astral-sh/ruff
