from premium_bond_checker.client import BondPeriod

DOMAIN = "premium_bond_checker"
INTEGRATION_TITLE = "Premium Bond Checker"

DEFAULT_SCAN_INTERVAL_WEEKS = 4

CONF_HOLDER_NUMBER = "holder_number"

COORDINATOR_CHECKER = "checker"
COORDINATOR_NEXT_DRAW = "next_draw"


ATTR_HEADER = "header"
ATTR_TAGLINE = "tagline"
ATTR_REVEAL_BY = "reveal_by"

BOND_PERIODS = {
    "this_month": BondPeriod.THIS_MONTH,
    "last_six_months": BondPeriod.LAST_SIX_MONTHS,
    "unclaimed": BondPeriod.UNCLAIMED,
}


BOND_PERIODS_TO_NAME = {
    "this_month": "This Month",
    "last_six_months": "Last Six Months",
    "unclaimed": "Unclaimed",
}


def build_entity_unique_id(config_entry_id: str, key: str) -> str:
    """Build a stable, non-sensitive entity unique ID."""
    return f"{config_entry_id}_{key}"
