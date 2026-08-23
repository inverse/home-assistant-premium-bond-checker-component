from premium_bond_checker.client import BondPeriod

BOND_PERIOD_CONFIG = {
    "this_month": (BondPeriod.THIS_MONTH, "This Month"),
    "last_six_months": (BondPeriod.LAST_SIX_MONTHS, "Last Six Months"),
    "unclaimed": (BondPeriod.UNCLAIMED, "Unclaimed"),
}

DOMAIN = "premium_bond_checker"

DEFAULT_SCAN_INTERVAL_WEEKS = 4

CONF_HOLDER_NUMBER = "holder_number"

COORDINATOR_CHECKER = "checker"
COORDINATOR_NEXT_DRAW = "next_draw"


ATTR_HEADER = "header"
ATTR_TAGLINE = "tagline"
ATTR_REVEAL_BY = "reveal_by"
