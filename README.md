# Premium Bond Checker for Home Assistant

Home Assistant custom component for creating sensors for checking if your holder number(s) have won on the premium bonds.

Leveraging the [premium-bond-checker](https://github.com/inverse/python-premium-bond-checker) package.

## What it provides

- Binary sensors for each holder number you configure including metadata around the result for:
  - This month
  - Last 6 months
  - Unclaimed
- Sensor for the next draw date

## Installation

Follow the [hacs](https://hacs.xyz/docs/faq/custom_repositories) documentation for adding a custom repository.

Repo: `https://github.com/inverse/home-assistant-premium-bond-checker-component`

## Example usage

<img src="https://github.com/user-attachments/assets/3f7394c1-cd96-4cbf-bc52-9ff41282eac2" width="400" />


_Illustrative: when you really have won it will display the prize information

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
