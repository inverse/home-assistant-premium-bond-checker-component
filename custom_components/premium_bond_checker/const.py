from premium_bond_checker.client import BondPeriod

DOMAIN = "premium_bond_checker"

DEFAULT_SCAN_INTERVAL_WEEKS = 4

CONF_HOLDER_NUMBER = "holder_number"


ATTR_HEADER = "header"
ATTR_TAGLINE = "tagline"

BOND_PERIODS = [
    BondPeriod.THIS_MONTH,
    BondPeriod.LAST_SIX_MONTHS,
    BondPeriod.UNCLAIMED,
]


BOND_PERIODS_TO_NAME = {
    BondPeriod.THIS_MONTH: "This Month",
    BondPeriod.LAST_SIX_MONTHS: "Last Six Months",
    BondPeriod.UNCLAIMED: "Unclaimed",
}
